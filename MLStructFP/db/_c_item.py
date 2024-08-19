"""
MLSTRUCT-FP - DB - CITEM

Item component.
"""

__all__ = ['Item']

from MLStructFP.db._c import BasePolyObj
from MLStructFP._types import List, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Item(BasePolyObj):
    """
    FP Item.
    """

    def __init__(
            self,
            item_id: int,
            floor: 'Floor',
            x: List[float],
            y: List[float],
            color: str,
            category: int,
            category_name: str
    ) -> None:
        """
        Constructor.

        :param item_id: ID of the item
        :param floor: Floor object
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        :param color: Item color
        :param category: Item category
        :param category_name: Item category name
        """
        # noinspection PyProtectedMember
        BasePolyObj.__init__(self, floor._item, 'Item', item_id, floor, x, y, color,
                             category=category, category_name=category_name)
