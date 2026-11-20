"""Decision engine (District D3) — the firewall's hot path.

Ties detection -> decision -> action -> evidence. Given a text payload and the
destination it is headed to, it returns the sanitized payload, the per-entity
decisions, an audit-evidence record (DPDP Rule-6 style), and the latency.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from .detect import Detector
from .policy import Policy, Trust, TrustRegistry, decide
from .taxonomy import Action
from .vault import TokenVault

_FULL_MASK = {"NAME", "ADDRESS", "HEALTH", "EMAIL"}
# severity order for the overall payload status
_SEVERITY = {Action.ALLOW: 0, Action.MASK: 1, Action.TOKENIZE: 2, Action.ESCALATE: 3, Action.BLOCK: 4}
_STATUS = {0: "clean", 1: "sanitized", 2: "sanitized", 3: "needs_review", 4: "blocked_parts"}


@dataclass
class EntityDecision:
    cls: str
    value: str
    start: int
    end: int
    confidence: float
    method: str
    action: Action
    reason: str


@dataclass
class Result:
    destination: str
    trust: str
    status: str
    sanitized_text: str
    decisions: list[EntityDecision]
    evidence: dict
    latency_ms: float = field(default=0.0)


class DecisionEngine:
    def __init__(self, detector: Detector | None = None, policy: Policy | None = None,
                 trust: TrustRegistry | None = None, vault: TokenVault | None = None,
                 audit=None):
        self.detector = detector or Detector()
        self.policy = policy or Policy()
        self.trust = trust or TrustRegistry()
        self.vault = vault or TokenVault()
        self.audit = audit

    def _mask(self, cls: str, value: str) -> str:
        if cls in _FULL_MASK:
            return f"[{cls}]"
        tail = value[-4:]
        return "X" * max(0, len(value) - 4) + tail

    def _apply(self, action: Action, cls: str, value: str) -> str | None:
        if action is Action.ALLOW:
            return None
        if action is Action.MASK:
            return self._mask(cls, value)
        if action is Action.TOKENIZE:
            return self.vault.tokenize(cls, value)
        if action is Action.BLOCK:
            return f"[BLOCKED:{cls}]"
        if action is Action.ESCALATE:
            return f"[REVIEW:{cls}]"
        return None

    def process(self, text: str, destination: str, direction: str = "outbound") -> Result:
        t0 = time.perf_counter()
        trust = self.trust.level(destination)
        decisions: list[EntityDecision] = []
        for d in self.detector.scan(text):
            action, reason = decide(d.cls, d.confidence, trust, self.policy)
            decisions.append(EntityDecision(d.cls, d.value, d.start, d.end,
                                            d.confidence, d.method, action, reason))

        # apply right-to-left so spans stay valid
        sanitized = text
        for ed in sorted(decisions, key=lambda x: -x.start):
            repl = self._apply(ed.action, ed.cls, ed.value)
            if repl is not None:
                sanitized = sanitized[:ed.start] + repl + sanitized[ed.end:]

        worst = max((_SEVERITY[ed.action] for ed in decisions), default=0)
        status = _STATUS[worst]
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        evidence = {
            "evidence_id": "ev_" + uuid.uuid4().hex[:12],
            "direction": direction,
            "destination": destination,
            "trust": trust.value,
            "status": status,
            "policy_version": self.policy.policy_version,
            "latency_ms": latency_ms,
            "entities": [
                {
                    "cls": ed.cls, "action": ed.action.value, "reason": ed.reason,
                    "confidence": ed.confidence, "method": ed.method,
                    "span": [ed.start, ed.end],
                    # NB: raw value intentionally NOT stored in the audit record
                }
                for ed in decisions
            ],
        }
        if self.audit is not None:
            self.audit.record(evidence)
        return Result(destination, trust.value, status, sanitized, decisions, evidence, latency_ms)
