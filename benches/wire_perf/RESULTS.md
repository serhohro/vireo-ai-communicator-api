# Vireo Wire & Crypto Performance Results

**Status:** Measured
**Environment:** Windows 10, Python 3.11.9, pytest 9.1.1
**Date:** 2026-09-11

**Command:**

    python -m benches.wire_perf.bench_wire --profile=all --iterations=1000
    python -m benches.wire_perf.bench_crypto

## Wire: JSON vs Vireo Canonical Binary

| Profile | Format | Mean (ns) | Median (ns) | P99 (ns) | Size (B) | Speedup vs JSON |
|---------|--------|-----------|-------------|----------|----------|-----------------|
| small   | JSON   | 2,149     | 2,100       | 3,400    | 286      | -               |
| small   | Vireo  | 2,389     | 2,300       | 3,000    | 111      | 0.90x (slower)  |
| medium  | JSON   | 2,649     | 2,600       | 3,200    | 399      | -               |
| medium  | Vireo  | 4,161     | 4,100       | 4,900    | 223      | 0.64x (slower)  |
| large   | JSON   | 3,055,510 | 2,915,950   | 6,401,600| 289,178  | -               |
| large   | Vireo  | 7,304,184 | 6,964,700   |11,847,200| 289,002  | 0.42x (slower)  |

### Key Insights

Vireo serialization is slower than raw `json.dumps()` because it performs:

1. RFC 8785 JCS canonicalization (sort keys, NFC normalization, no whitespace)
2. BLAKE2b-256 hashing for sender/recipient DID
3. Fixed 96-byte header (magic + version + intent + timestamp + nonce + DID hashes)

However, Vireo delivers unique value:

| Feature                    | JSON | Vireo                |
|----------------------------|------|----------------------|
| Deterministic bytes        | No   | Yes (RFC 8785)       |
| Cross-language identical   | No   | Yes (Py/Rust/TS)     |
| Signature-ready            | No   | Yes (BLAKE2b+Ed25519)|
| Size (small)               | 286B | 111B (2.58x smaller) |
| Size (medium)              | 399B | 223B (1.79x smaller) |
| Size (large)               | 289K | 289K (same)          |
| Speed (small)              | 2.1us| 2.4us (0.90x)        |
| Speed (medium)             | 2.6us| 4.2us (0.64x)        |
| Speed (large)              | 3.1ms| 7.3ms (0.42x)        |

Conclusion: Vireo trades raw speed for deterministic canonical form,
which is required for cross-language Ed25519 signatures.

## Hash: BLAKE2b-256 vs SHA-256 (1 KB input)

| Algorithm    | Mean (ns) | Speedup          |
|--------------|-----------|------------------|
| BLAKE2b-256  | 1,694     | 1.53x faster     |
| SHA-256      | 2,587     | -                |

## Ed25519

| Operation | Mean (ns) | Mean (us) |
|-----------|-----------|-----------|
| Sign      | 39,306    | 39.3      |
| Verify    | 66,388    | 66.4      |

## Honest Claims Policy

DO NOT claim:

- "10x faster than JSON" - measured 0.42x-0.90x (slower)
- "Blazing fast" - Vireo is optimized for correctness, not raw speed
- "Production ready" - this is a proof-of-concept

MAY claim:

- "Up to 2.58x smaller wire format for small messages"
- "Deterministic canonical bytes (RFC 8785 JCS)"
- "Cross-language identical representation (Python/Rust/TypeScript)"
- "BLAKE2b-256 is 1.53x faster than SHA-256"
- "Ed25519 sign: 39 us, verify: 66 us"

Reproducibility: any third party with Python 3.10+ can re-run these
benchmarks on their hardware to verify the numbers above.
