"""
MLSTRUCTFP - DB - CFLOOR

Floor component, container of slabs and rectangles.
"""

__all__ = ['Floor']

import os
import plotly.graph_objects as go

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._crect import Rect
    from MLStructFP.db._cslab import Slab


class Floor(object):
    """
    FP Floor.
    """
    id: int
    image_path: str
    image_scale: float
    rect: Dict[int, 'Rect']  # id => rect
    slab: Dict[int, 'Slab']  # id => slab

    def __init__(self, floor_id: int, image_path: str, image_scale: float) -> None:
        """
        Constructor.

        :param floor_id: Floor ID
        :param image_path: Image path
        :param image_scale: Image scale (px to units)
        """
        assert isinstance(floor_id, int) and floor_id > 0
        assert os.path.isfile(image_path)
        assert isinstance(image_scale, (int, float)) and image_scale > 0
        self.id = floor_id
        self.image_path = image_path
        self.image_scale = float(image_scale)
        self.rect = {}
        self.slab = {}

    def plot_basic(self) -> 'go.Figure':
        """
        Plot basic objects.

        :return: Go figure object
        """
        return self.plot_complex(fill=False, use_complex_walls=False)

    def plot_complex(
            self,
            fill: bool = True,
            draw_rect: bool = True,
            draw_slab: bool = True,
            **kwargs
    ) -> 'go.Figure':
        """
        Complex plot.

        :param fill: Fill figure
        :param draw_rect: Draw wall rects
        :param draw_slab: Draw slabs
        :param kwargs: Optional keyword arguments
        """
        fig = go.Figure()

        if draw_slab:
            for s in self.slab.values():
                s.plot_plotly(
                    fig=fig,
                    fill=fill,
                    **kwargs
                )
        if draw_rect:
            for r in self.rect.values():
                r.plot_plotly(
                    fig=fig,
                    fill=fill,
                    **kwargs
                )

        grid_color = kwargs.get('plot_gridcolor', '#d7d7d7')
        fig.update_layout(
            plot_bgcolor=kwargs.get('plot_bgcolor', '#ffffff'),
            showlegend=kwargs.get('show_legend', True),
            title=f'Floor - ID {self.id}',
            font=dict(
                size=kwargs.get('font_size', 14),
            ),
            yaxis_zeroline=False,
            xaxis_zeroline=False,
            xaxis=dict(
                gridcolor=grid_color
            ),
            yaxis=dict(
                gridcolor=grid_color,
                scaleanchor='x',
                scaleratio=1
            )
        )
        show_grid = kwargs.get('show_grid', True)
        fig.update_layout(xaxis_showgrid=show_grid, yaxis_showgrid=show_grid)
        fig.update_xaxes(title_text='x (m)', hoverformat='.3f')
        fig.update_yaxes(title_text='y (m)', hoverformat='.3f')
        return fig
