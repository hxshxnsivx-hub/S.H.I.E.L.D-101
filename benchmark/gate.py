"""Benchmark quality gate (District / immune system).

Fails CI if detection recall/precision drop below thresholds — so a change can
never silently regress the firewall. Runs the deterministic + heuristic path
(no model), which is what a clean CI runner has.

    python benchmark/gate.py           # thresholds via GATE_RECALL / GATE_PRECISION
"""
from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate as G  # noqa: E402
from kavach.detect import Detector  # noqa: E402


def main() -> None:
    n = int(os.environ.get("GATE_N", "1500"))
    random.seed(5)
    examples = list(G.generate(n))
    det = Detector()

    gold = hit = found = 0
    for ex in examples:
        g = {(e["cls"], e["canonical"]) for e in ex["entities"]}
        f = {(d.cls, d.canonical) for d in det.scan(ex["text"])}
        gold += len(g)
        found += len(f)
        hit += len(g & f)

    recall = hit / max(1, gold)
    precision = hit / max(1, found)
    print(f"gate: recall={recall:.3f} precision={precision:.3f} (n={n})")

    need_r = float(os.environ.get("GATE_RECALL", "0.95"))
    need_p = float(os.environ.get("GATE_PRECISION", "0.95"))
    if recall < need_r or precision < need_p:
        print(f"FAIL: below thresholds (recall>={need_r}, precision>={need_p})")
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
