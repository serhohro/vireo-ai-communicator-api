# Vireo Roadmap

## v3.1 — Interoperability Release (current)

**Focus:** make the protocol real, not wider.

Completed:

- [x] RFC 8785 JCS canonical serialization
- [x] BLAKE2b-256 hashing
- [x] 96-byte wire header
- [x] Ed25519 signing/verification (real)
- [x] State machine (enforced)
- [x] Nonce replay protection (SQLite)
- [x] DID resolution
- [x] Trust bootstrap (challenge-response)
- [x] Conformance test suite (32 tests PASS)
- [x] Benchmark harness
- [x] Specification: WIRE_FORMAT_v3.1.md, CRYPTO_v3.1.md, COMPLIANCE.md

In progress:

- [ ] Cross-language conformance (Python ↔ Rust ↔ TS)
- [ ] Fill tests/conformance/vectors/001_propose_commit.json
- [ ] Remove remaining mock endpoints

## v3.2 — Execution Security

- [ ] WASM runtime
- [ ] Semantic AST Pass
- [ ] Full SMT verification (business logic)
- [ ] GPU support (optional)
- [ ] OpenTelemetry
- [ ] Property-based testing
- [ ] Fuzzing harness
- [ ] Rust SDK production-ready
- [ ] TypeScript SDK production-ready

## v4.0 — Standardization

- [ ] RFC process
- [ ] Independent implementations
- [ ] IETF submission (optional)
- [ ] EU cloud integrations (OVH, Hetzner)

## Principles

1. No new features until existing ones are real.
2. No overclaims in documentation.
3. Conformance test vectors are the source of truth.
4. Cross-language interop is the North Star.

## North Star

> **"Prove that Vireo can make independently implemented AI agents interoperable."**

The proof is a single conformance test vector:

    tests/conformance/vectors/001_propose_commit.json

When this vector produces identical `canonical_hex`, `wire_hash_hex`,
and `signature_hex` in Python, Rust, and TypeScript — the North Star
is achieved.