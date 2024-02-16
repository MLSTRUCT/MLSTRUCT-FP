"""
MLSTRUCTFP - DB - CSLAB

Slab component.
"""

from MLStructFP.db._c import BasePolyComponent
from MLStructFP._types import List, TYPE_CHECKING, NumberType

import matplotlib.pyplot as plt
import plotly.graph_objects as go

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class Slab(BasePolyComponent):
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
        BasePolyComponent.__init__(self, slab_id, x, y, floor)
        # noinspection PyProtectedMember
        self.floor._slab[slab_id] = self

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
        super().plot_plotly(fig, dx, dy, opacity, '#666666' if color == '' else color, f'Slab ID{self.id}{postname}',
                            **kwargs)

    def plot_matplotlib(
            self,
            ax: 'plt.Axes',
            linewidth: NumberType = 2.0,
            alpha: NumberType = 1.0,
            color: str = '',
            fill: bool = False
    ) -> None:
        super().plot_matplotlib(ax, linewidth, alpha, '#666666' if color == '' else color, fill)
