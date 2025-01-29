# tests/SpatialBasics_test.py

import unittest
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
    ObjectHandling
)
import math


class TestNearbySchema(unittest.TestCase):
    def test_enum_members(self):
        """Test that all NearbySchema members exist and have correct values."""
        self.assertEqual(NearbySchema.fixed.value, "fixed")
        self.assertEqual(NearbySchema.circle.value, "circle")
        self.assertEqual(NearbySchema.sphere.value, "sphere")
        self.assertEqual(NearbySchema.perimeter.value, "perimeter")
        self.assertEqual(NearbySchema.area.value, "area")

    def test_named_method_valid(self):
        """Test the named method with valid names."""
        self.assertEqual(NearbySchema.named("fixed"), NearbySchema.fixed)
        self.assertEqual(NearbySchema.named("circle"), NearbySchema.circle)
        self.assertEqual(NearbySchema.named("sphere"), NearbySchema.sphere)
        self.assertEqual(NearbySchema.named("perimeter"), NearbySchema.perimeter)
        self.assertEqual(NearbySchema.named("area"), NearbySchema.area)

    def test_named_method_invalid(self):
        """Test the named method with invalid names."""
        self.assertIsNone(NearbySchema.named("invalid"))
        self.assertIsNone(NearbySchema.named(""))
        self.assertIsNone(NearbySchema.named("Fixed"))  # Case-sensitive


class TestSectorSchema(unittest.TestCase):
    def test_enum_members(self):
        """Test that all SectorSchema members exist and have correct values."""
        self.assertEqual(SectorSchema.fixed.value, "fixed")
        self.assertEqual(SectorSchema.dimension.value, "dimension")
        self.assertEqual(SectorSchema.perimeter.value, "perimeter")
        self.assertEqual(SectorSchema.area.value, "area")
        self.assertEqual(SectorSchema.nearby.value, "nearby")

    def test_named_method_valid(self):
        """Test the named method with valid names."""
        self.assertEqual(SectorSchema.named("fixed"), SectorSchema.fixed)
        self.assertEqual(SectorSchema.named("dimension"), SectorSchema.dimension)
        self.assertEqual(SectorSchema.named("perimeter"), SectorSchema.perimeter)
        self.assertEqual(SectorSchema.named("area"), SectorSchema.area)
        self.assertEqual(SectorSchema.named("nearby"), SectorSchema.nearby)

    def test_named_method_invalid(self):
        """Test the named method with invalid names."""
        self.assertIsNone(SectorSchema.named("invalid"))
        self.assertIsNone(SectorSchema.named(""))
        self.assertIsNone(SectorSchema.named("Fixed"))  # Case-sensitive


class TestSpatialAdjustment(unittest.TestCase):
    def test_default_initialization(self):
        """Test the default initialization of SpatialAdjustment."""
        adjustment = SpatialAdjustment()
        self.assertEqual(adjustment.maxGap, 0.02)
        self.assertAlmostEqual(adjustment.maxAngleDelta, 0.05 * math.pi)
        self.assertEqual(adjustment.sectorSchema, SectorSchema.nearby)
        self.assertEqual(adjustment.sectorFactor, 1.0)
        self.assertEqual(adjustment.sectorLimit, 2.5)
        self.assertEqual(adjustment.nearbySchema, NearbySchema.circle)
        self.assertEqual(adjustment.nearbyFactor, 2.0)
        self.assertEqual(adjustment.nearbyLimit, 2.5)
        self.assertEqual(adjustment.longRatio, 4.0)
        self.assertEqual(adjustment.thinRatio, 10.0)

    def test_custom_initialization(self):
        """Test custom initialization of SpatialAdjustment."""
        adjustment = SpatialAdjustment(
            maxGap=0.05,
            angle=math.pi / 4,
            sector_schema=SectorSchema.fixed,
            sector_factor=2.0,
            sector_limit=5.0,
            nearby_schema=NearbySchema.sphere,
            nearby_factor=3.0,
            nearby_limit=6.0
        )
        self.assertEqual(adjustment.maxGap, 0.05)
        self.assertAlmostEqual(adjustment.maxAngleDelta, math.pi / 4)
        self.assertEqual(adjustment.sectorSchema, SectorSchema.fixed)
        self.assertEqual(adjustment.sectorFactor, 2.0)
        self.assertEqual(adjustment.sectorLimit, 5.0)
        self.assertEqual(adjustment.nearbySchema, NearbySchema.sphere)
        self.assertEqual(adjustment.nearbyFactor, 3.0)
        self.assertEqual(adjustment.nearbyLimit, 6.0)
        self.assertEqual(adjustment.longRatio, 4.0)
        self.assertEqual(adjustment.thinRatio, 10.0)

    def test_yaw_property(self):
        """Test the yaw property of SpatialAdjustment."""
        adjustment = SpatialAdjustment(angle=math.pi / 6)
        self.assertAlmostEqual(adjustment.yaw, 30.0)  # 30 degrees

    def test_setYaw_method(self):
        """Test the setYaw method of SpatialAdjustment."""
        adjustment = SpatialAdjustment()
        adjustment.setYaw(45.0)
        self.assertAlmostEqual(adjustment.maxAngleDelta, math.pi / 4)
        self.assertAlmostEqual(adjustment.yaw, 45.0)


class TestSpatialPredicateCategories(unittest.TestCase):
    def test_default_initialization(self):
        """Test the default initialization of SpatialPredicateCategories."""
        categories = SpatialPredicateCategories()
        self.assertTrue(categories.topology)
        self.assertTrue(categories.connectivity)
        self.assertFalse(categories.comparability)
        self.assertFalse(categories.similarity)
        self.assertFalse(categories.sectoriality)
        self.assertFalse(categories.visibility)
        self.assertFalse(categories.geography)

    def test_custom_initialization(self):
        """Test custom initialization of SpatialPredicateCategories."""
        categories = SpatialPredicateCategories()
        categories.topology = False
        categories.connectivity = False
        categories.comparability = True
        categories.similarity = True
        categories.sectoriality = True
        categories.visibility = True
        categories.geography = True

        self.assertFalse(categories.topology)
        self.assertFalse(categories.connectivity)
        self.assertTrue(categories.comparability)
        self.assertTrue(categories.similarity)
        self.assertTrue(categories.sectoriality)
        self.assertTrue(categories.visibility)
        self.assertTrue(categories.geography)


class TestObjectConfidence(unittest.TestCase):
    def test_default_initialization(self):
        """Test the default initialization of ObjectConfidence."""
        confidence = ObjectConfidence()
        self.assertEqual(confidence.pose, 0.0)
        self.assertEqual(confidence.dimension, 0.0)
        self.assertEqual(confidence.label, 0.0)
        self.assertEqual(confidence.look, 0.0)
        self.assertEqual(confidence.value, 0.0)
        self.assertEqual(confidence.spatial, 0.0)

    def test_setValue_method(self):
        """Test the setValue method of ObjectConfidence."""
        confidence = ObjectConfidence()
        confidence.setValue(0.6)
        self.assertEqual(confidence.pose, 0.6)
        self.assertEqual(confidence.dimension, 0.6)
        self.assertEqual(confidence.label, 0.6)
        self.assertEqual(confidence.value, 0.6)
        self.assertEqual(confidence.spatial, 0.6)

    def test_setSpatial_method(self):
        """Test the setSpatial method of ObjectConfidence."""
        confidence = ObjectConfidence()
        confidence.setSpatial(0.8)
        self.assertEqual(confidence.pose, 0.8)
        self.assertEqual(confidence.dimension, 0.8)
        self.assertEqual(confidence.spatial, 0.8)

    def test_asDict_method(self):
        """Test the asDict method of ObjectConfidence."""
        confidence = ObjectConfidence()
        confidence.pose = 0.7
        confidence.dimension = 0.5
        confidence.label = 0.9
        confidence.look = 0.3
        expected_dict = {
            "pose": 0.7,
            "dimension": 0.5,
            "label": 0.9,
            "look": 0.3
        }
        self.assertEqual(confidence.asDict(), expected_dict)


class TestSpatialAtribute(unittest.TestCase):
    def test_enum_members(self):
        """Test that all SpatialAtribute members exist and have correct values."""
        self.assertEqual(SpatialAtribute.none.value, "none")
        self.assertEqual(SpatialAtribute.width.value, "width")
        self.assertEqual(SpatialAtribute.height.value, "height")
        self.assertEqual(SpatialAtribute.depth.value, "depth")
        self.assertEqual(SpatialAtribute.length.value, "length")
        self.assertEqual(SpatialAtribute.angle.value, "angle")
        self.assertEqual(SpatialAtribute.yaw.value, "yaw")
        self.assertEqual(SpatialAtribute.azimuth.value, "azimuth")
        self.assertEqual(SpatialAtribute.footprint.value, "footprint")
        self.assertEqual(SpatialAtribute.frontface.value, "frontface")
        self.assertEqual(SpatialAtribute.sideface.value, "sideface")
        self.assertEqual(SpatialAtribute.surface.value, "surface")
        self.assertEqual(SpatialAtribute.volume.value, "volume")
        self.assertEqual(SpatialAtribute.perimeter.value, "perimeter")
        self.assertEqual(SpatialAtribute.baseradius.value, "baseradius")
        self.assertEqual(SpatialAtribute.radius.value, "radius")
        self.assertEqual(SpatialAtribute.speed.value, "speed")
        self.assertEqual(SpatialAtribute.confidence.value, "confidence")
        self.assertEqual(SpatialAtribute.lifespan.value, "lifespan")


class TestSpatialExistence(unittest.TestCase):
    def test_enum_members(self):
        """Test that all SpatialExistence members exist and have correct values."""
        self.assertEqual(SpatialExistence.undefined.value, "undefined")
        self.assertEqual(SpatialExistence.real.value, "real")
        self.assertEqual(SpatialExistence.virtual.value, "virtual")
        self.assertEqual(SpatialExistence.conceptual.value, "conceptual")
        self.assertEqual(SpatialExistence.aggregational.value, "aggregational")

    def test_named_method_valid(self):
        """Test the named method with valid names."""
        self.assertEqual(SpatialExistence.named("real"), SpatialExistence.real)
        self.assertEqual(SpatialExistence.named("virtual"), SpatialExistence.virtual)
        self.assertEqual(SpatialExistence.named("conceptual"), SpatialExistence.conceptual)
        self.assertEqual(SpatialExistence.named("aggregational"), SpatialExistence.aggregational)
        self.assertEqual(SpatialExistence.named("undefined"), SpatialExistence.undefined)

    def test_named_method_invalid(self):
        """Test the named method with invalid names."""
        self.assertEqual(SpatialExistence.named("invalid"), SpatialExistence.undefined)
        self.assertEqual(SpatialExistence.named(""), SpatialExistence.undefined)
        self.assertEqual(SpatialExistence.named("Real"), SpatialExistence.undefined)  # Case-sensitive


class TestObjectCause(unittest.TestCase):
    def test_enum_members(self):
        """Test that all ObjectCause members exist and have correct values."""
        self.assertEqual(ObjectCause.unknown.value, "unknown")
        self.assertEqual(ObjectCause.plane_detected.value, "plane_detected")
        self.assertEqual(ObjectCause.object_detected.value, "object_detected")
        self.assertEqual(ObjectCause.self_tracked.value, "self_tracked")
        self.assertEqual(ObjectCause.user_captured.value, "user_captured")
        self.assertEqual(ObjectCause.user_generated.value, "user_generated")
        self.assertEqual(ObjectCause.rule_produced.value, "rule_produced")
        self.assertEqual(ObjectCause.remote_created.value, "remote_created")

    def test_named_method_valid(self):
        """Test the named method with valid names."""
        self.assertEqual(ObjectCause.named("unknown"), ObjectCause.unknown)
        self.assertEqual(ObjectCause.named("plane_detected"), ObjectCause.plane_detected)
        self.assertEqual(ObjectCause.named("object_detected"), ObjectCause.object_detected)
        self.assertEqual(ObjectCause.named("self_tracked"), ObjectCause.self_tracked)
        self.assertEqual(ObjectCause.named("user_captured"), ObjectCause.user_captured)
        self.assertEqual(ObjectCause.named("user_generated"), ObjectCause.user_generated)
        self.assertEqual(ObjectCause.named("rule_produced"), ObjectCause.rule_produced)
        self.assertEqual(ObjectCause.named("remote_created"), ObjectCause.remote_created)

    def test_named_method_invalid(self):
        """Test the named method with invalid names."""
        self.assertEqual(ObjectCause.named("invalid"), ObjectCause.unknown)
        self.assertEqual(ObjectCause.named(""), ObjectCause.unknown)
        self.assertEqual(ObjectCause.named("Unknown"), ObjectCause.unknown)  # Case-sensitive


class TestMotionState(unittest.TestCase):
    def test_enum_members(self):
        """Test that all MotionState members exist and have correct values."""
        self.assertEqual(MotionState.unknown.value, "unknown")
        self.assertEqual(MotionState.stationary.value, "stationary")
        self.assertEqual(MotionState.idle.value, "idle")
        self.assertEqual(MotionState.moving.value, "moving")


class TestObjectShape(unittest.TestCase):
    def test_enum_members(self):
        """Test that all ObjectShape members exist and have correct values."""
        self.assertEqual(ObjectShape.unknown.value, "unknown")
        self.assertEqual(ObjectShape.planar.value, "planar")
        self.assertEqual(ObjectShape.cubical.value, "cubical")
        self.assertEqual(ObjectShape.spherical.value, "spherical")
        self.assertEqual(ObjectShape.cylindrical.value, "cylindrical")
        self.assertEqual(ObjectShape.conical.value, "conical")
        self.assertEqual(ObjectShape.irregular.value, "irregular")
        self.assertEqual(ObjectShape.changing.value, "changing")

    def test_named_method_valid(self):
        """Test the named method with valid names."""
        self.assertEqual(ObjectShape.named("unknown"), ObjectShape.unknown)
        self.assertEqual(ObjectShape.named("planar"), ObjectShape.planar)
        self.assertEqual(ObjectShape.named("cubical"), ObjectShape.cubical)
        self.assertEqual(ObjectShape.named("spherical"), ObjectShape.spherical)
        self.assertEqual(ObjectShape.named("cylindrical"), ObjectShape.cylindrical)
        self.assertEqual(ObjectShape.named("conical"), ObjectShape.conical)
        self.assertEqual(ObjectShape.named("irregular"), ObjectShape.irregular)
        self.assertEqual(ObjectShape.named("changing"), ObjectShape.changing)

    def test_named_method_invalid(self):
        """Test the named method with invalid names."""
        self.assertEqual(ObjectShape.named("invalid"), ObjectShape.unknown)
        self.assertEqual(ObjectShape.named(""), ObjectShape.unknown)
        self.assertEqual(ObjectShape.named("Unknown"), ObjectShape.unknown)  # Case-sensitive


class TestObjectHandling(unittest.TestCase):
    def test_enum_members(self):
        """Test that all ObjectHandling members exist and have correct values."""
        self.assertEqual(ObjectHandling.none.value, "none")
        self.assertEqual(ObjectHandling.movable.value, "movable")
        self.assertEqual(ObjectHandling.slidable.value, "slidable")
        self.assertEqual(ObjectHandling.liftable.value, "liftable")
        self.assertEqual(ObjectHandling.portable.value, "portable")
        self.assertEqual(ObjectHandling.rotatable.value, "rotatable")
        self.assertEqual(ObjectHandling.openable.value, "openable")

    def test_enum_members_tangible_not_present(self):
        """Test that 'tangible' is not present in ObjectHandling."""
        self.assertNotIn('tangible', ObjectHandling.__members__)

    def test_enum_usage(self):
        """Test usage of ObjectHandling enum."""
        handling = ObjectHandling.movable
        self.assertEqual(handling, ObjectHandling.movable)
        self.assertEqual(handling.value, "movable")

    def test_enum_invalid_access(self):
        """Test accessing an invalid member of ObjectHandling."""
        with self.assertRaises(KeyError):
            ObjectHandling['tangible']


if __name__ == '__main__':
    unittest.main()
