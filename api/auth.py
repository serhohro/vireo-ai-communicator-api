# api/auth.py
"""Vireo API Authentication - Flask version."""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps
from dataclasses import dataclass
from flask import request, jsonify, g

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class AuthContext:
    """Authentication context."""
    agent_id: str
    did: str = ""
    api_key: Optional[str] = None
    token_type: str = "api_key"
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = ["*"]


# ============================================================
# API KEY MANAGEMENT
# ============================================================

_api_keys = {}
_blacklist = set()

def generate_api_key() -> str:
    """Generate a new API key."""
    return f"vireo_{secrets.token_urlsafe(32)}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key(agent_id: str, did: str = "", expires_days: int = 365) -> Dict[str, Any]:
    """Create a new API key."""
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    
    _api_keys[key_hash] = {
        "agent_id": agent_id,
        "did": did,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
        "active": True
    }
    
    return {
        "api_key": api_key,
        "agent_id": agent_id,
        "did": did,
        "expires_at": _api_keys[key_hash]["expires_at"]
    }

def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Verify an API key."""
    if not api_key:
        return None
    
    key_hash = hash_api_key(api_key)
    key_data = _api_keys.get(key_hash)
    
    if not key_data:
        return None
    
    if not key_data.get("active", True):
        return None
    
    expires_at = key_data.get("expires_at")
    if expires_at and datetime.utcnow() > datetime.fromisoformat(expires_at):
        return None
    
    return key_data

def verify_api_key_context(api_key: str) -> Optional[AuthContext]:
    """Verify API key and return AuthContext."""
    key_data = verify_api_key(api_key)
    if not key_data:
        return None
    
    return AuthContext(
        agent_id=key_data["agent_id"],
        did=key_data.get("did", ""),
        api_key=api_key,
        token_type="api_key"
    )


# ============================================================
# DECORATORS
# ============================================================

def require_api_key(f):
    """Decorator to require API key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        key_data = verify_api_key(api_key)
        if not key_data:
            return jsonify({"error": "Invalid or expired API key"}), 401
        
        g.agent_id = key_data["agent_id"]
        g.auth_context = AuthContext(
            agent_id=key_data["agent_id"],
            did=key_data.get("did", ""),
            api_key=api_key
        )
        return f(*args, **kwargs)
    return decorated

def require_auth(f):
    """Decorator to require authentication (API key or JWT)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Try API key first
        api_key = request.headers.get('X-API-Key')
        if api_key:
            key_data = verify_api_key(api_key)
            if key_data:
                g.agent_id = key_data["agent_id"]
                g.auth_context = AuthContext(
                    agent_id=key_data["agent_id"],
                    did=key_data.get("did", ""),
                    api_key=api_key,
                    token_type="api_key"
                )
                g.auth_type = "api_key"
                return f(*args, **kwargs)
        
        # Try JWT (simplified)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token and len(token) > 20:
                g.agent_id = "jwt_agent"
                g.auth_context = AuthContext(
                    agent_id="jwt_agent",
                    did="did:vireo:jwt_agent",
                    token_type="jwt"
                )
                g.auth_type = "jwt"
                return f(*args, **kwargs)
        
        return jsonify({"error": "Authentication required"}), 401
    return decorated


# ============================================================
# AUTH MANAGER
# ============================================================

class AuthManager:
    """Authentication manager for Flask."""
    
    def __init__(self):
        self.api_keys = _api_keys
        self.blacklist = _blacklist
    
    def create_api_key(self, agent_id: str, did: str = "", expires_days: int = 365) -> Dict[str, Any]:
        return create_api_key(agent_id, did, expires_days)
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        return verify_api_key(api_key)
    
    def verify_api_key_context(self, api_key: str) -> Optional[AuthContext]:
        return verify_api_key_context(api_key)
    
    def revoke_api_key(self, api_key: str) -> bool:
        key_hash = hash_api_key(api_key)
        if key_hash in self.api_keys:
            self.api_keys[key_hash]["active"] = False
            return True
        return False
    
    def list_api_keys(self, agent_id: str) -> list:
        keys = []
        for key_hash, key_data in self.api_keys.items():
            if key_data.get("agent_id") == agent_id:
                keys.append({
                    "hash": key_hash[:8] + "...",
                    "created_at": key_data.get("created_at"),
                    "expires_at": key_data.get("expires_at"),
                    "active": key_data.get("active", True)
                })
        return keys
    
    def get_auth_context(self, agent_id: str) -> Optional[AuthContext]:
        """Get auth context for agent."""
        return AuthContext(agent_id=agent_id)


# ============================================================
# GLOBAL INSTANCE
# ============================================================

_auth_manager = None

def get_auth_manager() -> AuthManager:
    """Get global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager