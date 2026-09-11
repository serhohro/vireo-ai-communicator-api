"""
Vireo Core v3.1

Central module for protocol, crypto, identity, and sandbox.
"""

from .config import config

from .crypto import (
    jcs_serialize, canonical_wire_bytes, parse_wire_bytes,
    blake2b_256, payload_hash, wire_hash, did_hash,
    generate_keypair, sign_vireo_message, verify_vireo_message,
)

from .protocol import (
    ProtocolState, VireoStateMachine, IllegalTransitionError,
    TERMINAL_STATES, verify_vireo_signature, NonceManager,
    VireoMessage, validate_envelope, PROTOCOL_VERSION, WIRE_VERSION,
)

from .identity import (
    make_did, resolve_public_key, register_did,
    get_did_document, list_dids,
    KeyManager, TrustBootstrap, Reputation,
)

__all__ = [
    "config",
    "jcs_serialize", "canonical_wire_bytes", "parse_wire_bytes",
    "blake2b_256", "payload_hash", "wire_hash", "did_hash",
    "generate_keypair", "sign_vireo_message", "verify_vireo_message",
    "ProtocolState", "VireoStateMachine", "IllegalTransitionError",
    "TERMINAL_STATES", "verify_vireo_signature", "NonceManager",
    "VireoMessage", "validate_envelope", "PROTOCOL_VERSION", "WIRE_VERSION",
    "make_did", "resolve_public_key", "register_did",
    "get_did_document", "list_dids",
    "KeyManager", "TrustBootstrap", "Reputation",
]

__version__ = "3.1.0"
