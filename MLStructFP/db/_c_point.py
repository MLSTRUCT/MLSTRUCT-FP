"""
MLSTRUCTFP - DB - CPOINT

Point component.
"""

from MLStructFP.db._c import BasePolyComponent
from MLStructFP._types import List, TYPE_CHECKING, NumberType

import matplotlib.pyplot as plt
import plotly.graph_objects as go

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Point(BasePolyComponent):
    """
    FP Point.
    """
    topo: int  # Topological order
    wall_id: int  # Wall ID

    def __init__(
            self,
            point_id: int,
            wall_id: int,
            floor: 'Floor',
            x: List[float],
            y: List[float],
            topo: int
    ) -> None:
        """
        Constructor.

        :param point_id: ID of the point
        :param wall_id: ID of the wall
        :param floor: Floor object
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        :param topo: Topological order
        """
        BasePolyComponent.__init__(self, point_id, x, y, floor)
        self.topo = topo
        self.wall_id = wall_id
        # noinspection PyProtectedMember
        self.floor._point[point_id] = self

    def __color(self) -> str:
        """
        :return: Color based on topological order
        """
        if self.topo == 1:
            color = '#ff0000'
        elif self.topo == 2:
            color = '#00ff00'
        elif self.topo == 3:
            color = '#0000ff'
        elif self.topo == 4:
            color = '#ff00ff'
        else:
            color = '#00ffff'
        return color

    # noinspection PyUnusedLocal
    def plot_plotly(
            self,
            fig: 'go.Figure',
            dx: NumberType = 0,
            dy: NumberType = 0,
            postname: str = '',
            opacity: NumberType = 0.2,
            color: str = '',
            name: str = '',
            **kwargs
    ) -> None:
        super().plot_plotly(fig, dx, dy, opacity, self.__color() if color == '' else color,
                            f'Point ID{self.id}{postname} Wall {self.wall_id} TOPO-{self.topo}', **kwargs)

    def plot_matplotlib(
            self,
            ax: 'plt.Axes',
            linewidth: NumberType = 2.0,
            alpha: NumberType = 1.0,
            color: str = '',
            fill: bool = False
    ) -> None:
        super().plot_matplotlib(ax, linewidth, alpha, self.__color() if color == '' else color, fill)
