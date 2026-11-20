"""Audit & evidence plane (District D5).

An append-only, hash-chained log of decision evidence. Each record commits to
the previous one, so any later edit/removal breaks the chain and `verify()`
finds it. Records hold decisions and metadata only — never raw PII — which is
exactly what DPDP Rule 6 "logging/monitoring" asks for, plus a one-call
evidence report for breach / audit response.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from collections import Counter
from dataclasses import dataclass

GENESIS = "0" * 64


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _hash(prev: str, body: dict) -> str:
    return hashlib.sha256((prev + _canon(body)).encode("utf-8")).hexdigest()


@dataclass
class AuditRecord:
    seq: int
    ts: float
    prev_hash: str
    hash: str
    evidence: dict

    def body(self) -> dict:
        return {"seq": self.seq, "ts": self.ts, "prev_hash": self.prev_hash, "evidence": self.evidence}


class AuditLog:
    """Hash-chained, optionally file-backed, tamper-evident evidence log."""

    def __init__(self, path: str | None = None):
        self.path = path
        self._records: list[AuditRecord] = []
        self._last = GENESIS
        if path and os.path.exists(path):
            self._load()

    def _load(self) -> None:
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                rec = AuditRecord(d["seq"], d["ts"], d["prev_hash"], d["hash"], d["evidence"])
                self._records.append(rec)
                self._last = rec.hash

    def record(self, evidence: dict) -> AuditRecord:
        seq = len(self._records)
        ts = round(time.time(), 3)
        body = {"seq": seq, "ts": ts, "prev_hash": self._last, "evidence": evidence}
        h = _hash(self._last, body)
        rec = AuditRecord(seq, ts, self._last, h, evidence)
        self._records.append(rec)
        self._last = h
        if self.path:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(_canon({**body, "hash": h}) + "\n")
        return rec

    def verify(self) -> tuple[bool, int | None]:
        """Recompute the chain from genesis; return (ok, first_bad_seq)."""
        prev = GENESIS
        for rec in self._records:
            if rec.prev_hash != prev or _hash(prev, rec.body()) != rec.hash:
                return False, rec.seq
            prev = rec.hash
        return True, None

    def __len__(self) -> int:
        return len(self._records)

    def entries(self) -> list[AuditRecord]:
        return list(self._records)

    def report(self) -> dict:
        """A DPDP-style evidence summary over the whole log."""
        actions: Counter = Counter()
        classes: Counter = Counter()
        statuses: Counter = Counter()
        dests: Counter = Counter()
        incidents = 0  # blocked or escalated events = reportable candidates
        for rec in self._records:
            ev = rec.evidence
            statuses[ev.get("status", "?")] += 1
            dests[ev.get("destination", "?")] += 1
            if ev.get("status") in ("blocked_parts", "needs_review"):
                incidents += 1
            for ent in ev.get("entities", []):
                actions[ent.get("action", "?")] += 1
                classes[ent.get("cls", "?")] += 1
        ok, bad = self.verify()
        return {
            "events": len(self._records),
            "chain_intact": ok,
            "first_tampered_seq": bad,
            "by_status": dict(statuses),
            "by_action": dict(actions),
            "by_class": dict(classes),
            "by_destination": dict(dests),
            "reportable_events": incidents,
        }
