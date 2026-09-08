"""
Decentralized Identifier (DID) Implementation

DID specification: https://www.w3.org/TR/did-core/

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import json
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set, Union, Callable, ClassVar
from datetime import datetime
from copy import deepcopy

from ..types import VireoDID, VireoURI
from ..errors import VireoIdentityError, VireoKeyError


class DIDMethod(Enum):
    """Supported DID methods."""
    KEY = "key"
    WEB = "web"
    ETHR = "ethr"
    ION = "ion"
    PEER = "peer"
    VIVO = "vivo"
    CUSTOM = "custom"
    
    @classmethod
    def from_string(cls, value: str) -> DIDMethod:
        try:
            return cls(value.lower())
        except ValueError:
            return cls.CUSTOM


@dataclass
class VerificationMethod:
    """Verification method for a DID."""
    id: str
    type: str
    controller: str
    public_key_multibase: Optional[str] = None
    public_key_hex: Optional[str] = None
    public_key_jwk: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VerificationMethod:
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "Ed25519VerificationKey2020"),
            controller=data.get("controller", ""),
            public_key_multibase=data.get("publicKeyMultibase"),
            public_key_hex=data.get("publicKeyHex"),
            public_key_jwk=data.get("publicKeyJwk"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "type": self.type,
            "controller": self.controller,
        }
        if self.public_key_multibase:
            result["publicKeyMultibase"] = self.public_key_multibase
        if self.public_key_hex:
            result["publicKeyHex"] = self.public_key_hex
        if self.public_key_jwk:
            result["publicKeyJwk"] = self.public_key_jwk
        return result


@dataclass
class ServiceEndpoint:
    """Service endpoint for a DID."""
    id: str
    type: str
    service_endpoint: Union[str, Dict[str, Any], List[str]]
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ServiceEndpoint:
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            service_endpoint=data.get("serviceEndpoint", ""),
            description=data.get("description"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "type": self.type,
            "serviceEndpoint": self.service_endpoint,
        }
        if self.description:
            result["description"] = self.description
        return result


@dataclass
class Authentication:
    """Authentication methods."""
    methods: List[Union[str, VerificationMethod]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: List[Any]) -> Authentication:
        methods = []
        for item in data:
            if isinstance(item, str):
                methods.append(item)
            elif isinstance(item, dict):
                methods.append(VerificationMethod.from_dict(item))
        return cls(methods)
    
    def to_dict(self) -> List[Any]:
        result = []
        for method in self.methods:
            if isinstance(method, str):
                result.append(method)
            else:
                result.append(method.to_dict())
        return result


@dataclass
class DIDDocument:
    """DID Document according to DID Core specification."""
    id: str
    controller: Optional[Union[str, List[str]]] = None
    also_known_as: Optional[List[str]] = None
    verification_method: List[VerificationMethod] = field(default_factory=list)
    authentication: List[Union[str, VerificationMethod]] = field(default_factory=list)
    assertion_method: List[Union[str, VerificationMethod]] = field(default_factory=list)
    key_agreement: List[Union[str, VerificationMethod]] = field(default_factory=list)
    capability_invocation: List[Union[str, VerificationMethod]] = field(default_factory=list)
    capability_delegation: List[Union[str, VerificationMethod]] = field(default_factory=list)
    service: List[ServiceEndpoint] = field(default_factory=list)
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    expires: Optional[datetime] = None
    context: List[str] = field(default_factory=lambda: ["https://www.w3.org/ns/did/v1"])
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DIDDocument:
        doc = cls(
            id=data.get("id", ""),
            controller=data.get("controller"),
            also_known_as=data.get("alsoKnownAs"),
            created=datetime.fromisoformat(data["created"]) if data.get("created") else None,
            updated=datetime.fromisoformat(data["updated"]) if data.get("updated") else None,
            expires=datetime.fromisoformat(data["expires"]) if data.get("expires") else None,
            context=data.get("@context", ["https://www.w3.org/ns/did/v1"]),
        )
        
        # Parse verification methods
        if "verificationMethod" in data:
            doc.verification_method = [
                VerificationMethod.from_dict(vm) for vm in data["verificationMethod"]
            ]
        
        # Parse authentication
        if "authentication" in data:
            doc.authentication = []
            for item in data["authentication"]:
                if isinstance(item, str):
                    doc.authentication.append(item)
                elif isinstance(item, dict):
                    doc.authentication.append(VerificationMethod.from_dict(item))
        
        # Parse assertion method
        if "assertionMethod" in data:
            doc.assertion_method = []
            for item in data["assertionMethod"]:
                if isinstance(item, str):
                    doc.assertion_method.append(item)
                elif isinstance(item, dict):
                    doc.assertion_method.append(VerificationMethod.from_dict(item))
        
        # Parse key agreement
        if "keyAgreement" in data:
            doc.key_agreement = []
            for item in data["keyAgreement"]:
                if isinstance(item, str):
                    doc.key_agreement.append(item)
                elif isinstance(item, dict):
                    doc.key_agreement.append(VerificationMethod.from_dict(item))
        
        # Parse capability invocation
        if "capabilityInvocation" in data:
            doc.capability_invocation = []
            for item in data["capabilityInvocation"]:
                if isinstance(item, str):
                    doc.capability_invocation.append(item)
                elif isinstance(item, dict):
                    doc.capability_invocation.append(VerificationMethod.from_dict(item))
        
        # Parse capability delegation
        if "capabilityDelegation" in data:
            doc.capability_delegation = []
            for item in data["capabilityDelegation"]:
                if isinstance(item, str):
                    doc.capability_delegation.append(item)
                elif isinstance(item, dict):
                    doc.capability_delegation.append(VerificationMethod.from_dict(item))
        
        # Parse service endpoints
        if "service" in data:
            doc.service = [ServiceEndpoint.from_dict(s) for s in data["service"]]
        
        return doc
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "@context": self.context,
            "id": self.id,
        }
        
        if self.controller:
            result["controller"] = self.controller
        if self.also_known_as:
            result["alsoKnownAs"] = self.also_known_as
        if self.created:
            result["created"] = self.created.isoformat()
        if self.updated:
            result["updated"] = self.updated.isoformat()
        if self.expires:
            result["expires"] = self.expires.isoformat()
        
        if self.verification_method:
            result["verificationMethod"] = [vm.to_dict() for vm in self.verification_method]
        
        if self.authentication:
            result["authentication"] = []
            for item in self.authentication:
                if isinstance(item, str):
                    result["authentication"].append(item)
                else:
                    result["authentication"].append(item.to_dict())
        
        if self.assertion_method:
            result["assertionMethod"] = []
            for item in self.assertion_method:
                if isinstance(item, str):
                    result["assertionMethod"].append(item)
                else:
                    result["assertionMethod"].append(item.to_dict())
        
        if self.key_agreement:
            result["keyAgreement"] = []
            for item in self.key_agreement:
                if isinstance(item, str):
                    result["keyAgreement"].append(item)
                else:
                    result["keyAgreement"].append(item.to_dict())
        
        if self.capability_invocation:
            result["capabilityInvocation"] = []
            for item in self.capability_invocation:
                if isinstance(item, str):
                    result["capabilityInvocation"].append(item)
                else:
                    result["capabilityInvocation"].append(item.to_dict())
        
        if self.capability_delegation:
            result["capabilityDelegation"] = []
            for item in self.capability_delegation:
                if isinstance(item, str):
                    result["capabilityDelegation"].append(item)
                else:
                    result["capabilityDelegation"].append(item.to_dict())
        
        if self.service:
            result["service"] = [s.to_dict() for s in self.service]
        
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> DIDDocument:
        return cls.from_dict(json.loads(json_str))
    
    def get_verification_method(self, id: str) -> Optional[VerificationMethod]:
        """Get a verification method by ID."""
        for vm in self.verification_method:
            if vm.id == id or vm.id == f"{self.id}#{id}":
                return vm
        return None
    
    def get_service(self, id: str) -> Optional[ServiceEndpoint]:
        """Get a service endpoint by ID."""
        for service in self.service:
            if service.id == id or service.id == f"{self.id}#{id}":
                return service
        return None
    
    def is_expired(self) -> bool:
        """Check if the DID document is expired."""
        if self.expires:
            return datetime.now(datetime.timezone.utc) > self.expires
        return False
    
    def add_verification_method(self, method: VerificationMethod) -> None:
        """Add a verification method."""
        self.verification_method.append(method)
        self.updated = datetime.now(datetime.timezone.utc)
    
    def remove_verification_method(self, id: str) -> bool:
        """Remove a verification method by ID."""
        for i, vm in enumerate(self.verification_method):
            if vm.id == id or vm.id == f"{self.id}#{id}":
                del self.verification_method[i]
                self.updated = datetime.now(datetime.timezone.utc)
                return True
        return False


class DID:
    """Decentralized Identifier."""
    
    DID_PATTERN = re.compile(r'^did:([a-zA-Z0-9]+):([a-zA-Z0-9\-_.:]+)$')
    
    def __init__(self, value: str):
        if not self.is_valid(value):
            raise VireoIdentityError(f"Invalid DID: {value}")
        self._value = value
        self._method = DIDMethod.from_string(self._parse_method(value))
        self._identifier = self._parse_identifier(value)
    
    @property
    def value(self) -> str:
        return self._value
    
    @property
    def method(self) -> DIDMethod:
        return self._method
    
    @property
    def method_string(self) -> str:
        return self._method.value
    
    @property
    def identifier(self) -> str:
        return self._identifier
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a string is a valid DID."""
        if not value.startswith("did:"):
            return False
        return bool(cls.DID_PATTERN.match(value))
    
    @classmethod
    def _parse_method(cls, value: str) -> str:
        match = cls.DID_PATTERN.match(value)
        if match:
            return match.group(1)
        return "unknown"
    
    @classmethod
    def _parse_identifier(cls, value: str) -> str:
        match = cls.DID_PATTERN.match(value)
        if match:
            return match.group(2)
        return ""
    
    @classmethod
    def from_method(cls, method: str, identifier: str) -> DID:
        return cls(f"did:{method}:{identifier}")
    
    def to_vireo(self) -> VireoDID:
        return VireoDID(self._value)
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"DID('{self._value}')"
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DID):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False
    
    def __hash__(self) -> int:
        return hash(self._value)


class DIDResolver:
    """DID resolver interface."""
    
    def __init__(self):
        self._resolvers: Dict[str, Callable[[str], Optional[DIDDocument]]] = {}
        self._default_resolver: Optional[Callable[[str], Optional[DIDDocument]]] = None
    
    def register(self, method: str, resolver: Callable[[str], Optional[DIDDocument]]) -> None:
        """Register a resolver for a DID method."""
        self._resolvers[method.lower()] = resolver
    
    def set_default(self, resolver: Callable[[str], Optional[DIDDocument]]) -> None:
        """Set default resolver."""
        self._default_resolver = resolver
    
    def resolve(self, did: Union[str, DID]) -> Optional[DIDDocument]:
        """Resolve a DID to a DID Document."""
        if isinstance(did, DID):
            did_str = did.value
            method = did.method_string
        else:
            if not DID.is_valid(did):
                raise VireoIdentityError(f"Invalid DID: {did}")
            did_obj = DID(did)
            did_str = did_obj.value
            method = did_obj.method_string
        
        # Try method-specific resolver
        if method in self._resolvers:
            result = self._resolvers[method](did_str)
            if result:
                return result
        
        # Try default resolver
        if self._default_resolver:
            return self._default_resolver(did_str)
        
        return None


class DIDRegistry:
    """Registry for DID documents."""
    
    def __init__(self):
        self._documents: Dict[str, DIDDocument] = {}
        self._resolver = DIDResolver()
    
    def register(self, did: str, document: DIDDocument) -> None:
        """Register a DID document."""
        if document.id != did:
            raise VireoIdentityError(f"DID mismatch: {document.id} != {did}")
        self._documents[did] = document
    
    def resolve(self, did: str) -> Optional[DIDDocument]:
        """Resolve a DID."""
        return self._documents.get(did)
    
    def update(self, did: str, document: DIDDocument) -> None:
        """Update a DID document."""
        if did not in self._documents:
            raise VireoIdentityError(f"DID not found: {did}")
        if document.id != did:
            raise VireoIdentityError(f"DID mismatch: {document.id} != {did}")
        document.updated = datetime.now(datetime.timezone.utc)
        self._documents[did] = document
    
    def delete(self, did: str) -> bool:
        """Delete a DID document."""
        if did in self._documents:
            del self._documents[did]
            return True
        return False
    
    def list(self) -> List[str]:
        """List all registered DIDs."""
        return list(self._documents.keys())
    
    @property
    def resolver(self) -> DIDResolver:
        return self._resolver