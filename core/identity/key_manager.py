"""Key Management for Vireo v2.0.1"""

from typing import Optional, Tuple
import base64
import os
import json

from cryptography.hazmat.primitives import ed25519
from cryptography.hazmat.primitives.asymmetric import ed25519 as ed25519_asym


class KeyManager:
    """Ed25519 key management"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._private_key: Optional[ed25519_asym.Ed25519PrivateKey] = None
        self._public_key: Optional[bytes] = None
        self._load_or_generate_keys()
    
    def _load_or_generate_keys(self) -> None:
        """Load existing keys or generate new ones"""
        # Try to load from file
        key_path = f"./keys/{self.agent_id}.key"
        
        if os.path.exists(key_path):
            try:
                with open(key_path, 'r') as f:
                    data = json.load(f)
                    private_bytes = base64.b64decode(data["private_key"])
                    self._private_key = ed25519_asym.Ed25519PrivateKey.from_private_bytes(private_bytes)
                    self._public_key = self._private_key.public_key().public_bytes_raw()
                return
            except Exception:
                pass
        
        # Generate new keys
        self._private_key = ed25519_asym.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key().public_bytes_raw()
        
        # Save keys
        os.makedirs("./keys", exist_ok=True)
        with open(key_path, 'w') as f:
            json.dump({
                "agent_id": self.agent_id,
                "private_key": base64.b64encode(
                    self._private_key.private_bytes_raw()
                ).decode()
            }, f, indent=2)
    
    def get_public_key(self) -> bytes:
        """Get public key"""
        return self._public_key
    
    def get_public_key_b64(self) -> str:
        """Get public key as base64"""
        return base64.b64encode(self._public_key).decode()
    
    def sign(self, message: bytes) -> bytes:
        """Sign a message"""
        if self._private_key is None:
            raise ValueError("Private key not available")
        return self._private_key.sign(message)
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify a signature"""
        try:
            pub_key = ed25519_asym.Ed25519PublicKey.from_public_bytes(public_key)
            pub_key.verify(signature, message)
            return True
        except Exception:
            return False
    
    def rotate_keys(self) -> Tuple[bytes, bytes]:
        """Rotate keys (generate new ones)"""
        # Generate new keys
        self._private_key = ed25519_asym.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key().public_bytes_raw()
        
        # Save new keys
        key_path = f"./keys/{self.agent_id}.key"
        with open(key_path, 'w') as f:
            json.dump({
                "agent_id": self.agent_id,
                "private_key": base64.b64encode(
                    self._private_key.private_bytes_raw()
                ).decode()
            }, f, indent=2)
        
        return self._public_key, self._private_key.private_bytes_raw()
    
    @classmethod
    def generate_keypair(cls) -> Tuple[bytes, bytes]:
        """Generate a new keypair"""
        private_key = ed25519_asym.Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes_raw()
        return public_key, private_key.private_bytes_raw()