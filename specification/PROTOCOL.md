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
DISCOVER_RESPONSE	Response to discovery request
PROPOSAL	Propose a contract
ACCEPT	Accept proposal
REJECT	Reject proposal
COMMIT	Commit to contract
EXECUTE	Execute contract
EXECUTION_RESULT	Result of execution
VERIFY	Request verification
VERIFICATION_RESULT	Verification result
ESCALATE	Escalate to human
DONE	Completion notification
ERROR	Error response
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
State Transition Table
From	Event	To
DISCOVER	DISCOVER	PROPOSE
PROPOSE	ACCEPT	NEGOTIATE
PROPOSE	REJECT	REJECTED
PROPOSE	TIMEOUT	TIMEOUT
NEGOTIATE	COMMIT	COMMIT
NEGOTIATE	REJECT	REJECTED
NEGOTIATE	TIMEOUT	TIMEOUT
COMMIT	EXECUTE	EXECUTE
COMMIT	CANCEL	CANCELLED
COMMIT	TIMEOUT	TIMEOUT
EXECUTE	VERIFY	VERIFY
EXECUTE	FAIL	FAILED
EXECUTE	TIMEOUT	TIMEOUT
VERIFY	DONE	DONE
VERIFY	ESCALATE	ESCALATED
VERIFY	FAIL	FAILED
ESCALATED	RESOLVE	DONE
ESCALATED	REJECT	FAILED
Invalid Transitions
Any transition not listed above is invalid and MUST be rejected.

5. Contract Specification
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
      "action": "analyze",
      "input": { "data": "..." }
    },
    "agent-456": {
      "action": "report",
      "input": { "analysis": "$ref:agent-123.output" }
    }
  },
  "condition": "analysis.confidence > 0.85",
  "on_failure": "escalate",
  "signatures": {
    "agent-123": "base64_signature",
    "agent-456": "base64_signature"
  }
}
6. Error Codes
Code	Description
E001	Invalid message format
E002	Unauthorized sender
E003	Contract validation failed
E004	Capability not available
E005	Timeout occurred
E006	Verification failed
E007	Escalation required
E008	Signature verification failed
E009	Agent not found
E010	Contract not found