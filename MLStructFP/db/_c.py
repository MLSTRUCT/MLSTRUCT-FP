"""
MLSTRUCT-FP - DB - C

Base FP components.
"""

__all__ = ['BaseComponent', 'BasePolyComponent', 'BasePolyObj']

import abc
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from MLStructFP.utils import GeomPoint2D
from MLStructFP._types import List, TYPE_CHECKING, VectorInstance, NumberType, Dict

if TYPE_CHECKING:
    from MLStructFP.db._floor import Floor


class BaseComponent(abc.ABC):
    """
    Floor plan base component.
    """
    _floor: 'Floor'
    _id: int
    _points: List['GeomPoint2D']  # The coordinates of the object

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
        self._floor = floor
        self._id = component_id
        self._points = []
        for i in range(len(x)):
            self._points.append(GeomPoint2D(float(x[i]), float(y[i])))

    @property
    def floor(self) -> 'Floor':
        return self._floor

    @property
    def id(self) -> int:
        return self._id

    @property
    def points(self) -> List['GeomPoint2D']:
        return [p for p in self._points]

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


class BasePolyComponent(BaseComponent, abc.ABC):
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
        px, py = [p.x for p in self._points], [p.y for p in self._points]
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
        px, py = [p.x for p in self._points], [p.y for p in self._points]
        px.append(px[0])
        py.append(py[0])
        if fill:
            ax.fill(px, py, color=color, lw=None, alpha=alpha)
        else:
            ax.plot(px, py, '-', color=color, linewidth=linewidth, alpha=alpha)


class BasePolyObj(BasePolyComponent, abc.ABC):
    """
    FP base polygon object.
    """
    __basename: str
    __color: str
    _category: int
    _category_name: str

    def __init__(
            self,
            ctx: Dict[int, 'BasePolyObj'],
            basename: str,
            obj_id: int,
            floor: 'Floor',
            x: List[float],
            y: List[float],
            color: str,
            category: int,
            category_name: str,
    ) -> None:
        """
        Constructor.

        :param ctx: Polygon object context
        :param basename: Basename
        :param obj_id: ID of the object
        :param floor: Floor object
        :param x: List of coordinates within x-axis
        :param y: List of coordinates within y-axis
        :param color: Object color
        :param category: Object category
        :param category_name: Object category name
        """
        BasePolyComponent.__init__(self, obj_id, x, y, floor)
        ctx[obj_id] = self
        self.__basename = basename
        self.__color = color
        self._category_name = category_name
        self._category = category

    @property
    def category(self) -> int:
        return self._category

    @property
    def category_name(self) -> str:
        return self._category_name

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
        if name != '':
            name = f'{name} '
        super().plot_plotly(
            fig, dx, dy, opacity, self.__color if color == '' else color,
            '' if self.category_name == '' else f'[{self.category}] ' + f'{self.__basename} {name}ID{self.id}{postname}',
            **kwargs)

    def plot_matplotlib(
            self,
            ax: 'plt.Axes',
            linewidth: NumberType = 2.0,
            alpha: NumberType = 1.0,
            color: str = '',
            fill: bool = True
    ) -> None:
        super().plot_matplotlib(ax, linewidth, alpha, self.__color if color == '' else color, fill)
