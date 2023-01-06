"""
MLSTRUCTFP - DB - CRECT

Rectangle component.
"""

__all__ = ['Rect']

from mlstructfp.utils import GeomLine2D

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from mlstructfp.db._cfloor import Floor


class Rect(object):
    """
    FP Rectangle.
    """
    angle: float
    floor: 'Floor'
    id: int
    length: float
    line: GeomLine2D
    thickness: float
    wall: int
    x: List[float]
    y: List[float]

    def __init__(
            self,
            rect_id: int,
            wall_id: int,
            floor: 'Floor',
            angle: float,
            length: float,
            thickness: float,
            x: List[float],
            y: List[float],
            line_m: float,
            line_n: float,
            line_theta: float
    ) -> None:
        """
        Constructor.

        :param rect_id: ID of the rect
        :param wall_id: ID of the wall
        :param floor: Floor object
        :param angle: Rect angle
        :param length: Rect length
        :param thickness: Rect thickness
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        :param line_m: Line slope
        :param line_n: Line intercept
        :param line_theta: Line angle
        """
        assert isinstance(rect_id, int) and rect_id > 0
        assert isinstance(wall_id, int) and wall_id > 0
        assert isinstance(angle, (int, float))
        assert isinstance(length, (int, float)) and length > 0
        assert isinstance(x, (list, tuple)) and len(x) > 0
        assert isinstance(y, (list, tuple)) and len(y) == len(x)
        assert isinstance(line_m, (int, float))
        assert isinstance(line_n, (int, float))
        assert isinstance(line_theta, (int, float))
        self.angle = float(angle)
        self.floor = floor
        self.floor.rect[rect_id] = self
        self.id = rect_id
        self.length = float(length)
        self.line = GeomLine2D()
        self.line.m = float(line_m)
        self.line.n = float(line_n)
        self.line.theta = float(line_theta)
        self.thickness = float(thickness)
        self.wall = wall_id
        self.x = list(x)
        self.y = list(y)
