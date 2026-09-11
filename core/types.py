"""
Vireo Core Types v3.1

Shared type definitions used across core, protocol, and API layers.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Intent(str, Enum):
    """Wire-level intent (state transition request)."""
    DISCOVER  = "DISCOVER"
    PROPOSE   = "PROPOSE"
    NEGOTIATE = "NEGOTIATE"
    COMMIT    = "COMMIT"
    REJECT    = "REJECT"
    EXECUTE   = "EXECUTE"
    VERIFY    = "VERIFY"
    DONE      = "DONE"
    ESCALATED = "ESCALATED"
    CANCELLED = "CANCELLED"
    FAILED    = "FAILED"
    TIMEOUT   = "TIMEOUT"


@dataclass
class Envelope:
    """
    Vireo wire envelope. Canonical representation is:
        header (96 bytes) + payload_len (4B) + payload_bytes
    """
    intent: Intent
    timestamp_ms: int
    nonce: bytes                # 16 bytes
    sender_did_hash: bytes      # 32 bytes
    recipient_did_hash: bytes   # 32 bytes
    payload: dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "intent": self.intent.value if isinstance(self.intent, Intent) else self.intent,
            "timestamp_ms": self.timestamp_ms,
            "nonce": self.nonce.hex() if isinstance(self.nonce, bytes) else self.nonce,
            "sender_did_hash": self.sender_did_hash.hex() if isinstance(self.sender_did_hash, bytes) else self.sender_did_hash,
            "recipient_did_hash": self.recipient_did_hash.hex() if isinstance(self.recipient_did_hash, bytes) else self.recipient_did_hash,
            "payload": self.payload,
        }


@dataclass
class SignedEnvelope:
    """Envelope + signature + sender DID."""
    envelope: Envelope
    signature_hex: str
    sender_did: str


@dataclass
class VerificationResult:
    valid: bool
    error: Optional[str] = None
    sender_did: Optional[str] = None


@dataclass
class AgentRecord:
    did: str
    name: str
    public_key_hex: str
    capabilities: list[str] = field(default_factory=list)
    endpoint: str = ""
    registered_at: int = 0