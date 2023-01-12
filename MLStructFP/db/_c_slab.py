"""
MLSTRUCTFP - DB - CSLAB

Slab component.
"""

from MLStructFP.db._c import BaseComponent
from MLStructFP._types import List, TYPE_CHECKING, NumberType

import matplotlib.pyplot as plt
import plotly.graph_objects as go

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Slab(BaseComponent):
    """
    FP Slab.
    """

    def __init__(
            self,
            slab_id: int,
            floor: 'Floor',
            x: List[float],
            y: List[float]
    ) -> None:
        """
        Constructor.

        :param slab_id: ID of the slab
        :param floor: Floor object
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        """
        BaseComponent.__init__(self, slab_id, x, y, floor)
        # noinspection PyProtectedMember
        self.floor._slab[slab_id] = self

    def svg_path(self, dx: NumberType = 0, dy: NumberType = 0) -> str:
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
            dx: NumberType = 0,
            dy: NumberType = 0,
            postname: str = '',
            opacity: NumberType = 0.2,
            color: str = '',
            **kwargs
    ) -> None:
        """
        Plot slab.

        :param fig: Figure object
        :param dx: X displacement
        :param dy: Y displacement
        :param postname: String added at the end of the name
        :param opacity: Object opacity
        :param color: Color, if empty use default object color
        :param kwargs: Optional keyword arguments
        """
        if color == '':
            color = '#666666'
        _path = self.svg_path(dx=dx, dy=dy)
        fig.add_shape(
            fillcolor=color,
            line_color=color,
            name=f'Slab ID{self.id}{postname}',
            opacity=opacity,
            path=_path,
            type='path'
        )

    def plot_matplotlib(
            self,
            ax: 'plt.Axes',
            linewidth: NumberType = 2.0,
            alpha: NumberType = 1.0
    ) -> None:
        """
        Plot simple using matplotlib.

        :param ax: Matplotlib axes reference
        :param linewidth: Plot linewidth
        :param alpha: Alpha transparency value (0-1)
        """
        px, py = [p.x for p in self.points], [p.y for p in self.points]
        px.append(px[0])
        py.append(py[0])
        ax.plot(px, py, '-', color='#666666', linewidth=linewidth, alpha=alpha)
