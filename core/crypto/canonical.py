"""
RFC 8785 JSON Canonicalization Scheme (JCS) + Vireo wire encoding.

Wire layout:
┌──────────────────────────────────────────────┐
│ Header (96 bytes)                            │
│  Magic           4B   b"VIRE"                │
│  Version         2B   uint16 BE = 0x0301     │
│  Intent          2B   uint16 BE              │
│  Timestamp       8B   uint64 BE (ms)         │
│  Nonce          16B   random bytes           │
│  Sender hash    32B   BLAKE2b-256            │
│  Recipient hash 32B   BLAKE2b-256            │
├──────────────────────────────────────────────┤
│ Payload Length   4B   uint32 BE              │
│ Payload          var  RFC 8785 JCS JSON      │
└──────────────────────────────────────────────┘
"""

import json
import struct
import unicodedata
from typing import Any

WIRE_MAGIC = b"VIRE"
WIRE_VERSION = 0x0301   # v3.1
HEADER_SIZE = 4 + 2 + 2 + 8 + 16 + 32 + 32   # 96 bytes

INTENT = {
    "DISCOVER":  1,
    "PROPOSE":   2,
    "NEGOTIATE": 3,
    "COMMIT":    4,
    "REJECT":    5,
    "EXECUTE":   6,
    "VERIFY":    7,
    "DONE":      8,
    "ESCALATED": 9,
    "CANCELLED": 10,
    "FAILED":    11,
    "TIMEOUT":   12,
}
REVERSE_INTENT = {v: k for k, v in INTENT.items()}


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _normalize(v: Any) -> Any:
    if isinstance(v, str):
        return _nfc(v)
    if isinstance(v, dict):
        return {_nfc(k): _normalize(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_normalize(x) for x in v]
    return v


def jcs_serialize(obj: Any) -> bytes:
    """
    RFC 8785 JSON Canonicalization Scheme.

    Rules:
    - Keys sorted lexicographically by Unicode code point
    - No whitespace outside strings
    - UTF-8 NFC normalized strings
    - No NaN/Infinity
    """
    if not isinstance(obj, (dict, list)):
        raise TypeError("JCS top level must be object or array")
    normalized = _normalize(obj)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_wire_bytes(envelope: dict) -> bytes:
    """
    Build the canonical Vireo wire bytes.

    Required envelope keys:
        intent: str
        timestamp_ms: int
        nonce: bytes (16)
        sender_did_hash: bytes (32)
        recipient_did_hash: bytes (32)
        payload: dict
    """
    for f in ("intent", "timestamp_ms", "nonce",
              "sender_did_hash", "recipient_did_hash", "payload"):
        if f not in envelope:
            raise ValueError(f"Missing envelope field: {f}")

    intent_str = envelope["intent"]
    if intent_str not in INTENT:
        raise ValueError(f"Unknown intent: {intent_str}")

    nonce = envelope["nonce"]
    if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != 16:
        raise ValueError("nonce must be 16 bytes")

    s_hash = envelope["sender_did_hash"]
    r_hash = envelope["recipient_did_hash"]
    if len(s_hash) != 32 or len(r_hash) != 32:
        raise ValueError("DID hashes must be 32 bytes")

    header = b"".join([
        WIRE_MAGIC,
        struct.pack(">H", WIRE_VERSION),
        struct.pack(">H", INTENT[intent_str]),
        struct.pack(">Q", envelope["timestamp_ms"]),
        bytes(nonce),
        bytes(s_hash),
        bytes(r_hash),
    ])
    assert len(header) == HEADER_SIZE

    payload_bytes = jcs_serialize(envelope["payload"])
    payload_section = struct.pack(">I", len(payload_bytes)) + payload_bytes

    return header + payload_section


def parse_wire_bytes(data: bytes) -> dict:
    """
    Parse canonical wire bytes into an envelope dict.
    Does NOT verify signature.
    """
    if len(data) < HEADER_SIZE + 4:
        raise ValueError(f"Wire message too short: {len(data)} bytes")

    offset = 0
    magic = data[offset:offset+4]; offset += 4
    if magic != WIRE_MAGIC:
        raise ValueError(f"Bad magic: {magic!r}")

    version = struct.unpack(">H", data[offset:offset+2])[0]; offset += 2
    if version != WIRE_VERSION:
        raise ValueError(f"Unsupported version: {version:#06x}")

    intent_id = struct.unpack(">H", data[offset:offset+2])[0]; offset += 2
    if intent_id not in REVERSE_INTENT:
        raise ValueError(f"Unknown intent id: {intent_id}")

    timestamp_ms = struct.unpack(">Q", data[offset:offset+8])[0]; offset += 8
    nonce = data[offset:offset+16]; offset += 16
    s_hash = data[offset:offset+32]; offset += 32
    r_hash = data[offset:offset+32]; offset += 32

    payload_len = struct.unpack(">I", data[offset:offset+4])[0]; offset += 4
    payload_bytes = data[offset:offset+payload_len]
    if len(payload_bytes) != payload_len:
        raise ValueError("Truncated payload")

    payload = json.loads(payload_bytes.decode("utf-8"))

    return {
        "intent": REVERSE_INTENT[intent_id],
        "timestamp_ms": timestamp_ms,
        "nonce": nonce,
        "sender_did_hash": s_hash,
        "recipient_did_hash": r_hash,
        "payload": payload,
    }