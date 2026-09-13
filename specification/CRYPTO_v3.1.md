# Vireo Cryptography v3.1

## Algorithms

| Purpose   | Algorithm   | Reference |
|-----------|-------------|-----------|
| Signature | Ed25519     | RFC 8032  |
| Hash      | BLAKE2b-256 | RFC 7693  |
| Canonical | RFC 8785    | RFC 8785  |
| DID       | did:vireo   | this spec |

## Why BLAKE2b-256 over SHA-256

Measured: BLAKE2b-256 is 1.53x faster than SHA-256 on 1 KB input.

Additional reasons:

- Deterministic by default
- No length-extension attacks
- Cross-language: hashlib / blake2 crate / @noble/hashes
- Aligns with RFC 8785 JCS

## Signing Flow

    canonical_bytes = canonical_wire_bytes(envelope)
    wire_hash = BLAKE2b-256(canonical_bytes)
    signature = Ed25519_Sign(private_key, wire_hash)

## DID Format

    did:vireo:<base64url(BLAKE2b-256("agent:name"))>

## DID Document (minimal)

    {
      "did": "did:vireo:...",
      "publicKeys": [
        {
          "id": "did:vireo:...#keys-1",
          "type": "Ed25519VerificationKey2020",
          "publicKeyHex": "..."
        }
      ]
    }

## Key Discovery

1. In-memory registry (default).
2. Static HTTP: https://host/.well-known/did.json (future).
3. Fallback: embed public key in first message.

## Nonce Replay Protection

- Store: SQLite
- TTL: 24 hours
- Clock skew tolerance: +/- 5 minutes
- Key: (nonce, sender_id)
- Nonce size: 16 bytes

## Benchmark (measured)

| Operation        | Mean      |
|------------------|-----------|
| BLAKE2b-256 (1K) | 1.69 us   |
| SHA-256 (1K)     | 2.59 us   |
| BLAKE2b speedup  | 1.53x     |
| Ed25519 sign     | 39.3 us   |
| Ed25519 verify   | 66.4 us   |

## Threat Model

| Threat              | Mitigation                     |
|---------------------|--------------------------------|
| Signature forgery   | Ed25519                        |
| Payload tampering   | BLAKE2b-256 over canonical     |
| Replay attack       | Nonce store + timestamp window |
| MITM                | Signature binds sender DID     |
| Key substitution    | DID registry + trust bootstrap |
| Ambiguous encoding  | RFC 8785 JCS                   |