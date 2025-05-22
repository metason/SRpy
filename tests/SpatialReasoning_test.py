import math
import unittest

from src.SpatialObject import SpatialObject
from src.SpatialReasoner import SpatialReasoner, SpatialInference  # if needed
from src.Vector3 import Vector3
from src.BBoxSector import BBoxSector, BBoxSectorFlags
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

def keywords(query: str):
    "replace python keywords with their corresponding tokens"
    tokens = query.replace("(", "").replace(")", "").split()
    return [t for t in tokens if t.lower() not in {"and", "or", "not"}]


class TestSpatialReasoningQueries(unittest.TestCase):

    def test_parse_keywords(self):
        query = "near AND (left OR right)"
        words = keywords(query)
        self.assertEqual(len(words), 3)

    def test_predicate1(self):
        # immobile == true
        obj = SpatialObject("2", position=Vector3(0, 0, 0),width=0.1, height=1.0, depth=0.1)
        obj.immobile = True
        obj_dict = obj.asDict()  # assume as_dict() returns a dictionary
        self.assertEqual(obj_dict["immobile"], True)
        sr = SpatialReasoner()
        sr.load([obj])
        
        
        condition = "immobile == True"
        # Assume SpatialInference.attribute_predicate returns a callable predicate.
        predicate = SpatialInference.attribute_predicate(condition)
        # In our Python version we simply call the predicate with the dictionary.
        result = predicate(obj_dict)
        self.assertTrue(result)

    def test_predicate2(self):
        # (long AND immobile) OR (long AND volume > 1.5)
        obj = SpatialObject("2", position=Vector3(0, 0, 0), width=0.1, height=1.0, depth=0.1)
        obj.immobile = True
        obj_dict = obj.asDict()
        sr = SpatialReasoner()
        sr.load([obj])
        
        condition = "(long AND immobile) OR (long AND volume > 1.5)"
        predicate = SpatialInference.attribute_predicate(condition)
        result = predicate(obj_dict)
        self.assertTrue(result)
        
    def test_filter_volume(self):
        obj1 = SpatialObject("1", position=Vector3(-1.5, 0, 0), width=0.1, height=1.0, depth=0.1)
        obj2 = SpatialObject("2", position=Vector3(0, 0, 0), width=0.8, height=1.0, depth=0.6)
        obj3 = SpatialObject("3", position=Vector3(0, 1.2, 0.75), width=0.7, height=0.7, depth=0.7)
        obj4 = SpatialObject("3", position=Vector3(0, 1.2, 0.75), width=5, height=5, depth=1.0)
        sr = SpatialReasoner()
        sr.load([obj1, obj2, obj3,obj4])
        done = sr.run("filter(volume > 0.5)")
        self.assertTrue(done)
        filtered_objects = list(filter(lambda obj: obj.volume < 20.4, sr.objects))
        knowledge_base = sr.take_snapshot()
        print(knowledge_base)
        self.assertEqual(len(filtered_objects), 3)
        
    def test_pipeline(self):
            obj1 = SpatialObject( "1", position=Vector3(-1.5, 1.2, 0), width=0.1, height=1.0, depth=0.1)
            obj2 = SpatialObject( "2", position=Vector3(0, 0, 0), width=0.8, height=1.0, depth=0.6)
            obj3 = SpatialObject( "3", position=Vector3(0, 0, 1.6), width=0.8, height=0.8, depth=0.8)
            # initialize reasoner and run pipeline
            sr = SpatialReasoner()
            sr.load([obj1, obj2, obj3])
            pipeline = "filter(volume > 0.4) | pick(left AND above) | log()"
            if sr.run(pipeline):
                # result of processed pipeline as list of SpatialObject 
                result = sr.result() 
                
            
        
    def test_deduce_comparability(self):
        # filter | pick
        obj1 = SpatialObject("1", position=Vector3(-1.5, 0, 0), width=0.1, height=1.0, depth=0.1)
        obj2 = SpatialObject("2", position=Vector3(0, 0, 0), width=0.8, height=1.0, depth=0.6)
        obj3 = SpatialObject("3", position=Vector3(0, 1.2, 0.75), width=0.7, height=0.7, depth=0.7)
        sr = SpatialReasoner()
        sr.load([obj1, obj2, obj3])
        
        pipeline = (
            "deduce(topology comparability) | filter(volume < 20.4) | log(base)"
        )
        done = sr.run(pipeline)
        knowledge_base = sr.take_snapshot()
        #ids = [obj.id for obj in knowledge_base["objects"]]
        #for id in ids:
        #    self.assertTrue(id in {"1", "2", "3"})
        #
        self.assertTrue(done)
        
    def test_filter_pick(self):
        # filter | pick
        obj1 = SpatialObject("1", position=Vector3(-1.5, 0, 0), width=0.1, height=1.0, depth=0.1)
        obj2 = SpatialObject("2", position=Vector3(0, 0, 0), width=0.8, height=1.0, depth=0.6)
        obj3 = SpatialObject("3", position=Vector3(0, 1.2, 0.75),width=0.7, height=0.7, depth=0.7)
        sr = SpatialReasoner()
        sr.load([obj1, obj2, obj3])
        
        pipeline = (
            "deduce(topology comparability) | filter(volume < 20.4) | pick(ahead AND smaller) | log(base)"
        )
        done = sr.run(pipeline)
        print("Objects in base:", sr.base.get("objects"))
        self.assertTrue(done)

    def test_log_aligned_meeting(self):
        subject = SpatialObject("subj", position=Vector3(-0.55, 0, 0.8),width=1.01, height=1.03, depth=1.02)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8),width=1.0, height=1.0, depth=1.0)
        obj.angle = math.pi / 2.0
        observer = SpatialObject.createPerson("user",
                                                position=Vector3(0.3, 0, 3.8),
                                                name="observer")
        observer.angle = math.pi + 0.24
        sr = SpatialReasoner()
        sr.load([subject, obj, observer])
        done = sr.run("log(base 3D aligned meeting opposite)")
        self.assertTrue(done)

    def test_opposite_walls(self):
        wall1 = SpatialObject.createBuildingElement_from_vectors("wall1", from_pos=Vector3(-2, 0, -1), to_pos=Vector3(2, 0, -1),height=2.3, depth=0.4)
        wall2 = SpatialObject.createBuildingElement_from_vectors("wall2", from_pos=Vector3(2, 0, 2.5), to_pos=Vector3(-2, 0, 2.5),height=2.3, depth=0.4)
        sr = SpatialReasoner()
        sr.adjustment.sectorSchema = SectorSchema.fixed
        sr.adjustment.sectorFactor = 1.0
        sr.adjustment.nearbySchema = NearbySchema.fixed
        sr.adjustment.nearbyFactor = 1.0
        sr.load([wall1, wall2])
        pipeline = (
            "deduce(topology connectivity) | select(opposite) | log(base 3D beside)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)
        self.assertEqual(len(sr.result()), 2)

    def test_walls_by(self):
        wall1 = SpatialObject.createBuildingElement_from_vectors("wall1", from_pos=Vector3(-2, 0, 0), to_pos=Vector3(2, 0, 0),height=2.3)
        wall2 = SpatialObject.createBuildingElement_from_vectors("wall2", from_pos=Vector3(2, 0, 0), to_pos=Vector3(2, 0, 3.5),height=2.3)
        wall3 = SpatialObject.createBuildingElement_from_vectors("wall3", from_pos=Vector3(2, 0, 3.5), to_pos=Vector3(-2, 0, 3.5),height=2.3)
        wall4 = SpatialObject.createBuildingElement_from_vectors("wall4", from_pos=Vector3(-2, 0, 3.5), to_pos=Vector3(-2, 0, 0),height=2.3)
        sr = SpatialReasoner()
        sr.load([wall1, wall2, wall3, wall4])
        pipeline = (
            "adjust(sector fixed 1.0; nearby fixed 1.0) | deduce(topology connectivity) | log(base 3D beside)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)

    def test_log_room(self):
        wall1 = SpatialObject.createBuildingElement_from_vectors("wall1", from_pos=Vector3(-2, 0, 0), to_pos=Vector3(2, 0, 0),height=2.3)
        wall2 = SpatialObject.createBuildingElement_from_vectors("wall2", from_pos=Vector3(2, 0, 0), to_pos=Vector3(2, 0, 2.5),height=2.3)
        wall3 = SpatialObject.createBuildingElement_from_vectors("wall3", from_pos=Vector3(2, 0, 2.5), to_pos=Vector3(-2, 0, 2.5),height=2.3)
        wall4 = SpatialObject.createBuildingElement_from_vectors("wall4", from_pos=Vector3(-2, 0, 2.5), to_pos=Vector3(-2, 0, 0), height=2.3)
        floor = SpatialObject.createBuildingElement("floor", from_pos=Vector3(0, -0.2, 1.25),width=4.5, height=0.2, depth=3.0)
        door = SpatialObject.createBuildingElement_from_vectors("door", from_pos=Vector3(0.4, 0, 0), to_pos=Vector3(1.3, 0, 0), height=2.05)
        window = SpatialObject.createBuildingElement_from_vectors("window", from_pos=Vector3(2, 0.7, 1), to_pos=Vector3(2, 0.7, 2.2), height=1.35)
        table = SpatialObject("table", position=Vector3(-0.65, 0, 0.9), width=1.4, height=0.72, depth=0.9)
        book = SpatialObject("book", position=Vector3(-0.75, 0.725, 0.72), width=0.22, height=0.02, depth=0.32)
        book.angle = 0.4
        picture = SpatialObject("picture", position=Vector3(-1.99, 1, 1.4), width=0.9, height=0.6, depth=0.02)
        picture.angle = math.pi / 2.0
        sr = SpatialReasoner()
        sr.adjustment.sectorSchema = SectorSchema.fixed
        sr.adjustment.nearbyFactor = 1.0
        sr.load([wall1, wall2, wall3, wall4, floor, door, window, table, book, picture])
        pipeline = (
            "deduce(topology connectivity) | log(base 3D ontop inside)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)

    def test_as_seen(self):
        subject = SpatialObject("subj", position=Vector3(-0.55, 0, 0.8), width=1.01, height=1.03, depth=1.02)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8), width=1.0, height=1.0, depth=1.0)
        obj.angle = math.pi / 2.0
        observer = SpatialObject.createPerson("ego", position=Vector3(0.3, 0, 3.8), name="ego")
        observer.angle = math.pi + 0.24
        sr = SpatialReasoner()
        sr.load([subject, obj, observer])
        pipeline = (
            "deduce(topology visibility) | log(base 3D left right seenleft seenright)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)

    def test_select(self):
        subject = SpatialObject("subj", position=Vector3(-0.55, 0, 0.8), width=1.01, height=1.03, depth=1.02)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8), width=1.0, height=1.0, depth=1.0)
        obj.angle = math.pi / 2.0
        observer = SpatialObject.createPerson("user", position=Vector3(0.3, 0, 2.3), name="observer")
        observer.angle = math.pi + 0.24
        sr = SpatialReasoner()
        sr.load([subject, obj, observer])
        pipeline = (
            "deduce(topology) | select(ahead ? volume > 0.3) | sort(footprint <) | log(base 3D near infront)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)

    def test_sort(self):
        subject1 = SpatialObject("subj1", position=Vector3(-0.55, 0, -2.1),width=1.01, height=1.03, depth=1.02)
        subject2 = SpatialObject("subj2", position=Vector3(-0.95, 0, 1.5), width=0.4, height=0.5, depth=0.3)
        subject3 = SpatialObject("subj3", position=Vector3(2.2, 0.3, 1.2), width=0.4, height=0.2, depth=0.3)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, -0.8), width=1.0, height=1.0, depth=1.0)
        obj.angle = math.pi / 2.0
        observer = SpatialObject.createPerson("ego", position=Vector3(0.3, 0, 2.3))
        observer.angle = math.pi + 0.24
        sr = SpatialReasoner()
        sr.load([obj, subject1, subject2, subject3, observer])
        
        pipeline = (
                "deduce(topology) "
                "| filter(id == 'ego') "
                "| pick(disjoint) "
                "| sort(disjoint.delta <) "
                "| slice(1) "
                "| log(base 3D disjoint)"
            )
        done = sr.run(pipeline)
        
        self.assertTrue(done)

    def test_calc(self):
        subject = SpatialObject("subj", position=Vector3(-0.55, 0, 0.8), width=1.01, height=0.5, depth=1.02)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8), width=1.0, height=1.0, depth=1.0)
        sr = SpatialReasoner()
        sr.load([subject, obj])
        pipeline = (
            "calc(vol = objects[0].volume; avgh = average(objects.height)) | log(base)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)

    def test_map(self):
        subject = SpatialObject("subj", position=Vector3(-0.55, 0, 0.8), width=1.01, height=1.03, depth=1.02)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8), width=1.0, height=1.0, depth=1.0)
        sr = SpatialReasoner()
        sr.load([subject, obj])
        pipeline = (
            "map(weight = volume * 140.0; type = 'bed') | sort(weight >) | log(base)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)
        self.assertEqual(subject.type, "bed")

    def test_reload(self):
        subject = SpatialObject("subj", position=Vector3(-0.55, 0, 0.8), width=1.01, height=1.03, depth=1.02)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8), width=1.0, height=1.0, depth=1.0)
        sr = SpatialReasoner()
        sr.load([subject, obj])
        pipeline = (
            "map(weight = volume * 140.0; type = 'bed') | sort(weight >) | reload() | log(base)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)
        self.assertEqual(subject.type, "bed")

    def test_duplicate(self):
        subject = SpatialObject("subj", position=Vector3(-0.55, 0, 0.8), width=1.01, height=1.03, depth=1.02)
        obj = SpatialObject("obj", position=Vector3(0.5, 0, 0.8), width=1.0, height=1.0, depth=1.0)
        sr = SpatialReasoner()
        sr.load([subject, obj])
        pipeline = (
            "produce(copy : height = 0.02; label = 'copy') | log(base)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)

    def test_aggregate(self):
        subject = SpatialObject("subj", position=Vector3(-0.75, 0.2, 1.2), width=1.01, height=1.03, depth=1.02, angle=0.3)
        obj = SpatialObject("obj", position=Vector3(0.5, 0.4, 1.4), width=1.0, height=1.0, depth=0.5, angle=-0.4)
        ref = SpatialObject("ref", position=Vector3(0.0, 0, 0.0), width=0.2, height=0.2, depth=0.2)
        sr = SpatialReasoner()
        sr.load([subject, obj, ref])
        
        pipeline = "filter(id != 'ref')"
        done = sr.run(pipeline)
        self.assertTrue(done)
        
        pipeline = "produce(group : label = 'group')"
        done = sr.run(pipeline)
        self.assertTrue(done)

        pipeline = "filter(id != 'ref') | produce(group : label = 'group') | log(base)"
        done = sr.run(pipeline)
        self.assertTrue(done)

    def test_produce_by(self):
        # produce(by: edge)
        subject = SpatialObject("subj", position=Vector3(0.83, 0, -0.2), width=0.4, height=0.8, depth=0.5)
        subject.setYaw(45.0)
        obj = SpatialObject("obj", position=Vector3(0, 0, 0), width=1.0, height=1.0, depth=1.0)
        sr = SpatialReasoner()
        sr.load([subject, obj])
        pipeline = (
            "filter(id != 'ref') | produce(by : label = 'group') | log(base)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)
        

    def test_produce_corner(self):
        wall1 = SpatialObject.createBuildingElement_from_vectors(
            "wall1", from_pos=Vector3(-2, 0, 0), to_pos=Vector3(2, 0, 0),
            height=2.3)
        wall2 = SpatialObject.createBuildingElement_from_vectors(
            "wall2", from_pos=Vector3(2, 0, 0), to_pos=Vector3(2, 0, 3.5),
            height=2.3)
        wall3 = SpatialObject.createBuildingElement_from_vectors(
            "wall3", from_pos=Vector3(2, 0, 3.5), to_pos=Vector3(-2, 0, 3.5),
            height=2.3)
        wall4 = SpatialObject.createBuildingElement_from_vectors(
            "wall4", from_pos=Vector3(-2, 0, 3.5), to_pos=Vector3(-2, 0, 0),
            height=2.3)
        sr = SpatialReasoner()
        sr.load([wall1, wall2, wall3, wall4])
        pipeline = (
            "produce(by : label = 'corner'; h = 0.02) | log(base 3D overlapping)"
        )
        done = sr.run(pipeline)
        self.assertTrue(done)


if __name__ == '__main__':
    unittest.main()
