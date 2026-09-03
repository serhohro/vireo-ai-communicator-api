# 🔐 Vireo Security Specification

**Version:** 2.0.2
**Last Updated:** 2026-09-03

---

## 1. Overview

Vireo is designed with security as a first-class concern. This document specifies the security model, cryptographic requirements, and trust mechanisms for all Vireo-compatible implementations.

### 1.1 Core Principles

| Principle | Description |
|-----------|-------------|
| **Zero Trust** | No implicit trust between agents |
| **Cryptographic Verification** | All actions are verifiable |
| **Defense in Depth** | Multiple layers of security |
| **Least Privilege** | Agents have minimal required permissions |
| **Auditability** | All actions are logged and auditable |

### 1.2 RFC 2119 Keywords

| Keyword | Meaning |
|---------|---------|
| **MUST** | Absolute requirement |
| **MUST NOT** | Absolute prohibition |
| **SHOULD** | Recommended |
| **SHOULD NOT** | Not recommended |
| **MAY** | Optional |

---

## 2. Cryptographic Requirements

### 2.1 Ed25519 Signatures

All Vireo messages **MUST** be signed with Ed25519 (RFC 8032).

| Parameter | Requirement |
|-----------|-------------|
| **Algorithm** | Ed25519 |
| **Private Key Size** | 32 bytes |
| **Public Key Size** | 32 bytes (64 hex chars) |
| **Signature Size** | 64 bytes (128 hex chars) |
| **Signing** | Deterministic (no randomness required) |

**Key Validation:**

```python
def validate_public_key(public_key_hex: str) -> bool:
    """Validate Ed25519 public key."""
    if len(public_key_hex) != 64:
        return False
    try:
        bytes.fromhex(public_key_hex)
        return True
    except ValueError:
        return False
2.2 Canonical Serialization
Messages MUST be serialized canonically before signing:

JSON: Sort keys alphabetically

Exclude: signature field

Encoding: UTF-8

python
def canonical_serialize(data: dict) -> bytes:
    """Serialize data for signing."""
    sorted_data = {k: data[k] for k in sorted(data.keys()) if k != "signature"}
    return json.dumps(sorted_data, separators=(",", ":"), sort_keys=True).encode("utf-8")
3. Trust Bootstrap Protocol
3.1 Protocol Flow
text
Agent A                                    Agent B
   │                                          │
   │ 1. HELLO (DID_A, public_key_A)           │
   │──────────────────────────────────────────>│
   │                                          │
   │ 2. HELLO_ACK (DID_B, public_key_B)       │
   │<──────────────────────────────────────────│
   │                                          │
   │ 3. CHALLENGE (nonce_A)                   │
   │──────────────────────────────────────────>│
   │                                          │
   │ 4. CHALLENGE_RESP (signature_B)          │
   │<──────────────────────────────────────────│
   │                                          │
   │ 5. VERIFY (success/fail)                 │
   │──────────────────────────────────────────>│
3.2 Whitelist
Agents MAY maintain a whitelist of trusted DIDs:

python
whitelist: Dict[str, bytes] = {
    "agent-vision": b"public_key_bytes",
    "agent-training": b"public_key_bytes"
}
3.3 Challenge-Response
MUST include:

Nonce: 32 bytes (64 hex chars) generated securely

Timestamp: ISO 8601 UTC

Signature: Ed25519 signature of nonce + timestamp

python
def verify_challenge(nonce: str, timestamp: str, signature: bytes, public_key: bytes) -> bool:
    message = (nonce + timestamp).encode("utf-8")
    return ed25519_verify(public_key, signature, message)
4. Authentication & Authorization
4.1 Authentication Flow
text
Identity → Authentication → Authorization → Capability Verification → Execution
4.2 Capability-Based Authorization
Agents MUST declare their capabilities:

vireo
agent Vision {
    capability image_analysis
    capability object_detection
}
4.3 Contract-Based Authorization
Contracts define resource limits and permissions:

vireo
contract Agreement {
    max_tokens: Int = 1000
    timeout_sec: Int = 30
    allowed_actions: List[String] = ["train_model", "predict"]
}
5. Key Management
5.1 Key Rotation
MUST support key rotation:

python
def rotate_key(agent_id: str, old_public_key_hex: str, new_public_key_hex: str, signature_hex: str) -> bool:
    # Verify signature from old key
    # Update whitelist with new key
    pass
5.2 Key Revocation
MUST support key revocation:

python
def revoke_key(agent_id: str) -> bool:
    # Remove agent from whitelist
    pass
5.3 Key Storage
SHOULD use secure key storage:

Environment	Recommended Storage
Development	.env files (encrypted)
Production	HSM / KMS
Cloud	AWS KMS / Azure Key Vault
6. Attack Mitigation
Attack	Mitigation	Requirement
Identity Spoofing	Ed25519 signatures + DID verification	MUST
Replay Attacks	Nonce + timestamp validation	MUST
Message Tampering	Signatures	MUST
Capability Forgery	Whitelist + verification	MUST
Resource Exhaustion	Contract limits	MUST
Injection Attacks	AST validation	MUST
Denial of Service	Rate limiting	SHOULD
Compromised LLM	Sandboxing	SHOULD
7. Audit Logging
7.1 Required Fields
Each audit log entry MUST include:

Field	Description
timestamp	ISO 8601 timestamp
conversation_id	Conversation identifier
agent_id	Agent identifier
intent	Message intent
contract	Contract details (if applicable)
signature	Message signature
result	Execution result
verified	Verification status
7.2 Audit Log Format
json
{
  "timestamp": "2026-09-03T12:00:00Z",
  "conversation_id": "conv-1234",
  "agent_id": "agent-vision",
  "intent": "PROPOSE",
  "contract": { "max_tokens": 1000 },
  "signature": "a1b2c3d4...",
  "result": { "status": "success" },
  "verified": true
}
7.3 Log Retention
Environment	Retention Period
Development	30 days
Production	90 days
Compliance	7 years
8. Incident Response
8.1 Incident Types
Type	Severity	Response
Key compromise	🔴 Critical	Immediate rotation, notify all
Contract violation	🔴 High	Escalate, review contract
Authentication failure	🟠 Medium	Investigate source
Suspicious activity	🟡 Low	Monitor, log
8.2 Response Process
python
def handle_incident(incident_type: str, details: dict):
    # 1. Log incident
    log_incident(incident_type, details)
    
    # 2. Assess severity
    severity = assess_severity(incident_type)
    
    # 3. Take action
    if severity == "critical":
        revoke_all_trust()
        rotate_keys()
    elif severity == "high":
        create_escalation(incident_type, details)
    else:
        monitor_incident(incident_type, details)
    
    # 4. Notify affected parties
    notify_parties(incident_type, severity)
9. Compliance
9.1 GDPR
Data minimization: Collect only necessary data

Right to deletion: Support agent deletion

Encryption: All personal data encrypted

Audit trails: All access logged

9.2 EU AI Act
Transparency: All decisions explainable

Human oversight: Override mechanisms

Risk assessment: Regular security reviews

Documentation: Complete documentation required

10. Conformance Tests
All Vireo-compatible implementations MUST pass these security tests:

Test ID	Description	Requirement
T-SEC-001	Ed25519 signature verification	MUST
T-SEC-002	Trust Bootstrap Protocol	MUST
T-SEC-003	Contract validation	MUST
T-SEC-004	Replay attack protection	MUST
T-SEC-005	Key rotation	SHOULD
T-SEC-006	Message tampering detection	MUST
T-SEC-007	Nonce validation	MUST
T-SEC-008	Capability verification	MUST
📄 Full conformance suite →

11. Future Enhancements
Feature	Description	Target Version
Zero-Knowledge Proofs	Privacy-preserving verification	v3.0.0
Post-Quantum Cryptography	Quantum-resistant algorithms	v3.0.0
Hardware Security Modules	Secure key storage	v2.2.0
Formal Verification	Mathematical proof of security	v3.0.0
WASM Sandboxing	Secure execution environment	v2.2.0
12. References
Ed25519 RFC 8032

DID Core

JSON Schema

Vireo Protocol

Vireo Conformance Tests

🌿 Vireo — The World's First AI-to-AI Communication Language. 🚀