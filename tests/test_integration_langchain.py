"""LangChain integration test (District D1).

Skipped if langchain_core isn't installed.
"""
import importlib.util
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_HAS_LC = importlib.util.find_spec("langchain_core") is not None


@unittest.skipUnless(_HAS_LC, "langchain_core not installed")
class TestLangChain(unittest.TestCase):
    def test_guarded_tool_sanitizes_invoke(self):
        from langchain_core.tools import tool

        from kavach import Kavach, Trust
        from kavach.integrations.langchain import guard_tools

        @tool
        def echo(summary: str) -> str:
            """Echo the summary back (stands in for an external call)."""
            return summary

        kav = Kavach(trust={"echo": Trust.UNTRUSTED})
        guarded = guard_tools(kav, [echo])[0]

        self.assertEqual(guarded.name, "echo")  # still a real LangChain tool
        out = guarded.invoke({"summary": "pay card 4111111111111111"})
        self.assertNotIn("4111111111111111", out)   # card never reached the tool body
        self.assertEqual(len(kav.audit), 1)          # recorded


if __name__ == "__main__":
    unittest.main(verbosity=2)
