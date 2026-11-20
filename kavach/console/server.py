"""Kavach admin console server (District D6).

Dependency-free (stdlib http.server) web console over the decision engine:
guard a payload to a destination, see the sanitized output + per-entity
decisions, and watch the tamper-evident DPDP audit panel update live.

    python -m kavach.console.server         # then open http://localhost:8765
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# allow running as a plain file (python .../server.py) from any cwd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kavach.audit import AuditLog
from kavach.detect import Detector
from kavach.engine import DecisionEngine
from kavach.policy import Policy, Trust, TrustRegistry
from kavach.taxonomy import REGISTRY

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("KAVACH_PORT", "8765"))

AUDIT = AuditLog()
TRUST = TrustRegistry({
    "crm_external_api": Trust.UNTRUSTED,
    "analytics_vendor": Trust.UNTRUSTED,
    "internal_crm": Trust.INTERNAL,
    "core_banking": Trust.TRUSTED,
})
ENGINE = DecisionEngine(detector=Detector(), policy=Policy(), trust=TRUST, audit=AUDIT)


def _result_json(r):
    return {
        "sanitized": r.sanitized_text, "status": r.status, "trust": r.trust,
        "latency_ms": r.latency_ms,
        "decisions": [
            {"cls": d.cls, "value": d.value, "start": d.start, "end": d.end,
             "confidence": d.confidence, "method": d.method,
             "action": d.action.value, "reason": d.reason}
            for d in r.decisions
        ],
        "evidence": r.evidence,
    }


def _audit_json():
    recent = [
        {"seq": rec.seq, "hash": rec.hash[:10],
         "status": rec.evidence.get("status"), "destination": rec.evidence.get("destination"),
         "entities": len(rec.evidence.get("entities", []))}
        for rec in ENGINE.audit.entries()[-25:][::-1]
    ]
    return {"report": ENGINE.audit.report(), "recent": recent}


def _meta_json():
    return {
        "destinations": [{"name": d, "trust": TRUST.level(d).value}
                         for d in ("crm_external_api", "analytics_vendor", "internal_crm", "core_banking")],
        "trust_levels": [t.value for t in Trust],
        "classes": [{"code": c.code, "label": c.label, "group": c.group,
                     "sensitivity": c.sensitivity.name, "action": c.default_action.value}
                    for c in REGISTRY.values()],
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, obj, code=200, ctype="application/json"):
        if ctype == "application/json":
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        else:
            body = obj if isinstance(obj, bytes) else obj.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if "html" in ctype or "json" in ctype else ""))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as fh:
                self._send(fh.read(), ctype="text/html")
        elif path == "/api/meta":
            self._send(_meta_json())
        elif path == "/api/audit":
            self._send(_audit_json())
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        if path == "/api/scan":
            r = ENGINE.process(data.get("text", ""), data.get("destination", "crm_external_api"))
            self._send(_result_json(r))
        elif path == "/api/trust":
            TRUST.set(data["destination"], Trust(data["level"]))
            self._send({"ok": True})
        else:
            self._send({"error": "not found"}, 404)


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Kavach console on http://localhost:{PORT}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
