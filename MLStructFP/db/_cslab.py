"""
MLSTRUCTFP - DB - CSLAB

Slab component.
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._cfloor import Floor


class Slab(object):
    """
    FP Slab.
    """
    floor: 'Floor'
    slab_id: int
    x: List[float]
    y: List[float]

    def __init__(
            self,
            slab_id: int,
            floor: 'Floor',
            x: List[float],
            y: List[float]
    ) -> None:
        """
        Constructor.

        :param slab_id: ID of the slab
        :param floor: Floor object
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        """
        assert isinstance(slab_id, int) and slab_id > 0
        assert isinstance(x, (list, tuple)) and len(x) > 0
        assert isinstance(y, (list, tuple)) and len(y) == len(x)
        self.floor = floor
        self.floor.slab[slab_id] = self
        self.slab_id = slab_id
        self.x = list(x)
        self.y = list(y)
