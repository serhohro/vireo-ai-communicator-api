"""
Vireo Message v3.1 — high-level envelope + signature wrapper.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import time
import os

from core.crypto.canonical import canonical_wire_bytes, parse_wire_bytes
from core.crypto.ed25519 import sign_vireo_message, verify_vireo_message
from core.crypto.hashing import did_hash


@dataclass
class VireoMessage:
    intent: str
    payload: dict[str, Any]
    sender_did: str
    recipient_did: str
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    nonce: bytes = field(default_factory=lambda: os.urandom(16))
    signature_hex: Optional[str] = None

    @property
    def envelope(self) -> dict:
        return {
            "intent": self.intent,
            "timestamp_ms": self.timestamp_ms,
            "nonce": self.nonce,
            "sender_did_hash": did_hash(self.sender_did),
            "recipient_did_hash": did_hash(self.recipient_did),
            "payload": self.payload,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_wire_bytes(self.envelope)

    def sign(self, private_key_hex: str) -> "VireoMessage":
        self.signature_hex = sign_vireo_message(
            private_key_hex, self.canonical_bytes()
        )
        return self

    def to_wire(self) -> bytes:
        return self.canonical_bytes()

    def to_dict(self) -> dict:
        return {
            "envelope": {
                "intent": self.intent,
                "timestamp_ms": self.timestamp_ms,
                "nonce": self.nonce.hex(),
                "sender_did_hash": did_hash(self.sender_did).hex(),
                "recipient_did_hash": did_hash(self.recipient_did).hex(),
                "payload": self.payload,
            },
            "signature": self.signature_hex,
            "sender_did": self.sender_did,
            "recipient_did": self.recipient_did,
        }

    @classmethod
    def from_wire(cls, data: bytes) -> "VireoMessage":
        env = parse_wire_bytes(data)
        return cls(
            intent=env["intent"],
            payload=env["payload"],
            sender_did="",         # unknown until signature resolved
            recipient_did="",
            timestamp_ms=env["timestamp_ms"],
            nonce=env["nonce"],
        )

    @classmethod
    def from_dict(cls, d: dict) -> "VireoMessage":
        env = d["envelope"]
        return cls(
            intent=env["intent"],
            payload=env["payload"],
            sender_did=d.get("sender_did", ""),
            recipient_did=d.get("recipient_did", ""),
            timestamp_ms=env["timestamp_ms"],
            nonce=bytes.fromhex(env["nonce"]) if isinstance(env["nonce"], str) else env["nonce"],
            signature_hex=d.get("signature"),
        )