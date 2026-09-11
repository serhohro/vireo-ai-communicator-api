"""
Vireo Signature Verification v3.1.

Replaces mock `valid: True` with real Ed25519 verification.
"""

from core.crypto.canonical import canonical_wire_bytes
from core.crypto.ed25519 import verify_vireo_message
from core.identity.did import resolve_public_key
from core.protocol.validator import validate_envelope


def verify_vireo_signature(request_data: dict) -> dict:
    """
    Verify a signed Vireo envelope.

    request_data:
        {
            "envelope": dict,
            "signature": hex str,
            "sender_did": str
        }

    Returns:
        {"valid": bool, "error": str | None, "sender_did": str | None}
    """
    signature_hex = request_data.get("signature")
    if not signature_hex:
        return {"valid": False, "error": "Missing signature", "sender_did": None}

    envelope = request_data.get("envelope")
    if not envelope:
        return {"valid": False, "error": "Missing envelope", "sender_did": None}

    sender_did = request_data.get("sender_did")
    if not sender_did:
        return {"valid": False, "error": "Missing sender_did", "sender_did": None}

    ok, err = validate_envelope(envelope)
    if not ok:
        return {"valid": False, "error": f"Invalid envelope: {err}", "sender_did": sender_did}

    public_key_hex = resolve_public_key(sender_did)
    if not public_key_hex:
        return {
            "valid": False,
            "error": f"Cannot resolve public key for {sender_did}",
            "sender_did": sender_did,
        }

    try:
        canonical_bytes = canonical_wire_bytes(envelope)
    except (ValueError, TypeError) as e:
        return {
            "valid": False,
            "error": f"Canonical encoding failed: {e}",
            "sender_did": sender_did,
        }

    valid, verr = verify_vireo_message(public_key_hex, canonical_bytes, signature_hex)
    return {"valid": valid, "error": verr, "sender_did": sender_did}