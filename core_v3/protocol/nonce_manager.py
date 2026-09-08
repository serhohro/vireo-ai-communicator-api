"""
Nonce Manager

Replay protection via nonce management.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import time
import threading
from typing import Optional, Dict, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from ..types import VireoNonce
from ..errors import VireoNonceError, VireoProtocolError


class NonceError(VireoProtocolError):
    """Nonce-related errors."""
    
    def __init__(self, message: str, nonce: Optional[str] = None):
        super().__init__(message, "VIREO_1030", {"nonce": nonce})


class NonceStorage:
    """Interface for nonce storage."""
    
    def store(self, sender: str, nonce: VireoNonce, message_id: str) -> None:
        """Store a nonce."""
        raise NotImplementedError
    
    def exists(self, sender: str, nonce: VireoNonce) -> bool:
        """Check if nonce exists."""
        raise NotImplementedError
    
    def mark_used(self, sender: str, nonce: VireoNonce, message_id: str) -> None:
        """Mark nonce as used."""
        raise NotImplementedError
    
    def is_used(self, sender: str, nonce: VireoNonce) -> bool:
        """Check if nonce has been used."""
        raise NotImplementedError
    
    def cleanup(self, max_age_seconds: int) -> None:
        """Clean up old nonces."""
        raise NotImplementedError


class InMemoryNonceStorage(NonceStorage):
    """In-memory nonce storage."""
    
    def __init__(self):
        self._nonces: Dict[str, Dict[str, Dict[str, float]]] = {}
        self._lock = threading.RLock()
    
    def _get_sender_nonces(self, sender: str) -> Dict[str, Dict[str, float]]:
        if sender not in self._nonces:
            self._nonces[sender] = {}
        return self._nonces[sender]
    
    def store(self, sender: str, nonce: VireoNonce, message_id: str) -> None:
        with self._lock:
            sender_nonces = self._get_sender_nonces(sender)
            nonce_hex = nonce.hex()
            sender_nonces[nonce_hex] = {
                "message_id": message_id,
                "timestamp": time.time(),
                "used": False,
            }
    
    def exists(self, sender: str, nonce: VireoNonce) -> bool:
        with self._lock:
            sender_nonces = self._get_sender_nonces(sender)
            return nonce.hex() in sender_nonces
    
    def mark_used(self, sender: str, nonce: VireoNonce, message_id: str) -> None:
        with self._lock:
            sender_nonces = self._get_sender_nonces(sender)
            nonce_hex = nonce.hex()
            if nonce_hex in sender_nonces:
                sender_nonces[nonce_hex]["used"] = True
                sender_nonces[nonce_hex]["message_id"] = message_id
    
    def is_used(self, sender: str, nonce: VireoNonce) -> bool:
        with self._lock:
            sender_nonces = self._get_sender_nonces(sender)
            nonce_hex = nonce.hex()
            if nonce_hex in sender_nonces:
                return sender_nonces[nonce_hex].get("used", False)
            return False
    
    def cleanup(self, max_age_seconds: int) -> None:
        with self._lock:
            now = time.time()
            for sender in list(self._nonces.keys()):
                sender_nonces = self._nonces[sender]
                for nonce_hex in list(sender_nonces.keys()):
                    if now - sender_nonces[nonce_hex]["timestamp"] > max_age_seconds:
                        del sender_nonces[nonce_hex]
                if not sender_nonces:
                    del self._nonces[sender]


class RedisNonceStorage(NonceStorage):
    """Redis-based nonce storage."""
    
    def __init__(self, redis_client, prefix: str = "vireo:nonce:"):
        self._redis = redis_client
        self._prefix = prefix
    
    def _key(self, sender: str, nonce_hex: str) -> str:
        return f"{self._prefix}{sender}:{nonce_hex}"
    
    def store(self, sender: str, nonce: VireoNonce, message_id: str) -> None:
        key = self._key(sender, nonce.hex())
        self._redis.hset(key, "message_id", message_id)
        self._redis.hset(key, "timestamp", time.time())
        self._redis.hset(key, "used", "0")
    
    def exists(self, sender: str, nonce: VireoNonce) -> bool:
        key = self._key(sender, nonce.hex())
        return self._redis.exists(key) > 0
    
    def mark_used(self, sender: str, nonce: VireoNonce, message_id: str) -> None:
        key = self._key(sender, nonce.hex())
        self._redis.hset(key, "used", "1")
        self._redis.hset(key, "message_id", message_id)
    
    def is_used(self, sender: str, nonce: VireoNonce) -> bool:
        key = self._key(sender, nonce.hex())
        used = self._redis.hget(key, "used")
        return used == b"1"
    
    def cleanup(self, max_age_seconds: int) -> None:
        # Redis handles expiration automatically
        # We can use EXPIRE on keys
        pass


class NonceManager:
    """
    Nonce manager for replay protection.
    
    Tracks and validates nonces to prevent replay attacks.
    """
    
    def __init__(
        self,
        storage: Optional[NonceStorage] = None,
        max_age_seconds: int = 300,
        max_clock_skew_seconds: int = 30,
    ):
        self.storage = storage or InMemoryNonceStorage()
        self.max_age_seconds = max_age_seconds
        self.max_clock_skew_seconds = max_clock_skew_seconds
        self._lock = threading.RLock()
    
    def generate_nonce(self) -> VireoNonce:
        """Generate a new nonce."""
        return VireoNonce.random()
    
    def register_nonce(self, sender: str, nonce: VireoNonce, message_id: str) -> None:
        """
        Register a nonce.
        
        Called when receiving a message with a nonce.
        """
        with self._lock:
            # Check if nonce is known
            if self.storage.exists(sender, nonce):
                raise NonceError(
                    f"Nonce already exists: {nonce.hex()}",
                    nonce.hex()
                )
            
            # Store nonce
            self.storage.store(sender, nonce, message_id)
    
    def validate_nonce(self, sender: str, nonce: VireoNonce, message_id: str) -> bool:
        """
        Validate a nonce.
        
        Returns True if nonce is valid and not used.
        """
        with self._lock:
            # Check if nonce exists
            if not self.storage.exists(sender, nonce):
                return False
            
            # Check if nonce has been used
            if self.storage.is_used(sender, nonce):
                return False
            
            # Mark as used
            self.storage.mark_used(sender, nonce, message_id)
            
            return True
    
    def validate_and_consume(self, sender: str, nonce: VireoNonce, message_id: str) -> bool:
        """
        Validate and consume a nonce in one operation.
        
        Returns True if nonce is valid and was consumed.
        """
        with self._lock:
            if not self.validate_nonce(sender, nonce, message_id):
                return False
            
            # Mark as used
            self.storage.mark_used(sender, nonce, message_id)
            return True
    
    def cleanup(self) -> None:
        """Clean up expired nonces."""
        self.storage.cleanup(self.max_age_seconds)
    
    def create_nonce_for_message(self, sender: str, message_id: str) -> VireoNonce:
        """
        Create and register a new nonce for a message.
        
        Returns the generated nonce.
        """
        nonce = self.generate_nonce()
        self.register_nonce(sender, nonce, message_id)
        return nonce
    
    def is_nonce_valid(self, sender: str, nonce: VireoNonce) -> bool:
        """Check if a nonce is valid (exists and not used)."""
        with self._lock:
            if not self.storage.exists(sender, nonce):
                return False
            if self.storage.is_used(sender, nonce):
                return False
            return True
    
    def get_nonce_state(self, sender: str, nonce: VireoNonce) -> Dict[str, Any]:
        """Get the state of a nonce."""
        with self._lock:
            return {
                "sender": sender,
                "nonce": nonce.hex(),
                "exists": self.storage.exists(sender, nonce),
                "used": self.storage.is_used(sender, nonce) if self.storage.exists(sender, nonce) else False,
            }