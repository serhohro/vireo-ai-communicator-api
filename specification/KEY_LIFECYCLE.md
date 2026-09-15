# Vireo Key Lifecycle Specification

**Version:** 0.1 (Draft)
**Status:** Working Draft
**Date:** 2026-09-15

## 1. Abstract

This document specifies the lifecycle of cryptographic keys used by Vireo agents for identity and signing. It covers key generation, rotation, revocation, expiry, and recovery. The specification is designed to address the "key lifecycle gap" identified in external reviews: without rotation and revocation, a compromised key represents permanent identity theft.

## 2. Key Generation

### 2.1 Algorithm
All Vireo agent identity keys MUST use **Ed25519** (RFC 8032).

### 2.2 DID Derivation
The agent's DID is derived from the public key:
did:vireo:<first-32-hex-chars-of-SHA256(public-key-bytes)>

text

### 2.3 Verification Key ID
The `verification_key_id` MUST be derived from the SHA-256 hash of the raw public key:
Format: vireo-key-<first-16-hex-chars-of-SHA256(public-key)>

text

### 2.4 Private Key Handling
- Private keys MUST NOT appear in any serialized representation (JSON, logs, DID documents).
- Private keys SHOULD be stored in secure enclaves or OS keychains where available.

## 3. Key Rotation

### 3.1 Rotation Triggers
Key rotation MUST occur:
- **Periodically:** Every 90 days (default, configurable).
- **On-demand:** After suspected compromise or security incident.

### 3.2 Rotation Protocol
1. Agent generates new Ed25519 keypair.
2. Agent creates a **rotation proof**: a message signed by the *old* key declaring the new public key.
3. Agent updates its DID document, adding the new key and marking the old key as "rotated".
4. Rotation proof is published alongside the DID document update.

### 3.3 Rotation Proof Format
```json
{
  "type": "VireoKeyRotation",
  "old_key_id": "vireo-key-abc123...",
  "new_key_id": "vireo-key-def456...",
  "new_public_key": "base64...",
  "rotated_at": "2026-09-15T10:00:00Z",
  "signature": "base64..."
}
3.4 Grace Period
Old keys MUST remain valid for signature verification for 7 days after rotation.

After grace period, signatures from old keys MUST be rejected.

4. Key Revocation
4.1 Voluntary Revocation
An agent MAY self-revoke its key by:

Signing a revocation message with the current private key.

Publishing the revocation to its DID document.

Marking key status as revoked.

4.2 Forced Revocation
A DID registry operator MAY force revocation if:

Key compromise is proven.

Agent is confirmed malicious.

4.3 Revocation List
Revoked keys MUST be published in a Revocation List.

Revocation List MUST be signed and distributed.

Verification MUST check Revocation List before accepting signatures.

4.4 Revocation Message Format
json
{
  "type": "VireoKeyRevocation",
  "key_id": "vireo-key-abc123...",
  "reason": "compromise" | "decommission" | "security",
  "revoked_at": "2026-09-15T10:00:00Z",
  "signature": "base64..."
}
5. Key Expiry
5.1 Default TTL
Default key validity: 1 year.

DID documents MAY specify shorter TTL.

5.2 Renewal
Agents SHOULD renew keys 30 days before expiry.

Renewal follows the same protocol as rotation.

5.3 Expired Keys
Signatures from expired keys MUST be rejected.

DID documents MUST NOT accept updates signed with expired keys.

6. Recovery
6.1 Social Recovery (Optional)
Agent MAY designate N-of-M recovery keys.

Recovery requires signatures from M of N designated keys.

6.2 Backup Key (Recommended)
Agents SHOULD maintain a cold-storage backup key.

Backup key MAY be used only for recovery, not routine signing.

6.3 Recovery Protocol
Agent proves loss of primary key via recovery keys.

New keypair generated.

DID document updated with new key.

Old key marked as recovered.

7. Security Considerations
7.1 Key Compromise
Compromised keys MUST be revoked immediately.

All signatures made after compromise time MAY be considered invalid.

7.2 Replay Protection
Nonce replay protection (as specified in Vireo wire format) MUST be maintained across key rotations.

7.3 Log Flooding
Verification failures MUST be logged at DEBUG level only.

Logging at WARNING or higher enables log-flooding attacks.

8. References
RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA)

W3C Decentralized Identifiers (DIDs) v1.0

AgentMesh Identity and Trust Specification v1.0 (Microsoft)

SAR Protocol v0.2