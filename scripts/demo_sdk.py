"""SDK demo (District D1): an agent tool guarded by Kavach.

The agent calls a tool with raw PII in the arguments; Kavach intercepts the
call and the external tool only ever receives sanitised data.

    python scripts/demo_sdk.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from kavach import Kavach, Trust  # noqa: E402
from kavach import validators as v  # noqa: E402

kav = Kavach(trust={"crm_external_api": Trust.UNTRUSTED})
aadhaar = "23456789012" + v.verhoeff_checksum("23456789012")


@kav.guard_tool(destination="crm_external_api")
def crm_create_case(summary: str, customer: str):
    # pretend this POSTs to a third-party CRM
    print("   [external CRM receives]")
    print("      summary :", summary)
    print("      customer:", customer)
    return "case#123"


print("Agent calls the tool with RAW PII in its arguments:")
print(f"   summary  = Aadhaar {aadhaar}, card 4111111111111111, OTP 999123")
print("   customer = Priya from Chennai")
print("-" * 70)
crm_create_case(
    summary=f"Aadhaar {aadhaar}, card 4111111111111111, OTP 999123",
    customer="Priya from Chennai",
)
print("-" * 70)
print("The external tool never saw the Aadhaar, card, or OTP.")
