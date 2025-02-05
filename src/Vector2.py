import numpy as np
from typing import List, Optional, Any

class Vector2:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        """
        Initialize a 2D vector.
        
        Args:
            x (float): The x-component of the vector. Defaults to 0.0.
            y (float): The y-component of the vector. Defaults to 0.0.
        """
        self.array = np.array([x, y], dtype=float)
    
    @property
    def x(self) -> float:
        """Get the x-component of the vector."""
        return self.array[0]
    
    @property
    def y(self) -> float:
        """Get the y-component of the vector."""
        return self.array[1]
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        """
        Add two vectors.
        
        Args:
            other (Vector2): The vector to add.
        
        Returns:
            Vector2: The resulting vector.
        """
        if not isinstance(other, Vector2):
            raise TypeError("Addition is supported between Vector2 instances only.")
        return Vector2(*(self.array + other.array))
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """
        Subtract one vector from another.
        
        Args:
            other (Vector2): The vector to subtract.
        
        Returns:
            Vector2: The resulting vector.
        """
        if not isinstance(other, Vector2):
            raise TypeError("Subtraction is supported between Vector2 instances only.")
        return Vector2(*(self.array - other.array))
    
    def dot(self, other: 'Vector2') -> float:
        """
        Compute the dot product of two vectors.
        
        Args:
            other (Vector2): The other vector.
        
        Returns:
            float: The dot product.
        """
        if not isinstance(other, Vector2):
            raise TypeError("Dot product is supported between Vector2 instances only.")
        return np.dot(self.array, other.array)
    
    def magnitude(self) -> float:
        """
        Compute the magnitude (length) of the vector.
        
        Returns:
            float: The magnitude.
        """
        return np.linalg.norm(self.array)
    
    def length(self) -> float:
        """
        Alias for magnitude.
        
        Returns:
            float: The magnitude.
        """
        return self.magnitude()
    
    def normalize(self) -> 'Vector2':
        """
        Normalize the vector (make it unit length).
        
        Returns:
            Vector2: The normalized vector.
        """
        norm = self.magnitude()
        if norm == 0:
            return Vector2()
        return Vector2(*(self.array / norm))
    
    def rotate(self, radians: float) -> 'Vector2':
        """
        Rotate the vector by a given angle in radians.
        
        Args:
            radians (float): The angle to rotate the vector.
        
        Returns:
            Vector2: The rotated vector.
        """
        
        radians = 1 * radians
        rotation_sin = np.sin(radians)
        rotation_cos = np.cos(radians)
        
        # Apply the 2D rotation transformation.
        new_x = self.x * rotation_cos - self.y * rotation_sin
        new_y = self.x * rotation_sin + self.y * rotation_cos
        
        return Vector2(new_x, new_y)
    
    def distance_to(self, other: 'Vector2') -> float:
        """
        Compute the distance to another vector.
        
        Args:
            other (Vector2): The other vector.
        
        Returns:
            float: The distance.
        """
        if not isinstance(other, Vector2):
            raise TypeError("Distance can only be computed between Vector2 instances.")
        return np.linalg.norm(self.array - other.array)
    
    def nearest(self, points: List['Vector2']) -> List['Vector2']:
        """
        Find the nearest point(s) to this vector from a list of points.
        
        Args:
            points (List[Vector2]): The list of points to search.
        
        Returns:
            List[Vector2]: A list of the nearest point(s).
        """
        if not points:
            return []
        distances = [self.distance_to(p) for p in points]
        min_distance = min(distances)
        nearest_points = [p for p, d in zip(points, distances) if np.isclose(d, min_distance)]
        return nearest_points
    
    def __eq__(self, other: Any) -> bool:
        """
        Check if two vectors are equal within a tolerance.
        
        Args:
            other (Any): The object to compare.
        
        Returns:
            bool: True if vectors are equal, False otherwise.
        """
        if not isinstance(other, Vector2):
            return False
        return np.allclose(self.array, other.array, atol=1e-8)
    
    def __repr__(self) -> str:
        """
        Return the string representation of the vector.
        
        Returns:
            str: The string representation.
        """
        return f"Vector2(x={self.x}, y={self.y})"
