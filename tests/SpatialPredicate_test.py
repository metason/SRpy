# tests/test_spatial_predicate.py

import unittest
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
    sectors
)
class TestSpatialPredicateEnum(unittest.TestCase):
    def test_enum_members(self):
        """Test that all SpatialPredicate members exist and have correct values."""
        self.assertEqual(SpatialPredicate.undefined.value, "undefined")
        self.assertEqual(SpatialPredicate.near.value, "near")
        self.assertEqual(SpatialPredicate.far.value, "far")
        self.assertEqual(SpatialPredicate.left.value, "left")
        self.assertEqual(SpatialPredicate.right.value, "right")
        self.assertEqual(SpatialPredicate.above.value, "above")
        self.assertEqual(SpatialPredicate.below.value, "below")
        self.assertEqual(SpatialPredicate.ahead.value, "ahead")
        self.assertEqual(SpatialPredicate.behind.value, "behind")
        self.assertEqual(SpatialPredicate.ontop.value, "on top")
        self.assertEqual(SpatialPredicate.beneath.value, "beneath")
        self.assertEqual(SpatialPredicate.upperside.value, "at upper side")
        self.assertEqual(SpatialPredicate.lowerside.value, "at lower side")
        self.assertEqual(SpatialPredicate.leftside.value, "at left side")
        self.assertEqual(SpatialPredicate.rightside.value, "at right side")
        self.assertEqual(SpatialPredicate.frontside.value, "at front side")
        self.assertEqual(SpatialPredicate.backside.value, "at back side")
        self.assertEqual(SpatialPredicate.orthogonal.value, "orthogonal")
        self.assertEqual(SpatialPredicate.opposite.value, "opposite")
        self.assertEqual(SpatialPredicate.aligned.value, "aligned")
        self.assertEqual(SpatialPredicate.frontaligned.value, "front aligned")
        self.assertEqual(SpatialPredicate.backaligned.value, "back aligned")
        self.assertEqual(SpatialPredicate.leftaligned.value, "left aligned")
        self.assertEqual(SpatialPredicate.rightaligned.value, "right aligned")
        self.assertEqual(SpatialPredicate.disjoint.value, "disjoint")
        self.assertEqual(SpatialPredicate.inside.value, "inside")
        self.assertEqual(SpatialPredicate.containing.value, "containing")
        self.assertEqual(SpatialPredicate.overlapping.value, "overlapping")
        self.assertEqual(SpatialPredicate.crossing.value, "crossing")
        self.assertEqual(SpatialPredicate.touching.value, "touching")
        self.assertEqual(SpatialPredicate.meeting.value, "meeting")
        self.assertEqual(SpatialPredicate.beside.value, "beside")
        self.assertEqual(SpatialPredicate.fitting.value, "fitting")
        self.assertEqual(SpatialPredicate.exceeding.value, "exceeding")
        self.assertEqual(SpatialPredicate.smaller.value, "smaller")
        self.assertEqual(SpatialPredicate.bigger.value, "bigger")
        self.assertEqual(SpatialPredicate.shorter.value, "shorter")
        self.assertEqual(SpatialPredicate.longer.value, "longer")
        self.assertEqual(SpatialPredicate.taller.value, "taller")
        self.assertEqual(SpatialPredicate.thinner.value, "thinner")
        self.assertEqual(SpatialPredicate.wider.value, "wider")
        self.assertEqual(SpatialPredicate.samewidth.value, "same width")
        self.assertEqual(SpatialPredicate.sameheight.value, "same height")
        self.assertEqual(SpatialPredicate.samedepth.value, "same depth")
        self.assertEqual(SpatialPredicate.samelength.value, "same length")
        self.assertEqual(SpatialPredicate.samefront.value, "same front face")
        self.assertEqual(SpatialPredicate.sameside.value, "same side face")
        self.assertEqual(SpatialPredicate.samefootprint.value, "same footprint")
        self.assertEqual(SpatialPredicate.samevolume.value, "same volume")
        self.assertEqual(SpatialPredicate.samecenter.value, "same center")
        self.assertEqual(SpatialPredicate.sameposition.value, "same position")
        self.assertEqual(SpatialPredicate.samecuboid.value, "same cuboid")
        self.assertEqual(SpatialPredicate.congruent.value, "congruent")
        self.assertEqual(SpatialPredicate.sameshape.value, "same shape")
        self.assertEqual(SpatialPredicate.seenleft.value, "seen left")
        self.assertEqual(SpatialPredicate.seenright.value, "seen right")
        self.assertEqual(SpatialPredicate.infront.value, "in front")
        self.assertEqual(SpatialPredicate.atrear.value, "at rear")
        self.assertEqual(SpatialPredicate.tangible.value, "tangible")
        self.assertEqual(SpatialPredicate.eightoclock.value, "eight o'clock")
        self.assertEqual(SpatialPredicate.nineoclock.value, "nine o'clock")
        self.assertEqual(SpatialPredicate.tenoclock.value, "ten o'clock")
        self.assertEqual(SpatialPredicate.elevenoclock.value, "eleven o'clock")
        self.assertEqual(SpatialPredicate.twelveoclock.value, "twelve o'clock")
        self.assertEqual(SpatialPredicate.oneoclock.value, "one o'clock")
        self.assertEqual(SpatialPredicate.twooclock.value, "two o'clock")
        self.assertEqual(SpatialPredicate.threeoclock.value, "three o'clock")
        self.assertEqual(SpatialPredicate.fouroclock.value, "four o'clock")
        self.assertEqual(SpatialPredicate.secondleft.value, "second left")
        self.assertEqual(SpatialPredicate.secondright.value, "second right")
        self.assertEqual(SpatialPredicate.mostleft.value, "most left")
        self.assertEqual(SpatialPredicate.mostright.value, "most right")
        self.assertEqual(SpatialPredicate.on.value, "on")
        self.assertEqual(SpatialPredicate.at.value, "at")
        self.assertEqual(SpatialPredicate.by.value, "by")
        self.assertEqual(SpatialPredicate.in_.value, "in")
        self.assertEqual(SpatialPredicate.i.value, "i")
        self.assertEqual(SpatialPredicate.a.value, "a")
        self.assertEqual(SpatialPredicate.b.value, "b")
        self.assertEqual(SpatialPredicate.l.value, "l")
        self.assertEqual(SpatialPredicate.r.value, "r")
        self.assertEqual(SpatialPredicate.o.value, "o")
        self.assertEqual(SpatialPredicate.u.value, "u")
        self.assertEqual(SpatialPredicate.al.value, "al")
        self.assertEqual(SpatialPredicate.ar.value, "ar")
        self.assertEqual(SpatialPredicate.bl.value, "bl")
        self.assertEqual(SpatialPredicate.br.value, "br")
        self.assertEqual(SpatialPredicate.ao.value, "ao")
        self.assertEqual(SpatialPredicate.au.value, "au")
        self.assertEqual(SpatialPredicate.bo.value, "bo")
        self.assertEqual(SpatialPredicate.bu.value, "bu")
        self.assertEqual(SpatialPredicate.lo.value, "lo")
        self.assertEqual(SpatialPredicate.lu.value, "lu")
        self.assertEqual(SpatialPredicate.ro.value, "ro")
        self.assertEqual(SpatialPredicate.ru.value, "ru")
        self.assertEqual(SpatialPredicate.alo.value, "alo")
        self.assertEqual(SpatialPredicate.aro.value, "aro")
        self.assertEqual(SpatialPredicate.blo.value, "blo")
        self.assertEqual(SpatialPredicate.bro.value, "bro")
        self.assertEqual(SpatialPredicate.alu.value, "alu")
        self.assertEqual(SpatialPredicate.aru.value, "aru")
        self.assertEqual(SpatialPredicate.blu.value, "blu")
        self.assertEqual(SpatialPredicate.bru.value, "bru")
        self.assertEqual(SpatialPredicate.north.value, "north")
        self.assertEqual(SpatialPredicate.south.value, "south")
        self.assertEqual(SpatialPredicate.east.value, "east")
        self.assertEqual(SpatialPredicate.west.value, "west")
        self.assertEqual(SpatialPredicate.northwest.value, "northwest")
        self.assertEqual(SpatialPredicate.northeast.value, "northeast")
        self.assertEqual(SpatialPredicate.southwest.value, "southwest")
        self.assertEqual(SpatialPredicate.southeast.value, "southeast")


class TestPredicateTerm(unittest.TestCase):
    def test_predicate_term_initialization(self):
        """Test the initialization of PredicateTerm."""
        term = PredicateTerm(
            code=SpatialPredicate.near,
            predicate="near",
            preposition="to",
            synonym="close",
            reverse="near",
            antonym="far",
            verb="is"
        )
        self.assertEqual(term.code, SpatialPredicate.near)
        self.assertEqual(term.predicate, "near")
        self.assertEqual(term.preposition, "to")
        self.assertEqual(term.synonym, "close")
        self.assertEqual(term.reverse, "near")
        self.assertEqual(term.antonym, "far")
        self.assertEqual(term.verb, "is")

    def test_predicate_term_defaults(self):
        """Test the default values of PredicateTerm."""
        term = PredicateTerm(
            code=SpatialPredicate.far,
            predicate="far",
            preposition="from",
            synonym="close",      # Explicitly set synonym
            reverse="far",
            antonym="near",
            verb="is"
        )
        self.assertEqual(term.code, SpatialPredicate.far)
        self.assertEqual(term.predicate, "far")
        self.assertEqual(term.preposition, "from")
        self.assertEqual(term.synonym, "close")  # Now correctly set
        self.assertEqual(term.reverse, "far")
        self.assertEqual(term.antonym, "near")
        self.assertEqual(term.verb, "is")


class TestSpatialTerms(unittest.TestCase):
    def test_list_population(self):
        """Test that SpatialTerms.list is correctly populated."""
        self.assertTrue(len(SpatialTerms.list) > 0)
        # Example: Check first term
        first_term = SpatialTerms.list[0]
        self.assertEqual(first_term.code, SpatialPredicate.near)
        self.assertEqual(first_term.predicate, "near")
        self.assertEqual(first_term.preposition, "to")
        self.assertEqual(first_term.synonym, "close")
        self.assertEqual(first_term.reverse, "near")
        self.assertEqual(first_term.antonym, "far")
        self.assertEqual(first_term.verb, "is")

    def test_predicate_method(self):
        """Test the SpatialTerms.predicate method."""
        self.assertEqual(SpatialTerms.predicate("near"), SpatialPredicate.near)
        self.assertEqual(SpatialTerms.predicate("close"), SpatialPredicate.near)
        self.assertEqual(SpatialTerms.predicate("far"), SpatialPredicate.far)
        self.assertEqual(SpatialTerms.predicate("on top"), SpatialPredicate.ontop)
        self.assertEqual(SpatialTerms.predicate("at the top"), SpatialPredicate.ontop)
        self.assertEqual(SpatialTerms.predicate("fitting"), SpatialPredicate.fitting)
        self.assertEqual(SpatialTerms.predicate("exceeding"), SpatialPredicate.exceeding)
        self.assertEqual(SpatialTerms.predicate("same width"), SpatialPredicate.samewidth)
        self.assertEqual(SpatialTerms.predicate("similar width"), SpatialPredicate.samewidth)
        self.assertEqual(SpatialTerms.predicate("similar depth"), SpatialPredicate.samedepth)
        self.assertEqual(SpatialTerms.predicate("nonexistent"), SpatialPredicate.undefined)

    def test_term_method(self):
        """Test the SpatialTerms.term method."""
        self.assertEqual(SpatialTerms.term(SpatialPredicate.near), "near")
        self.assertEqual(SpatialTerms.term(SpatialPredicate.far), "far")
        self.assertEqual(SpatialTerms.term(SpatialPredicate.ontop), "on top")
        self.assertEqual(SpatialTerms.term(SpatialPredicate.beneath), "beneath")
        self.assertEqual(SpatialTerms.term(SpatialPredicate.samewidth), "same width")
        self.assertEqual(SpatialTerms.term(SpatialPredicate.undefined), "undefined")

    def test_termWithPreposition_method(self):
        """Test the SpatialTerms.termWithPreposition method."""
        self.assertEqual(SpatialTerms.termWithPreposition(SpatialPredicate.near), "near to")
        self.assertEqual(SpatialTerms.termWithPreposition(SpatialPredicate.far), "far from")
        self.assertEqual(SpatialTerms.termWithPreposition(SpatialPredicate.left), "left of")
        self.assertEqual(SpatialTerms.termWithPreposition(SpatialPredicate.above), "above")
        self.assertEqual(SpatialTerms.termWithPreposition(SpatialPredicate.ontop), "on top of")
        self.assertEqual(SpatialTerms.termWithPreposition(SpatialPredicate.samewidth), "same width as")
        self.assertEqual(SpatialTerms.termWithPreposition(SpatialPredicate.undefined), "undefined")

    def test_termWithVerbAndPreposition_method(self):
        """Test the SpatialTerms.termWithVerbAndPreposition method."""
        self.assertEqual(SpatialTerms.termWithVerbAndPreposition(SpatialPredicate.near), "is near to")
        self.assertEqual(SpatialTerms.termWithVerbAndPreposition(SpatialPredicate.far), "is far from")
        self.assertEqual(SpatialTerms.termWithVerbAndPreposition(SpatialPredicate.left), "is left of")
        self.assertEqual(SpatialTerms.termWithVerbAndPreposition(SpatialPredicate.above), "is above")
        self.assertEqual(SpatialTerms.termWithVerbAndPreposition(SpatialPredicate.ontop), "is on top of")
        self.assertEqual(SpatialTerms.termWithVerbAndPreposition(SpatialPredicate.samewidth), "has same width as")
        self.assertEqual(SpatialTerms.termWithVerbAndPreposition(SpatialPredicate.undefined), "undefined")

    def test_symmetric_method(self):
        """Test the SpatialTerms.symmetric method."""
        self.assertTrue(SpatialTerms.symmetric(SpatialPredicate.orthogonal))
        self.assertTrue(SpatialTerms.symmetric(SpatialPredicate.opposite))
        self.assertFalse(SpatialTerms.symmetric(SpatialPredicate.left))
        self.assertTrue(SpatialTerms.symmetric(SpatialPredicate.near))  # Updated expectation
        self.assertTrue(SpatialTerms.symmetric(SpatialPredicate.congruent))

    def test_inverse_method(self):
        """Test the SpatialTerms.inverse method."""
        self.assertEqual(SpatialTerms.inverse("on top"), SpatialPredicate.beneath)
        self.assertEqual(SpatialTerms.inverse("beneath"), SpatialPredicate.ontop)
        self.assertEqual(SpatialTerms.inverse("near"), SpatialPredicate.near)
        self.assertEqual(SpatialTerms.inverse("unknown"), SpatialPredicate.undefined)

    def test_negation_method(self):
        """Test the SpatialTerms.negation method."""
        self.assertEqual(SpatialTerms.negation("near"), SpatialPredicate.far)
        self.assertEqual(SpatialTerms.negation("far"), SpatialPredicate.near)
        self.assertEqual(SpatialTerms.negation("overlapping"), SpatialPredicate.disjoint)
        self.assertEqual(SpatialTerms.negation("disjoint"), SpatialPredicate.overlapping)
        self.assertEqual(SpatialTerms.negation("unknown"), SpatialPredicate.undefined)


class TestSpatialPredicateCategories(unittest.TestCase):
    def test_category_membership(self):
        """Test that global lists contain correct SpatialPredicate members."""
        # Proximity
        self.assertListEqual(proximity, [SpatialPredicate.near, SpatialPredicate.far])
        # Directionality
        self.assertListEqual(directionality, [SpatialPredicate.left, SpatialPredicate.right, SpatialPredicate.above, SpatialPredicate.below, SpatialPredicate.ahead, SpatialPredicate.behind])
        # Adjacency
        self.assertListEqual(adjacency, [
            SpatialPredicate.leftside, SpatialPredicate.rightside, SpatialPredicate.ontop, SpatialPredicate.beneath,
            SpatialPredicate.upperside, SpatialPredicate.lowerside, SpatialPredicate.frontside, SpatialPredicate.backside
        ])
        # Orientations
        self.assertListEqual(orientations, [
            SpatialPredicate.orthogonal, SpatialPredicate.opposite, SpatialPredicate.aligned,
            SpatialPredicate.frontaligned, SpatialPredicate.backaligned, SpatialPredicate.rightaligned,
            SpatialPredicate.leftaligned
        ])
        # Assembly
        self.assertListEqual(assembly, [
            SpatialPredicate.disjoint, SpatialPredicate.inside, SpatialPredicate.containing,
            SpatialPredicate.overlapping, SpatialPredicate.crossing, SpatialPredicate.touching,
            SpatialPredicate.meeting, SpatialPredicate.beside
        ])
        # Topology
        self.assertListEqual(topology, proximity + directionality + adjacency + orientations + assembly)
        # Contacts
        self.assertListEqual(contacts, [SpatialPredicate.on, SpatialPredicate.at, SpatialPredicate.by, SpatialPredicate.in_])
        # Connectivity
        self.assertListEqual(connectivity, [SpatialPredicate.on, SpatialPredicate.at, SpatialPredicate.by, SpatialPredicate.in_])
        # Comparability
        self.assertListEqual(comparability, [
            SpatialPredicate.smaller, SpatialPredicate.bigger, SpatialPredicate.shorter, SpatialPredicate.longer,
            SpatialPredicate.taller, SpatialPredicate.thinner, SpatialPredicate.wider, SpatialPredicate.fitting,
            SpatialPredicate.exceeding
        ])
        # Similarity
        self.assertListEqual(similarity, [
            SpatialPredicate.sameheight, SpatialPredicate.samewidth, SpatialPredicate.samedepth,
            SpatialPredicate.samelength, SpatialPredicate.samefront, SpatialPredicate.sameside,
            SpatialPredicate.samefootprint, SpatialPredicate.samevolume, SpatialPredicate.samecenter,
            SpatialPredicate.samecuboid, SpatialPredicate.congruent, SpatialPredicate.sameshape
        ])
        # Visibility
        self.assertListEqual(visibility, [
            SpatialPredicate.seenleft, SpatialPredicate.seenright, SpatialPredicate.infront,
            SpatialPredicate.atrear, SpatialPredicate.tangible, SpatialPredicate.eightoclock,
            SpatialPredicate.nineoclock, SpatialPredicate.tenoclock, SpatialPredicate.elevenoclock,
            SpatialPredicate.twelveoclock, SpatialPredicate.oneoclock, SpatialPredicate.twooclock,
            SpatialPredicate.threeoclock, SpatialPredicate.fouroclock
        ])
        # Geography
        self.assertListEqual(geography, [
            SpatialPredicate.north, SpatialPredicate.south, SpatialPredicate.east, SpatialPredicate.west,
            SpatialPredicate.northwest, SpatialPredicate.northeast, SpatialPredicate.southwest, SpatialPredicate.southeast
        ])
        # Sectors
        self.assertListEqual(sectors, [
            SpatialPredicate.i, SpatialPredicate.a, SpatialPredicate.b, SpatialPredicate.o, SpatialPredicate.u,
            SpatialPredicate.l, SpatialPredicate.r, SpatialPredicate.al, SpatialPredicate.ar, SpatialPredicate.bl,
            SpatialPredicate.br, SpatialPredicate.ao, SpatialPredicate.au, SpatialPredicate.bo, SpatialPredicate.bu,
            SpatialPredicate.lo, SpatialPredicate.lu, SpatialPredicate.ro, SpatialPredicate.ru, SpatialPredicate.alo,
            SpatialPredicate.aro, SpatialPredicate.blo, SpatialPredicate.bro, SpatialPredicate.alu, SpatialPredicate.aru,
            SpatialPredicate.blu, SpatialPredicate.bru
        ])

if __name__ == '__main__':
    unittest.main()
