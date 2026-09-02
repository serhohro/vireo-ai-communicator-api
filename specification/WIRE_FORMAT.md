```markdown
# 🔌 Vireo Wire Format Specification

**Version:** 2.0.1  
**Status:** Draft  
**Last Updated:** 2026-01-15

---

## 1. Overview

The Wire Format defines how Vireo messages are serialized for transmission between agents.

### Goals

1. **Language-agnostic** — Serializable in any language
2. **Compact** — Minimal overhead
3. **Self-describing** — Can be parsed without external schema
4. **Versioned** — Supports protocol evolution

---

## 2. Serialization Formats

### Primary Format: JSON

JSON is the primary wire format for simplicity and universal support.

```json
{
  "version": "2.0.1",
  "type": "PROPOSAL",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-15T10:30:00Z",
  "sender_id": "agent-123",
  "recipient_id": "agent-456",
  "payload": {
    "contract": {
      "contract_id": "contract-789",
      "parties": ["agent-123", "agent-456"],
      "terms": {
        "max_tokens": 1000,
        "timeout_sec": 60
      },
      "obligations": {
        "agent-123": {
          "action": "analyze",
          "input": {"image": "s3://image.jpg"}
        }
      }
    },
    "signature": "base64_encoded_ed25519_signature"
  },
  "metadata": {
    "capabilities": ["analyze", "report"],
    "ttl": 300
  }
}
Alternative Format: Protocol Buffers
For high-performance scenarios, Protocol Buffers can be used.

protobuf
syntax = "proto3";

message Message {
  string version = 1;
  MessageType type = 2;
  string message_id = 3;
  string timestamp = 4;
  string sender_id = 5;
  string recipient_id = 6;
  bytes payload = 7;
  map<string, string> metadata = 8;
}

enum MessageType {
  DISCOVER = 0;
  PROPOSAL = 1;
  ACCEPT = 2;
  REJECT = 3;
  COMMIT = 4;
  EXECUTE = 5;
  VERIFY = 6;
  ESCALATE = 7;
  DONE = 8;
}
3. Message Structure
Header Fields
Field	Type	Required	Description
version	string	✅	Protocol version (e.g., "2.0.1")
type	string	✅	Message type (see below)
message_id	string	✅	UUID for deduplication
timestamp	string	✅	ISO 8601 timestamp
sender_id	string	✅	Unique agent ID
recipient_id	string	❌	Optional (broadcast if missing)
payload	object	✅	Message-specific data
metadata	object	❌	Additional metadata
signature	string	❌	Ed25519 signature
Message Types
Type	Description	Payload
DISCOVER	Discover capabilities	capabilities: string[], constraints: object
DISCOVER_RESPONSE	Discovery response	capabilities: object[]
PROPOSAL	Propose contract	contract: Contract
ACCEPT	Accept proposal	proposal_id: string
REJECT	Reject proposal	proposal_id: string, reason: string
COMMIT	Commit to contract	contract_id: string, signatures: object
EXECUTE	Execute contract	contract_id: string, inputs: object
EXECUTION_RESULT	Execution result	contract_id: string, outputs: object
VERIFY	Request verification	contract_id: string
VERIFICATION_RESULT	Verification result	contract_id: string, verified: boolean, proof: string
ESCALATE	Escalate issue	contract_id: string, reason: string, context: object
DONE	Completion	contract_id: string
ERROR	Error response	code: string, message: string
4. Contract Serialization
Contract Object
json
{
  "contract_id": "uuid",
  "parties": ["agent-123", "agent-456"],
  "terms": {
    "max_tokens": 1000,
    "timeout_sec": 60,
    "max_cost_usd": 10.0,
    "max_rounds": 5,
    "deadline": "2026-01-16T10:30:00Z"
  },
  "obligations": {
    "agent-123": {
      "action": "analyze_image",
      "input": {"image_url": "s3://...", "model": "resnet50"},
      "output": {"result": "json"}
    }
  },
  "condition": "result.confidence > 0.85",
  "on_failure": "escalate",
  "signatures": {
    "agent-123": "base64_signature"
  }
}
5. Discovery Protocol
Discovery Request
json
{
  "version": "2.0.1",
  "type": "DISCOVER",
  "message_id": "uuid",
  "timestamp": "2026-01-15T10:30:00Z",
  "sender_id": "agent-123",
  "payload": {
    "capabilities_required": ["analyze_image", "report"],
    "constraints": {
      "max_cost_usd": 5.0,
      "max_tokens": 1000
    },
    "max_results": 5
  }
}
Discovery Response
json
{
  "version": "2.0.1",
  "type": "DISCOVER_RESPONSE",
  "message_id": "uuid",
  "timestamp": "2026-01-15T10:30:01Z",
  "sender_id": "agent-456",
  "recipient_id": "agent-123",
  "payload": {
    "capabilities": [
      {
        "name": "analyze_image",
        "description": "Analyze medical images",
        "cost": 1.0,
        "estimated_tokens": 500,
        "timeout_sec": 30
      },
      {
        "name": "report",
        "description": "Generate reports",
        "cost": 0.5,
        "estimated_tokens": 200,
        "timeout_sec": 10
      }
    ],
    "accepts_contracts": true,
    "max_contracts": 5,
    "public_key": "base64_ed25519_pubkey"
  }
}
6. Error Messages
Error Object
json
{
  "version": "2.0.1",
  "type": "ERROR",
  "message_id": "uuid",
  "timestamp": "2026-01-15T10:30:00Z",
  "sender_id": "agent-456",
  "recipient_id": "agent-123",
  "payload": {
    "code": "E003",
    "message": "Contract validation failed",
    "details": {
      "field": "terms.max_tokens",
      "reason": "Must be positive integer"
    },
    "original_message_id": "msg-789"
  }
}
Error Codes
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
E011	Insufficient resources
E012	Rate limit exceeded
7. Signatures
Signing Algorithm
python
# Ed25519 signing
import hashlib
from cryptography.hazmat.primitives import ed25519

def sign_message(payload: dict, private_key: bytes) -> str:
    # 1. Canonicalize payload (sorted keys)
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 2. Hash payload
    digest = hashlib.sha256(canonical.encode()).digest()
    
    # 3. Sign with Ed25519
    signature = private_key.sign(digest)
    
    # 4. Base64 encode
    return base64.b64encode(signature).decode('utf-8')

def verify_message(payload: dict, signature: str, public_key: bytes) -> bool:
    # 1. Canonicalize payload
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 2. Hash payload
    digest = hashlib.sha256(canonical.encode()).digest()
    
    # 3. Decode signature
    sig_bytes = base64.b64decode(signature)
    
    # 4. Verify with Ed25519
    try:
        public_key.verify(sig_bytes, digest)
        return True
    except:
        return False
8. Versioning
Version Format
text
MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)
Version Negotiation
json
{
  "version": "2.0.1",
  "type": "DISCOVER",
  "payload": {
    "supports": ["2.0.1", "2.0.0"],
    "preferred": "2.0.1"
  }
}
9. Compression
Optional Compression
Messages can be compressed using gzip or zstd.

json
{
  "version": "2.0.1",
  "compression": "gzip",
  "payload": "base64_encoded_compressed_data"
}
10. Examples
Complete Negotiation Flow
json
// 1. DISCOVER
{
  "type": "DISCOVER",
  "sender_id": "buyer",
  "payload": {"capabilities_required": ["sell"]}
}

// 2. DISCOVER_RESPONSE
{
  "type": "DISCOVER_RESPONSE",
  "sender_id": "seller",
  "recipient_id": "buyer",
  "payload": {"capabilities": [{"name": "sell", "cost": 10}]}
}

// 3. PROPOSAL
{
  "type": "PROPOSAL",
  "sender_id": "buyer",
  "recipient_id": "seller",
  "payload": {
    "contract": {
      "parties": ["buyer", "seller"],
      "terms": {"max_cost_usd": 8},
      "obligations": {"seller": {"action": "sell", "input": {"item": "laptop"}}}
    }
  }
}

// 4. ACCEPT
{
  "type": "ACCEPT",
  "sender_id": "seller",
  "recipient_id": "buyer",
  "payload": {"proposal_id": "prop-123"}
}

// 5. COMMIT
{
  "type": "COMMIT",
  "sender_id": "buyer",
  "recipient_id": "seller",
  "payload": {
    "contract_id": "contract-456",
    "signatures": {"buyer": "sig123"}
  }
}

// 6. EXECUTE
{
  "type": "EXECUTE",
  "sender_id": "seller",
  "recipient_id": "buyer",
  "payload": {
    "contract_id": "contract-456",
    "inputs": {"item": "laptop"}
  }
}

// 7. EXECUTION_RESULT
{
  "type": "EXECUTION_RESULT",
  "sender_id": "seller",
  "recipient_id": "buyer",
  "payload": {
    "contract_id": "contract-456",
    "outputs": {"sold": true, "price": 8}
  }
}

// 8. VERIFY
{
  "type": "VERIFY",
  "sender_id": "buyer",
  "recipient_id": "seller",
  "payload": {"contract_id": "contract-456"}
}

// 9. VERIFICATION_RESULT
{
  "type": "VERIFICATION_RESULT",
  "sender_id": "seller",
  "recipient_id": "buyer",
  "payload": {
    "contract_id": "contract-456",
    "verified": true,
    "proof": "base64_proof"
  }
}

// 10. DONE
{
  "type": "DONE",
  "sender_id": "buyer",
  "recipient_id": "seller",
  "payload": {"contract_id": "contract-456"}
}