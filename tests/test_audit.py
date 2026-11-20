"""Audit plane tests (District D5)."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import Kavach, Trust  # noqa: E402
from kavach import validators as v  # noqa: E402
from kavach.audit import AuditLog  # noqa: E402


def _ev(status="sanitized", dest="x"):
    return {"status": status, "destination": dest,
            "entities": [{"cls": "AADHAAR", "action": "tokenize"}]}


class TestAudit(unittest.TestCase):
    def test_chain_verifies(self):
        log = AuditLog()
        for _ in range(3):
            log.record(_ev())
        self.assertEqual(len(log), 3)
        ok, bad = log.verify()
        self.assertTrue(ok)
        self.assertIsNone(bad)

    def test_tamper_detected(self):
        log = AuditLog()
        log.record(_ev("clean", "a"))
        log.record(_ev("blocked_parts", "b"))
        log.entries()[0].evidence["destination"] = "tampered"
        ok, bad = log.verify()
        self.assertFalse(ok)
        self.assertEqual(bad, 0)

    def test_sdk_auto_records(self):
        base = "23456789012"
        aad = base + v.verhoeff_checksum(base)
        kav = Kavach(trust={"crm": Trust.UNTRUSTED})
        kav.guard(f"Aadhaar {aad}, OTP 123456", "crm")
        self.assertEqual(len(kav.audit), 1)
        rep = kav.audit.report()
        self.assertTrue(rep["chain_intact"])
        self.assertEqual(rep["events"], 1)
        self.assertGreaterEqual(rep["reportable_events"], 1)  # OTP block -> reportable

    def test_persistence_roundtrip_no_raw(self):
        base = "23456789012"
        aad = base + v.verhoeff_checksum(base)
        d = tempfile.mkdtemp()
        path = os.path.join(d, "audit.jsonl")
        kav = Kavach(trust={"crm": Trust.UNTRUSTED}, audit=AuditLog(path))
        kav.guard(f"Aadhaar {aad}, card 4111111111111111", "crm")
        with open(path, encoding="utf-8") as fh:
            blob = fh.read()
        self.assertNotIn(aad, blob)                 # raw value never persisted
        self.assertNotIn("4111111111111111", blob)
        reloaded = AuditLog(path)                    # reopen from disk
        self.assertEqual(len(reloaded), 1)
        ok, _ = reloaded.verify()
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main(verbosity=2)
