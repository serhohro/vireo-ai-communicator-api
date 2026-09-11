# Vireo Wire Format v3.1

Version: 3.1
Wire version: 0x0301
Status: Specification

## Overview

Vireo wire messages are binary, canonical, and deterministic.
The exact same logical message MUST produce the exact same bytes
across Python, Rust, and TypeScript.

## Canonical Binary Layout

### Header (fixed 96 bytes, Big-Endian)

| Offset | Field            | Size | Type     |
|--------|------------------|------|----------|
| 0      | Magic            | 4 B  | bytes    |
| 4      | Version          | 2 B  | uint16   |
| 6      | Intent           | 2 B  | uint16   |
| 8      | Timestamp        | 8 B  | uint64   |
| 16     | Nonce            | 16 B | bytes    |
| 32     | Sender DID hash  | 32 B | bytes    |
| 64     | Recipient hash   | 32 B | bytes    |
| 96     | (end of header)  | -    | -        |

### Payload Section

| Offset | Field          | Size | Type     |
|--------|----------------|------|----------|
| 96     | Payload length | 4 B  | uint32   |
| 100    | Payload        | var  | bytes    |

Payload bytes are RFC 8785 JCS canonical JSON.

## Intent Mapping

| ID | Intent    |
|----|-----------|
| 1  | DISCOVER  |
| 2  | PROPOSE   |
| 3  | NEGOTIATE |
| 4  | COMMIT    |
| 5  | REJECT    |
| 6  | EXECUTE   |
| 7  | VERIFY    |
| 8  | DONE      |
| 9  | ESCALATED |
| 10 | CANCELLED |
| 11 | FAILED    |
| 12 | TIMEOUT   |

## Canonical Rules

1. All integers Big-Endian (network byte order).
2. Strings encoded as UTF-8 NFC.
3. No whitespace outside JSON string values.
4. Object keys sorted lexicographically by Unicode code point.
5. Floats formatted per ECMAScript/IEEE-754 shortest round-trip.
6. No NaN, Infinity, -Infinity.
7. No floating-point numbers in header fields.

## Signing

    payload_hash = BLAKE2b-256(payload_bytes)
    canonical_bytes = header || payload_length || payload_bytes
    wire_hash = BLAKE2b-256(canonical_bytes)
    signature = Ed25519_Sign(private_key, wire_hash)

## Verification

1. Parse header. Reject if magic or version mismatch.
2. Verify payload length matches actual bytes.
3. Recompute canonical_bytes.
4. Recompute wire_hash.
5. Resolve sender public key via DID.
6. Verify Ed25519 signature.
7. Check nonce not replayed.
8. Check timestamp within +/- 5 min tolerance.

## Why not Protobuf?

Custom binary chosen because:

- Zero dependencies (stdlib only)
- Deterministic by default
- Transparent for debugging (hex dump)
- Cross-language: struct.pack / byteorder / DataView

Protobuf can be added in v3.2 as an alternative codec.

## Benchmark

Wire serialization is slower than raw json.dumps() (0.42x-0.90x)
because it performs RFC 8785 canonicalization + BLAKE2b hashing.

Vireo delivers deterministic bytes for cross-language Ed25519 signatures.

See benches/wire_perf/RESULTS.md for measured data.