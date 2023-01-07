"""
MLSTRUCTFP - UTILS - PLOT - FLOOR

Display floors in 2D plots.
"""

__all__ = ['FloorPlot']

from MLStructFP.utils._geometry import GeomPoint2D
from MLStructFP.utils.plot._generic import GenericPlot
from MLAi.utils import configure_figure, DEFAULT_PLOT_DPI, typechecked

from typing import TYPE_CHECKING, List
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import statistics

if TYPE_CHECKING:
    from MLAi.assemble.api import ObjFloor, ObjSlab, ObjWall, ObjWallRect
    from matplotlib.figure import Figure


class FloorPlot(GenericPlot):
    """
    2D floor plot.
    """

    _floor: 'ObjFloor'

    def __init__(self, floor: 'ObjFloor') -> None:
        """
        Constructor.

        :param floor: Floor object
        """
        super().__init__()
        self._floor = floor

    def basic(self) -> 'go.Figure':
        """
        Plot basic objects.

        :return: Go figure object
        """
        return self.complex(fill=False, use_complex_walls=False)

    def complex(
            self,
            fill: bool = True,
            draw_wall_point: bool = True,
            draw_wall_rect: bool = True,
            draw_slab: bool = True,
            use_complex_walls: bool = True,
            **kwargs
    ) -> 'go.Figure':
        """
        Complex plot.

        :param fill: Fill figure
        :param draw_wall_point: Draw wall points
        :param draw_wall_rect: Draw wall rects
        :param draw_slab: Draw slabs
        :param use_complex_walls: Use complex walls in plot
        :param kwargs: Optional keyword arguments
        """
        fig = go.Figure()

        def add_wall(wall: 'ObjWall') -> None:
            """
            Add wall to plot.

            :param wall: Wall
            """
            wall.plot_plotly(
                fig=fig,
                basic=not use_complex_walls,
                fill=fill,
                draw_rect=draw_wall_rect,
                draw_point=draw_wall_point,
                **kwargs
            )

        def add_slab(slab: 'ObjSlab') -> None:
            """
            Add slab to plot.

            :param slab: Slab
            """
            slab.plot_plotly(fig, **kwargs)

        if draw_slab:
            self._floor.each_slab(add_slab)
        if draw_wall_rect or draw_wall_point:
            self._floor.each_wall(add_wall)

        grid_color = kwargs.get('plot_gridcolor', '#d7d7d7')
        fig.update_layout(
            plot_bgcolor=kwargs.get('plot_bgcolor', '#ffffff'),
            showlegend=kwargs.get('show_legend', True),
            title=f'Floor {self._floor.full_label()} - ID {self._floor.id}',
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

    def rect_projection(
            self,
            rect_id: int,
            proj_type: str,
            fill: bool = False
    ) -> 'go.Figure':
        """
        Plot wall rect projections.

        :param rect_id: Rect object ID
        :param proj_type: Projection type 'bottom', 'top'
        :param fill: Fill figures
        :return: Go figure object
        """
        rect = self._floor.get_wall_rect(rect_id)
        return rect.get_wall().plot.rect_projection(rect_id=rect_id, proj_type=proj_type, fill=fill)

    def rect_triangulation(self, rect_id: int) -> 'go.Figure':
        """
        Plot wall rect triangulation elements.

        :param rect_id: Rect object ID
        """
        rect = self._floor.get_wall_rect(rect_id)
        return rect.get_wall().plot.rect_triangulation(rect_id=rect_id)

    def triangulation_delaunay(
            self,
            grid: bool = True,
            rect: bool = True,
            slab: bool = True
    ) -> 'Figure':
        """
        Plot constrained delaunay triangulation w/matplotlib.

        :param grid: Show grid
        :param rect: Plots the rect objects
        :param slab: Plots the slab object
        :return: Plot object
        """
        t = self._floor.get_triangulation()
        # noinspection PyTypeChecker
        vv = np.array(t['vertices'].tolist())
        tt = t['triangles'].tolist()
        fig, ax = plt.subplots(dpi=DEFAULT_PLOT_DPI)
        plt.triplot(vv[:, 0], vv[:, 1], tt, alpha=0.5, linewidth=1)

        def _plot_slab(s: 'ObjSlab') -> None:
            """
            Plot object slabs.
            """
            s.plot_matplotlib(ax, linewidth=2, alpha=0.75)

        def _plot_rect(r: 'ObjWallRect') -> None:
            """
            Plot object rects.
            """
            r.plot_matplotlib(ax, linewidth=3)

        if slab:
            self._floor.each_slab(_plot_slab)
        if rect:
            self._floor.each_wall_rect(_plot_rect)
        plt.plot(vv[:, 0], vv[:, 1], 'o', markersize=3)
        plt.xlabel('x (m)')
        plt.ylabel('y (m)')
        plt.title(f'Constrained Delaunay Triangulation - Floor {self._floor.label} ID {self._floor.id}')
        plt.axis('equal')
        kwargs = {'cfg_grid': grid}
        configure_figure(**kwargs)
        return fig

    def voronoi_diagram(self, **kwargs) -> 'Figure':
        """
        Plot voronoi diagram w/matplotlib.

        :param kwargs: Optional keyword arguments
        :return: Plot object
        """
        v = self._floor.get_voronoi()
        edges = v['edges']
        vert = v['points']
        fig, ax = plt.subplots(dpi=DEFAULT_PLOT_DPI)

        def _point_inside(p: List[float]) -> bool:
            """
            Returns true if the point is inside the floor.

            :param p: Point
            :return: True if inside
            """
            return self._floor.point_inside(GeomPoint2D(p[0], p[1]))

        # Plot lines
        for e in edges:
            v1 = vert[e[0]]
            v2 = vert[e[1]]
            if not _point_inside(v1) or not _point_inside(v2):
                continue
            plt.plot([v1[0], v2[0]], [v1[1], v2[1]], 'k-', linewidth=1)

        def _plot_slab(s: 'ObjSlab') -> None:
            s.plot_matplotlib(ax, linewidth=2, alpha=0.75)

        def _plot_rect(r: 'ObjWallRect') -> None:
            r.plot_matplotlib(ax, linewidth=3)

        self._floor.each_slab(_plot_slab)
        self._floor.each_wall_rect(_plot_rect)
        plt.title(f'Voronoi Diagram - Floor {self._floor.label} ID {self._floor.id}')
        plt.xlabel('x (m)')
        plt.ylabel('y (m)')
        configure_figure(**kwargs)
        return fig

    def assoc_hist(self, nbins: int = 20, **kwargs) -> 'Figure':
        """
        Histogram of associated rects scores.

        :param nbins: Number of bins
        :param kwargs: Optional keyword arguments
        :return: Matplotlib figure
        """
        _x = self._floor.get_rect_assoc_scores()
        fig = plt.figure(dpi=DEFAULT_PLOT_DPI)
        plt.hist(_x, bins=nbins)
        plt.title(f'Score association rects - Floor ID {self._floor.id}')
        plt.xlabel('Score')
        plt.ylabel('N° of elements')
        configure_figure(**kwargs)
        print(f'Scores | Mean: {statistics.mean(_x):.3f}. Median: {statistics.median(_x):.3f}')
        return fig

    def rect_assoc(
            self,
            floor1_color: str = '#0000ff',
            floor2_color: str = '#ff0000',
            focus_arch: bool = True,
            focus_struct: bool = True,
            focus_rect_id: int = 0,
            force_fill: bool = False,
            **kwargs
    ) -> 'go.Figure':
        """
        Compare floor with associated floor. Non associated rects will not be plotted.

        :param floor1_color: Color of elements of base floor
        :param floor2_color: Color of elements of other floor
        :param focus_arch: Write architectural associated wall rects
        :param focus_struct: Write structural associated wall rects
        :param focus_rect_id: Focus a given arch rect ID
        :param force_fill: Force rect fill
        :param kwargs: Optional keyword arguments
        """
        assert focus_rect_id >= 0
        fig = self.floor_assoc(
            floor1_color=floor1_color,
            floor2_color=floor2_color,
            wall_opacity=0.25,
            slab_opacity=0.1,
            **kwargs
        )

        base_offset = self._floor.get_offset()
        assoc_offset = self._floor.get_assoc().get_offset()

        rect_opacity = 1.0
        if focus_rect_id != 0:
            rect_opacity = 0

        # Plot arch rects if assoc has been made
        def add_arch_rect(rect: 'ObjWallRect') -> None:
            """
            Plot architectural and assoc rects if exists.

            :param rect: Wall rect
            """
            rect_assoc: List['ObjWallRect'] = rect.get_assoc()

            # If the rect is the same as focused, set opacity to 1.0
            color1 = floor1_color
            color2 = floor2_color
            rect_op = rect_opacity
            if rect.id == focus_rect_id:
                # color1 = '#F5EB22'
                # color2 = '#080501'
                rect_op = 1.0

            if len(rect_assoc) == 0:
                return
            if focus_arch:
                rect.plot_plotly(
                    fig=fig,
                    basic=False,
                    dx=base_offset.x,
                    dy=base_offset.y,
                    color=color1,
                    opacity=rect_op,
                    fill=(rect.id == focus_rect_id) or force_fill,
                    show_legend=False
                )
            if focus_struct:
                r: 'ObjWallRect'
                for r in rect_assoc:
                    r.plot_plotly(
                        fig=fig,
                        basic=False,
                        dx=assoc_offset.x,
                        dy=assoc_offset.y,
                        color=color2,
                        opacity=rect_op,
                        fill=(rect.id == focus_rect_id) or force_fill,
                        show_legend=False
                    )

        self._floor.each_wall_rect(add_arch_rect)
        return fig

    def floor_assoc(
            self,
            floor1_color: str = '#0000ff',
            floor2_color: str = '#ff0000',
            wall_opacity: float = 1.0,
            slab_opacity: float = 0.5,
            **kwargs
    ) -> 'go.Figure':
        """
        Compare floor with associated floor.

        :param floor1_color: Color of elements of base floor
        :param floor2_color: Color of elements of other floor
        :param wall_opacity: Opacity of wall objects
        :param slab_opacity: Opacity of slab objects
        :param kwargs: Optional keyword arguments
        """
        f1ps: str = ' STRUCT'  # Post-name
        f2ps: str = ' ARCH'
        if self._floor.is_architectural():
            f1ps = ' ARCH'
            f2ps = ' STRUCT'
        return self.compare(
            floor=self._floor.get_assoc(),
            draw_wall_point=False,
            draw_slab=False,
            floor1_wall_rect_color=floor1_color,
            floor2_wall_rect_color=floor2_color,
            floor1_postname=f1ps,
            floor2_postname=f2ps,
            wall_opacity=wall_opacity,
            slab_opacity=slab_opacity,
            **kwargs
        )

    def compare(
            self,
            floor: 'ObjFloor',
            fill: bool = False,
            draw_wall_point: bool = True,
            draw_wall_rect: bool = True,
            draw_slab: bool = True,
            wall_point_random_color: bool = False,
            wall_point_diff: bool = False,
            floor1_wall_rect_color: str = '',
            floor2_wall_rect_color: str = '',
            floor1_wall_point_color: str = '',
            floor2_wall_point_color: str = '',
            floor1_slab_color: str = '',
            floor2_slab_color: str = '',
            floor1_postname: str = '',
            floor2_postname: str = '',
            wall_opacity: float = 1.0,
            slab_opacity: float = 0.5,
            offset_floor: tuple = (0, 0),
            wall_rect_basic_mode: bool = False,
            **kwargs
    ) -> 'go.Figure':
        """
        Compare floor with another floor.

        :param floor: Floor to compare
        :param fill: Fill figure
        :param draw_wall_point: Draw wall points
        :param draw_wall_rect: Draw wall rects
        :param draw_slab: Draw slabs
        :param wall_point_random_color: Draw wall points with random colors
        :param wall_point_diff: If true ignore points that does not have projection
        :param floor1_wall_rect_color: Color of wall rects of floor 1 (base)
        :param floor1_wall_point_color: Color of wall points of floor 1 (base)
        :param floor2_wall_rect_color: Color of wall rects of floor 2 (other)
        :param floor2_wall_point_color: Color of wall points of floor 1 (other)
        :param floor1_slab_color: Color of slabs of floor 2 (other)
        :param floor2_slab_color: Color of slabs of floor 1 (other)
        :param floor1_postname: Post name of floor 1
        :param floor2_postname: Post name of floor 2
        :param wall_opacity: Opacity of wall objects
        :param slab_opacity: Opacity of slab objects
        :param offset_floor: Apply an additional offset to "other" floor
        :param wall_rect_basic_mode: Use basic draw mode on rect
        :param kwargs: Optional keyword arguments
        """
        fig = go.Figure()
        base_offset = self._floor.get_offset()
        other_offset = floor.get_offset()

        def add_wall1(wall: 'ObjWall') -> None:
            """
            Add wall to plot (base floor).

            :param wall: Wall
            """
            wall.plot_plotly(
                fig=fig,
                basic=wall_rect_basic_mode,
                dx=base_offset.x,
                dy=base_offset.y,
                postname=f' Floor ID {self._floor.id}' + floor1_postname,
                fill=fill,
                draw_point=draw_wall_point,
                draw_rect=draw_wall_rect,
                point_diff=wall_point_diff,
                point_color=floor1_wall_point_color,
                rect_color=floor1_wall_rect_color,
                opacity=wall_opacity
            )

        def add_wall2(wall: 'ObjWall') -> None:
            """
            Add wall to plot (other floor).

            :param wall: Wall
            """
            wall.plot_plotly(
                fig=fig,
                basic=wall_rect_basic_mode,
                dx=other_offset.x + offset_floor[0],
                dy=other_offset.y + offset_floor[1],
                postname=f' Floor ID {floor.id}' + floor2_postname,
                fill=fill,
                draw_point=draw_wall_point,
                draw_rect=draw_wall_rect,
                point_random_color=wall_point_random_color,
                point_diff=wall_point_diff,
                point_color=floor2_wall_point_color,
                rect_color=floor2_wall_rect_color,
                opacity=wall_opacity
            )

        def add_slab1(slab: 'ObjSlab') -> None:
            """
            Add slab to plot.

            :param slab: Slab
            """
            slab.plot_plotly(
                fig=fig,
                dx=base_offset.x,
                dy=base_offset.y,
                postname=f' Floor ID {self._floor.id}' + floor1_postname,
                color=floor1_slab_color,
                opacity=slab_opacity
            )

        def add_slab2(slab: 'ObjSlab') -> None:
            """
            Add slab to plot.

            :param slab: Slab
            """
            slab.plot_plotly(
                fig=fig,
                dx=other_offset.x,
                dy=other_offset.y,
                postname=f' Floor ID {floor.id}' + floor2_postname,
                color=floor2_slab_color,
                opacity=slab_opacity
            )

        if draw_slab:
            self._floor.each_slab(add_slab1)
            floor.each_slab(add_slab2)
        if draw_wall_point or draw_wall_rect:
            self._floor.each_wall(add_wall1)
            floor.each_wall(add_wall2)

        grid_color = kwargs.get('plot_gridcolor', '#d7d7d7')
        fig.update_layout(
            plot_bgcolor=kwargs.get('plot_bgcolor', '#ffffff'),
            title='Floor {0} ID:{1} vs {2} ID:{3}'.format(
                self._floor.full_label(),
                self._floor.id,
                floor.full_label(),
                floor.id
            ),
            showlegend=kwargs.get('show_legend', True),
            yaxis_zeroline=False,
            xaxis=dict(
                gridcolor=grid_color
            ),
            xaxis_zeroline=False,
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

    def compare_points(self, floor: 'ObjFloor', diff: bool = False) -> 'go.Figure':
        """
        Comparision points plot.

        :param floor: Floor to compare
        :param diff: If diff show points only if they have projections
        :return: Go plot object
        """
        return self.compare(
            floor=floor,
            draw_wall_rect=False,
            draw_slab=False,
            wall_point_random_color=True,
            wall_point_diff=diff
        )
