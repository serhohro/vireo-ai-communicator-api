"""
Vireo Identity Module

Decentralized Identity (DID), key management, trust bootstrap, and reputation.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from .did import (
    DID,
    DIDDocument,
    DIDMethod,
    DIDResolver,
    DIDRegistry,
    ServiceEndpoint,
    VerificationMethod,
    Authentication,
    AssertionMethod,
    KeyAgreement,
    CapabilityInvocation,
    CapabilityDelegation,
)

from .key_manager import (
    KeyManager,
    KeyPair,
    KeyUsage,
    KeyState,
    KeyMetadata,
    KeyRotationPolicy,
    KeyStorage,
    InMemoryKeyStorage,
    FileKeyStorage,
)

from .trust_bootstrap import (
    TrustBootstrap,
    TrustAnchor,
    TrustChain,
    TrustVerification,
    TrustLevel,
    BootstrapMethod,
    Certificate,
    CertificateChain,
)

from .reputation import (
    ReputationSystem,
    ReputationScore,
    ReputationEvent,
    ReputationEventType,
    ReputationFactor,
    ReputationCalculator,
    ReputationStorage,
)

__all__ = [
    # DID
    "DID",
    "DIDDocument",
    "DIDMethod",
    "DIDResolver",
    "DIDRegistry",
    "ServiceEndpoint",
    "VerificationMethod",
    "Authentication",
    "AssertionMethod",
    "KeyAgreement",
    "CapabilityInvocation",
    "CapabilityDelegation",
    # Key Manager
    "KeyManager",
    "KeyPair",
    "KeyUsage",
    "KeyState",
    "KeyMetadata",
    "KeyRotationPolicy",
    "KeyStorage",
    "InMemoryKeyStorage",
    "FileKeyStorage",
    # Trust Bootstrap
    "TrustBootstrap",
    "TrustAnchor",
    "TrustChain",
    "TrustVerification",
    "TrustLevel",
    "BootstrapMethod",
    "Certificate",
    "CertificateChain",
    # Reputation
    "ReputationSystem",
    "ReputationScore",
    "ReputationEvent",
    "ReputationEventType",
    "ReputationFactor",
    "ReputationCalculator",
    "ReputationStorage",
]