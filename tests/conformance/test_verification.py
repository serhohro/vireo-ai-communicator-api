#!/usr/bin/env python3
"""
Conformance Tests: Verification

Tests for result verification and validation.
"""

import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocol.agents.verifier_agent import VerifierAgent, VerifierConfig
from core.crypto import ed25519, blake2b
from core.protocol import Message


class TestVerifierAgent:
    """Verifier agent conformance tests."""
    
    @pytest.fixture
    def verifier(self):
        """Create a verifier agent for testing."""
        config = VerifierConfig(
            name="TestVerifier",
            verification_threshold=0.7
        )
        return VerifierAgent(config)
    
    def test_verifier_initialization(self, verifier):
        """Test verifier initialization."""
        assert verifier is not None
        assert verifier.verifier_config.verification_threshold == 0.7
        assert len(verifier._verifications) == 0
        
    def test_verify_integrity(self, verifier):
        """Test integrity verification."""
        data = {"test": "data"}
        data_bytes = json.dumps(data, sort_keys=True).encode()
        expected = blake2b.blake2b(data_bytes).hex()
        
        record = {
            "type": "integrity",
            "data": data,
            "expected": expected
        }
        
        result = verifier._verify_integrity(record)
        assert result["verified"] is True
        assert result["score"] == 1.0
        
    def test_verify_integrity_fail(self, verifier):
        """Test integrity verification failure."""
        data = {"test": "data"}
        expected = "wrong_hash"
        
        record = {
            "type": "integrity",
            "data": data,
            "expected": expected
        }
        
        result = verifier._verify_integrity(record)
        assert result["verified"] is False
        assert result["score"] == 0.0
        
    def test_verify_signature(self, verifier):
        """Test signature verification."""
        key_pair = ed25519.Ed25519.generate()
        data = b"Test data"
        signature = ed25519.Ed25519.sign(data, key_pair.private_key)
        
        record = {
            "type": "signature",
            "data": data,
            "expected": {
                "signature": signature.hex(),
                "public_key": key_pair.public_key.hex()
            }
        }
        
        result = verifier._verify_signature(record)
        assert result["verified"] is True
        assert result["score"] == 1.0
        
    def test_verify_signature_fail(self, verifier):
        """Test signature verification failure."""
        key_pair = ed25519.Ed25519.generate()
        data = b"Test data"
        signature = ed25519.Ed25519.sign(b"Wrong data", key_pair.private_key)
        
        record = {
            "type": "signature",
            "data": data,
            "expected": {
                "signature": signature.hex(),
                "public_key": key_pair.public_key.hex()
            }
        }
        
        result = verifier._verify_signature(record)
        assert result["verified"] is False
        assert result["score"] == 0.0
        
    def test_verify_schema(self, verifier):
        """Test schema verification."""
        data = {"name": "test", "age": 30}
        schema = {"name": str, "age": int}
        
        record = {
            "type": "schema",
            "data": data,
            "expected": schema
        }
        
        result = verifier._verify_schema(record)
        assert result["verified"] is True
        assert result["score"] == 1.0
        
    def test_verify_schema_fail(self, verifier):
        """Test schema verification failure."""
        data = {"name": "test", "age": "30"}
        schema = {"name": str, "age": int}
        
        record = {
            "type": "schema",
            "data": data,
            "expected": schema
        }
        
        result = verifier._verify_schema(record)
        assert result["verified"] is False
        assert result["score"] < 1.0
        
    def test_combine_verifications(self, verifier):
        """Test combining verification results."""
        verifications = [
            {"result": {"verified": True, "score": 0.9}},
            {"result": {"verified": True, "score": 0.8}},
            {"result": {"verified": False, "score": 0.3}}
        ]
        
        result = verifier._combine_verifications(verifications)
        assert result["verified"] is True
        assert result["score"] == (0.9 + 0.8 + 0.3) / 3
        
    def test_combine_verifications_fail(self, verifier):
        """Test combining verification results with failure."""
        verifier.verifier_config.verification_threshold = 0.8
        
        verifications = [
            {"result": {"verified": True, "score": 0.9}},
            {"result": {"verified": False, "score": 0.1}}
        ]
        
        result = verifier._combine_verifications(verifications)
        assert result["verified"] is False
        
    def test_register_validation_rule(self, verifier):
        """Test registering a validation rule."""
        def custom_rule(data, params):
            return {
                "verified": data.get("valid", False),
                "score": 1.0 if data.get("valid", False) else 0.0,
                "details": {"custom": "check"}
            }
        
        verifier.register_validation_rule("custom", custom_rule)
        assert "custom" in verifier._validation_rules
        
    def test_verify_custom(self, verifier):
        """Test custom verification."""
        def custom_rule(data, params):
            return {
                "verified": data.get("valid", False),
                "score": 1.0 if data.get("valid", False) else 0.0,
                "details": {"custom": "check"}
            }
        
        verifier.register_validation_rule("custom", custom_rule)
        
        record = {
            "type": "custom",
            "data": {"valid": True},
            "expected": {"rule_name": "custom"}
        }
        
        result = verifier._verify_custom(record)
        assert result["verified"] is True
        
    def test_get_stats(self, verifier):
        """Test getting verifier statistics."""
        stats = verifier.get_stats()
        assert "total" in stats
        assert "verified" in stats
        assert "failed" in stats
        assert "success_rate" in stats
        assert stats["total"] == 0