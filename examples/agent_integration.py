"""How Kavach attaches to a REAL agent (the console is just a demo UI).

An AI agent, at runtime, does one risky thing: it calls TOOLS (external APIs,
CRMs, email, payment) with arguments — and those arguments are where the user's
PII leaks to third parties. Kavach intercepts the tool call BEFORE it executes.

You do NOT rewrite Kavach per agent. You wire it in at ONE place (the tool
dispatch) and declare which destinations are trusted. Two styles below.

    python examples/agent_integration.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from kavach import Kavach, Trust      # the product
from kavach import validators as v

aadhaar = "23456789012" + v.verhoeff_checksum("23456789012")


# ---- the agent's real tools (these would POST to external services) --------
def create_crm_ticket(summary: str, customer: str):
    print(f"      >> EXTERNAL CRM receives: summary={summary!r}")
    print(f"                                customer={customer!r}")
    return {"ticket_id": "T-1001"}


def send_sms(to: str, body: str):
    print(f"      >> SMS GATEWAY receives: to={to!r} body={body!r}")
    return {"sent": True}


TOOLS = {"create_crm_ticket": create_crm_ticket, "send_sms": send_sms}

# ---- Kavach configured ONCE: which tool destinations are (un)trusted -------
kav = Kavach(trust={
    "create_crm_ticket": Trust.UNTRUSTED,   # third-party SaaS
    "send_sms": Trust.UNTRUSTED,            # external gateway
}, mode="sanitize")


# ===========================================================================
# STYLE A — guard at the agent's dispatch layer (works with ANY framework)
# This single function is the only integration point. LangChain, an MCP server,
# OpenAI function-calling, a custom loop — they all end up calling a tool by
# name with an arguments dict. Wrap that one call.
# ===========================================================================
def agent_dispatch(tool_name: str, arguments: dict):
    guarded = kav.guard_arguments(tool_name, arguments)       # <-- intercept
    print(f"   [kavach] {tool_name}: status={guarded.status}")
    return TOOLS[tool_name](**guarded.sanitized)              # run with SAFE args


# What an LLM agent "decided" to do this turn (raw PII in the tool calls):
agent_plan = [
    ("create_crm_ticket", {
        "summary": f"Customer complaint. Aadhaar {aadhaar}, card 4111111111111111.",
        "customer": "Priya from Chennai",
    }),
    ("send_sms", {"to": "9876543210", "body": "Your OTP is 123456 for account 918273645501."}),
]

print("=" * 74)
print("STYLE A — Kavach wired into the agent's tool dispatch")
print("=" * 74)
for name, args in agent_plan:
    print(f"agent calls {name}(...) with raw PII:")
    agent_dispatch(name, args)
    print()


# ===========================================================================
# STYLE B — decorate a single tool (zero dispatch changes)
# ===========================================================================
print("=" * 74)
print("STYLE B — @guard_tool decorator on one tool")
print("=" * 74)


@kav.guard_tool(destination="create_crm_ticket")
def file_ticket(summary: str, customer: str):
    return create_crm_ticket(summary, customer)


print("agent calls file_ticket(...) with raw PII:")
file_ticket(summary=f"UPI ravi@okhdfcbank, Aadhaar {aadhaar}", customer="Arjun from Madurai")

print("\n" + "=" * 74)
print("The external CRM / SMS gateway NEVER saw the Aadhaar, card, or OTP.")
print(f"Every call was recorded in the audit log: {len(kav.audit)} events, "
      f"chain intact = {kav.audit.verify()[0]}")
