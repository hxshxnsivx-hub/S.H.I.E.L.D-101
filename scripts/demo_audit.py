"""Audit-plane demo (District D5): tamper-evident evidence + DPDP report.

    python scripts/demo_audit.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from kavach import Kavach, Trust  # noqa: E402
from kavach import validators as v  # noqa: E402

kav = Kavach(trust={"crm_external_api": Trust.UNTRUSTED, "core_banking": Trust.TRUSTED})
aad = "23456789012" + v.verhoeff_checksum("23456789012")

for dest, txt in [
    ("crm_external_api", f"Aadhaar {aad}, OTP 123456"),
    ("core_banking", "customer Priya, routine note"),
    ("crm_external_api", "card 4111111111111111, UPI ravi@okhdfcbank"),
]:
    kav.guard(txt, dest)

print(f"audit records: {len(kav.audit)}")
print("DPDP evidence report:")
print(json.dumps(kav.audit.report(), indent=2, ensure_ascii=False))

ok, bad = kav.audit.verify()
print(f"\nchain intact: {ok}")

# simulate tampering with a stored record
kav.audit.entries()[0].evidence["destination"] = "somewhere_else"
ok, bad = kav.audit.verify()
print(f"after tampering with record 0 -> chain intact: {ok}  (first bad seq: {bad})")
