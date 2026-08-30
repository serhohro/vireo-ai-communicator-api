# ============================================================
# LAYER 3 — TRUST & SECURITY VERSION = "1.4.3"
# ============================================================

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
import logging
from typing import Optional, Dict, Tuple, Any, List
from dataclasses import dataclass, field
from enum import Enum

from .message import Message

logger = logging.getLogger("vireo.protocol.trust")


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class Identity:
    id: str
    public_key: Optional[str] = None
    permissions: List[Permission] = field(default_factory=list)
    trust_level: float = 0.5
    model: Optional[str] = None
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions or Permission.ADMIN in self.permissions


def sign(message: Message, secret: str) -> str:
    payload = message.unsigned_payload_for_signature().encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return digest


def attach_signature(message: Message, secret: str) -> Message:
    message.signature = sign(message, secret)
    return message


def verify(message: Message, secret: str) -> bool:
    if message.signature is None:
        return False
    expected = sign(message, secret)
    return hmac.compare_digest(expected, message.signature)


class TrustManager:
    def __init__(self, secret: Optional[str] = None, ttl: int = 60):
        self.secret = secret
        self.ttl = ttl
        self._used_nonces: Dict[str, float] = {}
        self._identities: Dict[str, Identity] = {}
    
    def register_identity(self, identity: Identity) -> None:
        self._identities[identity.id] = identity
    
    def get_identity(self, agent_id: str) -> Optional[Identity]:
        return self._identities.get(agent_id)
    
    def generate_nonce(self) -> Tuple[str, float]:
        nonce = secrets.token_hex(32)
        timestamp = time.time()
        return nonce, timestamp
    
    def validate_nonce(self, nonce: str, timestamp: float) -> bool:
        if nonce in self._used_nonces:
            return False
        if time.time() - timestamp > self.ttl:
            return False
        self._used_nonces[nonce] = timestamp
        return True