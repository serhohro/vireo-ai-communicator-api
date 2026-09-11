"""
Vireo Envelope Validator v3.1.
"""

from core.config import config


REQUIRED_FIELDS = (
    "intent", "timestamp_ms", "nonce",
    "sender_did_hash", "recipient_did_hash", "payload",
)


def validate_envelope(envelope: dict) -> tuple[bool, str | None]:
    """Basic structural validation before canonicalization."""
    if not isinstance(envelope, dict):
        return False, "envelope must be a dict"

    for f in REQUIRED_FIELDS:
        if f not in envelope:
            return False, f"missing field: {f}"

    if not isinstance(envelope["intent"], str):
        return False, "intent must be str"

    if not isinstance(envelope["timestamp_ms"], int):
        return False, "timestamp_ms must be int"

    nonce = envelope["nonce"]
    if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != 16:
        return False, f"nonce must be 16 bytes, got {len(nonce) if hasattr(nonce, '__len__') else type(nonce)}"

    for f in ("sender_did_hash", "recipient_did_hash"):
        if not isinstance(envelope[f], (bytes, bytearray)) or len(envelope[f]) != 32:
            return False, f"{f} must be 32 bytes"

    if not isinstance(envelope["payload"], dict):
        return False, "payload must be dict"

    return True, None