"""
Vireo Protocol Module

Protocol state machine, messaging, and validation.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from .state import (
    ProtocolState,
    ProtocolStateMachine,
    StateTransition,
    StateError,
    InvalidTransitionError,
)

from .message import (
    Message,
    MessageType,
    MessageHeader,
    MessageBody,
    MessageEnvelope,
    MessageBuilder,
    MessageParser,
)

from .validator import (
    MessageValidator,
    ValidationResult,
    ValidationRule,
    ValidatorRegistry,
    MessageSchema,
)

from .nonce_manager import (
    NonceManager,
    NonceStorage,
    InMemoryNonceStorage,
    RedisNonceStorage,
    NonceError,
)

from .version import (
    VersionManager,
    VersionInfo,
    VersionConstraint,
    VersionCompatibility,
)

__all__ = [
    # State
    "ProtocolState",
    "ProtocolStateMachine",
    "StateTransition",
    "StateError",
    "InvalidTransitionError",
    # Message
    "Message",
    "MessageType",
    "MessageHeader",
    "MessageBody",
    "MessageEnvelope",
    "MessageBuilder",
    "MessageParser",
    # Validator
    "MessageValidator",
    "ValidationResult",
    "ValidationRule",
    "ValidatorRegistry",
    "MessageSchema",
    # Nonce
    "NonceManager",
    "NonceStorage",
    "InMemoryNonceStorage",
    "RedisNonceStorage",
    "NonceError",
    # Version
    "VersionManager",
    "VersionInfo",
    "VersionConstraint",
    "VersionCompatibility",
]