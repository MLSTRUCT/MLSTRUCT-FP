"""
MLSTRUCTFP - DB - CSLAB

Slab component.
"""

from MLStructFP.db._c import BasePolyObj
from MLStructFP._types import List, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Slab(BasePolyObj):
    """
    FP Slab.
    """

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
        # noinspection PyProtectedMember
        BasePolyObj.__init__(self, floor._slab, 'Slab', slab_id, floor, x, y, '#666666',
                             category=0, category_name='')
