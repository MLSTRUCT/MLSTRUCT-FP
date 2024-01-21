"""
MLSTRUCTFP - DB - DBLOADER

Loads a given dataset .json file.
"""

__all__ = ['DbLoader']

from MLStructFP.db._floor import Floor
from MLStructFP.db._c_rect import Rect
from MLStructFP.db._c_slab import Slab
from MLStructFP._types import Tuple

import json
import os
import tabulate

from IPython.display import HTML, display
from pathlib import Path
from typing import Dict


class DbLoader(object):
    """
    Dataset loader.
    """
    _path: str
    floor: Dict[int, 'Floor']

    def __init__(self, db: str) -> None:
        """
        Loads a dataset file.

        :param db: Dataset path
        """
        assert os.path.isfile(db), f'Dataset file {db} not found'
        self._path = str(Path(os.path.realpath(db)).parent)
        self.floor = {}

        with open(db, 'r', encoding='utf8') as dbfile:
            data = json.load(dbfile)

            # Assemble objects
            for f_id in data['floor']:
                f_data: dict = data['floor'][f_id]
                self.floor[int(f_id)] = Floor(
                    floor_id=int(f_id),
                    image_path=os.path.join(self._path, f_data['image']),
                    image_scale=f_data['scale'],
                    project_id=f_data['project'] if 'project' in f_data else -1
                )
            for rect_id in data['rect']:
                rect_data: dict = data['rect'][rect_id]
                rect_a = rect_data['angle']
                Rect(
                    rect_id=int(rect_id),
                    wall_id=rect_data['wallID'],
                    floor=self.floor[rect_data['floorID']],
                    angle=rect_a if not isinstance(rect_a, list) else rect_a[0],
                    length=rect_data['length'],
                    thickness=rect_data['thickness'],
                    x=rect_data['x'],
                    y=rect_data['y'],
                    line_m=rect_data['line'][0],  # Slope
                    line_n=rect_data['line'][1],  # Intercept
                    line_theta=rect_data['line'][2]  # Theta
                )
            for slab_id in data['slab']:
                slab_data: dict = data['slab'][slab_id]
                Slab(
                    slab_id=int(slab_id),
                    floor=self.floor[slab_data['floorID']],
                    x=slab_data['x'],
                    y=slab_data['y']
                )

    @property
    def floors(self) -> Tuple['Floor', ...]:
        # noinspection PyTypeChecker
        return tuple(self.floor.values())

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
        for t in ('Floor ID', 'No. rects', 'No. slabs', 'Floor image path'):
            theads.append(t)
        table = [theads]
        for j in range(len(self.floors)):
            f: 'Floor' = self.floors[j]
            table_data = [j]
            if show_project_id:
                table_data.append(f.project_id)
            for i in (f.id, len(f.rect), len(f.slab), f.image_path):
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
