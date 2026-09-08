# Vireo Wire Format Specification v3.0.0

## Overview

Vireo uses a **binary canonical format** for all protocol messages.

### Design Goals

- ✅ **Deterministic** — Same message → same bytes across all languages
- ✅ **Compact** — Minimal overhead
- ✅ **Fast** — Zero-copy parsing possible
- ✅ **Secure** — Ed25519 signatures over canonical bytes
- ✅ **Versioned** — Protocol version in header

---

## Message Structure
┌─────────────────────────────────────────────────────────────────┐
│ VIREO MESSAGE FORMAT v3.0.0 │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ HEADER (8 bytes) │ │
│ │ Magic: "VIRE" (4 bytes) │ │
│ │ Version: 0x30 (v3.0) (1 byte) │ │
│ │ Flags: 0x00-0xFF (1 byte) │ │
│ │ Reserved: 0x0000 (2 bytes) │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ BODY (variable) │ │
│ │ Sender: Length(1) + UTF-8 │ │
│ │ Recipient: Length(1) + UTF-8 │ │
│ │ Intent: 1 byte (0x01-0x08) │ │
│ │ Timestamp: 8 bytes (u64, ms since epoch) │ │
│ │ Nonce: 16 bytes │ │
│ │ Proposal ID: Length(1) + UTF-8 │ │
│ │ Payload Hash: 32 bytes (BLAKE2b) │ │
│ │ Signature: 64 bytes (Ed25519) │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────┘

text

---

## Field Specifications

### Header

| Field | Offset | Size | Type | Value |
|-------|--------|------|------|-------|
| Magic | 0 | 4 | bytes | `0x56 0x49 0x52 0x45` ("VIRE") |
| Version | 4 | 1 | u8 | `0x30` (v3.0) |
| Flags | 5 | 1 | u8 | Bit flags |
| Reserved | 6 | 2 | u16 | `0x0000` |

### Body

| Field | Type | Size | Description |
|-------|------|------|-------------|
| Sender | Length-prefixed | 1 + N | DID: `did:vireo:agent:{id}` |
| Recipient | Length-prefixed | 1 + N | DID: `did:vireo:agent:{id}` |
| Intent | u8 | 1 | See Intent table |
| Timestamp | u64 | 8 | Milliseconds since Unix epoch |
| Nonce | bytes | 16 | Random 128-bit nonce |
| Proposal ID | Length-prefixed | 1 + N | Unique proposal identifier |
| Payload Hash | bytes | 32 | BLAKE2b of canonical JSON payload |
| Signature | bytes | 64 | Ed25519 signature |

### Intent Codes

| Code | Intent |
|------|--------|
| 0x01 | PROPOSE |
| 0x02 | COMMIT |
| 0x03 | EXECUTE |
| 0x04 | VERIFY |
| 0x05 | DONE |
| 0x06 | ESCALATE |
| 0x07 | REJECT |
| 0x08 | TIMEOUT |

---

## Canonical Hash Algorithm

```python
from hashlib import blake2b
import struct

def canonical_hash(msg: Message) -> bytes:
    parts = [
        b'VIRE',                           # Magic
        bytes([msg.version]),              # Version
        bytes([msg.flags]),                # Flags
        b'\x00\x00',                       # Reserved
        bytes([len(msg.sender)]),          # Sender length
        msg.sender.encode('utf-8'),        # Sender
        bytes([len(msg.recipient)]),       # Recipient length
        msg.recipient.encode('utf-8'),     # Recipient
        bytes([msg.intent]),               # Intent
        struct.pack('>Q', msg.timestamp_ms),  # Timestamp
        msg.nonce,                         # Nonce
        bytes([len(msg.proposal_id)]),     # Proposal ID length
        msg.proposal_id.encode('utf-8'),   # Proposal ID
        msg.payload_hash,                  # Payload hash
    ]
    return blake2b(b''.join(parts), digest_size=32).digest()
Serialization Rules
Integers
All integers are big-endian (network byte order)

Strings
UTF-8 encoded

NFC normalized

Length-prefixed (1 byte, max 255 bytes)

Timestamps
Unix epoch in milliseconds

u64 integer (no floating point)

Time window: ±5 minutes for replay protection

Nonces
16 random bytes

MUST be unique per message

Test Vectors
All implementations MUST pass these test vectors:

Name	File	Description
PROPOSE	propose_v3_0.bin	Valid proposal
COMMIT	commit_v3_0.bin	Valid commit
EXECUTE	execute_v3_0.bin	Valid execute
VERIFY	verify_v3_0.bin	Valid verify
DONE	done_v3_0.bin	Valid done
ESCALATE	escalate_v3_0.bin	Valid escalate
Unicode	unicode_nfc.bin	NFC normalization
Negative Zero	float_negative_zero.bin	-0.0 handling
Big Integer	big_int.bin	>2^53 handling