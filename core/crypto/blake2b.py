"""
BLAKE2b-256 hashing for Vireo v3.1.

Why BLAKE2b over SHA-256:
- ~3x faster
- Deterministic by default (no padding ambiguities)
- No length-extension attacks
- Cross-language:
    - Python:  hashlib.blake2b
    - Rust:    blake2 crate
    - TypeScript: @noble/hashes

Reference: RFC 7693
"""

import hashlib

# BLAKE2b-256 digest size
DIGEST_SIZE = 32


def blake2b_256(data: bytes) -> bytes:
    """
    Compute BLAKE2b-256 hash of arbitrary bytes.

    Args:
        data: input bytes

    Returns:
        32-byte digest

    Raises:
        TypeError: if data is not bytes-like
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(
            f"blake2b_256 requires bytes, got {type(data).__name__}"
        )
    return hashlib.blake2b(bytes(data), digest_size=DIGEST_SIZE).digest()


def payload_hash(payload_bytes: bytes) -> bytes:
    """Hash of the opaque payload inside the envelope."""
    return blake2b_256(payload_bytes)


def wire_hash(canonical_bytes: bytes) -> bytes:
    """Hash of the canonical wire bytes. This is what Ed25519 signs."""
    return blake2b_256(canonical_bytes)


def did_hash(did_string: str) -> bytes:
    """Hash of a DID string for the wire header (32 bytes)."""
    if not isinstance(did_string, str):
        raise TypeError(
            f"did_hash requires str, got {type(did_string).__name__}"
        )
    return blake2b_256(did_string.encode("utf-8"))


# Backward-compat aliases
hash_bytes = blake2b_256
hash_payload = payload_hash


__all__ = [
    "DIGEST_SIZE",
    "blake2b_256",
    "payload_hash",
    "wire_hash",
    "did_hash",
    "hash_bytes",
    "hash_payload",
]