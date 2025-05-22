# tests/SpatialObject_test.py

import unittest
import math
from unittest.mock import MagicMock
import datetime  # Added import for datetime operations

# Import the necessary classes and enums from your modules
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
    defaultAdjustment
)
from src.SpatialPredicate import (
    SpatialPredicate,
    PredicateTerm,
    SpatialTerms,
    proximity,
    directionality,
    adjacency,
    orientations,
    assembly,
    topology,
    contacts,
    connectivity,
    comparability,
    similarity,
    visibility,
    geography,
    sectors,
)
from src.SpatialReasoner import SpatialReasoner
from src.SpatialRelation import SpatialRelation  # Ensure correct import
from src.SpatialObject import SpatialObject
from src.BBoxSector import BBoxSector, BBoxSectorFlags  # Import BBoxSector and its flags


class TestSpatialObjectInitialization(unittest.TestCase):
    def test_default_initialization(self):
        obj = SpatialObject(
            id="obj1",
            position=Vector3(),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        self.assertEqual(obj.id, "obj1")
        self.assertEqual(obj.position, Vector3())
        self.assertEqual(obj.width, 1.0)
        self.assertEqual(obj.height, 1.0)
        self.assertEqual(obj.depth, 1.0)
        self.assertEqual(obj.angle, 0.0)
        self.assertEqual(obj.label, "")
        self.assertEqual(obj.confidence.value, 0.0)
        self.assertFalse(obj.immobile)
        self.assertEqual(obj.shape, ObjectShape.unknown)
        self.assertFalse(obj.visible)
        self.assertFalse(obj.focused)

    def test_custom_initialization(self):
        position = Vector3(1.0, 2.0, 3.0)
        obj = SpatialObject(
            id="obj2",
            position=position,
            width=2.0,
            height=3.0,
            depth=4.0,
            angle=math.pi / 4,
            label="Test Object",
            confidence=0.8
        )
        self.assertEqual(obj.id, "obj2")
        self.assertEqual(obj.position, position)
        self.assertEqual(obj.width, 2.0)
        self.assertEqual(obj.height, 3.0)
        self.assertEqual(obj.depth, 4.0)
        self.assertAlmostEqual(obj.angle, math.pi / 4, places=5)
        self.assertEqual(obj.label, "Test Object")
        self.assertAlmostEqual(obj.confidence.value, 0.8, places=5)
        self.assertFalse(obj.immobile)
        self.assertEqual(obj.shape, ObjectShape.unknown)
        self.assertFalse(obj.visible)
        self.assertFalse(obj.focused)


class TestSpatialObjectDerivedProperties(unittest.TestCase):
    def setUp(self):
        self.obj = SpatialObject(
            id="obj3",
            position=Vector3(0.0, 0.0, 0.0),
            width=2.0,
            height=4.0,
            depth=6.0
        )

    def test_center_property(self):
        # Assuming center is calculated as (position.x + width/2, position.y + height/2, position.z + depth/2)
        expected_center = Vector3(0.0, 2.0, 0.0)
        self.assertEqual(self.obj.center, expected_center)

    def test_volume_property(self):
        expected_volume = 2.0 * 4.0 * 6.0
        self.assertEqual(self.obj.volume, expected_volume)

    def test_footprint_property(self):
        expected_footprint = 2.0 * 6.0  # width * depth
        self.assertEqual(self.obj.footprint, expected_footprint)

    def test_surface_property(self):
        # Surface area = 2*(wh + wd + hd)
        expected_surface = 2.0 * (4.0 * 2.0 + 6.0 * 2.0 + 6.0 * 4.0)
        self.assertEqual(self.obj.surface, expected_surface)

    def test_radius_property(self):
        # Assuming radius is the magnitude from the center to a corner
        expected_radius = Vector3(1.0, 2.0, 3.0).magnitude()
        self.assertAlmostEqual(self.obj.radius, expected_radius, places=5)

    def test_baseradius_property(self):
        # Assuming baseradius is the hypotenuse of width/2 and depth/2
        expected_baseradius = math.hypot(2.0 / 2.0, 6.0 / 2.0)
        self.assertAlmostEqual(self.obj.baseradius, expected_baseradius, places=5)


class TestSpatialObjectPositionMethods(unittest.TestCase):
    def setUp(self):
        self.obj = SpatialObject(
            id="obj4",
            position=Vector3(1.0, 1.0, 1.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            confidence=0.0
        )
        self.obj.adjustment = SpatialAdjustment()

    def test_set_position_updates_velocity(self):
        # Mock the 'updated' timestamp to simulate elapsed time
        self.obj.updated = datetime.datetime.now() - datetime.timedelta(seconds=1)
        new_position = Vector3(2.0, 2.0, 2.0)
        self.obj.setPosition(new_position)
        expected_velocity = (new_position - Vector3(1.0, 1.0, 1.0)) / 1.0  # Assuming delta time is 1 second
        self.assertAlmostEqual(self.obj.velocity, expected_velocity,places=2)
        self.assertAlmostEqual(self.obj.position, new_position,places=2)

    def test_set_position_without_movement(self):
        # If the object is immobile, velocity should not update
        self.obj.immobile = True
        self.obj.updated = datetime.datetime.now() - datetime.timedelta(seconds=1)
        new_position = Vector3(3.0, 3.0, 3.0)
        self.obj.setPosition(new_position)
        self.assertEqual(self.obj.velocity, Vector3())  # Velocity remains unchanged
        self.assertEqual(self.obj.position, new_position)

    def test_set_center(self):
        new_center = Vector3(5.0, 5.0, 5.0)
        self.obj.setCenter(new_center)
        # Assuming setCenter adjusts the position to make the center the new_center
        expected_position = Vector3(
            new_center.x - self.obj.width / 2.0,
            new_center.y - self.obj.height / 2.0,
            new_center.z - self.obj.depth / 2.0
        )
        self.assertEqual(self.obj.position, expected_position)


class TestSpatialObjectRotation(unittest.TestCase):
    def setUp(self):
        self.obj = SpatialObject(
            id="obj5",
            position=Vector3(0.0, 0.0, 0.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            angle=0.0
        )

    def test_rotate_pts(self):
        pts = [Vector3(1.0, 0.0, 1.0), Vector3(0.0, 0.0, 1.0)]
        rotated = self.obj.rotate_pts(pts, math.pi / 2)
        expected = [Vector3(-1.0, 0.0, 1.0), Vector3(-1.0, 0.0, 0.0)]
        for r, e in zip(rotated, expected):
            self.assertAlmostEqual(r.x, e.x, places=5)
            self.assertAlmostEqual(r.y, e.y, places=5)
            self.assertAlmostEqual(r.z, e.z, places=5)

    def test_into_local(self):
        global_pt = Vector3(1.0, 0.0, 1.0)
        self.obj.angle = -math.pi / 2  # 90 degrees
        local_pt = self.obj.intoLocal(global_pt)
        # After rotating -90 degrees, (1, 0, 1) becomes (1.0, 0.0, -1.0)
        expected_local_pt = Vector3(1.0, 0.0, -1.0)
        self.assertAlmostEqual(local_pt.x, expected_local_pt.x, places=5)
        self.assertAlmostEqual(local_pt.y, expected_local_pt.y, places=5)
        self.assertAlmostEqual(local_pt.z, expected_local_pt.z, places=5)


class TestSpatialObjectSectorMethods(unittest.TestCase):
    def setUp(self):
        self.obj = SpatialObject(
            id="obj6",
            position=Vector3(0.0, 0.0, 0.0),
            width=4.0,
            height=4.0,
            depth=4.0
        )
        self.obj.adjustment = SpatialAdjustment(maxGap=0.5)

    def test_sector_of_inside_point(self):
        point = Vector3(1.0, 1.0, 1.0)
        
        subject = SpatialObject(
            id="subj",
            position=point,
            width=0.5,
            height=0.5,
            depth=0.5
        )
        center = self.obj.intoLocal(subject.center)
        sector = self.obj.sectorOf(center)
        # Check if 'i' flag is set
        self.assertTrue(sector.contains(BBoxSectorFlags.i))

    def test_sector_of_left_point(self):
        point = Vector3(3.0, 1.0, 1.0)  # Beyond width/2 + maxGap (4/2 + 0.5 = 2.5)
        subject = SpatialObject(
            id="subj",
            position=point,
            width=0.5,
            height=0.5,
            depth=0.5
        )
        center = self.obj.intoLocal(subject.center)
        sector = self.obj.sectorOf(center)
        self.assertTrue(sector.contains(BBoxSectorFlags.l))

    def test_sector_of_right_point(self):
        point = Vector3(-3.0, 1.0, 1.0)  # Beyond -width/2 - maxGap
        sector = self.obj.sectorOf(point)
        self.assertTrue(sector.contains(BBoxSectorFlags.r))

    def test_sector_of_ahead_point(self):
        point = Vector3(1.0, 1.0, 3.0)  # Beyond depth/2 + maxGap
        sector = self.obj.sectorOf(point)
        self.assertTrue(sector.contains(BBoxSectorFlags.a))

    def test_sector_of_behind_point(self):
        point = Vector3(1.0, 1.0, -3.0)  # Beyond -depth/2 - maxGap
        sector = self.obj.sectorOf(point)
        self.assertTrue(sector.contains(BBoxSectorFlags.b))

    def test_sector_of_above_point(self):
        point = Vector3(1.0, 5.0, 1.0)  # Above height
        sector = self.obj.sectorOf(point)
        self.assertTrue(sector.contains(BBoxSectorFlags.o))

    def test_sector_of_under_point(self):
        point = Vector3(1.0, -1.0, 1.0)  # Below 0
        sector = self.obj.sectorOf(point)
        self.assertTrue(sector.contains(BBoxSectorFlags.u))


class TestSpatialObjectSpatialRelations(unittest.TestCase):
    def setUp(self):
        self.obj1 = SpatialObject(
            id="obj7",
            position=Vector3(0.0, 0.0, 0.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            confidence=0.0
        )
        self.obj2 = SpatialObject(
            id="obj8",
            position=Vector3(1.0, 0.0, 1.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            confidence=0.0
        )
        # Mock SpatialRelation and SpatialPredicate if needed
        # Assuming SpatialRelation is correctly implemented
        adjustment_1 = SpatialAdjustment()
        adjustment_1.maxGap = 1.0
        adjustment_2 = SpatialAdjustment()
        adjustment_2.maxGap = 1.0
        
        self.obj1.adjustment = adjustment_1
        self.obj2.adjustment = adjustment_2
        # create the spatial context SpatialReasoner
        self.spatial_reasoner = SpatialReasoner()
        self.spatial_reasoner.load([self.obj1, self.obj2])
        pipeline = """
            deduce(topology visibility)
            | log(base 3D left right seenleft seenright)
        """
        self.spatial_reasoner.run(pipeline)
        
    def test_near_relation(self):
        relations = self.obj1.topologies(self.obj2)
        near_rel = next((rel for rel in relations if rel.predicate == SpatialPredicate.near), None)
        self.assertIsNotNone(near_rel)
        expected_gap = (self.obj2.center - self.obj1.center).magnitude()
        self.assertAlmostEqual(near_rel.delta, expected_gap, places=5)

    def test_far_relation(self):
        self.obj2.position = Vector3(10.0, 0.0, 10.0)
        relations = self.obj1.topologies(self.obj2)
        far_rel = next((rel for rel in relations if rel.predicate == SpatialPredicate.far), None)
        self.assertIsNotNone(far_rel)
        expected_gap = (self.obj2.center - self.obj1.center).magnitude()
        self.assertAlmostEqual(far_rel.delta, expected_gap, places=5)

    def test_overlapping_relation(self):
        # Objects overlap
        self.obj2.position = Vector3(1.0, 0.0, 1.0)  # Overlaps with obj1
        relations = self.obj1.topologies(self.obj2)
        overlapping_rel = next((rel for rel in relations if rel.predicate == SpatialPredicate.overlapping), None)
        self.assertIsNotNone(overlapping_rel)

    def test_disjoint_relation(self):
        # Objects are disjoint
        self.obj2.position = Vector3(5.0, 0.0, 5.0)
        relations = self.obj1.topologies(self.obj2)
        disjoint_rel = next((rel for rel in relations if rel.predicate == SpatialPredicate.disjoint), None)
        self.assertIsNotNone(disjoint_rel)

    def test_inside_relation(self):
        # obj2 is inside obj1
        self.obj1.width = 10.0
        self.obj1.height = 10.0
        self.obj1.depth = 10.0
        self.obj2.position = Vector3(1.0, 1.0, 1.0)
        relations = self.obj1.topologies(self.obj2)
        inside_rel = next((rel for rel in relations if rel.predicate == SpatialPredicate.inside), None)
        self.assertIsNotNone(inside_rel)

    def test_containing_relation(self):
        # obj1 is contained within obj2
        obj1 = SpatialObject(id="obj1", position= Vector3(0.0, 0.2,0.0), width=0.5, height=0.5, depth=0.5)
        obj2 = SpatialObject(id="obj2", position= Vector3(0.0, 0.0,0.0), width=1.0, height=1.0, depth=1.0)
        relations = obj1.topologies(obj2)
        for relation in relations:
            print("relations: ",relation.desc())
        containing_rel = next((rel for rel in relations if rel.predicate == SpatialPredicate.containing), None)
        self.assertIsNotNone(containing_rel)

    def test_same_center_relation(self):
        # Both objects have the same center
        self.obj1.position = Vector3(0.0, 0.0, 0.0)
        self.obj2.position = Vector3(0.0, 0.0, 0.0)
        relations = self.obj1.topologies(self.obj2)
        ## print all relations
        
        samecenter_rel = next((rel for rel in relations if rel.predicate == SpatialPredicate.samecenter), None)
        self.assertIsNotNone(samecenter_rel)
        self.assertEqual(samecenter_rel.delta, 0.0)


class TestSpatialObjectSerialization(unittest.TestCase):
    def setUp(self):
        self.obj = SpatialObject(
            id="obj9",
            position=Vector3(1.0, 2.0, 3.0),
            width=4.0,
            height=5.0,
            depth=6.0,
            angle=math.pi / 3,
            label="Serializable Object",
            confidence=0.9
        )
        self.obj.cause = ObjectCause.object_detected
        self.obj.existence = SpatialExistence.real
        self.obj.shape = ObjectShape.cubical
        self.obj.visible = True
        self.obj.focused = False
        self.obj.setData("extra_attr", 123.456)
        
        self.spatial_reasoner = SpatialReasoner()
        self.spatial_reasoner.load([self.obj])

    def test_as_dict(self):
        obj_dict = self.obj.asDict()
        self.assertEqual(obj_dict["id"], "obj9")
        self.assertEqual(obj_dict["position"], [1.0, 2.0, 3.0])
        self.assertEqual(obj_dict["width"], 4.0)
        self.assertEqual(obj_dict["height"], 5.0)
        self.assertEqual(obj_dict["depth"], 6.0)
        self.assertEqual(obj_dict["angle"], math.pi / 3)
        self.assertEqual(obj_dict["label"], "Serializable Object")
        self.assertEqual(obj_dict["cause"], ObjectCause.object_detected.value)
        self.assertEqual(obj_dict["existence"], SpatialExistence.real.value)
        self.assertEqual(obj_dict["shape"], ObjectShape.cubical.value)
        self.assertTrue(obj_dict["visible"])
        self.assertFalse(obj_dict["focused"])
        self.assertEqual(obj_dict["extra_attr"], 123.456)

    def test_to_any(self):
        obj_any = self.obj.toAny()
        self.assertEqual(obj_any["id"], "obj9")
        self.assertEqual(obj_any["position"], [1.0, 2.0, 3.0])
        self.assertEqual(obj_any["width"], 4.0)
        self.assertEqual(obj_any["height"], 5.0)
        self.assertEqual(obj_any["depth"], 6.0)
        self.assertEqual(obj_any["angle"], math.pi / 3)
        self.assertEqual(obj_any["label"], "Serializable Object")
        self.assertEqual(obj_any["type"], "")  # Default type
        self.assertEqual(obj_any["supertype"], "")  # Default supertype
        self.assertEqual(obj_any["cause"], ObjectCause.object_detected.value)
        self.assertEqual(obj_any["existence"], SpatialExistence.real.value)
        self.assertEqual(obj_any["shape"], ObjectShape.cubical.value)
        self.assertTrue(obj_any["visible"])
        self.assertFalse(obj_any["focused"])
        self.assertEqual(obj_any["extra_attr"], 123.456)

    def test_from_any(self):
        input_data = {
            "id": "obj10",
            "position": [7.0, 8.0, 9.0],
            "width": 10.0,
            "height": 11.0,
            "depth": 12.0,
            "angle": math.pi / 4,
            "label": "Updated Object",
            "type": "Box",
            "supertype": "Container",
            "confidence": 0.95,
            "cause": "user_generated",
            "existence": "virtual",
            "immobile": True,
            "shape": "spherical",
            "look": "Shiny",
            "visible": False,
            "focused": True,
            "new_attr": "additional data"
        }
        self.obj.fromAny(input_data)
        self.assertEqual(self.obj.id, "obj10")
        self.assertEqual(self.obj.position, Vector3(7.0, 8.0, 9.0))
        self.assertEqual(self.obj.width, 10.0)
        self.assertEqual(self.obj.height, 11.0)
        self.assertEqual(self.obj.depth, 12.0)
        self.assertAlmostEqual(self.obj.angle, math.pi / 4, places=5)
        self.assertEqual(self.obj.label, "Updated Object")
        self.assertEqual(self.obj.type, "Box")
        self.assertEqual(self.obj.supertype, "Container")
        self.assertAlmostEqual(self.obj.confidence.value, 0.95, places=5)
        self.assertEqual(self.obj.cause, ObjectCause.user_generated)
        self.assertEqual(self.obj.existence, SpatialExistence.virtual)
        self.assertTrue(self.obj.immobile)
        self.assertEqual(self.obj.shape, ObjectShape.spherical)
        self.assertEqual(self.obj.look, "Shiny")
        self.assertFalse(self.obj.visible)
        self.assertTrue(self.obj.focused)
        self.assertEqual(self.obj.data["new_attr"], "additional data")


class TestSpatialObjectRelationValue(unittest.TestCase):
    def setUp(self):
        self.obj1 = SpatialObject(
            id="obj11",
            position=Vector3(0.0, 0.0, 0.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            angle=0.0,
            confidence=0.0
        )
        self.obj2 = SpatialObject(
            id="obj12",
            position=Vector3(1.0, 0.0, 1.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            angle=math.pi / 2,
            confidence=0.0
        )
        # Mock the context and SpatialRelation
        self.obj1.context = MagicMock()
        relation = SpatialRelation(
            subject=self.obj1,
            predicate=SpatialPredicate.near,
            object=self.obj2,
            delta=1.414,
            angle=math.pi / 2
        )
        self.obj1.context.relationsWith.return_value = [relation]

    def test_relation_value_angle(self):
        value = self.obj1.relationValue("near.angle", [0])
        self.assertAlmostEqual(value, math.pi / 2, places=5)

    def test_relation_value_delta(self):
        value = self.obj1.relationValue("near.delta", [0])
        self.assertAlmostEqual(value, 1.414, places=5)

    def test_relation_value_nonexistent_predicate(self):
        value = self.obj1.relationValue("far.delta", [0])
        self.assertEqual(value, 0.0)

    def test_relation_value_no_context(self):
        self.obj1.context = None
        value = self.obj1.relationValue("near.delta", [0])
        self.assertEqual(value, 0.0)

    def test_relation_value_invalid_attribute(self):
        value = self.obj1.relationValue("near.invalid", [0])
        self.assertEqual(value, 0.0)


class TestSpatialObjectSerializationEdgeCases(unittest.TestCase):
    def test_serialization_with_missing_attributes(self):
        # Create an object with some missing attributes
        obj = SpatialObject(
            id="obj13",
            position=Vector3(),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=0.0
        )
        obj.setData("optional_attr", "value")
        obj_dict = obj.asDict()
        self.assertIn("optional_attr", obj_dict)
        self.assertEqual(obj_dict["optional_attr"], "value")

    def test_deserialization_with_extra_attributes(self):
        input_data = {
            "id": "obj14",
            "position": [2.0, 3.0, 4.0],
            "width": 5.0,
            "height": 6.0,
            "depth": 7.0,
            "angle": math.pi / 6,
            "label": "Extra Object",
            "type": "Sphere",
            "supertype": "Shape",
            "confidence": 0.85,
            "cause": "remote_created",
            "existence": "conceptual",
            "immobile": False,
            "shape": "spherical",
            "look": "Smooth",
            "visible": True,
            "focused": True,
            "additional_info": {"key1": "value1", "key2": 2.0}
        }
        obj = SpatialObject(
            id="obj15",
            position=Vector3(),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=0.0
        )
        obj.fromAny(input_data)
        self.assertEqual(obj.id, "obj14")
        self.assertEqual(obj.position, Vector3(2.0, 3.0, 4.0))
        self.assertEqual(obj.width, 5.0)
        self.assertEqual(obj.height, 6.0)
        self.assertEqual(obj.depth, 7.0)
        self.assertAlmostEqual(obj.angle, math.pi / 6, places=5)
        self.assertEqual(obj.label, "Extra Object")
        self.assertEqual(obj.type, "Sphere")
        self.assertEqual(obj.supertype, "Shape")
        self.assertAlmostEqual(obj.confidence.value, 0.85, places=5)
        self.assertEqual(obj.cause, ObjectCause.remote_created)
        self.assertEqual(obj.existence, SpatialExistence.conceptual)
        self.assertFalse(obj.immobile)
        self.assertEqual(obj.shape, ObjectShape.spherical)
        self.assertEqual(obj.look, "Smooth")
        self.assertTrue(obj.visible)
        self.assertTrue(obj.focused)
        self.assertEqual(obj.data["additional_info"], {"key1": "value1", "key2": 2.0})


class TestSpatialObjectUtilityMethods(unittest.TestCase):
    def setUp(self):
        self.obj = SpatialObject(
            id="obj16",
            position=Vector3(0.0, 0.0, 0.0),
            width=2.0,
            height=4.0,
            depth=6.0,
            confidence=0.0
        )
        self.obj.adjustment = SpatialAdjustment()

    def test_main_direction(self):
        # Initial dimensions: width=2.0, height=4.0, depth=6.0
        # Dominant dimension: depth (0)
        self.assertEqual(self.obj.mainDirection(), 0)  # Depth is dominant

        # Change dimensions: width=1.0, height=4.0, depth=1.0
        # Dominant dimension: height (2)
        self.obj.width = 1.0
        self.obj.height = 4.0
        self.obj.depth = 1.0
        self.assertEqual(self.obj.mainDirection(), 2)  # Height is dominant

        # Change dimensions: width=5.0, height=2.0, depth=2.0
        # Dominant dimension: width (1)
        self.obj.width = 5.0
        self.obj.height = 2.0
        self.obj.depth = 2.0
        self.assertEqual(self.obj.mainDirection(), 1)  # Width is dominant

    def test_thin_ratio(self):
        self.assertFalse(self.obj.thin)
        self.obj.width = 0.1
        self.obj.height = 10.0
        self.obj.depth = 10.0
        self.assertTrue(self.obj.thin)

    def test_long_ratio(self):
        self.assertEqual(self.obj.long_ratio(), 0)
        self.obj.width = 1.0
        self.obj.height = 5.0
        self.obj.depth = 1.0
        self.assertEqual(self.obj.long_ratio(), 2)

    def test_yaw_property(self):
        self.obj.angle = math.pi
        self.assertAlmostEqual(self.obj.yaw, 180.0, places=5)

    def test_azimuth_property_with_no_context(self):
        self.obj.angle = math.pi / 2
        self.assertEqual(self.obj.azimuth, 0.0)  # Assuming default north is along +x

    def test_azimuth_property_with_context(self):
        # Mock the context and north
        north_vector = Vector3(1.0, 0.0, 0.0)
        self.obj.context = MagicMock()
        self.obj.context.north = north_vector
        # Calculate expected azimuth
        north_angle = math.atan2(north_vector.y, north_vector.x) * 180.0 / math.pi  # 0 degrees
        expected_azimuth = (-math.degrees(self.obj.angle) - north_angle) % 360.0  # Correct formula
        self.assertAlmostEqual(self.obj.azimuth, expected_azimuth, places=5)

    def test_lifespan_property(self):
        self.obj.created = datetime.datetime.now() - datetime.timedelta(seconds=10)
        lifespan = self.obj.lifespan
        self.assertTrue(9.0 <= lifespan <= 11.0)

    def test_update_interval_property(self):
        self.obj.updated = datetime.datetime.now() - datetime.timedelta(seconds=5)
        interval = self.obj.updateInterval
        self.assertTrue(4.0 <= interval <= 6.0)


class TestSpatialObjectSerializationAndDeserialization(unittest.TestCase):
    def test_serialization_deserialization_cycle(self):
        original_obj = SpatialObject(
            id="obj17",
            position=Vector3(3.0, 4.0, 5.0),
            width=6.0,
            height=7.0,
            depth=8.0,
            angle=math.pi / 6,
            label="Cycle Object",
            confidence=0.7
        )
        original_obj.cause = ObjectCause.object_detected
        original_obj.existence = SpatialExistence.real
        original_obj.shape = ObjectShape.spherical
        original_obj.visible = True
        original_obj.focused = True
        original_obj.setData("cycle_attr", "cycle_value")

        obj_dict = original_obj.asDict()
        new_obj = SpatialObject(
            id="dummy",
            position=Vector3(),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=0.0
        )
        new_obj.fromAny(obj_dict)

        self.assertEqual(new_obj.id, original_obj.id)
        self.assertEqual(new_obj.position, original_obj.position)
        self.assertEqual(new_obj.width, original_obj.width)
        self.assertEqual(new_obj.height, original_obj.height)
        self.assertEqual(new_obj.depth, original_obj.depth)
        self.assertAlmostEqual(new_obj.angle, original_obj.angle, places=5)
        self.assertEqual(new_obj.label, original_obj.label)
        self.assertEqual(new_obj.cause, original_obj.cause)
        self.assertEqual(new_obj.existence, original_obj.existence)
        self.assertEqual(new_obj.shape, original_obj.shape)
        self.assertTrue(new_obj.visible)
        self.assertTrue(new_obj.focused)
        self.assertEqual(new_obj.data["cycle_attr"], "cycle_value")


class TestSpatialObjectRelationValue(unittest.TestCase):
    def setUp(self):
        self.obj1 = SpatialObject(
            id="obj11",
            position=Vector3(0.0, 0.0, 0.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            angle=0.0,
            confidence=0.0
        )
        self.obj2 = SpatialObject(
            id="obj12",
            position=Vector3(1.0, 0.0, 1.0),
            width=2.0,
            height=2.0,
            depth=2.0,
            angle=math.pi / 2,
            confidence=0.0
        )
        # Mock the context and SpatialRelation
        self.obj1.context = MagicMock()
        relation = SpatialRelation(
            subject=self.obj1,
            predicate=SpatialPredicate.near,
            object=self.obj2,
            delta=1.414,
            angle=math.pi / 2
        )
        self.obj1.context.relations_with.return_value = [relation]

    def test_relation_value_angle(self):
        value = self.obj1.relationValue("near.angle", [0])
        self.assertAlmostEqual(value, math.pi / 2, places=5)

    def test_relation_value_delta(self):
        value = self.obj1.relationValue("near.delta", [0])
        self.assertAlmostEqual(value, 1.414, places=5)

    def test_relation_value_nonexistent_predicate(self):
        value = self.obj1.relationValue("far.delta", [0])
        self.assertEqual(value, 0.0)

    def test_relation_value_no_context(self):
        self.obj1.context = None
        value = self.obj1.relationValue("near.delta", [0])
        self.assertEqual(value, 0.0)

    def test_relation_value_invalid_attribute(self):
        value = self.obj1.relationValue("near.invalid", [0])
        self.assertEqual(value, 0.0)


class TestSpatialObjectSerializationEdgeCases(unittest.TestCase):
    def test_serialization_with_missing_attributes(self):
        # Create an object with some missing attributes
        obj = SpatialObject(
            id="obj13",
            position=Vector3(),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=0.0
        )
        obj.setData("optional_attr", "value")
        spatial_reasoner = SpatialReasoner()
        spatial_reasoner.load([obj])
        obj_dict = obj.asDict()
        self.assertIn("optional_attr", obj_dict)
        self.assertEqual(obj_dict["optional_attr"], "value")

    def test_deserialization_with_extra_attributes(self):
        input_data = {
            "id": "obj14",
            "position": [2.0, 3.0, 4.0],
            "width": 5.0,
            "height": 6.0,
            "depth": 7.0,
            "angle": math.pi / 6,
            "label": "Extra Object",
            "type": "Sphere",
            "supertype": "Shape",
            "confidence": 0.85,
            "cause": "remote_created",
            "existence": "conceptual",
            "immobile": False,
            "shape": "spherical",
            "look": "Smooth",
            "visible": True,
            "focused": True,
            "additional_info": {"key1": "value1", "key2": 2.0}
        }
        obj = SpatialObject(
            id="obj15",
            position=Vector3(),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=0.0
        )
        spatial_reasoner = SpatialReasoner()
        spatial_reasoner.load([obj])
        
        obj.fromAny(input_data)
        self.assertEqual(obj.id, "obj14")
        self.assertEqual(obj.position, Vector3(2.0, 3.0, 4.0))
        self.assertEqual(obj.width, 5.0)
        self.assertEqual(obj.height, 6.0)
        self.assertEqual(obj.depth, 7.0)
        self.assertAlmostEqual(obj.angle, math.pi / 6, places=5)
        self.assertEqual(obj.label, "Extra Object")
        self.assertEqual(obj.type, "Sphere")
        self.assertEqual(obj.supertype, "Shape")
        self.assertAlmostEqual(obj.confidence.value, 0.85, places=5)
        self.assertEqual(obj.cause, ObjectCause.remote_created)
        self.assertEqual(obj.existence, SpatialExistence.conceptual)
        self.assertFalse(obj.immobile)
        self.assertEqual(obj.shape, ObjectShape.spherical)
        self.assertEqual(obj.look, "Smooth")
        self.assertTrue(obj.visible)
        self.assertTrue(obj.focused)
        self.assertEqual(obj.data["additional_info"], {"key1": "value1", "key2": 2.0})


class TestSpatialObjectUtilityMethods(unittest.TestCase):
    def setUp(self):
        self.obj = SpatialObject(
            id="obj16",
            position=Vector3(0.0, 0.0, 0.0),
            width=2.0,
            height=4.0,
            depth=6.0,
            confidence=0.0
        )
        self.obj.adjustment = SpatialAdjustment()
        
        self.spatial_reasoner = SpatialReasoner()
        self.spatial_reasoner.load([self.obj])
        pipeline = """
            deduce(topology visibility)
            | log(base 3D left right seenleft seenright)
        """  
    def test_main_direction_deep(self):
        self.obj.depth = 25.0
        self.assertEqual(self.obj.mainDirection(), 3)
        
    def test_main_direction_tall(self):
        self.obj.width = 1.0
        self.obj.height = 4.0
        self.obj.depth = 1.0
        self.assertEqual(self.obj.mainDirection(), 2)
        
    def test_main_direction_wide(self):
        self.obj.width = 8.0
        self.obj.height = 2.0
        self.obj.depth = 2.0
        self.assertEqual(self.obj.mainDirection(), 1)

    def test_thin_ratio(self):
        self.assertFalse(self.obj.thin)
        self.obj.width = 0.1
        self.obj.height = 10.0
        self.obj.depth = 10.0
        self.assertTrue(self.obj.thin)

    def test_long_ratio(self):
        obj = SpatialObject("deep_obj", Vector3(0.0, 0.0, 0.0), 1.0, 1.0, 10.0)
        self.assertEqual(obj.long_ratio(), 3)
        obj = SpatialObject("tall_obj", Vector3(0.0, 0.0, 0.0), 1.0, 10.0, 1.0)
        self.assertEqual(obj.long_ratio(), 2)
        
    def test_long_ratio_deep(self):
        obj = SpatialObject("deep_obj", Vector3(0.0, 0.0, 0.0), 1.0, 1.0, 10.0)
        self.assertEqual(obj.long_ratio(), 3)
    
    def test_long_ratio_tall(self):
        obj = SpatialObject("tall_obj", Vector3(0.0, 0.0, 0.0), 1.0, 10.0, 1.0)
        self.assertEqual(obj.long_ratio(), 2)
    
    def test_long_ratio_wide(self):
        obj = SpatialObject("wide_obj", Vector3(0.0, 0.0, 0.0), 10.0, 1.0, 1.0)
        self.assertEqual(obj.long_ratio(), 1)
    
    def test_long_ratio_equal(self):
        obj = SpatialObject("equal_obj", Vector3(0.0, 0.0, 0.0), 1.0, 1.0, 1.0)
        self.assertEqual(obj.long_ratio(), 0)
    
    def test_long_ratio_zero(self):
        obj = SpatialObject("zero_obj", Vector3(0.0, 0.0, 0.0), 0.0, 0.0, 0.0)
        self.assertEqual(obj.long_ratio(), 0)

    def test_yaw_property(self):
        self.obj.angle = math.pi
        self.assertAlmostEqual(self.obj.yaw, 180.0, places=5)


    def test_azimuth_property_with_context(self):
        # Mock the context and north
        north_vector = self.spatial_reasoner.north
        self.obj.context = MagicMock()
        self.obj.context.north = north_vector

        # Calculate expected azimuth
        north_angle = math.degrees(math.atan2(north_vector.y, north_vector.x))  # Compute north angle
        value = self.obj.yaw + north_angle - 90.0  # Match azimuth computation
        expected_azimuth = -math.fmod(self.obj.yaw + north_angle - 90.0, 360.0)

        # Assert expected value
        self.assertAlmostEqual(self.obj.azimuth, expected_azimuth, places=5)

    def test_lifespan_property(self):
        self.obj.created = datetime.datetime.now() - datetime.timedelta(seconds=10)
        lifespan = self.obj.lifespan
        self.assertTrue(9.0 <= lifespan <= 11.0)

    def test_update_interval_property(self):
        self.obj.updated = datetime.datetime.now() - datetime.timedelta(seconds=5)
        interval = self.obj.updateInterval
        self.assertTrue(4.0 <= interval <= 6.0)


class TestSpatialObjectSerializationAndDeserialization(unittest.TestCase):
    def setUp(self):
        self.original_obj = SpatialObject(
            id="obj17",
            position=Vector3(3.0, 4.0, 5.0),
            width=6.0,
            height=7.0,
            depth=8.0,
            angle=math.pi / 6,
            label="Cycle Object",
            confidence=0.7
        )
        
        self.new_obj = SpatialObject(
            id="dummy",
            position=Vector3(),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=0.0
        )
        #self.obj.adjustment = SpatialAdjustment()
        
        self.spatial_reasoner = SpatialReasoner()
        
        
    def test_serialization_deserialization_cycle(self):
       
        self.original_obj.cause = ObjectCause.object_detected
        self.original_obj.existence = SpatialExistence.real
        self.original_obj.shape = ObjectShape.spherical
        self.original_obj.visible = True
        self.original_obj.focused = True
        self.original_obj.setData("cycle_attr", "cycle_value")
        
        original_obj = self.original_obj
        spatial_reasoner = SpatialReasoner()
        spatial_reasoner.load([original_obj])
        obj_dict = original_obj.asDict()
        new_obj = self.new_obj
        print("obj_dict: ",obj_dict)
        new_obj.fromAny(obj_dict)
        self.spatial_reasoner.load([original_obj,new_obj])

        self.assertEqual(new_obj.id, original_obj.id)
        self.assertEqual(new_obj.position, original_obj.position)
        self.assertEqual(new_obj.width, original_obj.width)
        self.assertEqual(new_obj.height, original_obj.height)
        self.assertEqual(new_obj.depth, original_obj.depth)
        self.assertAlmostEqual(new_obj.angle, original_obj.angle, places=5)
        self.assertEqual(new_obj.label, original_obj.label)
        self.assertEqual(new_obj.cause, original_obj.cause)
        self.assertEqual(new_obj.existence, original_obj.existence)
        self.assertEqual(new_obj.shape, original_obj.shape)
        self.assertTrue(new_obj.visible)
        self.assertTrue(new_obj.focused)
        self.assertEqual(new_obj.data["cycle_attr"], "cycle_value")


if __name__ == '__main__':
    unittest.main()
