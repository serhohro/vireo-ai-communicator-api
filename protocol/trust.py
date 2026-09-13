"""
VIREO TRUST — Ed25519 + Whitelist
"""

import base64
import json
import time
import secrets
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.exceptions import InvalidSignature


class TrustBootstrap:
    def __init__(self):
        self._whitelist: Dict[str, bytes] = {}
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self._nonce_store: Dict[str, float] = {}
    
    def register(self, agent_id: str, public_key_hex: str) -> None:
        if len(public_key_hex) != 64:
            raise ValueError(f"Invalid Ed25519 public key: expected 64 hex chars, got {len(public_key_hex)}")
        try:
            public_key_bytes = bytes.fromhex(public_key_hex)
            Ed25519PublicKey.from_public_bytes(public_key_bytes)
            self._whitelist[agent_id] = public_key_bytes
        except Exception as e:
            raise ValueError(f"Invalid Ed25519 public key: {e}")
    
    def unregister(self, agent_id: str) -> None:
        self._whitelist.pop(agent_id, None)
    
    def is_trusted(self, agent_id: str) -> bool:
        return agent_id in self._whitelist
    
    def verify_message(self, agent_id: str, message: bytes, signature: bytes) -> bool:
        if agent_id not in self._whitelist:
            return False
        try:
            public_key = Ed25519PublicKey.from_public_bytes(self._whitelist[agent_id])
            public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False
    
    def verify_json_message(self, agent_id: str, data: Dict, signature_b64: str) -> bool:
        data_copy = {k: v for k, v in data.items() if k != "signature"}
        message = json.dumps(data_copy, sort_keys=True).encode('utf-8')
        signature = base64.b64decode(signature_b64)
        return self.verify_message(agent_id, message, signature)
    
    def sign_message(self, data: Dict) -> tuple[bytes, str]:
        data_copy = {k: v for k, v in data.items() if k != "signature"}
        message = json.dumps(data_copy, sort_keys=True).encode('utf-8')
        signature = self._private_key.sign(message)
        return message, base64.b64encode(signature).decode('utf-8')
    
    def generate_nonce(self) -> str:
        nonce = secrets.token_hex(32)
        self._nonce_store[nonce] = time.time()
        return nonce
    
    def validate_nonce(self, nonce: str, ttl_sec: int = 60) -> bool:
        if nonce not in self._nonce_store:
            return False
        if time.time() - self._nonce_store[nonce] > ttl_sec:
            return False
        return True
    
    def get_own_public_key_hex(self) -> str:
        return self._public_key.public_bytes_raw().hex()
    
    def get_whitelist(self) -> Dict[str, str]:
        return {aid: pubkey.hex() for aid, pubkey in self._whitelist.items()}


# ============================================================
# СТАРИЙ TrustManager (для зворотної сумісності)
# ============================================================

class TrustManager:
    def __init__(self, secret: str):
        self.secret = secret.encode('utf-8')
    
    def verify_hmac(self, data: Dict, signature: str) -> bool:
        import hmac
        import hashlib
        message = json.dumps(data, sort_keys=True).encode('utf-8')
        expected = hmac.new(self.secret, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def sign_hmac(self, data: Dict) -> str:
        import hmac
        import hashlib
        message = json.dumps(data, sort_keys=True).encode('utf-8')
        return hmac.new(self.secret, message, hashlib.sha256).hexdigest()