"""
MLSTRUCT-FP - DB - IMAGE - RECT BINARY

Image of the surroundings of a rect.
"""

__all__ = ['RectBinaryImage', 'restore_plot_backend']

from MLStructFP.db.image._base import BaseImage, TYPE_IMAGE
from MLStructFP.utils import make_dirs
from MLStructFP._types import TYPE_CHECKING, Tuple, Dict, NumberType

from PIL import Image
import io
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import time

if TYPE_CHECKING:
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.db._floor import Floor
    from MLStructFP.utils import GeomPoint2D
    from matplotlib.figure import Figure

# Internal plot settings
INITIAL_BACKEND: str = matplotlib.get_backend()
MAX_STORED_FLOORS: int = 2
PLOT_BACKEND: str = 'agg'


def restore_plot_backend() -> None:
    """
    Restores plot backend.
    """
    if plt.get_backend() == PLOT_BACKEND:
        plt.switch_backend(INITIAL_BACKEND)


class RectBinaryImage(BaseImage):
    """
    Rect binary image.

    This class creates a segmentation mask iterating all rects from a given  floor;
    obviously, this can be further extended to create other maps,  for example, for
    wall joints (points), or can be concatenated to create multiple mask tensor for
    a given crop  (like wall segments + joints). It is up to your  imagination  and
    technical abilities =). I'd say that this is the most  important class  of all.
    """
    _crop_px: int
    _initial_backend: str
    _initialized: bool
    _plot: Dict[str, Tuple['Figure', 'plt.Axes']]

    def __init__(
            self,
            path: str = '',
            save_images: bool = False,
            image_size_px: int = 64
    ) -> None:
        """
        Constructor.

        :param path: Image path
        :param save_images: Save images on path
        :param image_size_px: Image size (width/height), bigger images are expensive; double the width, quad the size
        """
        BaseImage.__init__(self, path, save_images, image_size_px)
        self._crop_px = int(math.ceil(self._image_size / 32))  # Must be greater or equal than zero
        self._initialized = False
        self._plot = {}  # Store matplotlib figures

    def init(self) -> 'RectBinaryImage':
        """
        Initialize exporter.

        :return: Self
        """
        if plt.get_backend() != PLOT_BACKEND:
            plt.switch_backend(PLOT_BACKEND)
        self._initialized = True
        self.close(restore_plot=False)
        self._initialized = True
        return self

    def _get_floor_plot(self, floor: 'Floor', store: bool) -> Tuple['Figure', 'plt.Axes']:
        """
        Get basic figure of wall rects.

        :param floor: Source floor
        :param store: Store cache of the floor
        :return: Figure of the floor
        """
        floor_id = str(floor.id)
        if floor_id in self._plot.keys():
            return self._plot[floor_id]

        fig: 'Figure' = plt.figure(frameon=False)  # Don't configure dpi
        plt.style.use('default')  # Don't modify this either
        ax: 'plt.Axes' = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.set_aspect(aspect='equal')
        ax.grid(False)  # Don't enable as this may destroy the figures

        for r in floor.rect:
            r.plot_matplotlib(
                ax=ax,
                color='#000000'
            )

        # Save
        if store:
            if len(self._plot) >= MAX_STORED_FLOORS:
                key_iter = iter(self._plot.keys())
                k1: str = next(key_iter)
                f1, _ = self._plot[k1]
                plt.close(f1)  # Close the figure
                del self._plot[k1]  # Remove
            self._plot[floor_id] = (fig, ax)

        return fig, ax

    def make_rect(self, rect: 'Rect', crop_length: NumberType = 5) -> Tuple[int, 'np.ndarray']:
        """
        Generate image for the perimeter of a given rectangle.

        :param rect: Rectangle
        :param crop_length: Size of crop from center of the rect to any edge in meters
        :return: Returns the image index and matrix
        """
        cr: 'GeomPoint2D' = rect.get_mass_center()
        return self.make_region(
            xmin=cr.x - crop_length,
            xmax=cr.x + crop_length,
            ymin=cr.y - crop_length,
            ymax=cr.y + crop_length,
            floor=rect.floor
        )

    # noinspection PyMethodMayBeStatic
    def _convert_image_color(self, im: 'Image.Image') -> 'Image.Image':
        """
        Convert image.

        :param im: Image
        :return: Converted image
        """
        return im.convert('P', palette=Image.Palette.ADAPTIVE)

    # noinspection PyMethodMayBeStatic
    def _post_process(self, im: 'Image.Image') -> 'Image.Image':
        """
        Post process image.

        :param im: Image
        :return: Post-processed image
        """
        return im

    def _make(self, xmin: NumberType, xmax: NumberType, ymin: NumberType, ymax: NumberType,
              floor: 'Floor') -> 'Image.Image':
        """
        Generate image from a given coordinate (x, y).

        :param xmin: Minimum x-axis (m)
        :param xmax: Maximum x-axis (m)
        :param ymin: Minimum y-axis (m)
        :param ymax: Maximum y-axis (m)
        :param floor: Floor object
        :return: Returns the image
        """
        fig, ax = self._get_floor_plot(floor, store=True)

        # Set the current figure
        # noinspection PyUnresolvedReferences
        plt.figure(fig.number)

        # Extent axes
        ax.set_xlim(min(xmin, xmax), max(xmin, xmax))
        ax.set_ylim(min(ymin, ymax), max(ymin, ymax))

        # Convert from matplotlib
        ram = io.BytesIO()
        plt.savefig(ram, format='png', dpi=100, bbox_inches='tight', transparent=False)
        ram.seek(0)
        im = Image.open(ram).convert('RGB')
        ram.close()
        return im

    def make_region(self, xmin: NumberType, xmax: NumberType, ymin: NumberType, ymax: NumberType,
                    floor: 'Floor') -> Tuple[int, 'np.ndarray']:
        """
        Generate image for a given region.

        :param xmin: Minimum x-axis (m)
        :param xmax: Maximum x-axis (m)
        :param ymin: Minimum y-axis (m)
        :param ymax: Maximum y-axis (m)
        :param floor: Floor object
        :return: Returns the image index and matrix
        """
        if not self._initialized:
            raise RuntimeError('Exporter not initialized, use .init()')
        t0 = time.time()

        # Make crop
        im: 'Image.Image' = self._make(xmin, xmax, ymin, ymax, floor)

        # Convert color
        im2: 'Image.Image' = self._convert_image_color(im)

        # Resize
        s_resize = self._image_size + 2 * self._crop_px
        im3: 'Image.Image' = im2.resize((s_resize, s_resize))

        # Crop
        s_crop = self._image_size + self._crop_px
        im4: 'Image.Image' = self._post_process(im3.crop((self._crop_px, self._crop_px, s_crop, s_crop)))

        # Save to file
        figname: str = f'{floor.id}-x-{xmin:.2f}-{xmax:.2f}-y-{ymin:.2f}-{ymax:.2f}'
        if self._save_images:
            assert self._path != '', 'Path cannot be empty'
            filesave = os.path.join(self._path, figname + '.png')
            im4.save(make_dirs(filesave), format='PNG')

        # noinspection PyTypeChecker
        array = np.array(im4, dtype=TYPE_IMAGE)

        # Save to array
        if self.save:
            self._images.append(array)
            self._names.append(figname)

        # Close data
        im.close()
        im2.close()
        im3.close()
        im4.close()

        # Remove data
        del im, im2, im3, im4

        # Returns the image index on the library array
        self._last_make_region_time = time.time() - t0
        return len(self._images) - 1, array

    def close(self, restore_plot: bool = True) -> None:
        """
        Close and delete all generated figures.
        This function also restores plot engine.

        :param restore_plot: Restores plotting engine
        """
        if not self._initialized:
            raise RuntimeError('Exporter not initialized, it cannot be closed')

        # Close figures
        for f in self._plot.keys():
            fig, _ = self._plot[f]
            plt.close(fig)

        # Remove
        self._plot.clear()
        self._images.clear()
        self._names.clear()

        # Restore plot
        if restore_plot:
            restore_plot_backend()

        self._initialized = False
