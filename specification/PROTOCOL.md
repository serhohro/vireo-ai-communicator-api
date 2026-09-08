markdown
# 📡 Vireo Protocol Specification

**Version:** 2.0.1  
**Status:** Draft  
**Last Updated:** 2026-09-03

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
  "timestamp": "2026-09-03T10:30:00Z",
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
DONE	Completion
CANCEL	Cancel contract
TIMEOUT	Timeout occurred
4. State Transitions
Valid Transitions
text
DISCOVER → PROPOSE
PROPOSE → ACCEPT | REJECT | TIMEOUT | NEGOTIATE
NEGOTIATE → PROPOSE | ACCEPT | REJECT | TIMEOUT
ACCEPT → COMMIT | TIMEOUT
COMMIT → EXECUTE | CANCELLED | TIMEOUT
EXECUTE → VERIFY | FAILED | TIMEOUT
VERIFY → DONE | ESCALATED | FAILED | TIMEOUT
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
    "max_rounds": 5,
    "verify_timeout_sec": 15
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
  "condition": "verified == true",
  "on_failure": "escalate",
  "signatures": {
    "agent-123": "base64_signature",
    "agent-456": "base64_signature"
  }
}
Contract Validation
Check	Description
Syntax	All required fields present
Semantics	Terms are valid
Capabilities	Agents have required capabilities
Signatures	All parties have signed
6. VERIFY State
The VERIFY state ensures contract execution is cryptographically verifiable.

Verification Process
Collect evidence — Execution logs, outputs, signatures

Validate signatures — All parties' signatures

Verify outputs — Output matches contract specification

Check constraints — Max tokens, cost, time

Produce verification proof — Cryptographic attestation

Verification Conditions
json
{
  "verify": "result.confidence > 0.95 AND result.sources >= 5"
}
Verification Failure
If verification fails:

Move to ESCALATED state

Notify all parties

Log failure details

7. ESCALATE State
The ESCALATE state handles issues that require human intervention.

Escalation Triggers
Trigger	Description
Verification failure	Contract verification failed
Contract violation	Terms violated
Timeout	Timeout occurred
Dispute	Disagreement between agents
Unauthorized action	Unauthorized action detected
Escalation Process
Generate escalation report — Full context

Notify human operator — Via API or UI

Await decision — ACCEPT, REJECT, MODIFY

Resolve — Based on human decision

Escalation Types
text
ESCALATED
 ├── verification_failed
 ├── trust_below_threshold
 ├── capability_missing
 ├── contract_ambiguous
 ├── timeout
 ├── policy_violation
 └── human_approval_required
8. Trust Bootstrap Protocol
Initial Trust Setup
Identity Generation — Each agent generates Ed25519 keypair

Public Key Registration — Register with discovery service

Challenge-Response — Verify identity ownership

Trust Establishment — Mutual verification

Trust Verification
python
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
Trust Levels
Level	Description	Requirements
None	No trust established	None
Partial	Identity verified	Challenge-response passed
Full	Fully trusted	Challenge-response + key rotation
Bridged	Trusted via intermediary	Trust chain verified
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
10.1 Redis Transport
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
10.2 WebSocket Transport
javascript
// Client connects to WebSocket server
const ws = new WebSocket('ws://localhost:8765/vireo');

ws.onopen = () => {
    console.log('Connected to Vireo WebSocket server');
    
    // Register agent
    ws.send(JSON.stringify({
        type: 'REGISTER',
        agent_id: 'agent-vision',
        capabilities: ['image_analysis', 'object_detection']
    }));
};

// Send message
ws.send(JSON.stringify({
    version: '2.0.1',
    type: 'PROPOSE',
    message_id: 'msg-123',
    sender_id: 'agent-vision',
    recipient_id: 'agent-training',
    payload: {
        contract: { max_tokens: 1000 }
    }
}));

// Receive message
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    handleMessage(message);
};
10.3 gRPC Transport
protobuf
// vireo.proto
syntax = "proto3";

package vireo;

service VireoService {
    rpc SendMessage (MessageRequest) returns (MessageResponse);
    rpc StreamMessages (stream MessageRequest) returns (stream MessageResponse);
    rpc Negotiate (stream NegotiateRequest) returns (stream NegotiateResponse);
}

message MessageRequest {
    string version = 1;
    string type = 2;
    string message_id = 3;
    string timestamp = 4;
    string sender_id = 5;
    string recipient_id = 6;
    bytes payload = 7;
    bytes signature = 8;
}

message MessageResponse {
    bool success = 1;
    string error = 2;
    bytes response = 3;
}
python
import grpc
import vireo_pb2
import vireo_pb2_grpc

# Create channel
channel = grpc.insecure_channel('localhost:50051')
stub = vireo_pb2_grpc.VireoServiceStub(channel)

# Send message
request = vireo_pb2.MessageRequest(
    version='2.0.1',
    type='PROPOSE',
    message_id='msg-123',
    sender_id='agent-vision',
    recipient_id='agent-training',
    payload=b'{"contract": {"max_tokens": 1000}}'
)

response = stub.SendMessage(request)
11. Metrics and Monitoring
11.1 Key Metrics
Metric	Type	Description
messages_total	Counter	Total messages sent/received
message_latency_ms	Histogram	Message processing latency
active_agents	Gauge	Number of active agents
contracts_total	Counter	Total contracts created
contracts_verified	Counter	Verified contracts
contracts_escalated	Counter	Escalated contracts
errors_total	Counter	Total errors by type
11.2 Prometheus Integration
python
from prometheus_client import Counter, Histogram, Gauge

messages_total = Counter('vireo_messages_total', 'Total messages', ['type'])
message_latency = Histogram('vireo_message_latency_ms', 'Message latency', ['type'])
active_agents = Gauge('vireo_active_agents', 'Active agents')
contracts_total = Counter('vireo_contracts_total', 'Total contracts', ['status'])
11.3 Health Checks
Check	Description
/health	Basic health check
/health/ready	Readiness check
/health/live	Liveness check
/metrics	Prometheus metrics
11.4 Alerting Rules
yaml
groups:
  - name: vireo_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        annotations:
          summary: "High error rate detected"
      
      - alert: LowSuccessRate
        expr: rate(contracts_verified[5m]) / rate(contracts_total[5m]) < 0.9
        annotations:
          summary: "Verification success rate below 90%"
12. Complete Message Examples
12.1 Full Negotiation Flow
Discovery:

json
{
  "version": "2.0.1",
  "type": "DISCOVER",
  "message_id": "msg-001",
  "timestamp": "2026-09-03T10:00:00Z",
  "sender_id": "agent-vision",
  "recipient_id": "*",
  "payload": {
    "capabilities_required": ["analyze_image", "generate_report"],
    "constraints": {
      "max_tokens": 5000,
      "max_cost_usd": 10.0
    }
  }
}
Discovery Response:

json
{
  "version": "2.0.1",
  "type": "DISCOVER_RESPONSE",
  "message_id": "msg-002",
  "timestamp": "2026-09-03T10:00:01Z",
  "sender_id": "agent-training",
  "recipient_id": "agent-vision",
  "payload": {
    "capabilities": [
      {
        "name": "analyze_image",
        "description": "Analyze images using ResNet",
        "cost": 2.0,
        "estimated_tokens": 500
      },
      {
        "name": "generate_report",
        "description": "Generate analysis report",
        "cost": 1.0,
        "estimated_tokens": 300
      }
    ],
    "accepts_contract": true,
    "trust_level": 0.85
  }
}
Proposal:

json
{
  "version": "2.0.1",
  "type": "PROPOSAL",
  "message_id": "msg-003",
  "timestamp": "2026-09-03T10:00:05Z",
  "sender_id": "agent-vision",
  "recipient_id": "agent-training",
  "payload": {
    "contract": {
      "contract_id": "contract-001",
      "parties": ["agent-vision", "agent-training"],
      "terms": {
        "max_tokens": 1000,
        "timeout_sec": 60,
        "max_cost_usd": 5.0,
        "max_rounds": 3,
        "verify_timeout_sec": 15
      },
      "obligations": {
        "agent-training": {
          "action": "analyze_image",
          "input": {"image_url": "https://example.com/image.png"},
          "output": {"format": "json"}
        }
      },
      "condition": "verified == true",
      "on_failure": "escalate",
      "verify": "result.confidence > 0.95"
    },
    "signature": "base64_encoded_signature"
  }
}
Accept:

json
{
  "version": "2.0.1",
  "type": "ACCEPT",
  "message_id": "msg-004",
  "timestamp": "2026-09-03T10:00:06Z",
  "sender_id": "agent-training",
  "recipient_id": "agent-vision",
  "payload": {
    "contract_id": "contract-001",
    "accepted_terms": true,
    "signature": "base64_encoded_signature"
  }
}
Commit:

json
{
  "version": "2.0.1",
  "type": "COMMIT",
  "message_id": "msg-005",
  "timestamp": "2026-09-03T10:00:07Z",
  "sender_id": "agent-vision",
  "recipient_id": "agent-training",
  "payload": {
    "contract_id": "contract-001",
    "commitment": "commit",
    "signature": "base64_encoded_signature"
  }
}
Execute:

json
{
  "version": "2.0.1",
  "type": "EXECUTE",
  "message_id": "msg-006",
  "timestamp": "2026-09-03T10:00:10Z",
  "sender_id": "agent-training",
  "recipient_id": "agent-vision",
  "payload": {
    "contract_id": "contract-001",
    "result": {
      "status": "success",
      "output": {
        "analysis": "The image contains a cat",
        "confidence": 0.97,
        "labels": ["cat", "animal", "pet"]
      }
    },
    "execution_time": 2.5,
    "tokens_used": 450,
    "signature": "base64_encoded_signature"
  }
}
Verify:

json
{
  "version": "2.0.1",
  "type": "VERIFY",
  "message_id": "msg-007",
  "timestamp": "2026-09-03T10:00:11Z",
  "sender_id": "agent-vision",
  "recipient_id": "agent-training",
  "payload": {
    "contract_id": "contract-001",
    "verification": {
      "verified": true,
      "proof": "verification_proof_001",
      "details": {
        "signatures_valid": true,
        "confidence_met": true,
        "tokens_within_limit": true,
        "time_within_limit": true
      }
    },
    "signature": "base64_encoded_signature"
  }
}
Done:

json
{
  "version": "2.0.1",
  "type": "DONE",
  "message_id": "msg-008",
  "timestamp": "2026-09-03T10:00:12Z",
  "sender_id": "agent-vision",
  "recipient_id": "agent-training",
  "payload": {
    "contract_id": "contract-001",
    "final_status": "completed",
    "signature": "base64_encoded_signature"
  }
}
12.2 Failure Flow
Reject:

json
{
  "version": "2.0.1",
  "type": "REJECT",
  "message_id": "msg-009",
  "timestamp": "2026-09-03T10:00:08Z",
  "sender_id": "agent-training",
  "recipient_id": "agent-vision",
  "payload": {
    "contract_id": "contract-001",
    "reason": "Tokens limit exceeded",
    "signature": "base64_encoded_signature"
  }
}
Escalate:

json
{
  "version": "2.0.1",
  "type": "ESCALATE",
  "message_id": "msg-010",
  "timestamp": "2026-09-03T10:00:12Z",
  "sender_id": "agent-vision",
  "recipient_id": "human-operator",
  "payload": {
    "contract_id": "contract-001",
    "reason": "Verification failed: confidence 0.92 < 0.95",
    "evidence": {
      "result": "The image contains a cat",
      "confidence": 0.92,
      "contract": { "max_tokens": 1000 }
    },
    "escalation_type": "verification_failed",
    "signature": "base64_encoded_signature"
  }
}
Timeout:

json
{
  "version": "2.0.1",
  "type": "TIMEOUT",
  "message_id": "msg-011",
  "timestamp": "2026-09-03T10:01:05Z",
  "sender_id": "agent-vision",
  "recipient_id": "agent-training",
  "payload": {
    "contract_id": "contract-001",
    "reason": "Timeout after 60 seconds",
    "signature": "base64_encoded_signature"
  }
}
13. Error Codes
Code	Description
E001	Invalid message format
E002	Unauthorized sender
E003	Contract validation failed
E004	Capability not available
E005	Timeout occurred
E006	Verification failed
E007	Escalation required
E008	Signature verification failed
E009	Invalid state transition
E010	Max rounds exceeded
E011	Trust verification failed
E012	Resource limit exceeded
14. Security Considerations
Cryptographic Requirements
Requirement	Algorithm
Signing	Ed25519 (SHA-512)
Hashing	SHA-256
Encryption	AES-256-GCM (optional)
Attack Vectors
Vector	Mitigation
Replay attack	Message IDs + timestamps
MITM	Signatures + TLS
Identity spoofing	Public key verification
Denial of service	Rate limiting
Message tampering	Signatures
Nonce reuse	Unique nonce per message
15. Future Extensions
Extension	Description	Status
WASM Runtime	Execute Vireo code in sandboxed environment	🔵 Planned
MCP Adapter	Integration with Model Context Protocol	🔵 Planned
A2A Adapter	Compatibility with Google's A2A	🔵 Planned
Formal Verification	Mathematical proof of contract correctness	🔵 Planned
Zero-Knowledge Proofs	Privacy-preserving verification	🔵 Planned
16. References
LANGUAGE.md

AST.md

WIRE_FORMAT.md

CONTRACTS.md

TRUST_BOOTSTRAP.md

SECURITY.md

