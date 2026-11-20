"""Kavach inside a REAL LangChain tool stack.

We use genuine `langchain_core` tools and the real `.invoke()` execution path.
(The LLM's choice of tool/args is simulated here only because calling a hosted
LLM needs an API key; the tool objects and their execution are 100% real.)

    python examples/langchain_integration.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_core.tools import tool

from kavach import Kavach, Trust
from kavach import validators as v
from kavach.integrations.langchain import guard_tools

aadhaar = "23456789012" + v.verhoeff_checksum("23456789012")


@tool
def create_crm_ticket(summary: str, customer: str) -> str:
    """Create a support ticket in the external CRM."""
    print(f"      >> EXTERNAL CRM receives: summary={summary!r}")
    print(f"                                customer={customer!r}")
    return "T-1001"


@tool
def send_sms(to: str, body: str) -> str:
    """Send an SMS via the external gateway."""
    print(f"      >> SMS GATEWAY receives: to={to!r} body={body!r}")
    return "sent"


# Configure Kavach once and produce guarded versions of the real tools.
kav = Kavach()
safe_tools = guard_tools(
    kav,
    [create_crm_ticket, send_sms],
    trust={"create_crm_ticket": Trust.UNTRUSTED, "send_sms": Trust.UNTRUSTED},
)
safe = {t.name: t for t in safe_tools}

# What a LangChain agent would emit as tool calls (args carry raw PII):
calls = [
    ("create_crm_ticket", {"summary": f"Aadhaar {aadhaar}, card 4111111111111111",
                           "customer": "Priya from Chennai"}),
    ("send_sms", {"to": "9876543210", "body": "OTP 123456 for account 918273645501"}),
]

print("=" * 74)
print("RAW tools (no Kavach) — PII leaks to the external services")
print("=" * 74)
for name, args in calls:
    {"create_crm_ticket": create_crm_ticket, "send_sms": send_sms}[name].invoke(args)

print("\n" + "=" * 74)
print("GUARDED tools (real LangChain .invoke, now routed through Kavach)")
print("=" * 74)
for name, args in calls:
    safe[name].invoke(args)

print("\n" + "=" * 74)
print(f"These are real LangChain StructuredTools: {[t.name for t in safe_tools]}")
print(f"Audit: {len(kav.audit)} events, chain intact = {kav.audit.verify()[0]}")
print("To adopt: hand `safe_tools` to your agent instead of the raw tools. Nothing else changes.")
