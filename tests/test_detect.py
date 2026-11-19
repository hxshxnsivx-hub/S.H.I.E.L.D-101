"""Tests for the detection pipeline (District D2)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import validators as v  # noqa: E402
from kavach.detect import Detector  # noqa: E402
from kavach import normalize as nz  # noqa: E402


def classes(text):
    return {d.cls for d in Detector().scan(text)}


class TestDetect(unittest.TestCase):
    def setUp(self):
        self.det = Detector()
        base = "23456789012"
        self.aadhaar = base + v.verhoeff_checksum(base)

    def test_native_structured(self):
        text = (f"Aadhaar {self.aadhaar}, PAN ABCDE1234F, card 4111111111111111, "
                f"IFSC HDFC0001234, UPI ravi@okhdfcbank, GST 27AAPFU0939F1ZV")
        found = classes(text)
        self.assertEqual(
            {"AADHAAR", "PAN", "CARD_PAN", "IFSC", "UPI_VPA", "GSTIN"} - found,
            set(),
            f"missing: {found}",
        )

    def test_number_word_card(self):
        # a card dictated in English words must still be caught
        text = "my card is four one one one one one one one one one one one one one one one"
        dets = [d for d in self.det.scan(text) if d.cls == "CARD_PAN"]
        self.assertTrue(dets)
        self.assertEqual(dets[0].canonical, "4111111111111111")
        self.assertEqual(dets[0].method, "number_word")

    def test_confidence_tiers(self):
        text = f"Aadhaar {self.aadhaar} card 4111111111111111"
        by_cls = {d.cls: d.confidence for d in self.det.scan(text)}
        self.assertGreaterEqual(by_cls["AADHAAR"], 0.99)
        self.assertGreaterEqual(by_cls["CARD_PAN"], 0.9)

    def test_fake_pan_not_detected(self):
        self.assertNotIn("PAN", classes("code ABCD1234F here"))  # malformed PAN

    def test_gmail_not_upi(self):
        self.assertNotIn("UPI_VPA", classes("mail me at ravi@gmail.com"))

    def test_normalize_number_words(self):
        spans = nz.number_word_spans("pay four two to ravi")
        self.assertEqual(spans[0][0], "42")

    def test_email_and_phone(self):
        found = classes("reach me at ravi.k@gmail.com or mobile 9876543210")
        self.assertIn("EMAIL", found)
        self.assertIn("PHONE", found)

    def test_name_ner(self):
        self.assertIn("NAME", classes("My name is Priya and I need help"))
        self.assertIn("NAME", classes("என் பெயர் Karthik"))

    def test_number_word_gated_without_trigger(self):
        # 16 number-words but NO trigger word nearby -> must NOT be flagged
        words = " ".join(["four", "one", "one", "one", "one", "one", "one", "one",
                           "one", "one", "one", "one", "one", "one", "one", "one"])
        self.assertNotIn("CARD_PAN", classes("the lottery picks were " + words))
        # same digits WITH a trigger -> flagged
        self.assertIn("CARD_PAN", classes("your card is " + words))


if __name__ == "__main__":
    unittest.main(verbosity=2)
