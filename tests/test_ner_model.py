"""MuRIL NER backend tests (District D2).

The model test is gated behind an env var so the default suite never triggers
a ~900 MB download:  set KAVACH_TEST_NER=1 to run it.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach.detect import Detector  # noqa: E402
from kavach.ner_model import TransformerNER  # noqa: E402


class TestBackendWiring(unittest.TestCase):
    """Runs without the model: a stub backend must flow through the Detector."""

    def test_detector_uses_injected_backend(self):
        class StubNER:
            def detect(self, text):
                i = text.find("Venkatesh")
                return [("NAME", "Venkatesh", i, i + 9, 0.97)] if i >= 0 else []

        det = Detector(ner_backend=StubNER())
        found = det.scan("account holder Venkatesh paid today")
        names = [d for d in found if d.cls == "NAME"]
        self.assertTrue(names)
        self.assertEqual(names[0].method, "ner_model")
        self.assertEqual(names[0].value, "Venkatesh")


class TestUnion(unittest.TestCase):
    """Model + heuristic union: the gazetteer backstops names the model misses."""

    def test_union_recovers_known_name(self):
        class StubNER:
            def detect(self, text):
                i = text.find("Venkatachalapathy")
                return [("NAME", "Venkatachalapathy", i, i + 17, 0.95)] if i >= 0 else []

        det = Detector(ner_backend=StubNER())
        found = {(d.cls, d.value) for d in det.scan("Venkatachalapathy and Ravi are here")}
        self.assertIn(("NAME", "Venkatachalapathy"), found)  # from the model
        self.assertIn(("NAME", "Ravi"), found)               # gazetteer union recovered it

    def test_city_mislabelled_as_person_becomes_address(self):
        class StubNER:
            def detect(self, text):
                i = text.find("Chennai")
                return [("NAME", "Chennai", i, i + 7, 0.9)]

        det = Detector(ner_backend=StubNER())
        found = {(d.cls, d.value) for d in det.scan("shipped from Chennai today")}
        self.assertIn(("ADDRESS", "Chennai"), found)
        self.assertNotIn(("NAME", "Chennai"), found)


@unittest.skipUnless(os.environ.get("KAVACH_TEST_NER"), "set KAVACH_TEST_NER=1 to run the MuRIL model")
class TestMurilModel(unittest.TestCase):
    def test_detects_out_of_gazetteer_name(self):
        ner = TransformerNER()
        self.assertTrue(ner.available, f"model unavailable: {ner.error}")
        det = Detector(ner_backend=ner)
        # 'Venkatachalapathy' is NOT in the heuristic gazetteer
        found = {d.cls for d in det.scan("My name is Venkatachalapathy from Madurai")}
        self.assertIn("NAME", found)


if __name__ == "__main__":
    unittest.main(verbosity=2)
