"""Reversible token vault (thin slice of District D4).

In-memory, deterministic tokenization so a downstream tool still receives a
stable placeholder and authorised callers can reverse it. The production vault
is KMS/HSM-backed with RBAC on de-tokenization; this is the interface.
"""
from __future__ import annotations


class TokenVault:
    def __init__(self) -> None:
        self._fwd: dict[tuple[str, str], str] = {}
        self._rev: dict[str, str] = {}
        self._n = 0

    def tokenize(self, cls: str, value: str) -> str:
        key = (cls, value)
        tok = self._fwd.get(key)
        if tok is None:
            self._n += 1
            tok = f"<{cls}:tok{self._n:04d}>"
            self._fwd[key] = tok
            self._rev[tok] = value
        return tok

    def detokenize(self, token: str) -> str | None:
        """Reverse a token (RBAC-gated in production)."""
        return self._rev.get(token)

    def __len__(self) -> int:
        return len(self._rev)
