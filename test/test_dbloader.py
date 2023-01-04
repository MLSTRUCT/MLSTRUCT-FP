"""
MLSTRUCTFP - DbLoader - TEST

Test the database loader.
"""

import os
import unittest

from pathlib import Path
from mlstructfp import DbLoader


class DbLoaderTest(unittest.TestCase):

    def test_load(self) -> None:
        """
        Test db loader path and number of database items.
        """
        db = DbLoader('../db/database.json')
        self.assertEqual(os.path.join(Path(os.getcwd()).parent, 'db'), db._path)
        # print(db._data)
