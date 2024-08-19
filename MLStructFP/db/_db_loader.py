"""
MLSTRUCT-FP - DB - DBLOADER

Loads a given dataset .json file.
"""

__all__ = ['DbLoader']

from MLStructFP.db._floor import Floor
from MLStructFP.db._c_rect import Rect
from MLStructFP.db._c_point import Point
from MLStructFP.db._c_slab import Slab
from MLStructFP.db._c_room import Room
from MLStructFP.db._c_item import Item
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
            data: dict = json.load(dbfile)
            meta: dict = data['meta'] if 'meta' in data else {}

            # Load metadata
            floor_categories: Dict[int, str] = {}
            for cat in (meta['floor_categories'] if 'floor_categories' in meta else {}):
                floor_categories[meta['floor_categories'][cat]] = cat
            item_types: Dict[int, Tuple[str, str]] = {}
            for cat in (meta['item_types'] if 'item_types' in meta else {}):
                ic = meta['item_types'][cat]
                item_types[ic[0]] = (cat, ic[1])
            project_label: Dict[int, str] = {}
            for pid in (meta['project_label'] if 'project_label' in meta else {}):
                try:
                    project_label[int(pid)] = meta['project_label'][pid]
                except ValueError:
                    pass
            room_categories: Dict[int, Tuple[str, str]] = {}
            for cat in (meta['room_categories'] if 'room_categories' in meta else {}):
                rc = meta['room_categories'][cat]
                room_categories[rc[0]] = (cat, rc[1])

            # Load floors
            for f_id in data.get('floor', {}):
                f_data: dict = data['floor'][f_id]
                f_cat: int = int(f_data['category'] if 'category' in f_data else 0)
                project_id: int = f_data['project'] if 'project' in f_data else -1
                self.__floor[int(f_id)] = Floor(
                    floor_id=int(f_id),
                    image_path=os.path.join(self.__path, f_data['image']),
                    image_scale=f_data['scale'],
                    project_id=project_id,
                    project_label=project_label[project_id] if project_id in project_label else '',
                    category=f_cat,
                    category_name=floor_categories.get(f_cat, ''),
                    elevation=f_data['elevation'] if 'elevation' in f_data else False
                )
            if floor_only:
                return

            # Load objects
            for rect_id in data.get('rect', {}):
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
            for point_id in data.get('point', {}):
                point_data: dict = data['point'][point_id]
                Point(
                    point_id=int(point_id),
                    wall_id=int(point_data['wallID']),
                    floor=self.__floor[point_data['floorID']],
                    x=point_data['x'],
                    y=point_data['y'],
                    topo=int(point_data['topo'])
                )
            for slab_id in data.get('slab', {}):
                slab_data: dict = data['slab'][slab_id]
                Slab(
                    slab_id=int(slab_id),
                    floor=self.__floor[slab_data['floorID']],
                    x=slab_data['x'],
                    y=slab_data['y']
                )
            for room_id in data.get('room', {}):
                room_data: dict = data['room'][room_id]
                room_cat = int(room_data['category'])
                Room(
                    room_id=int(room_id),
                    floor=self.__floor[room_data['floorID']],
                    x=room_data['x'],
                    y=room_data['y'],
                    color=room_categories[room_cat][1] if room_cat in room_categories else '#000000',
                    category=room_cat,
                    category_name=room_categories[room_cat][0] if room_cat in room_categories else ''
                )
            for item_id in data.get('item', {}):
                item_data: dict = data['item'][item_id]
                item_cat = int(item_data['category'])
                Item(
                    item_id=int(item_id),
                    floor=self.__floor[item_data['floorID']],
                    x=item_data['x'],
                    y=item_data['y'],
                    color=item_types[item_cat][1] if item_cat in item_types else '#000000',
                    category=item_cat,
                    category_name=item_types[item_cat][0] if item_cat in item_types else ''
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

    def tabulate(self, limit: int = 0, legacy: bool = False,
                 f_filter: Optional[Callable[['Floor'], bool]] = None) -> None:
        """
        Tabulates each floor, with their file and number of rects.

        :param limit: Limits the number of items
        :param legacy: Show legacy mode
        :param f_filter: Floor filter
        """
        assert isinstance(limit, int) and limit >= 0, 'Limit must be an integer greater or equal than zero'
        theads = ['#']
        for t in (
                ('Project ID', 'Project label', 'Floor ID', 'Cat', 'Elev',
                 'Rects', 'Points', 'Slabs', 'Rooms', 'Items', 'Floor image path'
                 ) if not legacy else
                ('Floor ID', 'Rects', 'Slabs', 'Floor image path')
        ):
            theads.append(t)
        table = [theads]
        floors = self.floors
        for j in range(len(floors)):
            f: 'Floor' = floors[j]
            if f_filter is not None and not f_filter(f):
                continue
            table_data = [j]
            f_file: str = os.path.basename(f.image_path)
            for i in (
                    (f.project_id, f.project_label, f.id, f.category, 1 if f.elevation else 0,
                     len(f.rect), len(f.point), len(f.slab), len(f.room), len(f.item), f_file
                     ) if not legacy else
                    (f.id, len(f.rect), len(f.slab), f_file)
            ):
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
