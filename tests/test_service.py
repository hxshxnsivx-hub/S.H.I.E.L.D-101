"""Service core + metrics tests (District D8/D5).

Tests the plain core (do_*), which needs no running server or FastAPI.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import validators as v  # noqa: E402
from kavach.service import app as svc  # noqa: E402


class TestService(unittest.TestCase):
    def test_do_guard_untrusted_sanitises(self):
        aad = "23456789012" + v.verhoeff_checksum("23456789012")
        out = svc.do_guard(f"Aadhaar {aad}, OTP 123456", "crm_external_api")
        self.assertNotIn(aad, out["sanitized"])
        self.assertEqual(out["status"], "blocked_parts")
        self.assertTrue(out["evidence_id"].startswith("ev_"))

    def test_do_guard_arguments(self):
        gr = svc.do_guard_arguments("crm_external_api", {"note": "card 4111111111111111", "n": 5})
        self.assertNotIn("4111111111111111", gr["sanitized"]["note"])
        self.assertEqual(gr["sanitized"]["n"], 5)

    def test_metrics_increment(self):
        before = svc._METRICS["guard_total"]
        svc.do_guard("hello", "core_banking")
        self.assertEqual(svc._METRICS["guard_total"], before + 1)
        self.assertIn("kavach_guard_total", svc.metrics_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
