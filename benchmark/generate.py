"""Synthetic code-mixed PII-leak benchmark generator (District D7).

Emits labelled examples: agent-style utterances / tool-call payloads in
Hindi, Tamil and English (and code-mixed), with each PII value rendered as
native digits, number-words, or transliterated, plus ground-truth spans.

This is the seed of the open benchmark — the defensible asset. Enrich later
with design-partner traces under a DPA.

Usage:
    python benchmark/generate.py --n 8            # print JSONL
    python benchmark/generate.py --n 500 -o seed.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import random
import string
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kavach import validators as v  # noqa: E402
from kavach.ner import NAMES  # noqa: E402
from kavach.gazetteers import CITIES, HEALTH_TERMS  # noqa: E402

DIGIT_WORDS = {
    "en": ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
    "hi": ["शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ"],
    "ta": ["பூஜ்ஜியம்", "ஒன்று", "இரண்டு", "மூன்று", "நான்கு", "ஐந்து", "ஆறு", "ஏழு", "எட்டு", "ஒன்பது"],
}

# Code-mixed templates per language. {X} is replaced by a rendered PII value.
TEMPLATES = {
    "en": [
        "Please update my Aadhaar {AADHAAR} and PAN {PAN} in the system.",
        "Transfer to account {BANK} IFSC {IFSC}, my UPI is {UPI}.",
        "My card number is {CARD}, confirm the payment.",
        "My name is {NAME}, email {EMAIL}, mobile {PHONE}.",
        "Patient {NAME} from {ADDRESS}, diagnosed {HEALTH}, ABHA {ABHA}.",
    ],
    "hi": [
        "मेरा Aadhaar {AADHAAR} है aur PAN {PAN} update kar do.",
        "Payment {UPI} par bhej do, card {CARD} use mat karna.",
        "Account {BANK} IFSC {IFSC} me paisa daal do bhaiya.",
        "मेरा नाम {NAME} hai, email {EMAIL}, mobile number {PHONE}.",
        "मरीज {NAME}, पता {ADDRESS}, {HEALTH} की शिकायत, ABHA {ABHA}.",
    ],
    "ta": [
        "என் Aadhaar {AADHAAR}, PAN {PAN} ஐ update பண்ணுங்க.",
        "UPI {UPI} க்கு அனுப்புங்க, card {CARD} வேண்டாம்.",
        "Account {BANK} IFSC {IFSC} ல பணம் போடுங்க.",
        "என் பெயர் {NAME}, email {EMAIL}, mobile number {PHONE}.",
        "நோயாளி {NAME}, ஊர் {ADDRESS}, {HEALTH}, ABHA {ABHA}.",
    ],
}

PLACEHOLDER_CLASS = {
    "AADHAAR": "AADHAAR", "PAN": "PAN", "BANK": "BANK_ACCOUNT",
    "IFSC": "IFSC", "UPI": "UPI_VPA", "CARD": "CARD_PAN",
    "NAME": "NAME", "EMAIL": "EMAIL", "PHONE": "PHONE",
    "ADDRESS": "ADDRESS", "HEALTH": "HEALTH", "ABHA": "HEALTH",
}

_EMAIL_DOMAINS = ["gmail.com", "yahoo.in", "outlook.com", "rediffmail.com"]
_ABHA_HANDLES = ["abdm", "sbx", "ndhm"]


def _rand_aadhaar() -> str:
    base = random.choice("23456789") + "".join(random.choice(string.digits) for _ in range(10))
    return base + v.verhoeff_checksum(base)


def _luhn_check_digit(payload: str) -> str:
    for d in "0123456789":
        if v.luhn_validate(payload + d):
            return d
    return "0"


def _rand_card() -> str:
    body = "4" + "".join(random.choice(string.digits) for _ in range(14))
    return body + _luhn_check_digit(body)


def _rand_pan() -> str:
    L = string.ascii_uppercase
    return "".join(random.choice(L) for _ in range(5)) + "".join(random.choice(string.digits) for _ in range(4)) + random.choice(L)


def _rand_ifsc() -> str:
    L = string.ascii_uppercase
    return "".join(random.choice(L) for _ in range(4)) + "0" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def _rand_bank() -> str:
    return "".join(random.choice(string.digits) for _ in range(random.randint(11, 16)))


def _rand_upi() -> str:
    name = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(4, 8)))
    return f"{name}@{random.choice(sorted(v.PSP_HANDLES))}"


def _rand_name() -> str:
    return random.choice(NAMES)


def _rand_email() -> str:
    local = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 9)))
    return f"{local}@{random.choice(_EMAIL_DOMAINS)}"


def _rand_phone() -> str:
    return random.choice("6789") + "".join(random.choice(string.digits) for _ in range(9))


def _rand_address() -> str:
    return random.choice(CITIES)


def _rand_health() -> str:
    return random.choice(HEALTH_TERMS)


def _rand_abha() -> str:
    local = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(4, 8)))
    return f"{local}@{random.choice(_ABHA_HANDLES)}"


GENERATORS = {
    "AADHAAR": _rand_aadhaar, "PAN": _rand_pan, "BANK": _rand_bank,
    "IFSC": _rand_ifsc, "UPI": _rand_upi, "CARD": _rand_card,
    "NAME": _rand_name, "EMAIL": _rand_email, "PHONE": _rand_phone,
    "ADDRESS": _rand_address, "HEALTH": _rand_health, "ABHA": _rand_abha,
}

# classes whose value is purely numeric (eligible for number-word rendering)
_NUMERIC_PLACEHOLDERS = {"AADHAAR", "BANK", "CARD", "PHONE"}


def _to_number_words(value: str, lang: str) -> str:
    words = DIGIT_WORDS[lang]
    return " ".join(words[int(c)] if c.isdigit() else c for c in value)


def make_example(lang: str, form: str) -> dict:
    tmpl = random.choice(TEMPLATES[lang])
    rendered = tmpl
    entities = []
    for ph in [p for p in PLACEHOLDER_CLASS if "{" + p + "}" in tmpl]:
        raw = GENERATORS[ph]()
        if form == "number_words" and ph in _NUMERIC_PLACEHOLDERS:
            shown = _to_number_words(raw, lang)
        else:
            shown = raw
        rendered = rendered.replace("{" + ph + "}", shown, 1)
        start = rendered.find(shown)
        entities.append({
            "cls": PLACEHOLDER_CLASS[ph],
            "value": shown,
            "canonical": raw,
            "start": start,
            "end": start + len(shown),
        })
    return {"text": rendered, "lang": lang, "form": form, "entities": entities}


def generate(n: int):
    forms = ["native", "number_words"]
    langs = list(TEMPLATES)
    for _ in range(n):
        yield make_example(random.choice(langs), random.choice(forms))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)
    if args.out is None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows console defaults to cp1252
    out = open(args.out, "w", encoding="utf-8") if args.out else sys.stdout
    for ex in generate(args.n):
        out.write(json.dumps(ex, ensure_ascii=False) + "\n")
    if args.out:
        out.close()
        print(f"wrote {args.n} examples -> {args.out}")


if __name__ == "__main__":
    main()
