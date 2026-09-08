# 📚 Vireo v3.0.0 — API Reference

**Complete API documentation for all endpoints**

---

## Base URL
http://localhost:5000

text

## Protocol Version
Open Wire v3.0.0

text

---

## 📋 Table of Contents

1. [Core Protocol](#1-core-protocol)
2. [Lifecycle States](#2-lifecycle-states)
3. [DID & Trust](#3-did--trust)
4. [Formal Verification](#4-formal-verification)
5. [WASM Runtime](#5-wasm-runtime)
6. [Rust Integration](#6-rust-integration)
7. [MCP (Model Context Protocol)](#7-mcp-model-context-protocol)
8. [LLM Providers](#8-llm-providers)
9. [WebSocket](#9-websocket)
10. [Monitoring](#10-monitoring)
11. [Legacy (v2.x)](#11-legacy-v2x)

---

## 1. Core Protocol

### GET /api/v3/protocol/version

Get protocol version information.

**Response:**
```json
{
  "version": "3.0.0",
  "protocol": "Open Wire v3.0.0",
  "wire_format": "Protobuf + FlatBuffers",
  "features": ["binary_serialization", "canonical_hashing", "ed25519_signatures", "zk_snarks", "formal_verification"]
}
POST /api/v3/agent/register
Register a new agent.

Request Body:

json
{
  "id": "agent-1",
  "name": "Vision Agent",
  "model": "qwen2.5-coder:latest",
  "did": "did:vireo:agent-1"
}
Response:

json
{
  "success": true,
  "agent": {
    "id": "agent-1",
    "name": "Vision Agent",
    "status": "registered",
    "registered_at": "2026-09-06T10:30:00Z"
  }
}
POST /api/v3/agent/{id}/capability
Add a capability to an agent.

Request Body:

json
{
  "name": "analyze_images",
  "description": "Analyze medical images",
  "version": "1.0.0"
}
Response:

json
{
  "success": true,
  "agent": "agent-1",
  "capability": "analyze_images"
}
POST /api/v3/message
Send a message in Open Wire format.

Request Body:

json
{
  "type": "PROPOSE",
  "sender": "agent-1",
  "recipient": "agent-2",
  "payload": {
    "contract_id": "contract-123",
    "terms": {"price": 100}
  }
}
Response:

json
{
  "success": true,
  "message_id": "msg-abc123",
  "type": "PROPOSE",
  "wire_size": 156,
  "timestamp": "2026-09-06T10:30:00Z"
}
POST /api/v3/message/binary
Send a binary message (raw protobuf).

Request: Binary data (application/octet-stream)

Response:

json
{
  "success": true,
  "type": "PROPOSE",
  "sender": "agent-1",
  "recipient": "agent-2",
  "decoded": true
}
2. Lifecycle States
POST /api/v3/discover
Discover agents with specific capabilities.

Request Body:

json
{
  "capabilities": ["analyze_images", "train_model"]
}
Response:

json
{
  "success": true,
  "agents": [
    {
      "id": "agent-1",
      "did": "did:vireo:agent-1",
      "capabilities": ["analyze_images", "train_model"],
      "status": "registered"
    }
  ],
  "total": 1
}
POST /api/v3/propose
Create a contract proposal.

Request Body:

json
{
  "contract_id": "contract-123",
  "parties": ["agent-1", "agent-2"],
  "terms": {
    "max_tokens": 1000,
    "timeout_sec": 60,
    "max_rounds": 10
  },
  "obligations": {
    "agent-1": {
      "action": "analyze_images",
      "input": {"image": "sample.png"}
    },
    "agent-2": {
      "action": "train_model",
      "input": {"data": "$ref.agent-1.result"}
    }
  },
  "condition": "accuracy > 0.95",
  "on_failure": "escalate"
}
Response:

json
{
  "success": true,
  "contract": {
    "id": "contract-123",
    "parties": ["agent-1", "agent-2"],
    "status": "proposed",
    "created_at": "2026-09-06T10:30:00Z"
  }
}
POST /api/v3/negotiate
Negotiate contract terms.

Request Body:

json
{
  "contract_id": "contract-123",
  "proposal": {
    "max_tokens": 1500,
    "timeout_sec": 90
  }
}
Response:

json
{
  "success": true,
  "negotiation_id": "neg-456",
  "status": "accepted"
}
POST /api/v3/commit
Commit and sign a contract.

Request Body:

json
{
  "contract_id": "contract-123",
  "signatures": ["agent-1-sig-abc", "agent-2-sig-def"]
}
Response:

json
{
  "success": true,
  "contract": {
    "id": "contract-123",
    "status": "committed",
    "committed_at": "2026-09-06T10:30:00Z"
  }
}
POST /api/v3/execute
Execute a contract.

Request Body:

json
{
  "contract_id": "contract-123",
  "executor": "agent-1",
  "wasm_module": "base64_encoded_wasm" // optional
}
Response:

json
{
  "success": true,
  "execution_id": "exec-789",
  "result": {
    "status": "executed",
    "output": "Contract executed successfully"
  }
}
POST /api/v3/verify
Verify contract execution.

Request Body:

json
{
  "contract_id": "contract-123",
  "execution_id": "exec-789"
}
Response:

json
{
  "success": true,
  "verification_id": "ver-101",
  "verified": true
}
POST /api/v3/escalate
Escalate a dispute to Guardian Agent.

Request Body:

json
{
  "contract_id": "contract-123",
  "reason": "Execution failed: timeout"
}
Response:

json
{
  "success": true,
  "escalation_id": "esc-112",
  "status": "resolved",
  "resolution": "Guardian Agent resolved the dispute"
}
POST /api/v3/done
Complete the lifecycle.

Request Body:

json
{
  "contract_id": "contract-123"
}
Response:

json
{
  "success": true,
  "status": "done",
  "message": "Contract contract-123 completed"
}
3. DID & Trust
POST /api/v3/did/create
Create a Decentralized Identifier (DID).

Request Body:

json
{
  "name": "agent-1"
}
Response:

json
{
  "success": true,
  "did": "did:vireo:agent-1-abc123",
  "public_key": "ed25519_pk_abc123...",
  "created_at": "2026-09-06T10:30:00Z"
}
POST /api/v3/did/verify
Verify a DID with ZK-SNARK proof.

Request Body:

json
{
  "did": "did:vireo:agent-1-abc123",
  "proof": "zk_snark_proof_base64"
}
Response:

json
{
  "success": true,
  "did": "did:vireo:agent-1-abc123",
  "verified": true
}
POST /api/v3/trust/establish
Establish federated trust between agents.

Request Body:

json
{
  "agent_a": "did:vireo:agent-1",
  "agent_b": "did:vireo:agent-2"
}
Response:

json
{
  "success": true,
  "trust": {
    "agent_a": "did:vireo:agent-1",
    "agent_b": "did:vireo:agent-2",
    "trust_level": "full",
    "established_at": "2026-09-06T10:30:00Z"
  }
}
GET /api/v3/trust/reputation/{did}
Get agent reputation.

Response:

json
{
  "success": true,
  "did": "did:vireo:agent-1",
  "reputation": 0.85
}
POST /api/v3/vc/issue
Issue a Verifiable Credential.

Request Body:

json
{
  "issuer": "did:vireo:trust-authority",
  "subject": "did:vireo:agent-1",
  "claims": {
    "capability": "analyze_images",
    "level": "expert",
    "expires": "2027-12-31"
  }
}
Response:

json
{
  "success": true,
  "vc_id": "vc-123",
  "issued_at": "2026-09-06T10:30:00Z"
}
POST /api/v3/vc/verify
Verify a Verifiable Credential.

Request Body:

json
{
  "vc_id": "vc-123"
}
Response:

json
{
  "success": true,
  "verified": true,
  "claims": {
    "capability": "analyze_images",
    "level": "expert"
  }
}
4. Formal Verification
POST /api/v3/formal/verify
Formally verify a contract using SMT solver.

Request Body:

json
{
  "contract": {
    "id": "contract-123",
    "parties": ["agent-1", "agent-2"],
    "terms": {"max_tokens": 1000}
  },
  "properties": ["safety", "liveness", "fairness"]
}
Response:

json
{
  "success": true,
  "verified": true,
  "properties": ["safety", "liveness", "fairness"],
  "details": {
    "safety": true,
    "liveness": true,
    "fairness": true,
    "solver": "Z3 v4.12.0",
    "runtime": "0.234s"
  }
}
POST /api/v3/formal/check
Check contract invariants.

Request Body:

json
{
  "contract": {
    "id": "contract-123",
    "parties": ["agent-1", "agent-2"]
  },
  "invariants": [
    "max_tokens >= 0",
    "timeout_sec > 0",
    "parties != []"
  ]
}
Response:

json
{
  "success": true,
  "all_valid": true,
  "results": {
    "max_tokens >= 0": true,
    "timeout_sec > 0": true,
    "parties != []": true
  }
}
5. WASM Runtime
POST /api/v3/wasm/compile
Compile Vireo code to WASM.

Request Body:

json
{
  "code": "agent vision { capability analyze { ... } }"
}
Response:

json
{
  "success": true,
  "wasm_size": 1024,
  "format": "wasm"
}
POST /api/v3/wasm/execute
Execute a WASM module.

Request Body:

json
{
  "wasm_module": "base64_encoded_wasm",
  "params": {"input": "data"}
}
Response:

json
{
  "success": true,
  "result": {"status": "success", "output": "analysis_result"}
}
POST /api/v3/wasm/upload
Upload a WASM file.

Request: Multipart form with file field

Response:

json
{
  "success": true,
  "filename": "agent.wasm",
  "size": 1024,
  "module_id": "wasm-123"
}
6. Rust Integration
GET /api/v3/rust/status
Get Rust backend status.

Response:

json
{
  "success": true,
  "available": true,
  "version": "1.82.0",
  "features": ["native", "wasm"]
}
POST /api/v3/rust/execute
Execute code via Rust runtime.

Request Body:

json
{
  "code": "fn main() { println!(\"Hello from Rust!\"); }"
}
Response:

json
{
  "success": true,
  "result": "Hello from Rust!",
  "runtime": "0.001s"
}
7. MCP (Model Context Protocol)
GET /api/v3/mcp/tools
List available MCP tools.

Response:

json
{
  "success": true,
  "tools": [
    {
      "name": "analyze_data",
      "description": "Analyze data using AI",
      "input_schema": {
        "type": "object",
        "properties": {
          "data": {"type": "array"},
          "method": {"type": "string"}
        }
      }
    }
  ],
  "total": 1
}
POST /api/v3/mcp/invoke
Invoke an MCP tool.

Request Body:

json
{
  "tool": "analyze_data",
  "params": {
    "data": [1, 2, 3, 4, 5],
    "method": "statistical"
  }
}
Response:

json
{
  "success": true,
  "tool": "analyze_data",
  "result": {
    "mean": 3.0,
    "std": 1.58,
    "min": 1,
    "max": 5
  }
}
POST /api/v3/mcp/context
Get MCP context for an agent.

Request Body:

json
{
  "agent_id": "agent-1"
}
Response:

json
{
  "success": true,
  "context": {
    "agent": "agent-1",
    "capabilities": ["analyze_data"],
    "tools": ["analyze_data"],
    "active_contracts": ["contract-123"]
  }
}
8. LLM Providers
GET /api/providers
List available LLM providers.

Response:

json
{
  "success": true,
  "providers": ["ollama", "mistral", "openai", "gemini", "claude"],
  "models": {
    "ollama": ["qwen2.5-coder:latest", "llama3.1:latest"],
    "mistral": ["mistral-large-latest", "mistral-medium-latest"],
    "openai": ["gpt-4", "gpt-4-turbo"]
  }
}
POST /api/mistral/generate
Generate text using Mistral AI.

Request Body:

json
{
  "prompt": "Explain Vireo v3.0.0",
  "model": "mistral-large-latest",
  "max_tokens": 500,
  "temperature": 0.7
}
Response:

json
{
  "success": true,
  "provider": "mistral",
  "model": "mistral-large-latest",
  "result": "Vireo v3.0.0 is..."
}
POST /api/mistral/chat
Chat with Mistral AI.

Request Body:

json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "model": "mistral-large-latest",
  "max_tokens": 200
}
Response:

json
{
  "success": true,
  "provider": "mistral",
  "model": "mistral-large-latest",
  "result": "Hello! How can I help you?"
}
9. WebSocket
Connection
text
ws://localhost:5000/socket.io/
Events
Client → Server
Event	Payload	Description
message	{type, sender, recipient, payload}	Send message
negotiate	{contract_id, proposal}	Negotiate
execute	{contract_id}	Execute
verify	{contract_id, execution_id}	Verify
Server → Client
Event	Payload	Description
connected	{version, protocol}	Connection established
message_ack	{status, timestamp}	Message received
negotiate_ack	{status, counter}	Negotiation accepted
execute_ack	{status, result}	Execution complete
verify_ack	{status, verified}	Verification complete
10. Monitoring
GET /api/health
Health check.

Response:

json
{
  "status": "healthy",
  "version": "3.0.0",
  "name": "Vireo AI Communicator API",
  "protocol": "Open Wire v3.0.0",
  "features": {
    "core": true,
    "wasm": true,
    "formal": true,
    "mcp": true
  }
}
GET /api/v3/metrics
Performance metrics.

Response:

json
{
  "success": true,
  "agents": 5,
  "contracts": 10,
  "negotiations": 3,
  "executions": 7,
  "verifications": 5,
  "escalations": 1,
  "protocol_states": 15,
  "identities": 5,
  "trust_relationships": 3,
  "version": "3.0.0",
  "uptime": "1h 23m 45s"
}
GET /api/v3/agents
List all agents.

Response:

json
{
  "success": true,
  "agents": {
    "agent-1": {
      "id": "agent-1",
      "name": "Vision Agent",
      "status": "registered",
      "capabilities": ["analyze_images"]
    }
  },
  "total": 1
}
GET /api/v3/contracts
List all contracts.

Response:

json
{
  "success": true,
  "contracts": {
    "contract-123": {
      "id": "contract-123",
      "parties": ["agent-1", "agent-2"],
      "status": "done"
    }
  },
  "total": 1
}
11. Legacy (v2.x)
POST /api/v2/contracts
Create contract (v2.x compatible).

Request Body:

json
{
  "parties": ["agent-1", "agent-2"],
  "terms": {"max_tokens": 1000}
}
Response:

json
{
  "success": true,
  "contract_id": "contract-123"
}
POST /api/v2/contracts/{id}/execute
Execute contract (v2.x compatible).

Response:

json
{
  "success": true,
  "execution": {
    "contract_id": "contract-123",
    "status": "executed"
  }
}
POST /api/v2/agents/trust
Establish trust (v2.x compatible).

Request Body:

json
{
  "agent_a": "agent-1",
  "agent_b": "agent-2"
}
📊 Error Codes
Code	Description
200	Success
400	Bad Request — Invalid input
404	Not Found — Resource doesn't exist
409	Conflict — State conflict
422	Unprocessable Entity — Validation failed
500	Internal Server Error
📚 Additional Resources
QUICKSTART.md — Quick start guide

TUTORIAL.md — Complete tutorial

WIRE_FORMAT.md — Wire format spec

PROTOCOL.md — Protocol spec

SECURITY.md — Security guide

🌿 Vireo v3.0.0 — The World's First AI-to-AI Communication Language