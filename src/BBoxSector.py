# src/BBoxSector.py

from enum import IntFlag
from typing import Any
from src.SpatialPredicate import SpatialPredicate


class BBoxSectorFlags(IntFlag):
    none = 0  # no sector specified
    i = 1 << 0  # i : inside, inner
    a = 1 << 1  # a : ahead
    b = 1 << 2  # b : behind
    l = 1 << 3  # l : left
    r = 1 << 4  # r : right
    o = 1 << 5  # o : over
    u = 1 << 6  # u : under

    # Composite sectors
    al = a | l
    ar = a | r
    bl = b | l
    br = b | r
    ao = a | o
    au = a | u
    bo = b | o
    bu = b | u
    lo = l | o
    lu = l | u
    ro = r | o
    ru = r | u
    alo = a | l | o
    aro = a | r | o
    blo = b | l | o
    bro = b | r | o
    alu = a | l | u
    aru = a | r | u
    blu = b | l | u
    bru = b | r | u


class BBoxSector:
    """
    A mutable class that represents spatial sectors using bitmask flags.
    Mimics Swift's OptionSet behavior.
    """

    # Predefined descriptions for composite and individual sectors
    debug_descriptions = {
        BBoxSectorFlags.i: "i",
        BBoxSectorFlags.a: "a",
        BBoxSectorFlags.b: "b",
        BBoxSectorFlags.l: "l",
        BBoxSectorFlags.r: "r",
        BBoxSectorFlags.o: "o",
        BBoxSectorFlags.u: "u",
        BBoxSectorFlags.al: "al",
        BBoxSectorFlags.ar: "ar",
        BBoxSectorFlags.bl: "bl",
        BBoxSectorFlags.br: "br",
        BBoxSectorFlags.ao: "ao",
        BBoxSectorFlags.au: "au",
        BBoxSectorFlags.bo: "bo",
        BBoxSectorFlags.bu: "bu",
        BBoxSectorFlags.lo: "lo",
        BBoxSectorFlags.lu: "lu",
        BBoxSectorFlags.ro: "ro",
        BBoxSectorFlags.ru: "ru",
        BBoxSectorFlags.alo: "alo",
        BBoxSectorFlags.aro: "aro",
        BBoxSectorFlags.blo: "blo",
        BBoxSectorFlags.bro: "bro",
        BBoxSectorFlags.alu: "alu",
        BBoxSectorFlags.aru: "aru",
        BBoxSectorFlags.blu: "blu",
        BBoxSectorFlags.bru: "bru",
    }

    # Define base flags (individual flags only)
    base_flags = {
        BBoxSectorFlags.i,
        BBoxSectorFlags.a,
        BBoxSectorFlags.b,
        BBoxSectorFlags.l,
        BBoxSectorFlags.r,
        BBoxSectorFlags.o,
        BBoxSectorFlags.u
    }

    def __init__(self, flags=BBoxSectorFlags.none):
        """
        Initialize a BBoxSector instance.

        Args:
            flags (BBoxSectorFlags, optional): Initial sector flags. Defaults to BBoxSectorFlags.none.
        """
        self.flags = flags

    def insert(self, flag: BBoxSectorFlags):
        """
        Insert a sector flag.

        Args:
            flag (BBoxSectorFlags): The flag to insert.
        """
        self.flags |= flag

    def remove(self, flag: BBoxSectorFlags):
        """
        Remove a sector flag.

        Args:
            flag (BBoxSectorFlags): The flag to remove.
        """
        self.flags &= ~flag

    def contains_flag(self, flag: BBoxSectorFlags) -> bool:
        """
        Check if a sector flag is present.

        Args:
            flag (BBoxSectorFlags): The flag to check.

        Returns:
            bool: True if the flag is present, False otherwise.
        """
        return (self.flags & flag) == flag

    def contains(self, flag: BBoxSectorFlags) -> bool:
        """
        Alias for contains_flag to maintain backward compatibility.

        Args:
            flag (BBoxSectorFlags): The flag to check.

        Returns:
            bool: True if the flag is present, False otherwise.
        """
        return self.contains_flag(flag)

    def divergencies(self) -> int:
        """
        Calculate the amount of divergency from the inner zone in all 3 directions.

        Returns:
            int: 0 if the sector includes 'i' (inside), otherwise the number of set bits.
        """
        if self.contains_flag(BBoxSectorFlags.i):
            return 0
        return bin(self.flags.value).count('1')

    def list_base_flags(self):
        """
        List only the base flags present in the sector.
        """
        return [name for name, member in BBoxSectorFlags.__members__.items()
                if member in self.flags and name != 'none' and member in BBoxSector.base_flags]

    def __str__(self) -> str:
        """
        Provide a string representation for the sector.

        Returns:
            str: The descriptive string of the sector.
        """
        # Always list base flags to match test expectations
        flags = self.list_base_flags()
        if flags:
            return '+'.join(flags)
        elif self.flags == BBoxSectorFlags.none:
            return "no sector"
        else:
            # If no base flags are set, but some composite flags are, list them
            # This can happen if only composite flags are set without their base flags
            composite_flags = [name for name, member in BBoxSectorFlags.__members__.items()
                               if member in self.flags and name != 'none' and member not in BBoxSector.base_flags]
            if composite_flags:
                return '+'.join(composite_flags)
            return "no sector"

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another BBoxSector instance.

        Args:
            other (Any): The object to compare.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, BBoxSector):
            return self.flags == other.flags
        return False

    def __repr__(self) -> str:
        """
        Return the official string representation of the sector.

        Returns:
            str: The string representation.
        """
        return f"BBoxSector(flags={self.flags})"

    def __or__(self, other: Any) -> 'BBoxSector':
        """
        Define the behavior of the | operator.

        Args:
            other (BBoxSector or BBoxSectorFlags): The other sector or flag to combine.

        Returns:
            BBoxSector: A new BBoxSector instance with combined flags.
        """
        if isinstance(other, BBoxSector):
            return BBoxSector(self.flags | other.flags)
        elif isinstance(other, BBoxSectorFlags):
            return BBoxSector(self.flags | other)
        else:
            return NotImplemented

    def __ior__(self, other: Any) -> 'BBoxSector':
        """
        Define the behavior of the |= operator.

        Args:
            other (BBoxSector or BBoxSectorFlags): The other sector or flag to combine.

        Returns:
            BBoxSector: The updated BBoxSector instance.
        """
        if isinstance(other, BBoxSector):
            self.flags |= other.flags
            return self
        elif isinstance(other, BBoxSectorFlags):
            self.flags |= other
            return self
        else:
            return NotImplemented

    def __contains__(self, item: Any) -> bool:
        """
        Enable the 'in' operator to check for SpatialPredicate or BBoxSectorFlags.

        Args:
            item (Any): SpatialPredicate or BBoxSectorFlags to check.

        Returns:
            bool: True if the item is present, False otherwise.
        """
        if isinstance(item, SpatialPredicate):
            # Map SpatialPredicate to BBoxSectorFlags
            flag_map = {
                SpatialPredicate.l: BBoxSectorFlags.l,
                SpatialPredicate.r: BBoxSectorFlags.r,
                SpatialPredicate.a: BBoxSectorFlags.a,
                SpatialPredicate.b: BBoxSectorFlags.b,
                SpatialPredicate.o: BBoxSectorFlags.o,
                SpatialPredicate.u: BBoxSectorFlags.u,
                SpatialPredicate.i: BBoxSectorFlags.i,
                SpatialPredicate.al: BBoxSectorFlags.al,
                SpatialPredicate.ar: BBoxSectorFlags.ar,
                SpatialPredicate.bl: BBoxSectorFlags.bl,
                SpatialPredicate.br: BBoxSectorFlags.br,
                SpatialPredicate.ao: BBoxSectorFlags.ao,
                SpatialPredicate.au: BBoxSectorFlags.au,
                SpatialPredicate.bo: BBoxSectorFlags.bo,
                SpatialPredicate.bu: BBoxSectorFlags.bu,
                SpatialPredicate.lo: BBoxSectorFlags.lo,
                SpatialPredicate.lu: BBoxSectorFlags.lu,
                SpatialPredicate.ro: BBoxSectorFlags.ro,
                SpatialPredicate.ru: BBoxSectorFlags.ru,
                SpatialPredicate.alo: BBoxSectorFlags.alo,
                SpatialPredicate.aro: BBoxSectorFlags.aro,
                SpatialPredicate.blo: BBoxSectorFlags.blo,
                SpatialPredicate.bro: BBoxSectorFlags.bro,
                SpatialPredicate.alu: BBoxSectorFlags.alu,
                SpatialPredicate.aru: BBoxSectorFlags.aru,
                SpatialPredicate.blu: BBoxSectorFlags.blu,
                SpatialPredicate.bru: BBoxSectorFlags.bru,
                # Add more mappings as needed
            }
            flag = flag_map.get(item, None)
            if flag is not None:
                return self.contains_flag(flag)
        elif isinstance(item, BBoxSectorFlags):
            return self.contains_flag(item)
        return False


# Example Usage

if __name__ == "__main__":
    # Initialize with a predefined composite sector
    sector = BBoxSector(BBoxSectorFlags.alo)
    print(f"Sector: {sector}")  # Output: Sector: a+l+o
    print(f"Divergencies: {sector.divergencies()}")  # Output: Divergencies: 3

    # Create an empty sector and insert flags
    combined_sector = BBoxSector()
    combined_sector.insert(BBoxSectorFlags.a)
    combined_sector.insert(BBoxSectorFlags.l)
    combined_sector.insert(BBoxSectorFlags.o)
    print(f"Combined Sector: {combined_sector}")  # Output: Combined Sector: a+l+o
    print(f"Divergencies: {combined_sector.divergencies()}")  # Output: Divergencies: 3

    # Initialize with the 'inside' sector
    inner_sector = BBoxSector(BBoxSectorFlags.i)
    print(f"Inner Sector: {inner_sector}")  # Output: Inner Sector: i
    print(f"Divergencies: {inner_sector.divergencies()}")  # Output: Divergencies: 0

    # Initialize with no sector
    no_sector = BBoxSector()
    print(f"No Sector: {no_sector}")  # Output: No Sector: no sector
    print(f"Divergencies: {no_sector.divergencies()}")  # Output: Divergencies: 0

    # Undefined composite sector example
    undefined_sector = BBoxSector()
    undefined_sector.insert(BBoxSectorFlags.a)
    undefined_sector.insert(BBoxSectorFlags.b)
    undefined_sector.insert(BBoxSectorFlags.l)
    undefined_sector.insert(BBoxSectorFlags.r)
    print(f"Undefined Combined Sector: {undefined_sector}")  # Output: Undefined Combined Sector: a+b+l+r
    print(f"Divergencies: {undefined_sector.divergencies()}")  # Output: Divergencies: 4
