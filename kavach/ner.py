"""Heuristic NER layer (District D2).

Covers the fuzzy classes that checksums/regex cannot: person names (here),
with addresses and health terms to follow. This is a GAZETTEER + TRIGGER-PHRASE
stand-in; the production swap-in is a fine-tuned MuRIL / IndicBERT model that
also catches names outside the gazetteer. Kept dependency-free so the pipeline
runs anywhere, and scored on the same benchmark so the upgrade is measurable.
"""
from __future__ import annotations

import re

# A small gazetteer of common Indian given names (extend heavily in production).
NAMES = [
    "Ravi", "Kumar", "Priya", "Arjun", "Deepa", "Suresh", "Anjali", "Vijay",
    "Lakshmi", "Karthik", "Meena", "Rahul", "Sneha", "Manoj", "Divya", "Ganesh",
    "Pooja", "Harish", "Nisha", "Ramesh", "Kavya", "Ashok", "Swathi", "Naveen",
    "Bhavna", "Mohan", "Revathi", "Sanjay", "Geetha", "Arun", "Fatima", "Imran",
]
_NAME_SET = {n.lower() for n in NAMES}

# Latin + Devanagari + Tamil letter runs.
_WORD = re.compile(r"[A-Za-zऀ-ॿ஀-௿]+")

_NAME_TRIGGERS = [
    "my name is", "name is", "myself", "i am",
    "मेरा नाम", "नाम", "என் பெயர்", "பெயர்",
]


def detect_names(text: str):
    """Return (value, start, end, confidence) for likely person names."""
    out = []
    seen = set()

    # 1) gazetteer hits
    for m in _WORD.finditer(text):
        if m.group().lower() in _NAME_SET and m.start() not in seen:
            out.append((m.group(), m.start(), m.end(), 0.7))
            seen.add(m.start())

    # 2) trigger-phrase capture (catches names outside the gazetteer)
    low = text.lower()
    for trg in _NAME_TRIGGERS:
        idx = 0
        while True:
            i = low.find(trg, idx)
            if i < 0:
                break
            idx = i + len(trg)
            m = _WORD.search(text, idx)
            if m and 0 <= (m.start() - idx) <= 4 and m.start() not in seen:
                out.append((m.group(), m.start(), m.end(), 0.6))
                seen.add(m.start())
    return out
