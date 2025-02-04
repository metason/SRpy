# tests/SectorTests.py

import unittest
import math

# Import the necessary classes and enums from your modules
from src.vector3 import Vector3
from src.SpatialObject import SpatialObject
from src.SpatialPredicate import SpatialPredicate
from src.SpatialRelation import SpatialRelation
from src.BBoxSector import BBoxSector, BBoxSectorFlags

class TestBBoxSectors(unittest.TestCase):
    def setUp(self):
        """
        Initialize SpatialObject instances before each test.
        """
        # Object against which subjects are tested
        self.obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0.0, z=0),
            width=1.1,
            height=1.1,
            depth=1.1
        )
    
    def test_sector_o(self):
        """
        Test that a subject located in sector 'o' (over) of an object is correctly identified.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=1.61, z=0.1),
            width=0.5,
            height=0.5,
            depth=0.5
        )
        
        relation = self.obj.sector(subject)
        self.assertEqual(relation.predicate, SpatialPredicate.o)
    
    def test_sector_al(self):
        """
        Test that a subject located in sector 'al' (ahead-left) of an object is correctly identified.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=1.2, y=0.21, z=1.4),
            width=0.5,
            height=0.5,
            depth=0.5
        )
        relation = self.obj.sector(subject)
        self.assertEqual(relation.predicate, SpatialPredicate.al)
    
    def test_sector_bru(self):
        """
        Test that a subject located in sector 'bru' (behind-right-under) of an object is correctly identified.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-1.2, y=-1.21, z=-1.4),
            width=0.5,
            height=0.5,
            depth=0.5
        )
        relation = self.obj.sector(subject)
        self.assertEqual(relation.predicate, SpatialPredicate.bru)
    
    def test_sector_i(self):
        """
        Test that a subject located in sector 'i' (inside) of an object is correctly identified.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=0, z=-0.1),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relation = self.obj.sector(subject)
        self.assertEqual(relation.predicate, SpatialPredicate.i)
    
    def test_nosector_not_nearby(self):
        """
        Test that a subject not located within the nearby sector of an object is correctly identified as 'undefined'.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=8, y=0, z=0.1),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        
        relation = self.obj.sector(subject, nearBy=True)
        self.assertEqual(relation.predicate, SpatialPredicate.undefined)

# Run the tests
if __name__ == '__main__':
    unittest.main()
