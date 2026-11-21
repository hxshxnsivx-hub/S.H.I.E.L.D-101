"""Normalization (District D2).

Turns the many surface forms of a value into something the deterministic
validators can check: strips separators, and — the important Indic case —
converts spoken number-words (English / Hindi / Tamil) back into digit runs
so a card or Aadhaar dictated in words is still caught.

Known limitation: number-word detection is not yet context-gated, so ordinary
prose containing "one", "four" etc. would be picked up. The ML/NER layer and
context gating (later in D2) address that; for now it is scored honestly.
"""
from __future__ import annotations

import re

DIGIT_WORDS = {
    "en": ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
    "hi": ["शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ"],
    "ta": ["பூஜ்ஜியம்", "ஒன்று", "இரண்டு", "மூன்று", "நான்கு", "ஐந்து", "ஆறு", "ஏழு", "எட்டு", "ஒன்பது"],
    "te": ["సున్నా", "ఒకటి", "రెండు", "మూడు", "నాలుగు", "ఐదు", "ఆరు", "ఏడు", "ఎనిమిది", "తొమ్మిది"],
    "bn": ["শূন্য", "এক", "দুই", "তিন", "চার", "পাঁচ", "ছয়", "সাত", "আট", "নয়"],
}

_WORD2DIGIT: dict[str, str] = {}
for _lang, _words in DIGIT_WORDS.items():
    for _i, _w in enumerate(_words):
        _WORD2DIGIT[_w.lower()] = str(_i)

_TOKEN = re.compile(r"\S+")


def only_digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def number_word_spans(text: str) -> list[tuple[str, int, int]]:
    """Return (digit_string, start, end) for each maximal run of number-words."""
    toks = [(m.group(), m.start(), m.end()) for m in _TOKEN.finditer(text)]
    runs: list[list[tuple[str, int, int]]] = []
    cur: list[tuple[str, int, int]] = []
    for tok, s, e in toks:
        key = tok.lower().strip(".,!?;:")
        if key in _WORD2DIGIT:
            cur.append((_WORD2DIGIT[key], s, e))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    out = []
    for run in runs:
        canon = "".join(d for d, _, _ in run)
        out.append((canon, run[0][1], run[-1][2]))
    return out
