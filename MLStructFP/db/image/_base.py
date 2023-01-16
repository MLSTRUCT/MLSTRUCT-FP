"""
MLSTRUCTFP - DB - IMAGE - BASE

Image of the surroundings of a rect.
"""

__all__ = ['BaseImage']

from MLStructFP._types import TYPE_CHECKING, List, NumberType

import math
import numpy as np
import os

if TYPE_CHECKING:
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.db._floor import Floor


class BaseImage(object):
    """
    Base dataset image object.
    """
    _crop_length: NumberType
    _image_size: int
    _images: List['np.ndarray']
    _names: List[str]
    _path: str
    _save_images: bool
    save: bool

    def __init__(self, path: str, save_images: bool, image_size_px: int, crop_length: NumberType) -> None:
        """
        Constructor.

        :param path: Image path
        :param save_images: Save images on path
        :param image_size_px: Image size (width/height), bigger images are expensive, double the width, quad the size
        :param crop_length: Size of crop from center of the rect to any edge in meters
        """
        assert image_size_px > 0
        assert crop_length > 0
        assert math.log(image_size_px, 2).is_integer(), 'Image size must be a power of 2'

        if path != '':
            os.makedirs(path, exist_ok=True)
            assert os.path.isdir(path), f'Path <{path}> does not exist'

        self._crop_length = crop_length  # This produces blocks of (2*BOUNDFACTOR x 2*BOUNDFACTOR) size
        self._image_size = image_size_px
        self._images = []
        self._names = []  # List of image names
        self._path = path
        self._save_images = save_images  # Caution, this can be file expensive

        self.save = True

    def make(self, rect: 'Rect') -> int:
        """
        Generate image for a given rect.
        """
        raise NotImplementedError()

    def make_floor(self, floor: 'Floor') -> None:
        """
        Make all rect images from a given floor.

        :param floor: Floor object
        """
        for r in floor.rect:
            self.make(r)

    def export(self, *args, **kwargs) -> None:
        """
        Export image.
        """
        raise NotImplementedError()

    def close(self) -> None:
        """
        Close and delete all generated figures.
        """
        raise NotImplementedError()
