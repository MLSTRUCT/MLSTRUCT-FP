"""
MLSTRUCTFP - DB - CRECT

Rectangle component.
"""

__all__ = ['Rect']

from MLStructFP.db._c import BaseComponent
from MLStructFP.utils import GeomLine2D

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Rect(BaseComponent):
    """
    FP Rectangle.
    """
    angle: float
    length: float
    line: GeomLine2D
    thickness: float
    wall: int

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
        BaseComponent.__init__(self, rect_id, x, y, floor)
        assert isinstance(wall_id, int) and wall_id > 0
        assert isinstance(angle, (int, float))
        assert isinstance(length, (int, float)) and length > 0
        assert isinstance(line_m, (int, float))
        assert isinstance(line_n, (int, float))
        assert isinstance(line_theta, (int, float))
        self.angle = float(angle)
        self.length = float(length)
        self.line = GeomLine2D()
        self.line.m = float(line_m)
        self.line.n = float(line_n)
        self.line.theta = float(line_theta)
        self.thickness = float(thickness)
        self.wall = wall_id
        # noinspection PyProtectedMember
        self.floor._rect[self.id] = self

    def plot_plotly(
            self,
            fig: 'go.Figure',
            dx: float = 0,
            dy: float = 0,
            postname: str = '',
            fill: bool = False,
            opacity: float = 1.0,
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
        px, py = [p.x for p in self.points], [p.y for p in self.points]
        px.append(px[0])
        py.append(py[0])
        if color == '':
            color = '#000000'
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
            linewidth: float = 2.0,
            alpha: float = 1.0,
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
        px, py = [p.x for p in self.points], [p.y for p in self.points]
        if fill:
            ax.fill(px, py, color=color, lw=None, alpha=alpha)
        else:
            ax.plot(px, py, color=color, lw=linewidth, alpha=alpha)
