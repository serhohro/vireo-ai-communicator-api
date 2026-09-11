"""
Vireo Core Errors v3.1
"""


class VireoError(Exception):
    """Base class for all Vireo errors."""


class WireFormatError(VireoError):
    """Malformed wire bytes."""


class CanonicalizationError(VireoError):
    """RFC 8785 canonicalization failure."""


class CryptoError(VireoError):
    """Signature or hash failure."""


class IllegalTransitionError(VireoError):
    """Illegal state machine transition."""

    def __init__(self, current, attempted):
        from core.protocol.state import ProtocolState
        cur_v = current.value if isinstance(current, ProtocolState) else str(current)
        att_v = attempted.value if isinstance(attempted, ProtocolState) else str(attempted)
        super().__init__(f"Illegal transition: {cur_v} → {att_v}")
        self.current = current
        self.attempted = attempted


class ReplayError(VireoError):
    """Nonce replay detected."""


class TrustError(VireoError):
    """Trust establishment failure."""


class DIDError(VireoError):
    """DID resolution failure."""