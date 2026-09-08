"""
Protocol Messages

Message types and structures for Vireo protocol.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import json
import struct
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union, Tuple, IO
from datetime import datetime
from uuid import uuid4

from ..types import (
    VireoValue,
    VireoObject,
    VireoArray,
    VireoString,
    VireoInteger,
    VireoFloat,
    VireoBoolean,
    VireoNull,
    VireoBinary,
    VireoTimestamp,
    VireoDID,
    VireoSignature,
    VireoNonce,
    VireoVersion,
    VireoUUID,
)
from ..errors import VireoMessageError, VireoValidationError


class MessageType(Enum):
    """Types of protocol messages."""
    PROPOSE = "propose"       # Propose an action/contract
    COMMIT = "commit"         # Commit to a proposal
    EXECUTE = "execute"       # Execute committed action
    VERIFY = "verify"         # Verify execution
    ESCALATE = "escalate"     # Escalate for resolution
    DONE = "done"            # Completion
    FAILED = "failed"        # Failure
    TIMEOUT = "timeout"      # Timeout
    ACK = "ack"              # Acknowledgement
    NACK = "nack"            # Negative acknowledgement
    QUERY = "query"          # Query for information
    RESPONSE = "response"    # Response to query
    ERROR = "error"          # Error message
    
    @classmethod
    def from_string(cls, value: str) -> MessageType:
        try:
            return cls(value.lower())
        except ValueError:
            raise VireoMessageError(f"Invalid message type: {value}")


@dataclass
class MessageHeader:
    """Message header."""
    type: MessageType
    version: str
    message_id: str
    timestamp: datetime
    sender: str
    receiver: Optional[str] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    nonce: Optional[VireoNonce] = None
    signature: Optional[VireoSignature] = None
    ttl_seconds: int = 300
    priority: int = 0
    flags: List[str] = field(default_factory=list)
    
    def to_bytes(self) -> bytes:
        """Serialize header to bytes."""
        data = {
            "type": self.type.value,
            "version": self.version,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender,
            "receiver": self.receiver,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "nonce": self.nonce.hex() if self.nonce else None,
            "signature": self.signature.hex() if self.signature else None,
            "ttl_seconds": self.ttl_seconds,
            "priority": self.priority,
            "flags": self.flags,
        }
        return json.dumps(data, sort_keys=True).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> MessageHeader:
        """Deserialize header from bytes."""
        try:
            json_data = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise VireoMessageError(f"Invalid header JSON: {e}")
        
        # Handle nonce
        nonce = None
        if json_data.get("nonce"):
            try:
                nonce = VireoNonce(bytes.fromhex(json_data["nonce"]))
            except:
                pass
        
        # Handle signature
        signature = None
        if json_data.get("signature"):
            try:
                signature = VireoSignature(bytes.fromhex(json_data["signature"]))
            except:
                pass
        
        return cls(
            type=MessageType.from_string(json_data["type"]),
            version=json_data["version"],
            message_id=json_data["message_id"],
            timestamp=datetime.fromisoformat(json_data["timestamp"]),
            sender=json_data["sender"],
            receiver=json_data.get("receiver"),
            correlation_id=json_data.get("correlation_id"),
            reply_to=json_data.get("reply_to"),
            nonce=nonce,
            signature=signature,
            ttl_seconds=json_data.get("ttl_seconds", 300),
            priority=json_data.get("priority", 0),
            flags=json_data.get("flags", []),
        )
    
    def is_expired(self) -> bool:
        """Check if header has expired."""
        age = (datetime.now(datetime.timezone.utc) - self.timestamp).total_seconds()
        return age > self.ttl_seconds


@dataclass
class MessageBody:
    """Message body."""
    content_type: str
    data: VireoValue
    metadata: Dict[str, Any] = field(default_factory=dict)
    schema_uri: Optional[str] = None
    size: int = 0
    
    def __post_init__(self):
        self.size = self.calculate_size()
    
    def calculate_size(self) -> int:
        """Calculate body size in bytes."""
        # Rough estimate
        return len(str(self.data)) * 2
    
    def to_bytes(self) -> bytes:
        """Serialize body to bytes."""
        data = {
            "content_type": self.content_type,
            "data": self._serialize_value(self.data),
            "metadata": self.metadata,
            "schema_uri": self.schema_uri,
        }
        return json.dumps(data, sort_keys=True).encode('utf-8')
    
    def _serialize_value(self, value: VireoValue) -> Any:
        """Serialize VireoValue to Python types."""
        if isinstance(value, VireoNull):
            return None
        elif isinstance(value, VireoBoolean):
            return value.value
        elif isinstance(value, VireoInteger):
            return value.value
        elif isinstance(value, VireoFloat):
            return value.value
        elif isinstance(value, VireoString):
            return value.value
        elif isinstance(value, VireoBinary):
            return {"__binary__": value.value.hex()}
        elif isinstance(value, VireoTimestamp):
            return {"__timestamp__": value.value.isoformat()}
        elif isinstance(value, VireoArray):
            return [self._serialize_value(v) for v in value.value]
        elif isinstance(value, VireoObject):
            return {k: self._serialize_value(v) for k, v in value.value.items()}
        elif isinstance(value, VireoDID):
            return {"__did__": value.value}
        elif isinstance(value, VireoSignature):
            return {"__signature__": value.hex()}
        elif isinstance(value, VireoNonce):
            return {"__nonce__": value.hex()}
        elif isinstance(value, VireoVersion):
            return {"__version__": value.value}
        elif isinstance(value, VireoUUID):
            return {"__uuid__": str(value.value)}
        else:
            return str(value)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> MessageBody:
        """Deserialize body from bytes."""
        try:
            json_data = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise VireoMessageError(f"Invalid body JSON: {e}")
        
        content_type = json_data.get("content_type", "application/json")
        raw_data = json_data.get("data")
        metadata = json_data.get("metadata", {})
        schema_uri = json_data.get("schema_uri")
        
        return cls(
            content_type=content_type,
            data=cls._deserialize_value(raw_data),
            metadata=metadata,
            schema_uri=schema_uri,
        )
    
    @classmethod
    def _deserialize_value(cls, data: Any) -> VireoValue:
        """Deserialize Python value to VireoValue."""
        if data is None:
            return VireoNull()
        elif isinstance(data, bool):
            return VireoBoolean(data)
        elif isinstance(data, int):
            return VireoInteger(data)
        elif isinstance(data, float):
            return VireoFloat(data)
        elif isinstance(data, str):
            # Check for special types
            if data.startswith('{') and data.endswith('}'):
                try:
                    parsed = json.loads(data)
                    if isinstance(parsed, dict):
                        # Check if it's a special type
                        if "__binary__" in parsed:
                            return VireoBinary(bytes.fromhex(parsed["__binary__"]))
                        elif "__timestamp__" in parsed:
                            return VireoTimestamp(datetime.fromisoformat(parsed["__timestamp__"]))
                        elif "__did__" in parsed:
                            return VireoDID(parsed["__did__"])
                        elif "__signature__" in parsed:
                            return VireoSignature(bytes.fromhex(parsed["__signature__"]))
                        elif "__nonce__" in parsed:
                            return VireoNonce(bytes.fromhex(parsed["__nonce__"]))
                        elif "__version__" in parsed:
                            return VireoVersion.parse(parsed["__version__"])
                        elif "__uuid__" in parsed:
                            import uuid
                            return VireoUUID(uuid.UUID(parsed["__uuid__"]))
                        else:
                            return VireoObject({
                                k: cls._deserialize_value(v) for k, v in parsed.items()
                            })
                except:
                    pass
            return VireoString(data)
        elif isinstance(data, list):
            return VireoArray([cls._deserialize_value(item) for item in data])
        elif isinstance(data, dict):
            return VireoObject({
                k: cls._deserialize_value(v) for k, v in data.items()
            })
        else:
            return VireoString(str(data))


@dataclass
class MessageEnvelope:
    """Full message envelope."""
    header: MessageHeader
    body: Optional[MessageBody] = None
    
    def to_bytes(self) -> bytes:
        """Serialize entire message to bytes."""
        header_bytes = self.header.to_bytes()
        body_bytes = self.body.to_bytes() if self.body else b''
        
        # Format: [header_length:4][header_data][body_data]
        header_len = len(header_bytes)
        return struct.pack('>I', header_len) + header_bytes + body_bytes
    
    @classmethod
    def from_bytes(cls, data: bytes) -> MessageEnvelope:
        """Deserialize entire message from bytes."""
        if len(data) < 4:
            raise VireoMessageError("Message too short")
        
        header_len = struct.unpack('>I', data[:4])[0]
        if len(data) < 4 + header_len:
            raise VireoMessageError(f"Invalid header length: {header_len}")
        
        header_bytes = data[4:4 + header_len]
        body_bytes = data[4 + header_len:]
        
        header = MessageHeader.from_bytes(header_bytes)
        body = None
        if body_bytes:
            body = MessageBody.from_bytes(body_bytes)
        
        return cls(header, body)
    
    def is_valid(self) -> bool:
        """Check if message is valid."""
        if self.header.is_expired():
            return False
        if self.body and self.body.calculate_size() > 1024 * 1024:  # 1MB limit
            return False
        return True


class MessageBuilder:
    """Builder for constructing messages."""
    
    def __init__(self):
        self._header: Optional[MessageHeader] = None
        self._body: Optional[MessageBody] = None
    
    def message_type(self, type: MessageType) -> MessageBuilder:
        """Set message type."""
        if not self._header:
            self._header = self._create_header()
        self._header.type = type
        return self
    
    def version(self, version: str) -> MessageBuilder:
        """Set protocol version."""
        if not self._header:
            self._header = self._create_header()
        self._header.version = version
        return self
    
    def sender(self, sender: str) -> MessageBuilder:
        """Set sender."""
        if not self._header:
            self._header = self._create_header()
        self._header.sender = sender
        return self
    
    def receiver(self, receiver: str) -> MessageBuilder:
        """Set receiver."""
        if not self._header:
            self._header = self._create_header()
        self._header.receiver = receiver
        return self
    
    def correlation_id(self, corr_id: str) -> MessageBuilder:
        """Set correlation ID."""
        if not self._header:
            self._header = self._create_header()
        self._header.correlation_id = corr_id
        return self
    
    def reply_to(self, reply_to: str) -> MessageBuilder:
        """Set reply-to address."""
        if not self._header:
            self._header = self._create_header()
        self._header.reply_to = reply_to
        return self
    
    def nonce(self, nonce: VireoNonce) -> MessageBuilder:
        """Set nonce."""
        if not self._header:
            self._header = self._create_header()
        self._header.nonce = nonce
        return self
    
    def signature(self, signature: VireoSignature) -> MessageBuilder:
        """Set signature."""
        if not self._header:
            self._header = self._create_header()
        self._header.signature = signature
        return self
    
    def ttl(self, seconds: int) -> MessageBuilder:
        """Set TTL."""
        if not self._header:
            self._header = self._create_header()
        self._header.ttl_seconds = seconds
        return self
    
    def priority(self, priority: int) -> MessageBuilder:
        """Set priority."""
        if not self._header:
            self._header = self._create_header()
        self._header.priority = priority
        return self
    
    def flags(self, flags: List[str]) -> MessageBuilder:
        """Set flags."""
        if not self._header:
            self._header = self._create_header()
        self._header.flags = flags
        return self
    
    def body(self, content_type: str, data: VireoValue, metadata: Optional[Dict[str, Any]] = None) -> MessageBuilder:
        """Set message body."""
        self._body = MessageBody(
            content_type=content_type,
            data=data,
            metadata=metadata or {},
        )
        return self
    
    def schema(self, schema_uri: str) -> MessageBuilder:
        """Set schema URI."""
        if not self._body:
            self._body = MessageBody(
                content_type="application/json",
                data=VireoNull(),
            )
        self._body.schema_uri = schema_uri
        return self
    
    def _create_header(self) -> MessageHeader:
        """Create a new header with defaults."""
        return MessageHeader(
            type=MessageType.QUERY,
            version="3.0.0",
            message_id=str(uuid4()),
            timestamp=datetime.now(datetime.timezone.utc),
            sender="unknown",
        )
    
    def build(self) -> MessageEnvelope:
        """Build the message."""
        if not self._header:
            raise VireoMessageError("Message header is required")
        return MessageEnvelope(self._header, self._body)


class MessageParser:
    """Parser for messages."""
    
    @staticmethod
    def parse(data: bytes) -> MessageEnvelope:
        """Parse message from bytes."""
        return MessageEnvelope.from_bytes(data)
    
    @staticmethod
    def parse_header(data: bytes) -> MessageHeader:
        """Parse only header from bytes."""
        if len(data) < 4:
            raise VireoMessageError("Message too short")
        header_len = struct.unpack('>I', data[:4])[0]
        if len(data) < 4 + header_len:
            raise VireoMessageError(f"Invalid header length: {header_len}")
        return MessageHeader.from_bytes(data[4:4 + header_len])
    
    @staticmethod
    def extract_body(data: bytes) -> Optional[MessageBody]:
        """Extract body from bytes."""
        envelope = MessageEnvelope.from_bytes(data)
        return envelope.body
    
    @staticmethod
    def validate(data: bytes) -> bool:
        """Validate message format."""
        try:
            envelope = MessageEnvelope.from_bytes(data)
            return envelope.is_valid()
        except:
            return False