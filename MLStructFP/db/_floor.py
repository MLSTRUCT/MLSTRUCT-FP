"""
MLSTRUCTFP - DB - CFLOOR

Floor component, container of objects.
"""

__all__ = ['Floor']

from MLStructFP.utils import GeomPoint2D, BoundingBox
from MLStructFP._types import Dict, Tuple, Optional, TYPE_CHECKING, NumberType, NumberInstance

import math
import os
import plotly.graph_objects as go

if TYPE_CHECKING:
    from MLStructFP.db._c import BaseComponent
    from MLStructFP.db._c_rect import Rect
    from MLStructFP.db._c_point import Point
    from MLStructFP.db._c_slab import Slab
    from MLStructFP.db._c_room import Room


class Floor(object):
    """
    FP Floor.
    """
    _bb: Optional['BoundingBox']
    _last_mutation: Optional[Dict[str, float]]
    _rect: Dict[int, 'Rect']  # id => rect
    _point: Dict[int, 'Point']  # id => point
    _slab: Dict[int, 'Slab']  # id => slab
    _room: Dict[int, 'Room']  # id => room
    category: int
    category_name: str
    elevation: bool
    id: int
    image_path: str
    image_scale: float
    project_id: int

    def __init__(self, floor_id: int, image_path: str, image_scale: NumberType, project_id: int,
                 category: int = 0, category_name: str = '', elevation: bool = False) -> None:
        """
        Constructor.

        :param floor_id: Floor ID
        :param image_path: Image path
        :param image_scale: Image scale (px to units)
        :param project_id: Project ID (default: -1)
        :param category: Project category
        :param category_name: Project category name
        :param elevation: Elevation mode
        """
        assert isinstance(floor_id, int) and floor_id > 0
        assert os.path.isfile(image_path), f'Image file {image_path} does not exist'
        assert isinstance(image_scale, NumberInstance) and image_scale > 0
        assert isinstance(elevation, bool)
        self.category = category
        self.category_name = category_name
        self.elevation = elevation
        self.id = floor_id
        self.image_path = image_path.replace('\\', '/')
        self.image_scale = float(image_scale)
        self.project_id = project_id
        self._bb = None
        self._last_mutation = None
        # Object containers
        self._rect = {}
        self._point = {}
        self._slab = {}
        self._room = {}

    @property
    def rect(self) -> Tuple['Rect', ...]:
        # noinspection PyTypeChecker
        return tuple(self._rect.values())

    @property
    def point(self) -> Tuple['Point', ...]:
        # noinspection PyTypeChecker
        return tuple(self._point.values())

    @property
    def slab(self) -> Tuple['Slab', ...]:
        # noinspection PyTypeChecker
        return tuple(self._slab.values())

    @property
    def room(self) -> Tuple['Room', ...]:
        # noinspection PyTypeChecker
        return tuple(self._room.values())

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
            draw_point: bool = True,
            draw_slab: bool = True,
            draw_room: bool = True,
            draw_item: bool = True,
            **kwargs
    ) -> 'go.Figure':
        """
        Complex plot.

        :param fill: Fill figure
        :param draw_rect: Draw wall rects
        :param draw_point: Draw points
        :param draw_slab: Draw slabs
        :param draw_room: Draw rooms
        :param draw_item: Draw items
        :param kwargs: Optional keyword arguments
        """
        fig = go.Figure()

        if draw_slab:
            for o in self.slab:
                o.plot_plotly(
                    fig=fig,
                    fill=fill,
                    **kwargs
                )
        if draw_room:
            for o in self.room:
                o.plot_plotly(
                    fig=fig,
                    fill=fill,
                    **kwargs
                )
        if draw_rect:
            for o in self.rect:
                o.plot_plotly(
                    fig=fig,
                    fill=fill,
                    **kwargs
                )
        if draw_point:
            for o in self.point:
                o.plot_plotly(
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

    def mutate(self, angle: NumberType = 0, sx: NumberType = 1, sy: NumberType = 1,
               scale_first: bool = True) -> 'Floor':
        """
        Apply mutator for each object within the floor.

        :param angle: Angle
        :param sx: Scale on x-axis
        :param sy: Scale on y-axis
        :param scale_first: Scale first, then rotate
        :return: Floor reference
        """
        assert isinstance(angle, NumberInstance)
        assert isinstance(sx, NumberInstance) and sx != 0
        assert isinstance(sy, NumberInstance) and sy != 0

        # Undo last mutation
        if self._last_mutation is not None:
            _angle, _sx, _sy = self.mutator_angle, self.mutator_scale_x, self.mutator_scale_y
            self._last_mutation = None  # Reset mutation
            self.mutate(-_angle, 1 / _sx, 1 / _sy, scale_first=False)  # Reverse operation

        # Apply mutation
        rotation_center = GeomPoint2D()
        o: Tuple['BaseComponent']
        for o in (self.rect, self.point, self.slab, self.room):
            for c in o:
                for p in c.points:
                    if not scale_first:
                        p.rotate(rotation_center, angle)
                    p.x *= sx
                    p.y *= sy
                    if scale_first:
                        p.rotate(rotation_center, angle)

        # Update mutation
        self._bb = None
        self._last_mutation = {
            'angle': angle,
            'sx': sx,
            'sy': sy
        }

        return self

    @property
    def mutator_angle(self) -> float:
        return float(0 if self._last_mutation is None else self._last_mutation['angle'])

    @property
    def mutator_scale_x(self) -> float:
        return float(1 if self._last_mutation is None else self._last_mutation['sx'])

    @property
    def mutator_scale_y(self) -> float:
        return float(1 if self._last_mutation is None else self._last_mutation['sy'])

    @property
    def bounding_box(self) -> 'BoundingBox':
        """
        :return: Return the bounding box of the floor, calculated using the slab and the points from the rects.
        """
        if self._bb is not None:
            return self._bb
        xmin = math.inf
        xmax = -math.inf
        ymin = math.inf
        ymax = -math.inf
        o: Tuple['BaseComponent']
        for o in (self.rect, self.slab):
            for c in o:
                for p in c.points:
                    xmin = min(xmin, p.x)
                    xmax = max(xmax, p.x)
                    ymin = min(ymin, p.y)
                    ymax = max(ymax, p.y)
        self._bb = BoundingBox(xmin, xmax, ymin, ymax)
        return self._bb
