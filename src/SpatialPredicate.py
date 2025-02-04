# src/spatial_predicate.py

from enum import Enum
from dataclasses import dataclass
from typing import List


class SpatialPredicate(Enum):
    undefined = "undefined"
    # TOPOLOGY
    # proximity: near by
    near = "near"                # A is near to B, is close
    far = "far"                  # not near
    # directionality: in relation to position and orientation of object comparing center
    left = "left"
    right = "right"
    above = "above"
    below = "below"
    ahead = "ahead"
    behind = "behind"
    # adjacency: near by and at one side
    ontop = "on top"             # A is on top of B, very close contact
    beneath = "beneath"          # A is beneath of B, very close contact
    upperside = "at upper side"  # A is at upper side of B
    lowerside = "at lower side"  # A is at lower side of B
    leftside = "at left side"    # A is left side from B
    rightside = "at right side"  # A is right side from B
    frontside = "at front side"  # A is at front side of B, ahead
    backside = "at back side"    # A is at back side of B, behind
    # orientations
    orthogonal = "orthogonal"    # A is orthogonal to B, perpendicular to
    opposite = "opposite"        # opposite alignment
    aligned = "aligned"          # equally aligned orientation, parallel with
    frontaligned = "front aligned"  # same orientation and in same front plane
    backaligned = "back aligned"    # same orientation and in same back plane
    leftaligned = "left aligned"    # same orientation and in same left plane
    rightaligned = "right aligned"  # same orientation and in same right plane
    # assembly
    disjoint = "disjoint"            # no space in common
    inside = "inside"                # A is inside B
    containing = "containing"        # A is containing/contains B
    overlapping = "overlapping"      # (partially) overlapping, intersecting
    crossing = "crossing"            # intersecting by going through object
    # dividing = "dividing"          # crossing and dividing into parts (commented out in Swift)
    touching = "touching"            # touching edge-to-edge or edge-to-side = at edge
    meeting = "meeting"              # meeting side-by-side
    beside = "beside"                # near but not above or below
    fitting = "fitting"              # is fitting into
    exceeding = "exceeding"          # not fitting into
    # COMPARABILITY
    # comparisons
    smaller = "smaller"              # volume
    bigger = "bigger"                # syn: larger
    shorter = "shorter"              # length, height
    longer = "longer"                # length
    taller = "taller"                # height
    thinner = "thinner"              # width, depth --> footprint, syn: narrower
    wider = "wider"                  # syn: thicker
    # SIMILARITY
    # fuzzy comparison considering max deviation
    samewidth = "same width"
    sameheight = "same height"
    samedepth = "same depth"
    samelength = "same length"       # same length of main direction
    samefront = "same front face"
    sameside = "same side face"
    samefootprint = "same footprint"
    samevolume = "same volume"
    samecenter = "same center"
    sameposition = "same position"  # on base
    samecuboid = "same cuboid"
    congruent = "congruent"          # A is congruent to B, similar w,h,d, center and orientation, identical
    sameshape = "same shape"
    samesurface = "samesurface"
    # samecause is commented out
    # VISIBILITY
    # perspectives: seen from user / observer
    seenleft = "seen left"           # A is seen left of B by P
    seenright = "seen right"
    infront = "in front"             # (partially) covering
    atrear = "at rear"               # at back
    tangible = "tangible"             # within arm reach by user
    eightoclock = "eight o'clock"   # at 8 o'clock
    nineoclock = "nine o'clock"
    tenoclock = "ten o'clock"
    elevenoclock = "eleven o'clock"
    twelveoclock = "twelve o'clock"
    oneoclock = "one o'clock"
    twooclock = "two o'clock"
    threeoclock = "three o'clock"
    fouroclock = "four o'clock"
    # multistage relations
    secondleft = "second left"
    secondright = "second right"
    mostleft = "most left"
    mostright = "most right"
    # CONNECTIVITY
    # contacts
    on = "on"                        # on top of, unilateral
    at = "at"                        # attached and aligned with, unilateral
    by = "by"                        # connected, bilateral
    in_ = "in"                       # within, unilateral (note: 'in' is a reserved keyword in Python)
    # SECTORIALITY
    # center within bbox sector
    i = "i"
    a = "a"
    b = "b"
    l = "l"
    r = "r"
    o = "o"
    u = "u"
    al = "al"
    ar = "ar"
    bl = "bl"
    br = "br"
    ao = "ao"
    au = "au"
    bo = "bo"
    bu = "bu"
    lo = "lo"
    lu = "lu"
    ro = "ro"
    ru = "ru"
    alo = "alo"
    aro = "aro"
    blo = "blo"
    bro = "bro"
    alu = "alu"
    aru = "aru"
    blu = "blu"
    bru = "bru"
    # GEOGRAPHY
    # geographic direction
    north = "north"
    south = "south"
    east = "east"
    west = "west"
    northwest = "northwest"
    northeast = "northeast"
    southwest = "southwest"
    southeast = "southeast"

    @staticmethod
    def named(name: str) -> 'SpatialPredicate':
        for member in SpatialPredicate:
            if member.value == name:
                return member
        return SpatialPredicate.undefined


@dataclass
class PredicateTerm:
    code: SpatialPredicate
    predicate: str  # subject - predicate - object
    preposition: str
    synonym: str = ""
    reverse: str = ""  # object - predicate - subject
    antonym: str = ""  # if not predicate then antonym
    verb: str = "is"


class SpatialTerms:
    # List of PredicateTerm instances
    list: List[PredicateTerm] = [
        # TOPOLOGY
        # proximity in WCS and OCS
        PredicateTerm(code=SpatialPredicate.near, predicate="near", preposition="to", synonym="close", reverse="near", antonym="far", verb="is"),
        PredicateTerm(code=SpatialPredicate.far, predicate="far", preposition="from", synonym="close", reverse="far", antonym="near", verb="is"),
        # directionality in OCS
        PredicateTerm(code=SpatialPredicate.left, predicate="left", preposition="of", synonym="to the left"),
        PredicateTerm(code=SpatialPredicate.right, predicate="right", preposition="of", synonym="to the right"),
        PredicateTerm(code=SpatialPredicate.ahead, predicate="ahead", preposition="of", synonym="before"),
        PredicateTerm(code=SpatialPredicate.behind, predicate="behind", preposition="", synonym="after"),
        PredicateTerm(code=SpatialPredicate.above, predicate="above", preposition="", synonym="over", reverse="below"),
        PredicateTerm(code=SpatialPredicate.below, predicate="below", preposition="", synonym="under", reverse="above"),
        
        PredicateTerm(code=SpatialPredicate.l, predicate="left", preposition="of", synonym="to the left"),
        PredicateTerm(code=SpatialPredicate.r, predicate="right", preposition="of", synonym="to the right"),
        PredicateTerm(code=SpatialPredicate.a, predicate="ahead", preposition="of", synonym="before"),
        PredicateTerm(code=SpatialPredicate.b, predicate="behind", preposition="", synonym="after"),
        PredicateTerm(code=SpatialPredicate.o, predicate="above", preposition="", synonym="over", reverse="below"),
        PredicateTerm(code=SpatialPredicate.u, predicate="below", preposition="", synonym="under", reverse="above"),
        # adjacency in OCS
        PredicateTerm(code=SpatialPredicate.ontop, predicate="on top", preposition="of", synonym="at the top", reverse="beneath"),
        PredicateTerm(code=SpatialPredicate.beneath, predicate="beneath", preposition="", synonym="underneath", reverse="on top"),
        PredicateTerm(code=SpatialPredicate.upperside, predicate="at upper side", preposition="of", reverse="at lower side"),
        PredicateTerm(code=SpatialPredicate.lowerside, predicate="at lower side", preposition="of", reverse="at upper side"),
        PredicateTerm(code=SpatialPredicate.leftside, predicate="at left side", preposition="of", synonym="at left-hand side"),
        PredicateTerm(code=SpatialPredicate.rightside, predicate="at right side", preposition="of", synonym="at right-hand side"),
        PredicateTerm(code=SpatialPredicate.frontside, predicate="at front side", preposition="of", synonym="at forefront"),
        PredicateTerm(code=SpatialPredicate.backside, predicate="at back side", preposition="of", synonym="at rear side"),
        # orientations
        PredicateTerm(code=SpatialPredicate.aligned, predicate="aligned", preposition="with", synonym="parallel", reverse="aligned"),
        PredicateTerm(code=SpatialPredicate.orthogonal, predicate="orthogonal", preposition="to", synonym="perpendicular", reverse="orthogonal"),
        PredicateTerm(code=SpatialPredicate.opposite, predicate="opposite", preposition="", synonym="vis-a-vis", reverse="opposite"),
        # topology
        PredicateTerm(code=SpatialPredicate.inside, predicate="inside", preposition="", synonym="within", reverse="containing"),
        PredicateTerm(code=SpatialPredicate.containing, predicate="containing", preposition="", synonym="contains", reverse="inside"),
        PredicateTerm(code=SpatialPredicate.crossing, predicate="crossing", preposition=""),
        PredicateTerm(code=SpatialPredicate.overlapping, predicate="overlapping", preposition="", synonym="intersecting", reverse="overlapping", antonym="disjoint"),
        PredicateTerm(code=SpatialPredicate.disjoint, predicate="disjoint", preposition="to", reverse="disjoint", antonym="overlapping"),
        PredicateTerm(code=SpatialPredicate.touching, predicate="touching", preposition="with", reverse="touching"),
        PredicateTerm(code=SpatialPredicate.frontaligned, predicate="front aligned", preposition="with", reverse="front aligned"),
        PredicateTerm(code=SpatialPredicate.meeting, predicate="meeting", preposition="", reverse="meeting"),
        PredicateTerm(code=SpatialPredicate.beside, predicate="beside", preposition="", reverse="beside"),
        PredicateTerm(code=SpatialPredicate.fitting, predicate="fitting", preposition="into", reverse="exceeding"),
        PredicateTerm(code=SpatialPredicate.exceeding, predicate="exceeding", preposition="into", reverse="fitting"),
        # connectivity
        PredicateTerm(code=SpatialPredicate.on, predicate="on", preposition="", reverse="beneath"),
        PredicateTerm(code=SpatialPredicate.at, predicate="at", preposition="", reverse="meeting"),
        PredicateTerm(code=SpatialPredicate.by, predicate="by", preposition="", reverse="by"),
        PredicateTerm(code=SpatialPredicate.in_, predicate="in", preposition="", reverse="containing"),
        # similarity
        PredicateTerm(code=SpatialPredicate.samewidth, predicate="same width", preposition="as", synonym="similar width", reverse="same width", verb="has"),
        PredicateTerm(code=SpatialPredicate.sameheight, predicate="same height", preposition="as", synonym="similar height", reverse="same height", verb="has"),
        PredicateTerm(code=SpatialPredicate.samedepth, predicate="same depth", preposition="as", synonym="similar depth", reverse="same depth", verb="has"),
        PredicateTerm(code=SpatialPredicate.samelength, predicate="same length", preposition="as", synonym="similar length", reverse="same length", verb="has"),
        PredicateTerm(code=SpatialPredicate.samefootprint, predicate="same footprint", preposition="as", synonym="similar base area", reverse="same footprint", verb="has"),
        PredicateTerm(code=SpatialPredicate.samefront, predicate="same front face", preposition="as", synonym="similar front face", reverse="same front face", verb="has"),
        PredicateTerm(code=SpatialPredicate.sameside, predicate="same side face", preposition="as", synonym="similar side face", reverse="same side face", verb="has"),
        PredicateTerm(code=SpatialPredicate.samevolume, predicate="same volume", preposition="as", synonym="similar volume", reverse="same volume", verb="has"),
        PredicateTerm(code=SpatialPredicate.samecuboid, predicate="same cuboid", preposition="as", synonym="similar cuboid", reverse="same cuboid", verb="has"),
        PredicateTerm(code=SpatialPredicate.samecenter, predicate="same center", preposition="as", synonym="similar center", reverse="same center", verb="has"),
        PredicateTerm(code=SpatialPredicate.sameshape, predicate="same shape", preposition="as", synonym="similar shape", reverse="same shape", verb="has"),
        PredicateTerm(code=SpatialPredicate.congruent, predicate="congruent", preposition="as", reverse="congruent"),
        # comparisons
        PredicateTerm(code=SpatialPredicate.smaller, predicate="smaller", preposition="than", synonym="tinier", reverse="bigger"),
        PredicateTerm(code=SpatialPredicate.bigger, predicate="bigger", preposition="than", synonym="larger", reverse="smaller"),
        PredicateTerm(code=SpatialPredicate.shorter, predicate="shorter", preposition="than", reverse="longer"),
        PredicateTerm(code=SpatialPredicate.longer, predicate="longer", preposition="than", reverse="shorter"),
        PredicateTerm(code=SpatialPredicate.taller, predicate="taller", preposition="than", reverse="shorter"),
        PredicateTerm(code=SpatialPredicate.thinner, predicate="thinner", preposition="than", synonym="narrower", reverse="wider"),
        PredicateTerm(code=SpatialPredicate.wider, predicate="wider", preposition="than", synonym="thicker", reverse="thinner"),
    ]

    @staticmethod
    def predicate(name: str) -> SpatialPredicate:
        pred = SpatialPredicate.named(name)
        if pred != SpatialPredicate.undefined:
            return pred
        for term in SpatialTerms.list:
            if term.predicate == name:
                return term.code
            if term.synonym == name:
                return term.code
        return SpatialPredicate.undefined

    @staticmethod
    def term(code: SpatialPredicate) -> str:
        for term in SpatialTerms.list:
            if term.code == code:
                return term.predicate
        if code != SpatialPredicate.undefined:
            return code.value
        return "undefined"

    @staticmethod
    def termWithPreposition(code: SpatialPredicate) -> str:
        for term in SpatialTerms.list:
            if term.code == code:
                if term.preposition:
                    return f"{term.predicate} {term.preposition}"
                return term.predicate
        return "undefined"

    @staticmethod
    def termWithVerbAndPreposition(code: SpatialPredicate) -> str:
        for term in SpatialTerms.list:
            if term.code == code:
                if term.preposition:
                    return f"{term.verb} {term.predicate} {term.preposition}"
                return f"{term.verb} {term.predicate}"
        return "undefined"

    @staticmethod
    def symmetric(code: SpatialPredicate) -> bool:
        for term in SpatialTerms.list:
            if term.code == code:
                return term.predicate == term.reverse
        return False

    @staticmethod
    def inverse(predicate: str) -> SpatialPredicate:
        for term in SpatialTerms.list:
            if term.predicate == predicate and term.reverse:
                # Handle 'in' differently due to Python keyword
                if term.reverse == "in":
                    return SpatialPredicate.in_
                try:
                    return SpatialPredicate(term.reverse)
                except ValueError:
                    return SpatialPredicate.undefined
        return SpatialPredicate.undefined

    @staticmethod
    def negation(predicate: str) -> SpatialPredicate:
        for term in SpatialTerms.list:
            if term.predicate == predicate and term.antonym:
                try:
                    return SpatialPredicate(term.antonym)
                except ValueError:
                    return SpatialPredicate.undefined
        return SpatialPredicate.undefined


# Global lists combining SpatialPredicate enums
proximity: List[SpatialPredicate] = [SpatialPredicate.near, SpatialPredicate.far]
directionality: List[SpatialPredicate] = [SpatialPredicate.left, SpatialPredicate.right, SpatialPredicate.above, SpatialPredicate.below, SpatialPredicate.ahead, SpatialPredicate.behind]
adjacency: List[SpatialPredicate] = [
    SpatialPredicate.leftside, SpatialPredicate.rightside, SpatialPredicate.ontop, SpatialPredicate.beneath,
    SpatialPredicate.upperside, SpatialPredicate.lowerside, SpatialPredicate.frontside, SpatialPredicate.backside
]
orientations: List[SpatialPredicate] = [
    SpatialPredicate.orthogonal, SpatialPredicate.opposite, SpatialPredicate.aligned,
    SpatialPredicate.frontaligned, SpatialPredicate.backaligned, SpatialPredicate.rightaligned,
    SpatialPredicate.leftaligned
]
assembly: List[SpatialPredicate] = [
    SpatialPredicate.disjoint, SpatialPredicate.inside, SpatialPredicate.containing,
    SpatialPredicate.overlapping, SpatialPredicate.crossing, SpatialPredicate.touching,
    SpatialPredicate.meeting, SpatialPredicate.beside
]
topology: List[SpatialPredicate] = proximity + directionality + adjacency + orientations + assembly
contacts: List[SpatialPredicate] = [SpatialPredicate.on, SpatialPredicate.at, SpatialPredicate.by, SpatialPredicate.in_]
connectivity: List[SpatialPredicate] = [SpatialPredicate.on, SpatialPredicate.at, SpatialPredicate.by, SpatialPredicate.in_]
comparability: List[SpatialPredicate] = [
    SpatialPredicate.smaller, SpatialPredicate.bigger, SpatialPredicate.shorter, SpatialPredicate.longer,
    SpatialPredicate.taller, SpatialPredicate.thinner, SpatialPredicate.wider, SpatialPredicate.fitting,
    SpatialPredicate.exceeding
]
similarity: List[SpatialPredicate] = [
    SpatialPredicate.sameheight, SpatialPredicate.samewidth, SpatialPredicate.samedepth,
    SpatialPredicate.samelength, SpatialPredicate.samefront, SpatialPredicate.sameside,
    SpatialPredicate.samefootprint, SpatialPredicate.samevolume, SpatialPredicate.samecenter,
    SpatialPredicate.samecuboid, SpatialPredicate.congruent, SpatialPredicate.sameshape
]
visibility: List[SpatialPredicate] = [
    SpatialPredicate.seenleft, SpatialPredicate.seenright, SpatialPredicate.infront,
    SpatialPredicate.atrear, SpatialPredicate.tangible, SpatialPredicate.eightoclock,
    SpatialPredicate.nineoclock, SpatialPredicate.tenoclock, SpatialPredicate.elevenoclock,
    SpatialPredicate.twelveoclock, SpatialPredicate.oneoclock, SpatialPredicate.twooclock,
    SpatialPredicate.threeoclock, SpatialPredicate.fouroclock
]
geography: List[SpatialPredicate] = [
    SpatialPredicate.north, SpatialPredicate.south, SpatialPredicate.east, SpatialPredicate.west,
    SpatialPredicate.northwest, SpatialPredicate.northeast, SpatialPredicate.southwest, SpatialPredicate.southeast
]
sectors: List[SpatialPredicate] = [
    SpatialPredicate.i, SpatialPredicate.a, SpatialPredicate.b, SpatialPredicate.o, SpatialPredicate.u,
    SpatialPredicate.l, SpatialPredicate.r, SpatialPredicate.al, SpatialPredicate.ar, SpatialPredicate.bl,
    SpatialPredicate.br, SpatialPredicate.ao, SpatialPredicate.au, SpatialPredicate.bo, SpatialPredicate.bu,
    SpatialPredicate.lo, SpatialPredicate.lu, SpatialPredicate.ro, SpatialPredicate.ru, SpatialPredicate.alo,
    SpatialPredicate.aro, SpatialPredicate.blo, SpatialPredicate.bro, SpatialPredicate.alu, SpatialPredicate.aru,
    SpatialPredicate.blu, SpatialPredicate.bru
]
