"""
MLSTRUCTFP - DbLoader

Loads a given database.json file.
"""

__all__ = ['DbLoader']

import json
import os

from pathlib import Path


class DbLoader(object):
    """
    Database loader.
    """
    _data: dict
    _path: str

    def __init__(self, db: str) -> None:
        """
        Loads a database file.

        :param db: Database path
        """
        assert os.path.isfile(db), f'Database file {db} not found'
        self._path = str(Path(os.path.realpath(db)).parent)

        with open(db, 'r', encoding='utf8') as dbfile:
            self._data = json.load(dbfile)
        print(self._data.keys())
