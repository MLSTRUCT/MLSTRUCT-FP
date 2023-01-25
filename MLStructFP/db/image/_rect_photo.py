"""
MLSTRUCTFP - DB - IMAGE - RECT PHOTO

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

IMAGES_TO_CLEAR_MEMORY = 10000
MAX_STORED_FLOORS = 2


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


def _swap_colors(image: 'np.ndarray', cfrom: int, cto: int, tol: float = 1e-3):
    """
    Swap colors from image.

    :param image: Target image
    :param cfrom: Color from
    :param cto: Color to
    :param tol: Tolerance
    """
    assert 0 <= cfrom <= 255
    assert 0 <= cto <= 255
    if cfrom == cto:
        return

    ccof = (cfrom, cfrom, cfrom)
    ccol = (cto, cto, cto)

    def _make_range(color) -> tuple:
        """
        Create color range from to.

        :param color: Target color
        :return: Range color
        """
        e = tol
        if color == 0:
            return (0, 0, 0), (color + e, color + e, color + e)
        elif abs(color - e) <= 255:
            return (color - e, color - e, color - e), (color, color, color)
        else:
            return (color, color, color), (color + e, color + e, color + e)

    # Create mask to change black to export color
    bc = _make_range(cfrom)
    mask_b_c = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), bc[0], bc[1])

    # Color to black
    cb = _make_range(cto)
    mask_c_b = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), cb[0], cb[1])
    # _show_img([mask_b_c, mask_c_b])

    # Replace color from mask
    image[mask_b_c == 255] = ccol
    image[mask_c_b == 255] = ccof


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
    if bound:
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
    _export_compressed: bool
    _export_current: int
    _export_each: int
    _export_filename: str
    _export_init: bool
    _export_part: int
    _export_total: int
    _export_total_last: int
    _floor_center_d: Dict[str, 'GeomPoint2D']  # No rotation image size in pixels
    _floor_images: Dict[str, 'np.ndarray']
    _kernel: 'np.ndarray'
    _verbose: bool

    def __init__(
            self,
            path: str = '',
            save_images: bool = False,
            image_size_px: int = 64,
            empty_color: int = -1
    ) -> None:
        """
        Constructor.

        :param path: Image path
        :param save_images: Save images on path
        :param image_size_px: Image size (width/height), bigger images are expensive, double the width, quad the size
        :param empty_color: Empty base color. If -1, disable empty replace color
        """
        BaseImage.__init__(self, path, save_images, image_size_px)

        if empty_color != -1:
            print('Using debug mode with different empty color')
        assert -1 <= empty_color <= 255

        self._empty_color = empty_color  # Color to replace empty data
        self._export_compressed = False  # Export as a compressed numpy file
        self._export_current = 0  # Total exported projects
        self._export_each = 0  # Export each N finished projects
        self._export_filename = ''  # Export filename target
        self._export_init = False  # Export has been initialized
        self._export_part = 1  # Actual part
        self._export_total = 0  # Total projects to be exported
        self._export_total_last = 0  # Number of total projects evaluated after last export
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

    def configure_export(
            self,
            filename: str,
            save_each: int,
            save_total: int,
            export_compressed: bool
    ) -> None:
        """
        Configure export

        :param filename: Export filename
        :param save_each: Export each N projects
        :param save_total: Total projects to be exported
        :param export_compressed: Export as a compressed .npz file
        """
        if self._export_init:
            raise RuntimeError('Exporter already configured')
        assert save_each >= 1
        assert save_each < save_total
        self._export_compressed = export_compressed
        self._export_init = True
        self._export_filename = filename
        self._export_each = save_each
        self._export_total = save_total
        self.save = True

    def _get_floor_image(self, floor: 'Floor') -> Tuple['np.ndarray', 'GeomPoint2D']:
        """
        Get floor image numpy class.

        :param floor: Floor object
        :return: Image array
        """
        floor_hash = f'{floor.id}{floor.mutator_angle}{floor.mutator_scale_x}{floor.mutator_scale_y}'
        if floor_hash in self._floor_images.keys():
            return self._floor_images[floor_hash], self._floor_center_d[floor_hash]

        ip = floor.image_path
        if self._verbose:
            print(f'Loading image: {ip}')

        # Make default empty color
        pixels: 'np.ndarray'
        if self._empty_color >= 0:
            image = cv2.imread(ip, cv2.IMREAD_UNCHANGED)

            # make mask of where the transparent bits are
            trans_mask = image[:, :, 3] == 0

            # replace areas of transparency with white and not transparent
            image[trans_mask] = [self._empty_color, self._empty_color, self._empty_color, 255]
            pixels = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        else:
            pixels = cv2.imread(ip)

            # Turn all black lines to white
            if np.max(pixels) == 0:
                image = cv2.imread(ip, cv2.IMREAD_UNCHANGED)
                trans_mask = image[:, :, 3] == 0
                image[trans_mask] = [255, 255, 255, 255]  # Turn all black to white to invert
                pixels = 255 - cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)  # Invert colors

        # Flip image
        if floor.mutator_scale_x < 0:
            pixels = cv2.flip(pixels, 1)
        if floor.mutator_scale_y < 0:
            pixels = cv2.flip(pixels, 0)

        # Transform image due to mutators
        sy, sx, _ = pixels.shape
        sx = int(math.ceil(abs(sx * floor.mutator_scale_x)))
        sy = int(math.ceil(abs(sy * floor.mutator_scale_y)))
        pixels = cv2.resize(pixels, (sx, sy))

        source_pixels: 'np.ndarray' = pixels
        if self._verbose:
            source_pixels = pixels.copy()
        cy, cx = pixels.shape[:2]  # Source center pixel
        pc = GeomPoint2D(cx, cy)
        pixels = _rotate_image(pixels, floor.mutator_angle)
        if self._verbose:
            _show_img([source_pixels, pixels])

        # Store
        self._floor_images[floor_hash] = pixels
        self._floor_center_d[floor_hash] = pc
        # print('Storing', self.name, floor_hash)

        if len(self._floor_images) >= MAX_STORED_FLOORS:
            key_iter = iter(self._floor_images.keys())
            k1: str = next(key_iter)
            del self._floor_images[k1]  # Remove
            del self._floor_center_d[k1]
            # print('Removing', self.name, k1)

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
                    floor: 'Floor', rect: Optional['Rect'] = None) -> Tuple[int, 'np.ndarray']:
        """
        Generate image for a given region.

        :param xmin: Minimum x-axis (image coordinates)
        :param xmax: Maximum x-axis (image coordinates)
        :param ymin: Minimum y-axis (image coordinates)
        :param ymax: Maximum y-axis (image coordinates)
        :param floor: Floor object
        :param rect: Optional rect for debug
        :return: Returns the image index on the library array
        """
        assert xmax > xmin and ymax > ymin
        dx = (xmax - xmin) / 2
        dy = (ymax - ymin) / 2
        return self._make(floor, GeomPoint2D(xmin + dx, ymin + dy), dx, dy, rect)

    def _make(self, floor: 'Floor', cr: 'GeomPoint2D', dx: float, dy: float, rect: Optional['Rect']) -> Tuple[int, 'np.ndarray']:
        """
        Generate image for a given coordinate (x, y).

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
            self._names.append(figname + '-part' + str(self._export_part))

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
        x = [x1, x2]
        y = [y1, y2]
        x1, x2 = min(x), max(x)
        y1, y2 = min(y), max(y)
        ww = int(x2 - x1)
        hh = int(y2 - y1)
        out_img = np.zeros((ww, hh, 3))
        w, h, _ = image.shape  # Real image size
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
                print(e)
                if rect is not None:
                    print(f'Shape inconsistency at rect ID <{rect.id}>, Floor ID {rect.floor.id}')
                raise RectFloorShapeException()

        """
        Good:       INTER_AREA
        Not good:   INTER_LANCZOS4, INTER_BITS, INTER_CUBIC, INTER_LINEAR,
                    INTER_LINEAR_EXACT
        Bad:        INTER_NEAREST
        """
        out_rz: 'np.ndarray' = cv2.resize(out_img, (self._image_size, self._image_size),
                                          interpolation=cv2.INTER_AREA)
        # if self._verbose:
        #     print('Process finished in {0} seconds'.format(int(time.time() - t)))
        im = out_rz.astype(TYPE_IMAGE)
        _alpha = -5
        if self._empty_color == 0:
            adjusted: 'np.ndarray' = cv2.convertScaleAbs(im, alpha=_alpha, beta=0)
        else:
            adjusted = im
        # _swap_colors(adjusted, 0, self._empty_color)

        # Apply kernel
        image_kernel = cv2.filter2D(adjusted, -1, self._kernel)

        # _show_img([im, adjusted, cv2.convertScaleAbs(im, alpha=2 * _alpha, beta=0), 255 - adjusted, image_kernel],
        #           ['Base', 'Adjusted', 'Adjusted2', 'Negative adjusted', 'By kernel'])

        return image_kernel

    def close(self) -> None:
        """
        Close and delete all generated figures.
        """
        del self._names
        self._names = []
        self._processed_images = 0

    def export(self) -> None:
        """
        Call to export parts, if the current part is greater than export each or the current project
        is the last save to file.
        """
        if not self._export_init:
            raise RuntimeError('Exporter has not been configured yet')
        assert len(self._images) > 0, 'Exporter cannot be empty'

        # Add project
        self._export_current += 1
        self._export_total_last += 1
        if not (self._export_total_last >= self._export_each or self._export_current == self._export_total):
            return

        # Export images
        filename = self._export_filename + f'_{self._image_size}_part{self._export_part}'
        self._export_part += 1
        self._export_total_last = 0
        if self._export_compressed:
            np.savez_compressed(filename, data=self.get_images())  # .npz
        else:
            np.save(filename, self.get_images())  # .npy

        # Export names
        imnames = open(self._export_filename + f'_{self._image_size}_files.csv', 'w', encoding='utf-8')
        imnames.write('ID,File\n')
        for i in range(len(self._names)):
            imnames.write(f'{i},{self._names[i]}\n')
        imnames.close()

        # Clear memory
        del self._images
        self._images = []
        del self._floor_images
        self._floor_images = {}
        del self._floor_center_d
        self._floor_center_d = {}
        gc.collect()
        time.sleep(2)


class RectFloorShapeException(Exception):
    """
    Custom exception from rect floor generation image.
    """

    def __init__(self) -> None:
        Exception.__init__(self)
