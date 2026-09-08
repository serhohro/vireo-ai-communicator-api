"""
Vireo Core Module

Core types, cryptography, identity management, protocol state machine,
and sandbox execution for Vireo v3.0.0.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from .types import (
    VireoType,
    VireoValue,
    VireoObject,
    VireoArray,
    VireoString,
    VireoInteger,
    VireoFloat,
    VireoBoolean,
    VireoNull,
    VireoBinary,
    VireoTimestamp,
    VireoDuration,
    VireoURI,
    VireoUUID,
    VireoDID,
    VireoSignature,
    VireoPublicKey,
    VireoPrivateKey,
    VireoHash,
    VireoNonce,
    VireoVersion,
)

from .errors import (
    VireoError,
    VireoProtocolError,
    VireoCryptoError,
    VireoValidationError,
    VireoSerializationError,
    VireoIdentityError,
    VireoTrustError,
    VireoSandboxError,
    VireoStateError,
    VireoVersionError,
    VireoNonceError,
    VireoSignatureError,
    VireoKeyError,
)

from .config import (
    VireoConfig,
    load_config,
    get_config,
    set_config,
    reset_config,
    DEFAULT_CONFIG,
    Environment,
    LogLevel,
)

from .identity import (
    DID,
    DIDDocument,
    KeyManager,
    TrustBootstrap,
    ReputationSystem,
    TrustLevel,
    ReputationScore,
)

from .protocol import (
    ProtocolState,
    ProtocolStateMachine,
    Message,
    MessageType,
    MessageValidator,
    NonceManager,
    VersionManager,
    ProtocolError,
)

from .crypto import (
    Ed25519,
    BLAKE2b,
    Hash,
    HashAlgorithm,
    verify_signature,
    sign_message,
    generate_keypair,
    hash_data,
)

from .sandbox import (
    SandboxLevel,
    SandboxLevel1,
    SandboxLevel2,
    SandboxLevel3,
    SandboxExecutor,
    SandboxResult,
    SandboxError,
)

__version__ = "3.0.0"
__author__ = "Serhii (serhohro)"

__all__ = [
    # Types
    "VireoType",
    "VireoValue",
    "VireoObject",
    "VireoArray",
    "VireoString",
    "VireoInteger",
    "VireoFloat",
    "VireoBoolean",
    "VireoNull",
    "VireoBinary",
    "VireoTimestamp",
    "VireoDuration",
    "VireoURI",
    "VireoUUID",
    "VireoDID",
    "VireoSignature",
    "VireoPublicKey",
    "VireoPrivateKey",
    "VireoHash",
    "VireoNonce",
    "VireoVersion",
    # Errors
    "VireoError",
    "VireoProtocolError",
    "VireoCryptoError",
    "VireoValidationError",
    "VireoSerializationError",
    "VireoIdentityError",
    "VireoTrustError",
    "VireoSandboxError",
    "VireoStateError",
    "VireoVersionError",
    "VireoNonceError",
    "VireoSignatureError",
    "VireoKeyError",
    # Config
    "VireoConfig",
    "load_config",
    "get_config",
    "set_config",
    "reset_config",
    "DEFAULT_CONFIG",
    "Environment",
    "LogLevel",
    # Identity
    "DID",
    "DIDDocument",
    "KeyManager",
    "TrustBootstrap",
    "ReputationSystem",
    "TrustLevel",
    "ReputationScore",
    # Protocol
    "ProtocolState",
    "ProtocolStateMachine",
    "Message",
    "MessageType",
    "MessageValidator",
    "NonceManager",
    "VersionManager",
    "ProtocolError",
    # Crypto
    "Ed25519",
    "BLAKE2b",
    "Hash",
    "HashAlgorithm",
    "verify_signature",
    "sign_message",
    "generate_keypair",
    "hash_data",
    # Sandbox
    "SandboxLevel",
    "SandboxLevel1",
    "SandboxLevel2",
    "SandboxLevel3",
    "SandboxExecutor",
    "SandboxResult",
    "SandboxError",
]