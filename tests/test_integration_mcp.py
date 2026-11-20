"""MCP integration test (District D1). Skipped if mcp isn't installed."""
import importlib.util
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_HAS_MCP = importlib.util.find_spec("mcp") is not None


@unittest.skipUnless(_HAS_MCP, "mcp not installed")
class TestMCP(unittest.TestCase):
    def test_guard_call_tool(self):
        from kavach import Kavach, Trust
        from kavach.integrations.mcp import guard_call_tool

        received = {}

        def call_tool(name, arguments):
            received.update(arguments)
            return "ok"

        kav = Kavach(trust={"push": Trust.UNTRUSTED})
        guarded = guard_call_tool(kav, call_tool)
        guarded("push", {"summary": "pay card 4111111111111111"})
        self.assertNotIn("4111111111111111", received["summary"])
        self.assertEqual(len(kav.audit), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
