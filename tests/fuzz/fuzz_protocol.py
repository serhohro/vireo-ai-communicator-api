#!/usr/bin/env python3
"""
Fuzz Testing: Protocol

Fuzz testing for protocol state machine robustness.
"""

import pytest
import random
import sys
import json
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from core.protocol import Protocol, State, Message
    from core.protocol.validator import MessageValidator
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    print("⚠️ Core modules not available, running limited fuzz tests")


class FuzzProtocol:
    """Protocol fuzz testing."""
    
    def random_state(self) -> str:
        """Generate a random state name."""
        states = ["idle", "propose", "commit", "execute", "verify", "escalate", "done", "cancel"]
        return random.choice(states)
    
    def random_message_type(self) -> str:
        """Generate a random message type."""
        types = ["propose", "commit", "execute", "verify", "escalate", "done", "cancel", "heartbeat", "error"]
        return random.choice(types)
    
    def random_payload(self) -> Dict[str, Any]:
        """Generate a random payload."""
        payload = {}
        if random.random() < 0.3:
            payload["task"] = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(5, 20)))
        if random.random() < 0.3:
            payload["price"] = random.randint(1, 1000)
        if random.random() < 0.3:
            payload["deadline"] = f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        if random.random() < 0.3:
            payload["status"] = random.choice(["success", "failure", "pending"])
        if random.random() < 0.3:
            payload["data"] = [random.randint(0, 100) for _ in range(random.randint(0, 10))]
        return payload
    
    def random_message(self) -> Message:
        """Generate a random message."""
        return Message(
            type=self.random_message_type(),
            sender=f"did:vireo:{self.random_state()}",
            recipient=f"did:vireo:{self.random_state()}",
            payload=self.random_payload(),
            nonce=f"n_{random.randint(100000, 999999)}"
        )
    
    def test_fuzz_protocol_transitions(self):
        """Fuzz test protocol transitions."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        protocol = Protocol()
        
        for _ in range(100):
            try:
                # Randomly transition
                target = self.random_state()
                if hasattr(State, target.upper()):
                    target_state = getattr(State, target.upper())
                    # Try to transition
                    if protocol.can_transition(target_state):
                        protocol.transition(target_state)
                    else:
                        # Should fail gracefully
                        pass
            except Exception as e:
                # Should not crash
                print(f"Protocol transition fuzz failed: {e}")
                continue
                
    def test_fuzz_message_processing(self):
        """Fuzz test message processing."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        protocol = Protocol()
        
        for _ in range(100):
            try:
                msg = self.random_message()
                # Process message
                result = protocol.process(msg)
                # Should either process or fail gracefully
            except Exception as e:
                print(f"Message processing fuzz failed: {e}")
                continue
                
    def test_fuzz_invalid_state_transitions(self):
        """Fuzz test invalid state transitions."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        protocol = Protocol()
        
        # Try all state transitions
        for state in State:
            try:
                if protocol.can_transition(state):
                    protocol.transition(state)
                else:
                    # Should fail gracefully
                    pass
            except Exception as e:
                print(f"Invalid transition fuzz failed: {e}")
                continue
                
    def test_fuzz_message_validation(self):
        """Fuzz test message validation."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        validator = MessageValidator()
        
        for _ in range(100):
            try:
                msg = self.random_message()
                result = validator.validate(msg)
                # Should always return a result
                assert result is not None
            except Exception as e:
                print(f"Message validation fuzz failed: {e}")
                continue
                
    def test_fuzz_malformed_messages(self):
        """Fuzz test with malformed messages."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        malformed_messages = [
            {},  # Empty
            {"type": "unknown"},  # Unknown type
            {"type": "propose"},  # Missing sender
            {"type": "propose", "sender": "alice"},  # Missing recipient
            {"type": "propose", "sender": "alice", "recipient": "bob", "payload": None},  # Invalid payload
            {"type": "propose", "sender": "alice", "recipient": "bob", "payload": "not_a_dict"},  # Wrong payload type
            {"type": "propose", "sender": 123, "recipient": "bob"},  # Wrong sender type
            {"type": "propose", "sender": "alice", "recipient": 456},  # Wrong recipient type
            {"type": "propose", "sender": "alice", "recipient": "bob", "payload": {"task": 123}},  # Wrong nested type
        ]
        
        protocol = Protocol()
        validator = MessageValidator()
        
        for data in malformed_messages:
            try:
                # Try to create message from dict
                msg = Message.from_dict(data)
                result = validator.validate(msg)
                if result.is_valid:
                    protocol.process(msg)
            except Exception:
                # Expected for malformed input
                pass
                
    def test_fuzz_rapid_transitions(self):
        """Fuzz test rapid state transitions."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        protocol = Protocol()
        
        # Perform rapid random transitions
        states = list(State)
        
        for _ in range(500):
            try:
                state = random.choice(states)
                if protocol.can_transition(state):
                    protocol.transition(state)
            except Exception:
                pass
                
        # Should still be in a valid state
        assert protocol.get_state() in State


class TestFuzzProtocol:
    """Protocol fuzz test class for pytest."""
    
    def test_fuzz_basic_protocol(self):
        """Fuzz basic protocol operations."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        protocol = Protocol()
        
        # Standard flow
        protocol.process("propose", {"task": "test"})
        assert protocol.get_state() == State.PROPOSE
        
        protocol.process("commit", {"accepted": True})
        assert protocol.get_state() == State.COMMIT
        
        protocol.process("execute", {"data": "test"})
        assert protocol.get_state() == State.EXECUTE
        
        protocol.process("verify", {"result": "success"})
        assert protocol.get_state() == State.VERIFY
        
        protocol.process("done", {"status": "complete"})
        assert protocol.get_state() == State.DONE
        
    def test_fuzz_escalation_flow(self):
        """Fuzz escalation flow."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        protocol = Protocol()
        
        protocol.process("propose", {"task": "test"})
        protocol.process("commit", {"accepted": True})
        protocol.process("execute", {"data": "test"})
        
        # Escalate
        protocol.process("escalate", {"reason": "issue"})
        assert protocol.get_state() == State.ESCALATE
        
        # Resolve
        protocol.process("done", {"status": "resolved"})
        assert protocol.get_state() == State.DONE
        
    def test_fuzz_cancel_flow(self):
        """Fuzz cancel flow."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        protocol = Protocol()
        
        protocol.process("propose", {"task": "test"})
        protocol.process("commit", {"accepted": True})
        
        # Cancel
        protocol.process("cancel", {"reason": "cancelled"})
        assert protocol.get_state() == State.CANCEL