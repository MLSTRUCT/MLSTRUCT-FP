"""
MLSTRUCT-FP - TEST - DB

Test the dataset loader and object components.
"""

import numpy as np
import os
import unittest

from MLStructFP.db import DbLoader, Floor
from MLStructFP.db.image import *

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'fp.json')


class DbLoaderTest(unittest.TestCase):

    def test_db_load(self) -> None:
        """
        Test db loader path and number of dataset items.
        """
        db = DbLoader(DB_PATH)
        self.assertEqual(os.path.dirname(DB_PATH), db.path)
        db.tabulate()

        # Test floors
        self.assertEqual(len(db.floors), 7)

        # Test geometry of a given object
        f = db[302]
        self.assertEqual(len(f.rect), 80)
        self.assertEqual(len(f.slab), 1)
        self.assertAlmostEqual(f.bounding_box.xmin, 1.08599, places=3)
        self.assertAlmostEqual(f.bounding_box.xmax, 49.24599, places=3)
        self.assertAlmostEqual(f.bounding_box.ymin, -24.69863, places=3)
        self.assertAlmostEqual(f.bounding_box.ymax, -11.07863, places=3)

        # Check rectangle data
        r = f.rect[0]
        self.assertEqual(r.id, 20279)
        self.assertEqual(r.floor.id, 302)
        mc = r.get_mass_center()
        self.assertAlmostEqual(mc.x, 1.1659, places=3)
        self.assertAlmostEqual(mc.y, -22.13863, places=3)
        self.assertEqual(len(r.points), 4)

        # Check image
        self.assertEqual(f.image_scale, 188.445)
        self.assertEqual(os.path.basename(f.image_path), 'f23ccf42b9c42bfe7c37a1fb7a1ea100e3d34596.png')

        # Test filter
        def my_filter(db_f: 'Floor') -> bool:
            return db_f.id >= 1000

        db.set_filter(my_filter)
        self.assertEqual(len(db.floors), 3)

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
        bb = f.bounding_box
        self.assertEqual(f.mutator_angle, 0)
        self.assertEqual(f.mutator_scale_x, 1)
        self.assertEqual(f.mutator_scale_y, 1)
        test(83.1, -6.3)

        # Test rotation
        f.mutate(45)
        test(63.2, 54.3)
        self.assertNotEqual(bb, f.bounding_box)

        # Rollback angle
        f.mutate()
        bb2 = f.bounding_box
        self.assertAlmostEqual(bb.xmin, bb2.xmin)
        self.assertAlmostEqual(bb.ymin, bb2.ymin)
        test(83.1, -6.3)

        # Test scale
        f.mutate(0, -1)
        test(-83.1, -6.3)
        f.mutate(0, 1, -1)
        test(83.1, 6.3)

        # Test rotate and scale
        f.mutate(60, -1, 0.65)
        test(-38, -74)

        # Rollback
        f.mutate()
        test(83.1, -6.3)

    def test_image(self) -> None:
        """
        Test image obtain in binary/photo.
        """
        f = DbLoader(DB_PATH).floors

        image_binary = RectBinaryImage(image_size_px=256).init()
        image_photo = RectFloorPhoto(image_size_px=256)
        self.assertEqual(image_binary.image_shape, (256, 256))

        r = f[0].rect[3]  # Selected rectangle
        image_binary.make_rect(r)
        image_photo.make_rect(r)
        r = f[1].rect[0]  # Selected rectangle
        image_binary.make_rect(r)
        image_photo.make_rect(r)

        self.assertEqual(np.sum(image_binary._images[0]), 2708)
        self.assertEqual(np.sum(image_binary._images[1]), 6332)

        self.assertEqual(np.sum(image_photo._images[0]), 284580)
        self.assertEqual(np.sum(image_photo._images[1]), 883326)

        # Export
        if not os.path.isdir('.out'):
            os.mkdir('.out')
        image_binary.export('.out/binary')
        image_photo.export('.out/photo')

        # Now exporters must be closed
        self.assertEqual(len(image_binary.get_images()), 0)
        self.assertEqual(len(image_photo.get_images()), 0)
