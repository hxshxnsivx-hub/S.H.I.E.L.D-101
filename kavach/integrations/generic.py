"""Framework-agnostic tool guard (District D1).

Any agent framework (CrewAI, AutoGen, LlamaIndex, Semantic Kernel, a custom
loop) ultimately runs a tool as a Python callable taking keyword arguments.
``guard_callable`` wraps that callable so its string args are sanitised first —
one helper that covers the long tail of frameworks.

    guarded = guard_callable(kav, my_tool_fn, destination="crm_api")
"""
from __future__ import annotations

from functools import wraps


def guard_callable(kav, fn, destination: str | None = None):
    dest = destination or getattr(fn, "__name__", "tool")

    @wraps(fn)
    def wrapper(**kwargs):
        guarded = kav.guard_arguments(dest, kwargs)
        return fn(**guarded.sanitized)

    return wrapper
