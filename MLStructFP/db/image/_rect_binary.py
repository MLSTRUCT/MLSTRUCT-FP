"""
MLSTRUCTFP - DB - IMAGE - RECT BINARY

Image of the surroundings of a rect.
"""

__all__ = ['RectBinaryImage']

from MLStructFP.db.image._base import BaseImage
from MLStructFP._types import TYPE_CHECKING, Tuple, Dict, NumberType

from PIL import Image
import cv2
import io
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os

# import matplotlib as mpl
# mpl.rcParams['savefig.pad_inches'] = 0

if TYPE_CHECKING:
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.utils import GeomPoint2D
    from matplotlib.figure import Figure

HIGHLIGHT_RECT = False
HIGHLIGHT_RECT_COLOR = '#FF0000'
MAX_STORED_FLOORS = 2
RECT_COLOR = '#000000'
TYPE_IMAGE = 'uint8'

assert HIGHLIGHT_RECT_COLOR != HIGHLIGHT_RECT, 'Highlight color must be different'
INITIAL_BACKEND = matplotlib.get_backend()


class RectBinaryImage(BaseImage):
    """
    Rect binary image.
    """
    _crop_px: int
    _initial_backend: str
    _initialized: bool
    _plot: Dict[str, Tuple['Figure', 'plt.Axes']]

    def __init__(
            self,
            path: str = '',
            save_images: bool = False,
            image_size_px: int = 64,
            crop_length: NumberType = 5.0
    ) -> None:
        """
        Constructor.

        :param path: Image path
        :param save_images: Save images on path
        :param image_size_px: Image size (width/height), bigger images are expensive, double the width, quad the size
        :param crop_length: Size of crop from center of the rect to any edge in meters
        """
        BaseImage.__init__(self, path, save_images, image_size_px, crop_length)
        self._crop_px = int(math.ceil(self._image_size / 32))  # Must be greater or equal than zero
        self._initialized = False
        self._plot = {}  # Store matplotlib figures

    def init(self) -> 'RectBinaryImage':
        """
        Initialize exporter.

        :return: Self
        """
        plt.switch_backend('agg')
        self._initialized = True
        self.close()
        self._initialized = True
        return self

    def _get_floor_plot(self, rect: 'Rect', store: bool) -> Tuple['Figure', 'plt.Axes']:
        """
        Get basic figure of wall rects.

        :param rect: Source rect
        :param store: Store cache of the floor
        :return: Figure of the floor
        """
        floor_id = str(rect.floor.id)

        if floor_id in self._plot.keys():
            return self._plot[floor_id]

        fig: 'Figure'
        ax: 'plt.Axes'
        fig = plt.figure(frameon=False)  # Don't configure dpi
        plt.style.use('default')  # Don't modify this either
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.set_aspect(aspect='equal')
        ax.grid(False)  # Don't enable as this may destroy the figures

        for r in rect.floor.rect:
            r.plot_matplotlib(
                ax=ax,
                color=RECT_COLOR if rect.id != r.id or not HIGHLIGHT_RECT else HIGHLIGHT_RECT_COLOR
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

    def make(self, rect: 'Rect') -> int:
        """
        Generate image.

        :return: Returns the image index on the library array
        """
        if not self._initialized:
            raise RuntimeError('Exporter not initialized, use .init()')
        store_matplotlib_figure = not HIGHLIGHT_RECT
        fig, ax = self._get_floor_plot(rect, store=store_matplotlib_figure)

        # Set the current figure
        # noinspection PyUnresolvedReferences
        plt.figure(fig.number)

        # Save the figure
        figname = f'{rect.id}'

        # Zoom to rect
        cr: 'GeomPoint2D' = rect.get_mass_center()

        # Compute crop area
        xmin = cr.x - self._crop_length
        xmax = cr.x + self._crop_length
        ymin = cr.y - self._crop_length
        ymax = cr.y + self._crop_length

        ax.set_xlim(min(xmin, xmax), max(xmin, xmax))
        ax.set_ylim(min(ymin, ymax), max(ymin, ymax))

        # Convert
        ram = io.BytesIO()
        plt.savefig(ram, format='png', dpi=100, bbox_inches='tight', transparent=False)
        ram.seek(0)
        im: 'Image.Image' = Image.open(ram)

        im2: 'Image.Image' = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
        # im2 = im.convert('RGB')  # Produces larger files
        # im2 = im.convert('1')

        # Resize
        s_resize = self._image_size + 2 * self._crop_px
        im3: 'Image.Image' = im2.resize((s_resize, s_resize))

        # Crop
        s_crop = self._image_size + self._crop_px
        im4: 'Image.Image' = im3.crop((self._crop_px, self._crop_px, s_crop, s_crop))

        # Save to file
        if self._save_images:
            assert self._path != '', 'Path cannot be empty'
            filesave = os.path.join(self._path, figname + '.png')
            im4.save(filesave, format='PNG')
            # print('Rect {0} saved to {1}'.format(rect.id, filesave))

        # Save to array
        if self.save:
            # noinspection PyTypeChecker
            array = np.array(im4, dtype=TYPE_IMAGE)
            # array = np.where(array > 0, 0, 1)
            self._images.append(array)
            # self._images.append(array)
            self._names.append(figname)
            del array

        # Close data
        ram.close()
        im.close()
        im2.close()
        im3.close()
        im4.close()

        if not store_matplotlib_figure:
            plt.close(fig)

        # Remove data
        del im, im2, im3, im4, fig, ax

        # Returns the image index on the library array
        return len(self._images) - 1

    def save_image_id(self, im_id: int, filename: str) -> None:
        """
        Save image to file.

        :param im_id: Image ID
        :param filename: Filename
        """
        assert 0 <= im_id < len(self._images), 'Invalid image ID'
        cv2.imwrite(filename, (1 - self._images[im_id]) * 255)

    def close(self) -> None:
        """
        Close and delete all generated figures.
        """
        if not self._initialized:
            raise RuntimeError('Exporter not initialized, it cannot be closed')

        # Close figures
        for f in self._plot.keys():
            fig, _ = self._plot[f]
            plt.close(fig)

        # Remove plots
        del self._plot
        self._plot = {}

        # Remove images
        del self._images
        self._images = []

        # Remove names
        del self._names
        self._names = []

        self._initialized = False

    @staticmethod
    def restore_plot() -> None:
        """
        Restore plot backend.
        """
        if plt.get_backend() == 'agg':
            plt.switch_backend(INITIAL_BACKEND)

    def get_file_id(self, filename) -> int:
        """
        Returns the index of a given filename.

        :param filename: Name of the file
        :return: Index on saved list
        """
        if filename not in self._names:
            raise ValueError(f'File <{filename}> have not been processed yet')
        return self._names.index(filename)

    def get_images(self) -> 'np.ndarray':
        """
        :return: Images as numpy ndarray
        """
        return np.array(self._images, dtype=TYPE_IMAGE)

    def export(self, filename: str, close: bool = True, compressed: bool = True) -> None:
        """
        Export saved images to numpy format and remove all data.

        :param filename: File to export
        :param close: Close after export
        :param compressed: Save compressed file
        """
        assert len(self._images) > 0, 'Exporter cannot be empty'
        filename += f'_{self._image_size}'
        if compressed:
            np.savez_compressed(filename, data=self.get_images())  # .npz
        else:
            np.save(filename, self.get_images())  # .npy
        imnames = open(filename + '_files.csv', 'w', encoding='utf-8')
        imnames.write('ID,File\n')
        for i in range(len(self._names)):
            imnames.write(f'{i},{self._names[i]}\n')
        imnames.close()
        if close:
            self.close()
