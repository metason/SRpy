# src/vector3.py
import numpy as np

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.array = np.array([x, y, z], dtype=float)
    
    @property
    def x(self):
        return self.array[0]
    
    @property
    def y(self):
        return self.array[1]
    
    @property
    def z(self):
        return self.array[2]
    
    def __add__(self, other):
        return Vector3(*(self.array + other.array))
    
    def __sub__(self, other):
        #if other is not Vector3 but number
        if not isinstance(other, Vector3):
            return Vector3(*(self.array - other))
        return Vector3(*(self.array - other.array))
    def __truediv__(self, other):
        return Vector3(*(self.array / other))

    
    def dot(self, other):
        return np.dot(self.array, other.array)
    
    def cross(self, other):
        return Vector3(*np.cross(self.array, other.array))
    
    def magnitude(self):
        return np.linalg.norm(self.array)
    
    def length(self):
        return self.magnitude()
    
    def normalize(self):
        norm = self.magnitude()
        if norm == 0:
            return Vector3()
        return Vector3(*(self.array / norm))
    
    def rotate(self, radians):
        radians = -1 * radians
        rotation_matrix = np.array([
            [np.cos(radians), 0, np.sin(radians)],
            [0,                1,               0],
            [-np.sin(radians), 0, np.cos(radians)]
        ])
        rotated = rotation_matrix.dot(self.array)
        return Vector3(*rotated)
    
    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return False
        return np.allclose(self.array, other.array, atol=1e-8)
    
    def __repr__(self):
        return f"Vector3(x={self.x}, y={self.y}, z={self.z})"
