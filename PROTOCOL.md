markdown
# 📡 Vireo Protocol Specification

**Version:** 2.0.1  
**Status:** Draft  
**Last Updated:** 2026-01-15

---

## 1. Overview

Vireo Protocol defines the communication rules for autonomous AI agents to discover, negotiate, execute, and verify tasks.

### Core Principles

1. **Decentralized** — No central authority
2. **Secure** — Cryptographic verification
3. **Deterministic** — Well-defined state machine
4. **Interoperable** — Language-agnostic
5. **Extensible** — Capability-based

---

## 2. Protocol Lifecycle
┌────────────┐
│ DISCOVER │ ← Agents discover each other's capabilities
└─────┬──────┘
│
▼
┌────────────┐
│ PROPOSE │ ← Agent proposes a contract
└─────┬──────┘
│
▼
┌────────────┐
│ NEGOTIATE │ ← Agents negotiate terms
└─────┬──────┘
│
▼
┌────────────┐
│ COMMIT │ ← Agents commit to contract
└─────┬──────┘
│
▼
┌────────────┐
│ EXECUTE │ ← Contract execution
└─────┬──────┘
│
▼
┌────────────┐
│ VERIFY │ ← Cryptographic verification
└─────┬──────┘
│
▼
┌────────────┐
│ DONE │ ← Completion
└────────────┘

text

### Error States

| State | Description |
|-------|-------------|
| **REJECTED** | Proposal/contract rejected |
| **CANCELLED** | Cancelled by one party |
| **FAILED** | Execution failure |
| **ESCALATED** | Escalated for human review |
| **TIMEOUT** | Timeout occurred |

---

## 3. Message Format

All protocol messages follow this structure:

```json
{
  "version": "2.0.1",
  "type": "PROPOSAL | ACCEPT | REJECT | COMMIT | EXECUTE | VERIFY | ESCALATE",
  "message_id": "uuid",
  "timestamp": "2026-01-15T10:30:00Z",
  "sender_id": "agent-123",
  "recipient_id": "agent-456",
  "payload": {
    "contract": { ... },
    "signature": "base64_encoded_signature",
    "data": { ... }
  },
  "metadata": {
    "capabilities": ["analyze", "report"],
    "ttl": 60
  }
}
Message Types
Type	Description
DISCOVER	Request capability discovery
PROPOSAL	Propose a contract
ACCEPT	Accept proposal
REJECT	Reject proposal
COMMIT	Commit to contract
EXECUTE	Execute contract
VERIFY	Request verification
ESCALATE	Escalate to human
4. State Transitions
Valid Transitions
text
DISCOVER → PROPOSE
PROPOSE → ACCEPT | REJECT | TIMEOUT
ACCEPT → COMMIT | TIMEOUT
COMMIT → EXECUTE | CANCELLED | TIMEOUT
EXECUTE → VERIFY | FAILED | TIMEOUT
VERIFY → DONE | ESCALATED | FAILED
ESCALATED → DONE | FAILED
Invalid Transitions
Any transition not listed above is invalid and MUST be rejected.

5. Contract Specification
Contracts are the central mechanism of Vireo protocol.

Contract Structure
json
{
  "contract_id": "uuid",
  "parties": ["agent-123", "agent-456"],
  "terms": {
    "max_tokens": 1000,
    "timeout_sec": 60,
    "max_cost_usd": 10.0,
    "max_rounds": 5
  },
  "obligations": {
    "agent-123": {
      "action": "analyze_image",
      "input": { "image_url": "..." },
      "output": { "format": "json" }
    },
    "agent-456": {
      "action": "report",
      "input": { "analysis": "$ref:agent-123.output" },
      "output": { "format": "json" }
    }
  },
  "signatures": {
    "agent-123": "base64_signature",
    "agent-456": "base64_signature"
  }
}
Contract Validation
Syntax: All required fields present

Semantics: Terms are valid

Capabilities: Agents have required capabilities

Signatures: All parties have signed

6. VERIFY State
The VERIFY state ensures contract execution is cryptographically verifiable.

Verification Process
Collect evidence — Execution logs, outputs, signatures

Validate signatures — All parties' signatures

Verify outputs — Output matches contract specification

Check constraints — Max tokens, cost, time

Produce verification proof — Cryptographic attestation

Verification Failure
If verification fails:

Move to ESCALATED state

Notify all parties

Log failure details

7. ESCALATE State
The ESCALATE state handles issues that require human intervention.

Escalation Triggers
Verification failure

Contract violation

Timeout

Dispute between agents

Unauthorized action

Escalation Process
Generate escalation report — Full context

Notify human operator — Via API or UI

Await decision — ACCEPT, REJECT, MODIFY

Resolve — Based on human decision

8. Trust Bootstrap Protocol
Initial Trust Setup
Identity Generation — Each agent generates Ed25519 keypair

Public Key Registration — Register with discovery service

Challenge-Response — Verify identity ownership

Trust Establishment — Mutual verification

Trust Verification
python
# Trust verification flow
def verify_identity(agent_id, public_key, signature, challenge):
    # 1. Verify signature
    if not verify_signature(public_key, signature, challenge):
        return False
    
    # 2. Check against registry
    if not registry.check_public_key(agent_id, public_key):
        return False
    
    # 3. Verify challenge matches
    if not verify_challenge(agent_id, challenge):
        return False
    
    return True
9. Capability Discovery
Discovery Request
json
{
  "type": "DISCOVER",
  "sender_id": "agent-123",
  "payload": {
    "capabilities_required": ["analyze_image", "report"],
    "constraints": {
      "max_cost_usd": 5.0,
      "max_tokens": 1000
    }
  }
}
Discovery Response
json
{
  "type": "DISCOVER_RESPONSE",
  "sender_id": "agent-456",
  "payload": {
    "capabilities": [
      {
        "name": "analyze_image",
        "description": "Analyze medical images",
        "cost": 1.0,
        "estimated_tokens": 500
      }
    ],
    "accepts_contract": true
  }
}
10. Transport Layer
Redis Transport
python
# Message serialization
class Message:
    def to_dict(self):
        return {
            "version": self.version,
            "type": self.type,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            version=data.get("version", "2.0.1"),
            type=data["type"],
            message_id=data["message_id"],
            timestamp=data["timestamp"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            payload=data["payload"],
            metadata=data.get("metadata", {})
        )
11. Error Codes
Code	Description
E001	Invalid message format
E002	Unauthorized sender
E003	Contract validation failed
E004	Capability not available
E005	Timeout occurred
E006	Verification failed
E007	Escalation required
E008	Signature verification failed
12. Security Considerations
Cryptographic Requirements
Signing: Ed25519 (SHA-512)

Hashing: SHA-256

Encryption: AES-256-GCM (optional)

Attack Vectors
Vector	Mitigation
Replay attack	Message IDs + timestamps
MITM	Signatures + TLS
Identity spoofing	Public key verification
Denial of service	Rate limiting
13. Future Extensions
WASM Runtime: Execute Vireo code in sandboxed environment

MCP Adapter: Integration with Model Context Protocol

A2A Adapter: Compatibility with Google's A2A

Formal Verification: Mathematical proof of contract correctness

References
LANGUAGE.md

AST.md

WIRE_FORMAT.md

CONTRACTS.md

TRUST_BOOTSTRAP.md