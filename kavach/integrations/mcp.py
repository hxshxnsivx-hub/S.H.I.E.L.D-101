"""MCP integration (District D1).

An MCP server receives tool calls as (name, arguments) — Kavach plugs in right
there, sanitising arguments before your tool runs. Version-agnostic: it wraps
the stable name+arguments entry point, so it works across MCP SDK versions and
with any server implementation. Sync and async handlers supported.

    from kavach.integrations.mcp import guard_call_tool
    call_tool = guard_call_tool(kav, call_tool)   # wrap your dispatcher
"""
from __future__ import annotations

import functools
import inspect


def sanitize_arguments(kav, name: str, arguments: dict | None, destination: str | None = None):
    """Return (sanitised_arguments, GuardResult) for an MCP tool call."""
    gr = kav.guard_arguments(destination or name, dict(arguments or {}))
    return gr.sanitized, gr


def guard_call_tool(kav, call_tool, destination: str | None = None):
    """Wrap an MCP server's ``call_tool(name, arguments)`` dispatcher."""
    if inspect.iscoroutinefunction(call_tool):
        @functools.wraps(call_tool)
        async def aw(name, arguments=None):
            safe, _ = sanitize_arguments(kav, name, arguments, destination)
            return await call_tool(name, safe)
        return aw

    @functools.wraps(call_tool)
    def w(name, arguments=None):
        safe, _ = sanitize_arguments(kav, name, arguments, destination)
        return call_tool(name, safe)
    return w


def guard_tool_fn(kav, fn, destination: str | None = None):
    """Wrap a single MCP tool function (keyword arguments)."""
    dest = destination or getattr(fn, "__name__", "tool")
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def aw(**kwargs):
            gr = kav.guard_arguments(dest, kwargs)
            return await fn(**gr.sanitized)
        return aw

    @functools.wraps(fn)
    def w(**kwargs):
        gr = kav.guard_arguments(dest, kwargs)
        return fn(**gr.sanitized)
    return w
