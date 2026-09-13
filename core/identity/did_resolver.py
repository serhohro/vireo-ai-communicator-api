"""
Minimal DID resolution for Vireo v3.1.

DID format:
    did:vireo:<base58(BLAKE2b-256("agent:name"))>

Resolution strategy:
1. Static HTTP: https://<host>/.well-known/did.json
2. Local cache (in-memory)
3. Fallback: embedded public key in first message

This is NOT a full W3C DID implementation.
See specification/CRYPTO_v3.1.md for full schema.
"""

import base64
import json
import threading
import urllib.request
from typing import Optional

from core.crypto.hashing import did_hash, blake2b_256


# In-memory cache: did -> {public_key_hex, endpoint, fetched_at}
_CACHE: dict[str, dict] = {}
_CACHE_LOCK = threading.Lock()
CACHE_TTL_SEC = 3600


def make_did(name: str) -> str:
    """
    Derive a Vireo DID from an agent name.

    Example:
        make_did("agent:alice") -> "did:vireo:abc123..."
    """
    h = blake2b_256(name.encode("utf-8"))
    encoded = base64.urlsafe_b64encode(h).rstrip(b"=").decode("ascii")
    return f"did:vireo:{encoded}"


def did_to_hash(did: str) -> bytes:
    """Convert DID to its 32-byte BLAKE2b hash for wire header."""
    return did_hash(did)


def resolve_public_key(did: str) -> Optional[str]:
    """
    Resolve a DID to a public key hex string.

    Returns None if resolution fails.
    """
    cached = _get_cached(did)
    if cached is not None:
        return cached

    endpoint = _did_to_well_known_url(did)
    if endpoint is None:
        return None

    try:
        with urllib.request.urlopen(endpoint, timeout=5) as resp:
            doc = json.loads(resp.read().decode("utf-8"))
        public_key_hex = _extract_public_key(doc, did)
        if public_key_hex:
            _set_cached(did, public_key_hex, endpoint)
        return public_key_hex
    except Exception:
        return None


def register_local(did: str, public_key_hex: str, endpoint: str = "") -> None:
    """
    Register a DID locally (for tests and air-gapped deployments).
    """
    _set_cached(did, public_key_hex, endpoint)


def _did_to_well_known_url(did: str) -> Optional[str]:
    """For now, we don't have a universal resolver. Return None."""
    return None


def _extract_public_key(doc: dict, did: str) -> Optional[str]:
    """Extract first Ed25519VerificationKey2020 from a DID document."""
    keys = doc.get("publicKeys") or doc.get("verificationMethod") or []
    for key in keys:
        if key.get("type") in (
            "Ed25519VerificationKey2020",
            "Ed25519VerificationKey2018",
        ):
            if "publicKeyHex" in key:
                return key["publicKeyHex"]
            if "publicKeyBase58" in key:
                # Convert base58 to hex
                try:
                    import base58
                    return base58.b58decode(key["publicKeyBase58"]).hex()
                except ImportError:
                    return None
    return None


def _get_cached(did: str) -> Optional[str]:
    import time
    with _CACHE_LOCK:
        entry = _CACHE.get(did)
        if entry and time.time() - entry["fetched_at"] < CACHE_TTL_SEC:
            return entry["public_key_hex"]
    return None


def _set_cached(did: str, public_key_hex: str, endpoint: str) -> None:
    import time
    with _CACHE_LOCK:
        _CACHE[did] = {
            "public_key_hex": public_key_hex,