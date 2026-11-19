"""Tests for the deterministic validator library (District D7).

Run from the repo root:  python -m unittest -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import validators as v  # noqa: E402
from kavach import taxonomy as tx  # noqa: E402


class TestAadhaar(unittest.TestCase):
    def test_generated_checksum_validates(self):
        base = "23456789012"  # 11 digits, does not start 0/1
        full = base + v.verhoeff_checksum(base)
        self.assertTrue(v.is_aadhaar(full))

    def test_flipped_digit_fails(self):
        base = "23456789012"
        full = base + v.verhoeff_checksum(base)
        bad = ("9" if full[5] != "9" else "8")
        corrupted = full[:5] + bad + full[6:]
        self.assertFalse(v.is_aadhaar(corrupted))

    def test_rejects_wrong_length_and_leading_digit(self):
        self.assertFalse(v.is_aadhaar("1234"))
        self.assertFalse(v.is_aadhaar("012345678901"))  # starts with 0
        self.assertFalse(v.is_aadhaar("abcd56789012"))

    def test_tolerates_spaces(self):
        base = "23456789012"
        full = base + v.verhoeff_checksum(base)
        spaced = f"{full[:4]} {full[4:8]} {full[8:]}"
        self.assertTrue(v.is_aadhaar(spaced))


class TestLuhn(unittest.TestCase):
    def test_valid_card(self):
        self.assertTrue(v.luhn_validate("4111111111111111"))  # Visa test number

    def test_invalid_card(self):
        self.assertFalse(v.luhn_validate("4111111111111112"))

    def test_too_short(self):
        self.assertFalse(v.luhn_validate("411111"))


class TestPanIfsc(unittest.TestCase):
    def test_pan(self):
        self.assertTrue(v.is_pan("ABCDE1234F"))
        self.assertFalse(v.is_pan("ABCD1234F"))
        self.assertFalse(v.is_pan("ABCDE12345"))

    def test_ifsc(self):
        self.assertTrue(v.is_ifsc("HDFC0001234"))
        self.assertFalse(v.is_ifsc("HDFCX001234"))  # 5th char must be 0
        self.assertFalse(v.is_ifsc("HDF0001234"))


class TestGstin(unittest.TestCase):
    def test_self_consistent(self):
        prefix = "27AAPFU0939F1Z"  # well-formed 14-char prefix
        full = prefix + v.gstin_checksum(prefix)
        self.assertTrue(v.is_gstin(full))

    def test_known_example(self):
        # Canonical GSTN example; check char should be 'V'.
        self.assertEqual(v.gstin_checksum("27AAPFU0939F1Z"), "V")
        self.assertTrue(v.is_gstin("27AAPFU0939F1ZV"))

    def test_bad_checksum(self):
        self.assertFalse(v.is_gstin("27AAPFU0939F1ZX"))

    def test_bad_structure(self):
        self.assertFalse(v.is_gstin("27AAPFU0939F1Y0"))  # 13th char must be Z


class TestUpiVpa(unittest.TestCase):
    def test_valid_known_psp(self):
        self.assertTrue(v.is_upi_vpa("ravikumar@okhdfcbank"))
        self.assertTrue(v.is_upi_vpa("9876543210@ybl"))

    def test_unknown_psp_strict(self):
        self.assertFalse(v.is_upi_vpa("someone@notarealpsp"))

    def test_unknown_psp_lenient(self):
        self.assertTrue(v.is_upi_vpa("someone@notarealpsp", strict_psp=False))

    def test_not_a_vpa(self):
        # a normal email is not a VPA (PSP handle has no dot)
        self.assertFalse(v.is_upi_vpa("just-an-email@gmail.com", strict_psp=False))
        self.assertFalse(v.is_upi_vpa("nope", strict_psp=False))


class TestRegistry(unittest.TestCase):
    def test_registry_wired(self):
        self.assertEqual(tx.AADHAAR.sensitivity, tx.Sensitivity.S3)
        self.assertEqual(tx.AADHAAR.default_action, tx.Action.TOKENIZE)
        self.assertIn("UPI_VPA", tx.REGISTRY)
        # every named validator actually exists on the module
        for cls in tx.REGISTRY.values():
            if cls.validator:
                self.assertTrue(hasattr(v, cls.validator), f"missing validator {cls.validator}")

    def test_sensitivity_coverage(self):
        groups = {c.group for c in tx.REGISTRY.values()}
        self.assertTrue({"government", "financial", "secret", "biometric"} <= groups)


if __name__ == "__main__":
    unittest.main(verbosity=2)
