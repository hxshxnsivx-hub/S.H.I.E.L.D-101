"""Policy & decision logic (District D3).

Turns a detection + the destination's trust level into an action. Core rules:
- secrets (OTP, passwords, keys) never egress — always BLOCK;
- a trusted destination may receive the data (ALLOW);
- otherwise apply the class's default action (mask / tokenize / block), but
  a low-confidence high-sensitivity hit is ESCALATED to a human rather than
  silently acted on (fail-safe).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .taxonomy import REGISTRY, Action, Sensitivity


class Trust(Enum):
    TRUSTED = "trusted"      # vetted first-party / internal system
    INTERNAL = "internal"    # same org, still governed
    UNTRUSTED = "untrusted"  # third-party tool / external API
    UNKNOWN = "unknown"      # not in the registry -> treated as untrusted


class TrustRegistry:
    """Maps a destination (tool / API name) to a trust level; default UNKNOWN."""

    def __init__(self, mapping: dict[str, Trust] | None = None):
        self._m: dict[str, Trust] = dict(mapping or {})

    def set(self, destination: str, level: Trust) -> None:
        self._m[destination] = level

    def level(self, destination: str) -> Trust:
        return self._m.get(destination, Trust.UNKNOWN)


@dataclass
class Policy:
    policy_version: str = "v1"
    escalate_below: float = 0.6
    overrides: dict[str, Action] = field(default_factory=dict)

    def action_for(self, cls: str) -> Action:
        if cls in self.overrides:
            return self.overrides[cls]
        return REGISTRY[cls].default_action if cls in REGISTRY else Action.MASK

    def sensitivity(self, cls: str) -> Sensitivity:
        return REGISTRY[cls].sensitivity if cls in REGISTRY else Sensitivity.S2

    def group(self, cls: str) -> str:
        return REGISTRY[cls].group if cls in REGISTRY else "contact"


def decide(cls: str, confidence: float, trust: Trust, policy: Policy) -> tuple[Action, str]:
    """Return (action, human-readable reason) for one detected entity."""
    if policy.group(cls) == "secret":
        return Action.BLOCK, "secret must never egress"
    if trust is Trust.TRUSTED:
        return Action.ALLOW, "trusted destination"
    if policy.sensitivity(cls) is Sensitivity.S3 and confidence < policy.escalate_below:
        return Action.ESCALATE, f"low-confidence ({confidence:.2f}) high-sensitivity entity"
    base = policy.action_for(cls)
    return base, f"{policy.sensitivity(cls).name} -> {trust.value}"
