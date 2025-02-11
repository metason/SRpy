# tests/SpatialRelationsTests.py

import os
import math
import unittest
from unittest.mock import MagicMock

from src.Exporter import SceneExporter
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
from src.SpatialRelation import SpatialRelation
from src.SpatialObject import SpatialObject
from src.BBoxSector import BBoxSector, BBoxSectorFlags
from src.SpatialReasoner import SpatialReasoner


class TestSpatialRelations(unittest.TestCase):
    def setUp(self):
        # Set up a temporary directory for scene exports
        self.temp_dir = "./tests/scenes/"
        os.makedirs(self.temp_dir, exist_ok=True)
        # Instantiate the SceneExporter once for the tests that need export.
        self.exporter = SceneExporter(self.temp_dir)
        # Save original global adjustments.
        self.original_nearby_factor = defaultAdjustment.nearbyFactor

    def tearDown(self):
        # Reset any global settings after each test.
        defaultAdjustment.nearbyFactor = self.original_nearby_factor
        self.exporter = None
        self.exporter = SceneExporter(self.temp_dir)

    def print_relations(self, relations):
        for relation in relations:
            print(f"{relation.subject.id} {relation.predicate} {relation.object.id} | Δ:{relation.delta:.2f}  α:{relation.yaw:.1f}°")


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
        defaultAdjustment.nearbyFactor = 1.5
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)

        spatial_objects = [obj, subject]
        export_filename = f"near.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.near, predicates)
        self.assertIn(SpatialPredicate.disjoint, predicates)
        self.assertIn(SpatialPredicate.below, predicates)

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

        spatial_objects = [obj, subject]
        export_filename = f"not_near.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [obj, subject]
        export_filename = f"inside.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [obj, subject]
        export_filename = f"containing.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

        predicates = [rel.predicate for rel in relations]
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

        spatial_objects = [wall1, door]
        export_filename = f"door_inside_wall.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [wall2, window]
        export_filename = f"window_inside_wall.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)
        
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.inside, predicates)

    def test_below(self):
        """
        Test that a subject is below an object.
        """
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0, y=-1.10, z=0.00),
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

        spatial_objects = [subject, obj]
        export_filename = f"below.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [subject, obj]
        export_filename = f"above.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [subject, obj]
        export_filename = f"ontop.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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
        spatial_reasoner = SpatialReasoner()
        spatial_reasoner.load([obj, subject])
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)

        spatial_objects = [subject, obj]
        export_filename = f"overlapping.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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
            angle=math.radians(20.0)
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

        spatial_objects = [subject, obj]
        export_filename = f"crossing_hor.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [subject, obj]
        export_filename = f"crossing_vert.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.crossing, predicates)

    def test_touching(self):
        """
        Test that a subject is touching and beside an object.
        """
        # Create the subject with the same properties as in Swift.
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0.83, y=0, z=-0.2),
            width=0.4,
            height=0.8,
            depth=0.5
        )
        subject.setYaw(45.0)  # Set yaw to 45 degrees, as in the Swift test.

        # Create the object.
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )

        # Compute the spatial relations.
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)

        # Optionally export the scene for visualization.
        spatial_objects = [subject, obj]
        export_filename = "touching.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

        # Verify that both 'touching' and 'beside' predicates are present.
        predicates = [rel.predicate for rel in relations]
        self.assertIn(SpatialPredicate.touching, predicates)
        self.assertIn(SpatialPredicate.beside, predicates)

    def test_meeting(self):
        """
        Test that the subject is meeting the object.
        """
        # Create the subject with the same properties as in Swift.
        subject = SpatialObject(
            id="subj",
            position=Vector3(x=0.76, y=0, z=-0.5),
            width=0.8,
            height=0.8,
            depth=0.5
        )
        subject.setYaw(90.0)  # Rotate the subject 90 degrees around the yaw axis.

        # Create the object (the reference spatial object).
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0, y=0, z=0),
            width=1.0,
            height=1.0,
            depth=1.0
        )

        # Compute the spatial relations between object and subject.
        relations = obj.relate(subject=subject, topology=True)
        self.print_relations(relations)

        # Optionally export the scene for visualization.
        spatial_objects = [subject, obj]
        export_filename = "meeting.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

        # Verify that the 'meeting' predicate is among the computed relations.
        predicates = [rel.predicate for rel in relations]
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
            angle=math.pi / 4.0 - 0.05
        )
        obj = SpatialObject(
            id="obj",
            position=Vector3(x=0.3, y=0, z=0.8),
            width=1.0,
            height=1.0,
            depth=1.0,
            angle=math.pi / 4.0
        )
        relations = obj.relate(subject=subject, similarity=True)
        self.print_relations(relations)

        spatial_objects = [subject, obj]
        export_filename = f"congruent.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [obj, subject, observer]
        export_filename = f"seen_right.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)
        
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
        observer.angle = math.radians(90.0) + 1.1
        relations = obj.asseen(subject=subject, observer=observer)
        self.print_relations(relations)

        spatial_objects = [obj, subject, observer]
        export_filename = f"seen_left.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)
        
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
            angle=0.2
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

        spatial_objects = [obj, subject, observer]
        export_filename = f"seen_infront.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [obj, subject, observer]
        export_filename = f"rear.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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
        spatial_reasoner = SpatialReasoner()
        spatial_reasoner.load([subject, observer])
        pipeline = """
            deduce(topology visibility)
            | log(base 3D left right seenleft seenright)
        """
        spatial_reasoner.run(pipeline)
        
        relations = observer.relate(subject=subject, topology=True)
        self.print_relations(relations)

        spatial_objects = [ subject, observer]
        export_filename = f"at_11.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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
        
        spatial_reasoner = SpatialReasoner()
        spatial_reasoner.load([subject, observer])
        pipeline = """
            deduce(topology visibility)
            | log(base 3D left right seenleft seenright)
        """
        spatial_reasoner.run(pipeline)
        
        relations = observer.relate(subject=subject, topology=True)
        self.print_relations(relations)

        spatial_objects = [ subject, observer]
        export_filename = f"at_2.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [obj, subject]
        export_filename = f"thinner.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)

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

        spatial_objects = [obj, subject]
        export_filename = f"corners.usdz"
        self.exporter = SceneExporter(self.temp_dir)
        self.exporter.exportUSDZ(spatial_objects, export_filename)
        

    def test_thin_ratio_edge_case(self):
        """
        Additional test to ensure thin ratio functionality if applicable.
        """

        pass


if __name__ == '__main__':
    unittest.main()
