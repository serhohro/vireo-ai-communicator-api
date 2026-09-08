#!/usr/bin/env python3
"""
Conformance Tests: Signatures

Tests for cryptographic signature functionality.
"""

import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.crypto import ed25519, blake2b
from core.identity import KeyManager, DID
from core.protocol import Message
from core.wire_format import WireFormat


class TestEd25519:
    """Ed25519 signature conformance tests."""
    
    def test_key_generation(self):
        """Test Ed25519 key generation."""
        key_pair = ed25519.Ed25519.generate()
        
        assert key_pair is not None
        assert len(key_pair.private_key) == 32
        assert len(key_pair.public_key) == 32
        
    def test_signing(self):
        """Test Ed25519 signing."""
        key_pair = ed25519.Ed25519.generate()
        data = b"Hello, Vireo!"
        
        signature = ed25519.Ed25519.sign(data, key_pair.private_key)
        assert len(signature) == 64
        
    def test_verification(self):
        """Test Ed25519 verification."""
        key_pair = ed25519.Ed25519.generate()
        data = b"Hello, Vireo!"
        
        signature = ed25519.Ed25519.sign(data, key_pair.private_key)
        assert ed25519.Ed25519.verify(data, signature, key_pair.public_key) is True
        
        # Wrong data
        wrong_data = b"Wrong data!"
        assert ed25519.Ed25519.verify(wrong_data, signature, key_pair.public_key) is False
        
        # Wrong signature
        wrong_sig = b"x" * 64
        assert ed25519.Ed25519.verify(data, wrong_sig, key_pair.public_key) is False
        
    def test_sign_verify_roundtrip(self):
        """Test complete sign/verify roundtrip."""
        key_pair = ed25519.Ed25519.generate()
        
        test_data = [
            b"Simple string",
            b"Complex data with \x00\x01\x02",
            b"Very long data " * 100,
            "Unicode text: 🚀🌿💬".encode(),
            b""
        ]
        
        for data in test_data:
            signature = ed25519.Ed25519.sign(data, key_pair.private_key)
            assert ed25519.Ed25519.verify(data, signature, key_pair.public_key) is True
            
    def test_different_keys(self):
        """Test that different keys produce different signatures."""
        key_pair1 = ed25519.Ed25519.generate()
        key_pair2 = ed25519.Ed25519.generate()
        data = b"Test data"
        
        sig1 = ed25519.Ed25519.sign(data, key_pair1.private_key)
        sig2 = ed25519.Ed25519.sign(data, key_pair2.private_key)
        
        assert sig1 != sig2
        
        # Verify cross-key
        assert ed25519.Ed25519.verify(data, sig1, key_pair1.public_key) is True
        assert ed25519.Ed25519.verify(data, sig1, key_pair2.public_key) is False


class TestBLAKE2b:
    """BLAKE2b hash conformance tests."""
    
    def test_hash_generation(self):
        """Test BLAKE2b hash generation."""
        data = b"Hello, Vireo!"
        hash_bytes = blake2b.blake2b(data)
        
        assert len(hash_bytes) == 32
        assert isinstance(hash_bytes, bytes)
        
    def test_hash_deterministic(self):
        """Test that hash is deterministic."""
        data = b"Test data"
        
        hash1 = blake2b.blake2b(data)
        hash2 = blake2b.blake2b(data)
        
        assert hash1 == hash2
        
    def test_hash_different_data(self):
        """Test that different data produces different hashes."""
        data1 = b"Data 1"
        data2 = b"Data 2"
        
        hash1 = blake2b.blake2b(data1)
        hash2 = blake2b.blake2b(data2)
        
        assert hash1 != hash2
        
    def test_hash_digest_sizes(self):
        """Test different digest sizes."""
        data = b"Test data"
        
        hash32 = blake2b.blake2b(data, digest_size=32)
        hash64 = blake2b.blake2b(data, digest_size=64)
        
        assert len(hash32) == 32
        assert len(hash64) == 64
        assert hash32 != hash64
        
    def test_hash_keyed(self):
        """Test keyed BLAKE2b."""
        data = b"Test data"
        key = b"secret_key"
        
        hash1 = blake2b.blake2b(data, key=key)
        hash2 = blake2b.blake2b(data, key=key)
        
        assert hash1 == hash2
        
        # Different key
        key2 = b"different_key"
        hash3 = blake2b.blake2b(data, key=key2)
        
        assert hash1 != hash3


class TestMessageSigning:
    """Message signing conformance tests."""
    
    def test_message_signing(self):
        """Test signing a message."""
        key_pair = ed25519.Ed25519.generate()
        
        message = Message(
            type="propose",
            sender="alice",
            recipient="bob",
            payload={"task": "test"}
        )
        
        # Sign message
        signature = ed25519.Ed25519.sign(
            message.to_bytes(),
            key_pair.private_key
        )
        message.signature = signature
        
        assert message.signature is not None
        assert len(message.signature) == 64
        
    def test_message_verification(self):
        """Test verifying a signed message."""
        key_pair = ed25519.Ed25519.generate()
        
        message = Message(
            type="propose",
            sender="alice",
            recipient="bob",
            payload={"task": "test"}
        )
        
        # Sign
        signature = ed25519.Ed25519.sign(
            message.to_bytes_without_signature(),
            key_pair.private_key
        )
        message.signature = signature
        
        # Verify
        is_valid = ed25519.Ed25519.verify(
            message.to_bytes_without_signature(),
            message.signature,
            key_pair.public_key
        )
        assert is_valid is True
        
    def test_message_tampering_detection(self):
        """Test detection of message tampering."""
        key_pair = ed25519.Ed25519.generate()
        
        message = Message(
            type="propose",
            sender="alice",
            recipient="bob",
            payload={"task": "test"}
        )
        
        # Sign
        signature = ed25519.Ed25519.sign(
            message.to_bytes_without_signature(),
            key_pair.private_key
        )
        message.signature = signature
        
        # Tamper with message
        message.payload = {"task": "tampered"}
        
        # Verify should fail
        is_valid = ed25519.Ed25519.verify(
            message.to_bytes_without_signature(),
            message.signature,
            key_pair.public_key
        )
        assert is_valid is False


class TestKeyManager:
    """Key manager conformance tests."""
    
    def test_manager_initialization(self):
        """Test key manager initialization."""
        manager = KeyManager()
        assert manager is not None
        
    def test_key_generation(self):
        """Test key generation via manager."""
        manager = KeyManager()
        
        did = DID.generate()
        key_pair = manager.generate_key(did)
        
        assert key_pair is not None
        assert len(key_pair.private_key) == 32
        assert len(key_pair.public_key) == 32
        
    def test_key_storage(self):
        """Test key storage and retrieval."""
        manager = KeyManager()
        
        did = DID.generate()
        key_pair = manager.generate_key(did)
        
        # Store
        manager.store_key(did, key_pair)
        
        # Retrieve
        retrieved = manager.get_key(did)
        assert retrieved is not None
        assert retrieved.private_key == key_pair.private_key
        assert retrieved.public_key == key_pair.public_key
        
    def test_key_signing(self):
        """Test signing via key manager."""
        manager = KeyManager()
        
        did = DID.generate()
        key_pair = manager.generate_key(did)
        manager.store_key(did, key_pair)
        
        data = b"Test data"
        signature = manager.sign(did, data)
        
        assert len(signature) == 64
        
    def test_key_verification(self):
        """Test verification via key manager."""
        manager = KeyManager()
        
        did = DID.generate()
        key_pair = manager.generate_key(did)
        manager.store_key(did, key_pair)
        
        data = b"Test data"
        signature = manager.sign(did, data)
        
        assert manager.verify(did, data, signature) is True
        
        # Wrong data
        assert manager.verify(did, b"Wrong data", signature) is False