"""
Generic hashing module for Vireo v3.1.

This module exists for backward compatibility with the v3.0.0 structure.
It re-exports everything from `blake2b.py`.

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