# [file name]: src/crypto/__init__.py
# ============================================================
# VIREO CRYPTOGRAPHY PACKAGE
# ============================================================
"""
Cryptographic primitives for Vireo.

Provides:
- Ed25519 signatures (non-repudiation)
- W3C DID (Decentralized Identifiers)
- Zero-Trust protocol with nonce protection
"""

from .ed25519 import Ed25519Crypto
from .did import DIDManager
from .trust import TrustManager

__all__ = [
    "Ed25519Crypto",
    "DIDManager",
    "TrustManager",
]