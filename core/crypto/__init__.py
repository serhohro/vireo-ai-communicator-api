"""
Vireo Crypto Module v3.1

Provides:
- RFC 8785 JSON Canonicalization
- BLAKE2b-256 hashing
- Ed25519 signing/verification
- Canonical wire byte encoding
"""

from .canonical import (
    jcs_serialize,
    canonical_wire_bytes,
    parse_wire_bytes,
    INTENT,
    REVERSE_INTENT,
    WIRE_MAGIC,
    WIRE_VERSION,
    HEADER_SIZE,
)
from .blake2b import (
    DIGEST_SIZE,
    blake2b_256,
    payload_hash,
    wire_hash,
    did_hash,
    hash_bytes,
    hash_payload,
)
from .ed25519 import (
    generate_keypair,
    sign_vireo_message,
    verify_vireo_message,
)

__all__ = [
    # Canonical
    "jcs_serialize",
    "canonical_wire_bytes",
    "parse_wire_bytes",
    "INTENT",
    "REVERSE_INTENT",
    "WIRE_MAGIC",
    "WIRE_VERSION",
    "HEADER_SIZE",

    # Hashing
    "DIGEST_SIZE",
    "blake2b_256",
    "payload_hash",
    "wire_hash",
    "did_hash",
    "hash_bytes",
    "hash_payload",

    # Ed25519
    "generate_keypair",
    "sign_vireo_message",
    "verify_vireo_message",
]

__version__ = "3.1.0"