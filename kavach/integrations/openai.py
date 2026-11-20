"""OpenAI function-calling integration (District D1).

When an OpenAI model wants to call a function it returns a tool call with
``function.name`` and ``function.arguments`` (a JSON string). Before you run the
matching local function, pass that tool call through Kavach.

    from kavach.integrations.openai import guard_tool_call
    name, safe_args, _ = guard_tool_call(kav, tool_call)
    result = LOCAL_FUNCS[name](**safe_args)   # runs on sanitised arguments
"""
from __future__ import annotations

import json


def _get(obj, key):
    return obj[key] if isinstance(obj, dict) else getattr(obj, key)


def guard_tool_call(kav, tool_call, destination: str | None = None):
    """Guard an OpenAI-style tool call (object or dict).

    Returns (name, sanitised_arguments_dict, GuardResult).
    """
    fn = _get(tool_call, "function")
    name = _get(fn, "name")
    raw = _get(fn, "arguments")
    args = json.loads(raw) if isinstance(raw, str) else dict(raw)
    gr = kav.guard_arguments(destination or name, args)
    return name, gr.sanitized, gr
