from enum import IntFlag
import numpy as np

class BBoxSector(IntFlag):
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

    def divergencies(self) -> int:
        """
        Calculate the amount of divergency from the inner zone in all 3 directions.

        Returns:
            int: 0 if the sector includes 'i' (inside), otherwise the number of set bits.
        """
        if self & BBoxSector.i:
            return 0
        return bin(self).count('1')

    def __str__(self) -> str:
        """
        Provide a string representation for the sector.

        Returns:
            str: The descriptive string of the sector.
        """
        # Predefined descriptions for composite and individual sectors
        debug_descriptions = {
            BBoxSector.i: "i",
            BBoxSector.a: "a",
            BBoxSector.b: "b",
            BBoxSector.l: "l",
            BBoxSector.r: "r",
            BBoxSector.o: "o",
            BBoxSector.u: "u",
            BBoxSector.al: "al",
            BBoxSector.ar: "ar",
            BBoxSector.bl: "bl",
            BBoxSector.br: "br",
            BBoxSector.ao: "ao",
            BBoxSector.au: "au",
            BBoxSector.bo: "bo",
            BBoxSector.bu: "bu",
            BBoxSector.lo: "lo",
            BBoxSector.lu: "lu",
            BBoxSector.ro: "ro",
            BBoxSector.ru: "ru",
            BBoxSector.alo: "alo",
            BBoxSector.aro: "aro",
            BBoxSector.blo: "blo",
            BBoxSector.bro: "bro",
            BBoxSector.alu: "alu",
            BBoxSector.aru: "aru",
            BBoxSector.blu: "blu",
            BBoxSector.bru: "bru",
        }

        if self in debug_descriptions:
            return debug_descriptions[self]
        elif self == BBoxSector.none:
            return "no sector"
        else:
            # List all individual flags set
            flags = [name for name, member in BBoxSector.__members__.items()
                     if member in self and name != 'none']
            if flags:
                return '+'.join(flags)
            else:
                return "no sector"

# Example Usage
if __name__ == "__main__":
    sector = BBoxSector.alo
    print(f"Sector: {sector}")  # Output: Sector: alo
    print(f"Divergencies: {sector.divergencies()}")  # Output: Divergencies: 3

    combined_sector = BBoxSector.a | BBoxSector.l | BBoxSector.o
    print(f"Combined Sector: {combined_sector}")  # Output: Combined Sector: alo
    print(f"Divergencies: {combined_sector.divergencies()}")  # Output: Divergencies: 3

    inner_sector = BBoxSector.i
    print(f"Inner Sector: {inner_sector}")  # Output: Inner Sector: i
    print(f"Divergencies: {inner_sector.divergencies()}")  # Output: Divergencies: 0

    no_sector = BBoxSector.none
    print(f"No Sector: {no_sector}")  # Output: No Sector: no sector
    print(f"Divergencies: {no_sector.divergencies()}")  # Output: Divergencies: 0

    # Undefined composite sector example
    undefined_sector = BBoxSector.a | BBoxSector.l | BBoxSector.o | BBoxSector.u
    print(f"Undefined Combined Sector: {undefined_sector}")  # Output: a+l+o+u
    print(f"Divergencies: {undefined_sector.divergencies()}")  # Output: Divergencies: 4
