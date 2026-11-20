"""Decision engine tests (District D3)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import validators as v  # noqa: E402
from kavach.engine import DecisionEngine  # noqa: E402
from kavach.policy import Trust  # noqa: E402


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.eng = DecisionEngine()
        self.eng.trust.set("ext_api", Trust.UNTRUSTED)
        self.eng.trust.set("core", Trust.TRUSTED)
        base = "23456789012"
        self.aadhaar = base + v.verhoeff_checksum(base)
        self.text = (f"Aadhaar {self.aadhaar}, UPI ravi@okhdfcbank, "
                     f"card 4111111111111111, OTP 123456")

    def test_untrusted_sanitizes(self):
        r = self.eng.process(self.text, "ext_api")
        self.assertNotIn(self.aadhaar, r.sanitized_text)          # tokenized
        self.assertNotIn("4111111111111111", r.sanitized_text)    # tokenized
        self.assertIn("<AADHAAR:tok", r.sanitized_text)
        self.assertIn("[BLOCKED:OTP]", r.sanitized_text)          # secret blocked
        self.assertEqual(r.status, "blocked_parts")

    def test_trusted_allows_but_blocks_secret(self):
        r = self.eng.process(self.text, "core")
        self.assertIn(self.aadhaar, r.sanitized_text)             # allowed to trusted
        self.assertIn("[BLOCKED:OTP]", r.sanitized_text)          # secret never egresses

    def test_unknown_destination_defaults_untrusted(self):
        r = self.eng.process(self.text, "never-seen-tool")
        self.assertNotIn("4111111111111111", r.sanitized_text)

    def test_evidence_has_no_raw_value(self):
        r = self.eng.process(self.text, "ext_api")
        blob = json.dumps(r.evidence)
        self.assertNotIn(self.aadhaar, blob)
        self.assertNotIn("4111111111111111", blob)
        self.assertTrue(r.evidence["evidence_id"].startswith("ev_"))
        self.assertEqual(r.evidence["trust"], "untrusted")

    def test_vault_reversible(self):
        tok = self.eng.vault.tokenize("AADHAAR", self.aadhaar)
        self.assertEqual(self.eng.vault.detokenize(tok), self.aadhaar)


if __name__ == "__main__":
    unittest.main(verbosity=2)
