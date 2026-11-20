"""End-to-end Kavach demo (D2 detection + D3 decision).

Shows the same agent payload headed to an untrusted third-party tool vs a
trusted internal system, and what the firewall does to each.

    python scripts/demo.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from kavach import validators as v  # noqa: E402
from kavach.engine import DecisionEngine  # noqa: E402
from kavach.policy import Trust  # noqa: E402

eng = DecisionEngine()
eng.trust.set("crm_external_api", Trust.UNTRUSTED)
eng.trust.set("core_banking", Trust.TRUSTED)

base = "23456789012"
aadhaar = base + v.verhoeff_checksum(base)
payload = (f"Customer Priya from Chennai, Aadhaar {aadhaar}, UPI ravi@okhdfcbank, "
           f"card 4111111111111111, OTP 123456, diagnosis diabetes.")

for dest in ("crm_external_api", "core_banking"):
    r = eng.process(payload, dest)
    print("=" * 74)
    print(f"destination: {dest}   trust={r.trust}   status={r.status}   {r.latency_ms} ms")
    print(f"IN : {payload}")
    print(f"OUT: {r.sanitized_text}")
    for ed in r.decisions:
        print(f"    {ed.cls:12} {ed.action.value:9} conf={ed.confidence:<5} {ed.reason}")
print("=" * 74)
print(f"evidence (untrusted run) keys: {list(eng.process(payload, 'crm_external_api').evidence)}")
