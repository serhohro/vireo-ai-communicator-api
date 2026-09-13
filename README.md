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
- **Deterministic bytes** - identical in Python and Rust (TypeScript pending)

---

## Status: v3.2.0 — Rust SDK + Cross-Language Conformance

| Component | Status |
|-----------|--------|
| Wire format (96B header + RFC 8785 JCS) | Implemented (Python + Rust) |
| Ed25519 signing and verification | Implemented (Python + Rust) |
| BLAKE2b-256 hashing | Implemented (Python + Rust) |
| State machine (12 states, enforced) | Implemented |
| Nonce replay protection (SQLite) | Implemented |
| DID generation + resolution | Implemented |
| Trust bootstrap (challenge-response) | Implemented |
| Contract-level verification | Implemented |
| LLM provider adapters (9 providers) | Partial |
| **Cross-language conformance (Python ↔ Rust)** | **Implemented (v3.2.0)** |
| Rust SDK | Implemented (v3.2.0) |
| TypeScript SDK | v3.3 target |
| WASM runtime | v3.3 target |
| Semantic AST Pass | v3.3 target |

**Conformance:** 32 / 32 tests passed (Python 3.11.9) + 19 / 19 (Rust 1.98.1) + 1 / 1 cross-language vector

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
LLM = Reasoning Engine
Vireo = Control Plane
A2A = Agent Transport / Discovery
MCP = Tool / Context Interface
HTTP/WS/gRPC = Transport

text

### Lifecycle
DISCOVER -> PROPOSE -> NEGOTIATE -> COMMIT -> EXECUTE -> VERIFY -> DONE
| | | | |
REJECTED REJECTED CANCELLED FAILED ESCALATED
| | |
TIMEOUT TIMEOUT NEGOTIATE / DONE

text

Illegal transitions are physically forbidden by `VireoStateMachine`.

---

## Cryptography

- **Signature:** Ed25519 (RFC 8032)
- **Hash:** BLAKE2b-256 (RFC 7693)
- **Canonical form:** RFC 8785 JCS
- **DID:** `did:vireo:<base64url(BLAKE2b-256("agent:name"))>`

---

## Implementations

| Language | Path | Version | Status |
|----------|------|---------|--------|
| Python | `core/` + `api/` | v3.1.0 | 32/32 tests pass |
| Rust | `sdk/rust/` | v3.2.0 | 19/19 unit tests + 1/1 conformance pass |
| TypeScript | `sdk/typescript/` | — | v3.3 target |

---

## Quick Start

### Python

```bash
git clone https://github.com/serhohro/vireo-ai-communicator-4.git
cd vireo-ai-communicator-4
pip install -r requirements.txt
python -m api.server
Then open http://localhost:5000/web.

Rust
bash
cd sdk/rust
cargo test
cargo test --test test_vectors -- --nocapture
Conformance
Python SDK
bash
pytest tests/conformance/ -v
Result: 32 passed.

Rust SDK
bash
cd sdk/rust
cargo test
Result: 19 unit tests passed + 1 cross-language vector passed.

Cross-Language (North Star)
bash
# 1. Python generates the vector
python scripts/generate_test_vectors.py

# 2. Rust verifies the same vector
cd sdk/rust
cargo test --test test_vectors -- --nocapture
Expected output:

text
🌿 001_propose_commit — 001_propose_commit.json
   ✅ canonical bytes match (226 bytes)
   ✅ wire_hash match: 011c2182af8206779ae3bc4ff145467a49ae0a2389ee54f940da9de24e7255db
   ✅ Python signature verifies in Rust
   🎯 001_propose_commit — PASS
European LLM Support
Provider	Country
Mistral AI	France
Aleph Alpha	Germany
Cohere	Switzerland
The North Star
"Prove that Vireo can make independently implemented AI agents interoperable."

The proof is a single conformance test vector:

text
tests/conformance/vectors/001_propose_commit.json
When Python, Rust, and TypeScript produce identical canonical_hex, wire_hash_hex, and signature_hex - the North Star is achieved.

Current progress: ✅ Python OK | ✅ Rust OK | ⏳ TypeScript pending

Achieved on 2026-09-11: Python and Rust produce byte-identical output
for vector 001_propose_commit:

canonical bytes: 226 B, identical

wire_hash: 011c2182af8206779ae3bc4ff145467a49ae0a2389ee54f940da9de24e7255db

Ed25519 signature: Python's signature verifies in Rust.

License
Apache 2.0