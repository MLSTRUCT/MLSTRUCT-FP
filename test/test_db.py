"""
MLSTRUCTFP - TEST - DB

Test the database loader and object components (rect, slab, floor).
"""

import os
import unittest
from pathlib import Path

from mlstructfp.db import DbLoader


class DbLoaderTest(unittest.TestCase):

    def test_load(self) -> None:
        """
        Test db loader path and number of database items.
        """
        db = DbLoader('../db/database.json')
        self.assertEqual(os.path.join(Path(os.getcwd()).parent, 'db'), db._path)
