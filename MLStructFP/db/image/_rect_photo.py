"""
MLSTRUCT-FP - DB - IMAGE - RECT PHOTO

Image of the true rect photo from the base image plan.
"""

__all__ = ['RectFloorPhoto']

from MLStructFP.db.image._base import BaseImage, TYPE_IMAGE
from MLStructFP.utils import GeomPoint2D
from MLStructFP._types import TYPE_CHECKING, Dict, List, Union, Tuple, Optional, NumberType

import cv2
import gc
import math
import numpy as np
import os
import time

if TYPE_CHECKING:
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.db._floor import Floor

IMAGES_TO_CLEAR_MEMORY: int = 10000
MAX_STORED_FLOORS: int = 2


def _im_show(title: str, img: 'np.ndarray') -> None:
    """
    Image show using cv2.

    :param title: Title
    :param img: Image
    """
    w, h, _ = img.shape
    f = 1  # Factor
    _w = 768
    _h = 1024
    if w > _w or h > _h:
        fx = _w / w
        fy = _h / h
        f = min(fx, fy, 1)
    if f != 1:
        w = int(math.ceil(abs(w * f)))
        h = int(math.ceil(abs(h * f)))
        img = cv2.resize(img, (h, w), interpolation=cv2.INTER_AREA)
    cv2.imshow(title, img)


def _show_img(
        img: Union['np.ndarray', List['np.ndarray']],
        title: Union['str', List[str]] = ''
) -> None:
    """
    Show image with cv2.

    :param img: Image
    :param title: Image titles
    """
    if isinstance(img, list):
        for k in range(len(img)):
            if title == '':
                _im_show(f'Image {k + 1}', img[k])
            else:
                assert isinstance(title, list)
                _im_show(title[k], img[k])
    else:
        if title == '':
            title = 'Image'
        _im_show(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def _sgn(x) -> float:
    """
    Returns the sign of x.

    :param x: Number
    :return: Sign
    """
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1


def _rotate_image(image: 'np.ndarray', angle: float, bound: bool = True) -> 'np.ndarray':
    """
    Rotate image around center.

    :param image: Image
    :param angle: Rotation angle
    :param bound: Expands image to avoid cropping
    :return: Rotated image
    """
    if angle == 0:
        return image
    elif bound:
        return _rotate_image_bound(image, angle)
    (h, w) = image.shape[:2]
    image_center = (w // 2, h // 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def _rotate_image_bound(mat: 'np.ndarray', angle: float) -> 'np.ndarray':
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping.

    :param mat: Image
    :param angle: Rotation angle
    :return: Rotated image
    """
    height, width = mat.shape[:2]  # image shape has 3 dimensions
    image_center = (
        width / 2,
        height / 2)  # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origin) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def _show_frame_image(image: 'np.ndarray', x1: int, y1: int, x2: int, y2: int) -> None:
    """
    Write image frame and display.

    :param image: Image
    :param x1: Min x
    :param y1: Min y
    :param x2: Max x
    :param y2: Max y
    """
    image = image.copy()
    w = 100
    color = [255, 255, 255]
    image[y1:y2, x1:x1 + w] = color
    image[y1:y2, x2 - w:x2] = color
    image[y1:y1 + w, x1:x2] = color
    image[y2 - w:y2, x1:x2] = color
    _show_img(image, 'Frame')


def _show_dot_image(
        image: 'np.ndarray',
        points: List[Union[Tuple, 'GeomPoint2D']],
        colors: Optional[List[List]] = None
) -> None:
    """
    Write image dot and display.

    :param image: Image
    :param points: List of points
    """
    image = image.copy()

    def _dot(_x: Union[int, float], _y: Union[int, float], color: List[int]) -> None:
        """
        Create a dot on image.

        :param _x: X pos
        :param _y: Y pos
        :param color: Color of the point
        """
        x1 = int(_x)
        y1 = int(_y)
        w = 75
        x1 = int(x1 - w / 2)
        y1 = int(y1 - w / 2)
        x2 = x1 + w
        y2 = y1 + w
        image[y1:y2, x1:x1 + w] = color
        image[y1:y2, x2 - w:x2] = color
        image[y1:y1 + w, x1:x2] = color
        image[y2 - w:y2, x1:x2] = color

    if colors is None:
        colors = []
        for i in range(len(points)):
            colors.append([255, 255, 255])
    for j in range(len(points)):
        p = points[j]
        if not isinstance(p, tuple):
            _dot(p.x, p.y, colors[j])
        else:
            _dot(p[0], p[1], colors[j])
    _show_img(image, 'Frame')


class RectFloorPhoto(BaseImage):
    """
    Floor rect photo.
    """
    _empty_color: int
    _floor_center_d: Dict[str, 'GeomPoint2D']  # No rotation image size in pixels
    _floor_images: Dict[str, 'np.ndarray']
    _invert: bool
    _kernel: 'np.ndarray'
    _processed_images: int
    _verbose: bool

    def __init__(
            self,
            path: str = '',
            save_images: bool = False,
            image_size_px: int = 64,
            empty_color: int = -1,
            invert: bool = False
    ) -> None:
        """
        Constructor.

        :param path: Image path
        :param save_images: Save images on path
        :param image_size_px: Image size (width/height), bigger images are expensive, double the width, quad the size
        :param empty_color: Empty base color. If -1, disable empty replace color
        :param invert: Invert color
        """
        BaseImage.__init__(self, path, save_images, image_size_px)
        assert -1 <= empty_color <= 255
        assert isinstance(invert, bool)

        self._empty_color = empty_color  # Color to replace empty data
        self._invert = invert
        self._processed_images = 0
        self._verbose = False

        # Create filter kernel
        # self._kernel = np.array([[0, -1, 0],
        #                          [-1, 5, -1],
        #                          [0, -1, 0]])
        self._kernel = np.array([[-1, -1, -1],
                                 [-1, 9, -1],
                                 [-1, -1, -1]])

        # Store loaded images
        self._floor_images = {}
        self._floor_center_d = {}

    def _parse_image(self, ip: str, mutator_scale_x: float = 1, mutator_scale_y: float = 1,
                     mutator_angle: float = 0, verbose: bool = False) -> Tuple['np.ndarray', 'GeomPoint2D']:
        """
        Process image.

        :param ip: Image path
        :param mutator_scale_x: Mutator scale on x-axis
        :param mutator_scale_y: Mutator scale on y-axis
        :param mutator_angle: Mutator angle
        :param verbose: Verbose mode
        :return: Parsed image, center
        """
        # Make default empty color
        pixels: 'np.ndarray'
        if self._empty_color >= 0:
            image: 'np.ndarray' = cv2.imread(ip, cv2.IMREAD_UNCHANGED)
            if image is None:
                raise RectFloorPhotoFileLoadException(ip)
            if len(image.shape) == 3 and image.shape[2] == 4:
                # Make mask of where the transparent bits are
                trans_mask = image[:, :, 3] == 0
                # Replace areas of transparency with white and not transparent
                image[trans_mask] = [self._empty_color, self._empty_color, self._empty_color, 255]
                pixels = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
            else:
                pixels = image
        else:
            pixels = cv2.imread(ip)
            if pixels is None:
                raise RectFloorPhotoFileLoadException(ip)
            # Turn all black lines to white
            if len(pixels.shape) == 3 and np.max(pixels) == 0:
                image = cv2.imread(ip, cv2.IMREAD_UNCHANGED)
                trans_mask = image[:, :, 3] == 0
                image[trans_mask] = [255, 255, 255, 255]  # Turn all black to white to invert
                pixels = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        if self._invert:
            pixels = 255 - pixels

        # If image has only 1 channel, convert back to 3
        if len(pixels.shape) == 2:
            pixels = np.stack([pixels, pixels, pixels], axis=-1)

        # Flip image
        if mutator_scale_x != 1 or mutator_scale_y != 1:
            if mutator_scale_x < 0:
                pixels = cv2.flip(pixels, 1)
            if mutator_scale_y < 0:
                pixels = cv2.flip(pixels, 0)

            # Transform image due to mutators
            sy, sx, _ = pixels.shape
            sx = int(math.ceil(abs(sx * mutator_scale_x)))
            sy = int(math.ceil(abs(sy * mutator_scale_y)))
            pixels = cv2.resize(pixels, (sx, sy))

        source_pixels: Optional['np.ndarray'] = None
        if verbose:
            source_pixels = pixels.copy()
        cy, cx = pixels.shape[:2]  # Source center pixel
        pixels = _rotate_image(pixels, mutator_angle)
        if verbose:
            _show_img([source_pixels, pixels])

        return pixels, GeomPoint2D(cx, cy)

    def _get_floor_image(self, floor: 'Floor', store: bool = True) -> Tuple['np.ndarray', 'GeomPoint2D']:
        """
        Get floor image numpy class.

        :param floor: Floor object
        :param store: Store results for faster future queries
        :return: Image array
        """
        floor_hash = f'{floor.id}{floor.mutator_angle}{floor.mutator_scale_x}{floor.mutator_scale_y}'
        if floor_hash in self._floor_images.keys():
            return self._floor_images[floor_hash], self._floor_center_d[floor_hash]
        ip = floor.image_path

        if self._verbose:
            print(f'Loading image: {ip}')
        pixels, pc = self._parse_image(ip, floor.mutator_scale_x, floor.mutator_scale_y,
                                       floor.mutator_angle, self._verbose)

        # Store
        if store:
            self._floor_images[floor_hash] = pixels
            self._floor_center_d[floor_hash] = pc
            if self._verbose:
                print('Storing', ip, floor_hash)

            if len(self._floor_images) >= MAX_STORED_FLOORS:
                key_iter = iter(self._floor_images.keys())
                k1: str = next(key_iter)
                del self._floor_images[k1]  # Remove
                del self._floor_center_d[k1]
                if self._verbose:
                    print('Removing', ip, k1)

        # Return pixels and center
        return pixels, pc

    def make_rect(self, rect: 'Rect', crop_length: NumberType = 5) -> Tuple[int, 'np.ndarray']:
        """
        Generate image for the perimeter of a given rectangle.

        :param rect: Rectangle
        :param crop_length: Size of crop from center of the rect to any edge in meters
        :return: Returns the image index on the library array
        """
        return self._make(rect.floor, rect.get_mass_center(), crop_length, crop_length, rect)

    def make_region(self, xmin: NumberType, xmax: NumberType, ymin: NumberType, ymax: NumberType,
                    floor: 'Floor') -> Tuple[int, 'np.ndarray']:
        """
        Generate image for a given region.

        :param xmin: Minimum x-axis (image coordinates)
        :param xmax: Maximum x-axis (image coordinates)
        :param ymin: Minimum y-axis (image coordinates)
        :param ymax: Maximum y-axis (image coordinates)
        :param floor: Floor object
        :return: Returns the image index on the library array
        """
        assert xmax > xmin and ymax > ymin
        t0 = time.time()
        dx = (xmax - xmin) / 2
        dy = (ymax - ymin) / 2
        mk = self._make(floor, GeomPoint2D(xmin + dx, ymin + dy), dx, dy, None)
        self._last_make_region_time = time.time() - t0
        return mk

    def _make(self, floor: 'Floor', cr: 'GeomPoint2D', dx: float, dy: float, rect: Optional['Rect']
              ) -> Tuple[int, 'np.ndarray']:
        """
        Generate image from a given coordinate (x, y).

        :param floor: Object floor to process
        :param cr: Coordinate to process
        :param dx: Half crop distance on x-axis (m)
        :param dy: Half crop distance on y-axis (m)
        :param rect: Optional rect
        :return: Returns the image index on the library array
        """
        assert dx > 0 and dy > 0
        image, original_shape = self._get_floor_image(floor)

        # Compute crop area
        sc = floor.image_scale
        sx = floor.mutator_scale_x
        sy = -floor.mutator_scale_y

        # Image size in px
        h, w, _ = image.shape

        # Original center (non rotated)
        rc2 = original_shape.clone()
        rc2.scale(0.5)

        # Compute true point based on rotation
        ax = sc / _sgn(sx)
        ay = sc / _sgn(sy)
        cr.rotate(GeomPoint2D(), -floor.mutator_angle)

        # Scale to pixels
        cr.x *= ax
        cr.y *= ay

        if sx < 0:
            cr.x = original_shape.x - cr.x
        if sy > 0:
            cr.y = original_shape.y - cr.y

        # Compute the distance to original center and angle
        r = cr.dist(rc2)
        theta = cr.angle(rc2)
        del rc2

        # Create point from current center using radius and computed angle
        cr.x = w / 2 + r * math.cos(theta + math.pi * (1 - floor.mutator_angle / 180))
        cr.y = h / 2 + r * math.sin(theta + math.pi * (1 - floor.mutator_angle / 180))

        if self._verbose:
            if rect is not None:
                print(f'Processing rect ID <{rect.id}>')
            ce = GeomPoint2D(w / 2, h / 2)
            _show_dot_image(image, [ce, cr], [[255, 255, 255], [255, 0, 0]])

        # Scale back
        cr.x /= ax
        cr.y /= ay

        # Create region
        xmin = cr.x - dx
        xmax = cr.x + dx
        ymin = cr.y - dy
        ymax = cr.y + dy

        image: 'np.ndarray' = self._get_floor_image(floor)[0]
        figname = f'{rect.id}' if rect else f'{floor.id}-x-{xmin:.2f}-{xmax:.2f}-y-{ymin:.2f}-{ymax:.2f}'

        # Get cropped and resized box
        out_img: 'np.ndarray' = self._get_crop_image(
            image=image,
            x1=int(xmin * ax),
            x2=int(xmax * ax),
            y1=int(ymin * ay),
            y2=int(ymax * ay),
            rect=rect)

        if self._save_images:
            assert self._path != '', 'Path cannot be empty'
            filesave = os.path.join(self._path, figname + '.png')
            cv2.imwrite(filesave, out_img)

        # Save to array
        out_img_rgb = cv2.cvtColor(out_img, cv2.COLOR_BGR2RGB)
        if self.save:
            self._images.append(out_img_rgb)  # Save as rgb
            self._names.append(figname)

        self._processed_images += 1
        if self._processed_images % IMAGES_TO_CLEAR_MEMORY == 0:
            gc.collect()

        # Clear memory
        del out_img

        # Returns the image index on the library array
        return len(self._names) - 1, out_img_rgb  # Images array can change during export

    def _get_empty_image(self) -> 'np.ndarray':
        """
        :return: Desired output image with default empty color
        """
        img: 'np.ndarray' = np.ones((self._image_size, self._image_size, 3)) * self._empty_color
        img = img.astype(TYPE_IMAGE)
        return img

    def _get_crop_image(
            self,
            image: 'np.ndarray',
            x1: int,
            x2: int,
            y1: int,
            y2: int,
            rect: Optional['Rect']
    ) -> 'np.ndarray':
        """
        Create crop image.

        :param image: Source image array
        :param x1: Min pos (x axis)
        :param x2: Max pos (x axis)
        :param y1: Min pos (y axis)
        :param y2: Max pos (y axis)
        :param rect: Rect object from the image
        :return: Cropped image
        """
        t = time.time()
        x = [x1, x2]
        y = [y1, y2]
        x1, x2 = min(x), max(x)
        y1, y2 = min(y), max(y)
        ww = int(x2 - x1)
        hh = int(y2 - y1)
        if len(image.shape) == 2:
            w, h = image.shape
            out_img = np.zeros((ww, hh))
        else:
            w, h, c = image.shape
            out_img = np.zeros((ww, hh, c))
        dx = 0
        if x1 < 0:
            dx = - x1
            x1 = 0
        if x1 + hh > h:
            hh = max(0, h - x1)
        dy = 0
        if y1 < 0:
            dy = -y1
            y1 = 0
        if y1 + ww > w:
            ww = max(0, w - y1)
        if ww - dy > 0 and hh - dx > 0:
            _x2 = x1 + hh - dx
            _y2 = y1 + ww - dy
            if self._verbose:
                print(f'\tRead from x:{x1}->{_x2} to y:{y1}->{_y2}')
                print(f'\t{dy}', dx, y1, x1, ww, hh)
                _show_frame_image(image, x1, y1, x2, y2)
            try:
                out_img[dy:dy + ww, dx:dx + hh] = image[y1:_y2, x1:_x2]
            except ValueError as e:
                if rect is not None:
                    print(f'Shape inconsistency at rect ID <{rect.id}>, Floor ID {rect.floor.id}')
                raise RectFloorPhotoShapeException(str(e))

        """
        Good:       INTER_AREA
        Not good:   INTER_LANCZOS4, INTER_BITS, INTER_CUBIC, INTER_LINEAR,
                    INTER_LINEAR_EXACT
        Bad:        INTER_NEAREST
        """
        out_rz: 'np.ndarray' = cv2.resize(out_img, (self._image_size, self._image_size),
                                          interpolation=cv2.INTER_AREA)
        if self._verbose:
            print('Process finished in {0} seconds'.format(int(time.time() - t)))
        im = out_rz.astype(TYPE_IMAGE)
        _alpha = -5
        if self._empty_color == 0:
            adjusted: 'np.ndarray' = cv2.convertScaleAbs(im, alpha=_alpha, beta=0)
        else:
            adjusted = im

        # Apply kernel
        image_kernel = cv2.filter2D(adjusted, -1, self._kernel)

        if self._verbose:
            _show_img([im, adjusted, cv2.convertScaleAbs(im, alpha=2 * _alpha, beta=0), 255 - adjusted, image_kernel],
                      ['Base', 'Adjusted', 'Adjusted2', 'Negative adjusted', 'By kernel'])

        return image_kernel

    def close(self) -> None:
        """
        Close and delete all generated figures.
        """
        self._names.clear()
        self._processed_images = 0
        self._images.clear()
        self._floor_images.clear()
        self._floor_center_d.clear()
        gc.collect()


class RectFloorPhotoShapeException(Exception):
    """
    Custom exception from rect floor generation image.
    """


class RectFloorPhotoFileLoadException(Exception):
    """
    Exception thrown if the image could not be loaded.
    """
