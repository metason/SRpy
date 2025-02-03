# tests/BBoxSector_test.py

import unittest
from src.BBoxSector import BBoxSector, BBoxSectorFlags

class TestBBoxSector(unittest.TestCase):
    def test_individual_flags(self):
        for flag in BBoxSectorFlags:
            if flag == BBoxSectorFlags.none:
                continue
            sector = BBoxSector(flag)
            self.assertEqual(str(sector), BBoxSector.debug_descriptions.get(flag, "".join([name for name, member in BBoxSectorFlags.__members__.items() if member == flag])))

    def test_composite_flags(self):
        composite_flags = [
            BBoxSectorFlags.al,
            BBoxSectorFlags.ar,
            BBoxSectorFlags.bl,
            BBoxSectorFlags.br,
            # ... [Add all composite flags as needed] ...
        ]
        for flag in composite_flags:
            sector = BBoxSector(flag)
            self.assertEqual(str(sector), BBoxSector.debug_descriptions.get(flag, "unknown"))

    def test_invalid_combination(self):
        sector = BBoxSector()
        sector.insert(BBoxSectorFlags.a)
        sector.insert(BBoxSectorFlags.b)
        sector.insert(BBoxSectorFlags.l)
        self.assertEqual(str(sector), "abl")

    def test_str_representation_invalid(self):
        sector = BBoxSector()
        sector.insert(BBoxSectorFlags.a)
        sector.insert(BBoxSectorFlags.b)
        sector.insert(BBoxSectorFlags.l)
        sector.insert(BBoxSectorFlags.r)
        self.assertEqual(str(sector), "ablr")

    def test_no_sector(self):
        sector = BBoxSector()
        self.assertEqual(str(sector), "no sector")

    def test_inside_sector(self):
        sector = BBoxSector(BBoxSectorFlags.i)
        self.assertEqual(str(sector), "i")
        self.assertEqual(sector.divergencies(), 0)

    def test_multiple_flags(self):
        sector = BBoxSector()
        sector.insert(BBoxSectorFlags.a)
        sector.insert(BBoxSectorFlags.l)
        sector.insert(BBoxSectorFlags.o)
        self.assertEqual(str(sector), "alo")
        self.assertEqual(sector.divergencies(), 3)

    # ... [Additional tests as needed] ...

# Run the tests
if __name__ == '__main__':
    unittest.main()
