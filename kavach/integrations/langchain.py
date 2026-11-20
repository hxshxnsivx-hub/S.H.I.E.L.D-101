"""LangChain integration (District D1).

Wrap any LangChain tool so its arguments are sanitised by Kavach *before* the
tool runs — the agent, the LLM, and the rest of the graph are unchanged. You
hand the agent guarded tools instead of raw ones.

    from kavach import Kavach, Trust
    from kavach.integrations.langchain import guard_tools

    kav = Kavach(trust={"create_ticket": Trust.UNTRUSTED})
    safe_tools = guard_tools(kav, [create_ticket, send_sms])
    agent = create_react_agent(llm, safe_tools)   # same as before, now guarded
"""
from __future__ import annotations


def guard_tool(kav, tool, destination: str | None = None):
    """Return a LangChain tool whose string args are sanitised before it runs."""
    from langchain_core.tools import StructuredTool

    dest = destination or tool.name
    orig = tool.func  # underlying python callable

    def wrapped(**kwargs):
        guarded = kav.guard_arguments(dest, kwargs)
        return orig(**guarded.sanitized)

    return StructuredTool.from_function(
        func=wrapped,
        name=tool.name,
        description=tool.description,
        args_schema=getattr(tool, "args_schema", None),
    )


def guard_tools(kav, tools, trust=None):
    """Guard a list of tools. ``trust`` optionally maps tool name -> Trust level."""
    from .. import Trust  # noqa: F401  (kept for callers' convenience)

    if trust:
        for name, level in trust.items():
            kav.set_trust(name, level)
    return [guard_tool(kav, t) for t in tools]
