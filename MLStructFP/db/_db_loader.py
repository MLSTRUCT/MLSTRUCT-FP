"""
MLSTRUCTFP - DB - DBLOADER

Loads a given dataset .json file.
"""

__all__ = ['DbLoader']

from MLStructFP.db._floor import Floor
from MLStructFP.db._c_rect import Rect
from MLStructFP.db._c_point import Point
from MLStructFP.db._c_slab import Slab
from MLStructFP._types import Tuple

import json
import math
import os
import tabulate

from IPython.display import HTML, display
from pathlib import Path
from typing import Dict, Callable, Optional, List


class DbLoader(object):
    """
    Dataset loader.
    """
    __filter: Optional[Callable[['Floor'], bool]]
    __filtered_floors: List['Floor']
    __floor: Dict[int, 'Floor']
    __path: str

    def __init__(self, db: str, floor_only: bool = False) -> None:
        """
        Loads a dataset file.

        :param db: Dataset path
        :param floor_only: If true, load only floors
        """
        assert os.path.isfile(db), f'Dataset file {db} not found'
        self.__filter = None
        self.__filtered_floors = []
        self.__path = str(Path(os.path.realpath(db)).parent)
        self.__floor = {}

        with open(db, 'r', encoding='utf8') as dbfile:
            data = json.load(dbfile)

            # Load floors
            for f_id in data['floor']:
                f_data: dict = data['floor'][f_id]
                self.__floor[int(f_id)] = Floor(
                    floor_id=int(f_id),
                    image_path=os.path.join(self.__path, f_data['image']),
                    image_scale=f_data['scale'],
                    project_id=f_data['project'] if 'project' in f_data else -1
                )
            if floor_only:
                return

            # Load objects
            for rect_id in data['rect']:
                rect_data: dict = data['rect'][rect_id]
                rect_a = rect_data['angle']
                Rect(
                    rect_id=int(rect_id),
                    wall_id=int(rect_data['wallID']),
                    floor=self.__floor[rect_data['floorID']],
                    angle=rect_a if not isinstance(rect_a, list) else rect_a[0],
                    length=rect_data['length'],
                    thickness=rect_data['thickness'],
                    x=rect_data['x'],
                    y=rect_data['y'],
                    line_m=rect_data['line'][0],  # Slope
                    line_n=rect_data['line'][1],  # Intercept
                    line_theta=rect_data['line'][2]  # Theta
                )
            if 'point' in data:
                for point_id in data['point']:
                    point_data: dict = data['point'][point_id]
                    Point(
                        point_id=int(point_id),
                        wall_id=int(point_data['wallID']),
                        floor=self.__floor[point_data['floorID']],
                        x=point_data['x'],
                        y=point_data['y'],
                        topo=int(point_data['topo'])
                    )
            for slab_id in data['slab']:
                slab_data: dict = data['slab'][slab_id]
                Slab(
                    slab_id=int(slab_id),
                    floor=self.__floor[slab_data['floorID']],
                    x=slab_data['x'],
                    y=slab_data['y']
                )

    def __getitem__(self, item: int) -> 'Floor':
        return self.__floor[item]

    @property
    def floors(self) -> Tuple['Floor', ...]:
        if len(self.__filtered_floors) == 0:
            for f in self.__floor.values():
                if self.__filter is None or self.__filter(f):
                    self.__filtered_floors.append(f)
        return tuple(self.__filtered_floors)

    @property
    def path(self) -> str:
        return self.__path

    @property
    def scale_limits(self) -> Tuple[float, float]:
        sc_min = math.inf
        sc_max = 0
        for f in self.floors:
            sc_min = min(sc_min, f.image_scale)
            sc_max = max(sc_max, f.image_scale)
        return sc_min, sc_max

    def set_filter(self, f_filter: Callable[['Floor'], bool]) -> None:
        """
        Set floor filter.

        :param f_filter: Floor filter
        """
        self.__filter = f_filter
        self.__filtered_floors.clear()

    def tabulate(self, limit: int = 0, show_project_id: bool = False) -> None:
        """
        Tabulates each floor, with their file and number of rects.

        :param limit: Limit the number of items
        :param show_project_id: Show project ID (if exists)
        """
        assert isinstance(limit, int) and limit >= 0, 'Limit must be an integer greater or equal than zero'
        theads = ['#']
        if show_project_id:
            theads.append('Project ID')
        for t in ('Floor ID', 'No. rects', 'No. points', 'No. slabs', 'Floor image path'):
            theads.append(t)
        table = [theads]
        floors = self.floors
        for j in range(len(floors)):
            f: 'Floor' = floors[j]
            table_data = [j]
            if show_project_id:
                table_data.append(f.project_id)
            for i in (f.id, len(f.rect), len(f.point), len(f.slab), f.image_path):
                table_data.append(i)
            table.append(table_data)
            if 0 < limit - 1 <= j:
                break
        display(HTML(tabulate.tabulate(
            table,
            headers='firstrow',
            numalign='center',
            stralign='center',
            tablefmt='html'
        )))
