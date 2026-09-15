# did:vireo Method Specification

**Version:** 0.1 (Draft)
**Status:** Working Draft
**Date:** 2026-09-15

## 1. Abstract

`did:vireo` is a DID method for AI agent identity. The identifier is deterministically derived from an Ed25519 public key, enabling self-certifying identity without external registration. This specification covers DID syntax, DID document structure, CRUD operations, and security/privacy considerations.

## 2. Use Case & Requirements

### 2.1 Use Case
AI agents need portable, self-certifying identity to:
- Sign wire messages (Vireo wire format).
- Prove authorship of contracts.
- Establish trust without centralized registration.

### 2.2 Requirements
- Deterministic DID derivation from public key.
- No human KYC required.
- Cross-protocol compatibility (A2A, MCP).
- Key rotation and revocation support.

## 3. DID Syntax

### 3.1 ABNF Grammar

```abnf
vireo-did = "did:vireo:" vireo-id
vireo-id  = 32HEXDIG
3.2 Identifier Derivation
The identifier is derived deterministically from the public key:

text
identifier = LOWERHEX( SHA256(public-key-bytes)[0:16] )
3.3 Example
text
did:vireo:a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234
4. DID Document
4.1 Example DID Document
json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:vireo:a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234",
  "verificationMethod": [{
    "id": "did:vireo:a1b2c3d4...#vireo-key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:vireo:a1b2c3d4...",
    "publicKeyBase64": "base64-encoded-public-key"
  }],
  "authentication": ["did:vireo:a1b2c3d4...#vireo-key-1"],
  "assertionMethod": ["did:vireo:a1b2c3d4...#vireo-key-1"],
  "service": [{
    "id": "did:vireo:a1b2c3d4...#vireo-endpoint",
    "type": "VireoAgentEndpoint",
    "serviceEndpoint": "https://agent.example.com/vireo"
  }]
}
4.2 Key Status
The DID document MAY include key status extensions:

json
{
  "keyStatus": {
    "vireo-key-1": {
      "status": "active" | "rotated" | "revoked",
      "rotatedAt": "2026-09-15T10:00:00Z",
      "expiresAt": "2027-09-15T10:00:00Z"
    }
  }
}
5. CRUD Operations
5.1 Create
Generate Ed25519 keypair.

Derive DID from public key.

Create DID document.

Publish to Vireo DID Registry (or use self-certifying local document).

5.2 Read (Resolve)
Resolution via Vireo DID Registry API, OR

Local construction from public key (self-certifying).

5.3 Update
Updates MUST be signed by the current private key.

Key rotation updates MUST include rotation proof.

Updates to revoked keys MUST be rejected.

5.4 Deactivate
Signed deactivation message.

DID marked as deactivated in registry.

All keys marked as revoked.

6. Security Considerations
6.1 Key Compromise
See KEY_LIFECYCLE.md for rotation/revocation.

Compromised keys MUST be revoked immediately.

6.2 Replay Protection
Nonce replay protection MUST be maintained.

Timestamps MUST be checked.

6.3 Collision Resistance
SHA-256 provides collision resistance.

128-bit identifier space is sufficient for agent-scale identity.

7. Privacy Considerations
7.1 Correlation
DIDs are public by design.

Agents SHOULD use different DIDs for different contexts if correlation is a concern.

7.2 Data Minimization
DID documents SHOULD NOT contain PII.

Sponsor email (if present) SHOULD be a dedicated contact, not personal.

7.3 Operator Privacy
DID registry operators SHOULD NOT log resolution requests.

8. Intellectual Property
This specification is licensed under the Apache License 2.0.

Contributions to this specification are made under the terms of the Apache License 2.0. Implementers are free to use, modify, and distribute this specification in accordance with the license.

9. References
W3C Decentralized Identifiers (DIDs) v1.0

RFC 8032: EdDSA

AgentMesh Identity and Trust Specification v1.0

did:aip Method Specification (reference implementation)