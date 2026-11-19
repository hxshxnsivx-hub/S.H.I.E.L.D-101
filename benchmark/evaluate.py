"""Evaluate the detector against the synthetic benchmark (District D2/D7).

Produces the first real numbers: per-class recall and overall precision /
false-positive rate — the metrics that decide whether the firewall is safe to
put inline. Matching is by (class, canonical value), robust to span-boundary
differences between native-digit and number-word forms.

Usage:
    python benchmark/evaluate.py --n 2000
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate as G  # noqa: E402
from kavach.detect import Detector  # noqa: E402


def run(n: int, seed: int, use_ner: bool = False) -> None:
    import random
    random.seed(seed)
    examples = list(G.generate(n))
    ner_status = "off"
    if use_ner:
        from kavach.ner_model import TransformerNER
        backend = TransformerNER()
        if backend.available:
            det = Detector(ner_backend=backend)
            ner_status = f"on ({backend.model_id})"
        else:
            print("NER backend unavailable, falling back:", backend.error)
            det = Detector()
    else:
        det = Detector()

    gold_total: dict[str, int] = defaultdict(int)
    gold_hit: dict[str, int] = defaultdict(int)
    det_total = 0
    det_hit = 0
    fp_by_cls: dict[str, int] = defaultdict(int)

    for ex in examples:
        gold = {(e["cls"], e["canonical"]) for e in ex["entities"]}
        for cls, _ in gold:
            gold_total[cls] += 1
        found = {(d.cls, d.canonical) for d in det.scan(ex["text"])}
        for key in gold:
            if key in found:
                gold_hit[key[0]] += 1
        for key in found:
            det_total += 1
            if key in gold:
                det_hit += 1
            else:
                fp_by_cls[key[0]] += 1

    print(f"\nKavach D2 detection — benchmark eval (n={n} examples, seed={seed}, NER: {ner_status})\n")
    print(f"{'class':<14}{'gold':>6}{'found':>7}{'recall':>9}")
    print("-" * 40)
    for cls in sorted(gold_total):
        g = gold_total[cls]
        h = gold_hit[cls]
        print(f"{cls:<14}{g:>6}{h:>7}{(h / g if g else 0):>9.1%}")
    overall_recall = sum(gold_hit.values()) / max(1, sum(gold_total.values()))
    precision = det_hit / max(1, det_total)
    print("-" * 40)
    print(f"{'OVERALL':<14}{sum(gold_total.values()):>6}{sum(gold_hit.values()):>7}{overall_recall:>9.1%}")
    print(f"\nprecision: {precision:.1%}   detections: {det_total}   "
          f"false positives: {det_total - det_hit} ({(det_total - det_hit) / max(1, len(examples)):.3f}/example)")
    if fp_by_cls:
        print("false positives by class:", dict(fp_by_cls))
    print("\nnote: BANK_ACCOUNT↔CARD_PAN confusions are expected — a random "
          "account number can pass Luhn; checksum classes (AADHAAR/CARD/GSTIN) are the trustworthy ones.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--ner", action="store_true", help="enable the transformer NER backend")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    run(args.n, args.seed, use_ner=args.ner)


if __name__ == "__main__":
    main()
