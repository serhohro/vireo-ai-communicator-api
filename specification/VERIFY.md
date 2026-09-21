# Vireo VERIFY Intent Specification

**Version:** 3.4.0
**Status:** Draft
**Editors:** Serhii Hromyko (serhohro)
**License:** Apache 2.0
**Depends on:** PROTOCOL.md, WIRE_FORMAT_v3.1.md, CRYPTO_v3.1.md, DID_METHOD.md, KEY_LIFECYCLE.md

---

## 1. Abstract

`VERIFY` is one of the twelve Vireo intents. It is sent by the party
that requested work (`EXECUTE`) to signal that the delivered result
has been checked against the agreed acceptance criteria, and to
record the outcome of that check.

This document normatively defines:

- what VERIFY asserts, and what it does **not** assert
- the signed payload format
- the canonicalization and signing rules
- the validation algorithm for a receiver
- the interaction with the on-chain/off-chain oracle problem
- error handling

The document also explicitly addresses the **oracle problem**: a
signature proves that a VERIFY message was created by the sender. It
does **not** prove that the underlying real-world condition is true.
This limitation is documented so that implementers do not mistake
cryptographic proof for semantic truth.

---

## 2. What VERIFY Is (and Is Not)

### 2.1 What VERIFY Is

VERIFY is a **signed assertion by the verifier** that:

1. The verifier received a `DONE` (or `FAILED`) message from the
   executor for a given contract.
2. The verifier evaluated the delivered result against the
   acceptance criteria recorded in the contract.
3. The verifier reached a specific outcome (`accepted`,
   `rejected`, or `escalated`).

VERIFY is the point at which the verifier's key is used to bind the
verifier's identity to the outcome.

### 2.2 What VERIFY Is Not

VERIFY is **not** a proof that:

- the delivered result is correct in any objective sense
- the acceptance criteria were themselves reasonable
- the verifier is honest
- the verifier actually performed the evaluation
- the real-world condition referenced by the contract is true

VERIFY is a **cryptographic assertion about a claim**, not a proof of
the claim. This distinction is fundamental and is the reason the
"oracle problem" cannot be solved by cryptography alone.

### 2.3 The Oracle Problem

Any protocol that binds real-world outcomes to cryptographic
messages faces the oracle problem: the mapping from the real world
to the message is performed by a human or a program, and that
mapping is not itself verifiable by the receiver.

Vireo's position is:

- VERIFY records **who** asserted the outcome, **when**, and **for
  which contract**.
- VERIFY does **not** claim that the assertion is objectively true.
- Disputes about the truth of the assertion are handled **outside**
  the protocol (arbitration, reputation, legal contract, staking).

This is a deliberate design choice. It is documented here so that
implementers do not over-trust VERIFY.

---

## 3. Wire Encoding

### 3.1 Intent Value

VERIFY is intent value `7` in the Vireo wire format (see
WIRE_FORMAT_v3.1.md §4.2).

```
VERIFY = 7
```

### 3.2 Message Envelope

A VERIFY message uses the standard Vireo wire envelope (96-byte
header + payload + 64-byte Ed25519 signature). The payload is an
RFC 8785 JCS-canonicalized JSON object.

### 3.3 Payload Schema

The VERIFY payload has the following shape:

```json
{
  "type": "VireoVerify",
  "contractId": "0x9f2a...c41d",
  "executorDid": "did:vireo:agent.example.com:agents:bob",
  "verifierDid": "did:vireo:agent.example.com:agents:alice",
  "doneMessageHash": "b7e3...9a12",
  "outcome": "accepted",
  "acceptanceCriteriaHash": "a1b2...3c4d",
  "evidence": {
    "type": "sha256",
    "value": "d4e5...6f70"
  },
  "reason": null,
  "timestamp": "2026-09-20T12:00:00Z",
  "nonce": "3f8a1c2e4b5d6f7a8b9c0d1e2f3a4b5c"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | MUST be `"VireoVerify"` |
| `contractId` | string | yes | Contract identifier, hex-encoded |
| `executorDid` | string | yes | DID of the party that executed |
| `verifierDid` | string | yes | DID of the party asserting VERIFY |
| `doneMessageHash` | string | yes | BLAKE2b-256 hash of the `DONE` or `FAILED` message being verified, hex-encoded |
| `outcome` | string | yes | One of `"accepted"`, `"rejected"`, `"escalated"` |
| `acceptanceCriteriaHash` | string | yes | BLAKE2b-256 hash of the acceptance criteria from the contract |
| `evidence` | object | no | Optional reference to evidence supporting the outcome |
| `reason` | string | conditional | REQUIRED if `outcome` is `"rejected"` or `"escalated"`; MUST be `null` otherwise |
| `timestamp` | string | yes | ISO 8601 UTC timestamp |
| `nonce` | string | yes | 32 hex characters (16 random bytes) |

### 3.4 Outcome Semantics

| Outcome | Meaning |
|---------|---------|
| `accepted` | The verifier evaluated the result against the acceptance criteria and found it satisfactory. The contract transitions to `DONE`. |
| `rejected` | The verifier evaluated the result and found it unsatisfactory. The contract transitions to `FAILED` (or back to `NEGOTIATE`, depending on contract policy). `reason` is REQUIRED. |
| `escalated` | The verifier cannot or will not decide, and refers the matter to an external authority. The contract transitions to `ESCALATED`. `reason` is REQUIRED. |

### 3.5 Evidence Field

The `evidence` field is an optional reference to evidence supporting
the outcome. It is a small object, not the evidence itself:

```json
{
  "evidence": {
    "type": "sha256",
    "value": "d4e5f6...6f70"
  }
}
```

**Supported types:**

| Type | Value | Meaning |
|------|-------|---------|
| `sha256` | hex-encoded SHA-256 digest | Hash of an out-of-band artifact |
| `blake2b-256` | hex-encoded BLAKE2b-256 digest | Hash of an out-of-band artifact |
| `uri` | absolute URI | Reference to evidence retrievable by URI |
| `none` | `null` | Explicitly no evidence |

The verifier is not required to publish the evidence itself. The
`evidence` field only commits the verifier to a specific artifact,
so that a later dispute can be resolved by revealing the artifact
and checking the hash.

---

## 4. Signing

### 4.1 Canonicalization

The VERIFY payload MUST be canonicalized using RFC 8785 JCS before
signing. The canonical form is the byte string over which the
signature is computed.

### 4.2 Signing Key

The VERIFY payload MUST be signed by the **verifier's active
authentication key**, as published in the verifier's DID Document
(resolved via DID_METHOD.md).

```
signature = Ed25519_sign( verifier_private_key, JCS(verify_payload) )
```

### 4.3 Wire Signature

The 64-byte Ed25519 signature is appended to the wire envelope after
the payload, per WIRE_FORMAT_v3.1.md §4.1.

### 4.4 Recipient Binding

The recipient DID hash in the wire header (bytes 48–79) MUST be the
BLAKE2b-256 hash of the executor's DID. This binds the VERIFY message
to the specific executor.

---

## 5. Validation Algorithm

A receiver of a VERIFY message MUST perform the following
validation steps. If any step fails, the message MUST be rejected
with the indicated error.

```
Input:  wire_message (VERIFY), resolved_did_documents
Output: validated_verify OR error

1. Parse the wire envelope. Verify:
     - magic bytes == 0x56495245 ("VIRE")
     - version == 0x0301
     - intent == 7 (VERIFY)
   On failure, return error `malformedEnvelope`.

2. Parse the payload as JSON. Validate against the schema in §3.3.
   On failure, return error `malformedPayload`.

3. Verify that `payload.type == "VireoVerify"`.
   On failure, return error `malformedPayload`.

4. Resolve `payload.verifierDid` via DID_METHOD.md §5.1.
   On failure, return error `verifierDidNotResolved`.

5. Extract the verifier's active authentication key from the
   resolved DID Document (the key referenced by `authentication`).

6. Verify the wire signature (bytes after the payload) against
   JCS(payload) using the verifier's active key.
   On failure, return error `invalidSignature`.

7. Verify that `payload.timestamp` is within the acceptable window
   (recommended: ±300 seconds of the receiver's clock).
   On failure, return error `timestampOutOfWindow`.

8. Verify that `payload.nonce` has not been seen before for this
   `contractId` (replay protection).
   On failure, return error `nonceReplayed`.

9. Resolve `payload.executorDid` via DID_METHOD.md §5.1.
   On failure, return error `executorDidNotResolved`.

10. Verify that the receiver's own DID equals `payload.executorDid`.
    On failure, return error `notAddressedToMe`.

11. Look up the contract by `payload.contractId`.
    On failure, return error `unknownContract`.

12. Verify that the contract's state is `EXECUTE` (i.e., the
    executor has sent DONE or FAILED and is awaiting VERIFY).
    On failure, return error `invalidStateTransition`.

13. Verify that `payload.doneMessageHash` equals the BLAKE2b-256
    hash of the DONE or FAILED message recorded in the contract.
    On failure, return error `doneMessageHashMismatch`.

14. Verify that `payload.acceptanceCriteriaHash` equals the
    BLAKE2b-256 hash of the acceptance criteria recorded in the
    contract.
    On failure, return error `acceptanceCriteriaHashMismatch`.

15. If `payload.outcome` is `"rejected"` or `"escalated"`, verify
    that `payload.reason` is a non-empty string.
    On failure, return error `reasonRequired`.

16. Return `validated_verify`.
```

### 5.1 Error Codes

| Code | Meaning |
|------|---------|
| `malformedEnvelope` | Wire envelope is malformed |
| `malformedPayload` | Payload is not valid JSON or fails schema |
| `verifierDidNotResolved` | `verifierDid` could not be resolved |
| `executorDidNotResolved` | `executorDid` could not be resolved |
| `invalidSignature` | Signature does not verify against the verifier's active key |
| `timestampOutOfWindow` | Timestamp is outside the acceptable window |
| `nonceReplayed` | Nonce has been seen before for this contract |
| `notAddressedToMe` | `executorDid` does not match the receiver's DID |
| `unknownContract` | `contractId` is not known to the receiver |
| `invalidStateTransition` | Contract is not in a state that accepts VERIFY |
| `doneMessageHashMismatch` | `doneMessageHash` does not match the recorded DONE/FAILED message |
| `acceptanceCriteriaHashMismatch` | `acceptanceCriteriaHash` does not match the recorded criteria |
| `reasonRequired` | `reason` is missing or empty for `rejected`/`escalated` |

---

## 6. Interaction with the Contract State Machine

### 6.1 State Transition

A validated VERIFY message causes the following state transitions
in the contract state machine (see STATE_MACHINE.md):

```
EXECUTE --[VERIFY accepted]--> DONE
EXECUTE --[VERIFY rejected]--> FAILED
EXECUTE --[VERIFY escalated]--> ESCALATED
```

### 6.2 Terminal States

- `DONE` is terminal. No further VERIFY messages are accepted for
  this contract.
- `FAILED` is terminal unless the contract policy allows
  re-negotiation.
- `ESCALATED` is terminal from the protocol's perspective. The
  outcome is determined by an external authority.

### 6.3 Re-Verification

A contract MAY allow multiple VERIFY messages if the contract policy
explicitly permits re-verification (e.g., after a rejected result is
re-submitted). In that case, each VERIFY MUST use a fresh nonce.

---

## 7. Interaction with Key Lifecycle

The verifier's signature is validated against the verifier's active
authentication key at the time of validation. If the verifier's key
has been rotated since the VERIFY was sent, the receiver MUST check
the key history (KEY_LIFECYCLE.md §6) to confirm that the key was
active at the time indicated by `payload.timestamp`.

**Rule:** A VERIFY signature is valid if and only if:

1. The signing key was in state `active` at `payload.timestamp`, and
2. The signing key has not been revoked with `revokedAt` earlier
   than `payload.timestamp`.

If the key was revoked at or before `payload.timestamp`, the VERIFY
MUST be rejected with error `keyRevoked`.

### 7.1 Additional Error Code

| Code | Meaning |
|------|---------|
| `keyRevoked` | The verifier's key was revoked at or before the VERIFY timestamp |

---

## 8. Security Considerations

### 8.1 The Oracle Problem (Restated)

As stated in §2.3, VERIFY does not prove that the underlying
real-world condition is true. It proves only that the verifier
asserted a specific outcome at a specific time. Implementers MUST
NOT treat VERIFY as objective truth.

**Recommended mitigations for high-stakes contracts:**

- Use multiple independent verifiers and require a threshold of
  agreement.
- Require the verifier to stake value that can be slashed on proven
  misbehavior.
- Use an external arbitration service for disputes.
- Record evidence hashes so that disputes can be resolved by
  revealing the evidence.

These mitigations are **outside** the Vireo protocol. Vireo provides
the cryptographic substrate; the trust model is the application's
responsibility.

### 8.2 Replay Protection

The combination of `nonce`, `timestamp`, and `doneMessageHash` binds
each VERIFY to a specific DONE/FAILED message. A replayed VERIFY
will be rejected by the nonce check (§5 step 8).

### 8.3 Signature Binding

The wire signature binds the VERIFY payload to the verifier's
identity. An attacker cannot forge a VERIFY without the verifier's
private key.

### 8.4 Timestamp Trust

`timestamp` is self-asserted. A receiver SHOULD allow a small clock
skew (recommended: ±300 seconds) and MUST reject timestamps outside
that window.

### 8.5 Key Rotation

A key rotation after a VERIFY was sent does not invalidate the
VERIFY, provided the key was active at `timestamp`. See §7.

### 8.6 Revocation

A revoked key invalidates all VERIFY messages signed after
`revokedAt`. See §7.1.

### 8.7 Escalation

The `escalated` outcome is a deliberate escape hatch: the verifier
declares that it cannot or will not decide. This is preferable to a
forced binary decision in ambiguous cases. Receivers SHOULD handle
`escalated` by referring to the external authority named in the
contract.

---

## 9. Privacy Considerations

- The VERIFY payload reveals the contract ID, the executor DID, and
  the outcome. This information is visible to anyone who can observe
  the wire message. Contracts that require privacy SHOULD use an
  encrypted transport or a private Vireo deployment.
- The `evidence` field commits the verifier to a specific artifact
  by hash. If the artifact is later revealed, it may reveal
  information about the verifier's evaluation process. Verifiers
  SHOULD choose evidence types that do not leak more than necessary.
- The `reason` field, required for `rejected` and `escalated`, may
  reveal operational details. Verifiers SHOULD keep reasons concise
  and avoid disclosing sensitive information.

---

## 10. Intellectual Property

This specification is published under the Apache License, Version 2.0.

---

## 11. References

### Normative

- [PROTOCOL.md] ./PROTOCOL.md
- [WIRE_FORMAT_v3.1.md] ./WIRE_FORMAT_v3.1.md
- [CRYPTO_v3.1.md] ./CRYPTO_v3.1.md
- [DID_METHOD.md] ./DID_METHOD.md
- [KEY_LIFECYCLE.md] ./KEY_LIFECYCLE.md
- [STATE_MACHINE.md] ./STATE_MACHINE.md
- [RFC 8032] Edwards-Curve Digital Signature Algorithm (EdDSA)
- [RFC 8785] JSON Canonicalization Scheme (JCS)

### Informative

- [CONTRACTS.md] ./CONTRACTS.md
- [INTEROPERABILITY.md] ./INTEROPERABILITY.md
