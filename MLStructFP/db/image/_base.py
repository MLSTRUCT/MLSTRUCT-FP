"""
MLSTRUCTFP - DB - IMAGE - BASE

Image of the surroundings of a rect.
"""

__all__ = [
    'BaseImage',
    'TYPE_IMAGE'
]

from MLStructFP._types import TYPE_CHECKING, List, NumberType, Optional, Tuple

import math
import numpy as np
import os

if TYPE_CHECKING:
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.db._floor import Floor

TYPE_IMAGE = 'uint8'


class BaseImage(object):
    """
    Base dataset image object.
    """
    _image_size: int
    _images: List['np.ndarray']
    _names: List[str]
    _path: str
    _save_images: bool
    save: bool

    def __init__(self, path: str, save_images: bool, image_size_px: int) -> None:
        """
        Constructor.

        :param path: Image path
        :param save_images: Save images on path
        :param image_size_px: Image size (width/height), bigger images are expensive, double the width, quad the size
        """
        assert image_size_px > 0 and isinstance(image_size_px, int)
        assert math.log(image_size_px, 2).is_integer(), 'Image size must be a power of 2'

        if path != '':
            os.makedirs(path, exist_ok=True)
            assert os.path.isdir(path), f'Path <{path}> does not exist'

        self._image_size = image_size_px
        self._images = []
        self._names = []  # List of image names
        self._path = path
        self._save_images = save_images  # Caution, this can be file expensive

        self.save = True

    def make_rect(self, rect: 'Rect', crop_length: NumberType) -> Tuple[int, 'np.ndarray']:
        """
        Generate image for the perimeter of a given rectangle.

        :param rect: Rectangle
        :param crop_length: Size of crop from center of the rect to any edge in meters
        :return: Returns the image index and matrix
        """
        raise NotImplementedError()

    def make_region(self, xmin: NumberType, xmax: NumberType, ymin: NumberType, ymax: NumberType,
                    floor: 'Floor', rect: Optional['Rect'] = None) -> Tuple[int, 'np.ndarray']:
        """
        Generate image for a given region.

        :param xmin: Minimum x-axis (m)
        :param xmax: Maximum x-axis (m)
        :param ymin: Minimum y-axis (m)
        :param ymax: Maximum y-axis (m)
        :param floor: Floor object
        :param rect: Optional rect for debug
        :return: Returns the image index and matrix
        """
        raise NotImplementedError()

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

    def close(self) -> None:
        """
        Close and delete all generated figures.
        """
        raise NotImplementedError()

    def get_images(self) -> 'np.ndarray':
        """
        :return: Images as numpy ndarray
        """
        return np.array(self._images, dtype=TYPE_IMAGE)

    def get_file_id(self, filename) -> int:
        """
        Returns the index of a given filename.

        :param filename: Name of the file
        :return: Index on saved list
        """
        if filename not in self._names:
            raise ValueError(f'File <{filename}> have not been processed yet')
        return self._names.index(filename)
