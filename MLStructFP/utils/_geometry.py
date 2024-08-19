"""
MLSTRUCT-FP - DB - LINE 2D

Line definition class.
"""

__all__ = [
    'BoundingBox',
    'GeomLine2D',
    'GeomPoint2D'
]

from MLStructFP.utils._mathlib import dist2
from MLStructFP._types import Dict, Any, List, Union, Tuple, NumberType, NumberInstance

import math
import matplotlib.pyplot as plt

MIN_TOL: float = 1e-12


class GeomLine2D(object):
    """
    Geometric 2d segment between 2 points.
    """
    _def_points: Dict[str, 'GeomPoint2D']
    m: NumberType
    n: NumberType
    theta: NumberType

    def __init__(self) -> None:
        """
        Constructor.
        """
        self.m = 0.0
        self.theta = 0.0
        self.n = 0.0
        self._def_points = dict(
            p1=GeomPoint2D(),
            p2=GeomPoint2D()
        )

    def clone(self) -> 'GeomLine2D':
        """
        Returns a cloned object.

        :return: New line
        """
        line = GeomLine2D()
        line.m = self.m
        line.theta = self.theta
        line.n = self.n
        line._def_points['p1'] = self._def_points['p1'].clone()
        line._def_points['p2'] = self._def_points['p2'].clone()
        return line

    def __str__(self) -> str:
        return f'y = {self.m}*x + {self.n}. Theta: {self.theta}'

    def __repr__(self) -> str:
        return str(self)

    def from_2_points(self, p1: 'GeomPoint2D', p2: 'GeomPoint2D') -> 'GeomLine2D':
        """
        Set line from 2 points.

        :param p1: Point 1
        :param p2: Point 2
        :return: Self
        """
        self._def_points['p1'] = p1.clone()
        self._def_points['p2'] = p2.clone()
        m_a = p2.y - p1.y
        m_b = p2.x - p1.x + MIN_TOL
        self.m = m_a / m_b
        self.n = (-self.m * p1.x) + p2.y
        self.theta = math.atan2(m_a, m_b)
        return self

    def eval(self, x: NumberType) -> NumberType:
        """
        Eval line at given value.

        :param x: Evaluation point
        :return: Evaluated Ƒ(x)
        """
        return (self.m * x) + self.n

    def f(self, x: NumberType) -> 'GeomPoint2D':
        """
        Returns new point from (x,Ƒ(x)).

        :param x: Evaluation point
        :return: New point
        """
        return GeomPoint2D(x, self.eval(x))

    def _check_def_none(self) -> None:
        """
        Checks defined points are none.
        """
        if self._def_points['p1'] is None or self._def_points['p2'] is None:
            self._def_points['p1'] = self.f(0)
            self._def_points['p2'] = self.f(1)

    def point_left(self, p: 'GeomPoint2D') -> bool:
        """
        Check point is at left of the segment.

        :param p: Point
        :return: True if the point is located at the left of the segment
        """
        self._check_def_none()
        p1: 'GeomPoint2D' = self._def_points['p1']
        p2: 'GeomPoint2D' = self._def_points['p2']
        return (((p2.x - p1.x) * (p.y - p1.y)) - ((p2.y - p1.y) * (p.x - p1.x))) > 0

    def point_on(self, p: 'GeomPoint2D') -> bool:
        """
        Check point on segment.

        :param p: Point
        :return: True if point is on the segment
        """
        self._check_def_none()
        p1: 'GeomPoint2D' = self._def_points['p1']
        p2: 'GeomPoint2D' = self._def_points['p2']
        return math.fabs((((p2.x - p1.x) * (p.y - p1.y)) - ((p2.y - p1.y) * (p.x - p1.x)))) < MIN_TOL

    def ortho_distance_point_list(self, point_list: List['GeomPoint2D']) -> List[NumberType]:
        """
        Calculate the orthographic distance from a point.

        :param point_list: Point list
        :return: Distance list
        """
        dist = []
        for i in range(len(point_list)):
            dist.append(self.ortho_distance_point(point_list[i]))
        return dist

    def ortho_distance_point(self, p: 'GeomPoint2D') -> NumberType:
        """
        Returns the orthographic distance from a point.

        :param p: Point
        :return: Distance
        """
        a = -self.m
        b = 1
        c = -self.n
        return math.fabs((a * p.x) + (b * p.y) + c) / dist2(a, b)

    def ortho_distance_line(self, line: 'GeomLine2D', force: bool = False) -> NumberType:
        """
        Calculate the orthographic distance from another line.

        :param line: Line
        :param force: If true, vertical segments will be evaluated on x-axis
        :return: Distance
        """
        if math.fabs(math.fabs(self.m) - math.fabs(line.m)) > 1e-4:
            if not force:
                return math.inf
            else:
                return math.fabs(self.eval(0) - line.eval(0))
        return math.fabs(self.n - line.n) / dist2(1, self.m)


class GeomPoint2D(object):
    """
    2D coordinate.
    """
    _data: Dict[str, Any]
    x: NumberType
    y: NumberType

    def __init__(self, x: NumberType = 0, y: NumberType = 0) -> None:
        """
        Constructor.

        :param x: X coordinate
        :param y: Y coordinate
        """
        assert isinstance(x, NumberInstance)
        assert isinstance(y, NumberInstance)
        self.x = float(x)
        self.y = float(y)
        self._data = {}  # Point inner data

    def __eq__(self, other: 'GeomPoint2D') -> bool:
        return math.fabs(self.x - other.x) <= MIN_TOL and math.fabs(self.y - other.y) <= MIN_TOL

    def __ne__(self, other: 'GeomPoint2D') -> bool:
        """
        Returns true if points are not equal.

        :param other: Point
        :return: bool
        """
        return math.fabs(self.x - other.x) > MIN_TOL or math.fabs(self.y - other.y) > MIN_TOL

    def __mul__(self, other: 'GeomPoint2D') -> 'GeomPoint2D':
        """
        Multiply point with another.

        :param other: Point
        :return: Self
        """
        self.x *= other.x
        self.y *= other.y
        return self

    def __add__(self, other: 'GeomPoint2D') -> 'GeomPoint2D':
        """
        Add point with another.

        :param other: Point
        :return: Self
        """
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: 'GeomPoint2D') -> 'GeomPoint2D':
        """
        Subtract point with another.

        :param other: Point
        :return: Self
        """
        self.x -= other.x
        self.y -= other.y
        return self

    def __str__(self) -> str:
        return f'({self.x},{self.y})'

    def __repr__(self) -> str:
        return str(self)

    def list(self) -> List[float]:
        """
        Returns the point as a list.

        :return: Point list [x,y]
        """
        return [self.x, self.y]

    def tuple(self) -> Tuple[float, float]:
        """
        Returns the tuple of the point.

        :return: Tuple (x, y)
        """
        return self.x, self.y

    def rotate(self, center: 'GeomPoint2D', angle: float = 0) -> 'GeomPoint2D':
        """
        Rotate the point around a given center.

        :param center: Rotation center
        :param angle: Rotation angle, angles in degrees
        :return: Self
        """
        if angle == 0:
            return self

        s = math.sin(angle * math.pi / 180)
        c = math.cos(angle * math.pi / 180)

        # Translate
        self.x -= center.x
        self.y -= center.y

        # Rotate
        new_x = self.x * c - self.y * s
        new_y = self.x * s + self.y * c

        # Update
        self.x = new_x + center.x
        self.y = new_y + center.y
        return self

    def scale(self, s: float) -> 'GeomPoint2D':
        """
        Scale point with number.

        :param s: Scale factor
        :return: Self
        """
        self.x *= s
        self.y *= s
        return self

    def dist(self, other: 'GeomPoint2D') -> float:
        """
        Returns the distance between two points.

        :param other: Point
        :return: Distance
        """
        return dist2(self.x, self.y, other.x, other.y)

    def angle(self, other: Union['GeomPoint2D', List['GeomPoint2D']]) -> Union[float, List[float]]:
        """
        Returns the angle between two points.

        :param other: Point
        :return: Angle
        """
        if isinstance(other, list):
            dist = []
            for i in range(len(other)):
                dist.append(self.angle(other[i]))
            return dist
        if self.x == other.x and self.y == other.y:
            return 0.0
        return math.atan2(other.y - self.y, other.x - self.x)

    def set_property(self, key: str, data: Any) -> None:
        """
        Set point property.

        :param key: Key
        :param data: Data
        """
        if data is None:
            return
        assert isinstance(key, str)
        self._data[key] = data

    def get_property(self, key: str, default: Any = None) -> Any:
        """
        Get point property.

        :param key: Key
        :param default: Data
        :return: Value
        """
        if not self.has_property(key):
            return default
        return self._data[key]

    def has_property(self, key: str) -> bool:
        """
        Returns true if point has data.

        :param key: Key
        :return: True if key exists
        """
        return key in self._data.keys()

    def clone(self) -> 'GeomPoint2D':
        """
        Clone point.

        :return: New point
        """
        p = GeomPoint2D(self.x, self.y)
        for k in self._data.keys():
            p.set_property(k, self.get_property(k))
        return p

    def equals(self, other: 'GeomPoint2D') -> bool:
        """
        Points is equal to another.

        :param other: Point
        :return: True if points is equal
        """
        return math.fabs(self.x - other.x) < MIN_TOL and math.fabs(self.y - other.y) < MIN_TOL

    def set_zero(self) -> None:
        """
        Set point as zero.
        """
        self.x = 0
        self.y = 0

    def plot(self, ax: 'plt.Axes', color='#000000', marker_size: int = 10, style: str = '.') -> None:
        """
        Plot point.

        :param ax: Matplotlib axes
        :param color: Marker color
        :param marker_size: Marker size
        :param style: Marker style
        """
        assert isinstance(ax, plt.Axes)
        assert isinstance(color, str)
        assert isinstance(marker_size, int)
        assert isinstance(style, str)
        ax.plot(self.x, self.y, style, markersize=marker_size, color=color)


class BoundingBox(object):
    """
    Represents a bounding box from (xmin, xmax) to (ymin, ymax).
    """
    __xmin: NumberType
    __xmax: NumberType
    __ymin: NumberType
    __ymax: NumberType

    def __init__(self, xmin: NumberType, xmax: NumberType, ymin: NumberType, ymax: NumberType) -> None:
        """
        Constructor.
        """
        self.__xmin = xmin
        self.__xmax = xmax
        self.__ymin = ymin
        self.__ymax = ymax

    @property
    def xmin(self) -> NumberType:
        return self.__xmin

    @property
    def xmax(self) -> NumberType:
        return self.__xmax

    @property
    def ymin(self) -> NumberType:
        return self.__ymin

    @property
    def ymax(self) -> NumberType:
        return self.__ymax

    def __repr__(self) -> str:
        return f'BB: x({self.xmin},{self.xmax}), y({self.ymin},{self.ymax})'
