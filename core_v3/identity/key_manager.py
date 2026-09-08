"""
Key Manager

Cryptographic key management for Vireo.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import os
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union, Tuple, Callable
from datetime import datetime, timedelta
from pathlib import Path
import base64

from ..types import VireoPublicKey, VireoPrivateKey, VireoSignature
from ..crypto import Ed25519, BLAKE2b
from ..errors import VireoKeyError, VireoCryptoError


class KeyUsage(Enum):
    """Key usage types."""
    SIGNING = "signing"           # For signing messages
    ENCRYPTION = "encryption"     # For encryption
    AUTHENTICATION = "auth"       # For authentication
    KEY_AGREEMENT = "agreement"   # For key agreement
    VERIFICATION = "verification" # For verification only
    
    @classmethod
    def from_string(cls, value: str) -> KeyUsage:
        try:
            return cls(value)
        except ValueError:
            raise VireoKeyError(f"Invalid key usage: {value}")


class KeyState(Enum):
    """Key states."""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


@dataclass
class KeyMetadata:
    """Metadata for a key."""
    id: str
    algorithm: str
    usage: KeyUsage
    state: KeyState = KeyState.ACTIVE
    created: datetime = field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    expires: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None
    issuer: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    
    def is_active(self) -> bool:
        """Check if key is active."""
        if self.state != KeyState.ACTIVE:
            return False
        if self.expires and datetime.now(datetime.timezone.utc) > self.expires:
            return False
        return True
    
    def revoke(self, reason: Optional[str] = None) -> None:
        """Revoke the key."""
        self.state = KeyState.REVOKED
        self.revoked_at = datetime.now(datetime.timezone.utc)
        self.revoked_reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "algorithm": self.algorithm,
            "usage": self.usage.value,
            "state": self.state.value,
            "created": self.created.isoformat() if self.created else None,
            "expires": self.expires.isoformat() if self.expires else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoked_reason": self.revoked_reason,
            "issuer": self.issuer,
            "labels": self.labels,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KeyMetadata:
        return cls(
            id=data["id"],
            algorithm=data["algorithm"],
            usage=KeyUsage.from_string(data["usage"]),
            state=KeyState(data.get("state", "active")),
            created=datetime.fromisoformat(data["created"]) if data.get("created") else None,
            expires=datetime.fromisoformat(data["expires"]) if data.get("expires") else None,
            revoked_at=datetime.fromisoformat(data["revoked_at"]) if data.get("revoked_at") else None,
            revoked_reason=data.get("revoked_reason"),
            issuer=data.get("issuer"),
            labels=data.get("labels", []),
        )


@dataclass
class KeyPair:
    """Key pair with metadata."""
    public_key: bytes
    private_key: bytes
    metadata: KeyMetadata
    
    def sign(self, data: bytes) -> bytes:
        """Sign data with this key pair."""
        if not self.metadata.is_active():
            raise VireoKeyError("Key is not active")
        if self.metadata.usage not in [KeyUsage.SIGNING, KeyUsage.AUTHENTICATION]:
            raise VireoKeyError(f"Key usage {self.metadata.usage} does not support signing")
        
        if self.metadata.algorithm == "Ed25519":
            return Ed25519.sign(self.private_key, data)
        else:
            raise VireoKeyError(f"Unsupported algorithm: {self.metadata.algorithm}")
    
    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify signature."""
        if self.metadata.algorithm == "Ed25519":
            return Ed25519.verify(self.public_key, data, signature)
        else:
            raise VireoKeyError(f"Unsupported algorithm: {self.metadata.algorithm}")
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data (if supported)."""
        raise VireoKeyError(f"Encryption not supported for {self.metadata.algorithm}")
    
    def decrypt(self, data: bytes) -> bytes:
        """Decrypt data (if supported)."""
        raise VireoKeyError(f"Decryption not supported for {self.metadata.algorithm}")


@dataclass
class KeyRotationPolicy:
    """Policy for key rotation."""
    max_age_days: int = 90
    min_age_days: int = 1
    warning_days: int = 7
    auto_rotate: bool = True
    notify_on_rotation: bool = True
    rotation_algorithm: Optional[str] = None
    
    def should_rotate(self, metadata: KeyMetadata) -> bool:
        """Check if key should be rotated."""
        if not self.auto_rotate:
            return False
        if not metadata.expires:
            return False
        now = datetime.now(datetime.timezone.utc)
        days_until_expiry = (metadata.expires - now).days
        return days_until_expiry <= self.warning_days


class KeyStorage:
    """Interface for key storage."""
    
    def save(self, key_pair: KeyPair) -> None:
        """Save a key pair."""
        raise NotImplementedError
    
    def load(self, key_id: str) -> Optional[KeyPair]:
        """Load a key pair by ID."""
        raise NotImplementedError
    
    def delete(self, key_id: str) -> bool:
        """Delete a key pair."""
        raise NotImplementedError
    
    def list_keys(self) -> List[str]:
        """List all key IDs."""
        raise NotImplementedError
    
    def get_metadata(self, key_id: str) -> Optional[KeyMetadata]:
        """Get key metadata."""
        raise NotImplementedError
    
    def update_metadata(self, key_id: str, metadata: KeyMetadata) -> None:
        """Update key metadata."""
        raise NotImplementedError


class InMemoryKeyStorage(KeyStorage):
    """In-memory key storage."""
    
    def __init__(self):
        self._keys: Dict[str, KeyPair] = {}
    
    def save(self, key_pair: KeyPair) -> None:
        self._keys[key_pair.metadata.id] = key_pair
    
    def load(self, key_id: str) -> Optional[KeyPair]:
        return self._keys.get(key_id)
    
    def delete(self, key_id: str) -> bool:
        if key_id in self._keys:
            del self._keys[key_id]
            return True
        return False
    
    def list_keys(self) -> List[str]:
        return list(self._keys.keys())
    
    def get_metadata(self, key_id: str) -> Optional[KeyMetadata]:
        key = self._keys.get(key_id)
        return key.metadata if key else None
    
    def update_metadata(self, key_id: str, metadata: KeyMetadata) -> None:
        key = self._keys.get(key_id)
        if key:
            key.metadata = metadata


class FileKeyStorage(KeyStorage):
    """File-based key storage with encryption."""
    
    def __init__(self, directory: Union[str, Path], password: Optional[str] = None):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.password = password
    
    def _get_key_path(self, key_id: str) -> Path:
        return self.directory / f"{key_id}.key.json"
    
    def _get_metadata_path(self, key_id: str) -> Path:
        return self.directory / f"{key_id}.meta.json"
    
    def _encrypt(self, data: bytes) -> bytes:
        """Simple encryption (in production use proper encryption)."""
        if not self.password:
            return data
        # Simple XOR encryption (for demo only - use proper AES in production)
        key_bytes = self.password.encode('utf-8')
        return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
    
    def _decrypt(self, data: bytes) -> bytes:
        if not self.password:
            return data
        key_bytes = self.password.encode('utf-8')
        return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
    
    def save(self, key_pair: KeyPair) -> None:
        # Save keys
        key_data = {
            "id": key_pair.metadata.id,
            "public_key": base64.b64encode(key_pair.public_key).decode('ascii'),
            "private_key": base64.b64encode(key_pair.private_key).decode('ascii'),
            "metadata": key_pair.metadata.to_dict(),
        }
        key_json = json.dumps(key_data)
        encrypted = self._encrypt(key_json.encode('utf-8'))
        
        path = self._get_key_path(key_pair.metadata.id)
        with open(path, 'wb') as f:
            f.write(encrypted)
        
        # Save metadata separately
        meta_path = self._get_metadata_path(key_pair.metadata.id)
        with open(meta_path, 'w') as f:
            json.dump(key_pair.metadata.to_dict(), f, indent=2)
    
    def load(self, key_id: str) -> Optional[KeyPair]:
        path = self._get_key_path(key_id)
        if not path.exists():
            return None
        
        with open(path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self._decrypt(encrypted)
        data = json.loads(decrypted.decode('utf-8'))
        
        metadata = KeyMetadata.from_dict(data["metadata"])
        public_key = base64.b64decode(data["public_key"])
        private_key = base64.b64decode(data["private_key"])
        
        return KeyPair(public_key, private_key, metadata)
    
    def delete(self, key_id: str) -> bool:
        key_path = self._get_key_path(key_id)
        meta_path = self._get_metadata_path(key_id)
        
        deleted = False
        if key_path.exists():
            key_path.unlink()
            deleted = True
        if meta_path.exists():
            meta_path.unlink()
        
        return deleted
    
    def list_keys(self) -> List[str]:
        return [p.stem.replace('.meta', '') for p in self.directory.glob("*.meta.json")]
    
    def get_metadata(self, key_id: str) -> Optional[KeyMetadata]:
        path = self._get_metadata_path(key_id)
        if not path.exists():
            return None
        with open(path, 'r') as f:
            data = json.load(f)
        return KeyMetadata.from_dict(data)
    
    def update_metadata(self, key_id: str, metadata: KeyMetadata) -> None:
        # Update metadata file
        meta_path = self._get_metadata_path(key_id)
        with open(meta_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        # Update key file metadata
        key_path = self._get_key_path(key_id)
        if key_path.exists():
            with open(key_path, 'rb') as f:
                encrypted = f.read()
            decrypted = self._decrypt(encrypted)
            data = json.loads(decrypted.decode('utf-8'))
            data["metadata"] = metadata.to_dict()
            key_json = json.dumps(data)
            encrypted = self._encrypt(key_json.encode('utf-8'))
            with open(key_path, 'wb') as f:
                f.write(encrypted)


class KeyManager:
    """Key management system."""
    
    def __init__(self, storage: Optional[KeyStorage] = None):
        self.storage = storage or InMemoryKeyStorage()
        self._rotation_policy: Optional[KeyRotationPolicy] = None
        self._default_algorithm = "Ed25519"
    
    def generate_key(
        self,
        usage: KeyUsage = KeyUsage.SIGNING,
        algorithm: Optional[str] = None,
        id: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        issuer: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> KeyPair:
        """Generate a new key pair."""
        algorithm = algorithm or self._default_algorithm
        
        if algorithm == "Ed25519":
            public_key, private_key = Ed25519.generate_keypair()
        else:
            raise VireoKeyError(f"Unsupported algorithm: {algorithm}")
        
        # Generate ID
        if id is None:
            id = self._generate_key_id(public_key, algorithm)
        
        # Create metadata
        now = datetime.now(datetime.timezone.utc)
        expires = None
        if expires_in_days:
            expires = now + timedelta(days=expires_in_days)
        
        metadata = KeyMetadata(
            id=id,
            algorithm=algorithm,
            usage=usage,
            created=now,
            expires=expires,
            issuer=issuer,
            labels=labels or [],
        )
        
        key_pair = KeyPair(public_key, private_key, metadata)
        self.storage.save(key_pair)
        return key_pair
    
    def _generate_key_id(self, public_key: bytes, algorithm: str) -> str:
        """Generate a key ID from public key."""
        # Use BLAKE2b hash of public key
        hash_bytes = BLAKE2b.hash(public_key)
        # First 16 bytes as hex
        return f"{algorithm.lower()}-{hash_bytes[:16].hex()}"
    
    def load_key(self, key_id: str) -> Optional[KeyPair]:
        """Load a key by ID."""
        return self.storage.load(key_id)
    
    def get_active_key(self, usage: Optional[KeyUsage] = None) -> Optional[KeyPair]:
        """Get the active key matching usage."""
        for key_id in self.storage.list_keys():
            metadata = self.storage.get_metadata(key_id)
            if not metadata:
                continue
            if metadata.is_active():
                if usage is None or metadata.usage == usage:
                    key = self.storage.load(key_id)
                    if key:
                        return key
        return None
    
    def get_keys_by_usage(self, usage: KeyUsage) -> List[KeyPair]:
        """Get all keys for a specific usage."""
        keys = []
        for key_id in self.storage.list_keys():
            metadata = self.storage.get_metadata(key_id)
            if metadata and metadata.usage == usage:
                key = self.storage.load(key_id)
                if key:
                    keys.append(key)
        return keys
    
    def revoke_key(self, key_id: str, reason: Optional[str] = None) -> bool:
        """Revoke a key."""
        metadata = self.storage.get_metadata(key_id)
        if not metadata:
            return False
        metadata.revoke(reason)
        self.storage.update_metadata(key_id, metadata)
        return True
    
    def rotate_key(
        self,
        key_id: str,
        algorithm: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Optional[KeyPair]:
        """Rotate a key (create new key with same usage)."""
        old_key = self.storage.load(key_id)
        if not old_key:
            return None
        
        # Revoke old key
        old_key.metadata.revoke("Rotated")
        self.storage.update_metadata(key_id, old_key.metadata)
        
        # Generate new key with same usage
        return self.generate_key(
            usage=old_key.metadata.usage,
            algorithm=algorithm or old_key.metadata.algorithm,
            expires_in_days=expires_in_days,
            issuer=old_key.metadata.issuer,
            labels=old_key.metadata.labels,
        )
    
    def sign_data(self, key_id: str, data: bytes) -> bytes:
        """Sign data with a key."""
        key = self.storage.load(key_id)
        if not key:
            raise VireoKeyError(f"Key not found: {key_id}")
        return key.sign(data)
    
    def verify_signature(self, key_id: str, data: bytes, signature: bytes) -> bool:
        """Verify a signature."""
        key = self.storage.load(key_id)
        if not key:
            raise VireoKeyError(f"Key not found: {key_id}")
        return key.verify(data, signature)
    
    def set_rotation_policy(self, policy: KeyRotationPolicy) -> None:
        """Set key rotation policy."""
        self._rotation_policy = policy
    
    def check_rotation(self) -> List[str]:
        """Check which keys need rotation."""
        keys_to_rotate = []
        if not self._rotation_policy:
            return keys_to_rotate
        
        for key_id in self.storage.list_keys():
            metadata = self.storage.get_metadata(key_id)
            if metadata and self._rotation_policy.should_rotate(metadata):
                keys_to_rotate.append(key_id)
        
        return keys_to_rotate
    
    def rotate_expired_keys(self) -> Dict[str, Optional[KeyPair]]:
        """Automatically rotate expired keys."""
        result = {}
        for key_id in self.check_rotation():
            result[key_id] = self.rotate_key(key_id)
        return result
    
    def export_public_key(self, key_id: str) -> VireoPublicKey:
        """Export public key as Vireo type."""
        key = self.storage.load(key_id)
        if not key:
            raise VireoKeyError(f"Key not found: {key_id}")
        return VireoPublicKey(key.public_key, key.metadata.algorithm)
    
    def sign_vireo_message(self, key_id: str, message: bytes) -> VireoSignature:
        """Sign a message and return Vireo signature type."""
        signature = self.sign_data(key_id, message)
        return VireoSignature(signature)