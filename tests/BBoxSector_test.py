# tests/BBoxSector_test.py

import unittest
from src.BBoxSector import BBoxSector, BBoxSectorFlags

class TestBBoxSector(unittest.TestCase):
    def test_str_representation_basic(self):
        """Test the string representation of basic sectors."""
        self.assertEqual(str(BBoxSector.i), "i")
        self.assertEqual(str(BBoxSector.a), "a")
        self.assertEqual(str(BBoxSector.b), "b")
        self.assertEqual(str(BBoxSector.l), "l")
        self.assertEqual(str(BBoxSector.r), "r")
        self.assertEqual(str(BBoxSector.o), "o")
        self.assertEqual(str(BBoxSector.u), "u")

    def test_str_representation_composite(self):
        """Test the string representation of composite sectors."""
        self.assertEqual(str(BBoxSector.al), "al")
        self.assertEqual(str(BBoxSector.ar), "ar")
        self.assertEqual(str(BBoxSector.bl), "bl")
        self.assertEqual(str(BBoxSector.br), "br")
        self.assertEqual(str(BBoxSector.ao), "ao")
        self.assertEqual(str(BBoxSector.au), "au")
        self.assertEqual(str(BBoxSector.bo), "bo")
        self.assertEqual(str(BBoxSector.bu), "bu")
        self.assertEqual(str(BBoxSector.lo), "lo")
        self.assertEqual(str(BBoxSector.lu), "lu")
        self.assertEqual(str(BBoxSector.ro), "ro")
        self.assertEqual(str(BBoxSector.ru), "ru")
        self.assertEqual(str(BBoxSector.alo), "alo")
        self.assertEqual(str(BBoxSector.aro), "aro")
        self.assertEqual(str(BBoxSector.blo), "blo")
        self.assertEqual(str(BBoxSector.bro), "bro")
        self.assertEqual(str(BBoxSector.alu), "alu")
        self.assertEqual(str(BBoxSector.aru), "aru")
        self.assertEqual(str(BBoxSector.blu), "blu")
        self.assertEqual(str(BBoxSector.bru), "bru")

    def test_str_representation_invalid(self):
        """Test the string representation of an undefined sector."""
        # Create a combined sector not predefined
        undefined_sector = BBoxSector()  # Start with none
        undefined_sector.insert(BBoxSectorFlags.a)
        undefined_sector.insert(BBoxSectorFlags.b)
        undefined_sector.insert(BBoxSectorFlags.l)
        undefined_sector.insert(BBoxSectorFlags.r)
        self.assertEqual(str(undefined_sector), "a+b+l+r")

    def test_divergencies_inside(self):
        """Test divergencies method for the 'inside' sector."""
        self.assertEqual(BBoxSector.i.divergencies(), 0)

    def test_divergencies_basic(self):
        """Test divergencies method for basic sectors."""
        self.assertEqual(BBoxSector.a.divergencies(), 1)
        self.assertEqual(BBoxSector.b.divergencies(), 1)
        self.assertEqual(BBoxSector.l.divergencies(), 1)
        self.assertEqual(BBoxSector.r.divergencies(), 1)
        self.assertEqual(BBoxSector.o.divergencies(), 1)
        self.assertEqual(BBoxSector.u.divergencies(), 1)

    def test_divergencies_composite(self):
        """Test divergencies method for composite sectors."""
        self.assertEqual(BBoxSector.al.divergencies(), 2)
        self.assertEqual(BBoxSector.ar.divergencies(), 2)
        self.assertEqual(BBoxSector.bl.divergencies(), 2)
        self.assertEqual(BBoxSector.br.divergencies(), 2)
        self.assertEqual(BBoxSector.ao.divergencies(), 2)
        self.assertEqual(BBoxSector.au.divergencies(), 2)
        self.assertEqual(BBoxSector.bo.divergencies(), 2)
        self.assertEqual(BBoxSector.bu.divergencies(), 2)
        self.assertEqual(BBoxSector.lo.divergencies(), 2)
        self.assertEqual(BBoxSector.lu.divergencies(), 2)
        self.assertEqual(BBoxSector.ro.divergencies(), 2)
        self.assertEqual(BBoxSector.ru.divergencies(), 2)
        self.assertEqual(BBoxSector.alo.divergencies(), 3)
        self.assertEqual(BBoxSector.aro.divergencies(), 3)
        self.assertEqual(BBoxSector.blo.divergencies(), 3)
        self.assertEqual(BBoxSector.bro.divergencies(), 3)
        self.assertEqual(BBoxSector.alu.divergencies(), 3)
        self.assertEqual(BBoxSector.aru.divergencies(), 3)
        self.assertEqual(BBoxSector.blu.divergencies(), 3)
        self.assertEqual(BBoxSector.bru.divergencies(), 3)

    def test_divergencies_none(self):
        """Test divergencies method for the 'none' sector."""
        self.assertEqual(BBoxSector.none.divergencies(), 0)

    def test_composite_sector_flags(self):
        """Test that composite sectors have the correct flags set."""
        self.assertTrue(BBoxSector.al.contains(BBoxSectorFlags.a))
        self.assertTrue(BBoxSector.al.contains(BBoxSectorFlags.l))
        self.assertFalse(BBoxSector.al.contains(BBoxSectorFlags.o))

        self.assertTrue(BBoxSector.alo.contains(BBoxSectorFlags.a))
        self.assertTrue(BBoxSector.alo.contains(BBoxSectorFlags.l))
        self.assertTrue(BBoxSector.alo.contains(BBoxSectorFlags.o))

        self.assertTrue(BBoxSector.bru.contains(BBoxSectorFlags.b))
        self.assertTrue(BBoxSector.bru.contains(BBoxSectorFlags.r))
        self.assertTrue(BBoxSector.bru.contains(BBoxSectorFlags.u))

    def test_composite_sector_values(self):
        """Test that composite sectors have the correct integer values."""
        # Verify that al is a | l
        self.assertEqual(BBoxSector.al.flags, BBoxSectorFlags.a | BBoxSectorFlags.l)
        # Verify that alo is a | l | o
        self.assertEqual(BBoxSector.alo.flags, BBoxSectorFlags.a | BBoxSectorFlags.l | BBoxSectorFlags.o)
        # Verify that bru is b | r | u
        self.assertEqual(BBoxSector.bru.flags, BBoxSectorFlags.b | BBoxSectorFlags.r | BBoxSectorFlags.u)

    def test_none_sector(self):
        """Test the 'none' sector's properties."""
        self.assertEqual(str(BBoxSector.none), "no sector")
        self.assertEqual(BBoxSector.none.divergencies(), 0)

    def test_combined_sectors(self):
        """Test multiple combined sectors and their properties."""
        # Combine sectors using the | operator
        sector = BBoxSector.a | BBoxSector.l
        self.assertEqual(str(sector), "al")
        self.assertEqual(sector.divergencies(), 2)

        sector = BBoxSector.a | BBoxSector.l | BBoxSector.o
        self.assertEqual(str(sector), "alo")
        self.assertEqual(sector.divergencies(), 3)

        sector = BBoxSector.b | BBoxSector.r
        self.assertEqual(str(sector), "br")
        self.assertEqual(sector.divergencies(), 2)

    def test_invalid_combination(self):
        """Test an invalid combination that is not predefined."""
        # Creating an undefined combination: a | b | l
        sector = BBoxSector.a | BBoxSector.b | BBoxSector.l
        self.assertEqual(str(sector), "a+b+l")
        self.assertEqual(sector.divergencies(), 3)

    def test_only_two_flags_set(self):
        """Test sectors with exactly two flags set."""
        sectors = [
            BBoxSector.al,
            BBoxSector.ar,
            BBoxSector.bl,
            BBoxSector.br,
            BBoxSector.ao,
            BBoxSector.au,
            BBoxSector.bo,
            BBoxSector.bu,
            BBoxSector.lo,
            BBoxSector.lu,
            BBoxSector.ro,
            BBoxSector.ru,
        ]
        for sector in sectors:
            with self.subTest(sector=sector):
                self.assertEqual(sector.divergencies(), 2)
                expected_str = str(sector)
                self.assertTrue(len(expected_str) >= 2)  # e.g., "al"

    def test_three_flags_set(self):
        """Test sectors with exactly three flags set."""
        sectors = [
            BBoxSector.alo,
            BBoxSector.aro,
            BBoxSector.blo,
            BBoxSector.bro,
            BBoxSector.alu,
            BBoxSector.aru,
            BBoxSector.blu,
            BBoxSector.bru,
        ]
        for sector in sectors:
            with self.subTest(sector=sector):
                self.assertEqual(sector.divergencies(), 3)
                expected_str = str(sector)
                self.assertTrue(len(expected_str) >= 3)  # e.g., "alo"

if __name__ == '__main__':
    unittest.main()
