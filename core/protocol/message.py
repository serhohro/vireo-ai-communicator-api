"""Message definition for Vireo v2.0.1"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json


class MessageType(Enum):
    """Message types"""
    DISCOVER = "discover"
    DISCOVER_RESPONSE = "discover_response"
    PROPOSAL = "proposal"
    ACCEPT = "accept"
    REJECT = "reject"
    COMMIT = "commit"
    EXECUTE = "execute"
    EXECUTION_RESULT = "execution_result"
    VERIFY = "verify"
    VERIFICATION_RESULT = "verification_result"
    ESCALATE = "escalate"
    DONE = "done"
    ERROR = "error"


@dataclass
class Message:
    """Vireo protocol message"""
    
    version: str = "2.0.1"
    type: MessageType = MessageType.DISCOVER
    message_id: Optional[str] = None
    timestamp: Optional[str] = None
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "version": self.version,
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "metadata": self.metadata,
            "signature": self.signature
        }
    
    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dict"""
        if "type" in data and isinstance(data["type"], str):
            data["type"] = MessageType(data["type"])
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create from JSON"""
        data = json.loads(json_str)
        if "type" in data and isinstance(data["type"], str):
            data["type"] = MessageType(data["type"])
        return cls(**data)
    
    def sign(self, key_manager) -> 'Message':
        """Sign the message"""
        import hashlib
        import base64
        
        # Create canonical payload
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        
        # Hash
        digest = hashlib.sha256(canonical.encode()).digest()
        
        # Sign
        signature = key_manager.sign(digest)
        self.signature = base64.b64encode(signature).decode()
        return self
    
    def verify(self, public_key: bytes) -> bool:
        """Verify message signature"""
        if self.signature is None:
            return False
        
        import hashlib
        import base64
        
        # Create canonical payload
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        digest = hashlib.sha256(canonical.encode()).digest()
        
        # Decode signature
        try:
            signature_bytes = base64.b64decode(self.signature)
            from cryptography.hazmat.primitives import ed25519
            public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
            public_key_obj.verify(signature_bytes, digest)
            return True
        except Exception:
            return False
    
    @classmethod
    def create_discover(cls, sender_id: str, capabilities_required: list) -> 'Message':
        return cls(
            type=MessageType.DISCOVER,
            sender_id=sender_id,
            payload={
                "capabilities_required": capabilities_required
            }
        )
    
    @classmethod
    def create_proposal(cls, sender_id: str, recipient_id: str, contract: dict) -> 'Message':
        return cls(
            type=MessageType.PROPOSAL,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={
                "contract": contract
            }
        )
    
    @classmethod
    def create_accept(cls, sender_id: str, recipient_id: str, proposal_id: str) -> 'Message':
        return cls(
            type=MessageType.ACCEPT,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={
                "proposal_id": proposal_id
            }
        )
    
    @classmethod
    def create_commit(cls, sender_id: str, recipient_id: str, contract_id: str, signatures: dict) -> 'Message':
        return cls(
            type=MessageType.COMMIT,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={
                "contract_id": contract_id,
                "signatures": signatures
            }
        )
    
    @classmethod
    def create_verify(cls, sender_id: str, recipient_id: str, contract_id: str) -> 'Message':
        return cls(
            type=MessageType.VERIFY,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={
                "contract_id": contract_id
            }
        )
    
    @classmethod
    def create_escalate(cls, sender_id: str, recipient_id: str, contract_id: str, reason: str) -> 'Message':
        return cls(
            type=MessageType.ESCALATE,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={
                "contract_id": contract_id,
                "reason": reason
            }
        )