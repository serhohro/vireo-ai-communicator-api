# Vireo Key Lifecycle Specification

**Version:** 3.4.0
**Status:** Draft
**Editors:** Serhii Hromyko (serhohro)
**License:** Apache 2.0
**Depends on:** DID_METHOD.md, WIRE_FORMAT_v3.1.md, CRYPTO_v3.1.md

---

## 1. Abstract

This document normatively defines the lifecycle of Ed25519 keys used
by Vireo agents: generation, activation, rotation, revocation, and
expiry. It specifies the signed payload format, the canonicalization
rules, the publication mechanism, and the validation algorithm for
each lifecycle transition.

The key lifecycle is expressed entirely through signed updates to the
agent's DID Document. There is no separate registry, no out-of-band
state, and no trusted third party. A conforming verifier can validate
any key transition using only:

1. the current DID Document (resolved via DID_METHOD.md), and
2. the signed transition payload.

---

## 2. Requirements

1. **Self-contained.** Every key transition must be verifiable from
   the DID Document alone, without external state.
2. **Monotonic.** A key transition must not be reversible by an
   attacker who later compromises an old key.
3. **Chain-verifiable.** A verifier must be able to reconstruct the
   full chain of rotations from the current DID Document.
4. **Replay-resistant.** An old signed transition must not be
   replayable after the key it was signed with has been rotated.
5. **Revocable.** A compromised key must be revocable in a way that
   invalidates all future use.

---

## 3. Key States

A Vireo key is always in exactly one of the following states:

```
        +-----------+
        |  pending  |   (generated, not yet published)
        +-----------+
              |
              | publish (signed by current auth key or bootstrap)
              v
        +-----------+
        |  active   |   (published, valid for signing)
        +-----------+
           |     |
   rotate  |     |  revoke
           v     v
   +-----------+ +--------------+
   |  retired  | |  revoked     |
   +-----------+ +--------------+
        |
        | (after grace period)
        v
   +-----------+
   |  expired  |
   +-----------+
```

**States:**

- **pending** — key exists locally, not yet published in a DID
  Document.
- **active** — key is published in the DID Document and is valid for
  signing. A DID Document MUST have exactly one active authentication
  key at any time.
- **retired** — key was rotated out. It remains in the DID Document
  history for verification of past signatures, but MUST NOT be used
  for new signatures.
- **revoked** — key was compromised and is permanently invalid.
  Signatures made with a revoked key after the revocation timestamp
  MUST be rejected.
- **expired** — key passed its `expires` timestamp. It is treated as
  retired for signature verification, but the transition is driven by
  time rather than by a signed rotation.

---

## 4. Key Material

### 4.1 Algorithm

Vireo uses Ed25519 (RFC 8032) for all signing operations.

### 4.2 Public Key Representation

Public keys are represented in DID Documents using the normative
`publicKeyMultibase` property (see DID_METHOD.md §4.3):

```
publicKeyMultibase = "z" || base58btc( 0xed01 || ed25519_pubkey_bytes )
```

Where `ed25519_pubkey_bytes` is exactly 32 bytes.

### 4.3 Key Identifier

Every key has a fragment identifier within the DID Document:

```
did:vireo:<domain>:<path>#key-<n>
```

Where `<n>` is a monotonically increasing integer starting at 1. The
fragment MUST be stable for the lifetime of the key.

### 4.4 keyStatus Property

The `keyStatus` property (defined in DID_METHOD.md §4.1) records the
state of the authentication key:

```json
{
  "keyStatus": "active"
}
```

Allowed values: `"active"`, `"retired"`, `"revoked"`, `"expired"`.

---

## 5. Lifecycle Transitions

### 5.1 Generation

A new key is generated locally using a cryptographically secure
random number generator. The key is in state `pending` until it is
published.

**Normative requirements:**

- The RNG MUST be a CSPRNG (e.g. `/dev/urandom`, `getrandom(2)`).
- The private key MUST be stored encrypted at rest, or in a hardware
  security module.
- The private key MUST NOT be transmitted over the network in
  plaintext, ever.

### 5.2 Activation (Initial Publication)

The first key of a DID is published as part of the DID Document
creation (see DID_METHOD.md §6.1). The DID Document MUST:

- include the key in `verificationMethod`
- reference it from `authentication`
- set `keyStatus` to `"active"`

**Transition to active:** `pending` → `active`.

### 5.3 Rotation

Key rotation replaces the active authentication key with a new one.
Rotation is expressed as a signed Update to the DID Document
(DID_METHOD.md §6.3).

#### 5.3.1 Rotation Payload

The rotation payload is a JSON object with the following shape:

```json
{
  "type": "VireoKeyRotation",
  "did": "did:vireo:agent.example.com:agents:alice",
  "previousKeyId": "did:vireo:agent.example.com:agents:alice#key-1",
  "newKeyId": "did:vireo:agent.example.com:agents:alice#key-2",
  "newPublicKeyMultibase": "z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH",
  "effectiveTimestamp": "2026-09-20T12:00:00Z",
  "reason": "scheduled"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | MUST be `"VireoKeyRotation"` |
| `did` | string | yes | The DID being rotated |
| `previousKeyId` | string | yes | Fragment ID of the key being rotated out |
| `newKeyId` | string | yes | Fragment ID of the new key |
| `newPublicKeyMultibase` | string | yes | New public key in multibase form |
| `effectiveTimestamp` | string | yes | ISO 8601 UTC timestamp |
| `reason` | string | no | One of `"scheduled"`, `"compromise"`, `"expiry"` |

#### 5.3.2 Canonicalization

The rotation payload MUST be canonicalized using RFC 8785 JCS before
signing. The canonical form is the byte string over which the
signature is computed.

#### 5.3.3 Signing

The rotation payload MUST be signed by the **current active
authentication key** (the key identified by `previousKeyId`).

```
signature = Ed25519_sign( private_key_previous, JCS(rotation_payload) )
```

The signature is encoded as base64url (no padding) and included in
the DID Document update as a proof.

#### 5.3.4 Publication

The rotation is published as a DID Document Update (DID_METHOD.md
§6.3). The new DID Document MUST:

1. Move `previousKeyId` from `authentication` to a `keyHistory`
   array, with `keyStatus` set to `"retired"`.
2. Add `newKeyId` to `verificationMethod`.
3. Reference `newKeyId` from `authentication`.
4. Set the top-level `keyStatus` to `"active"`.
5. Include the rotation proof:

```json
{
  "proof": {
    "type": "VireoKeyRotationProof",
    "created": "2026-09-20T12:00:00Z",
    "proofPurpose": "keyRotation",
    "verificationMethod": "did:vireo:agent.example.com:agents:alice#key-1",
    "jws": "<base64url signature over JCS(rotation_payload)>"
  }
}
```

#### 5.3.5 Validation Algorithm

A verifier validating a rotation MUST:

```
Input:  oldDidDocument, newDidDocument, rotationProof
Output: valid OR error

1. Verify that newDidDocument.id == oldDidDocument.id.

2. Extract previousKeyId from rotationProof.verificationMethod.
   Verify that oldDidDocument.authentication contains previousKeyId.

3. Extract the previous public key from
   oldDidDocument.verificationMethod[previousKeyId].

4. Reconstruct the rotation payload from newDidDocument:
     - type = "VireoKeyRotation"
     - did = newDidDocument.id
     - previousKeyId = rotationProof.verificationMethod
     - newKeyId = newDidDocument.authentication[0]
     - newPublicKeyMultibase =
         newDidDocument.verificationMethod[newKeyId].publicKeyMultibase
     - effectiveTimestamp = rotationProof.created
     - reason = (as published)

5. Canonicalize the payload with RFC 8785 JCS.

6. Verify the JWS signature in rotationProof.jws against the
   canonical payload using the previous public key.

7. If verification fails, return error `invalidRotationProof`.

8. Verify that newDidDocument.keyStatus == "active".

9. Verify that newDidDocument.authentication[0] != previousKeyId
   (the key actually changed).

10. Return valid.
```

#### 5.3.6 Error Codes

| Code | Meaning |
|------|---------|
| `invalidRotationProof` | Signature does not verify against the previous key |
| `keyNotActive` | `previousKeyId` is not the current active key |
| `keyAlreadyRetired` | `previousKeyId` is already in `keyHistory` |
| `invalidNewKey` | `newPublicKeyMultibase` is malformed |
| `timestampInPast` | `effectiveTimestamp` is before the previous rotation |

### 5.4 Revocation

Revocation permanently invalidates a key. It is used when a key is
known or suspected to be compromised.

#### 5.4.1 Revocation Payload

```json
{
  "type": "VireoKeyRevocation",
  "did": "did:vireo:agent.example.com:agents:alice",
  "keyId": "did:vireo:agent.example.com:agents:alice#key-2",
  "effectiveTimestamp": "2026-09-20T12:00:00Z",
  "reason": "compromise"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | MUST be `"VireoKeyRevocation"` |
| `did` | string | yes | The DID whose key is revoked |
| `keyId` | string | yes | Fragment ID of the revoked key |
| `effectiveTimestamp` | string | yes | ISO 8601 UTC timestamp |
| `reason` | string | yes | One of `"compromise"`, `"cessation"`, `"superseded"` |

#### 5.4.2 Signing

The revocation payload MUST be signed by the **current active
authentication key**, unless that key is itself the one being
revoked. In that case, the payload MAY be signed by the next active
key, provided the rotation that introduced it is also published
atomically.

```
signature = Ed25519_sign( signing_key, JCS(revocation_payload) )
```

#### 5.4.3 Publication

The revocation is published as a DID Document Update. The revoked
key MUST:

1. Be moved from `authentication` to `keyHistory`.
2. Have `keyStatus` set to `"revoked"`.
3. Be included in the top-level `revocationList`:

```json
{
  "revocationList": [
    {
      "keyId": "did:vireo:agent.example.com:agents:alice#key-2",
      "revokedAt": "2026-09-20T12:00:00Z",
      "reason": "compromise"
    }
  ]
}
```

#### 5.4.4 Verification Rule

A verifier MUST reject any signature made by a revoked key **after**
the `revokedAt` timestamp. Signatures made **before** `revokedAt`
remain valid (they were made while the key was trusted).

#### 5.4.5 Compromise of the Active Key

If the active authentication key is compromised, the subject cannot
sign a rotation with it. In that case:

1. The subject MUST publish a new DID Document signed by the **new**
   key, containing a `VireoKeyRevocation` for the compromised key.
2. The new DID Document MUST be published at the same URL, replacing
   the old one.
3. Resolvers that cached the old DID Document will see the new one
   after cache expiry. The recommended TTL is 300 seconds.
4. The `revocationList` MUST include the compromised key with
   `revokedAt` set to the earliest known compromise time.

**Note:** This is the only transition that does not require a
signature from the previous active key. It is inherently
trust-on-first-use for resolvers that have not yet seen the new
document. This limitation is documented in §8.3.

### 5.5 Expiry

A key MAY have an `expires` timestamp in its DID Document entry:

```json
{
  "id": "did:vireo:agent.example.com:agents:alice#key-1",
  "type": "Ed25519VerificationKey2020",
  "controller": "did:vireo:agent.example.com:agents:alice",
  "publicKeyMultibase": "z6Mk...",
  "expires": "2027-09-20T12:00:00Z"
}
```

After `expires`, the key MUST be treated as retired:

- Signatures made **before** `expires` remain valid.
- Signatures made **after** `expires` MUST be rejected.
- The key MAY remain in `keyHistory` for verification of past
  signatures.

Expiry does not require a signed transition. It is driven purely by
the timestamp and the verifier's clock.

**Clock skew:** verifiers SHOULD allow a small skew (recommended:
60 seconds) when checking `expires`.

---

## 6. Chain of Rotation Proofs

The `keyHistory` array in a DID Document records the full chain of
rotations and revocations. Its entries are ordered by
`effectiveTimestamp` ascending:

```json
{
  "keyHistory": [
    {
      "keyId": "did:vireo:agent.example.com:agents:alice#key-1",
      "publicKeyMultibase": "z6Mk...",
      "status": "retired",
      "retiredAt": "2026-06-01T00:00:00Z",
      "rotationProof": "<base64url JWS>"
    },
    {
      "keyId": "did:vireo:agent.example.com:agents:alice#key-2",
      "publicKeyMultibase": "z6Mk...",
      "status": "revoked",
      "revokedAt": "2026-09-20T12:00:00Z",
      "revocationProof": "<base64url JWS>"
    }
  ]
}
```

A verifier reconstructing the chain MUST:

1. Start from the current active key.
2. For each entry in `keyHistory` (in reverse chronological order),
   verify the corresponding rotation or revocation proof.
3. Confirm that each proof was signed by the key that was active at
   the time of the transition.
4. Reject the chain if any proof fails.

If any proof in the chain fails, the DID Document MUST be treated as
invalid, and resolution MUST return error `invalidKeyHistory`.

---

## 7. Interaction with DID_METHOD.md

The `did:vireo` method (DID_METHOD.md) defines:

- the DID syntax and resolution algorithm (§3, §5)
- the DID Document structure (§4)
- CRUD operations, including Update (§6)

This document (`KEY_LIFECYCLE.md`) defines the semantics of the
`verificationMethod`, `authentication`, `keyHistory`, and
`revocationList` properties, and the signed payloads used to
transition between key states.

A conforming implementation MUST implement both documents. An
implementation that implements DID_METHOD.md but not this document
is not fully conforming.

---

## 8. Security Considerations

### 8.1 Rotation Proof Binding

Each rotation proof is bound to the specific `previousKeyId`,
`newKeyId`, `newPublicKeyMultibase`, and `effectiveTimestamp`. An
attacker cannot reuse a proof for a different key pair, because the
proof would fail verification.

### 8.2 Replay of Rotation Proofs

A rotation proof is valid only if `previousKeyId` is the **current**
active key in the verifier's view. Once the key is retired, a
replayed rotation proof from that key MUST be rejected (see §5.3.5
step 3, and §5.3.6 error `keyNotActive`).

### 8.3 Compromise of the Active Key

If the active authentication key is compromised, the attacker can
sign arbitrary updates, including a rotation to a key they control.
The legitimate subject can only recover by publishing a new DID
Document signed by a **new** key (see §5.4.5). This is inherently
trust-on-first-use: a resolver that has not yet seen the new document
cannot distinguish the attacker's update from the legitimate one.

**Mitigations:**

- Short resolution TTL (recommended: 300 seconds) limits the window.
- Out-of-band notification (e.g., a signed message over a separate
  channel) can alert peers.
- Hardware security modules reduce the risk of key extraction.

This limitation is intrinsic to any DID method that uses a single
active key without an external registry. It is documented here so
that implementers can make informed decisions.

### 8.4 No External State

The key lifecycle is entirely self-contained in the DID Document.
There is no separate registry, no external state, and no trusted
third party. This removes the "conflict-resolution procedure" concern
raised during W3C review: there are no conflicting updates because
the DID Document is the single source of truth, published at a
single HTTPS URL.

### 8.5 Canonicalization

All signed payloads MUST be canonicalized with RFC 8785 JCS before
signing. A verifier MUST canonicalize the reconstructed payload
identically. Differences in canonicalization (e.g., key ordering,
whitespace, number formatting) would cause verification to fail.

### 8.6 Timestamp Trust

`effectiveTimestamp` and `revokedAt` are self-asserted. A verifier
SHOULD check that they are not in the future (beyond a small clock
skew, recommended: 60 seconds) and not before the previous
transition. This prevents an attacker from backdating a rotation or
revocation.

---

## 9. Privacy Considerations

- The `keyHistory` array reveals the full rotation history of the
  subject, including the timestamps of rotations and revocations.
  Subjects that require unlinkability across rotations SHOULD use a
  new DID (and a new domain or path) rather than rotating in place.
- Revocation reasons (`"compromise"`, `"cessation"`,
  `"superseded"`) reveal operational information. Subjects SHOULD
  use `"superseded"` as the default and reserve `"compromise"` for
  cases where the disclosure is acceptable.
- The `expires` timestamp reveals the subject's key-rotation policy.
  Subjects that consider this sensitive SHOULD omit `expires` and
  rotate on a schedule instead.

---

## 10. Intellectual Property

This specification is published under the Apache License, Version 2.0.

---

## 11. References

### Normative

- [DID_METHOD.md] ./DID_METHOD.md
- [WIRE_FORMAT_v3.1.md] ./WIRE_FORMAT_v3.1.md
- [CRYPTO_v3.1.md] ./CRYPTO_v3.1.md
- [RFC 8032] Edwards-Curve Digital Signature Algorithm (EdDSA)
- [RFC 8785] JSON Canonicalization Scheme (JCS)
- [W3C DID Core] https://www.w3.org/TR/did-core/
- [Multibase] https://github.com/multiformats/multibase
- [Multicodec] https://github.com/multiformats/multicodec

### Informative

- [did:wba] https://github.com/w3c/did-extensions/blob/main/methods/wba.json
- [did:web] https://w3c-ccg.github.io/did-method-web/
