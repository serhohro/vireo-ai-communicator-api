# did:vireo Method Specification

**Version:** 3.4.0
**Status:** Draft
**Editors:** Serhii Hromyko (serhohro)
**License:** Apache 2.0

---

## 1. Abstract

`did:vireo` is a DID method for AI agents and services that need a
resolvable, self-certifying identifier anchored in an HTTPS-reachable
DID Document. The method follows the `did:wba` resolution pattern:
the method-specific identifier encodes a domain and path, and the
DID Document is retrieved from a well-known URL derived from that
identifier.

This document normatively defines the DID syntax, the DID Document
structure, the resolution algorithm, CRUD operations, and the
security and privacy considerations for the method.

---

## 2. Use Case & Requirements

Vireo is an AI-to-AI communication language and wire protocol. Agents
exchange signed messages (Ed25519) with contract-lifecycle intents
(DISCOVER, PROPOSE, NEGOTIATE, COMMIT, EXECUTE, VERIFY, DONE, ...).
Every message is addressed by a sender DID and a recipient DID.

Requirements for the identifier:

1. **Resolvable.** A resolver must be able to obtain the public key
   from the DID alone, without an out-of-band channel.
2. **Self-certifying.** The DID Document must bind the identifier to
   the key material used for signing.
3. **Normative.** There must be exactly one resolution model — no
   "registry OR local construction" ambiguity.
4. **Rotatable.** Key rotation must be expressible as a signed update
   to the DID Document, with a verifiable chain of rotation proofs.
5. **Web-compatible.** Resolution must reuse HTTPS and existing DID
   Document conventions (W3C DID Core, `did:web`-style URL mapping).

The `did:vireo` method satisfies all five requirements by mapping the
method-specific identifier to an HTTPS URL and reusing the normative
`publicKeyMultibase` verification-method representation.

---

## 3. DID Syntax

### 3.1 ABNF Grammar

```abnf
vireo-did       = "did:vireo:" domain-name *( ":" path-segment )

domain-name     = domain-label *( "." domain-label )
domain-label    = alnum *( alnum / "-" ) alnum
                / alnum
                ; must not start or end with "-"

path-segment    = 1*( lowercase / DIGIT / "-" / "_" / "." )
                ; lowercase ASCII only

lowercase       = %x61-7A  ; a-z
alnum           = lowercase / DIGIT
DIGIT           = %x30-39  ; 0-9
```

**Normative constraints:**

- All characters in `path-segment` MUST be lowercase. Uppercase
  characters are not permitted, and resolvers MUST reject
  identifiers that contain them.
- `domain-name` MUST be a valid DNS name per RFC 1035.
- A port, if present, MUST be percent-encoded as `%3A` inside the
  domain component (e.g.
  `did:vireo:agent.example.com%3A8443:agents:alice`).
- The total length of the DID MUST NOT exceed 2048 characters.

### 3.2 Identifier Derivation

The method-specific identifier is **not** derived from a hash of the
public key. It is a human-readable, domain-based locator:

```
did:vireo:<domain>:<path...>
```

The public key is obtained by resolving the DID (Section 5), not by
decoding the identifier. This removes the previous truncated-hash
design, which was neither resolvable nor self-certifying.

### 3.3 Examples

```
did:vireo:agent.example.com:agents:alice
did:vireo:agent.example.com:agents:bob
did:vireo:registry.vireo.ai:agents:did%3Akey-1
did:vireo:agents.acme.com:supply-chain:buyer-42
```

Each of these resolves to an HTTPS URL:

```
did:vireo:agent.example.com:agents:alice
  -> https://agent.example.com/agents/alice/did.json

did:vireo:agents.acme.com:supply-chain:buyer-42
  -> https://agents.acme.com/supply-chain/buyer-42/did.json
```

---

## 4. DID Document

### 4.1 JSON-LD Context

The DID Document MUST use the following `@context`:

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    {
      "keyStatus": "https://vireo.ai/ns#keyStatus",
      "VireoAgentEndpoint": "https://vireo.ai/ns#VireoAgentEndpoint",
      "Ed25519VerificationKey2020": "https://w3id.org/security#Ed25519VerificationKey2020"
    }
  ]
}
```

The custom terms `keyStatus` and `VireoAgentEndpoint` are defined here
so that conforming JSON-LD processors do not reject the document.

### 4.2 DID Document Structure

A conforming DID Document has the following shape:

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    {
      "keyStatus": "https://vireo.ai/ns#keyStatus",
      "VireoAgentEndpoint": "https://vireo.ai/ns#VireoAgentEndpoint",
      "Ed25519VerificationKey2020": "https://w3id.org/security#Ed25519VerificationKey2020"
    }
  ],
  "id": "did:vireo:agent.example.com:agents:alice",
  "verificationMethod": [
    {
      "id": "did:vireo:agent.example.com:agents:alice#key-1",
      "type": "Ed25519VerificationKey2020",
      "controller": "did:vireo:agent.example.com:agents:alice",
      "publicKeyMultibase": "z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
    }
  ],
  "authentication": [
    "did:vireo:agent.example.com:agents:alice#key-1"
  ],
  "assertionMethod": [
    "did:vireo:agent.example.com:agents:alice#key-1"
  ],
  "service": [
    {
      "id": "did:vireo:agent.example.com:agents:alice#vireo-endpoint",
      "type": "VireoAgentEndpoint",
      "serviceEndpoint": "https://agent.example.com/vireo"
    }
  ],
  "keyStatus": "active"
}
```

### 4.3 Verification Method

The verification method MUST use the normative
`publicKeyMultibase` property. The `publicKeyBase64` property is
**not** defined and MUST NOT be used.

For Ed25519 keys, `publicKeyMultibase` is constructed as follows:

1. Take the 32-byte raw Ed25519 public key (compressed Edwards
   point).
2. Prepend the multicodec prefix for Ed25519 public keys: `0xed01`.
3. Base58btc-encode the resulting 34 bytes.
4. Prepend the character `z` (multibase prefix for base58btc).

Formally:

```
publicKeyMultibase = "z" || base58btc( 0xed01 || ed25519_pubkey_bytes )
```

Where `ed25519_pubkey_bytes` is exactly 32 bytes, and the byte order
is the standard Ed25519 compressed-point encoding (RFC 8032).

### 4.4 Service Endpoints

A DID Document MAY include a `service` entry of type
`VireoAgentEndpoint`. The `serviceEndpoint` MUST be an HTTPS URL. If
present, it is the transport endpoint for Vireo wire messages
addressed to this DID.

---

## 5. DID Resolution (Normative)

### 5.1 Resolution Algorithm

There is exactly **one** normative resolution model. The previous
"Registry API OR local construction" language is withdrawn.

```
Input:  did-string (a DID conforming to Section 3.1)
Output: DID Document, or a resolution error

Algorithm:

1. Parse did-string per the ABNF in Section 3.1.
   On parse failure, return error `invalidDid`.

2. Extract the method-specific identifier:
     method-specific-id = did-string after "did:vireo:"
   Split it on ":" into:
     domain = first segment
     path   = remaining segments (one or more)

3. Percent-decode the domain component (so "%3A" becomes ":").

4. Construct the resolution URL:
     url = "https://" || domain || "/" || join(path, "/") || "/did.json"

5. Perform an HTTPS GET on `url` with header:
     Accept: application/did+json

6. If the HTTP status is 200:
     a. Parse the response body as JSON.
     b. Validate the DID Document:
          - `id` equals did-string
          - `@context` includes "https://www.w3.org/ns/did/v1"
          - `verificationMethod` is present and non-empty
          - each verificationMethod has `id`, `type`, `controller`
          - `publicKeyMultibase` is present and well-formed
     c. If validation fails, return error `invalidDidDocument`.
     d. If `deactivated` is true, return error `deactivated`.
     e. Return the DID Document.

7. If the HTTP status is 404, return error `notFound`.

8. If the Content-Type is not `application/did+json` or
   `application/json`, return error `representationNotSupported`.

9. For any other HTTP status, return error `notFound`.

10. For network failures, return error `notFound`.
```

### 5.2 Error Codes

| Code | Meaning |
|------|---------|
| `invalidDid` | The DID does not conform to the ABNF in Section 3.1. |
| `notFound` | The DID Document could not be retrieved (HTTP 404, network failure, or other non-200 status). |
| `representationNotSupported` | The server returned a Content-Type other than `application/did+json` or `application/json`. |
| `invalidDidDocument` | The retrieved JSON is not a valid DID Document per Section 4. |
| `deactivated` | The DID Document has `"deactivated": true`. |
| `methodNotSupported` | Reserved for future method versions. |

### 5.3 Resolution Is Normative

A resolver MUST implement the algorithm in Section 5.1. A resolver
MUST NOT construct the DID Document locally from a public key
supplied out of band. Local construction is not a conforming
resolution model.

---

## 6. CRUD Operations

### 6.1 Create

**Inputs:**

- `domain` — DNS name controlled by the subject
- `path` — one or more lowercase path segments
- `publicKeyMultibase` — an Ed25519 public key in multibase form
- `serviceEndpoint` (optional) — HTTPS URL

**Outputs:**

- `did` — the DID string
- `didDocumentUrl` — the HTTPS URL where the DID Document is
  published
- `didDocument` — the DID Document

**Algorithm:**

1. Construct the DID as `did:vireo:<domain>:<path...>`.
2. Construct the DID Document per Section 4.
3. Publish the DID Document at the URL from Section 5.1 step 4.
4. The publisher MUST serve `Content-Type: application/did+json`.

**Errors:**

- `invalidDomain` — domain is not a valid DNS name
- `invalidPath` — path contains uppercase or invalid characters
- `invalidPublicKey` — `publicKeyMultibase` is not a valid Ed25519
  key
- `alreadyExists` — a DID Document already exists at the URL
- `unauthorized` — the publisher does not control the domain

### 6.2 Read (Resolve)

**Inputs:**

- `did` — the DID string

**Outputs:**

- `didDocument` — the resolved DID Document

**Algorithm:**

- Execute the algorithm in Section 5.1.

**Errors:**

- All error codes from Section 5.2.

### 6.3 Update

**Inputs:**

- `did` — the DID string
- `newDidDocument` — the updated DID Document
- `signature` — Ed25519 signature over the canonicalized
  `newDidDocument` (RFC 8785 JCS) by the current authentication key

**Outputs:**

- `didDocument` — the updated DID Document

**Algorithm:**

1. Resolve the current DID Document (Section 5.1).
2. Extract the current authentication key from
   `verificationMethod` referenced by `authentication`.
3. Verify `signature` against the canonicalized `newDidDocument`
   (RFC 8785 JCS) using the current authentication key.
4. If verification fails, return error `invalidSignature`.
5. Validate `newDidDocument` per Section 4.
6. Publish `newDidDocument` at the same URL, overwriting the
   previous document.

**Errors:**

- `invalidSignature` — signature does not verify
- `invalidDidDocument` — new document fails validation
- `unauthorized` — caller does not control the publication URL
- All error codes from Section 5.2

**Note:** Key rotation is an Update in which `newDidDocument`
changes the `verificationMethod`. The rotation proof is the Update
signature itself. See KEY_LIFECYCLE.md for the full rotation
protocol.

### 6.4 Deactivate

**Inputs:**

- `did` — the DID string
- `signature` — Ed25519 signature over the canonicalized
  deactivation payload by the current authentication key

**Deactivation payload:**

```json
{
  "did": "did:vireo:agent.example.com:agents:alice",
  "deactivated": true,
  "timestamp": "2026-09-20T12:00:00Z"
}
```

**Outputs:**

- `didDocument` — the deactivated DID Document

**Algorithm:**

1. Resolve the current DID Document (Section 5.1).
2. Extract the current authentication key.
3. Verify `signature` over the canonicalized (RFC 8785 JCS)
   deactivation payload.
4. Publish a DID Document at the same URL with `"deactivated": true`.
5. Subsequent resolution of this DID returns error `deactivated`.

**Errors:**

- `invalidSignature` — signature does not verify
- `unauthorized` — caller does not control the publication URL
- All error codes from Section 5.2

---

## 7. Key Lifecycle Integration

Key rotation, revocation, and expiry are normatively defined in
`KEY_LIFECYCLE.md`. That document specifies:

- the signed rotation payload and its canonicalization (RFC 8785
  JCS)
- the publication mechanism (an Update to the DID Document)
- the validation algorithm (chain of rotation proofs)
- error handling for compromised keys

The `did:vireo` method relies on `KEY_LIFECYCLE.md` for all key
management semantics. A resolver that implements this document but
not `KEY_LIFECYCLE.md` is not fully conforming.

---

## 8. Security Considerations

### 8.1 No Truncation

The method-specific identifier does **not** embed a truncated SHA-256
hash. The previous design used
`did:vireo:<first-32-hex-of-SHA256(pubkey)>`, which provided only
~64-bit generic collision resistance and was not resolvable. That
design is withdrawn.

The new identifier is domain-based and human-readable. Integrity of
the binding between the DID and the public key is provided by:

- **TLS** on the HTTPS resolution channel, and
- **The DID Document itself**, which contains the public key.

There is no truncation, so there is no reduction in collision
resistance. Full SHA-256 (or BLAKE2b-256 for wire-format hashing)
is used where hashing is required, without truncation.

### 8.2 Replay Protection

Vireo wire messages include a 16-byte random nonce and a 64-bit
millisecond timestamp (see WIRE_FORMAT_v3.1.md). These prevent replay
of signed messages. The DID Document itself does not carry a nonce;
replay of DID Document updates is prevented by requiring each Update
to be signed by the current authentication key and by the
monotonicity rules in KEY_LIFECYCLE.md.

### 8.3 Key Compromise

If an authentication key is compromised, the subject MUST publish a
new DID Document signed by the compromised key (if still under
control) or, if not, follow the recovery procedure in
KEY_LIFECYCLE.md. The compromise window is bounded by the resolution
cache TTL; resolvers SHOULD use a short TTL (recommended: 300
seconds) and MUST respect HTTP cache directives.

### 8.4 Domain Control

The security of a `did:vireo` identifier depends on control of the
DNS domain and the HTTPS endpoint at the resolution URL. If an
attacker gains control of the domain or the TLS certificate, they
can publish a forged DID Document. This is the same trust model as
`did:web` and `did:wba`; it is appropriate for agents that already
rely on TLS for transport security.

### 8.5 No Local Construction

Resolvers MUST NOT construct the DID Document from a public key
supplied out of band. Doing so would bypass the normative resolution
model and allow a resolver to accept a DID Document that the subject
never published.

---

## 9. Privacy Considerations

- The DID contains a domain and path that may reveal the subject's
  organizational affiliation. Subjects that require unlinkability
  SHOULD use a dedicated domain or path that does not correlate with
  other identifiers.
- Resolution reveals the resolver's IP address to the domain's HTTPS
  endpoint. Resolvers that require network privacy SHOULD use a
  proxy or Tor.
- The DID Document MAY be served with standard HTTP caching headers.
  Subjects SHOULD set a short `Cache-Control` TTL to limit the
  window during which a compromised key remains trusted.
- The `service` endpoint, if present, reveals the transport endpoint
  for the agent. Subjects that do not wish to publish a transport
  endpoint SHOULD omit the `service` entry.

---

## 10. Intellectual Property

This specification is published under the Apache License, Version 2.0.

The `did:vireo` method name and the `VireoAgentEndpoint` service type
are intended for unrestricted use by conforming implementations.

---

## 11. References

### Normative

- [W3C DID Core] Decentralized Identifiers (DIDs) v1.0,
  https://www.w3.org/TR/did-core/
- [RFC 1035] Domain Names — Implementation and Specification
- [RFC 8032] Edwards-Curve Digital Signature Algorithm (EdDSA)
- [RFC 8785] JSON Canonicalization Scheme (JCS)
- [Multibase] https://github.com/multiformats/multibase
- [Multicodec] https://github.com/multiformats/multicodec
- [Ed25519VerificationKey2020]
  https://w3id.org/security#Ed25519VerificationKey2020

### Informative

- [did:wba] https://github.com/w3c/did-extensions/blob/main/methods/wba.json
- [did:web] https://w3c-ccg.github.io/did-method-web/
- [KEY_LIFECYCLE.md] ./KEY_LIFECYCLE.md
- [VERIFY.md] ./VERIFY.md
- [WIRE_FORMAT_v3.1.md] ./WIRE_FORMAT_v3.1.md
