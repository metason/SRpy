# tests/test_vector3.py
import math
import unittest
import numpy as np

from src.Vector3 import Vector3  # Adjust the import path if necessary

class TestVector3(unittest.TestCase):

    def test_initialization_and_properties(self):
        v = Vector3(1.0, 2.0, 3.0)
        self.assertAlmostEqual(v.x, 1.0)
        self.assertAlmostEqual(v.y, 2.0)
        self.assertAlmostEqual(v.z, 3.0)

    def test_addition(self):
        v1 = Vector3(1.0, 2.0, 3.0)
        v2 = Vector3(4.0, 5.0, 6.0)
        result = v1 + v2
        expected = Vector3(5.0, 7.0, 9.0)
        self.assertEqual(result, expected)

    def test_subtraction_vector(self):
        v1 = Vector3(5.0, 7.0, 9.0)
        v2 = Vector3(1.0, 2.0, 3.0)
        result = v1 - v2
        expected = Vector3(4.0, 5.0, 6.0)
        self.assertEqual(result, expected)

    def test_subtraction_scalar(self):
        v = Vector3(5.0, 7.0, 9.0)
        # Subtracting a scalar subtracts from each element.
        result = v - 2.0
        expected = Vector3(3.0, 5.0, 7.0)
        self.assertEqual(result, expected)

    def test_truedivision(self):
        v = Vector3(10.0, 20.0, 30.0)
        result = v / 2.0
        expected = Vector3(5.0, 10.0, 15.0)
        self.assertEqual(result, expected)

    def test_dot_product(self):
        v1 = Vector3(1.0, 2.0, 3.0)
        v2 = Vector3(4.0, 5.0, 6.0)
        # Dot product: 1*4 + 2*5 + 3*6 = 32
        self.assertAlmostEqual(v1.dot(v2), 32.0)

    def test_cross_product(self):
        v1 = Vector3(1.0, 0.0, 0.0)
        v2 = Vector3(0.0, 1.0, 0.0)
        # Cross product: (0, 0, 1)
        expected = Vector3(0.0, 0.0, 1.0)
        self.assertEqual(v1.cross(v2), expected)

    def test_magnitude(self):
        v = Vector3(3.0, 4.0, 0.0)
        # Magnitude should be 5
        self.assertAlmostEqual(v.magnitude(), 5.0)
        # __abs__ should return the same value
        self.assertAlmostEqual(abs(v), 5.0)

    def test_length(self):
        v = Vector3(1.0, 2.0, 2.0)
        # Length is the same as magnitude
        self.assertAlmostEqual(v.length(), math.sqrt(1 + 4 + 4), places=7)

    def test_normalize(self):
        v = Vector3(3.0, 4.0, 0.0)
        norm_v = v.normalize()
        # Normalized vector should have magnitude 1
        self.assertAlmostEqual(norm_v.magnitude(), 1.0)
        # And the components should be scaled accordingly
        expected = Vector3(3.0/5.0, 4.0/5.0, 0.0)
        self.assertEqual(norm_v, expected)

    def test_rotate(self):
        # Test rotation about the Y-axis.
        # The rotate method internally multiplies the radians by -1.
        # So rotating Vector3(1, 0, 0) by math.pi/2 should yield Vector3(0, 0, -1).
        v = Vector3(1.0, 0.0, 0.0)
        rotated = v.rotate(math.pi/2)
        expected = Vector3(0.0, 0.0, -1.0)
        self.assertTrue(np.allclose(rotated.array, expected.array, atol=1e-8),
                        msg=f"rotated: {rotated}, expected: {expected}")

    def test_eq_and_repr(self):
        v1 = Vector3(1.0, 2.0, 3.0)
        v2 = Vector3(1.0, 2.0, 3.0)
        v3 = Vector3(3.0, 2.0, 1.0)
        self.assertEqual(v1, v2)
        self.assertNotEqual(v1, v3)
        self.assertIn("Vector3", repr(v1))

if __name__ == '__main__':
    unittest.main()
