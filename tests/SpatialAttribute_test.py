import unittest
from src.SpatialRelation import SpatialRelation
from src.SpatialObject import SpatialObject
from src.BBoxSector import BBoxSector, BBoxSectorFlags
from src.SpatialReasoner import SpatialReasoner
from src.Vector3 import Vector3

from src.SpatialBasics import (
    NearbySchema,
    SectorSchema,
    SpatialAdjustment,
    SpatialPredicateCategories,
    ObjectConfidence,
    SpatialAtribute,
    SpatialExistence,
    ObjectCause,
    MotionState,
    ObjectShape,
    ObjectHandling,
    defaultAdjustment  # Ensure defaultAdjustment is accessible
)

class TestSpatialAttributes(unittest.TestCase):

    def test_is_thin(self):
        obj = SpatialObject("2", position=Vector3(0, 0, 0),
                            width=1.1, height=0.1, depth=1.2)
        self.assertTrue(obj.thin)

    def test_not_long(self):
        obj = SpatialObject("2", position=Vector3(0, 0, 0),
                            width=1.0, height=1.1, depth=1.2)
        self.assertFalse(obj.thin)

    def test_is_long(self):
        obj = SpatialObject("2", position=Vector3(0, 0, 0),
                            width=0.1, height=1.0, depth=0.1)
        self.assertTrue(obj.long)
        self.assertEqual(obj.mainDirection(), 2)

    def test_radi(self):
        obj = SpatialObject("2", position=Vector3(0, 0, 0),
                            width=1.0, height=0.2, depth=1.1)
        self.assertLess(obj.baseradius, obj.radius)

    def test_detected(self):
        obj = SpatialObject.createDetectedObject("1", label="Table",
                                                     width=1.6, height=0.8, depth=0.9)
        self.assertEqual(obj.label, "table")
        self.assertEqual(obj.cause, ObjectCause.object_detected)
        self.assertEqual(obj.existence, SpatialExistence.real)
        self.assertFalse(obj.long)

    def test_building_element(self):
        obj = SpatialObject.createBuildingElement("1", type="Wall",
                                                    from_pos=Vector3(0, 0, 0),
                                                    width=3.2, height=2.2, depth=0.3)
        self.assertGreater(obj.length, 3.0)
        self.assertEqual(obj.label, "wall")
        self.assertEqual(obj.type, "Wall")
        self.assertEqual(obj.existence, SpatialExistence.real)
        self.assertEqual(obj.shape, ObjectShape.cubical)
        self.assertEqual(obj.motion, MotionState.stationary)

    def test_virtual(self):
        obj = SpatialObject.createVirtualObject("1", width=1.0, height=0.0, depth=0.3)
        self.assertEqual(obj.cause, ObjectCause.user_generated)
        self.assertEqual(obj.existence, SpatialExistence.virtual)
        self.assertEqual(obj.confidence.spatial, 1.0)

    def test_ismoving(self):
        obj = SpatialObject("2", position=Vector3(0, 0, 0),
                            width=0.1, height=1.0, depth=0.1)
        obj.confidence.setValue(0.6)
        obj.velocity = Vector3(0.2, 0.0, 0.1)
        self.assertEqual(obj.motion, MotionState.moving  )

    def test_azimuth(self):
        obj = SpatialObject("2", position=Vector3(0, 0, 0),
                            width=0.1, height=1.0, depth=0.1)
        obj.setYaw(-30.0)
        sp = SpatialReasoner()
        sp.load([obj])
        print("Azimuth:", obj.azimuth)
        self.assertEqual(obj.azimuth, 210.0)

    def test_filter_attr(self):
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8),
                            width=1.0, height=1.0, depth=1.0)
        obj.existence = SpatialExistence.virtual
        obj.confidence.setValue(0.6)
        sp = SpatialReasoner()
        sp.load([obj])
        done = sp.run("filter(virtual AND NOT moving) | log(base)")
        self.assertTrue(done)
        # Assume sp.result() returns a list of objects
        self.assertEqual(len(sp.result()), 1)

    def test_filter_label(self):
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8),
                            width=1.0, height=1.0, depth=1.0)
        obj.existence = SpatialExistence.virtual
        obj.label = "Wall"
        obj.confidence.setValue(0.8)
        sp = SpatialReasoner()
        sp.load([obj])
        done = sp.run("filter(label == 'Wall' AND confidence.label > 0.7) | log(base)")
        self.assertTrue(done)
        self.assertEqual(len(sp.result()), 1)

if __name__ == '__main__':
    unittest.main()
