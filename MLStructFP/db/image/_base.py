"""
MLSTRUCT-FP - DB - IMAGE - BASE

Image of the surroundings of a rect.
"""

__all__ = ['BaseImage', 'TYPE_IMAGE']

from MLStructFP._types import TYPE_CHECKING, List, NumberType, Tuple
from MLStructFP.utils import make_dirs

import math
import numpy as np
import os

from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.db._floor import Floor

TYPE_IMAGE: str = 'uint8'


class BaseImage(ABC):
    """
    Base dataset image object.
    """
    _image_size: int
    _images: List['np.ndarray']  # List of stored images during make_region
    _last_make_region_time: float  # Total time for last make region
    _names: List[str]
    _path: str
    _save_images: bool

    patches: List['np.ndarray']  # Additional stored images
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
            make_dirs(path)
            assert os.path.isdir(path), f'Path <{path}> does not exist'

        super().__init__()
        self._image_size = image_size_px
        self._images = []
        self._names = []  # List of image names
        self._path = path
        self._save_images = save_images  # Caution, this can be file expensive

        self.patches = []
        self.save = True

    @property
    def image_shape(self) -> Tuple[int, int]:
        return self._image_size, self._image_size

    @abstractmethod
    def close(self, *args, **kwargs) -> None:
        """
        Close and delete all generated figures.
        """
        raise NotImplementedError()

    @abstractmethod
    def make_rect(self, rect: 'Rect', crop_length: NumberType) -> Tuple[int, 'np.ndarray']:
        """
        Generate image for the perimeter of a given rectangle.

        :param rect: Rectangle
        :param crop_length: Size of crop from center of the rect to any edge in meters
        :return: Returns the image index and matrix
        """
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @property
    def make_region_last_time(self) -> float:
        return self._last_make_region_time

    def export(self, filename: str, close: bool = True, compressed: bool = True) -> None:
        """
        Export saved images to numpy format and then removes all data.

        :param filename: File to export
        :param close: Close after export
        :param compressed: Save compressed file
        """
        assert len(self._images) > 0, 'Exporter cannot be empty'
        filename += f'_{self._image_size}'
        make_dirs(filename)
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

    def init(self) -> 'BaseImage':
        """
        Init the object.
        """
        return self
