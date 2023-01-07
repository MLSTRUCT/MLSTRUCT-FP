"""
MLSTRUCTFP - DB - CFLOOR

Floor component, container of slabs and rectangles.
"""

__all__ = ['Floor']

from MLStructFP.utils import GeomPoint2D

import os
import plotly.graph_objects as go

from typing import Dict, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from MLStructFP.db._c import BaseComponent
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.db._c_slab import Slab


class Floor(object):
    """
    FP Floor.
    """
    _last_mutation: Optional[Dict[str, float]]
    _rect: Dict[int, 'Rect']  # id => rect
    _slab: Dict[int, 'Slab']  # id => slab
    id: int
    image_path: str
    image_scale: float

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
        self._last_mutation = None
        self._rect = {}
        self._slab = {}

    @property
    def rect(self) -> Tuple['Rect']:
        return tuple(self._rect.values())

    @property
    def slab(self) -> Tuple['Slab']:
        return tuple(self._slab.values())

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
            for s in self.slab:
                s.plot_plotly(
                    fig=fig,
                    fill=fill,
                    **kwargs
                )
        if draw_rect:
            for r in self.rect:
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

    def mutate(self, angle: float, sx: float, sy: float) -> 'Floor':
        """
        Apply mutator for each object within the floor.

        :param angle: Angle
        :param sx: Scale on x-axis
        :param sy: Scale on y-axis
        :return: Floor reference
        """
        assert isinstance(angle, (int, float))
        assert isinstance(sx, (int, float)) and sx != 0
        assert isinstance(sy, (int, float)) and sy != 0

        # Undo last mutation
        if self._last_mutation is not None:
            _angle, _sx, _sy = self._last_mutation['angle'], self._last_mutation['sx'], self._last_mutation['sy']
            self._last_mutation = None
            self.mutate(_angle, _sx, _sy)

        # Apply mutation
        rotation_center = GeomPoint2D()
        o: Tuple['BaseComponent']
        for o in (self.rect, self.slab):
            for c in o:
                for p in c.points:
                    p.x *= sx
                    p.y *= sy
                    p.rotate(rotation_center, angle)

        # Update mutation
        self._last_mutation = {
            'angle': -angle,
            'sx': 1 / sx,
            'sy': 1 / sy
        }

        return self
