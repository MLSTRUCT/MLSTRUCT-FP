"""
MLSTRUCTFP - DB - CFLOOR

Floor component, container of slabs and rectangles.
"""

__all__ = ['Floor']

import os

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._crect import Rect
    from MLStructFP.db._cslab import Slab


class Floor(object):
    """
    FP Floor.
    """
    id: int
    image_path: str
    image_scale: float
    rect: Dict[int, 'Rect']  # id => rect
    slab: Dict[int, 'Slab']  # id => slab

    def __init__(self, floor_id: int, image_path: str, image_scale: float) -> None:
        """
        Constructor.

        :param floor_id: Floor ID
        :param image_path: Image path
        :param image_scale: Image scale (px to units)
        """
        assert isinstance(floor_id, int) and floor_id > 0
        assert os.path.isfile(image_path)
        assert isinstance(image_scale, (int, float)) and image_scale > 0
        self.id = floor_id
        self.image_path = image_path
        self.image_scale = float(image_scale)
        self.rect = {}
        self.slab = {}
