"""The PII / credential registry (District D7).

Every class Kavach must recognise, with its sensitivity tier and the
default action the decision engine applies when it is seen heading to an
untrusted destination. S3 = fail-safe (block/tokenize), S2 = mask,
S1 = contextual quasi-identifier.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Sensitivity(Enum):
    S1 = 1  # contextual / quasi-identifier (name, DOB)
    S2 = 2  # mask by default
    S3 = 3  # highest: fail-safe, block or tokenize


class Action(Enum):
    ALLOW = "allow"
    MASK = "mask"
    TOKENIZE = "tokenize"
    BLOCK = "block"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class PIIClass:
    code: str
    label: str
    group: str
    sensitivity: Sensitivity
    default_action: Action
    #: name of the deterministic validator in ``kavach.validators`` (if any)
    validator: str | None = None


REGISTRY: dict[str, PIIClass] = {}


def _register(cls: PIIClass) -> PIIClass:
    if cls.code in REGISTRY:
        raise ValueError(f"duplicate PII class code: {cls.code}")
    REGISTRY[cls.code] = cls
    return cls


# --- Government identifiers -------------------------------------------------
AADHAAR = _register(PIIClass("AADHAAR", "Aadhaar / UID", "government", Sensitivity.S3, Action.TOKENIZE, "is_aadhaar"))
PAN = _register(PIIClass("PAN", "PAN", "government", Sensitivity.S3, Action.MASK, "is_pan"))
GSTIN = _register(PIIClass("GSTIN", "GSTIN", "government", Sensitivity.S2, Action.MASK, "is_gstin"))
VOTER = _register(PIIClass("VOTER_EPIC", "Voter EPIC", "government", Sensitivity.S2, Action.MASK, None))
DL = _register(PIIClass("DRIVING_LICENCE", "Driving Licence", "government", Sensitivity.S2, Action.MASK, None))
PASSPORT = _register(PIIClass("PASSPORT", "Passport", "government", Sensitivity.S2, Action.MASK, None))

# --- Financial --------------------------------------------------------------
CARD = _register(PIIClass("CARD_PAN", "Payment card number", "financial", Sensitivity.S3, Action.TOKENIZE, "luhn_validate"))
CVV = _register(PIIClass("CVV", "Card CVV", "financial", Sensitivity.S3, Action.BLOCK, None))
BANK_ACC = _register(PIIClass("BANK_ACCOUNT", "Bank account number", "financial", Sensitivity.S3, Action.TOKENIZE, None))
IFSC = _register(PIIClass("IFSC", "IFSC code", "financial", Sensitivity.S2, Action.MASK, "is_ifsc"))
UPI_VPA = _register(PIIClass("UPI_VPA", "UPI VPA", "financial", Sensitivity.S3, Action.MASK, "is_upi_vpa"))

# --- Contact / identity -----------------------------------------------------
PHONE = _register(PIIClass("PHONE", "Phone number", "contact", Sensitivity.S2, Action.MASK, None))
EMAIL = _register(PIIClass("EMAIL", "Email", "contact", Sensitivity.S2, Action.MASK, None))
ADDRESS = _register(PIIClass("ADDRESS", "Postal address", "contact", Sensitivity.S2, Action.MASK, None))
NAME = _register(PIIClass("NAME", "Person name", "contact", Sensitivity.S1, Action.ALLOW, None))
DOB = _register(PIIClass("DOB", "Date of birth", "contact", Sensitivity.S1, Action.MASK, None))

# --- Sensitive-category / biometric ----------------------------------------
ABHA = _register(PIIClass("ABHA", "ABHA health ID / record", "health", Sensitivity.S3, Action.BLOCK, None))
BIOMETRIC = _register(PIIClass("BIOMETRIC", "Face / fingerprint", "biometric", Sensitivity.S3, Action.BLOCK, None))
VOICEPRINT = _register(PIIClass("VOICEPRINT", "Voiceprint (call audio)", "biometric", Sensitivity.S3, Action.ESCALATE, None))

# --- Secrets (credentials proper) -------------------------------------------
OTP = _register(PIIClass("OTP", "One-time passcode", "secret", Sensitivity.S3, Action.BLOCK, None))
SECRET = _register(PIIClass("SECRET", "Password / API key / token", "secret", Sensitivity.S3, Action.BLOCK, None))


def by_group(group: str) -> list[PIIClass]:
    return [c for c in REGISTRY.values() if c.group == group]
