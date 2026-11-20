"""SDK / interceptor tests (District D1)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import Kavach, KavachBlocked, Trust  # noqa: E402
from kavach import validators as v  # noqa: E402


class TestSDK(unittest.TestCase):
    def setUp(self):
        base = "23456789012"
        self.aadhaar = base + v.verhoeff_checksum(base)

    def test_guard_arguments_sanitizes(self):
        kav = Kavach(trust={"crm_api": Trust.UNTRUSTED})
        gr = kav.guard_arguments("crm_api", {"note": f"Aadhaar {self.aadhaar}", "amount": 500})
        self.assertNotIn(self.aadhaar, gr.sanitized["note"])
        self.assertIn("<AADHAAR:tok", gr.sanitized["note"])
        self.assertEqual(gr.sanitized["amount"], 500)   # non-string passes through

    def test_block_mode_raises_on_secret(self):
        kav = Kavach(trust={"crm_api": Trust.UNTRUSTED}, mode="block")
        with self.assertRaises(KavachBlocked):
            kav.guard_arguments("crm_api", {"msg": "your OTP is 123456"})

    def test_decorator_sanitizes_tool(self):
        kav = Kavach(trust={"crm_api": Trust.UNTRUSTED})
        received = {}

        @kav.guard_tool(destination="crm_api")
        def create_ticket(note: str, amount: int):
            received["note"] = note
            received["amount"] = amount
            return "ok"

        out = create_ticket(note="pay card 4111111111111111", amount=10)
        self.assertEqual(out, "ok")
        self.assertNotIn("4111111111111111", received["note"])  # tool never saw the card
        self.assertEqual(received["amount"], 10)

    def test_trusted_passthrough(self):
        kav = Kavach(trust={"core": Trust.TRUSTED})
        gr = kav.guard_arguments("core", {"note": f"Aadhaar {self.aadhaar}"})
        self.assertIn(self.aadhaar, gr.sanitized["note"])  # allowed to trusted


if __name__ == "__main__":
    unittest.main(verbosity=2)
