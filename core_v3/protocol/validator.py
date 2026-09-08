"""
Message Validator

Validation of protocol messages.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import json
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union, Callable, Set
from abc import ABC, abstractmethod

from .message import MessageEnvelope, MessageType, MessageHeader
from ..types import VireoValue, VireoObject, VireoArray
from ..errors import VireoValidationError, VireoMessageError


class ValidationResult:
    """Result of validation."""
    
    def __init__(self, valid: bool = True, errors: Optional[List[str]] = None):
        self.valid = valid
        self.errors = errors or []
    
    @classmethod
    def success(cls) -> ValidationResult:
        return cls(True, [])
    
    @classmethod
    def failure(cls, *errors: str) -> ValidationResult:
        return cls(False, list(errors))
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.valid = False
    
    def merge(self, other: ValidationResult) -> ValidationResult:
        self.valid = self.valid and other.valid
        self.errors.extend(other.errors)
        return self
    
    def is_valid(self) -> bool:
        return self.valid


class ValidationRule(ABC):
    """Base class for validation rules."""
    
    @abstractmethod
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        """Validate a message."""
        pass
    
    @property
    def name(self) -> str:
        return self.__class__.__name__


class MessageTypeRule(ValidationRule):
    """Validate message type."""
    
    def __init__(self, allowed_types: List[MessageType]):
        self.allowed_types = allowed_types
    
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        if message.header.type not in self.allowed_types:
            return ValidationResult.failure(
                f"Invalid message type: {message.header.type.value}"
            )
        return ValidationResult.success()


class VersionRule(ValidationRule):
    """Validate protocol version."""
    
    def __init__(self, min_version: str, max_version: Optional[str] = None):
        self.min_version = min_version
        self.max_version = max_version
    
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        version = message.header.version
        
        if not self._version_gte(version, self.min_version):
            return ValidationResult.failure(
                f"Version {version} is less than minimum {self.min_version}"
            )
        
        if self.max_version and not self._version_lte(version, self.max_version):
            return ValidationResult.failure(
                f"Version {version} is greater than maximum {self.max_version}"
            )
        
        return ValidationResult.success()
    
    def _version_parse(self, version: str) -> List[int]:
        """Parse version string to list of ints."""
        parts = re.sub(r'[^0-9.]', '', version).split('.')
        return [int(p) for p in parts if p]
    
    def _version_gte(self, v1: str, v2: str) -> bool:
        """Check if v1 >= v2."""
        parts1 = self._version_parse(v1)
        parts2 = self._version_parse(v2)
        
        for i in range(max(len(parts1), len(parts2))):
            p1 = parts1[i] if i < len(parts1) else 0
            p2 = parts2[i] if i < len(parts2) else 0
            if p1 < p2:
                return False
            if p1 > p2:
                return True
        return True
    
    def _version_lte(self, v1: str, v2: str) -> bool:
        """Check if v1 <= v2."""
        return self._version_gte(v2, v1)


class SignatureRule(ValidationRule):
    """Validate message signature."""
    
    def __init__(self, verify_func: Callable[[bytes, bytes], bool]):
        self.verify_func = verify_func
    
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        if not message.header.signature:
            return ValidationResult.failure("Missing signature")
        
        # Reconstruct signed data
        signed_data = self._get_signed_data(message)
        
        if not self.verify_func(signed_data, message.header.signature.value):
            return ValidationResult.failure("Invalid signature")
        
        return ValidationResult.success()
    
    def _get_signed_data(self, message: MessageEnvelope) -> bytes:
        """Get data that should be signed."""
        # Header without signature
        header_data = {
            "type": message.header.type.value,
            "version": message.header.version,
            "message_id": message.header.message_id,
            "timestamp": message.header.timestamp.isoformat(),
            "sender": message.header.sender,
            "receiver": message.header.receiver,
            "correlation_id": message.header.correlation_id,
            "reply_to": message.header.reply_to,
            "nonce": message.header.nonce.hex() if message.header.nonce else None,
            "ttl_seconds": message.header.ttl_seconds,
            "priority": message.header.priority,
            "flags": message.header.flags,
        }
        
        data = json.dumps(header_data, sort_keys=True).encode('utf-8')
        
        # Add body if present
        if message.body:
            data += message.body.to_bytes()
        
        return data


class NonceRule(ValidationRule):
    """Validate nonce."""
    
    def __init__(self, nonce_manager):
        self.nonce_manager = nonce_manager
    
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        if not message.header.nonce:
            return ValidationResult.failure("Missing nonce")
        
        if not self.nonce_manager.validate_nonce(
            message.header.sender,
            message.header.nonce,
            message.header.message_id,
        ):
            return ValidationResult.failure("Invalid or replayed nonce")
        
        return ValidationResult.success()


class TTLRule(ValidationRule):
    """Validate TTL."""
    
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        if message.header.is_expired():
            return ValidationResult.failure(
                f"Message expired (TTL: {message.header.ttl_seconds}s)"
            )
        return ValidationResult.success()


class BodySchemaRule(ValidationRule):
    """Validate body against schema."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        if not message.body:
            return ValidationResult.failure("Missing body")
        
        if not message.body.schema_uri:
            return ValidationResult.failure("Missing schema URI")
        
        # Check if schema matches
        if message.body.schema_uri != self.schema.get("$id"):
            return ValidationResult.failure(
                f"Schema mismatch: {message.body.schema_uri} != {self.schema.get('$id')}"
            )
        
        # Basic schema validation
        return self._validate_value(message.body.data, self.schema)
    
    def _validate_value(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        """Validate a value against a schema."""
        schema_type = schema.get("type")
        
        if schema_type == "object":
            return self._validate_object(value, schema)
        elif schema_type == "array":
            return self._validate_array(value, schema)
        elif schema_type == "string":
            return self._validate_string(value, schema)
        elif schema_type == "integer":
            return self._validate_integer(value, schema)
        elif schema_type == "number":
            return self._validate_number(value, schema)
        elif schema_type == "boolean":
            return self._validate_boolean(value, schema)
        elif schema_type == "null":
            return self._validate_null(value, schema)
        else:
            return ValidationResult.success()
    
    def _validate_object(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        if not isinstance(value, VireoObject):
            return ValidationResult.failure(f"Expected object, got {type(value)}")
        
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        for prop in required:
            if prop not in value.value:
                return ValidationResult.failure(f"Missing required property: {prop}")
        
        for prop, prop_schema in properties.items():
            if prop in value.value:
                result = self._validate_value(value.value[prop], prop_schema)
                if not result.is_valid():
                    return result
        
        return ValidationResult.success()
    
    def _validate_array(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        if not isinstance(value, VireoArray):
            return ValidationResult.failure(f"Expected array, got {type(value)}")
        
        items_schema = schema.get("items")
        if items_schema:
            for item in value.value:
                result = self._validate_value(item, items_schema)
                if not result.is_valid():
                    return result
        
        return ValidationResult.success()
    
    def _validate_string(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        if not isinstance(value, VireoString):
            return ValidationResult.failure(f"Expected string, got {type(value)}")
        
        # Check min/max length
        min_len = schema.get("minLength")
        max_len = schema.get("maxLength")
        
        if min_len and len(value.value) < min_len:
            return ValidationResult.failure(f"String too short: {len(value.value)} < {min_len}")
        if max_len and len(value.value) > max_len:
            return ValidationResult.failure(f"String too long: {len(value.value)} > {max_len}")
        
        # Check pattern
        pattern = schema.get("pattern")
        if pattern and not re.match(pattern, value.value):
            return ValidationResult.failure(f"String doesn't match pattern: {pattern}")
        
        return ValidationResult.success()
    
    def _validate_integer(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        if not isinstance(value, VireoInteger):
            return ValidationResult.failure(f"Expected integer, got {type(value)}")
        
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        
        if minimum is not None and value.value < minimum:
            return ValidationResult.failure(f"Value {value.value} < {minimum}")
        if maximum is not None and value.value > maximum:
            return ValidationResult.failure(f"Value {value.value} > {maximum}")
        
        return ValidationResult.success()
    
    def _validate_number(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        if not isinstance(value, (VireoInteger, VireoFloat)):
            return ValidationResult.failure(f"Expected number, got {type(value)}")
        
        return ValidationResult.success()
    
    def _validate_boolean(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        if not isinstance(value, VireoBoolean):
            return ValidationResult.failure(f"Expected boolean, got {type(value)}")
        return ValidationResult.success()
    
    def _validate_null(self, value: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        if not isinstance(value, VireoNull):
            return ValidationResult.failure(f"Expected null, got {type(value)}")
        return ValidationResult.success()


class ValidatorRegistry:
    """Registry for validation rules."""
    
    def __init__(self):
        self._rules: Dict[str, ValidationRule] = {}
        self._default_rules: List[ValidationRule] = []
    
    def register(self, name: str, rule: ValidationRule) -> None:
        """Register a validation rule."""
        self._rules[name] = rule
    
    def add_default_rule(self, rule: ValidationRule) -> None:
        """Add a default rule."""
        self._default_rules.append(rule)
    
    def get(self, name: str) -> Optional[ValidationRule]:
        """Get a rule by name."""
        return self._rules.get(name)
    
    def get_defaults(self) -> List[ValidationRule]:
        """Get default rules."""
        return self._default_rules.copy()


class MessageValidator:
    """Main message validator."""
    
    def __init__(self):
        self._registry = ValidatorRegistry()
        self._rules: List[ValidationRule] = []
        self._setup_defaults()
    
    def _setup_defaults(self) -> None:
        """Setup default validation rules."""
        # Add default rules
        self._registry.add_default_rule(MessageTypeRule([
            MessageType.PROPOSE,
            MessageType.COMMIT,
            MessageType.EXECUTE,
            MessageType.VERIFY,
            MessageType.ESCALATE,
            MessageType.DONE,
            MessageType.FAILED,
            MessageType.ACK,
            MessageType.NACK,
            MessageType.QUERY,
            MessageType.RESPONSE,
            MessageType.ERROR,
        ]))
        self._registry.add_default_rule(VersionRule("3.0.0", "3.0.9"))
        self._registry.add_default_rule(TTLRule())
        
        # Apply defaults
        self._rules = self._registry.get_defaults()
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self._rules.append(rule)
    
    def add_rules(self, rules: List[ValidationRule]) -> None:
        """Add multiple validation rules."""
        self._rules.extend(rules)
    
    def validate(self, message: MessageEnvelope) -> ValidationResult:
        """Validate a message."""
        result = ValidationResult.success()
        
        for rule in self._rules:
            try:
                rule_result = rule.validate(message)
                if not rule_result.is_valid():
                    result.merge(rule_result)
            except Exception as e:
                result.add_error(f"Rule {rule.name} error: {e}")
        
        return result
    
    def validate_header(self, header: MessageHeader) -> ValidationResult:
        """Validate only the header."""
        # Create a minimal envelope
        envelope = MessageEnvelope(header)
        return self.validate(envelope)
    
    def validate_body(self, body: VireoValue, schema: Dict[str, Any]) -> ValidationResult:
        """Validate a body against schema."""
        rule = BodySchemaRule(schema)
        # Create a mock message for validation
        return rule.validate(MessageEnvelope(
            MessageHeader(
                type=MessageType.QUERY,
                version="3.0.0",
                message_id="test",
                timestamp=datetime.now(datetime.timezone.utc),
                sender="test",
            ),
            MessageBody("application/json", body),
        ))
    
    @classmethod
    def default_validator(cls) -> MessageValidator:
        """Create a default validator."""
        return cls()