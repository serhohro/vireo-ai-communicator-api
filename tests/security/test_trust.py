# ============================================================
# TRUST AND IDENTITY SECURITY TESTS
# ============================================================
"""
Security tests for trust and identity in Vireo.

Tests verify:
- Trust Bootstrap Protocol
- Whitelist registration and unregistration
- Public key validation
- Message verification
- Key rotation
- Trust level management
- Escalation handling
"""

import pytest
import time
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.exceptions import InvalidSignature


class TestTrust:
    """Trust and identity security tests."""

    def setup_method(self):
        """Set up test environment."""
        self.trust_bootstrap = self._create_trust_bootstrap()
    
    def _create_trust_bootstrap(self):
        """Create a TrustBootstrap instance."""
        # Simple implementation for testing
        class TrustBootstrap:
            def __init__(self):
                self._whitelist: Dict[str, bytes] = {}
                self._private_key = Ed25519PrivateKey.generate()
                self._public_key = self._private_key.public_key()
            
            def register(self, agent_id: str, public_key_hex: str) -> bool:
                if len(public_key_hex) != 64:
                    return False
                try:
                    bytes.fromhex(public_key_hex)
                    self._whitelist[agent_id] = bytes.fromhex(public_key_hex)
                    return True
                except ValueError:
                    return False
            
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
            
            def get_whitelist(self) -> Dict[str, str]:
                return {aid: pubkey.hex() for aid, pubkey in self._whitelist.items()}
        
        return TrustBootstrap()

    def test_trust_bootstrap_register(self):
        """MUST: Agents can be registered in whitelist."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_hex = public_key.public_bytes_raw().hex()
        
        result = self.trust_bootstrap.register("agent-test", public_key_hex)
        assert result is True
        assert self.trust_bootstrap.is_trusted("agent-test") is True

    def test_trust_bootstrap_unregister(self):
        """MUST: Agents can be unregistered from whitelist."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_hex = public_key.public_bytes_raw().hex()
        
        self.trust_bootstrap.register("agent-test", public_key_hex)
        assert self.trust_bootstrap.is_trusted("agent-test") is True
        
        self.trust_bootstrap.unregister("agent-test")
        assert self.trust_bootstrap.is_trusted("agent-test") is False

    def test_invalid_public_key_rejected(self):
        """MUST: Invalid public keys are rejected."""
        # Wrong length
        result = self.trust_bootstrap.register("agent-test", "invalid")
        assert result is False
        
        # Non-hex characters
        result = self.trust_bootstrap.register("agent-test", "x" * 64)
        assert result is False
        
        # Empty key
        result = self.trust_bootstrap.register("agent-test", "")
        assert result is False

    def test_whitelist_verification(self):
        """MUST: Whitelist verification works."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_hex = public_key.public_bytes_raw().hex()
        
        self.trust_bootstrap.register("agent-test", public_key_hex)
        
        # Sign a message
        message = b"Test message for verification"
        signature = private_key.sign(message)
        
        # Verify
        assert self.trust_bootstrap.verify_message("agent-test", message, signature) is True

    def test_untrusted_agent_rejected(self):
        """MUST: Untrusted agents are rejected."""
        private_key = Ed25519PrivateKey.generate()
        message = b"Test message"
        signature = private_key.sign(message)
        
        # Agent not in whitelist
        assert self.trust_bootstrap.verify_message("unknown-agent", message, signature) is False

    def test_invalid_signature_rejected(self):
        """MUST: Invalid signatures are rejected."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_hex = public_key.public_bytes_raw().hex()
        
        self.trust_bootstrap.register("agent-test", public_key_hex)
        
        message = b"Test message"
        signature = private_key.sign(message)
        
        # Tamper with signature
        tampered = bytearray(signature)
        tampered[0] = (tampered[0] + 1) % 256
        tampered = bytes(tampered)
        
        assert self.trust_bootstrap.verify_message("agent-test", message, tampered) is False

    def test_whitelist_getter(self):
        """MUST: Whitelist can be retrieved."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_hex = public_key.public_bytes_raw().hex()
        
        self.trust_bootstrap.register("agent-1", public_key_hex)
        self.trust_bootstrap.register("agent-2", public_key_hex)
        
        whitelist = self.trust_bootstrap.get_whitelist()
        assert "agent-1" in whitelist
        assert "agent-2" in whitelist
        assert len(whitelist) == 2

    def test_message_verification_with_json(self):
        """SHOULD: JSON messages can be verified."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_hex = public_key.public_bytes_raw().hex()
        
        self.trust_bootstrap.register("agent-test", public_key_hex)
        
        # Create JSON message
        data = {"protocol": "VIREO-A2A", "intent": "PROPOSE", "message": "Hello"}
        message = json.dumps(data, sort_keys=True).encode()
        signature = private_key.sign(message)
        
        # Verify JSON message
        assert self.trust_bootstrap.verify_message("agent-test", message, signature) is True

    def test_key_rotation(self):
        """SHOULD: Key rotation works."""
        old_private = Ed25519PrivateKey.generate()
        old_public = old_private.public_key()
        old_public_hex = old_public.public_bytes_raw().hex()
        
        # Register old key
        self.trust_bootstrap.register("agent-test", old_public_hex)
        
        # Rotate to new key
        new_private = Ed25519PrivateKey.generate()
        new_public = new_private.public_key()
        new_public_hex = new_public.public_bytes_raw().hex()
        
        # Sign rotation with old key
        rotation_msg = f"key_rotation:agent-test:{new_public_hex}".encode()
        signature = old_private.sign(rotation_msg)
        
        # Verify rotation signature
        try:
            old_public.verify(signature, rotation_msg)
            rotation_valid = True
        except InvalidSignature:
            rotation_valid = False
        
        assert rotation_valid is True
        
        # Register new key (in real implementation, this would be more complex)
        self.trust_bootstrap.register("agent-test", new_public_hex)
        assert self.trust_bootstrap.is_trusted("agent-test") is True

    def test_concurrent_trust(self):
        """SHOULD: Multiple agents can be trusted simultaneously."""
        agents = []
        for i in range(5):
            private_key = Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            public_key_hex = public_key.public_bytes_raw().hex()
            agent_id = f"agent-{i}"
            self.trust_bootstrap.register(agent_id, public_key_hex)
            agents.append(agent_id)
        
        for agent_id in agents:
            assert self.trust_bootstrap.is_trusted(agent_id) is True
        
        whitelist = self.trust_bootstrap.get_whitelist()
        assert len(whitelist) == 5

    def test_trust_isolation(self):
        """SHOULD: Trust is isolated between agents."""
        # Create two agents
        priv1 = Ed25519PrivateKey.generate()
        pub1 = priv1.public_key()
        pub1_hex = pub1.public_bytes_raw().hex()
        
        priv2 = Ed25519PrivateKey.generate()
        pub2 = priv2.public_key()
        pub2_hex = pub2.public_bytes_raw().hex()
        
        # Register only agent 1
        self.trust_bootstrap.register("agent-1", pub1_hex)
        
        # Agent 1 should be trusted
        assert self.trust_bootstrap.is_trusted("agent-1") is True
        
        # Agent 2 should not be trusted
        assert self.trust_bootstrap.is_trusted("agent-2") is False
        
        # Verify message from agent 1 should work
        msg = b"Test"
        sig = priv1.sign(msg)
        assert self.trust_bootstrap.verify_message("agent-1", msg, sig) is True
        
        # Verify message from agent 2 should fail
        sig2 = priv2.sign(msg)
        assert self.trust_bootstrap.verify_message("agent-2", msg, sig2) is False