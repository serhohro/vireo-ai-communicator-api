"""
Backward-compat shim for `core.crypto.hashing`.

This module exists for backward compatibility with the v3.1 code
that referenced `core.crypto.hashing`. It redirects to `core.crypto.blake2b`.

Prefer importing directly from `core.crypto.blake2b`.
"""

from .blake2b import (
    DIGEST_SIZE,
    blake2b_256,
    payload_hash,
    wire_hash,
    did_hash,
    hash_bytes,
    hash_payload,
)

__all__ = [
    "DIGEST_SIZE",
    "blake2b_256",
    "payload_hash",
    "wire_hash",
    "did_hash",
    "hash_bytes",
    "hash_payload",
]