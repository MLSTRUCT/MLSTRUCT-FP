"""
MLSTRUCT-FP - UTILS - MATH

Math utils.
"""

__all__ = [
    'dist2',
    'dist3'
]

import math as _math


def dist2(x1: float, y1: float, x2: float = 0.0, y2: float = 0.0) -> float:
    """
    Returns the distance between (x1,y1) and (x2,y2).

    :param x1: X1
    :param y1: Y1
    :param x2: X2
    :param y2: Y2
    :return: Distance
    """
    return _math.sqrt(_math.pow(x1 - x2, 2) + _math.pow(y1 - y2, 2))


def dist3(x1: float, y1: float, z1: float, x2: float = 0.0, y2: float = 0.0, z2: float = 0.0) -> float:
    """
    Returns the distance between (x1,y1,z1) and (x2,y2,z2).

    :param x1: X1
    :param y1: Y1
    :param z1: Z1
    :param x2: X2
    :param y2: Y2
    :param z2: Z2
    :return: Distance
    """
    return _math.sqrt(_math.pow(x1 - x2, 2) + _math.pow(y1 - y2, 2) + _math.pow(z1 - z2, 2))
