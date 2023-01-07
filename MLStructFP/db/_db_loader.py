"""
MLSTRUCTFP - DB - DBLOADER

Loads a given database.json file.
"""

__all__ = ['DbLoader']

from MLStructFP.db._floor import Floor
from MLStructFP.db._c_rect import Rect
from MLStructFP.db._c_slab import Slab

import json
import os

from pathlib import Path
from typing import Dict


class DbLoader(object):
    """
    Database loader.
    """
    _path: str
    floor: Dict[int, 'Floor']

    def __init__(self, db: str) -> None:
        """
        Loads a database file.

        :param db: Database path
        """
        assert os.path.isfile(db), f'Database file {db} not found'
        self._path = str(Path(os.path.realpath(db)).parent)
        self.floor = {}

        with open(db, 'r', encoding='utf8') as dbfile:
            data = json.load(dbfile)

            # Assemble objects
            for f_id in data['floor']:
                f_data = data['floor'][f_id]
                self.floor[int(f_id)] = Floor(
                    floor_id=int(f_id),
                    image_path=os.path.join(self._path, f_data['image']),
                    image_scale=f_data['scale']
                )
            for rect_id in data['rect']:
                rect_data = data['rect'][rect_id]
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
                slab_data = data['slab'][slab_id]
                Slab(
                    slab_id=int(slab_id),
                    floor=self.floor[slab_data['floorID']],
                    x=slab_data['x'],
                    y=slab_data['y']
                )
