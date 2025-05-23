# SpatialRelation.py

from typing import Any
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .SpatialObject import SpatialObject  # Prevents circular import at runtime

from .SpatialPredicate import SpatialPredicate, SpatialTerms


class SpatialRelation:
    """
    Represents a spatial relation as a triple: subject - predicate - object.
    """

    def __init__(
        self,
        subject: "SpatialObject",
        predicate: SpatialPredicate,
        object: "SpatialObject",
        delta: float = 0.0,
        angle: float = 0.0,
    ):
        """
        Initializes a SpatialRelation instance.

        Args:
            subject (SpatialObject): The target subject.
            predicate (SpatialPredicate): The spatial predicate matching spatial condition and max deviation.
            object (SpatialObject): The reference object.
            delta (float, optional): Difference of predicate value between subject and object, e.g., distance. Defaults to 0.0.
            angle (float, optional): Angle deviation of object direction in radians. Defaults to 0.0.
        """
        self.subject: "SpatialObject" = subject
        self.predicate: SpatialPredicate = predicate
        self.object: "SpatialObject" = object
        self.delta: float = delta
        self.angle: float = angle

    @property
    def yaw(self) -> float:
        """
        Calculates the angle deviation in degrees.

        Returns:
            float: Angle deviation in degrees.
        """
        return self.angle * 180.0 / math.pi

    @property
    def subject_id(self) -> str:
        """
        Retrieves the ID of the subject.

        Returns:
            str: The subject's ID.
        """
        return self.subject.id

    @property
    def object_id(self) -> str:
        """
        Retrieves the ID of the object.

        Returns:
            str: The object's ID.
        """
        return self.object.id

    def desc(self) -> str:
        """
        Generates a descriptive string for the spatial relation.

        The format is:
        "<subject> <predicate> <object> (<predicate_raw_value> Δ:<delta> 𝜶:<yaw>°)"

        Returns:
            str: The descriptive string of the spatial relation.
        """
        # Determine subject representation
        if self.subject.label:
            subject_str = self.subject.label
        elif self.subject.type:
            subject_str = self.subject.type
        else:
            subject_str = self.subject.id

        # Get predicate as verb + preposition using SpatialTerms
        predicate_str = SpatialTerms.termWithVerbAndPreposition(self.predicate)

        # Determine object representation
        if self.object.label:
            object_str = self.object.label
        elif self.object.type:
            object_str = self.object.type
        else:
            object_str = self.object.id

        # Format the description string
        description = (
            f"{subject_str} {predicate_str} {object_str} "
            f"({self.predicate.value} Δ:{self.delta:.2f} 𝜶:{self.yaw:.1f}°)"
        )
        return description

    def __repr__(self) -> str:
        """
        Returns the official string representation of the SpatialRelation.

        Returns:
            str: Official string representation.
        """
        return (
            f"SpatialRelation(subject={self.subject}, "
            f"predicate={self.predicate}, object={self.object}, "
            f"delta={self.delta}, angle={self.angle})"
        )
