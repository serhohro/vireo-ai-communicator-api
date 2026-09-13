"""
Vireo Trust Bootstrap v3.1.

Real challenge-response protocol.
Replaces the mock `trust_level: "full"` endpoint.
"""

import os
import time
import threading
from typing import Optional

from core.crypto.ed25519 import verify_vireo_message
from core.crypto.hashing import wire_hash
from core.identity.did import resolve_public_key


class TrustBootstrap:
    """
    Two-phase trust establishment:
      1. Agent A sends challenge(nonce) to Agent B.
      2. Agent B signs challenge with its Ed25519 key.
      3. Agent A verifies signature against B's DID public key.
    """

    def __init__(self):
        self._challenges: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._trusted: dict[tuple[str, str], dict] = {}

    def create_challenge(self, initiator_did: str, responder_did: str) -> dict:
        challenge = os.urandom(32)
        with self._lock:
            self._challenges[challenge.hex()] = {
                "initiator_did": initiator_did,
                "responder_did": responder_did,
                "created_at": int(time.time() * 1000),
            }
        return {
            "challenge_hex": challenge.hex(),
            "initiator_did": initiator_did,
            "responder_did": responder_did,
        }

    def respond_to_challenge(
        self,
        challenge_hex: str,
        responder_did: str,
        signature_hex: str,
    ) -> dict:
        with self._lock:
            entry = self._challenges.get(challenge_hex)
            if not entry:
                return {"trusted": False, "error": "unknown challenge"}

            if entry["responder_did"] != responder_did:
                return {"trusted": False, "error": "responder_did mismatch"}

            # Expiry: 5 min
            if time.time() * 1000 - entry["created_at"] > 5 * 60 * 1000:
                del self._challenges[challenge_hex]
                return {"trusted": False, "error": "challenge expired"}

            public_key_hex = resolve_public_key(responder_did)
            if not public_key_hex:
                return {"trusted": False, "error": "cannot resolve responder public key"}

            # Signature is over the challenge bytes directly
            challenge_bytes = bytes.fromhex(challenge_hex)
            h = wire_hash(challenge_bytes)
            # We reuse verify_vireo_message with canonical_bytes = challenge_bytes
            valid, err = verify_vireo_message(public_key_hex, challenge_bytes, signature_hex)
            if not valid:
                return {"trusted": False, "error": f"signature invalid: {err}"}

            # Record trust
            key = (entry["initiator_did"], responder_did)
            self._trusted[key] = {
                "trusted_at": int(time.time() * 1000),
                "challenge_hex": challenge_hex,
            }
            del self._challenges[challenge_hex]
            return {
                "trusted": True,
                "initiator_did": entry["initiator_did"],
                "responder_did": responder_did,
            }

    def is_trusted(self, did_a: str, did_b: str) -> bool:
        with self._lock:
            return (did_a, did_b) in self._trusted or (did_b, did_a) in self._trusted

    def list_trusted(self) -> list[dict]:
        with self._lock:
            return [
                {"initiator_did": a, "responder_did": b, **v}
                for (a, b), v in self._trusted.items()
            ]


_default: Optional[TrustBootstrap] = None
_lock = threading.Lock()


def get_trust_bootstrap() -> TrustBootstrap:
    global _default
    if _default is None:
        with _lock:
            if _default is None:
                _default = TrustBootstrap()
    return _default