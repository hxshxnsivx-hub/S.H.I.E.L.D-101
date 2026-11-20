"""OpenAI function-calling integration test (District D1)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kavach import Kavach, Trust  # noqa: E402
from kavach.integrations.openai import guard_tool_call  # noqa: E402


class TestOpenAI(unittest.TestCase):
    def test_guard_tool_call_dict_shape(self):
        kav = Kavach(trust={"f": Trust.UNTRUSTED})
        tc = {"id": "c1", "type": "function",
              "function": {"name": "f", "arguments": json.dumps({"x": "pay card 4111111111111111"})}}
        name, args, gr = guard_tool_call(kav, tc)
        self.assertEqual(name, "f")
        self.assertNotIn("4111111111111111", args["x"])
        self.assertEqual(len(kav.audit), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
