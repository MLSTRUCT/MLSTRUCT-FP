"""
MLSTRUCTFP - TEST - DB

Test the database loader and object components (rect, slab, floor).
"""

import numpy as np
import os
import unittest

from MLStructFP.db import DbLoader
from MLStructFP.db.image import *

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'fp.json')


class DbLoaderTest(unittest.TestCase):

    def test_db_load(self) -> None:
        """
        Test db loader path and number of database items.
        """
        db = DbLoader(DB_PATH)
        self.assertEqual(os.path.dirname(DB_PATH), db._path)

        # Test floors
        self.assertEqual(len(db.floor), 7)

        # Test geometry of a given object
        f = db.floor[302]
        self.assertEqual(len(f.rect), 80)
        self.assertEqual(len(f.slab), 1)
        r = f.rect[0]

        # Check rectangle data
        self.assertEqual(r.id, 20279)
        self.assertEqual(r.floor.id, 302)
        mc = r.get_mass_center()
        self.assertAlmostEqual(mc.x, 1.1659, places=3)
        self.assertAlmostEqual(mc.y, 22.13863, places=3)
        self.assertEqual(len(r.points), 4)

        self.assertEqual(f.image_scale, 188.445)
        self.assertEqual(os.path.basename(f.image_path), 'f23ccf42b9c42bfe7c37a1fb7a1ea100e3d34596.png')

    def test_mutator(self) -> None:
        """
        Test floor mutator.
        """
        f = DbLoader(DB_PATH).floors[0]

        def test(x: float, y: float):
            p = f.rect[0].get_mass_center()
            self.assertEqual(round(p.x, 1), x)
            self.assertEqual(round(p.y, 1), y)

        # Test no mutator
        self.assertEqual(f.mutator_angle, 0)
        self.assertEqual(f.mutator_scale_x, 1)
        self.assertEqual(f.mutator_scale_y, 1)
        test(83.1, 6.3)

        # Test rotation
        f.mutate(45)
        test(54.3, 63.2)

        # Rollback angle
        f.mutate()
        test(83.1, 6.3)

        # Test scale
        f.mutate(0, -1)
        test(-83.1, 6.3)
        f.mutate(0, 1, -1)
        test(83.1, -6.3)

        # Test rotate and scale
        f.mutate(60, -1, 0.65)
        test(-45.1, -69.9)

        # Rollback
        f.mutate()
        test(83.1, 6.3)

    def test_image(self) -> None:
        """
        Test image obtain in binary/photo.
        """
        f = DbLoader(DB_PATH).floors

        image_binary = RectBinaryImage(image_size_px=256, crop_length=5.0).init()
        image_photo = RectFloorPhoto(image_size_px=256, crop_length=5.0)

        r = f[0].rect[3]  # Selected rectangle
        image_binary.make(r)
        image_photo.make(r)
        r = f[1].rect[0]  # Selected rectangle
        image_binary.make(r)
        image_photo.make(r)

        self.assertEqual(np.sum(image_binary._images[0]), 2708)
        self.assertEqual(np.sum(image_binary._images[1]), 6332)

        self.assertEqual(np.sum(image_photo._images[0]), 284580)
        self.assertEqual(np.sum(image_photo._images[1]), 993110)
