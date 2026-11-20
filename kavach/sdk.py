"""Public SDK / interceptors (District D1) — the "attach to any agent" layer.

Wraps the decision engine in a small, drop-in API so a host agent can guard
what it sends out without rebuilding anything:

    kav = Kavach(trust={"crm_api": Trust.UNTRUSTED})

    # 1) guard raw text
    kav.guard(text, destination="crm_api").sanitized_text

    # 2) guard tool-call arguments (MCP / function-calling) BEFORE dispatch
    safe_args = kav.guard_arguments("crm_api", {"note": "...", "amount": 500}).sanitized

    # 3) decorate a tool so its string args are sanitised automatically
    @kav.guard_tool(destination="crm_api")
    def create_ticket(note: str, amount: int): ...
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import wraps

from .detect import Detector
from .engine import DecisionEngine, Result
from .policy import Policy, Trust, TrustRegistry

_STATUS_ORDER = {"clean": 0, "sanitized": 1, "needs_review": 2, "blocked_parts": 3}
_ORDER_STATUS = {v: k for k, v in _STATUS_ORDER.items()}


class KavachBlocked(Exception):
    """Raised in mode='block' when a payload/argument must not be dispatched."""

    def __init__(self, result):
        self.result = result
        super().__init__(f"Kavach blocked dispatch: status={getattr(result, 'status', '?')}")


@dataclass
class GuardResult:
    tool: str
    status: str
    blocked: bool
    sanitized: dict          # arg name -> sanitised value (non-str passed through)
    results: dict            # arg name -> engine Result
    evidence: list           # list of per-arg evidence records


class Kavach:
    """Drop-in firewall facade for an AI agent / application."""

    def __init__(self, trust=None, policy: Policy | None = None,
                 ner_backend=None, mode: str = "sanitize"):
        if not isinstance(trust, TrustRegistry):
            trust = TrustRegistry(trust or {})
        self.engine = DecisionEngine(
            detector=Detector(ner_backend=ner_backend),
            policy=policy or Policy(),
            trust=trust,
        )
        if mode not in ("sanitize", "block"):
            raise ValueError("mode must be 'sanitize' or 'block'")
        self.mode = mode

    def set_trust(self, destination: str, level: Trust) -> None:
        self.engine.trust.set(destination, level)

    # --- 1) raw text --------------------------------------------------------
    def guard(self, text: str, destination: str, direction: str = "outbound") -> Result:
        r = self.engine.process(text, destination, direction)
        if self.mode == "block" and r.status in ("blocked_parts", "needs_review"):
            raise KavachBlocked(r)
        return r

    # --- 2) tool-call arguments (the MCP / function-calling entry point) -----
    def guard_arguments(self, tool: str, arguments: dict, direction: str = "outbound") -> GuardResult:
        sanitized: dict = {}
        results: dict = {}
        evidence: list = []
        worst = 0
        for key, val in arguments.items():
            if isinstance(val, str):
                r = self.engine.process(val, tool, direction)
                sanitized[key] = r.sanitized_text
                results[key] = r
                evidence.append({"arg": key, **r.evidence})
                worst = max(worst, _STATUS_ORDER.get(r.status, 0))
            else:
                sanitized[key] = val
        status = _ORDER_STATUS[worst]
        blocked = any(r.status == "blocked_parts" for r in results.values())
        gr = GuardResult(tool, status, blocked, sanitized, results, evidence)
        if self.mode == "block" and (blocked or status == "needs_review"):
            raise KavachBlocked(gr)
        return gr

    # --- 3) decorator -------------------------------------------------------
    def guard_tool(self, destination: str | None = None):
        """Decorate a tool: its string keyword-args are sanitised before it runs."""
        def deco(fn):
            dest = destination or fn.__name__

            @wraps(fn)
            def wrapper(**kwargs):
                gr = self.guard_arguments(dest, kwargs)
                return fn(**gr.sanitized)
            return wrapper
        return deco
