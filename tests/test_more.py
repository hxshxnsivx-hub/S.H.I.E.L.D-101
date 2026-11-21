"""More languages + generic adapter tests (brain / hands)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import Kavach, Trust  # noqa: E402
from kavach import normalize as nz  # noqa: E402
from kavach.integrations.generic import guard_callable  # noqa: E402


class TestLanguages(unittest.TestCase):
    def test_telugu_number_words(self):
        # "ఒకటి రెండు" = 1 2
        spans = nz.number_word_spans("రవి ఒకటి రెండు మూడు")
        self.assertEqual(spans[0][0], "123")

    def test_bengali_number_words(self):
        spans = nz.number_word_spans("এক দুই তিন")
        self.assertEqual(spans[0][0], "123")


class TestGenericAdapter(unittest.TestCase):
    def test_guard_callable(self):
        kav = Kavach(trust={"crm": Trust.UNTRUSTED})
        seen = {}

        def my_tool(note, n):
            seen["note"] = note
            seen["n"] = n
            return "ok"

        guarded = guard_callable(kav, my_tool, destination="crm")
        out = guarded(note="card 4111111111111111", n=3)
        self.assertEqual(out, "ok")
        self.assertNotIn("4111111111111111", seen["note"])
        self.assertEqual(seen["n"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
