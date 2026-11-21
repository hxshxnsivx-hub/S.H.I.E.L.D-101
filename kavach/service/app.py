"""Kavach production service (District D8) + metrics (District D5/nerves).

A real ASGI gateway: many agents POST their outbound text / tool-call arguments
and get a sanitised, policy-decided response, with Prometheus metrics. The core
(`do_*`) is plain Python so it's unit-testable without a running server; the
FastAPI app is only built if fastapi is installed.

    pip install "kavach[service]"
    uvicorn kavach.service.app:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

from collections import Counter

from kavach import Kavach, __version__
from kavach.config import build_policy, build_trust, load_config
from kavach.policy import Trust, TrustRegistry

_CFG = load_config()
_TRUST = build_trust(_CFG, TrustRegistry({
    "crm_external_api": Trust.UNTRUSTED,
    "analytics_vendor": Trust.UNTRUSTED,
    "internal_crm": Trust.INTERNAL,
    "core_banking": Trust.TRUSTED,
}))
KAV = Kavach(trust=_TRUST, policy=build_policy(_CFG))
_METRICS: Counter = Counter()


def _result_dict(r):
    return {
        "sanitized": r.sanitized_text, "status": r.status, "trust": r.trust,
        "latency_ms": r.latency_ms,
        "decisions": [{"cls": d.cls, "action": d.action.value, "reason": d.reason,
                       "confidence": d.confidence, "method": d.method} for d in r.decisions],
        "evidence_id": r.evidence["evidence_id"],
    }


def do_guard(text: str, destination: str) -> dict:
    r = KAV.guard(text, destination)
    _METRICS["guard_total"] += 1
    _METRICS[f"status_{r.status}"] += 1
    return _result_dict(r)


def do_guard_arguments(tool: str, arguments: dict) -> dict:
    gr = KAV.guard_arguments(tool, arguments)
    _METRICS["guard_arguments_total"] += 1
    _METRICS[f"status_{gr.status}"] += 1
    return {"tool": gr.tool, "status": gr.status, "blocked": gr.blocked, "sanitized": gr.sanitized}


def do_audit() -> dict:
    return {"report": KAV.audit.report()}


def set_trust(destination: str, level: str) -> None:
    KAV.set_trust(destination, Trust(level))


def metrics_text() -> str:
    lines = ["# Kavach metrics (Prometheus exposition)"]
    for k, v in sorted(_METRICS.items()):
        lines.append(f"kavach_{k} {v}")
    lines.append(f"kavach_audit_events {len(KAV.audit)}")
    return "\n".join(lines) + "\n"


try:  # build the ASGI app only if FastAPI is present
    from fastapi import FastAPI, Response
    from pydantic import BaseModel

    app = FastAPI(title="Kavach", version=__version__)

    class GuardReq(BaseModel):
        text: str
        destination: str

    class ArgsReq(BaseModel):
        tool: str
        arguments: dict

    class TrustReq(BaseModel):
        destination: str
        level: str

    @app.get("/health")
    def health():
        return {"status": "ok", "version": __version__}

    @app.post("/v1/guard")
    def guard(req: GuardReq):
        return do_guard(req.text, req.destination)

    @app.post("/v1/guard-arguments")
    def guard_arguments(req: ArgsReq):
        return do_guard_arguments(req.tool, req.arguments)

    @app.post("/v1/trust")
    def trust(req: TrustReq):
        set_trust(req.destination, req.level)
        return {"ok": True}

    @app.get("/v1/audit")
    def audit():
        return do_audit()

    @app.get("/metrics")
    def metrics():
        return Response(metrics_text(), media_type="text/plain")

except Exception:  # pragma: no cover
    # FastAPI absent OR an incompatible fastapi/starlette combo — the service is
    # optional, so degrade gracefully; the plain do_* core still works.
    app = None
