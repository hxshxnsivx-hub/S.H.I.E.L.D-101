"""Kavach — agent data-firewall for Indian PII & credentials.

District D7 (Phase 0): the PII taxonomy and the deterministic validator
library that gives the detection pipeline its high-precision first pass.
"""
from .taxonomy import Sensitivity, Action, PIIClass, REGISTRY
from . import validators
from .sdk import Kavach, KavachBlocked, GuardResult
from .policy import Trust, TrustRegistry, Policy
from .audit import AuditLog

__version__ = "0.0.1"
__all__ = [
    "Sensitivity", "Action", "PIIClass", "REGISTRY", "validators",
    "Kavach", "KavachBlocked", "GuardResult", "Trust", "TrustRegistry", "Policy",
    "AuditLog", "__version__",
]
