# SpatialObject.py
# Python translation of the Swift SpatialObject class.

import math
import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import logging

from .Vector3 import Vector3
from .Vector2 import Vector2
from .SpatialBasics import (
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

from .SpatialPredicate import (
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


from .BBoxSector import BBoxSector, BBoxSectorFlags
if TYPE_CHECKING:
    from .SpatialRelation import SpatialRelation
else:
    from .SpatialRelation import SpatialRelation


class SpatialObject:
    # Class Variables
    booleanAttributes: List[str] = [
        "immobile", "moving", "focused", "visible",
        "equilateral", "thin", "long", "real",
        "virtual", "conceptual"
    ]
    numericAttributes: List[str] = [
        "width", "height", "depth", "w", "h",
        "d", "position", "x", "y", "z", "angle", "confidence"
    ]
    stringAttributes: List[str] = [
        "id", "label", "type", "supertype",
        "existence", "cause", "shape", "look"
    ]

    def __init__(
        self,
        id: str,
        position: Vector3 = Vector3(),
        width: float = 1.0,
        height: float = 1.0,
        depth: float = 1.0,
        angle: float = 0.0,
        label: str = "",
        confidence: float = 0.0
    ):
        # Non-spatial characteristics
        self.id: str = id  # unique id: UUID of source or own generated unique id
        self.existence: SpatialExistence = SpatialExistence.real
        self.cause: ObjectCause = ObjectCause.unknown
        self.label: str = label  # name or label
        self.type: str = ""  # class
        self.supertype: str = ""  # superclass
        self.look: str = ""  # textual description of appearance
        self.data: Optional[Dict[str, Any]] = None  # auxiliary data
        self.created: datetime.datetime = datetime.datetime.now()  # creation time
        self.updated: datetime.datetime = datetime.datetime.now()  # last update time

        # Spatial characteristics
        self.position: Vector3 = position  # base center point at bottom
        self.width: float = width
        self.height: float = height
        self.depth: float = depth
        self.angle: float = angle  # rotation around y axis in radians, counter-clockwise
        self.immobile: bool = False
        self.velocity: Vector3 = Vector3()  # velocity vector
        self.confidence: ObjectConfidence = ObjectConfidence()
        self.confidence.setValue(confidence)
        self.shape: ObjectShape = ObjectShape.unknown
        self.visible: bool = False  # in screen
        self.focused: bool = False  # in center of screen, for some time
        self.context: Optional['SpatialReasoner'] = None  # optional context
        self.transparency = 0.5
    # Derived Attributes
    @property
    def center(self) -> Vector3:
        return Vector3(
        self.position.x + self.width / 2.0,
        self.position.y + self.height / 2.0,
        self.position.z + self.depth / 2.0
    )
        
    @property 
    def transparency(self) -> float:
        return self._transparency  # Use the backing variable
    
    @transparency.setter
    def transparency(self, value: float):
        # Clamp the value between 0.0 and 1.0
        if value < 0.0:
            self._transparency = 0.0
        elif value > 1.0:
            self._transparency = 1.0
        else:
            self._transparency = value

    @property
    def pos(self) -> Vector3:
        return self.position

    @property
    def yaw(self) -> float:
        # in degrees counter-clockwise of WCS
        return self.angle * 180.0 / math.pi

    @property
    def azimuth(self) -> float:
        if self.context is None or self.context.north is None:
            return 0.0
        north_angle = math.degrees(math.atan2(self.context.north.y, self.context.north.x))
        # Use math.fmod to replicate Swift's truncatingRemainder(dividingBy:)
        return -math.fmod(self.yaw + north_angle - 90.0, 360.0)

    
    @property
    def thin(self) -> bool:
        return self.thin_ratio() > 0

    @property
    def long(self) -> bool:
        return self.long_ratio() > 0

    @property
    def equilateral(self) -> bool:
        return self.long_ratio() == 0

    @property
    def real(self) -> bool:
        return self.existence == SpatialExistence.real

    @property
    def virtual(self) -> bool:
        return self.existence == SpatialExistence.virtual

    @property
    def conceptual(self) -> bool:
        return self.existence == SpatialExistence.conceptual

    @property
    def perimeter(self) -> float:
        # footprint perimeter
        return (self.depth + self.width) * 2.0

    @property
    def footprint(self) -> float:
        # base area, floor space
        return self.depth * self.width

    @property
    def frontface(self) -> float:
        # front area
        return self.height * self.width

    @property
    def sideface(self) -> float:
        # side area
        return self.height * self.depth

    @property
    def surface(self) -> float:
        # total surface of bbox
        return (self.height * self.width + self.depth * self.width + self.height * self.depth) * 2.0

    @property
    def volume(self) -> float:
        return self.depth * self.width * self.height

    @property
    def radius(self) -> float:
        # sphere radius from center comprising body volume
        return Vector3(self.width / 2.0, self.depth / 2.0, self.height / 2.0).length()

    @property
    def baseradius(self) -> float:
        # circle radius on 2D base / floor ground
        return math.hypot(self.width / 2.0, self.depth / 2.0)

    @property
    def motion(self) -> MotionState:
        if self.immobile:
            return MotionState.stationary
        if self.confidence.spatial > 0.5:
            if self.velocity.length() > self.adjustment.maxGap:
                return MotionState.moving
            return MotionState.idle
        return MotionState.unknown

    @property
    def moving(self) -> bool:
        return self.motion == MotionState.moving

    @property
    def speed(self) -> float:
        return self.velocity.length()

    @property
    def observing(self) -> bool:
        return self.cause == ObjectCause.self_tracked

    @property
    def length(self) -> float:
        alignment = self.long_ratio(1.1)
        if alignment == 1:
            return self.width
        elif alignment == 2:
            return self.height
        return self.depth

    @property
    def lifespan(self) -> float:
        now = datetime.datetime.now()
        return (now - self.created).total_seconds()

    @property
    def updateInterval(self) -> float:
        now = datetime.datetime.now()
        return (now - self.updated).total_seconds()

    @property
    def adjustment(self) -> SpatialAdjustment:
        return self.context.adjustment if self.context else defaultAdjustment
    
    @adjustment.setter
    def adjustment(self, value: SpatialAdjustment):
        if not isinstance(value, SpatialAdjustment):
            raise ValueError("adjustment must be an instance of SpatialAdjustment")
        self._adjustment = value

    # Index Method
    def index(self) -> int:
        if self.context is not None:
            try:
                return self.context.objects.index(self)
            except ValueError:
                return -1
        return -1

    # Static Methods
    @staticmethod
    def isBoolean(attribute: str) -> bool:
        return attribute in SpatialObject.booleanAttributes

    @staticmethod
    def createDetectedObject(
        id: str,
        label: str = "",
        width: float = 1.0,
        height: float = 1.0,
        depth: float = 1.0
    ) -> 'SpatialObject':
        obj = SpatialObject(
            id=id,
            position=Vector3(0.0, 0.0, 0.0),
            width=width,
            height=height,
            depth=depth
        )
        obj.label = label.lower()
        obj.type = label
        obj.cause = ObjectCause.object_detected
        obj.existence = SpatialExistence.real
        obj.confidence.setValue(0.25)
        obj.immobile = False
        obj.shape = ObjectShape.unknown
        return obj

    @staticmethod
    def createVirtualObject(
        id: str,
        width: float = 1.0,
        height: float = 1.0,
        depth: float = 1.0
    ) -> 'SpatialObject':
        obj = SpatialObject(
            id=id,
            position=Vector3(0.0, 0.0, 0.0),
            width=width,
            height=height,
            depth=depth
        )
        obj.cause = ObjectCause.user_generated
        obj.existence = SpatialExistence.virtual
        obj.confidence.setSpatial(1.0)
        obj.immobile = False
        return obj

    @staticmethod
    def createBuildingElement(
        id: str,
        type: str = "",
        from_pos: Vector3 = Vector3(),
        width: float = 1.0,
        height: float = 1.0,
        depth: float = 1.0
    ) -> 'SpatialObject':
        obj = SpatialObject(
            id=id,
            position=from_pos,
            width=width,
            height=height,
            depth=depth
        )
        obj.label = type.lower()
        obj.type = type
        obj.supertype = "Building Element"
        obj.cause = ObjectCause.plane_detected
        obj.existence = SpatialExistence.real
        obj.confidence.setValue(0.5)
        obj.immobile = True
        obj.shape = ObjectShape.cubical
        return obj

    @staticmethod
    def createBuildingElement_from_vectors(
        id: str,
        type: str = "",
        from_pos: Vector3 = Vector3(),
        to_pos: Vector3 = Vector3(),
        height: float = 1.0,
        depth: float = 0.25
    ) -> 'SpatialObject':
        mid_vector = (to_pos - from_pos) / 2.0
        mid_vector_length = mid_vector.length()
        factor = depth / mid_vector_length / 2.0
        normal = Vector3(mid_vector.x * factor, 0.0, mid_vector.z * factor).rotate(math.pi / 2.0)
        pos = from_pos + mid_vector - Vector3(normal.x, 0.0, normal.z)
        obj = SpatialObject(
            id=id,
            position=pos,
            width=mid_vector_length * 2.0,
            height=height,
            depth=depth
        )
        obj.angle = -math.atan2(mid_vector.z, mid_vector.x)
        obj.label = type.lower()
        obj.type = type
        obj.supertype = "Building Element"
        obj.cause = ObjectCause.user_captured
        obj.existence = SpatialExistence.real
        obj.confidence.setValue(0.9)
        obj.immobile = True
        obj.shape = ObjectShape.cubical
        return obj

    @staticmethod
    def createPerson(
        id: str,
        position: Vector3,
        name: str = ""
    ) -> 'SpatialObject':
        # Create with average dimensions of a person
        person = SpatialObject(
            id=id,
            position=position,
            width=0.46,
            height=1.72,
            depth=0.34
        )
        person.label = name
        person.cause = ObjectCause.self_tracked
        person.existence = SpatialExistence.real
        person.confidence.setValue(1.0)
        person.immobile = False
        person.supertype = "Creature"
        person.type = "Person"
        person.shape = ObjectShape.changing
        return person

    # Set Auxiliary Data
    def setData(self, key: str, value: Any):
        if self.data is not None:
            self.data[key] = value
        else:
            self.data = {key: value}

    def dataValue(self, key: str) -> float:
        if self.data is not None:
            value = self.data.get(key)
            if isinstance(value, float):
                return value
            if isinstance(value, (int,)):
                return float(value)
        return 0.0

    # Object Serialization
    # Full-fledged representation for fact base
    def asDict(self) -> Dict[str, Any]:
        output = {
            "id": self.id,
            "existence": self.existence.value,
            "cause": self.cause.value,
            "label": self.label,
            "type": self.type,
            "supertype": self.supertype,
            "position": [self.position.x, self.position.y, self.position.z],
            "center": [self.center.x, self.center.y, self.center.z],
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "length": self.length,
            "direction": self.mainDirection(),
            "thin": self.thin,
            "long": self.long,
            "equilateral": self.equilateral,
            "real": self.real,
            "virtual": self.virtual,
            "conceptual": self.conceptual,
            "moving": self.moving,
            "perimeter": self.perimeter,
            "footprint": self.footprint,
            "frontface": self.frontface,
            "sideface": self.sideface,
            "surface": self.surface,
            "baseradius": self.baseradius,
            "volume": self.volume,
            "radius": self.radius,
            "angle": self.angle,
            "yaw": self.yaw,
            "azimuth": self.azimuth,
            "lifespan": self.lifespan,
            "updateInterval": self.updateInterval,
            "confidence": self.confidence.asDict(),
            "immobile": self.immobile,
            "velocity": [self.velocity.x, self.velocity.y, self.velocity.z],
            "motion": self.motion.value,
            "shape": self.shape.value,
            "look": self.look,
            "visible": self.visible,
            "focused": self.focused
        }
        if self.data is not None:
            output.update(self.data)  # keeping current
        return output

    # For export
    def toAny(self) -> Dict[str, Any]:
        output = {
            "id": self.id,
            "existence": self.existence.value,
            "cause": self.cause.value,
            "label": self.label,
            "type": self.type,
            "supertype": self.supertype,
            "position": [self.position.x, self.position.y, self.position.z],
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "angle": self.angle,
            "volume": self.volume,
            "immobile": self.immobile,
            "velocity": [self.velocity.x, self.velocity.y, self.velocity.z],
            "confidence": self.confidence.value,
            "shape": self.shape.value,
            "look": self.look,
            "visible": self.visible,
            "focused": self.focused
        }
        if self.data is not None:
            output.update(self.data)  # keeping current
        return output

        # Import/Update from JSON data
    def fromAny(self, input_data: Dict[str, Any]):
            # ID Handling
            id_str = input_data.get("id", "")
            if id_str:
                if self.id != id_str:
                    print("import/update from another id!")
                self.id = id_str

            # Position Handling
            pos_list = input_data.get("position", [])
            if isinstance(pos_list, list) and len(pos_list) == 3:
                pos = Vector3(float(pos_list[0]), float(pos_list[1]), float(pos_list[2]))
            else:
                x = float(input_data.get("x", self.position.x))
                y = float(input_data.get("y", self.position.y))
                z = float(input_data.get("z", self.position.z))
                pos = Vector3(x, y, z)
            self.setPosition(pos)

            # Dimensions Handling
            self.width = float(input_data.get("width", input_data.get("w", self.width)))
            self.height = float(input_data.get("height", input_data.get("h", self.height)))
            self.depth = float(input_data.get("depth", input_data.get("d", self.depth)))

            # Angle Handling
            self.angle = float(input_data.get("angle", self.angle))

            # Labels and Types Handling
            self.label = input_data.get("label", self.label)
            self.type = input_data.get("type", self.type)
            self.supertype = input_data.get("supertype", self.supertype)

            # Confidence Handling
            confidence_data = input_data.get("confidence", self.confidence.value)
                    
            # Check if confidence_data is a dictionary
            if isinstance(confidence_data, dict):
                # Safely extract each confidence component with defaults
                self.confidence.pose = float(confidence_data.get("pose", self.confidence.pose))
                self.confidence.dimension = float(confidence_data.get("dimension", self.confidence.dimension))
                self.confidence.label = float(confidence_data.get("label", self.confidence.label))
                self.confidence.look = float(confidence_data.get("look", self.confidence.look))
            else:
                # Assume confidence_data is a float or convertible to float
                try:
                    confidence_val = float(confidence_data)
                    self.confidence.setValue(confidence_val)
                except (TypeError, ValueError):
                    self.confidence.setValue(self.confidence.value)
            

            # Cause and Existence Handling
            cause_str = input_data.get("cause", self.cause)
            self.cause = ObjectCause.named(cause_str)
            existence_str = input_data.get("existence", self.existence)
            self.existence = SpatialExistence.named(existence_str)

            # Immobile Handling
            self.immobile = bool(input_data.get("immobile", self.immobile))

            # Shape Handling
            shape_str = input_data.get("shape", self.shape)
            self.shape = ObjectShape.named(shape_str)

            # Look Handling
            self.look = input_data.get("look", self.look)

            # Other Attributes Handling
            self.visible = bool(input_data.get("visible", self.visible))
            self.focused = bool(input_data.get("focused", self.focused))

            # Auxiliary Data Handling
            for key, value in input_data.items():
                if key not in SpatialObject.stringAttributes and \
                key not in SpatialObject.numericAttributes and \
                key not in SpatialObject.booleanAttributes:
                    self.setData(key, value)

            # Update Time
            self.updated = datetime.datetime.now()

    # Description
    def desc(self) -> str:
        parts = []
        if self.label and self.label != self.id:
            parts.append(f"{self.label}, ")
        if self.type:
            parts.append(f"{self.type}, ")
        if self.supertype:
            parts.append(f"{self.supertype}, ")
        pos_str = f"{self.position.x:.2f}/" \
                  f"{self.position.y:.2f}/" \
                  f"{self.position.z:.2f}, "
        dims_str = f"{self.width:.2f}x{self.depth:.2f}x{self.height:.2f}, "
        angle_str = f"𝜶:{self.yaw:.1f}°"
        parts.append(pos_str)
        parts.append(dims_str)
        parts.append(angle_str)
        return "".join(parts)

    # Position Setters
    def setPosition(self, pos: Vector3):
        interval = self.updateInterval
        if interval > 0.003 and not self.immobile:
            prev_pos = self.position
            self.velocity = (pos - prev_pos) / interval
        self.position = pos

    def setCenter(self, ctr: Vector3):
        new_position = Vector3(
        ctr.x - self.width / 2.0,
        ctr.y - self.height / 2.0,
        ctr.z - self.depth / 2.0
       )
        self.setPosition(new_position)

    # Rotation and Shifting
    def rotShift(self, rad: float, dx: float, dy: float = 0.0, dz: float = 0.0):
        rotsin = math.sin(rad)
        rotcos = math.cos(rad)
        rx = dx * rotcos - dz * rotsin
        rz = dx * rotsin + dz * rotcos
        vector = Vector3(rx, dy, rz)
        self.position += vector

    def setYaw(self, degrees: float):
        self.angle = degrees * math.pi / 180.0

    # Directional Methods
    def mainDirection(self) -> int:
        return self.long_ratio()

    def long_ratio(self, ratio: float = defaultAdjustment.longRatio) -> int:
        values = (width,height,depth) = [self.width, self.height, self.depth]
        max_val = max(values) if values else 0.0
        min_val = min(values) if values else 0.0
        #not long in any direction        
        if not (max_val > 0 and max_val >= min_val * ratio): 
            return 0
        # if depth is the longest side
        if depth == max_val: 
            return 3
        # if height is the longest side
        if height == max_val: 
            return 2
        # if width is the longest side
        return 1
            
    def thin_ratio(self, ratio: float = defaultAdjustment.thinRatio) -> int:
        values = (width,height,depth) = [self.width, self.height, self.depth]
        max_val = max(values) if values else 0.0
        min_val = min(values) if values else 0.0
        min_ratio = min_val * ratio
        if max_val >= (min_val * ratio):
            if (height == min_val) and (width > (ratio * min_val)) and (depth > (ratio * min_val)):
                return 2
            if (width == min_val )and (height > (ratio * min_val)) and (depth > (ratio * min_val)):
                return 1
            if (depth == min_val) and (width > (ratio * min_val)) and (height > (ratio * min_val)):
                return 3
        return 0

    # Point Calculation Methods
    def lowerPoints(self, local: bool = False) -> List[Vector3]:
        p0 = Vector3(self.width / 2.0, self.depth / 2.0, 0.0)
        p1 = Vector3(-self.width / 2.0, self.depth / 2.0, 0.0)
        p2 = Vector3(-self.width / 2.0, -self.depth / 2.0, 0.0)
        p3 = Vector3(self.width / 2.0, -self.depth / 2.0, 0.0)
        vector = Vector3()

        if not local:
            p0 = p0.rotate(-self.angle)
            p1 = p1.rotate(-self.angle)
            p2 = p2.rotate(-self.angle)
            p3 = p3.rotate(-self.angle)
            vector = self.position

        return [
            Vector3(p0.x + vector.x, vector.y, p0.z + vector.z),
            Vector3(p1.x + vector.x, vector.y, p1.z + vector.z),
            Vector3(p2.x + vector.x, vector.y, p2.z + vector.z),
            Vector3(p3.x + vector.x, vector.y, p3.z + vector.z)
        ]

    def upperPoints(self, local: bool = False) -> List[Vector3]:
        p0 = Vector3(self.width / 2.0, self.depth / 2.0, self.height)
        p1 = Vector3(-self.width / 2.0, self.depth / 2.0, self.height)
        p2 = Vector3(-self.width / 2.0, -self.depth / 2.0, self.height)
        p3 = Vector3(self.width / 2.0, -self.depth / 2.0, self.height)
        vector = Vector3()

        if not local:
            p0 = p0.rotate(-self.angle)
            p1 = p1.rotate(-self.angle)
            p2 = p2.rotate(-self.angle)
            p3 = p3.rotate(-self.angle)
            vector = self.position

        return [
            Vector3(p0.x + vector.x, vector.y + self.height, p0.z + vector.z),
            Vector3(p1.x + vector.x, vector.y + self.height, p1.z + vector.z),
            Vector3(p2.x + vector.x, vector.y + self.height, p2.z + vector.z),
            Vector3(p3.x + vector.x, vector.y + self.height, p3.z + vector.z)
        ]

    def frontPoints(self, local: bool = False) -> List[Vector3]:
        p0 = Vector3(self.width / 2.0, self.depth / 2.0, 0.0)
        p1 = Vector3(-self.width / 2.0, self.depth / 2.0, 0.0)
        vector = Vector3()

        if not local:
            p0 = p0.rotate(-self.angle)
            p1 = p1.rotate(-self.angle)
            vector = self.position

        return [
            Vector3(p0.x + vector.x, vector.y, p0.z + vector.z),
            Vector3(p1.x + vector.x, vector.y, p1.z + vector.z),
            Vector3(p1.x + vector.x, vector.y + self.height, p1.z + vector.z),
            Vector3(p0.x + vector.x, vector.y + self.height, p0.z + vector.z)
        ]

    def backPoints(self, local: bool = False) -> List[Vector3]:
        p2 = Vector3(-self.width / 2.0, -self.depth / 2.0, 0.0)
        p3 = Vector3(self.width / 2.0, -self.depth / 2.0, 0.0)
        vector = Vector3()

        if not local:
            p2 = p2.rotate(-self.angle)
            p3 = p3.rotate(-self.angle)
            vector = self.position

        return [
            Vector3(p2.x + vector.x, vector.y, p2.z + vector.z),
            Vector3(p3.x + vector.x, vector.y, p3.z + vector.z),
            Vector3(p3.x + vector.x, vector.y + self.height, p3.z + vector.z),
            Vector3(p2.x + vector.x, vector.y + self.height, p2.z + vector.z)
        ]

    def rightPoints(self, local: bool = False) -> List[Vector3]:
        p1 = Vector3(-self.width / 2.0, self.depth / 2.0, 0.0)
        p2 = Vector3(-self.width / 2.0, -self.depth / 2.0, 0.0)
        vector = Vector3()

        if not local:
            p1 = p1.rotate(-self.angle)
            p2 = p2.rotate(-self.angle)
            vector = self.position

        return [
            Vector3(p1.x + vector.x, vector.y, p1.z + vector.z),
            Vector3(p2.x + vector.x, vector.y, p2.z + vector.z),
            Vector3(p2.x + vector.x, vector.y + self.height, p2.z + vector.z),
            Vector3(p1.x + vector.x, vector.y + self.height, p1.z + vector.z)
        ]

    def leftPoints(self, local: bool = False) -> List[Vector3]:
        p0 = Vector3(self.width / 2.0, self.depth / 2.0, 0.0)
        p3 = Vector3(self.width / 2.0, -self.depth / 2.0, 0.0)
        vector = Vector3()

        if not local:
            p0 = p0.rotate(-self.angle)
            p3 = p3.rotate(-self.angle)
            vector = self.position

        return [
            Vector3(p3.x + vector.x, vector.y, p3.z + vector.z),
            Vector3(p0.x + vector.x, vector.y, p0.z + vector.z),
            Vector3(p0.x + vector.x, vector.y + self.height, p0.z + vector.z),
            Vector3(p3.x + vector.x, vector.y + self.height, p3.z + vector.z)
        ]

    def points(self, local: bool = False) -> List[Vector3]:
        p0 = Vector2(self.width / 2.0, self.depth / 2.0)
        p1 = Vector2(-self.width / 2.0, self.depth / 2.0)
        p2 = Vector2(-self.width / 2.0, -self.depth / 2.0)
        p3 = Vector2(self.width / 2.0, -self.depth / 2.0)
        vector = Vector3()

        if not local:
            p0 = p0.rotate(-self.angle)
            p1 = p1.rotate(-self.angle)
            p2 = p2.rotate(-self.angle)
            p3 = p3.rotate(-self.angle)
            vector = self.position

        return [
            Vector3(p0.x + vector.x, vector.y, p0.y + vector.z),
            Vector3(p1.x + vector.x, vector.y, p1.y + vector.z),
            Vector3(p2.x + vector.x, vector.y, p2.y + vector.z),
            Vector3(p3.x + vector.x, vector.y, p3.y + vector.z),
            Vector3(p0.x + vector.x, vector.y + self.height, p0.y + vector.z),
            Vector3(p1.x + vector.x, vector.y + self.height, p1.y + vector.z),
            Vector3(p2.x + vector.x, vector.y + self.height, p2.y + vector.z),
            Vector3(p3.x + vector.x, vector.y + self.height, p3.y + vector.z)
        ]

    # Distance Methods
    def distance(self, to: Vector3) -> float:
        return (to - self.center).length()

    def baseDistance(self, to: Vector3) -> float:
        point = Vector3(to.x, self.position.y, to.z)
        return (point - self.position).length()

    # Coordinate Transformation
    def intoLocal(self, pt: Vector3) -> Vector3:
        vx = pt.x - self.position.x
        vz = pt.z - self.position.z
        rotsin = math.sin(self.angle)
        rotcos = math.cos(self.angle)
        x = vx * rotcos - vz * rotsin
        z = vx * rotsin + vz * rotcos
        return Vector3(x, pt.y - self.position.y, z)
    
    def intoLocal_pts(self, pts: List[Vector3]) -> List[Vector3]:
        rotsin = math.sin(self.angle)
        rotcos = math.cos(self.angle)
        result = []
        for pt in pts:
            vx = pt.x - self.position.x
            vz = pt.z - self.position.z
            x = vx * rotcos - vz * rotsin
            z = vx * rotsin + vz * rotcos
            result.append(Vector3(x, pt.y - self.position.y, z))
        return result

    def rotate_pts(self, pts: List[Vector3], by: float) -> List[Vector3]:
        rotsin = math.sin(by)
        rotcos = math.cos(by)
        result = []
        for pt in pts:
            x = pt.x * rotcos - pt.z * rotsin
            z = pt.x * rotsin + pt.z * rotcos
            result.append(Vector3(x, pt.y, z))
        return result

    # Sector Methods
    def sectorOf(self, point: Vector3, nearBy: bool = False, epsilon: float = -100.0) -> BBoxSector:
        zone = BBoxSector()
        if nearBy:
            pt = Vector3(point.x, point.y - self.height / 2.0, point.z)
            distance = pt.length()
            if distance > self.nearbyRadius():
                return zone
        if epsilon > -99.0:
            delta = epsilon
        else: 
            delta = self.adjustment.maxGap
    
        if (
            point.x <= self.width / 2.0 + delta and
            -point.x <= self.width / 2.0 + delta and
            point.z <= self.depth / 2.0 + delta and
            -point.z <= self.depth / 2.0 + delta and
            point.y <= self.height + delta and
            point.y >= -delta
        ):
            zone.insert(BBoxSectorFlags.i)
            return zone
        

        if point.x + delta > self.width / 2.0:
            zone.insert(BBoxSectorFlags.l)
        elif -point.x + delta > self.width / 2.0:
            zone.insert(BBoxSectorFlags.r)

        if point.z + delta > self.depth / 2.0:
            zone.insert(BBoxSectorFlags.a)
        elif -point.z + delta > self.depth / 2.0:
            zone.insert(BBoxSectorFlags.b)

        if point.y + delta > self.height:
            zone.insert(BBoxSectorFlags.o)
        elif point.y - delta < 0.0:
            zone.insert(BBoxSectorFlags.u)

        return zone

    def nearbyRadius(self) -> float:
        if self.adjustment.nearbySchema == NearbySchema.fixed:
            return self.adjustment.nearbyFactor
        elif self.adjustment.nearbySchema == NearbySchema.circle:
            return min(self.baseradius * self.adjustment.nearbyFactor, self.adjustment.nearbyLimit)
        elif self.adjustment.nearbySchema == NearbySchema.sphere:
            return min(self.radius * self.adjustment.nearbyFactor, self.adjustment.nearbyLimit)
        elif self.adjustment.nearbySchema == NearbySchema.perimeter:
            return min((self.height + self.width) * self.adjustment.nearbyFactor, self.adjustment.nearbyLimit)
        elif self.adjustment.nearbySchema == NearbySchema.area:
            return min(self.height * self.width * self.adjustment.nearbyFactor, self.adjustment.nearbyLimit)
        return 0.0

    def sector_lengths(self, sector: BBoxSector = BBoxSector(BBoxSectorFlags.i)) -> Vector3:
            """
            Calculate the sector lengths based on the provided sector.

            Args:
                sector (BBoxSector, optional): The sector to calculate lengths for. Defaults to inside sector.

            Returns:
                Vector3: The lengths in x, y, z directions.
            """
            result = Vector3(x=self.width, y=self.height, z=self.depth)
            
            if sector.contains(BBoxSectorFlags.a) or sector.contains(BBoxSectorFlags.b):
                if self.adjustment.sectorSchema == "fixed":
                    result.z = self.adjustment.sectorFactor
                elif self.adjustment.sectorSchema == "area":
                    result.z = min(self.height * self.width * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "dimension":
                    result.z = min(self.depth * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "perimeter":
                    result.z = min((self.height + self.width) * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "nearby":
                    result.z = min(self.nearby_radius(), self.adjustment.sectorLimit)
            
            if sector.contains(BBoxSectorFlags.l) or sector.contains(BBoxSectorFlags.r):
                if self.adjustment.sectorSchema == "fixed":
                    result.x = self.adjustment.sectorFactor
                elif self.adjustment.sectorSchema == "area":
                    result.x = min(self.height * self.depth * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "dimension":
                    result.x = min(self.width * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "perimeter":
                    result.x = min((self.height + self.depth) * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "nearby":
                    result.x = min(self.nearby_radius(), self.adjustment.sectorLimit)
            
            if sector.contains(BBoxSectorFlags.o) or sector.contains(BBoxSectorFlags.u):
                if self.adjustment.sectorSchema == "fixed":
                    result.y = self.adjustment.sectorFactor
                elif self.adjustment.sectorSchema == "area":
                    result.y = min(self.width * self.depth * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "dimension":
                    result.y = min(self.height * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "perimeter":
                    result.y = min((self.width + self.depth) * self.adjustment.sectorFactor, self.adjustment.sectorLimit)
                elif self.adjustment.sectorSchema == "nearby":
                    result.y = min(self.nearby_radius(), self.adjustment.sectorLimit)
            
            return result
        
        
    def _haveSameCenter(self, subject: 'SpatialObject', center_distance:float, result: List['SpatialRelation']) -> List['SpatialRelation']:
        if center_distance < 1e-6:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samecenter,
                object=self,
                delta=center_distance,
                angle=subject.angle - self.angle
            )
            result.append(relation)
        return result
    
    def _areNearOrFar(self, subject: 'SpatialObject', center_distance: float, result: List['SpatialRelation']) -> List['SpatialRelation']:
        if center_distance < subject.nearbyRadius() + self.nearbyRadius():
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.near,
                object=self,
                delta=center_distance,
                angle=subject.angle - self.angle
            )
            result.append(relation)
        else:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.far,
                object=self,
                delta=center_distance,
                angle=subject.angle - self.angle
            )
            result.append(relation)
        return result
    
    def _areDisjoint(self, subject: 'SpatialObject', center_distance:float, can_not_overlap:bool, result: List['SpatialRelation']) -> List['SpatialRelation']:
        if can_not_overlap:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.disjoint,
                object=self,
                delta=center_distance,
                angle=subject.angle - self.angle
            )
            result.append(relation)
        return result
    
    def _basicAdjacency(self, subject: 'SpatialObject', center_zone: BBoxSector, result: List['SpatialRelation']) -> List['SpatialRelation']:
        local_center = self.intoLocal(pt=subject.center)
        theta = subject.angle - self.angle
        if SpatialPredicate.l in center_zone:
            gap = float(local_center.x) - self.width / 2.0 - subject.width / 2.0
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.left,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)
        elif SpatialPredicate.r in center_zone:
            gap = float(-local_center.x) - self.width / 2.0 - subject.width / 2.0
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.right,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)

        if SpatialPredicate.a in center_zone:
            gap = float(local_center.z) - self.depth / 2.0 - subject.depth / 2.0
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.ahead,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)
        elif SpatialPredicate.b in center_zone:
            gap = float(-local_center.z) - self.depth / 2.0 - subject.depth / 2.0
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.behind,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)

        if SpatialPredicate.o in center_zone:
            gap = float(local_center.y) - subject.height / 2.0 - self.height
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.above,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)
        elif SpatialPredicate.u in center_zone:
            gap = float(-local_center.y) - subject.height / 2.0
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.below,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)
        return result
        
    def _catch_side_related_adjacency(self, subject: 'SpatialObject', result: List['SpatialRelation']) -> tuple[bool, List['SpatialRelation']]:
        theta = subject.angle - self.angle
        local_center = self.intoLocal(pt=subject.center)
        near_zone = self.sectorOf(point=local_center, nearBy=True, epsilon=-self.adjustment.maxGap)
        local_pts = self.intoLocal_pts(pts=subject.points())
        is_beside = False
        aligned = False
        side_gap = float('inf')
        if near_zone != SpatialPredicate.i:
            if abs(math.fmod(theta, math.pi/2.0)) < self.adjustment.maxAngleDelta:
                aligned = True
            # Check left/right sides.
            if SpatialPredicate.l in near_zone:
                for pt in local_pts:
                    side_gap = min(side_gap, float(pt.x) - self.width / 2.0)
                if side_gap >= 0.0:
                    is_beside = True
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.leftside,
                        object=self,
                        delta=side_gap,
                        angle=theta
                    )
                    result.append(relation)
            elif SpatialPredicate.r in near_zone:
                for pt in local_pts:
                    side_gap = min(side_gap, float(-pt.x) - self.width / 2.0)
                if side_gap >= 0.0:
                    is_beside = True
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.rightside,
                        object=self,
                        delta=side_gap,
                        angle=theta
                    )
                    result.append(relation)

            # Check top/bottom of sides.
            if SpatialPredicate.o in near_zone:
                temp_gap = float('inf')
                for pt in local_pts:
                    temp_gap = min(temp_gap, float(pt.y) - self.height)
                if temp_gap >= 0.0:
                    if temp_gap <= self.adjustment.maxGap:
                        relation = SpatialRelation(
                            subject=subject,
                            predicate=SpatialPredicate.ontop,
                            object=self,
                            delta=temp_gap,
                            angle=theta
                        )
                        result.append(relation)
                        # Optionally, add an "on" relation for connectivity.
                        if self.context and self.context.deduce.connectivity:
                            relation = SpatialRelation(
                                subject=subject,
                                predicate=SpatialPredicate.on,
                                object=self,
                                delta=temp_gap,
                                angle=theta
                            )
                            result.append(relation)
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.upperside,
                        object=self,
                        delta=temp_gap,
                        angle=theta
                    )
                    result.append(relation)
            elif SpatialPredicate.u in near_zone:
                temp_gap = float('inf')
                for pt in local_pts:
                    temp_gap = min(temp_gap, float(-pt.y))
                if temp_gap >= 0.0:
                    if temp_gap <= self.adjustment.maxGap:
                        relation = SpatialRelation(
                            subject=subject,
                            predicate=SpatialPredicate.beneath,
                            object=self,
                            delta=temp_gap,
                            angle=theta
                        )
                        result.append(relation)
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.lowerside,
                        object=self,
                        delta=temp_gap,
                        angle=theta
                    )
                    result.append(relation)

            # Check front/back sides.
            if SpatialPredicate.a in near_zone:
                temp_gap = float('inf')
                for pt in local_pts:
                    temp_gap = min(temp_gap, float(pt.z) - self.depth / 2.0)
                if temp_gap >= 0.0:
                    is_beside = True
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.frontside,
                        object=self,
                        delta=temp_gap,
                        angle=theta
                    )
                    result.append(relation)
            elif SpatialPredicate.b in near_zone:
                temp_gap = float('inf')
                for pt in local_pts:
                    temp_gap = min(temp_gap, float(-pt.z) - self.depth / 2.0)
                if temp_gap >= 0.0:
                    is_beside = True
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.backside,
                        object=self,
                        delta=temp_gap,
                        angle=theta
                    )
                    result.append(relation)

            if is_beside:
                # Add a general 'beside' relation if any side contact is detected.
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.beside,
                    object=self,
                    delta=side_gap if side_gap != float('inf') else 0.0,
                    angle=theta
                )
                result.append(relation)
                # Additionally, if the gap is very small, add a 'touching' relation.
                if side_gap <= 0.05:  # threshold for "touching"
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.touching,
                        object=self,
                        delta=side_gap,
                        angle=theta
                    )
                    result.append(relation)
        return aligned, result
    
    def _check_Assembly(self, subject: 'SpatialObject', result: List['SpatialRelation'],aligned=False) -> List['SpatialRelation']:
        # === 5. Assembly: Inside / Containing / Overlapping / Meeting ===
        # If all computed zones show the inside flag, add an 'inside' relation.
        radius_sum = self.radius + subject.radius
        theta = subject.angle - self.angle
        center_distance = (subject.center - self.center).length()
        can_not_overlap = center_distance > radius_sum

        # Convert subject points to local coordinates.
        local_pts = self.intoLocal_pts(pts=subject.points())
        zones = [self.sectorOf(point=pt, nearBy=False, epsilon=0.00001) for pt in local_pts]

        # Flags used to decide if we will later add connectivity or a disjoint relation.
        is_disjoint = True
        is_connected = False

        # --- Case 1: All zones show the inside flag.
        if all(zone.contains_flag(BBoxSectorFlags.i) for zone in zones):
            is_disjoint = False
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.inside,
                object=self,
                delta=center_distance,
                angle=theta
            )
            result.append(relation)
            # If connectivity is enabled add an additional 'in' relation.
            if self.context:
                if self.context.deduce.connectivity:
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.in_,
                        object=self,
                        delta=center_distance,
                        angle=theta
                    )
                    result.append(relation)
        else:
            # --- Case 2: If self completely encloses subject, add a 'containing' relation.
            if ((subject.radius - self.radius) > (center_distance / 2.0) and
                subject.width > self.width and
                subject.height > self.height and
                subject.depth > self.depth):
                is_disjoint = False
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.containing,
                    object=self,
                    delta=0.0,
                    angle=theta
                )
                result.append(relation)
            else:
                # --- Case 3: Partial overlap.
                cnt = sum(1 for zone in zones if zone.contains_flag(BBoxSectorFlags.i))
                if cnt > 0 and not can_not_overlap:
                    is_disjoint = False
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.overlapping,
                        object=self,
                        delta=center_distance,
                        angle=theta
                    )
                    result.append(relation)

                # --- Compute the bounding box of the local points.
                # Assume local_pts is non-empty.
                min_y = min(pt.y for pt in local_pts)
                max_y = max(pt.y for pt in local_pts)
                min_y = local_pts[0].y
                max_y = local_pts[-1].y
                min_x = min(pt.x for pt in local_pts)
                max_x = max(pt.x for pt in local_pts)
                min_z = min(pt.z for pt in local_pts)
                max_z = max(pt.z for pt in local_pts)

                # --- Check for "crossing" conditions.
                crossings = 0
                if not can_not_overlap:
                    if (min_x < -self.width/2.0 and max_x > self.width/2.0 and
                        min_z < self.depth/2.0 and max_z > -self.depth/2.0 and
                        min_y < self.height and max_y > 0):
                        crossings += 1
                    if (min_z < -self.depth/2.0 and max_z > self.depth/2.0 and
                        min_x < self.width/2.0 and max_x > -self.width/2.0 and
                        min_y < self.height and max_y > 0):
                        crossings += 1
                    if (min_y < 0.0 and max_y > self.height and
                        min_x < self.width/2.0 and max_x > -self.width/2.0 and
                        min_z < self.depth/2.0 and max_z > -self.depth/2.0):
                        crossings += 1

                    if crossings > 0:
                        is_disjoint = False
                        relation = SpatialRelation(
                            subject=subject,
                            predicate=SpatialPredicate.crossing,
                            object=self,
                            delta=center_distance,
                            angle=theta
                        )
                        result.append(relation)

                # --- Compute overlaps along each axis.
                # Y-overlap (ylap):
                ylap = self.height
                if max_y < self.height and min_y > 0:
                    ylap = max_y - min_y
                else:
                    if min_y > 0:
                        ylap = abs(self.height - min_y)
                    else:
                        ylap = abs(max_y)

                # X-overlap (xlap):
                xlap = self.width
                if (min_x < (self.width/2.0 + self.adjustment.maxGap)) and (max_x > (-self.width/2.0 - self.adjustment.maxGap)):
                    if (max_x < self.width/2.0) and (min_x > -self.width/2.0):
                        xlap = max_x - min_x
                    else:
                        if min_x > (-self.width/2.0 - self.adjustment.maxGap):
                            xlap = abs(self.width/2.0 - min_x)
                        else:
                            xlap = abs(max_x + self.width/2.0)
                else:
                    xlap = -1

                # Z-overlap (zlap):
                zlap = self.depth
                if min_z < (self.depth/2.0 + self.adjustment.maxGap) and max_z > (-self.depth/2.0 - self.adjustment.maxGap):
                    if (max_z < self.depth/2.0) and( min_z > -self.depth/2.0):
                        zlap = max_z - min_z
                    else:
                        if min_z > (-self.depth/2.0):
                            zlap = abs(self.depth/2.0 - min_z)
                        else:
                            zlap = abs(max_z + self.depth/2.0)
                else:
                    zlap = -1

                # --- Determine contact or meeting relations.
                if (min_y < (self.height + self.adjustment.maxGap)) and (max_y > (-self.adjustment.maxGap)):
                    gap = min(xlap, zlap)
                    # First, try a "touching" relation when the boxes are not aligned,
                    # subject cannot overlap self, and gap is positive but less than maxGap.
                    if (not aligned and can_not_overlap and gap > 0.0 and gap < self.adjustment.maxGap):
                        if (max_x < ((-self.width/2.0) + self.adjustment.maxGap) or
                            min_x > ((self.width/2.0) - self.adjustment.maxGap) or
                            max_z < ((-self.depth/2.0) + self.adjustment.maxGap) or
                            min_z > ((self.depth/2.0) - self.adjustment.maxGap)):
                            relation = SpatialRelation(
                                subject=subject,
                                predicate=SpatialPredicate.touching,
                                object=self,
                                delta=gap,
                                angle=theta
                            )
                            result.append(relation)
                            if (not is_connected and
                                (self.context is not None) and self.context.deduce.connectivity):
                                relation = SpatialRelation(
                                    subject=subject,
                                    predicate=SpatialPredicate.by,
                                    object=self,
                                    delta=gap,
                                    angle=theta
                                )
                                result.append(relation)
                                is_connected = True
                        else:
                            print(f"OOPS, rotated bbox might cross: assembly relations by shortest distance not yet implemented! {subject.id} - ? - {self.id}")
                    else:
                        # When boxes are aligned.
                        if xlap >= 0.0 and zlap >= 0.0:
                            # If there is extra overlap in Y (indicating one object is beside the other)
                            # and gap is less than maxGap, decide between meeting and touching.
                            if ylap > self.adjustment.maxGap and gap < self.adjustment.maxGap:
                                if xlap > self.adjustment.maxGap or zlap > self.adjustment.maxGap:
                                    relation = SpatialRelation(
                                        subject=subject,
                                        predicate=SpatialPredicate.meeting,
                                        object=self,
                                        delta=max(xlap, zlap),
                                        angle=theta
                                    )
                                    result.append(relation)
                                    if (not is_connected and
                                        (self.context is not None) and self.context.deduce.connectivity and
                                        subject.volume < self.volume):
                                        relation = SpatialRelation(
                                            subject=subject,
                                            predicate=SpatialPredicate.at,
                                            object=self,
                                            delta=gap,
                                            angle=theta
                                        )
                                        result.append(relation)
                                        is_connected = True
                                else:
                                    relation = SpatialRelation(
                                        subject=subject,
                                        predicate=SpatialPredicate.touching,
                                        object=self,
                                        delta=gap,
                                        angle=theta
                                    )
                                    result.append(relation)
                                    if (not is_connected and
                                        (self.context is not None) and  self.context.deduce.connectivity):
                                        relation = SpatialRelation(
                                            subject=subject,
                                            predicate=SpatialPredicate.by,
                                            object=self,
                                            delta=gap,
                                            angle=theta
                                        )
                                        result.append(relation)
                                        is_connected = True
                            else:
                                gap = ylap
                                if xlap > self.adjustment.maxGap and zlap > self.adjustment.maxGap:
                                    relation = SpatialRelation(
                                        subject=subject,
                                        predicate=SpatialPredicate.meeting,
                                        object=self,
                                        delta=gap,
                                        angle=theta
                                    )
                                    result.append(relation)
                                else:
                                    relation = SpatialRelation(
                                        subject=subject,
                                        predicate=SpatialPredicate.touching,
                                        object=self,
                                        delta=gap,
                                        angle=theta
                                    )
                                    result.append(relation)

        # --- If nothing has been marked as overlapping (or any other relation), mark as disjoint.
        if is_disjoint:
            gap = center_distance
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.disjoint,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)
        return result
    
    def _deduce_orientation(self, subject: 'SpatialObject', result: List['SpatialRelation']) -> List['SpatialRelation']:
        theta = subject.angle - self.angle
        local_center = self.intoLocal(pt=subject.center)
        center_distance = (subject.center - self.center).length()
        
        if abs(theta) < self.adjustment.maxAngleDelta:
            gap = float(local_center.z)
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.aligned,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)

            front_gap = float(local_center.z) + subject.depth / 2.0 - self.depth / 2.0
            if abs(front_gap) < self.adjustment.maxGap:
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.frontaligned,
                    object=self,
                    delta=front_gap,
                    angle=theta
                )
                result.append(relation)

            back_gap = float(local_center.z) - subject.depth / 2.0 + self.depth / 2.0
            if abs(back_gap) < self.adjustment.maxGap:
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.backaligned,
                    object=self,
                    delta=back_gap,
                    angle=theta
                )
                result.append(relation)

            right_gap = float(local_center.x) - subject.width / 2.0 + self.width / 2.0
            if abs(right_gap) < self.adjustment.maxGap:
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.rightaligned,
                    object=self,
                    delta=right_gap,
                    angle=theta
                )
                result.append(relation)

            left_gap = float(local_center.x) + subject.width / 2.0 - self.width / 2.0
            if abs(left_gap) < self.adjustment.maxGap:
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.leftaligned,
                    object=self,
                    delta=left_gap,
                    angle=theta
                )
                result.append(relation)
        else:
            gap = center_distance
            if abs(theta % math.pi) < self.adjustment.maxAngleDelta:
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.opposite,
                    object=self,
                    delta=gap,
                    angle=theta
                )
                result.append(relation)
            elif abs(theta % (math.pi / 2.0)) < self.adjustment.maxAngleDelta:
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.orthogonal,
                    object=self,
                    delta=gap,
                    angle=theta
                )
                result.append(relation)
        return result
    
    def _deduce_visibility(self, subject: 'SpatialObject', result: List['SpatialRelation']) -> List['SpatialRelation']:
        center_distance = (subject.center - self.center).length()
        if self.context is None: 
            return result
        if self.context.deduce.visibility:
            # Compute the observer-relative bearing.
            rad = math.atan2(subject.center.x, subject.center.z)
            angle_deg = rad * 180.0 / math.pi
            hour_angle = 30.0  # 360/12
            # Adjust angle_deg so that boundaries fall near clock numbers.
            if angle_deg < 0.0:
                angle_deg -= hour_angle / 2.0
            else:
                angle_deg += hour_angle / 2.0
            cnt = int(round(angle_deg / hour_angle))
            # Map cnt to clock predicates:
            clock_map = {
                -4: SpatialPredicate.fouroclock,
                -3: SpatialPredicate.threeoclock,
                -2: SpatialPredicate.twooclock,
                -1: SpatialPredicate.oneoclock,
                0: SpatialPredicate.twelveoclock,
                1: SpatialPredicate.elevenoclock,
                2: SpatialPredicate.tenoclock,
                3: SpatialPredicate.nineoclock,
                4: SpatialPredicate.eightoclock
            }
            if cnt in clock_map:
                pred = clock_map[cnt]
                relation = SpatialRelation(
                    subject=subject,
                    predicate=pred,
                    object=self,
                    delta=center_distance,
                    angle=rad
                )
                result.append(relation)
                # Optionally, if very close, add a tangible relation.
                if center_distance <= 1.25:
                    relation = SpatialRelation(
                        subject=subject,
                        predicate=SpatialPredicate.tangible,
                        object=self,
                        delta=center_distance,
                        angle=rad
                    )
                    result.append(relation)
        
        return result
        
        

    def topologies(self, subject: 'SpatialObject') -> List['SpatialRelation']:
        result: List['SpatialRelation'] = []
        theta = subject.angle - self.angle
        center_distance = (subject.center - self.center).length()
        radius_sum = self.radius + subject.radius
        can_not_overlap = center_distance > radius_sum

        # Compute local coordinates once for use below.
        local_pts = self.intoLocal_pts(pts=subject.points())
        local_pts = [self.intoLocal(pt=pt) for pt in subject.points()]
        local_center = self.intoLocal(pt=subject.center)
        center_zone = self.sectorOf(point=local_center, nearBy=False, epsilon=-self.adjustment.maxGap)

        # === 1. Same Center Relation ===
        result = self._haveSameCenter(subject=subject, center_distance=center_distance, result=result)

        # === 2. Near / Far Relation ===
        result = self._areNearOrFar(subject=subject, center_distance=center_distance, result=result)

        # Always add a disjoint relation if objects cannot overlap.
        result = self._areDisjoint(subject=subject, center_distance=center_distance,can_not_overlap=can_not_overlap, result=result)

        # === 3. Basic Adjacency by Center Zone (front/back/left/right/above/below) ===
        result = self._basicAdjacency(subject=subject, center_zone=center_zone, result=result) 
        # === 4. Side-related Adjacency Using "nearBy" Zone ===
        # Recompute zone with nearBy flag to catch touching/beside relations.
        (aligned, result) = self._catch_side_related_adjacency(subject=subject, result=result)
        

        # === 5. Assembly: Inside / Containing / Overlapping / Meeting ===
        # If all computed zones show the inside flag, add an 'inside' relation.
        result = self._check_Assembly(subject=subject, result=result,aligned=aligned)
        
        # === 6. Orientation Deduction ===
        result = self._deduce_orientation(subject=subject, result=result)

        # === 7. Visibility Deduction (Clock Angle Predicates) ===
        result = self._deduce_visibility(subject=subject, result=result)

        return result


    # Similarities Method
    def similarities(self, subject: 'SpatialObject') -> List['SpatialRelation']:
        result: List['SpatialRelation'] = []
        relation: 'SpatialRelation'
        theta = subject.angle - self.angle
        val: float = 0.0
        minVal: float = 0.0
        maxVal: float = 0.0
        sameWidth: bool = False
        sameDepth: bool = False
        sameHeight: bool = False

        # Same Center
        val = (self.center - subject.center).length()
        if val < self.adjustment.maxGap:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samecenter,
                object=self,
                delta=val,
                angle=theta
            )
            result.append(relation)

        # Same Position
        val = (self.position - subject.position).length()
        if val < self.adjustment.maxGap:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.sameposition,
                object=self,
                delta=val,
                angle=theta
            )
            result.append(relation)

        # Same Width
        val = abs(self.width - subject.width)
        if val < self.adjustment.maxGap:
            sameWidth = True
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samewidth,
                object=self,
                delta=val,
                angle=theta
            )
            result.append(relation)

        # Same Depth
        val = abs(self.depth - subject.depth)
        if val < self.adjustment.maxGap:
            sameDepth = True
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samedepth,
                object=self,
                delta=val,
                angle=theta
            )
            result.append(relation)

        # Same Height
        val = abs(self.height - subject.height)
        if val < self.adjustment.maxGap:
            sameHeight = True
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.sameheight,
                object=self,
                delta=val,
                angle=theta
            )
            result.append(relation)

        # Same Perimeter
        val = subject.depth * subject.width
        minVal = (self.depth - self.adjustment.maxGap) + (self.width - self.adjustment.maxGap)
        maxVal = (self.depth + self.adjustment.maxGap) + (self.width + self.adjustment.maxGap)
        if minVal < val < maxVal:
            gap = self.depth * self.width - val
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.sameperimeter,
                object=self,
                delta=2.0 * gap,
                angle=theta
            )
            result.append(relation)

        # Same Cuboid
        if sameWidth and sameDepth and sameHeight:
            val = subject.volume - self.volume
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samecuboid,
                object=self,
                delta=val,
                angle=theta
            )
            result.append(relation)

        # Same Length
        val = abs(self.length - subject.length)
        if val < self.adjustment.maxGap:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samelength,
                object=self,
                delta=val,
                angle=theta
            )
            result.append(relation)

        # Same Front
        val = subject.height * subject.width
        minVal = (self.height - self.adjustment.maxGap) * (self.width - self.adjustment.maxGap)
        maxVal = (self.height + self.adjustment.maxGap) * (self.width + self.adjustment.maxGap)
        if minVal < val < maxVal:
            gap = self.height * self.width - val
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samefront,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)

        # Same Side
        val = subject.height * subject.depth
        minVal = (self.height - self.adjustment.maxGap) * (self.depth - self.adjustment.maxGap)
        maxVal = (self.height + self.adjustment.maxGap) * (self.depth + self.adjustment.maxGap)
        if minVal < val < maxVal:
            gap = self.height * self.depth - val
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.sameside,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)

        # Same Footprint
        val = subject.width * subject.depth
        minVal = (self.width - self.adjustment.maxGap) * (self.depth - self.adjustment.maxGap)
        maxVal = (self.width + self.adjustment.maxGap) * (self.depth + self.adjustment.maxGap)
        if minVal < val < maxVal:
            gap = self.width * self.depth - val
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samefootprint,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)

        # Same Surface
        val = (subject.width ** 2) + (subject.depth ** 2) + (subject.height ** 2)
        minVal = ((self.width - self.adjustment.maxGap) ** 2) + ((self.depth - self.adjustment.maxGap) ** 2) + ((self.height - self.adjustment.maxGap) ** 2)
        maxVal = ((self.width + self.adjustment.maxGap) ** 2) + ((self.depth + self.adjustment.maxGap) ** 2) + ((self.height + self.adjustment.maxGap) ** 2)
        if minVal < val < maxVal:
            gap = ((self.width ** 2) + (self.depth ** 2) + (self.height ** 2)) - val
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samesurface,
                object=self,
                delta=2.0 * gap,
                angle=theta
            )
            result.append(relation)

        # Same Volume
        val = subject.width * subject.depth * subject.height
        minVal = (self.width - self.adjustment.maxGap) * (self.depth - self.adjustment.maxGap) * (self.height - self.adjustment.maxGap)
        maxVal = (self.width + self.adjustment.maxGap) * (self.depth + self.adjustment.maxGap) * (self.height + self.adjustment.maxGap)
        if minVal < val < maxVal:
            gap = self.width * self.depth * self.height - val
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.samevolume,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)
            val_distance = (self.position - subject.position).length()
            angle_diff = abs(self.angle - subject.angle)
            if sameWidth and sameDepth and sameHeight and val_distance < self.adjustment.maxGap and angle_diff < self.adjustment.maxAngleDelta:
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.congruent,
                    object=self,
                    delta=gap,
                    angle=theta
                )
                result.append(relation)

        # Same Shape
        if self.shape == subject.shape and self.shape != ObjectShape.unknown and subject.shape != ObjectShape.unknown:
            gap = self.width * self.depth * self.height - val
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.sameshape,
                object=self,
                delta=gap,
                angle=theta
            )
            result.append(relation)

        return result

    # Comparisons Method
    def comparisons(self, subject: 'SpatialObject') -> List['SpatialRelation']:
        result: List['SpatialRelation'] = []
        relation: 'SpatialRelation'
        theta = subject.angle - self.angle
        objVal: float = 0.0
        subjVal: float = 0.0
        diff: float = 0.0
        shorterAdded: bool = False

        # Longer or Shorter Length
        objVal = self.length
        subjVal = subject.length
        diff = subjVal - objVal
        if diff > (self.adjustment.maxGap ** 3):
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.longer,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)
        elif -diff > (self.adjustment.maxGap ** 3):
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.shorter,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)
            shorterAdded = True

        # Taller or Shorter Height
        objVal = self.height
        subjVal = subject.height
        diff = subjVal - objVal
        if diff > self.adjustment.maxGap:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.taller,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)
        elif -diff > self.adjustment.maxGap and not shorterAdded:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.shorter,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)

        # Wider or Thinner Footprint
        if subject.mainDirection() == 2:
            objVal = self.footprint
            subjVal = subject.footprint
            diff = subjVal - objVal
            if diff > (self.adjustment.maxGap ** 2):
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.wider,
                    object=self,
                    delta=diff,
                    angle=theta
                )
                result.append(relation)
            elif -diff > (self.adjustment.maxGap ** 2):
                relation = SpatialRelation(
                    subject=subject,
                    predicate=SpatialPredicate.thinner,
                    object=self,
                    delta=diff,
                    angle=theta
                )
                result.append(relation)

        # Same Volume
        objVal = self.volume
        subjVal = subject.volume
        diff = subjVal - objVal
        if (self.width * self.depth * self.height) - subjVal > (self.adjustment.maxGap ** 3):
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.bigger,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.exceeding,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)
        elif -diff > (self.adjustment.maxGap ** 3):
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.smaller,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)

        # Fitting
        if self.height > subject.height and self.footprint > subject.footprint:
            relation = SpatialRelation(
                subject=subject,
                predicate=SpatialPredicate.fitting,
                object=self,
                delta=diff,
                angle=theta
            )
            result.append(relation)

        return result

    # Sector Relation Method
    def sector(self, subject: 'SpatialObject', nearBy: bool = False, epsilon: float = 0.0) -> 'SpatialRelation':
        center_vector = subject.center - self.center
        center_distance = center_vector.length()
        local_center = self.intoLocal(pt=subject.center)
        center_zone = self.sectorOf(point=local_center, nearBy=nearBy, epsilon=epsilon)
        theta = subject.angle - self.angle
        pred = SpatialPredicate.named(str(center_zone))
        return SpatialRelation(
            subject=subject,
            predicate=pred,
            object=self,
            delta=center_distance,
            angle=theta
        )

    # As Seen Relations Method
    def asseen(self, subject: 'SpatialObject', observer: 'SpatialObject') -> List['SpatialRelation']:
        result: List['SpatialRelation'] = []
        pos_vector = subject.position - self.position
        pos_distance = pos_vector.length()
        radius_sum = self.baseradius + subject.baseradius

        # Check for nearby
        if pos_distance < subject.nearbyRadius() + self.nearbyRadius():
            center_object = observer.intoLocal(pt=self.center)
            center_subject = observer.intoLocal(pt=subject.center)
            if center_subject.z > 0.0 and center_object.z > 0.0:  # both are ahead of observer
                # Turn both by view angle to become normal to observer
                rad = math.atan2(center_object.x, center_object.z)
                rotated = self.rotate(pts=[center_object, center_subject], by=-rad)
                center_object = rotated[0]
                center_subject = rotated[1]
                xgap = float(center_subject.x - center_object.x)
                zgap = float(center_subject.z - center_object.z)

                if abs(xgap) > min(self.width / 2.0, self.depth / 2.0) and abs(zgap) < radius_sum:
                    if xgap > 0.0:
                        relation = SpatialRelation(
                            subject=subject,
                            predicate=SpatialPredicate.seenleft,
                            object=self,
                            delta=abs(xgap),
                            angle=0.0
                        )
                        result.append(relation)
                    else:
                        relation = SpatialRelation(
                            subject=subject,
                            predicate=SpatialPredicate.seenright,
                            object=self,
                            delta=abs(xgap),
                            angle=0.0
                        )
                        result.append(relation)

                if abs(zgap) > min(self.width / 2.0, self.depth / 2.0) and abs(xgap) < radius_sum:
                    if zgap > 0.0:
                        relation = SpatialRelation(
                            subject=subject,
                            predicate=SpatialPredicate.atrear,
                            object=self,
                            delta=abs(zgap),
                            angle=0.0
                        )
                        result.append(relation)
                    else:
                        relation = SpatialRelation(
                            subject=subject,
                            predicate=SpatialPredicate.infront,
                            object=self,
                            delta=abs(zgap),
                            angle=0.0
                        )
                        result.append(relation)

        return result

    # Relate Method
    def relate(
        self,
        subject: 'SpatialObject',
        topology: bool = False,
        similarity: bool = False,
        comparison: bool = False
    ) -> List['SpatialRelation']:
        result: List['SpatialRelation'] = []
        if topology or (self.context and self.context.deduce.topology) or (self.context and self.context.deduce.connectivity):
            result.extend(self.topologies(subject=subject))
        if similarity or (self.context and self.context.deduce.similarity):
            result.extend(self.similarities(subject=subject))
        if comparison or (self.context and self.context.deduce.comparability):
            result.extend(self.comparisons(subject=subject))
        if self.context and self.context.observer and self.context.deduce.visibility:
            result.extend(self.asseen(subject=subject, observer=self.context.observer))
        return result

    # Relation Value Method
    def relationValue(self, relval: str, pre: List[int]) -> float:
        """
        Returns a numeric value for a given relation attribute (e.g., "angle" or "delta")
        for relations with a given predicate. If no matching relation is found or the
        attribute is unrecognized, 0.0 is returned.
        
        Args:
            relval (str): A string in the format "predicate.attribute" (e.g., "near.delta").
            pre (List[int]): A list of indices (or other parameters) used to query relations.
            
        Returns:
            float: The requested relation value, or 0.0 if not found or invalid.
        """
        # Split the input string into predicate and attribute parts.
        list_split = [part.strip() for part in relval.split(".")]
        if len(list_split) != 2 or self.context is None:
            return 0.0

        requested_predicate = list_split[0]  # e.g., "far" or "near"
        requested_attribute = list_split[1]  # e.g., "delta" or "angle"
        result_val: float = 0.0

        for i in pre:
            if self.context:
                # Retrieve relations for the given index and predicate.
                # (Note: Make sure that your context’s relationsWith() method
                #  filters on the predicate correctly, or else you need to check it here.)
                rels = self.context.relationsWith(i, predicate=requested_predicate)
                for rel in rels:
                    # Only use the relation if it both belongs to self and
                    # its predicate matches the requested predicate.
                    if rel.subject == self and rel.predicate.value == requested_predicate:
                        if requested_attribute == "angle":
                            result_val = rel.angle
                        elif requested_attribute == "delta":
                            result_val = rel.delta
                        else:
                            # Unknown attribute; return 0.0 per test expectations.
                            result_val = 0.0
                        # If a matching relation is found, you can break out early.
                        return result_val

        return result_val

    
    def rotate(self, pts: List[Vector3], by: float) -> List[Vector3]:
        """
        Rotates a list of Vector3 points around the Y-axis by the specified angle.

        Args:
            pts (List[Vector3]): The list of points to rotate.
            by_angle (float): The rotation angle in radians.

        Returns:
            List[Vector3]: A new list of rotated points.
        """
        result = []
        rotsin = math.sin(by)
        rotcos = math.cos(by)

        for pt in pts:
            new_x = pt.x * rotcos - pt.z * rotsin
            new_z = pt.x * rotsin + pt.z * rotcos
            # Y remains unchanged during Y-axis rotation
            rotated_pt = Vector3(x=new_x, y=pt.y, z=new_z)
            result.append(rotated_pt)

        return result

    # Visualization Functions
    """
    def bboxCube(self, color: Any) -> 'SCNNode':
        name = self.id if not self.label else self.label
        group = SCNNode()
        group.name = self.id
        box = SCNBox(width=self.width, height=self.height, length=self.depth, chamferRadius=0.0)
        box.firstMaterial.diffuse.contents = color
        box.firstMaterial.transparency = 1.0 - color.alpha
        boxNode = SCNNode(geometry=box)
        group.addChildNode(boxNode)

        # Set name at front
        text = SCNText(string=name, extrusionDepth=0.0)
        text.firstMaterial.diffuse.contents = color
        text.firstMaterial.lightingModel = .constant
        textNode = SCNNode(geometry=text)
        fontSize = 0.005
        min_bound, max_bound = textNode.boundingBox
        textNode.position.x = -((max_bound.x - min_bound.x) / 2.0 * fontSize)
        textNode.position.y = -self.height * 0.48
        textNode.position.z = self.depth / 2.0 + 0.2
        textNode.renderingOrder = 1
        textNode.eulerAngles.x = -math.pi / 2.0
        textNode.scale = Vector3(fontSize, fontSize, fontSize)
        group.addChildNode(textNode)

        group.eulerAngles.y = self.angle
        group.position = self.center
        return group

    def nearbySphere(self) -> 'SCNNode':
        r = self.nearbyRadius()
        sphere = SCNSphere(radius=r)
        sphere.firstMaterial.diffuse.contents = (0.1, 0.1, 0.1, 0.5)  # CGColor(gray: 0.1, alpha: 0.5)
        sphere.firstMaterial.transparency = 0.5
        node = SCNNode(geometry=sphere)
        node.name = f"Nearby sphere of {self.label if self.label else self.id}"
        node.position = self.center
        return node

    def sectorCube(self, sector: BBoxSector = BBoxSector.i, withLabel: bool = False) -> 'SCNNode':
        dims = self.sectorLenghts(sector)
        box = SCNBox(width=dims.x, height=dims.y, length=dims.z, chamferRadius=0.0)
        box.firstMaterial.diffuse.contents = (0.1, 0.1, 0.1, 0.5)  # CGColor(gray: 0.1, alpha: 0.5)
        box.firstMaterial.transparency = 0.5
        node = SCNNode(geometry=box)
        node.name = f"{sector.description} sector"

        shift = Vector3()
        if SpatialTerms.o in sector:
            shift.y = (self.height + dims.y) / 2.0
        elif SpatialTerms.u in sector:
            shift.y = (-self.height - dims.y) / 2.0

        if SpatialTerms.r in sector:
            shift.x = (-self.width - dims.x) / 2.0
        elif SpatialTerms.l in sector:
            shift.x = (self.width + dims.x) / 2.0

        if SpatialTerms.a in sector:
            shift.z = (self.depth + dims.z) / 2.0
        elif SpatialTerms.b in sector:
            shift.z = (-self.depth - dims.z) / 2.0

        node.position = self.center + shift

        if withLabel:
            text = SCNText(string=str(sector), extrusionDepth=0.0)
            text.firstMaterial.diffuse.contents = (1.0, 1.0, 0.0, 0.0)  # CGColor(red: 1.0, green: 1.0, blue: 0.0, alpha: 0.0)
            text.firstMaterial.lightingModel = .constant
            textNode = SCNNode(geometry=text)
            fontSize = 0.01
            min_bound, max_bound = textNode.boundingBox
            textNode.position.x = -((max_bound.x - min_bound.x) / 2.0 * fontSize)
            textNode.position.y = -0.2  # Adjust as needed
            textNode.position.z = 0.0
            textNode.renderingOrder = 1
            textNode.scale = Vector3(fontSize, fontSize, fontSize)
            node.addChildNode(textNode)

        return node

    def pointNodes(self, pts: Optional[List[Vector3]] = None) -> 'SCNNode':
        points = self.points() if not pts else pts
        group = SCNNode()
        group.name = f"BBox corners of {self.label if self.label else self.id}"
        for point in points:
            geometry = SCNSphere(radius=0.01)
            geometry.firstMaterial.diffuse.contents = (0.0, 1.0, 0.0, 0.0)  # CGColor(red: 0.0, green: 1.0, blue: 0.0, alpha: 0.0)
            node = SCNNode(geometry=geometry)
            node.position = point
            group.addChildNode(node)
        return group

    @staticmethod
    def export3D(to_url: str, nodes: List['SCNNode']):
        scene = SCNScene()
        for node in nodes:
            scene.rootNode.addChildNode(node)
        scene.write(to=to_url, options={}, delegate=None, progressHandler=None)

    # ... [End of the SpatialObject class]
    """
    