"""Detection pipeline (District D2).

Deterministic-first: structured regexes + checksum validators carry the
precision; number-word runs are normalized, context-gated and re-checked; a
heuristic NER layer covers names (MuRIL swap-in later). Each detection carries
a confidence and the method that produced it, feeding the decision engine (D3).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import gazetteers as gz
from . import ner
from . import normalize as nz
from . import validators as v


@dataclass
class Detection:
    cls: str
    value: str          # the substring as it appeared
    canonical: str      # normalized form (digits, or the token)
    start: int
    end: int
    confidence: float
    method: str


_ABHA = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@(?:abdm|sbx|ndhm)\b")
_UPI = re.compile(r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z][a-zA-Z0-9]{1,63}")
_EMAIL = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b")
_PAN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
_IFSC = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")
_GSTIN = re.compile(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]\b")
_DIGITS = re.compile(r"\d{10,19}")

# Context triggers that license a spoken number-word run as a real identifier.
# Without a nearby trigger, "one four ..." in ordinary prose is NOT treated as PII.
_TRIGGERS = {
    "card", "account", "acct", "aadhaar", "aadhar", "uid", "upi", "debit",
    "credit", "number", "mobile", "phone", "payment", "pay", "ifsc", "bank",
    "खाता", "आधार", "नंबर", "कार्ड", "मोबाइल", "भुगतान",
    "கணக்கு", "ஆதார்", "கார்டு", "எண்", "மொபைல்",
}


# Context words that disambiguate a 16-digit number that passes Luhn by accident.
_CARD_POS = {"card", "debit", "credit", "कार्ड", "கார்டு"}
_CARD_NEG = {"account", "bank", "acct", "खाता", "கணக்கு", "a/c"}


def _classify_number(canon: str) -> tuple[str | None, float]:
    n = len(canon)
    if n == 10 and canon[0] in "6789":
        return ("PHONE", 0.85)
    if n == 12 and v.is_aadhaar(canon):
        return ("AADHAAR", 0.99)
    if 13 <= n <= 19 and v.luhn_validate(canon):
        return ("CARD_PAN", 0.95)
    if 11 <= n <= 18:
        return ("BANK_ACCOUNT", 0.50)  # no checksum → ambiguous, low confidence
    return (None, 0.0)


def _has_trigger(text: str, start: int, window: int = 60) -> bool:
    ctx = text[max(0, start - window):start].lower()
    return any(t in ctx for t in _TRIGGERS)


class Detector:
    """Scans text and returns the PII/credential entities it finds.

    ``ner_backend`` is an object with ``.detect(text) -> [(cls, value, start,
    end, conf)]`` (e.g. ``kavach.ner_model.TransformerNER``). When omitted, the
    dependency-free heuristic name detector is used.
    """

    def __init__(self, ner_backend=None):
        self._ner = ner_backend

    def scan(self, text: str) -> list[Detection]:
        dets: list[Detection] = []
        occupied: list[tuple[int, int]] = []

        def overlaps(s: int, e: int) -> bool:
            return any(not (e <= os or s >= oe) for os, oe in occupied)

        def take(det: Detection) -> None:
            dets.append(det)
            occupied.append((det.start, det.end))

        # 1) structured identifiers (validated) — highest precision, run first
        structured = [
            (_ABHA, "HEALTH", 0.90, lambda x: True),   # ABHA address, before UPI/EMAIL
            (_GSTIN, "GSTIN", 0.99, v.is_gstin),
            (_PAN, "PAN", 0.90, v.is_pan),
            (_IFSC, "IFSC", 0.90, v.is_ifsc),
            (_UPI, "UPI_VPA", 0.90, lambda x: v.is_upi_vpa(x, strict_psp=True)),
            (_EMAIL, "EMAIL", 0.90, lambda x: True),
        ]
        for rx, cls, conf, valid in structured:
            for m in rx.finditer(text):
                tok = m.group()
                if valid(tok) and not overlaps(m.start(), m.end()):
                    take(Detection(cls, tok, tok, m.start(), m.end(), conf, "regex"))

        # 2) native digit runs
        for m in _DIGITS.finditer(text):
            if overlaps(m.start(), m.end()):
                continue
            canon = m.group()
            cls, conf = _classify_number(canon)
            # context disambiguation: a Luhn-passing account number near
            # "account"/"bank" (and not "card") is a bank account, not a card.
            if cls == "CARD_PAN":
                pre = text[max(0, m.start() - 40):m.start()].lower()
                if any(w in pre for w in _CARD_NEG) and not any(w in pre for w in _CARD_POS):
                    cls, conf = "BANK_ACCOUNT", 0.55
            if cls:
                take(Detection(cls, m.group(), canon, m.start(), m.end(), conf, "digits"))

        # 3) spoken number-word runs (the Indic code-mixed case), context-gated
        for canon, s, e in nz.number_word_spans(text):
            if len(canon) < 10 or overlaps(s, e) or not _has_trigger(text, s):
                continue
            cls, conf = _classify_number(canon)
            if cls:
                take(Detection(cls, text[s:e], canon, s, e, round(conf - 0.05, 2), "number_word"))

        # 4) NER layer — UNION of the MuRIL backend (generalises to unseen names/
        #    places) and the heuristic gazetteer (backstops known ones). Higher
        #    confidence wins on overlap; together they beat either alone.
        ner_hits: list[tuple[str, str, int, int, float, str]] = []
        if self._ner is not None:
            for cls, value, s, e, conf in self._ner.detect(text):
                ner_hits.append((cls, value, s, e, conf, "ner_model"))
        for value, s, e, conf in ner.detect_names(text):
            ner_hits.append(("NAME", value, s, e, conf, "ner_heuristic"))
        for cls, value, s, e, conf, method in sorted(ner_hits, key=lambda h: -h[4]):
            # a known city mislabelled as a person is an address
            if cls == "NAME" and value.lower() in gz.CITY_SET:
                cls = "ADDRESS"
            if not overlaps(s, e):
                take(Detection(cls, value, value, s, e, conf, method))

        # 5) gazetteers — health conditions and cities (NER generalises ADDRESS)
        for value, s, e in gz.scan(text, gz.HEALTH_SET):
            if not overlaps(s, e):
                take(Detection("HEALTH", value, value, s, e, 0.70, "gazetteer"))
        for value, s, e in gz.scan(text, gz.CITY_SET):
            if not overlaps(s, e):
                take(Detection("ADDRESS", value, value, s, e, 0.70, "gazetteer"))

        dets.sort(key=lambda d: d.start)
        return dets
