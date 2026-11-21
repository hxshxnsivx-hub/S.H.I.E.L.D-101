"""Reversible token vault (District D4).

In-memory, deterministic tokenization so a downstream tool still receives a
stable placeholder and authorised callers can reverse it. De-tokenization is
**RBAC-gated**: set ``require_role`` and callers must present it. The production
vault swaps the storage for a KMS/HSM backend — implement ``VaultBackend`` and
pass it in; the engine only calls ``tokenize``.
"""
from __future__ import annotations

from typing import Protocol


class VaultBackend(Protocol):
    """Storage interface — the seam where a KMS/HSM implementation plugs in."""

    def put(self, token: str, value: str) -> None: ...
    def get(self, token: str) -> str | None: ...


class _MemoryBackend:
    def __init__(self) -> None:
        self._m: dict[str, str] = {}

    def put(self, token: str, value: str) -> None:
        self._m[token] = value

    def get(self, token: str) -> str | None:
        return self._m.get(token)


class TokenVault:
    def __init__(self, backend: VaultBackend | None = None, require_role: str | None = None) -> None:
        self._backend = backend or _MemoryBackend()
        self._fwd: dict[tuple[str, str], str] = {}
        self._n = 0
        #: if set, detokenize() requires this role (RBAC)
        self.require_role = require_role

    def tokenize(self, cls: str, value: str) -> str:
        key = (cls, value)
        tok = self._fwd.get(key)
        if tok is None:
            self._n += 1
            tok = f"<{cls}:tok{self._n:04d}>"
            self._fwd[key] = tok
            self._backend.put(tok, value)
        return tok

    def detokenize(self, token: str, role: str | None = None) -> str | None:
        """Reverse a token. RBAC-gated when ``require_role`` is set."""
        if self.require_role is not None and role != self.require_role:
            raise PermissionError("de-tokenization not authorised for this role")
        return self._backend.get(token)

    def __len__(self) -> int:
        return len(self._fwd)
