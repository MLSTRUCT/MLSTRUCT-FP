"""
MLSTRUCT-FP - DB - CROOM

Room component.
"""

__all__ = ['Room']

from MLStructFP.db._c import BasePolyObj
from MLStructFP._types import List, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Room(BasePolyObj):
    """
    FP Room.
    """

    def __init__(
            self,
            room_id: int,
            floor: 'Floor',
            x: List[float],
            y: List[float],
            color: str,
            category: int,
            category_name: str
    ) -> None:
        """
        Constructor.

        :param room_id: ID of the room
        :param floor: Floor object
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        :param color: Room color
        :param category: Room category
        :param category_name: Room category name
        """
        # noinspection PyProtectedMember
        BasePolyObj.__init__(self, floor._room, 'Room', room_id, floor, x, y, color,
                             category=category, category_name=category_name)
