"""Vireo v3.1 crypto tests."""

import hashlib
import pytest

from core.crypto.blake2b import blake2b_256, did_hash
from core.crypto.ed25519 import generate_keypair, sign_vireo_message, verify_vireo_message


class TestBlake2b:
    def test_empty(self):
        assert len(blake2b_256(b"")) == 32

    def test_deterministic(self):
        assert blake2b_256(b"x") == blake2b_256(b"x")

    def test_rejects_str(self):
        with pytest.raises(TypeError):
            blake2b_256("x")

    def test_did_hash(self):
        assert len(did_hash("did:vireo:a")) == 32


class TestEd25519:
    def test_keypair(self):
        kp = generate_keypair()
        assert len(kp["private_key_hex"]) == 64
        assert len(kp["public_key_hex"]) == 64

    def test_sign_verify(self):
        kp = generate_keypair()
        sig = sign_vireo_message(kp["private_key_hex"], b"msg")
        valid, err = verify_vireo_message(kp["public_key_hex"], b"msg", sig)
        assert valid and err is None

    def test_wrong_key(self):
        kp1 = generate_keypair()
        kp2 = generate_keypair()
        sig = sign_vireo_message(kp1["private_key_hex"], b"msg")
        valid, _ = verify_vireo_message(kp2["public_key_hex"], b"msg", sig)
        assert not valid

    def test_tampered(self):
        kp = generate_keypair()
        sig = sign_vireo_message(kp["private_key_hex"], b"orig")
        valid, _ = verify_vireo_message(kp["public_key_hex"], b"tamp", sig)
        assert not valid
