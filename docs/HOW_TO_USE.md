# 🌿 How to Work with Vireo v3.0.0 — Complete Guide

**Version:** 3.0.0  
**Last Updated:** 2026-09-06  
**Protocol:** Open Wire v3.0.0

---

## 📋 Table of Contents

1. [Installation](#1-installation)
2. [Starting the Server](#2-starting-the-server)
3. [Vireo v3.0.0 Overview](#3-vireo-v300-overview)
4. [Working with Agents](#4-working-with-agents)
5. [Open Wire Protocol](#5-open-wire-protocol)
6. [Lifecycle States](#6-lifecycle-states)
7. [DIDs & Federated Trust](#7-dids--federated-trust)
8. [Formal Verification](#8-formal-verification)
9. [WASM Runtime](#9-wasm-runtime)
10. [Rust SDK](#10-rust-sdk)
11. [MCP (Model Context Protocol)](#11-mcp-model-context-protocol)
12. [LLM Providers](#12-llm-providers)
13. [WebSocket Real-time](#13-websocket-real-time)
14. [API Endpoints](#14-api-endpoints)
15. [Examples](#15-examples)
16. [Migration from v2.x](#16-migration-from-v2x)
17. [FAQ](#17-faq)

---

## 1. Installation

### Requirements
- **Python 3.9+**
- **Rust** (optional, for native performance)
- **Node.js 18+** (optional, for TypeScript SDK)
- **Redis** (optional, for distributed agents)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-4.git
cd vireo-ai-communicator-4

# 2. Install Python dependencies
pip install -e ".[all]"

# 3. Install Rust SDK (optional)
cd sdk/rust
cargo build --release
cd ../..

# 4. Install TypeScript SDK (optional)
cd sdk/typescript
npm install
npm run build
cd ../..

# 5. Configure .env
cp .env.example .env
# Edit .env with your configuration

# 6. Start Redis (if using)
redis-server
2. Starting the Server
Method 1: Quick Start (Recommended)
bash
# Windows
start_vireo.bat

# Linux/macOS
./start_vireo.sh
Method 2: Python Only
bash
python api/server.py
Method 3: With Rust Backend
bash
# Build Rust SDK
cd sdk/rust && cargo build --release && cd ../..
# Run with Rust support
python api/server.py --rust-enabled
Method 4: With WASM
bash
# Build WASM
./scripts/build_wasm.sh
# Run with WASM support
python api/server.py --wasm-enabled
After Starting
text
🌿 VIREO API SERVER v3.0.0
📍 Server:    http://localhost:5000
📚 API Docs:  http://localhost:5000/api/docs
📡 WebSocket: ws://localhost:5000/socket.io/
🔐 Health:    http://localhost:5000/api/health

🚀 V3.0.0 Features:
   ✅ Open Wire Protocol (Protobuf/FlatBuffers)
   ✅ Full Lifecycle: DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE
   ✅ DID-based Federated Trust
   ✅ Formal Verification (SMT)
   ✅ WASM Runtime
   ✅ MCP (Model Context Protocol)
   ✅ WebSocket Real-time
3. Vireo v3.0.0 Overview
What's New in v3.0.0
Feature	v2.x	v3.0.0
Protocol	JSON	Binary (Protobuf/FlatBuffers)
Runtime	Python only	Python + Rust + WASM
Trust	Whitelist	DIDs + ZK-SNARKs + Federated
Verification	Basic	Formal (SMT)
Performance	Interpreted	JIT + WASM + GPU
Browser	❌	✅ (WASM)
SDK	Python	Python + Rust + TypeScript
Architecture
text
┌─────────────────────────────────────────────────┐
│              Vireo v3.0.0                       │
├─────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  Python  │ │   Rust   │ │ TypeScript│      │
│  │   SDK    │ │   SDK    │ │   SDK    │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘      │
│       │            │            │              │
│  ┌────▼────────────▼────────────▼────┐        │
│  │      Open Wire Protocol           │        │
│  │    (Protobuf / FlatBuffers)      │        │
│  └────┬─────────────────────────────┘        │
│       │                                       │
│  ┌────▼─────────────────────────────┐        │
│  │       Vireo Runtime Core         │        │
│  │  ┌──────────┐ ┌──────────┐     │        │
│  │  │ Language │ │   JIT    │     │        │
│  │  │  Parser  │ │ Compiler │     │        │
│  │  └──────────┘ └──────────┘     │        │
│  └────┬─────────────────────────────┘        │
│       │                                       │
│  ┌────▼─────────────────────────────┐        │
│  │     Execution Environments       │        │
│  │  ┌──────────┐ ┌──────────┐     │        │
│  │  │  Native  │ │   WASM   │     │        │
│  │  │  Runner  │ │ Runtime  │     │        │
│  │  └──────────┘ └──────────┘     │        │
│  └─────────────────────────────────┘        │
└─────────────────────────────────────────────────┘
4. Working with Agents
Create an Agent (v3.0.0)
Via API
bash
curl -X POST http://localhost:5000/api/v3/agent/register \
  -H "Content-Type: application/json" \
  -d '{
    "id": "agent-1",
    "name": "Vision Agent",
    "model": "qwen2.5-coder:latest",
    "did": "did:vireo:agent-1"
  }'
Via Python SDK
python
from protocol.agent import Agent

agent = Agent(
    id="agent-1",
    name="Vision Agent",
    model="qwen2.5-coder:latest"
)
agent.register()
Via Rust SDK
rust
use vireo::Agent;

let agent = Agent::new("agent-1")
    .with_name("Vision Agent")
    .register();
Add Capability
bash
curl -X POST http://localhost:5000/api/v3/agent/agent-1/capability \
  -H "Content-Type: application/json" \
  -d '{
    "name": "analyze_images",
    "description": "Analyze medical images",
    "version": "1.0.0"
  }'
List Agents
bash
curl http://localhost:5000/api/v3/agents
5. Open Wire Protocol
What is Open Wire Protocol?
Binary protocol using Protobuf/FlatBuffers

10x faster than JSON

75% smaller messages

Canonical hashing for verification

Cross-language support

Message Format
protobuf
message Envelope {
    bytes id = 1;
    string sender = 2;
    string recipient = 3;
    uint64 timestamp = 4;
    oneof payload {
        DiscoveryMessage discover = 5;
        ProposalMessage propose = 6;
        NegotiationMessage negotiate = 7;
        CommitmentMessage commit = 8;
        ExecutionMessage execute = 9;
        VerificationMessage verify = 10;
        EscalationMessage escalate = 11;
    }
    bytes signature = 12;
    bytes proof = 13;
}
Send Binary Message
bash
# JSON message (will be serialized to binary)
curl -X POST http://localhost:5000/api/v3/message \
  -H "Content-Type: application/json" \
  -d '{
    "type": "PROPOSE",
    "sender": "agent-1",
    "recipient": "agent-2",
    "payload": {
      "contract_id": "contract-123",
      "terms": {"price": 100}
    }
  }'

# Binary message (raw protobuf)
curl -X POST http://localhost:5000/api/v3/message/binary \
  -H "Content-Type: application/octet-stream" \
  --data-binary @message.bin
Using Python
python
from core.protocol.wire import WireFormat
from core.protocol.message import Message

# Create message
msg = Message(
    type="PROPOSE",
    sender="agent-1",
    recipient="agent-2",
    payload={"contract_id": "123"}
)

# Serialize to binary
wire_data = WireFormat.serialize(msg)

# Deserialize from binary
restored = WireFormat.deserialize(wire_data)
Using Rust
rust
use vireo::protocol::{Message, WireFormat};

let msg = Message::propose("agent-1", "agent-2")
    .with_payload(json!({"contract_id": "123"}));

let wire_data = WireFormat::serialize(&msg);
let restored = WireFormat::deserialize(&wire_data);
6. Lifecycle States
Complete Lifecycle
text
DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE
    │          │           │          │         │         │
    ├→ REJECTED ├→ REJECTED ├→ CANCELLED ├→ FAILED ├→ ESCALATED
    └→ TIMEOUT  └→ TIMEOUT  └→ TIMEOUT   └→ TIMEOUT
1. DISCOVER — Find Agents
bash
curl -X POST http://localhost:5000/api/v3/discover \
  -H "Content-Type: application/json" \
  -d '{"capabilities": ["analyze_images", "train_model"]}'
2. PROPOSE — Create Proposal
bash
curl -X POST http://localhost:5000/api/v3/propose \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "contract-123",
    "parties": ["agent-1", "agent-2"],
    "terms": {"max_tokens": 1000, "timeout_sec": 60}
  }'
3. NEGOTIATE — Negotiate Terms
bash
curl -X POST http://localhost:5000/api/v3/negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "contract-123",
    "proposal": {"max_tokens": 1500}
  }'
4. COMMIT — Sign & Commit
bash
curl -X POST http://localhost:5000/api/v3/commit \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "contract-123",
    "signatures": ["agent-1-sig", "agent-2-sig"]
  }'
5. EXECUTE — Execute Contract
bash
curl -X POST http://localhost:5000/api/v3/execute \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "contract-123",
    "executor": "agent-1"
  }'
6. VERIFY — Verify Execution
bash
curl -X POST http://localhost:5000/api/v3/verify \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "contract-123",
    "execution_id": "exec-456"
  }'
7. DONE — Complete
bash
curl -X POST http://localhost:5000/api/v3/done \
  -H "Content-Type: application/json" \
  -d '{"contract_id": "contract-123"}'
7. DIDs & Federated Trust
What are DIDs?
Decentralized Identifiers (DID)

Self-sovereign identity

No central authority

ZK-SNARK proofs for privacy

Create DID
bash
curl -X POST http://localhost:5000/api/v3/did/create \
  -H "Content-Type: application/json" \
  -d '{"name": "agent-1"}'
Response
json
{
  "success": true,
  "did": "did:vireo:agent-1-abc123",
  "public_key": "ed25519_pk_abc123...",
  "created_at": "2026-09-06T10:30:00Z"
}
Establish Trust
bash
curl -X POST http://localhost:5000/api/v3/trust/establish \
  -H "Content-Type: application/json" \
  -d '{
    "agent_a": "did:vireo:agent-1",
    "agent_b": "did:vireo:agent-2"
  }'
Check Reputation
bash
curl http://localhost:5000/api/v3/trust/reputation/did:vireo:agent-1
Verifiable Credentials (VC)
bash
# Issue VC
curl -X POST http://localhost:5000/api/v3/vc/issue \
  -H "Content-Type: application/json" \
  -d '{
    "issuer": "did:vireo:trust-authority",
    "subject": "did:vireo:agent-1",
    "claims": {"capability": "analyze_images", "level": "expert"}
  }'

# Verify VC
curl -X POST http://localhost:5000/api/v3/vc/verify \
  -H "Content-Type: application/json" \
  -d '{"vc_id": "vc-123"}'
8. Formal Verification
What is Formal Verification?
Mathematical proof of contract correctness

Uses SMT solvers (Z3, CVC5)

Proves safety, liveness, fairness

Catches bugs before execution

Verify Contract
bash
curl -X POST http://localhost:5000/api/v3/formal/verify \
  -H "Content-Type: application/json" \
  -d '{
    "contract": {
      "id": "contract-123",
      "parties": ["agent-1", "agent-2"],
      "terms": {"max_tokens": 1000}
    },
    "properties": ["safety", "liveness", "fairness"]
  }'
Response
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
Using Python
python
from core.protocol.formal_verifier import FormalVerifier

verifier = FormalVerifier()
verified = verifier.verify_contract(contract)

if verified:
    print("✅ Contract is mathematically correct")
else:
    print("❌ Contract has issues:", verifier.get_errors())
9. WASM Runtime
What is WASM Runtime?
Run Vireo agents in the browser

Edge computing support

Lightning-fast startup

Memory safe

Compile Vireo to WASM
bash
curl -X POST http://localhost:5000/api/v3/wasm/compile \
  -H "Content-Type: application/json" \
  -d '{
    "code": "agent vision { capability analyze { ... } }"
  }'
Execute WASM
bash
curl -X POST http://localhost:5000/api/v3/wasm/execute \
  -H "Content-Type: application/json" \
  -d '{
    "wasm_module": "base64_encoded_wasm",
    "params": {"input": "image_data"}
  }'
Browser Example
html
<!-- Use in browser -->
<script type="module">
import init from './web/wasm/vireo.js';

const { VireoAgent } = await init();

const agent = new VireoAgent('agent-1');
await agent.connect('ws://localhost:5000');
await agent.propose({ contract_id: '123' });
</script>
Build WASM Locally
bash
# Build WASM
./scripts/build_wasm.sh

# Output: web/wasm/vireo_bg.wasm, web/wasm/vireo.js
10. Rust SDK
Why Rust?
50x faster than Python

Memory safe by design

Native WASM compilation

Production ready

Installation
toml
# Cargo.toml
[dependencies]
vireo = { git = "https://github.com/serhohro/vireo-ai-communicator-4" }
Example Usage
rust
use vireo::{Agent, Protocol, WireFormat};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create agent
    let agent = Agent::new("rust-agent-1")
        .with_did("did:vireo:rust-agent-1")
        .register()
        .await?;
    
    // Create proposal
    let proposal = agent.propose(
        "agent-2",
        json!({
            "contract_id": "contract-123",
            "terms": {"max_tokens": 1000}
        })
    ).await?;
    
    // Negotiate
    let contract = agent.negotiate(&proposal).await?;
    
    // Commit
    let committed = agent.commit(&contract).await?;
    
    // Execute
    let result = agent.execute(&committed).await?;
    
    println!("✅ Contract executed: {:?}", result);
    Ok(())
}
Performance Comparison
Operation	Python	Rust	Speedup
Serialize	500µs	10µs	50x
Deserialize	800µs	15µs	53x
Sign	2ms	0.05ms	40x
Verify	3ms	0.07ms	43x
11. MCP (Model Context Protocol)
What is MCP?
Standard for LLM tool integration

Discover, invoke, and manage tools

Context sharing between agents

List MCP Tools
bash
curl http://localhost:5000/api/v3/mcp/tools
Invoke MCP Tool
bash
curl -X POST http://localhost:5000/api/v3/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "analyze_data",
    "params": {"data": [1, 2, 3, 4, 5]}
  }'
Get MCP Context
bash
curl -X POST http://localhost:5000/api/v3/mcp/context \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-1"}'
12. LLM Providers
Supported Providers (v3.0.0)
Provider	Models	Type
Ollama	qwen2.5-coder:latest, llama3.1:latest, mistral:latest	🆓 Local
Mistral AI	mistral-large-latest, mistral-medium-latest, open-mistral-7b	🇪🇺 European
OpenAI	gpt-4, gpt-4-turbo, gpt-3.5-turbo	💰 Paid
Gemini	gemini-1.5-pro, gemini-1.5-flash	🌟 Google
Claude	claude-3-sonnet-20241022, claude-3-haiku	💰 Anthropic
DeepSeek	deepseek-chat, deepseek-coder	🇨🇳 Chinese
List Providers
bash
curl http://localhost:5000/api/providers
Generate with Mistral
bash
curl -X POST http://localhost:5000/api/mistral/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain Vireo v3.0.0 protocol",
    "model": "mistral-large-latest",
    "max_tokens": 500
  }'
13. WebSocket Real-time
Connect to WebSocket
javascript
// Browser
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('✅ Connected to Vireo v3.0.0');
});

socket.on('message', (data) => {
    console.log('📨 Message:', data);
});

// Send message
socket.emit('message', {
    type: 'PROPOSE',
    sender: 'agent-1',
    recipient: 'agent-2',
    payload: { contract_id: '123' }
});
WebSocket Events
Event	Direction	Description
connect	Server → Client	Connection established
message	Both	Send/receive messages
negotiate	Both	Negotiate contracts
execute	Both	Execute contracts
verify	Both	Verify executions
disconnect	Server → Client	Disconnected
14. API Endpoints
v3.0.0 Endpoints
Method	URL	Description
Core Protocol		
GET	/api/v3/protocol/version	Protocol version
POST	/api/v3/message	Send message
POST	/api/v3/message/binary	Send binary message
Lifecycle		
POST	/api/v3/discover	Discover agents
POST	/api/v3/propose	Create proposal
POST	/api/v3/negotiate	Negotiate
POST	/api/v3/commit	Commit contract
POST	/api/v3/execute	Execute contract
POST	/api/v3/verify	Verify execution
POST	/api/v3/escalate	Escalate dispute
POST	/api/v3/done	Complete lifecycle
DID & Trust		
POST	/api/v3/did/create	Create DID
POST	/api/v3/did/verify	Verify DID
POST	/api/v3/trust/establish	Establish trust
GET	/api/v3/trust/reputation/{did}	Get reputation
POST	/api/v3/vc/issue	Issue VC
POST	/api/v3/vc/verify	Verify VC
Formal Verification		
POST	/api/v3/formal/verify	Formal verify
POST	/api/v3/formal/check	Check invariants
WASM		
POST	/api/v3/wasm/compile	Compile to WASM
POST	/api/v3/wasm/execute	Execute WASM
POST	/api/v3/wasm/upload	Upload WASM
Rust		
GET	/api/v3/rust/status	Rust status
POST	/api/v3/rust/execute	Execute in Rust
MCP		
GET	/api/v3/mcp/tools	List MCP tools
POST	/api/v3/mcp/invoke	Invoke MCP tool
POST	/api/v3/mcp/context	Get MCP context
Monitoring		
GET	/api/v3/metrics	Performance metrics
GET	/api/v3/agents	List agents
GET	/api/v3/contracts	List contracts
Health		
GET	/health	Health check
GET	/api/health	Health check
Legacy v2.x Endpoints (Backward Compatible)
Method	URL	Description
POST	/api/v2/contracts	Create contract
GET	/api/v2/contracts/{id}	Get contract
POST	/api/v2/contracts/{id}/execute	Execute contract
POST	/api/v2/contracts/{id}/verify	Verify contract
POST	/api/v2/agents/trust	Establish trust
POST	/api/v2/agents/discover	Discover agents
15. Examples
Example 1: Full Lifecycle in Python
python
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Create agent
agent = requests.post(f"{BASE_URL}/api/v3/agent/register",
    json={"id": "agent-1", "model": "qwen2.5-coder:latest"}
).json()

# 2. Create DID
did = requests.post(f"{BASE_URL}/api/v3/did/create",
    json={"name": "agent-1"}
).json()

# 3. Discover other agents
agents = requests.post(f"{BASE_URL}/api/v3/discover",
    json={"capabilities": ["analyze"]}
).json()

# 4. Propose contract
proposal = requests.post(f"{BASE_URL}/api/v3/propose",
    json={
        "contract_id": "contract-123",
        "parties": ["agent-1", "agent-2"],
        "terms": {"max_tokens": 1000}
    }
).json()

# 5. Formal verification
verified = requests.post(f"{BASE_URL}/api/v3/formal/verify",
    json={"contract": proposal["contract"]}
).json()
print(f"✅ Formal verification: {verified['verified']}")

# 6. Negotiate
negotiated = requests.post(f"{BASE_URL}/api/v3/negotiate",
    json={"contract_id": "contract-123", "proposal": {"max_tokens": 1500}}
).json()

# 7. Commit
committed = requests.post(f"{BASE_URL}/api/v3/commit",
    json={"contract_id": "contract-123", "signatures": ["sig-1", "sig-2"]}
).json()

# 8. Execute
executed = requests.post(f"{BASE_URL}/api/v3/execute",
    json={"contract_id": "contract-123", "executor": "agent-1"}
).json()

# 9. Verify
verified_exec = requests.post(f"{BASE_URL}/api/v3/verify",
    json={"contract_id": "contract-123", "execution_id": executed["execution_id"]}
).json()

# 10. Done
done = requests.post(f"{BASE_URL}/api/v3/done",
    json={"contract_id": "contract-123"}
).json()

print("✅ Full lifecycle completed!")
Example 2: WASM in Browser
html
<!DOCTYPE html>
<html>
<head>
    <title>Vireo v3.0 WASM Demo</title>
</head>
<body>
    <h1>🌿 Vireo v3.0.0 WASM</h1>
    <div id="status">Loading...</div>
    
    <script type="module">
        import init from './web/wasm/vireo.js';
        
        const status = document.getElementById('status');
        
        try {
            // Initialize WASM
            const { VireoAgent, WireFormat } = await init();
            status.textContent = '✅ WASM loaded!';
            
            // Create agent
            const agent = new VireoAgent('web-agent-1');
            
            // Create message
            const msg = {
                type: 'PROPOSE',
                sender: 'web-agent-1',
                recipient: 'agent-2',
                payload: { contract_id: '123' }
            };
            
            // Serialize
            const wire = WireFormat.serialize(msg);
            status.textContent += `\nSerialized: ${wire.length} bytes`;
            
            // Deserialize
            const restored = WireFormat.deserialize(wire);
            status.textContent += `\nDeserialized: ${restored.type}`;
            
        } catch (error) {
            status.textContent = `❌ Error: ${error.message}`;
        }
    </script>
</body>
</html>
Example 3: Rust Agent with WebSocket
rust
use vireo::{Agent, WebSocketTransport, Protocol};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut agent = Agent::new("rust-agent-1")
        .with_transport(WebSocketTransport::new("ws://localhost:5000"))
        .register()
        .await?;
    
    // Listen for messages
    while let Some(msg) = agent.next_message().await {
        match msg.type.as_str() {
            "PROPOSE" => {
                println!("📨 Received proposal: {:?}", msg.payload);
                let response = agent.negotiate(&msg).await?;
                agent.send(response).await?;
            }
            "EXECUTE" => {
                println!("⚡ Executing contract: {:?}", msg.payload);
                let result = agent.execute(&msg).await?;
                agent.send(result).await?;
            }
            _ => println!("📨 Message: {:?}", msg),
        }
    }
    
    Ok(())
}
16. Migration from v2.x
Key Changes
v2.x	v3.0.0	Migration
api_server.py	api/server.py	Update imports
JSON protocol	Binary (Protobuf)	Use WireFormat
Whitelist trust	DIDs + Federated	Update trust logic
Basic verification	Formal (SMT)	Use FormalVerifier
Python only	Python + Rust + WASM	Install Rust SDK
Migration Steps
python
# v2.x code
from protocol.agent import Agent
agent = Agent(id="agent-1")
agent.register()
contract = agent.create_contract(...)

# v3.0.0 code (backward compatible)
from protocol.agent import Agent
agent = Agent(id="agent-1", version="v3.0.0")
agent.register()

# New features
from core.protocol.wire import WireFormat
from core.identity.did import DID

# Create DID
did = DID.create("agent-1")

# Use Wire Format
wire_data = WireFormat.serialize(message)
Running Both Versions
bash
# v2.x (port 5001)
python api_server_v2.py --port 5001

# v3.0.0 (port 5000)
python api/server.py --port 5000
17. FAQ
❓ What's new in v3.0.0?
A: Open Wire Protocol (binary), WASM runtime, Rust SDK, DIDs with federated trust, formal verification (SMT), MCP support, and full lifecycle states.

❓ Is v3.0.0 backward compatible with v2.x?
A: Yes! All v2.x endpoints still work. You can migrate gradually.

❓ Do I need Rust to use v3.0.0?
A: No, Rust is optional. Python version works without Rust.

❓ How do I enable WASM?
A: Run ./scripts/build_wasm.sh and start server with --wasm-enabled.

❓ Where are DIDs stored?
A: DIDs are stored in keys/dids/ directory.

❓ How to use formal verification?
A: Use /api/v3/formal/verify endpoint or FormalVerifier in Python.

❓ Can I run Vireo in the browser?
A: Yes! Use WASM runtime. See the WASM section.

❓ How to contribute?
A: See CONTRIBUTING.md and GOVERNANCE.md.

📚 Additional Resources
Resource	Description
README.md	Project overview
QUICKSTART.md	5-minute quickstart
TUTORIAL.md	Complete tutorial
PROTOCOL.md	Protocol specification
WIRE_FORMAT.md	Open Wire spec
SECURITY.md	Security guide
GOVERNANCE.md	Governance model
API_REFERENCE.md	API reference
🌿 Vireo v3.0.0 — The World's First AI-to-AI Communication Language

Open Wire Protocol · WASM · Rust · Formal Verification · Federated Trust