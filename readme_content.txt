# Vireo

**The world's first AI-to-AI communication language with built-in Ed25519, DIDs, and contract lifecycle.**

*Experimental proof-of-concept. Do not use in production without a security audit.*

---

## Why "the world's first"?

Vireo is the first system that unifies **four layers** in a single language:

| Layer | Vireo provides | Others |
|-------|----------------|--------|
| **Language** | Vireo DSL for agent coordination | FIPA-ACL (1990s) - protocol only |
| **Protocol** | 96-byte wire + RFC 8785 JCS | A2A - JSON-RPC only |
| **Cryptography** | Ed25519 + BLAKE2b-256 | MCP - no crypto |
| **Identity** | DID-based (`did:vireo:...`) | None in A2A/MCP |

No other system combines all four.

**What makes it "first":**

- **Ed25519 built into the wire format** - every message is signed
- **DIDs as first-class identity** - no central authority
- **Contract lifecycle enforced** - DISCOVER -> PROPOSE -> NEGOTIATE -> COMMIT -> EXECUTE -> VERIFY -> DONE
- **Deterministic bytes** - identical in Python, Rust, TypeScript

---

## Status: v3.1 - Interoperability Release

| Component | Status |
|-----------|--------|
| Wire format (96B header + RFC 8785 JCS) | Implemented |
| Ed25519 signing and verification | Implemented |
| BLAKE2b-256 hashing | Implemented |
| State machine (12 states, enforced) | Implemented |
| Nonce replay protection (SQLite) | Implemented |
| DID generation + resolution | Implemented |
| Trust bootstrap (challenge-response) | Implemented |
| Contract-level verification | Implemented |
| LLM provider adapters (9 providers) | Partial |
| Cross-language conformance | v3.2 target |
| WASM runtime | v3.2 target |
| Semantic AST Pass | v3.2 target |

**Conformance:** 32 / 32 tests passed (Python 3.11.9)

**Benchmarks** (measured, not marketing):

| Metric | Result |
|--------|--------|
| Wire size (small) | 2.58x smaller than JSON |
| Wire size (medium) | 1.79x smaller |
| BLAKE2b vs SHA-256 | 1.53x faster |
| Ed25519 sign | 39.3 us |
| Ed25519 verify | 66.4 us |
| Serialization speed | 0.42x-0.90x slower than JSON |

**Honest note:** Vireo trades raw serialization speed for **deterministic bytes** - required for cross-language Ed25519 signatures.

---

## Architecture
