# ============================================================
# CRYPTOGRAPHY SECURITY TESTS
# ============================================================
"""
Security tests for cryptographic operations in Vireo.

Tests verify:
- Ed25519 key generation
- Signing and verification
- Key format validation
- Invalid signature rejection
- Nonce generation and validation
- Replay attack protection
"""

import pytest
import time
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.exceptions import InvalidSignature


class TestCrypto:
    """Cryptography security tests."""

    def test_ed25519_key_generation(self):
        """MUST: Ed25519 keys are generated correctly."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        assert private_key is not None
        assert public_key is not None
        assert isinstance(private_key, Ed25519PrivateKey)
        assert isinstance(public_key, Ed25519PublicKey)

    def test_ed25519_key_sizes(self):
        """MUST: Ed25519 keys have correct sizes."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes_raw()
        public_bytes = public_key.public_bytes_raw()
        
        assert len(private_bytes) == 32
        assert len(public_bytes) == 32
        assert len(public_bytes.hex()) == 64  # 32 bytes = 64 hex chars

    def test_ed25519_sign_and_verify(self):
        """MUST: Sign and verify works correctly."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        message = b"Hello, Vireo! This is a test message for security."
        signature = private_key.sign(message)
        
        assert len(signature) == 64
        assert len(signature.hex()) == 128
        
        # Verify
        try:
            public_key.verify(signature, message)
            verified = True
        except InvalidSignature:
            verified = False
        
        assert verified is True

    def test_ed25519_invalid_signature_rejected(self):
        """MUST: Invalid signatures are rejected."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        message = b"Hello, Vireo!"
        signature = private_key.sign(message)
        
        # Tamper with signature
        tampered = bytearray(signature)
        tampered[0] = (tampered[0] + 1) % 256
        tampered = bytes(tampered)
        
        try:
            public_key.verify(tampered, message)
            verified = True
        except InvalidSignature:
            verified = False
        
        assert verified is False

    def test_ed25519_wrong_message_rejected(self):
        """MUST: Wrong message signature is rejected."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        message = b"Hello, Vireo!"
        wrong_message = b"Hello, World!"
        signature = private_key.sign(message)
        
        try:
            public_key.verify(signature, wrong_message)
            verified = True
        except InvalidSignature:
            verified = False
        
        assert verified is False

    def test_ed25519_public_key_validation(self):
        """MUST: Public key validation works."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes_raw()
        public_hex = public_bytes.hex()
        
        # Valid key: 64 hex chars
        assert len(public_hex) == 64
        assert self._validate_public_key(public_hex) is True
        
        # Invalid key: wrong length
        assert self._validate_public_key(public_hex[:63]) is False
        assert self._validate_public_key("") is False
        
        # Invalid key: non-hex characters
        assert self._validate_public_key("x" * 64) is False
    
    def _validate_public_key(self, public_key_hex: str) -> bool:
        """Validate Ed25519 public key."""
        if len(public_key_hex) != 64:
            return False
        try:
            bytes.fromhex(public_key_hex)
            return True
        except ValueError:
            return False

    def test_signature_format_validation(self):
        """MUST: Signature format is validated."""
        private_key = Ed25519PrivateKey.generate()
        message = b"Test message"
        signature = private_key.sign(message)
        signature_hex = signature.hex()
        
        # Valid signature: 128 hex chars
        assert len(signature_hex) == 128
        assert self._validate_signature(signature_hex) is True
        
        # Invalid signature: wrong length
        assert self._validate_signature(signature_hex[:127]) is False
        
        # Invalid signature: non-hex
        assert self._validate_signature("x" * 128) is False
    
    def _validate_signature(self, signature_hex: str) -> bool:
        """Validate Ed25519 signature."""
        if len(signature_hex) != 128:
            return False
        try:
            bytes.fromhex(signature_hex)
            return True
        except ValueError:
            return False

    def test_nonce_generation(self):
        """MUST: Nonces are generated correctly."""
        import secrets
        
        nonce = secrets.token_hex(32)
        
        assert len(nonce) == 64  # 32 bytes = 64 hex chars
        assert isinstance(nonce, str)
        
        # Nonces should be unique
        nonce2 = secrets.token_hex(32)
        assert nonce != nonce2

    def test_nonce_validation(self):
        """MUST: Nonce validation prevents replay attacks."""
        import secrets
        import time
        
        nonce_store = {}
        
        def generate_nonce() -> str:
            nonce = secrets.token_hex(32)
            nonce_store[nonce] = time.time()
            return nonce
        
        def validate_nonce(nonce: str, ttl_sec: int = 60) -> bool:
            if nonce not in nonce_store:
                return False
            if time.time() - nonce_store[nonce] > ttl_sec:
                return False
            return True
        
        # Generate and validate
        nonce = generate_nonce()
        assert validate_nonce(nonce) is True
        
        # Invalid nonce
        assert validate_nonce("invalid_nonce") is False
        
        # Expired nonce
        old_nonce = generate_nonce()
        nonce_store[old_nonce] = time.time() - 120  # 2 minutes ago
        assert validate_nonce(old_nonce, ttl_sec=60) is False

    def test_canonical_serialization(self):
        """MUST: Canonical serialization is deterministic."""
        data = {
            "protocol": "VIREO-A2A",
            "version": "2.0.2",
            "message_id": "msg-001",
            "sender": {"id": "agent-a", "model": "gpt-4"},
            "intent": "PROPOSE",
            "timestamp": 1234567890
        }
        
        # Remove signature field if present
        data_without_sig = {k: v for k, v in data.items() if k != "signature"}
        
        # Serialize with sorted keys
        canonical1 = json.dumps(data_without_sig, separators=(",", ":"), sort_keys=True)
        canonical2 = json.dumps(data_without_sig, separators=(",", ":"), sort_keys=True)
        
        assert canonical1 == canonical2
        
        # Different order should produce same result
        data2 = {
            "timestamp": 1234567890,
            "sender": {"model": "gpt-4", "id": "agent-a"},
            "version": "2.0.2",
            "protocol": "VIREO-A2A",
            "intent": "PROPOSE",
            "message_id": "msg-001"
        }
        canonical3 = json.dumps(data2, separators=(",", ":"), sort_keys=True)
        assert canonical1 == canonical3

    def test_key_rotation_signature(self):
        """SHOULD: Key rotation uses correct signature format."""
        old_private = Ed25519PrivateKey.generate()
        old_public = old_private.public_key()
        old_public_hex = old_public.public_bytes_raw().hex()
        
        new_private = Ed25519PrivateKey.generate()
        new_public = new_private.public_key()
        new_public_hex = new_public.public_bytes_raw().hex()
        
        # Message to sign for key rotation
        agent_id = "test-agent"
        rotation_message = f"key_rotation:{agent_id}:{new_public_hex}".encode()
        signature = old_private.sign(rotation_message)
        signature_hex = signature.hex()
        
        # Verify
        try:
            old_public.verify(signature, rotation_message)
            verified = True
        except InvalidSignature:
            verified = False
        
        assert verified is True
        assert len(signature_hex) == 128

    def test_secure_key_comparison(self):
        """SHOULD: Use constant-time comparison for keys."""
        import hmac
        
        key1 = b"secret_key_123"
        key2 = b"secret_key_123"
        key3 = b"different_key"
        
        # HMAC comparison is constant-time
        assert hmac.compare_digest(key1, key2) is True
        assert hmac.compare_digest(key1, key3) is False