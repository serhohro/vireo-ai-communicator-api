# core/identity.py
"""Vireo identity management."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import hashlib
import json
import time

@dataclass
class DID:
    """Decentralized Identifier."""
    id: str
    public_key: str
    created_at: float = time.time()
    metadata: Dict[str, Any] = None
    
    @classmethod
    def create(cls, name: str, public_key: str = None) -> "DID":
        """Create a new DID."""
        if public_key is None:
            public_key = f"did:vireo:{name}-{hashlib.sha256(name.encode()).hexdigest()[:16]}"
        return cls(
            id=f"did:vireo:{name}",
            public_key=public_key
        )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "public_key": self.public_key,
            "created_at": self.created_at,
            "metadata": self.metadata or {}
        }


class KeyManager:
    """Key management for Vireo."""
    
    def __init__(self):
        self._keys = {}
    
    def generate_keypair(self, name: str) -> tuple:
        """Generate a key pair."""
        # Simple mock implementation
        private_key = f"private_{name}_{int(time.time())}"
        public_key = f"public_{name}_{int(time.time())}"
        self._keys[name] = {"private": private_key, "public": public_key}
        return private_key, public_key
    
    def get_public_key(self, name: str) -> Optional[str]:
        """Get public key by name."""
        if name in self._keys:
            return self._keys[name]["public"]
        return None
    
    def get_private_key(self, name: str) -> Optional[str]:
        """Get private key by name."""
        if name in self._keys:
            return self._keys[name]["private"]
        return None
    
    def sign(self, name: str, message: str) -> str:
        """Sign a message."""
        private_key = self.get_private_key(name)
        if private_key is None:
            raise ValueError(f"Key not found for {name}")
        return hashlib.sha256(f"{private_key}:{message}".encode()).hexdigest()
    
    def verify(self, name: str, message: str, signature: str) -> bool:
        """Verify a signature."""
        expected = self.sign(name, message)
        return signature == expected


class TrustBootstrap:
    """Trust bootstrap for Vireo."""
    
    def __init__(self):
        self._trust_anchors = {}
    
    def add_trust_anchor(self, name: str, public_key: str):
        """Add a trust anchor."""
        self._trust_anchors[name] = public_key
    
    def verify(self, did: str, proof: str) -> bool:
        """Verify a proof."""
        return True  # Simplified for now