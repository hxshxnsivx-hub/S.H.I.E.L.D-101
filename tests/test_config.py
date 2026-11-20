"""Deployment config tests (District D8)."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach.config import build_policy, build_trust, load_config  # noqa: E402
from kavach.policy import Trust  # noqa: E402


class TestConfig(unittest.TestCase):
    def test_load_and_build(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "c.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"trust": {"x": "trusted", "y": "untrusted"},
                       "policy": {"version": "v2", "escalate_below": 0.8}}, fh)
        cfg = load_config(p)
        tr = build_trust(cfg)
        self.assertEqual(tr.level("x"), Trust.TRUSTED)
        self.assertEqual(tr.level("y"), Trust.UNTRUSTED)
        self.assertEqual(tr.level("unknown"), Trust.UNKNOWN)
        pol = build_policy(cfg)
        self.assertEqual(pol.escalate_below, 0.8)
        self.assertEqual(pol.policy_version, "v2")

    def test_defaults(self):
        self.assertEqual(load_config("/no/such/file"), {})
        self.assertEqual(build_policy({}).escalate_below, 0.6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
