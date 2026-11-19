"""Small multilingual gazetteers (District D2).

Deterministic lists for cities (ADDRESS) and health conditions (HEALTH) in
Hindi / Tamil / English. Single-token entries so a token scan catches them.
The MuRIL NER generalises ADDRESS beyond this list; the gazetteer guarantees a
dependency-free floor and the shared-list health terms.
"""
from __future__ import annotations

import re

CITIES = [
    "Chennai", "Madurai", "Coimbatore", "Tiruppur", "Salem", "Trichy",
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Kolkata", "Pune",
    "Jaipur", "Nagpur", "Kochi", "Lucknow",
]

HEALTH_TERMS = [
    "diabetes", "hypertension", "asthma", "pregnancy", "cancer",
    "tuberculosis", "anemia", "HIV",
    "मधुमेह", "क्षयरोग", "गर्भावस्था",           # Hindi
    "நீரிழிவு", "காசநோய்", "கர்ப்பம்",            # Tamil
]

CITY_SET = {c.lower() for c in CITIES}
HEALTH_SET = {h.lower() for h in HEALTH_TERMS}

_WORD = re.compile(r"[A-Za-zऀ-ॿ஀-௿]+")


def scan(text: str, wordset: set[str]):
    """Return (value, start, end) for tokens that are in ``wordset``."""
    out = []
    for m in _WORD.finditer(text):
        if m.group().lower() in wordset:
            out.append((m.group(), m.start(), m.end()))
    return out
