"""Deployment configuration (District D8).

Load trust registry and policy from a JSON file (KAVACH_CONFIG), so an on-prem
operator configures the firewall without touching code. Everything here is
stdlib-only — no external calls — which is what makes the core air-gap safe.
"""
from __future__ import annotations

import json
import os

from .policy import Policy, Trust, TrustRegistry


def load_config(path: str | None = None) -> dict:
    path = path or os.environ.get("KAVACH_CONFIG")
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def build_trust(cfg: dict, base: TrustRegistry | None = None) -> TrustRegistry:
    tr = base or TrustRegistry()
    for dest, level in (cfg.get("trust") or {}).items():
        tr.set(dest, Trust(level))
    return tr


def build_policy(cfg: dict) -> Policy:
    p = cfg.get("policy") or {}
    return Policy(
        policy_version=p.get("version", "v1"),
        escalate_below=float(p.get("escalate_below", 0.6)),
    )
