# Vireo VERIFY Semantics

**Version:** 0.1 (Draft)
**Status:** Working Draft
**Date:** 2026-09-15

## 1. Problem

Vireo signatures prove that **bytes were exchanged**, not that the **real-world commitment was fulfilled**. This is the "oracle problem" identified in external reviews.

### 1.1 What Signatures Prove
- Message authored by holder of private key.
- Message not tampered with in transit.
- Nonce prevents replay.

### 1.2 What Signatures Do NOT Prove
- That the executor actually performed the work.
- That the output satisfies the specification.
- That any real-world outcome occurred.

## 2. Minimal VERIFY Protocol

### 2.1 Model
Agent action → Verify → Sign → Receipt → Execute

text

### 2.2 VERIFY Semantics
VERIFY checks whether an output **satisfies its specification**.

VERIFY does NOT:
- Execute payments.
- Enforce outcomes.
- Provide identity.
- Resolve disputes.

## 3. Receipt Model

### 3.1 Receipt Schema (receipt_v0_1)

```json
{
  "task_id_hash": "sha256:...",
  "verdict": "PASS" | "FAIL" | "INDETERMINATE",
  "confidence": 0.95,
  "reason_code": "SPEC_MATCH" | "SPEC_MISMATCH" | "INSUFFICIENT_EVIDENCE",
  "ts": "2026-09-15T10:00:00Z",
  "verifier_kid": "vireo-key-abc123..."
}
3.2 Canonicalization
Receipt MUST be canonicalized using RFC 8785 (JCS).

SHA-256 hash of canonical form is receipt_id.

Ed25519 signature over receipt_id.

3.3 Verification Flow
Extract receipt.

Canonicalize (RFC 8785 JCS).

Compute SHA-256 digest.

Confirm digest matches receipt_id.

Resolve verifier_kid to public key.

Verify Ed25519 signature.

No server interaction required after key resolution.

4. What VERIFY Does NOT Prove
Explicitly:

Real-world outcome — VERIFY does not know if the work was actually done.

Correctness of computation — VERIFY does not re-execute the computation.

Third-party attestation — VERIFY is self-attestation unless combined with oracles.

5. Future: Attested Execution
5.1 TEE Receipts
Trusted Execution Environment (TEE) can attest to computation.

TEE receipt MAY be included as evidence.

5.2 Oracle Attestation
Third-party oracle can attest to real-world outcome.

Oracle receipt MAY be included.

5.3 Zero-Knowledge Proofs
ZK proofs can prove computation without revealing inputs.

Future extension.

6. References
SAR Protocol v0.2 (default-settlement-verifier)

RFC 8785: JSON Canonicalization Scheme

IETF draft: Compliance Receipts