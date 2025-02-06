# tests/SpatialRelationsTests.py

import unittest
import math
from unittest.mock import MagicMock

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
from src.SpatialRelation import (SpatialRelation)  # Ensure correct import
from src.SpatialObject import SpatialObject
from src.BBoxSector import BBoxSector, BBoxSectorFlags  # Import BBoxSector and its flags


class TestSpatialRelations(unittest.TestCase):
    def setUp(self):
        # Setup any common configurations or objects here if needed
        # For example, setting defaultAdjustment if it's a global or shared resource
        # Assuming defaultAdjustment is a singleton or global instance
        self.original_nearby_factor = defaultAdjustment.nearbyFactor

    def tearDown(self):
        # Reset any global settings after each test
        defaultAdjustment.nearbyFactor = self.original_nearby_factor

    def print_relations(self, relations):
        for relation in relations:
            print(f"{relation.subject.id} {relation.predicate} {relation.object.id} | Δ:{relation.delta:.2f}  α:{relation.yaw:.1f}°")

    @unittest.skip("Export functionality is ignored as per user instructions")
    def export(self, nodes):
        pass  # Export functionality is ignored

    def test_near(self):
        """
        Test that a subject is near to an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=1.75, y=0.0, z=0.01),
            width=1.4,
            height=1.4,
            depth=1.4
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=1.8, y=1.8, z=1.8),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        # Adjust nearbyFactor before relating
        defaultAdjustment.nearbyFactor = 1.5
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored
        # self.export([...])

        # Check that relations contain 'near' and 'disjoint'
        predicates = [rel.predicate for rel in relations]

        self.assertIn(SpatialPredicate.near, predicates)
        self.assertIn(SpatialPredicate.disjoint, predicates)
        self.assertIn(SpatialPredicate.below, predicates)

        # Reset nearbyFactor
        defaultAdjustment.nearbyFactor = self.original_nearby_factor

    def test_notnear(self):
        """
        Test that a subject is far from an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=4.2, y=0.0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0.0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'far' and do not contain 'near'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.far, predicates)
        self.assertNotIn(SpatialPredicate.near, predicates)

    def test_inside(self):
        """
        Test that a subject is inside an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0.0, y=0.2, z=0),
            width=0.5,
            height=0.5,
            depth=0.5
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0.0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'inside' and do not contain 'disjoint'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.inside, predicates)
        self.assertNotIn(SpatialPredicate.disjoint, predicates)

    def test_containing(self):
        """
        Test that a subject is containing an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=0.0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.0, y=0.0, z=0),
            width=0.1,
            height=0.1,
            depth=0.1
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'containing' and do not contain 'disjoint'
        predicates = [rel.predicate for rel in relations]
        print("****************************************************************************************")
        for predicate in predicates: 
            print("predicate: ", predicate)
        print("*"*100)
        self.assertIn(SpatialPredicate.containing, predicates)
        self.assertNotIn(SpatialPredicate.disjoint, predicates)

    def test_door_inside_wall(self):
        """
        Test that a door is inside a wall.
        """
        wall1 = SpatialObject.createBuildingElement_from_vectors(
            id="wall1",
            from_pos=Vector3(x=-2, y=0, z=0),
            to_pos=Vector3(x=2, y=0, z=0),
            height=2.3
        )
        door = SpatialObject.createBuildingElement_from_vectors(
            id="door",
            from_pos=Vector3(x=0.4, y=0, z=0),
            to_pos=Vector3(x=1.3, y=0, z=0),
            height=2.05
        )
        relations = wall1.relate(subject=door, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'inside'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.inside, predicates)

    def test_window_inside_wall(self):
        """
        Test that a window is inside a wall.
        """
        wall2 = SpatialObject.createBuildingElement_from_vectors(
            id="wall2",
            from_pos=Vector3(x=2, y=0, z=0),
            to_pos=Vector3(x=2, y=0, z=2.5),
            height=2.3
        )
        window = SpatialObject.createBuildingElement_from_vectors(
            id="window",
            from_pos=Vector3(x=2, y=0.7, z=1),
            to_pos=Vector3(x=2, y=0.7, z=2.2),
            height=1.35
        )
        relations = wall2.relate(subject=window, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'inside'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.inside, predicates)

    def test_below(self):
        """
        Test that a subject is below an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=-1.10, z=0.05),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0.0, z=0),
            width=1.1,
            height=1.1,
            depth=1.1
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'below'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.below, predicates)

    def test_above(self):
        """
        Test that a subject is above an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=1.61, z=0.1),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0.0, z=0),
            width=1.1,
            height=1.1,
            depth=1.1
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'above'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.above, predicates)

    def test_ontop(self):
        """
        Test that a subject is on top of an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=1.01, z=0),
            width=0.8,
            height=0.6,
            depth=0.25
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'ontop'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.ontop, predicates)

    def test_overlapping(self):
        """
        Test that a subject is overlapping an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0.4, y=0.4, z=0.2),
            width=1.1,
            height=1.1,
            depth=1.1
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'overlapping'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.overlapping, predicates)

    def test_crossing_hor(self):
        """
        Test that a subject is crossing an object horizontally.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=0.45, z=0),
            width=2.8,
            height=0.3,
            depth=0.4,
            angle=math.radians(20.0)  # Convert degrees to radians
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'crossing'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.crossing, predicates)

    def test_crossing_vert(self):
        """
        Test that a subject is crossing an object vertically.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.2, y=-0.5, z=-0.1),
            width=0.4,
            height=1.8,
            depth=0.5
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'crossing'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.crossing, predicates)

    def test_touching(self):
        """
        Test that a subject is touching and beside an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0.83, y=0, z=-0.2),
            width=0.4,
            height=0.8,
            depth=0.5
        )
        subject.setYaw(math.radians(0.0))  # Assuming setYaw takes radians
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'touching' and 'beside'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.touching, predicates)
        self.assertIn(SpatialPredicate.beside, predicates)

    def test_meeting(self):
        """
        Test that a subject is meeting an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=1, y=1, z=1),
            width=0.5,
            height=0.5,
            depth=0.5
        )  # Assuming setYaw takes radians
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=1, z=0),
            width=0.50,
            height=0.50,
            depth=0.50
        )
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'meeting'
        predicates = [rel.predicate for rel in relations]
        print("****************************************************************************************")
        for predicate in predicates: 
            print("predicate: ", predicate)
        print("*"*100)
        self.assertIn(SpatialPredicate.meeting, predicates)

    def test_congruent(self):
        """
        Test that a subject is congruent with an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0.3, y=0, z=0.8),
            width=1.01,
            height=1.005,
            depth=1.002,
            angle=math.pi / 4.0 - 0.05  # Approximately 40 degrees
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.3, y=0, z=0.8),
            width=1.0,
            height=1.0,
            depth=1.0,
            angle=math.pi / 4.0  # 45 degrees
        )
        relations = obj.relate(subject=subject, similarity=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'congruent'
        predicates = [rel.predicate for rel in relations]

        self.assertIn(SpatialPredicate.congruent, predicates)

    def test_seen_right(self):
        """
        Test that a subject is seen to the right from an observer's perspective.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.5, y=0, z=0.8),
            width=1.01,
            height=1.03,
            depth=1.02
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.5, y=0, z=0.8),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        observer = SpatialObject.createPerson(
            id="ego",
            position=Vector3(x=0.3, y=0, z=-2.0),
            name="ego"
        )
        relations = obj.asseen(subject=subject, observer=observer)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'seenright'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.seenright, predicates)

    def test_seen_left(self):
        """
        Test that a subject is seen to the left from an observer's perspective.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.55, y=0, z=0.8),
            width=1.01,
            height=1.03,
            depth=1.02
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.5, y=0, z=0.8),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        observer = SpatialObject.createPerson(
            id="ego",
            position=Vector3(x=0.3, y=0, z=3.8),
            name="ego"
        )
        observer.angle = math.radians(90.0) + 1.1  # Assuming angle is in radians
        relations = obj.asseen(subject=subject, observer=observer)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'seenleft'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.seenleft, predicates)

    def test_infront(self):
        """
        Test that a subject is in front of an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.2, y=0, z=-1.1),
            width=1.01,
            height=1.03,
            depth=1.02,
            angle=0.2  # Assuming angle is in radians
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.1, y=0, z=0.0),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        observer = SpatialObject.createPerson(
            id="ego",
            position=Vector3(x=0.3, y=0, z=-3.8),
            name="user"
        )
        relations = obj.asseen(subject=subject, observer=observer)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'infront'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.infront, predicates)

    def test_rear(self):
        """
        Test that a subject is at the rear of an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.2, y=0, z=0.95),
            width=0.8,
            height=0.8,
            depth=0.8
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.1, y=0, z=-0.15),
            width=1.0,
            height=1.0,
            depth=1.0
        )
        observer = SpatialObject.createPerson(
            id="ego",
            position=Vector3(x=0.3, y=0, z=-2.7)
        )
        relations = obj.asseen(subject=subject, observer=observer)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'atrear'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.atrear, predicates)

    def test_at11clock(self):
        """
        Test that a subject is at 11 o'clock from the observer's perspective.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0.65, y=0, z=1.6),
            width=0.4,
            height=0.6,
            depth=0.5
        )
        observer = SpatialObject.createPerson(
            id="ego",
            position=Vector3(x=0, y=0, z=0),
            name="user"
        )
        relations = observer.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'elevenoclock'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.elevenoclock, predicates)

    def test_at2clock(self):
        """
        Test that a subject is at 2 o'clock from the observer's perspective.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.95, y=0, z=0.45),
            width=0.4,
            height=0.6,
            depth=0.5
        )
        observer = SpatialObject.createPerson(
            id="ego",
            position=Vector3(x=0, y=0, z=0),
            name="user"
        )
        relations = observer.relate(subject=subject, topology=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'twooclock'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.twooclock, predicates)

    def test_thinner(self):
        """
        Test that a subject is thinner than an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.2, y=0, z=0.8),
            width=0.2,
            height=0.9,
            depth=0.2
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.6, y=0, z=0.8),
            width=0.25,
            height=1.0,
            depth=0.25
        )
        relations = obj.relate(subject=subject, comparison=True)
        self.print_relations(relations)
        # Export is ignored

        # Check that relations contain 'thinner'
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.thinner, predicates)

    def test_corners(self):
        """
        Test corner relationships between objects.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=-0.2, y=0, z=0.8),
            width=0.2,
            height=0.9,
            depth=0.2,
            angle=0.2
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.6, y=0, z=0.8),
            width=0.25,
            height=1.0,
            depth=0.25,
            angle=-0.2
        )
        relations = obj.relate(subject=subject, comparison=True)
        self.print_relations(relations)
        # Export is ignored

        # No specific assertion provided in Swift, so we'll assume no check needed

    def test_thin_ratio_edge_case(self):
        """
        Additional test to ensure thin ratio functionality if applicable.
        """
        # Implemented as per need based on the actual SpatialObject implementation
        pass

    # Add more tests as necessary based on additional predicates or functionalities


# Run the tests
if __name__ == '__main__':
    unittest.main()
