"""Kavach with OpenAI function-calling.

The model returns a tool call ({function:{name, arguments:JSON}}); Kavach guards
the arguments before the local function runs. (The model's choice is simulated
here because a live call needs an API key; the tool-call shape is exactly what
the OpenAI API returns.)

    python examples/openai_integration.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from kavach import Kavach, Trust
from kavach import validators as v
from kavach.integrations.openai import guard_tool_call

aadhaar = "23456789012" + v.verhoeff_checksum("23456789012")


def create_crm_ticket(summary, customer):
    print(f"      >> EXTERNAL CRM receives: summary={summary!r} customer={customer!r}")
    return "T-1001"


LOCAL_FUNCS = {"create_crm_ticket": create_crm_ticket}

kav = Kavach(trust={"create_crm_ticket": Trust.UNTRUSTED})

# Exactly the shape the OpenAI API returns in message.tool_calls:
tool_call = {
    "id": "call_abc",
    "type": "function",
    "function": {
        "name": "create_crm_ticket",
        "arguments": json.dumps({
            "summary": f"Aadhaar {aadhaar}, card 4111111111111111",
            "customer": "Priya from Chennai",
        }),
    },
}

print("=" * 74)
print("OpenAI tool call -> guard arguments -> run local function")
print("=" * 74)
name, safe_args, gr = guard_tool_call(kav, tool_call)
print(f"[kavach] {name}: status={gr.status}")
LOCAL_FUNCS[name](**safe_args)
print(f"\naudit: {len(kav.audit)} events, chain intact = {kav.audit.verify()[0]}")
print("The CRM received tokenised/masked arguments, not the raw Aadhaar/card.")
