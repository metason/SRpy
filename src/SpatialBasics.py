from enum import Enum
import math
from typing import Dict


# Calculation schema to determine nearby radius
class NearbySchema(Enum):
    fixed = "fixed"      # use nearbyFactor as fix nearby radius
    circle = "circle"    # use base circle radius of bbox multiplied with nearbyFactor
    sphere = "sphere"    # use sphere radius of bbox multiplied with nearbyFactor
    perimeter = "perimeter"  # use base perimeter multiplied with nearbyFactor
    area = "area"        # use area multiplied with nearbyFactor

    @staticmethod
    def named(name: str):
        return NearbySchema(name) if name in NearbySchema.__members__ else None


# Calculation schema to determine sector size for extruding bbox area
class SectorSchema(Enum):
    fixed = "fixed"      # use sectorFactor as fix sector length for extruding area
    dimension = "dimension"  # use same dimension as object bbox multiplied with sectorFactor
    perimeter = "perimeter"  # use base perimeter multiplied with sectorFactor
    area = "area"        # use area multiplied with sectorFactor
    nearby = "nearby"    # use nearby settings of spatial adjustment for extruding

    @staticmethod
    def named(name: str):
        return SectorSchema(name) if name in SectorSchema.__members__ else None


# Set adjustment parameters before executing pipeline or calling relate() method.
# SpatialReasoner has its own local adjustment that should be set upfront.
class SpatialAdjustment:
    def __init__(
        self,
        maxGap: float = 0.02,
        angle: float = 0.05 * math.pi,
        sector_schema: SectorSchema = SectorSchema.nearby,
        sector_factor: float = 1.0,
        sector_limit: float = 2.5,
        nearby_schema: NearbySchema = NearbySchema.circle,
        nearby_factor: float = 2.0,
        nearby_limit: float = 2.5
    ):
        # Max deviations
        self.maxGap: float = maxGap  # max distance of deviation in all directions in meters
        self.maxAngleDelta: float = angle  # max angle delta in both directions in radians

        # Sector size
        self.sectorSchema: SectorSchema = sector_schema
        self.sectorFactor: float = sector_factor  # multiplying result of calculation schema
        self.sectorLimit: float = sector_limit  # maximal length

        # Vicinity
        self.nearbySchema: NearbySchema = nearby_schema
        self.nearbyFactor: float = nearby_factor  # multiplying radius sum of object and subject (relative to size) as max distance
        self.nearbyLimit: float = nearby_limit  # maximal absolute distance

        # Proportions
        self.longRatio: float = 4.0  # one dimension is factor larger than both others
        self.thinRatio: float = 10.0  # one dimension is 1/factor smaller than both others

    @property
    def yaw(self) -> float:
        """Get max delta of orientation in degrees."""
        return self.maxAngleDelta * 180.0 / math.pi

    def setYaw(self, degrees: float):
        """Set max delta of orientation in degrees."""
        self.maxAngleDelta = degrees * math.pi / 180.0


# Default adjustment only used when no SpatialReasoner builds context
defaultAdjustment = SpatialAdjustment()
tightAdjustment = SpatialAdjustment(maxGap=0.002, angle=0.01 * math.pi, sector_factor=0.5)


class SpatialPredicateCategories:
    def __init__(self):
        self.topology: bool = True
        self.connectivity: bool = True
        self.contacts: bool = False
        self.comparability: bool = False
        self.similarity: bool = False
        self.sectoriality: bool = False
        self.visibility: bool = False
        self.geography: bool = False
        self.contacts: bool = False



class ObjectConfidence:
    """Plausibility values between 0.0 and 1.0"""

    def __init__(self):
        self.pose: float = 0.0  # plausibility of position and orientation of (partially) detected part
        self.dimension: float = 0.0  # plausibility of size of spatial object
        self.label: float = 0.0  # plausibility of classification: label, type, supertype
        self.look: float = 0.0  # plausibility of look and shape

    @property
    def value(self) -> float:
        return (self.pose + self.dimension + self.label) / 3.0

    def setValue(self, value: float):
        self.pose = value
        self.dimension = value
        self.label = value
    @property
    def spatial(self) -> float:
        return (self.pose + self.dimension) / 2.0

    def setSpatial(self, value: float):
        self.pose = value
        self.dimension = value

    def asDict(self) -> Dict[str, float]:
        return {
            "pose": self.pose,
            "dimension": self.dimension,
            "label": self.label,
            "look": self.look
        }


# Searchable, metric, spatio-temporal attributes
class SpatialAtribute(Enum):
    none = "none"
    width = "width"
    height = "height"
    depth = "depth"
    length = "length"
    angle = "angle"
    yaw = "yaw"
    azimuth = "azimuth"  # deviation from north direction
    footprint = "footprint"  # base surface
    frontface = "frontface"  # front surface
    sideface = "sideface"  # side surface
    surface = "surface"  # total bbox surface
    volume = "volume"
    perimeter = "perimeter"
    baseradius = "baseradius"  # radius of 2D floorground circle
    radius = "radius"  # radius of sphere including 3D bbox around center
    speed = "speed"
    confidence = "confidence"
    lifespan = "lifespan"


class SpatialExistence(Enum):
    undefined = "undefined"
    real = "real"  # visual, detected, real object
    virtual = "virtual"  # visual, created, virtual object
    conceptual = "conceptual"  # non-visual, conceptual area, e.g., corner, zone, sensing area, region of interest, interaction field
    aggregational = "aggregational"  # non-visual part-of group, container

    @staticmethod
    def named(name: str):
        return SpatialExistence(name) if name in SpatialExistence.__members__ else SpatialExistence.undefined


class ObjectCause(Enum):
    unknown = "unknown"
    plane_detected = "plane_detected"  # on-device plane detection
    object_detected = "object_detected"  # on-device object detection
    self_tracked = "self_tracked"  # device of user registered and tracked in space
    user_captured = "user_captured"  # captured by user
    user_generated = "user_generated"  # generated by user
    rule_produced = "rule_produced"  # produced by rule or by program logic
    remote_created = "remote_created"  # created by remote service

    @staticmethod
    def named(name: str):
        return ObjectCause(name) if name in ObjectCause.__members__ else ObjectCause.unknown


class MotionState(Enum):
    unknown = "unknown"
    stationary = "stationary"  # immobile
    idle = "idle"  # idle
    moving = "moving"  # moving


class ObjectShape(Enum):
    unknown = "unknown"
    planar = "planar"  # plane, thin box
    cubical = "cubical"  # box
    spherical = "spherical"
    cylindrical = "cylindrical"  # along longest dimension when long
    conical = "conical"
    irregular = "irregular"  # complex shape
    changing = "changing"  # changing shape, e.g., of creature

    @staticmethod
    def named(name: str):
        return ObjectShape(name) if name in ObjectShape.__members__ else ObjectShape.unknown


# TODO: operable?
class ObjectHandling(Enum):
    none = "none"
    movable = "movable"
    slidable = "slidable"
    liftable = "liftable"
    portable = "portable"
    rotatable = "rotatable"
    openable = "openable"
    # tangible = "tangible"  # ?? user-dep.


# Example Usage
if __name__ == "__main__":
    # SpatialAdjustment example
    adjustment = SpatialAdjustment()
    print(f"Default Adjustment Max Gap: {adjustment.maxGap}")  # Output: 0.02
    print(f"Default Adjustment Yaw: {adjustment.yaw} degrees")  # Output: ~2.864788975654116 degrees

    adjustment.setYaw(10.0)
    print(f"Updated Adjustment Max Angle Delta: {adjustment.maxAngleDelta} radians")  # Output: ~0.17453292519943295 radians

    # ObjectConfidence example
    confidence = ObjectConfidence()
    confidence.pose = 0.8
    confidence.dimension = 0.7
    confidence.label = 0.9
    confidence.look = 0.6
    print(f"Object Confidence Value: {confidence.value}")  # Output: (0.8 + 0.7 + 0.9) / 3 = 0.8
    print(f"Object Confidence Spatial: {confidence.spatial}")  # Output: (0.8 + 0.7) / 2 = 0.75
    print(f"Object Confidence as Dictionary: {confidence.asDict()}")  # Output: {'pose': 0.8, 'dimension': 0.7, 'label': 0.9, 'look': 0.6}

    # Enum usage example
    schema = NearbySchema.circle
    print(f"Nearby Schema: {schema.value}")  # Output: "circle"

    existence = SpatialExistence.named("virtual")
    print(f"Spatial Existence: {existence.value}")  # Output: "virtual"

    cause = ObjectCause.named("user_generated")
    print(f"Object Cause: {cause.value}")  # Output: "user_generated"

    shape = ObjectShape.named("spherical")
    print(f"Object Shape: {shape.value}")  # Output: "spherical"

    handling = ObjectHandling.movable
    print(f"Object Handling: {handling.value}")  # Output: "movable"
