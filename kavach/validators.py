"""Deterministic validators — the high-precision first pass (District D2/D7).

These separate a *real* identifier from a look-alike using checksums and
structure, which is what keeps the false-positive rate low enough that the
host agent tolerates the firewall. ML/NER only handles what these cannot.

Pure standard library; no dependencies.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Verhoeff checksum — Aadhaar
# ---------------------------------------------------------------------------
_VERHOEFF_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)
_VERHOEFF_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)
_VERHOEFF_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def verhoeff_validate(number: str) -> bool:
    """True if ``number`` (digits incl. trailing check digit) passes Verhoeff."""
    if not number.isdigit():
        return False
    c = 0
    for i, item in enumerate(reversed(number)):
        c = _VERHOEFF_D[c][_VERHOEFF_P[i % 8][int(item)]]
    return c == 0


def verhoeff_checksum(payload: str) -> str:
    """Return the Verhoeff check digit to append to ``payload`` (digits only)."""
    if not payload.isdigit():
        raise ValueError("payload must be digits")
    c = 0
    for i, item in enumerate(reversed(payload)):
        c = _VERHOEFF_D[c][_VERHOEFF_P[(i + 1) % 8][int(item)]]
    return str(_VERHOEFF_INV[c])


def is_aadhaar(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    # Aadhaar is 12 digits and never begins with 0 or 1.
    if len(digits) != 12 or digits[0] in "01":
        return False
    return verhoeff_validate(digits)


# ---------------------------------------------------------------------------
# Luhn — payment card numbers
# ---------------------------------------------------------------------------
def luhn_validate(value: str) -> bool:
    digits = [int(d) for d in value if d.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


# ---------------------------------------------------------------------------
# Structural: PAN, IFSC
# ---------------------------------------------------------------------------
_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
_IFSC_RE = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")


def is_pan(value: str) -> bool:
    return bool(_PAN_RE.match(value.strip().upper()))


def is_ifsc(value: str) -> bool:
    return bool(_IFSC_RE.match(value.strip().upper()))


# ---------------------------------------------------------------------------
# GSTIN — structure + base-36 checksum (official GSTN algorithm)
# ---------------------------------------------------------------------------
_GST_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_GSTIN_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]$")


def gstin_checksum(first14: str) -> str:
    """Return the GSTIN check character for the first 14 characters."""
    n = len(_GST_CHARS)
    factor = 2
    total = 0
    for ch in reversed(first14):
        v = factor * _GST_CHARS.index(ch)
        factor = 1 if factor == 2 else 2
        v = (v // n) + (v % n)
        total += v
    return _GST_CHARS[(n - (total % n)) % n]


def is_gstin(value: str) -> bool:
    v = value.strip().upper()
    if not _GSTIN_RE.match(v):
        return False
    return gstin_checksum(v[:14]) == v[14]


# ---------------------------------------------------------------------------
# UPI VPA — structure + PSP-handle allowlist (first-class PII class)
# ---------------------------------------------------------------------------
_VPA_RE = re.compile(r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z][a-zA-Z0-9]{1,63}$")

# A starter allowlist of common PSP / bank handles. Extend from the NPCI list.
PSP_HANDLES = {
    "ybl", "okhdfcbank", "okaxis", "oksbi", "okicici", "paytm", "apl", "ibl",
    "upi", "axl", "axisbank", "hdfcbank", "sbi", "icici", "yapl", "fam",
    "jupiteraxis", "naviaxis", "ikwik", "pz", "rapl", "waaxis", "yescred",
}


def is_upi_vpa(value: str, strict_psp: bool = True) -> bool:
    v = value.strip()
    if not _VPA_RE.match(v):
        return False
    if strict_psp:
        return v.split("@", 1)[1].lower() in PSP_HANDLES
    return True
