"""
Vireo DID v3.1 — minimal DID implementation.

Format:
    did:vireo:<base64url(BLAKE2b-256("agent:name"))>

Resolution:
    - In-memory registry (this module)
    - JSON file (config.DID_REGISTRY_PATH)
    - Static HTTP: /.well-known/did.json (future)
"""

import base64
import json
import threading
import time
from pathlib import Path
from typing import Optional

from core.config import config
from core.crypto.hashing import blake2b_256, did_hash


_REGISTRY: dict[str, dict] = {}
_REGISTRY_LOCK = threading.Lock()
_LOADED = False


def make_did(name: str) -> str:
    """Derive a Vireo DID from an agent name."""
    h = blake2b_256(name.encode("utf-8"))
    encoded = base64.urlsafe_b64encode(h).rstrip(b"=").decode("ascii")
    return f"did:vireo:{encoded}"


def _load_registry() -> None:
    global _LOADED
    if _LOADED:
        return
    with _REGISTRY_LOCK:
        if _LOADED:
            return
        path = Path(config.DID_REGISTRY_PATH)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                _REGISTRY.update(data)
            except Exception:
                pass
        _LOADED = True


def _save_registry() -> None:
    path = Path(config.DID_REGISTRY_PATH)
    try:
        path.write_text(json.dumps(_REGISTRY, indent=2), encoding="utf-8")
    except Exception:
        pass


def register_did(
    did: str,
    public_key_hex: str,
    name: str = "",
    endpoint: str = "",
) -> dict:
    """Register or update a DID entry."""
    _load_registry()
    with _REGISTRY_LOCK:
        _REGISTRY[did] = {
            "did": did,
            "name": name,
            "public_key_hex": public_key_hex,
            "endpoint": endpoint,
            "registered_at": int(time.time() * 1000),
        }
        _save_registry()
        return _REGISTRY[did]


def resolve_public_key(did: str) -> Optional[str]:
    """Resolve a DID to its Ed25519 public key hex."""
    _load_registry()
    with _REGISTRY_LOCK:
        entry = _REGISTRY.get(did)
        if entry:
            return entry.get("public_key_hex")
    return None


def get_did_document(did: str) -> Optional[dict]:
    """Return a minimal DID document for the given DID."""
    _load_registry()
    with _REGISTRY_LOCK:
        entry = _REGISTRY.get(did)
        if not entry:
            return None
        return {
            "did": did,
            "publicKeys": [{
                "id": f"{did}#keys-1",
                "type": "Ed25519VerificationKey2020",
                "publicKeyHex": entry["public_key_hex"],
            }],
            "service": [{
                "id": f"{did}#endpoint",
                "type": "VireoEndpoint",
                "serviceEndpoint": entry.get("endpoint", ""),
            }],
            "registered_at": entry.get("registered_at", 0),
        }


def list_dids() -> list[dict]:
    _load_registry()
    with _REGISTRY_LOCK:
        return list(_REGISTRY.values())


def did_to_hash(did: str) -> bytes:
    return did_hash(did)


DID_REGISTRY = _REGISTRY