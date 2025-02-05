import unittest
import math
import numpy as np
from src.Vector2 import Vector2  # Adjust import if necessary

class TestVector2(unittest.TestCase):

    def test_initialization_and_properties(self):
        v = Vector2(1.0, 2.0)
        self.assertAlmostEqual(v.x, 1.0)
        self.assertAlmostEqual(v.y, 2.0)

    def test_addition(self):
        v1 = Vector2(1.0, 2.0)
        v2 = Vector2(3.0, 4.0)
        result = v1 + v2
        expected = Vector2(4.0, 6.0)
        self.assertEqual(result, expected)

    def test_subtraction(self):
        v1 = Vector2(5.0, 7.0)
        v2 = Vector2(2.0, 3.0)
        result = v1 - v2
        expected = Vector2(3.0, 4.0)
        self.assertEqual(result, expected)

    def test_dot_product(self):
        v1 = Vector2(1.0, 2.0)
        v2 = Vector2(3.0, 4.0)
        # Dot product: 1*3 + 2*4 = 3 + 8 = 11
        self.assertAlmostEqual(v1.dot(v2), 11.0)

    def test_magnitude(self):
        v = Vector2(3.0, 4.0)
        # Magnitude should be 5
        self.assertAlmostEqual(v.magnitude(), 5.0)

    def test_length(self):
        v = Vector2(6.0, 8.0)
        # Length is the same as magnitude
        self.assertAlmostEqual(v.length(), 10.0)

    def test_normalize(self):
        v = Vector2(3.0, 4.0)
        norm_v = v.normalize()
        # Normalized vector should have magnitude 1
        self.assertAlmostEqual(norm_v.magnitude(), 1.0)
        # And the components should be scaled accordingly
        expected = Vector2(3.0/5.0, 4.0/5.0)
        self.assertEqual(norm_v, expected)

    def test_rotation(self):
        v = Vector2(1.0, 0.0)
        rotated = v.rotate(math.pi / 2)  # 90-degree counterclockwise rotation
        expected = Vector2(0.0, 1.0)
        self.assertTrue(np.allclose(rotated.array, expected.array, atol=1e-8),
                        msg=f"rotated: {rotated}, expected: {expected}")

        # Rotate 180 degrees
        rotated = v.rotate(math.pi)
        expected = Vector2(-1.0, 0.0)
        self.assertTrue(np.allclose(rotated.array, expected.array, atol=1e-8))

        # Rotate -90 degrees (clockwise)
        rotated = v.rotate(-math.pi / 2)
        expected = Vector2(0.0, -1.0)
        self.assertTrue(np.allclose(rotated.array, expected.array, atol=1e-8))

    def test_distance_to(self):
        v1 = Vector2(0.0, 0.0)
        v2 = Vector2(3.0, 4.0)
        # Distance should be 5 (Pythagorean theorem)
        self.assertAlmostEqual(v1.distance_to(v2), 5.0)

    def test_nearest(self):
        base = Vector2(0.0, 0.0)
        points = [Vector2(1.0, 1.0), Vector2(-1.0, -1.0), Vector2(0.5, 0.5)]
        nearest_points = base.nearest(points)
        # Nearest point should be (0.5, 0.5)
        self.assertEqual(nearest_points, [Vector2(0.5, 0.5)])

    def test_equality(self):
        v1 = Vector2(1.0, 2.0)
        v2 = Vector2(1.0, 2.0)
        v3 = Vector2(2.0, 3.0)
        self.assertEqual(v1, v2)
        self.assertNotEqual(v1, v3)
        self.assertIn("Vector2", repr(v1))

if __name__ == '__main__':
    unittest.main()
