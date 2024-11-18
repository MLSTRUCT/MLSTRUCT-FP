"""
MLSTRUCT-FP - DB - CRECT

Rectangle component (wall segment).
"""

__all__ = ['Rect']

from MLStructFP.db._c import BaseComponent
from MLStructFP._types import NumberType, NumberInstance, List, TYPE_CHECKING
from MLStructFP.utils import GeomLine2D, GeomPoint2D

import matplotlib.pyplot as plt
import plotly.graph_objects as go

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Rect(BaseComponent):
    """
    FP Rectangle.
    """
    angle: float
    length: float
    line: GeomLine2D
    partition: bool
    thickness: float
    wall: int

    def __init__(
            self,
            rect_id: int,
            wall_id: int,
            floor: 'Floor',
            angle: NumberType,
            length: NumberType,
            thickness: NumberType,
            x: List[float],
            y: List[float],
            line_m: NumberType,
            line_n: NumberType,
            line_theta: NumberType,
            partition: bool
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
        :param partition: Rect is partition wall
        """
        BaseComponent.__init__(self, rect_id, x, y, floor)
        assert isinstance(wall_id, int) and wall_id > 0
        assert isinstance(angle, NumberInstance)
        assert isinstance(length, NumberInstance) and length > 0
        assert isinstance(line_m, NumberInstance)
        assert isinstance(line_n, NumberInstance)
        assert isinstance(line_theta, NumberInstance)
        assert isinstance(partition, bool)
        self.angle = float(angle)
        self.length = float(length)
        self.line = GeomLine2D()
        self.line.m = float(line_m)
        self.line.n = float(line_n)
        self.line.theta = float(line_theta)
        self.partition = partition
        self.thickness = float(thickness)
        self.wall = wall_id
        # noinspection PyProtectedMember
        self.floor._rect[self.id] = self

    def get_mass_center(self) -> 'GeomPoint2D':
        """
        Returns the mass center of the rect.
        """
        return GeomPoint2D(sum(p.x for p in self._points), sum(p.y for p in self._points)).scale(1 / len(self._points))

    def plot_plotly(
            self,
            fig: 'go.Figure',
            dx: NumberType = 0,
            dy: NumberType = 0,
            postname: str = '',
            fill: bool = False,
            opacity: NumberType = 1.0,
            color: str = '',
            show_legend: bool = True
    ) -> None:
        """
        Plot rect.

        :param fig: Figure object
        :param dx: X displacement
        :param dy: Y displacement
        :param postname: String added at the end of the name
        :param fill: Fill figure
        :param opacity: Object opacity
        :param color: Color, if empty use default object color
        :param show_legend: Add object legend to plot
        """
        px, py = [p.x for p in self._points], [p.y for p in self._points]
        px.append(px[0])
        py.append(py[0])
        if color == '':
            color = '#0000ff'
        for i in range(len(px)):
            px[i] += dx
            py[i] += dy
        _fill = 'none'
        if fill:
            _fill = 'toself'
        fig.add_trace(go.Scatter(
            fill=_fill,
            line=dict(color=color),
            mode='lines',
            name=f'Rect ID {self.id} - W {self.wall} ∢{round(self.angle, 3)}°{postname}',
            opacity=opacity,
            showlegend=show_legend,
            x=px,
            y=py
        ))

    def plot_matplotlib(
            self,
            ax: 'plt.Axes',
            linewidth: NumberType = 2.0,
            alpha: NumberType = 1.0,
            color: str = '',
            fill: bool = True
    ) -> None:
        """
        Plot simple using matplotlib.

        :param ax: Matplotlib axes reference
        :param linewidth: Plot linewidth
        :param alpha: Alpha transparency value (0-1)
        :param color: Override color
        :param fill: Fill rect object
        """
        if color == '':
            color = '#000000'
        px, py = [p.x for p in self._points], [p.y for p in self._points]
        if fill:
            ax.fill(px, py, color=color, lw=None, alpha=alpha)
        else:
            ax.plot(px, py, color=color, lw=linewidth, alpha=alpha)
