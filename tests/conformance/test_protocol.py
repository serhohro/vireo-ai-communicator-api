#!/usr/bin/env python3
"""
Conformance Tests: Protocol

Tests for the Vireo A2A protocol implementation.
"""

import pytest
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.protocol import Protocol, State, Message, MessageType
from core.protocol.validator import MessageValidator
from core.protocol.nonce_manager import NonceManager
from core.protocol.version import VersionManager


class TestProtocol:
    """Protocol conformance tests."""
    
    def test_protocol_initialization(self):
        """Test protocol initialization."""
        protocol = Protocol(version="3.0.0")
        assert protocol.get_state() == State.IDLE
        assert protocol.version == "3.0.0"
        assert protocol.get_history() == []
        
    def test_protocol_state_transitions(self):
        """Test state transitions."""
        protocol = Protocol()
        
        # IDLE -> PROPOSE
        assert protocol.transition(State.PROPOSE) is True
        assert protocol.get_state() == State.PROPOSE
        
        # PROPOSE -> COMMIT
        assert protocol.transition(State.COMMIT) is True
        assert protocol.get_state() == State.COMMIT
        
        # COMMIT -> EXECUTE
        assert protocol.transition(State.EXECUTE) is True
        assert protocol.get_state() == State.EXECUTE
        
        # EXECUTE -> VERIFY
        assert protocol.transition(State.VERIFY) is True
        assert protocol.get_state() == State.VERIFY
        
        # VERIFY -> DONE
        assert protocol.transition(State.DONE) is True
        assert protocol.get_state() == State.DONE
        
    def test_protocol_invalid_transitions(self):
        """Test invalid state transitions."""
        protocol = Protocol()
        
        # IDLE -> EXECUTE (invalid)
        assert protocol.transition(State.EXECUTE) is False
        assert protocol.get_state() == State.IDLE
        
        # IDLE -> DONE (invalid)
        assert protocol.transition(State.DONE) is False
        assert protocol.get_state() == State.IDLE
        
        # After PROPOSE
        protocol.transition(State.PROPOSE)
        # PROPOSE -> DONE (invalid)
        assert protocol.transition(State.DONE) is False
        assert protocol.get_state() == State.PROPOSE
        
    def test_protocol_history(self):
        """Test protocol history tracking."""
        protocol = Protocol()
        
        protocol.transition(State.PROPOSE)
        protocol.transition(State.COMMIT)
        protocol.transition(State.EXECUTE)
        
        history = protocol.get_history()
        assert len(history) == 3
        assert history[0] == State.IDLE
        assert history[1] == State.PROPOSE
        assert history[2] == State.COMMIT
        
    def test_protocol_reset(self):
        """Test protocol reset."""
        protocol = Protocol()
        
        protocol.transition(State.PROPOSE)
        protocol.transition(State.COMMIT)
        assert protocol.get_state() == State.COMMIT
        
        protocol.reset()
        assert protocol.get_state() == State.IDLE
        assert protocol.get_history() == []
        
    def test_protocol_allow_transition(self):
        """Test allowed transitions."""
        protocol = Protocol()
        
        allowed = protocol.get_allowed_transitions()
        assert State.PROPOSE in allowed
        assert State.COMMIT not in allowed
        assert State.EXECUTE not in allowed
        
        protocol.transition(State.PROPOSE)
        allowed = protocol.get_allowed_transitions()
        assert State.COMMIT in allowed
        assert State.CANCEL in allowed


class TestMessage:
    """Message conformance tests."""
    
    def test_message_creation(self):
        """Test message creation."""
        message = Message(
            type=MessageType.PROPOSE,
            sender="did:vireo:alice",
            recipient="did:vireo:bob",
            payload={"task": "analyze_data"}
        )
        
        assert message.type == MessageType.PROPOSE
        assert message.sender == "did:vireo:alice"
        assert message.recipient == "did:vireo:bob"
        assert message.payload["task"] == "analyze_data"
        assert message.id is not None
        assert message.timestamp is not None
        assert message.nonce is not None
        
    def test_message_serialization(self):
        """Test message serialization and deserialization."""
        original = Message(
            type=MessageType.PROPOSE,
            sender="alice",
            recipient="bob",
            payload={"data": "test"}
        )
        
        json_str = original.to_json()
        restored = Message.from_json(json_str)
        
        assert restored.type == original.type
        assert restored.sender == original.sender
        assert restored.recipient == original.recipient
        assert restored.payload == original.payload
        
    def test_message_binary_serialization(self):
        """Test binary serialization."""
        original = Message(
            type=MessageType.EXECUTE,
            sender="alice",
            recipient="bob",
            payload={"action": "compute"}
        )
        
        binary = original.to_bytes()
        restored = Message.from_bytes(binary)
        
        assert restored.type == original.type
        assert restored.sender == original.sender
        assert restored.recipient == original.recipient
        assert restored.payload == original.payload
        
    def test_message_requires_response(self):
        """Test message response requirements."""
        propose = Message(
            type=MessageType.PROPOSE,
            sender="alice",
            recipient="bob",
            payload={}
        )
        assert propose.requires_response() is True
        
        commit = Message(
            type=MessageType.COMMIT,
            sender="alice",
            recipient="bob",
            payload={}
        )
        assert commit.requires_response() is True
        
        done = Message(
            type=MessageType.DONE,
            sender="alice",
            recipient="bob",
            payload={}
        )
        assert done.requires_response() is False
        
        error = Message(
            type=MessageType.ERROR,
            sender="alice",
            recipient="bob",
            payload={}
        )
        assert error.requires_response() is False


class TestMessageValidator:
    """Message validator conformance tests."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = MessageValidator()
        assert validator is not None
        
    def test_validator_valid_message(self):
        """Test validating a valid message."""
        validator = MessageValidator()
        message = Message(
            type=MessageType.PROPOSE,
            sender="alice",
            recipient="bob",
            payload={"task": "test"}
        )
        
        result = validator.validate(message)
        assert result.is_valid is True
        
    def test_validator_invalid_type(self):
        """Test validating invalid message type."""
        validator = MessageValidator()
        message = Message(
            type="invalid_type",
            sender="alice",
            recipient="bob",
            payload={}
        )
        
        result = validator.validate(message)
        assert result.is_valid is False
        assert "invalid type" in result.errors[0].lower()
        
    def test_validator_missing_sender(self):
        """Test validating message with missing sender."""
        validator = MessageValidator()
        message = Message(
            type=MessageType.PROPOSE,
            sender="",
            recipient="bob",
            payload={}
        )
        
        result = validator.validate(message)
        assert result.is_valid is False
        
    def test_validator_missing_recipient(self):
        """Test validating message with missing recipient."""
        validator = MessageValidator()
        message = Message(
            type=MessageType.PROPOSE,
            sender="alice",
            recipient="",
            payload={}
        )
        
        result = validator.validate(message)
        assert result.is_valid is False
        
    def test_validator_large_payload(self):
        """Test validating message with large payload."""
        validator = MessageValidator(max_size=1024)
        large_payload = {"data": "x" * 2000}
        message = Message(
            type=MessageType.PROPOSE,
            sender="alice",
            recipient="bob",
            payload=large_payload
        )
        
        result = validator.validate(message)
        assert result.is_valid is False
        assert "size" in result.errors[0].lower()


class TestNonceManager:
    """Nonce manager conformance tests."""
    
    def test_nonce_generation(self):
        """Test nonce generation."""
        manager = NonceManager()
        nonce1 = manager.generate_nonce()
        nonce2 = manager.generate_nonce()
        
        assert nonce1 != nonce2
        assert len(nonce1) > 0
        assert len(nonce2) > 0
        
    def test_nonce_check(self):
        """Test nonce checking."""
        manager = NonceManager()
        
        nonce = manager.generate_nonce()
        assert manager.check_nonce(nonce) is True
        
        # Same nonce again should fail
        assert manager.check_nonce(nonce) is False
        
    def test_nonce_expiration(self):
        """Test nonce expiration."""
        manager = NonceManager(ttl_seconds=1)
        
        nonce = manager.generate_nonce()
        assert manager.check_nonce(nonce) is True
        
        time.sleep(1.5)
        assert manager.check_nonce(nonce) is False
        
    def test_nonce_cleanup(self):
        """Test nonce cleanup."""
        manager = NonceManager()
        
        # Add many nonces
        for _ in range(100):
            nonce = manager.generate_nonce()
            manager.check_nonce(nonce)
        
        # Cleanup should remove old nonces
        manager.cleanup()
        assert len(manager._nonces) < 100


class TestVersionManager:
    """Version manager conformance tests."""
    
    def test_version_compatibility(self):
        """Test version compatibility."""
        manager = VersionManager()
        
        assert manager.is_compatible("3.0.0", "3.0.0") is True
        assert manager.is_compatible("3.0.0", "3.1.0") is True
        assert manager.is_compatible("3.0.0", "2.9.0") is False
        assert manager.is_compatible("3.0.0", "4.0.0") is False
        
    def test_version_compare(self):
        """Test version comparison."""
        manager = VersionManager()
        
        assert manager.compare("3.0.0", "3.0.0") == 0
        assert manager.compare("3.1.0", "3.0.0") > 0
        assert manager.compare("2.9.0", "3.0.0") < 0
        
    def test_version_parse(self):
        """Test version parsing."""
        manager = VersionManager()
        
        major, minor, patch = manager.parse("3.0.0")
        assert major == 3
        assert minor == 0
        assert patch == 0
        
        major, minor, patch = manager.parse("3.1.2")
        assert major == 3
        assert minor == 1
        assert patch == 2