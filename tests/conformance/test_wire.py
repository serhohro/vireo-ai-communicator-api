"""Vireo v3.1 wire format tests."""

import struct
import pytest

from core.crypto.canonical import (
    jcs_serialize, canonical_wire_bytes, parse_wire_bytes,
    WIRE_MAGIC, WIRE_VERSION, HEADER_SIZE,
)
from core.crypto.blake2b import did_hash


def _env():
    return {
        "intent": "PROPOSE",
        "timestamp_ms": 1773168000000,
        "nonce": bytes(16),
        "sender_did_hash": did_hash("did:vireo:alice"),
        "recipient_did_hash": did_hash("did:vireo:bob"),
        "payload": {"task": "test"},
    }


class TestJCS:
    def test_sorted(self):
        assert jcs_serialize({"b": 1, "a": 2}) == b'{"a":2,"b":1}'

    def test_no_whitespace(self):
        assert b" " not in jcs_serialize({"a": 1})

    def test_reject_nan(self):
        with pytest.raises(ValueError):
            jcs_serialize({"x": float("nan")})

    def test_reject_scalar(self):
        with pytest.raises(TypeError):
            jcs_serialize("scalar")


class TestWire:
    def test_header_size(self):
        assert len(canonical_wire_bytes(_env())) >= HEADER_SIZE + 4

    def test_magic(self):
        assert canonical_wire_bytes(_env())[:4] == WIRE_MAGIC

    def test_version(self):
        wire = canonical_wire_bytes(_env())
        assert struct.unpack(">H", wire[4:6])[0] == WIRE_VERSION

    def test_roundtrip(self):
        env = _env()
        parsed = parse_wire_bytes(canonical_wire_bytes(env))
        assert parsed["intent"] == env["intent"]
        assert parsed["payload"] == env["payload"]

    def test_bad_magic(self):
        wire = b"XXXX" + canonical_wire_bytes(_env())[4:]
        with pytest.raises(ValueError, match="Bad magic"):
            parse_wire_bytes(wire)

    def test_short(self):
        with pytest.raises(ValueError):
            parse_wire_bytes(b"VIRE")

    def test_missing_field(self):
        env = _env()
        del env["intent"]
        with pytest.raises(ValueError, match="Missing"):
            canonical_wire_bytes(env)

    def test_bad_nonce(self):
        env = _env()
        env["nonce"] = b"short"
        with pytest.raises(ValueError, match="nonce"):
            canonical_wire_bytes(env)
