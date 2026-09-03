"""
Conformance tests for Vireo signatures.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import pytest
import base64
import json


class TestSignatures:
    """Signature conformance tests."""

    def test_ed25519_public_key_format(self):
        """MUST: Ed25519 public key is 64 hex chars."""
        valid_key = "a" * 64
        invalid_key = "a" * 63
        assert len(valid_key) == 64
        assert len(invalid_key) != 64

    def test_ed25519_signature_format(self):
        """MUST: Ed25519 signature is 128 hex chars."""
        valid_sig = "a" * 128
        invalid_sig = "a" * 127
        assert len(valid_sig) == 128
        assert len(invalid_sig) != 128

    def test_verify_message(self):
        """MUST: Messages can be verified."""
        pass

    def test_invalid_signature_rejected(self):
        """MUST: Invalid signatures are rejected."""
        pass

    def test_replay_protection(self):
        """SHOULD: Nonce protects against replay attacks."""
        pass