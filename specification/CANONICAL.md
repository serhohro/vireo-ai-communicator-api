# Vireo Canonical Format Specification v3.0.0

## Overview

The canonical format ensures deterministic serialization of Vireo messages across all implementations. Any two valid implementations must produce identical byte sequences for the same logical message.

## Design Goals

- ✅ **Deterministic** — Same message → same bytes
- ✅ **Compact** — Minimal byte overhead
- ✅ **Fast** — Zero-copy parsing possible
- ✅ **Secure** — Used for cryptographic hashing
- ✅ **Language-Neutral** — Works in Python, Rust, TypeScript, Go, Java, etc.

## Serialization Rules

### Integers

All integers are big-endian (network byte order).

| Type | Size | Range |
|------|------|-------|
| u8 | 1 byte | 0-255 |
| u16 | 2 bytes | 0-65,535 |
| u32 | 4 bytes | 0-4,294,967,295 |
| u64 | 8 bytes | 0-18,446,744,073,709,551,615 |

### Strings

- UTF-8 encoded
- NFC normalized (Unicode Normalization Form C)
- Length-prefixed (1 byte, max 255 bytes)

**Example:**
"Hello" → 05 48 65 6c 6c 6f
"Café" → 04 43 61 66 c3 a9 (NFC normalized)

text

### Maps (Dictionaries)

- Keys are sorted lexicographically (by UTF-8 bytes)
- Strings are UTF-8, NFC normalized
- No duplicate keys allowed
- Values are encoded recursively
- Empty maps are serialized as `00`

**Example:**
```json
{"a": 1, "b": 2}
→ Sorted keys: a, b
→ Serialized: a then b

Arrays
Elements are serialized in order

No length prefix (size is derived from context)

Homogeneous types

Empty arrays are serialized as 00

Example:

json
[1, 2, 3]
→ Serialized: 1 then 2 then 3

Floats
IEEE 754 double precision (64-bit)

Big-endian

Negative zero (-0.0) normalized to +0.0

NaN normalized to a canonical value (0x7FF8000000000000)

Infinities preserved (0x7FF0000000000000 for +∞, 0xFFF0000000000000 for -∞)

Normalization Examples:

Input	Normalized
-0.0	0.0
NaN	0x7FF8000000000000
+∞	0x7FF0000000000000
-∞	0xFFF0000000000000
Big Integers
Variable-length encoding

Sign bit (0 = positive, 1 = negative)

Length prefix (1 byte) followed by bytes

Zero is represented as 00

Encoding:

Value	Bytes
0	00
1	01 01
-1	81 01
256	02 01 00
Timestamps
Unix epoch in milliseconds

u64 integer (no floating point)

UTC timezone

Booleans
true → 01

false → 00

Null / Empty
null → 00

Empty strings are not allowed (use null instead)

Message Canonicalization
Header
text
┌────────┬─────────┬─────────┬──────────┐
│ Magic  │ Version │  Flags  │ Reserved │
│ 4 bytes│ 1 byte  │ 1 byte  │ 2 bytes  │
└────────┴─────────┴─────────┴──────────┘
Body
text
┌──────────┬────────────┬──────────┬────────────┬──────────┐
│  Sender  │ Recipient  │  Intent  │ Timestamp  │  Nonce   │
│ len+UTF8 │ len+UTF8   │ 1 byte   │ 8 bytes    │ 16 bytes │
├──────────┼────────────┼──────────┼────────────┼──────────┤
│ProposalID│PayloadHash │ Signature│            │          │
│ len+UTF8 │ 32 bytes   │ 64 bytes │            │          │
└──────────┴────────────┴──────────┴────────────┴──────────┘
Canonical Hash Algorithm
python
from hashlib import blake2b
import struct

def canonical_hash(message):
    parts = [
        b'VIRE',                       # Magic
        bytes([message.version]),       # Version
        bytes([message.flags]),         # Flags
        b'\x00\x00',                   # Reserved
        bytes([len(message.sender)]),   # Sender length
        message.sender.encode('utf-8'), # Sender
        bytes([len(message.recipient)]),# Recipient length
        message.recipient.encode('utf-8'), # Recipient
        bytes([message.intent]),        # Intent
        struct.pack('>Q', message.timestamp_ms), # Timestamp
        message.nonce,                 # Nonce
        bytes([len(message.proposal_id)]), # Proposal ID length
        message.proposal_id.encode('utf-8'), # Proposal ID
        message.payload_hash,          # Payload hash
    ]
    return blake2b(b''.join(parts), digest_size=32).digest()
Cross-Language Examples
Python
python
from core.protocol.message import Message, Intent

msg = Message.create(
    sender="did:vireo:agent:alice",
    recipient="did:vireo:agent:bob",
    intent=Intent.PROPOSE,
    proposal_id="prop_001",
    payload={"hello": "world"}
)
data = msg.serialize()
# data = b'VIRE0\x00\x00\x00\x1ddid:vireo:agent:alice\x1bdid:vireo:agent:bob\x01...'
Rust
rust
use vireo::{Message, Intent};
use serde_json::json;

let mut msg = Message::new(
    "did:vireo:agent:alice".to_string(),
    "did:vireo:agent:bob".to_string(),
    Intent::Propose,
    "prop_001".to_string(),
    json!({"hello": "world"})
);
let data = msg.serialize();
// data = b'VIRE0\x00\x00\x00\x1ddid:vireo:agent:alice\x1bdid:vireo:agent:bob\x01...'
TypeScript
typescript
import { Message, Intent } from 'vireo';

const msg = Message.create(
    "did:vireo:agent:alice",
    "did:vireo:agent:bob",
    Intent.PROPOSE,
    "prop_001",
    { hello: "world" }
);
const data = msg.serialize();
// data = Buffer.from('VIRE0...')
Go
go
import "github.com/vireo-ai/vireo"

msg := NewMessage(
    "did:vireo:agent:alice",
    "did:vireo:agent:bob",
    Propose,
    "prop_001",
    map[string]interface{}{"hello": "world"},
)
data := msg.Serialize()
Java
java
import com.vireo.*;

Message msg = new Message(
    "did:vireo:agent:alice",
    "did:vireo:agent:bob",
    Intent.PROPOSE,
    "prop_001",
    Map.of("hello", "world")
);
byte[] data = msg.serialize();
All five implementations produce identical bytes.

Canonical JSON
For payloads, JSON is serialized canonically:

Rules for Canonical JSON
Sort keys lexicographically

No extra whitespace — compact format

UTF-8 without BOM

Escape only required characters (", \, control chars)

No trailing commas

No comments

Example
Input:

json
{
    "b": 2,
    "a": 1,
    "c": "hello"
}
Canonical Output:

text
{"a":1,"b":2,"c":"hello"}
Implementation
python
import json

def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':')
    )
Test Vectors
Message: PROPOSE
text
Byte sequence: 56 49 52 45 30 00 00 00 1d 64 69 64 3a 76 69 72 ...
Message: COMMIT
text
Byte sequence: 56 49 52 45 30 00 00 00 1d 64 69 64 3a 76 69 72 ...
Edge Cases
Case	Description	Test File
Unicode	NFC normalization	unicode_nfc.bin
Negative Zero	-0.0 → 0.0	float_negative_zero.bin
Big Integer	>2^53 handling	big_int.bin
Duplicate Keys	Map with duplicate keys	duplicate_keys.bin
Malformed	Invalid message format	malformed.bin
Empty Map	Map with no entries	empty_map.bin
Empty Array	Array with no elements	empty_array.bin
Null Values	Null field handling	null_values.bin
Implementation Requirements
Any Vireo-compatible implementation MUST:

Produce identical bytes for the same logical message

Use BLAKE2b (32 bytes) for cryptographic hashing

Use Ed25519 for signatures

Sort map keys lexicographically

NFC-normalize all strings

Use big-endian for integers

Normalize -0.0 to +0.0

Reject messages with duplicate keys

Support UTF-8 encoding

Reject messages larger than 1MB

Validation
python
def validate_canonical(data: bytes) -> bool:
    """Validate canonical message format."""
    if len(data) < 8:
        return False
    
    # Check magic
    if data[:4] != b'VIRE':
        return False
    
    # Check version
    if data[4] != 0x30:
        return False
    
    # Check reserved bytes
    if data[6:8] != b'\x00\x00':
        return False
    
    # Check nonce
    if len(data) < 8 + 16:
        return False
    offset = 8 + 16  # Skip to signature
    if len(data) < offset + 64:
        return False
    
    return True
Performance Considerations
Benchmarks
Operation	Python	Rust	TypeScript	Go	Java
Serialize	1.2µs	0.3µs	0.8µs	0.5µs	0.7µs
Deserialize	2.1µs	0.4µs	1.2µs	0.6µs	0.9µs
Hash	0.8µs	0.2µs	0.5µs	0.3µs	0.4µs
Optimization Tips
Use zero-copy parsing where possible

Pre-allocate buffers for serialization

Cache hash computations for repeated messages

Use SIMD for hash computation

Batch operations for multiple messages

Security Considerations
Canonical Hash Security
BLAKE2b provides 256-bit security

Used for message authentication

Collision-resistant

Pre-image resistant

Signature Security
Ed25519 provides 128-bit security

Deterministic signatures

Resistant to side-channel attacks

Fast verification

Replay Protection
Nonce + timestamp in canonical hash

Unique per message

Prevents replay attacks

TTL of 5 minutes


