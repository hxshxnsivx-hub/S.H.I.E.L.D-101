"""Voice hooks + async/batch tests (District D1)."""
import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import Kavach, Trust  # noqa: E402
from kavach.integrations.voice import guard_stt, guard_tts  # noqa: E402


class TestVoice(unittest.TestCase):
    def setUp(self):
        self.kav = Kavach(trust={"crm": Trust.UNTRUSTED})

    def test_stt_sanitises_before_tool(self):
        out = guard_stt(self.kav, "pay with card 4111111111111111", "crm")
        self.assertNotIn("4111111111111111", out)

    def test_tts_never_speaks_secret(self):
        out = guard_tts(self.kav, "your OTP is 123456 sir")
        self.assertIn("[BLOCKED:OTP]", out)


class TestAsyncBatch(unittest.TestCase):
    def test_aguard(self):
        kav = Kavach(trust={"crm": Trust.UNTRUSTED})
        r = asyncio.run(kav.aguard("card 4111111111111111", "crm"))
        self.assertNotIn("4111111111111111", r.sanitized_text)

    def test_batch(self):
        kav = Kavach(trust={"crm": Trust.UNTRUSTED})
        out = kav.guard_batch([("card 4111111111111111", "crm"), ("name Priya", "crm")])
        self.assertEqual(len(out), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
