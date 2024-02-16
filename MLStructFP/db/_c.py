"""
MLSTRUCTFP - DB - C

Base FP component.
"""

__all__ = ['BaseComponent', 'BasePolyComponent']

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from MLStructFP.utils import GeomPoint2D
from MLStructFP._types import List, TYPE_CHECKING, VectorInstance, NumberType

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
        assert isinstance(x, VectorInstance) and len(x) > 0
        assert isinstance(y, VectorInstance) and len(y) == len(x)
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


class BasePolyComponent(BaseComponent):
    """
    Polygonal-type base component.
    """

    def __svg_path(self, dx: NumberType = 0, dy: NumberType = 0) -> str:
        """
        Get svg path for plotting the object.

        :return: SVG path string
        :param dx: X displacement
        :param dy: Y displacement
        """
        px, py = [p.x for p in self.points], [p.y for p in self.points]
        for i in range(len(px)):  # Adds displacement (dx, dy)
            px[i] += dx
            py[i] += dy
        svg = f'M {px[0]},{py[0]}'
        for i in range(1, len(px)):
            svg += f' L{px[i]},{py[i]}'
        svg += ' Z'
        return svg

    # noinspection PyUnusedLocal
    def plot_plotly(
            self,
            fig: 'go.Figure',
            dx: NumberType,
            dy: NumberType,
            opacity: NumberType,
            color: str,
            name: str,
            **kwargs
    ) -> None:
        """
        Plot polygon object.

        :param fig: Figure object
        :param dx: X displacement
        :param dy: Y displacement
        :param opacity: Object opacity
        :param color: Color
        :param name: Object name
        :param kwargs: Optional keyword arguments
        """
        _path = self.__svg_path(dx=dx, dy=dy)
        fig.add_shape(
            fillcolor=color,
            line_color=color,
            name=name,
            opacity=opacity,
            path=_path,
            type='path'
        )

    def plot_matplotlib(
            self,
            ax: 'plt.Axes',
            linewidth: NumberType,
            alpha: NumberType,
            color: str,
            fill: bool
    ) -> None:
        """
        Plot simple using matplotlib.

        :param ax: Matplotlib axes reference
        :param linewidth: Plot linewidth
        :param alpha: Alpha transparency value (0-1)
        :param color: Plot color
        :param fill: Fill object
        """
        px, py = [p.x for p in self.points], [p.y for p in self.points]
        px.append(px[0])
        py.append(py[0])
        if fill:
            ax.fill(px, py, color=color, lw=None, alpha=alpha)
        else:
            ax.plot(px, py, '-', color=color, linewidth=linewidth, alpha=alpha)
