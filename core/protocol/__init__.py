"""
Vireo Protocol Core v3.1

Central protocol module:
- State machine (VireoStateMachine, ProtocolState)
- Signature verification
- Nonce replay protection
- Message wrapper
- Version constants

Exports:
    ProtocolState          — 12 lifecycle states
    VireoStateMachine      — physically forbids illegal transitions
    IllegalTransitionError — raised on illegal transition
    TERMINAL_STATES        — frozenset of terminal states
    verify_vireo_signature — real Ed25519 verification
    NonceManager           — SQLite-backed replay protection
    VireoMessage           — high-level envelope + signature wrapper
    validate_envelope      — structural validation
    PROTOCOL_VERSION       — "3.1"
    WIRE_VERSION           — 0x0301
"""

from .state import (
    ProtocolState,
    VireoStateMachine,
    IllegalTransitionError,
    TERMINAL_STATES,
)
from .verification import verify_vireo_signature
from .nonce_manager import NonceManager
from .message import VireoMessage
from .validator import validate_envelope
from .version import PROTOCOL_VERSION, WIRE_VERSION

__all__ = [
    # State
    "ProtocolState",
    "VireoStateMachine",
    "IllegalTransitionError",
    "TERMINAL_STATES",

    # Verification
    "verify_vireo_signature",

    # Nonce
    "NonceManager",

    # Message
    "VireoMessage",

    # Validation
    "validate_envelope",

    # Version
    "PROTOCOL_VERSION",
    "WIRE_VERSION",
]

__version__ = "3.1.0"