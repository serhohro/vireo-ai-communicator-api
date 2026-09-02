"""Trust Bootstrap Protocol for Vireo v2.0.1"""

from typing import Dict, Optional, Tuple, Any
import base64
import hashlib
import time
from datetime import datetime, timedelta
import logging

from .key_manager import KeyManager
from ..protocol.message import Message, MessageType

logger = logging.getLogger(__name__)


class TrustBootstrapProtocol:
    """Trust Bootstrap Protocol implementation"""
    
    def __init__(self, agent_id: str, key_manager: KeyManager):
        self.agent_id = agent_id
        self.key_manager = key_manager
        self.trusted_peers: Dict[str, Dict[str, Any]] = {}
        self._nonce_cache = set()
        self._logger = logging.getLogger(f"{__name__}.{agent_id}")
    
    def create_challenge(self) -> Dict[str, Any]:
        """Create a challenge for identity verification"""
        nonce = hashlib.sha256(
            str(time.time()).encode() + os.urandom(32)
        ).hexdigest()
        
        self._nonce_cache.add(nonce)
        # Clean cache periodically
        if len(self._nonce_cache) > 1000:
            self._nonce_cache = set(list(self._nonce_cache)[-500:])
        
        return {
            "nonce": nonce,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def verify_challenge_response(
        self,
        agent_id: str,
        nonce: str,
        signature: str,
        public_key_b64: str,
        timestamp: str
    ) -> Tuple[bool, str]:
        """Verify a challenge response"""
        # Check timestamp (max 5 minutes)
        try:
            ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            if datetime.utcnow() - ts > timedelta(minutes=5):
                return False, "timestamp_expired"
        except ValueError:
            return False, "invalid_timestamp"
        
        # Check nonce not reused
        if nonce not in self._nonce_cache:
            return False, "nonce_not_found_or_reused"
        
        # Remove from cache after use
        self._nonce_cache.remove(nonce)
        
        # Decode public key
        try:
            public_key = base64.b64decode(public_key_b64)
        except Exception:
            return False, "invalid_public_key"
        
        # Verify signature
        message = (nonce + timestamp).encode()
        try:
            signature_bytes = base64.b64decode(signature)
        except Exception:
            return False, "invalid_signature"
        
        if not self.key_manager.verify(message, signature_bytes, public_key):
            return False, "signature_verification_failed"
        
        # Store trusted peer
        self.trusted_peers[agent_id] = {
            "public_key": public_key_b64,
            "verified_at": datetime.utcnow().isoformat() + "Z",
            "trust_level": "full"
        }
        
        return True, "verified"
    
    def get_trust_level(self, agent_id: str) -> str:
        """Get trust level for a peer"""
        if agent_id not in self.trusted_peers:
            return "none"
        return self.trusted_peers[agent_id].get("trust_level", "none")
    
    def is_trusted(self, agent_id: str, level: str = "full") -> bool:
        """Check if peer is trusted at a given level"""
        return self.get_trust_level(agent_id) == level
    
    def revoke_trust(self, agent_id: str, reason: str = "manual") -> None:
        """Revoke trust for a peer"""
        if agent_id in self.trusted_peers:
            self.trusted_peers[agent_id]["trust_level"] = "none"
            self.trusted_peers[agent_id]["revoked_at"] = datetime.utcnow().isoformat() + "Z"
            self.trusted_peers[agent_id]["revoked_reason"] = reason
            self._logger.info(f"Revoked trust for {agent_id}: {reason}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export trust state"""
        return {
            "agent_id": self.agent_id,
            "trusted_peers": self.trusted_peers,
            "trusted_count": len(self.trusted_peers)
        }
    
    @classmethod
    def create_message(cls, agent_id: str, peer_id: str, challenge_data: Dict) -> Message:
        """Create a challenge message"""
        return Message(
            type=MessageType.DISCOVER,
            sender_id=agent_id,
            recipient_id=peer_id,
            payload={
                "challenge": challenge_data
            }
        )


# Singleton instance
_trust_bootstrap: Optional[TrustBootstrapProtocol] = None


def get_trust_bootstrap(agent_id: str, key_manager: Optional[KeyManager] = None) -> TrustBootstrapProtocol:
    """Get or create TrustBootstrapProtocol instance"""
    global _trust_bootstrap
    if _trust_bootstrap is None:
        if key_manager is None:
            raise ValueError("KeyManager required for first initialization")
        _trust_bootstrap = TrustBootstrapProtocol(agent_id, key_manager)
    return _trust_bootstrap