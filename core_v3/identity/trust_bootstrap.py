"""
Trust Bootstrap

Trust establishment and bootstrapping for Vireo agents.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set, Union, Tuple
from datetime import datetime, timedelta

from .did import DID, DIDDocument, DIDResolver, DIDRegistry
from .key_manager import KeyManager, KeyPair, KeyUsage, KeyState
from ..crypto import Ed25519, BLAKE2b
from ..types import VireoSignature
from ..errors import VireoTrustError, VireoIdentityError, VireoSignatureError


class TrustLevel(Enum):
    """Trust levels."""
    NONE = 0
    UNTRUSTED = 1
    BASIC = 2
    VERIFIED = 3
    HIGH = 4
    MAXIMUM = 5
    
    def __ge__(self, other: TrustLevel) -> bool:
        return self.value >= other.value
    
    def __gt__(self, other: TrustLevel) -> bool:
        return self.value > other.value
    
    def __le__(self, other: TrustLevel) -> bool:
        return self.value <= other.value
    
    def __lt__(self, other: TrustLevel) -> bool:
        return self.value < other.value


class BootstrapMethod(Enum):
    """Methods for trust bootstrapping."""
    STATIC = "static"           # Pre-configured trust anchors
    DID_DOCUMENT = "did"        # Via DID document verification
    CERTIFICATE = "cert"        # Via X.509-like certificates
    CHAIN_OF_TRUST = "chain"    # Via chain of trust
    WEB_OF_TRUST = "web"        # Via web of trust
    MULTI_FACTOR = "multi"      # Multi-factor verification
    ZERO_TRUST = "zero"         # Zero-trust approach


@dataclass
class Certificate:
    """Certificate for trust verification."""
    id: str
    subject: str
    issuer: str
    public_key: bytes
    validity_start: datetime
    validity_end: datetime
    signature: bytes
    algorithm: str = "Ed25519"
    subject_did: Optional[str] = None
    issuer_did: Optional[str] = None
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        subject: str,
        public_key: bytes,
        issuer_private_key: bytes,
        validity_days: int = 365,
        issuer: Optional[str] = None,
        subject_did: Optional[str] = None,
        issuer_did: Optional[str] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ) -> Certificate:
        """Create a new certificate."""
        now = datetime.now(datetime.timezone.utc)
        
        # Build certificate data
        cert_data = {
            "subject": subject,
            "public_key": public_key.hex(),
            "validity_start": now.isoformat(),
            "validity_end": (now + timedelta(days=validity_days)).isoformat(),
        }
        if subject_did:
            cert_data["subject_did"] = subject_did
        if issuer_did:
            cert_data["issuer_did"] = issuer_did
        if extensions:
            cert_data["extensions"] = extensions
        
        cert_json = json.dumps(cert_data, sort_keys=True).encode('utf-8')
        signature = Ed25519.sign(issuer_private_key, cert_json)
        
        return cls(
            id=f"cert-{BLAKE2b.hash(cert_json)[:16].hex()}",
            subject=subject,
            issuer=issuer or subject,
            public_key=public_key,
            validity_start=now,
            validity_end=now + timedelta(days=validity_days),
            signature=signature,
            subject_did=subject_did,
            issuer_did=issuer_did,
            extensions=extensions or {},
        )
    
    def verify(self, issuer_public_key: bytes) -> bool:
        """Verify certificate signature."""
        cert_data = {
            "subject": self.subject,
            "public_key": self.public_key.hex(),
            "validity_start": self.validity_start.isoformat(),
            "validity_end": self.validity_end.isoformat(),
        }
        if self.subject_did:
            cert_data["subject_did"] = self.subject_did
        if self.issuer_did:
            cert_data["issuer_did"] = self.issuer_did
        if self.extensions:
            cert_data["extensions"] = self.extensions
        
        cert_json = json.dumps(cert_data, sort_keys=True).encode('utf-8')
        return Ed25519.verify(issuer_public_key, cert_json, self.signature)
    
    def is_expired(self) -> bool:
        """Check if certificate is expired."""
        return datetime.now(datetime.timezone.utc) > self.validity_end
    
    def is_valid(self) -> bool:
        """Check if certificate is valid and not expired."""
        now = datetime.now(datetime.timezone.utc)
        return self.validity_start <= now <= self.validity_end
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "subject": self.subject,
            "issuer": self.issuer,
            "public_key": self.public_key.hex(),
            "validity_start": self.validity_start.isoformat(),
            "validity_end": self.validity_end.isoformat(),
            "signature": self.signature.hex(),
            "algorithm": self.algorithm,
            "subject_did": self.subject_did,
            "issuer_did": self.issuer_did,
            "extensions": self.extensions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Certificate:
        return cls(
            id=data["id"],
            subject=data["subject"],
            issuer=data["issuer"],
            public_key=bytes.fromhex(data["public_key"]),
            validity_start=datetime.fromisoformat(data["validity_start"]),
            validity_end=datetime.fromisoformat(data["validity_end"]),
            signature=bytes.fromhex(data["signature"]),
            algorithm=data.get("algorithm", "Ed25519"),
            subject_did=data.get("subject_did"),
            issuer_did=data.get("issuer_did"),
            extensions=data.get("extensions", {}),
        )


@dataclass
class CertificateChain:
    """Chain of certificates."""
    certificates: List[Certificate]
    
    def verify(self, root_public_key: bytes) -> bool:
        """Verify the entire certificate chain."""
        if not self.certificates:
            return False
        
        # Verify each certificate in chain
        current_pubkey = root_public_key
        for cert in self.certificates:
            if not cert.verify(current_pubkey):
                return False
            if cert.is_expired():
                return False
            current_pubkey = cert.public_key
        
        return True
    
    def get_leaf(self) -> Optional[Certificate]:
        """Get the leaf certificate."""
        return self.certificates[-1] if self.certificates else None
    
    def get_root(self) -> Optional[Certificate]:
        """Get the root certificate."""
        return self.certificates[0] if self.certificates else None


@dataclass
class TrustAnchor:
    """Trust anchor for bootstrapping."""
    id: str
    name: str
    public_key: bytes
    did: Optional[str] = None
    certificate: Optional[Certificate] = None
    trust_level: TrustLevel = TrustLevel.HIGH
    issued_at: datetime = field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    expires_at: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if trust anchor is valid."""
        if self.expires_at and datetime.now(datetime.timezone.utc) > self.expires_at:
            return False
        if self.certificate and not self.certificate.is_valid():
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "public_key": self.public_key.hex(),
            "did": self.did,
            "certificate": self.certificate.to_dict() if self.certificate else None,
            "trust_level": self.trust_level.value,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class TrustVerification:
    """Trust verification utilities."""
    
    @staticmethod
    def verify_did_document(did_doc: DIDDocument, trusted_dids: List[str]) -> bool:
        """Verify a DID document against trusted DIDs."""
        return did_doc.id in trusted_dids
    
    @staticmethod
    def verify_signature(
        data: bytes,
        signature: bytes,
        public_key: bytes,
        algorithm: str = "Ed25519",
    ) -> bool:
        """Verify a signature using the given public key."""
        if algorithm == "Ed25519":
            return Ed25519.verify(public_key, data, signature)
        else:
            raise VireoSignatureError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def verify_certificate_chain(
        chain: CertificateChain,
        trust_anchors: List[TrustAnchor],
    ) -> Tuple[bool, Optional[str]]:
        """Verify a certificate chain against trust anchors."""
        for anchor in trust_anchors:
            if not anchor.is_valid():
                continue
            
            # Try to verify with this trust anchor
            try:
                if chain.verify(anchor.public_key):
                    # Verify leaf certificate
                    leaf = chain.get_leaf()
                    if leaf and leaf.is_valid():
                        return True, f"Verified by trust anchor: {anchor.name}"
            except Exception:
                continue
        
        return False, "No valid trust anchor found"


class TrustBootstrap:
    """
    Trust bootstrapping system.
    
    Establishes initial trust between Vireo agents.
    """
    
    def __init__(self, key_manager: Optional[KeyManager] = None):
        self.key_manager = key_manager or KeyManager()
        self._trust_anchors: Dict[str, TrustAnchor] = {}
        self._resolver = DIDResolver()
        self._registry = DIDRegistry()
        self._trust_levels: Dict[str, TrustLevel] = {}
        self._certificates: Dict[str, Certificate] = {}
    
    def add_trust_anchor(self, anchor: TrustAnchor) -> None:
        """Add a trust anchor."""
        if not anchor.is_valid():
            raise VireoTrustError(f"Trust anchor {anchor.id} is invalid")
        self._trust_anchors[anchor.id] = anchor
        self._trust_levels[anchor.id] = anchor.trust_level
    
    def remove_trust_anchor(self, anchor_id: str) -> bool:
        """Remove a trust anchor."""
        if anchor_id in self._trust_anchors:
            del self._trust_anchors[anchor_id]
            if anchor_id in self._trust_levels:
                del self._trust_levels[anchor_id]
            return True
        return False
    
    def get_trust_anchor(self, anchor_id: str) -> Optional[TrustAnchor]:
        """Get a trust anchor by ID."""
        return self._trust_anchors.get(anchor_id)
    
    def list_trust_anchors(self) -> List[TrustAnchor]:
        """List all trust anchors."""
        return list(self._trust_anchors.values())
    
    def bootstrap_with_anchor(
        self,
        anchor_id: str,
        message: bytes,
        signature: bytes,
    ) -> Tuple[bool, Optional[TrustLevel]]:
        """
        Bootstrap trust using a trust anchor.
        
        Verifies that the message is signed by the trust anchor.
        """
        anchor = self._trust_anchors.get(anchor_id)
        if not anchor:
            return False, None
        
        if not anchor.is_valid():
            return False, None
        
        # Verify signature
        if TrustVerification.verify_signature(message, signature, anchor.public_key):
            return True, anchor.trust_level
        
        return False, None
    
    def bootstrap_with_did(
        self,
        did: str,
        message: bytes,
        signature: bytes,
        trusted_dids: List[str],
    ) -> Tuple[bool, Optional[TrustLevel]]:
        """
        Bootstrap trust using a DID.
        
        Verifies that the message is signed by the DID's key.
        """
        # Resolve DID
        did_doc = self._resolver.resolve(did)
        if not did_doc:
            return False, None
        
        # Check if DID is trusted
        if did not in trusted_dids:
            return False, None
        
        # Get verification method
        # Try to find a verification method with public key
        public_key = None
        for vm in did_doc.verification_method:
            if vm.public_key_multibase:
                # Decode multibase
                # For now, assume hex
                try:
                    public_key = bytes.fromhex(vm.public_key_multibase[1:])
                except:
                    continue
            elif vm.public_key_hex:
                try:
                    public_key = bytes.fromhex(vm.public_key_hex)
                except:
                    continue
        
        if not public_key:
            return False, None
        
        # Verify signature
        if TrustVerification.verify_signature(message, signature, public_key):
            return True, TrustLevel.HIGH
        
        return False, None
    
    def bootstrap_with_certificate(
        self,
        certificate: Certificate,
        message: bytes,
        signature: bytes,
    ) -> Tuple[bool, Optional[TrustLevel]]:
        """
        Bootstrap trust using a certificate.
        
        Verifies the certificate and the message signature.
        """
        # Verify certificate
        if not certificate.is_valid():
            return False, None
        
        # Check certificate against trust anchors
        for anchor in self._trust_anchors.values():
            if not anchor.is_valid():
                continue
            
            if certificate.verify(anchor.public_key):
                # Certificate verified by trust anchor
                # Now verify message signature
                if TrustVerification.verify_signature(
                    message, signature, certificate.public_key
                ):
                    return True, TrustLevel.HIGH
        
        return False, None
    
    def bootstrap_with_certificate_chain(
        self,
        chain: CertificateChain,
        message: bytes,
        signature: bytes,
    ) -> Tuple[bool, Optional[TrustLevel]]:
        """
        Bootstrap trust using a certificate chain.
        """
        # Verify certificate chain
        for anchor in self._trust_anchors.values():
            if not anchor.is_valid():
                continue
            
            if chain.verify(anchor.public_key):
                # Chain verified
                leaf = chain.get_leaf()
                if leaf and leaf.is_valid():
                    # Verify message signature
                    if TrustVerification.verify_signature(
                        message, signature, leaf.public_key
                    ):
                        return True, TrustLevel.HIGH
        
        return False, None
    
    def bootstrap_multi_factor(
        self,
        evidence: Dict[str, Any],
    ) -> Tuple[bool, Optional[TrustLevel]]:
        """
        Multi-factor trust bootstrapping.
        
        Combines multiple verification methods.
        """
        factors_verified = 0
        required_factors = evidence.get("required", 2)
        
        # Factor 1: DID document verification
        if "did" in evidence:
            did = evidence["did"]
            if "signature" in evidence and "trusted_dids" in evidence:
                result, level = self.bootstrap_with_did(
                    did,
                    evidence.get("message", b""),
                    evidence["signature"],
                    evidence["trusted_dids"],
                )
                if result:
                    factors_verified += 1
        
        # Factor 2: Certificate verification
        if "certificate" in evidence:
            cert = evidence["certificate"]
            if "signature" in evidence:
                result, level = self.bootstrap_with_certificate(
                    cert,
                    evidence.get("message", b""),
                    evidence["signature"],
                )
                if result:
                    factors_verified += 1
        
        # Factor 3: Trust anchor verification
        if "anchor_id" in evidence:
            anchor_id = evidence["anchor_id"]
            if "signature" in evidence:
                result, level = self.bootstrap_with_anchor(
                    anchor_id,
                    evidence.get("message", b""),
                    evidence["signature"],
                )
                if result:
                    factors_verified += 1
        
        # Factor 4: Reputation check
        if "reputation" in evidence:
            reputation = evidence["reputation"]
            if reputation >= 0.8:
                factors_verified += 1
        
        # Determine final trust level
        if factors_verified >= required_factors:
            if factors_verified >= 3:
                return True, TrustLevel.MAXIMUM
            elif factors_verified >= 2:
                return True, TrustLevel.HIGH
            else:
                return True, TrustLevel.VERIFIED
        
        return False, TrustLevel.NONE
    
    def set_trust_level(self, entity_id: str, level: TrustLevel) -> None:
        """Set trust level for an entity."""
        self._trust_levels[entity_id] = level
    
    def get_trust_level(self, entity_id: str) -> TrustLevel:
        """Get trust level for an entity."""
        return self._trust_levels.get(entity_id, TrustLevel.NONE)
    
    def is_trusted(self, entity_id: str, minimum_level: TrustLevel = TrustLevel.BASIC) -> bool:
        """Check if entity is trusted at the given level."""
        level = self.get_trust_level(entity_id)
        return level >= minimum_level
    
    @property
    def resolver(self) -> DIDResolver:
        return self._resolver
    
    @property
    def registry(self) -> DIDRegistry:
        return self._registry
    
    @property
    def key_manager(self) -> KeyManager:
        return self._key_manager