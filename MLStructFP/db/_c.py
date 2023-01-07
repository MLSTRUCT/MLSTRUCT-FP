"""
MLSTRUCTFP - DB - C

Base FP component.
"""

__all__ = ['BaseComponent']

from MLStructFP.utils import GeomPoint2D

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class BaseComponent(object):
    """
    Flor plan base component.
    """
    floor: 'Floor'
    id: int
    points: List['GeomPoint2D']

    def __init__(
            self,
            component_id: int,
            x: List[float],
            y: List[float],
            floor: 'Floor'
    ) -> None:
        """
        Constructor.

        :param component_id: ID of the component
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        :param floor: Floor object
        """
        assert isinstance(component_id, int) and component_id > 0
        assert isinstance(x, (list, tuple)) and len(x) > 0
        assert isinstance(y, (list, tuple)) and len(y) == len(x)
        self.id = component_id
        self.floor = floor
        self.points = []
        for i in range(len(x)):
            self.points.append(GeomPoint2D(float(x[i]), float(y[i])))

    def plot_plotly(self, *args, **kwargs) -> None:
        """
        Plot rect.
        """
        raise NotImplementedError

    def plot_matplotlib(self, *args, **kwargs) -> None:
        """
        Plot simple using matplotlib.
        """
        raise NotImplementedError
