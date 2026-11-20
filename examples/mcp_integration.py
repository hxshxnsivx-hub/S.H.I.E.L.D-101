"""Kavach inside an MCP server's tool dispatch.

An MCP server executes tools via call_tool(name, arguments). Kavach wraps that
one entry point so arguments are sanitised before the tool runs.

    python examples/mcp_integration.py
"""
from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import mcp  # noqa: F401  (prove the real MCP SDK is installed)

from kavach import Kavach, Trust
from kavach import validators as v
from kavach.integrations.mcp import guard_call_tool

aadhaar = "23456789012" + v.verhoeff_checksum("23456789012")


async def call_tool(name: str, arguments: dict):
    """Stand-in for the MCP server executing a tool (external side effect)."""
    print(f"      >> MCP tool '{name}' executes with: {arguments}")
    return {"ok": True}


kav = Kavach(trust={"push_to_crm": Trust.UNTRUSTED})
guarded_call_tool = guard_call_tool(kav, call_tool)

args = {"summary": f"Aadhaar {aadhaar}, card 4111111111111111", "note": "OTP 123456"}


async def main():
    print("=" * 74)
    print("RAW MCP call_tool — PII reaches the tool")
    print("=" * 74)
    await call_tool("push_to_crm", args)
    print("\n" + "=" * 74)
    print("GUARDED MCP call_tool (same dispatcher, wrapped by Kavach)")
    print("=" * 74)
    await guarded_call_tool("push_to_crm", args)
    print(f"\naudit: {len(kav.audit)} events, chain intact = {kav.audit.verify()[0]}")


asyncio.run(main())
