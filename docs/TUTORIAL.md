# 🌿 Vireo v3.0.0 — Complete Tutorial

**Learn Vireo step by step**

---

## Table of Contents

1. [Part 1: Your First Agent](#part-1-your-first-agent)
2. [Part 2: Agents Communicating](#part-2-agents-communicating)
3. [Part 3: Contracts & Negotiation](#part-3-contracts--negotiation)
4. [Part 4: Formal Verification](#part-4-formal-verification)
5. [Part 5: DIDs & Trust](#part-5-dids--trust)
6. [Part 6: WASM Runtime](#part-6-wasm-runtime)
7. [Part 7: Rust SDK](#part-7-rust-sdk)
8. [Part 8: MCP Integration](#part-8-mcp-integration)
9. [Part 9: Advanced Lifecycle](#part-9-advanced-lifecycle)
10. [Part 10: Production Deployment](#part-10-production-deployment)

---

## Part 1: Your First Agent

### Step 1.1: Start the Server

```bash
python api/server.py
You should see:

text
🌿 VIREO API SERVER v3.0.0
📍 Server: http://localhost:5000
Step 1.2: Create an Agent
python
import requests

BASE = "http://localhost:5000"

agent = requests.post(f"{BASE}/api/v3/agent/register", json={
    "id": "alice",
    "name": "Alice Agent",
    "model": "qwen2.5-coder:latest"
}).json()

print(f"✅ Agent Alice created: {agent['id']}")
Step 1.3: Add Capabilities
python
requests.post(f"{BASE}/api/v3/agent/alice/capability", json={
    "name": "process_text",
    "description": "Process natural language text"
})

requests.post(f"{BASE}/api/v3/agent/alice/capability", json={
    "name": "analyze_sentiment",
    "description": "Analyze sentiment of text"
})
Step 1.4: Check Agent Status
bash
curl http://localhost:5000/api/v3/agents | jq
Part 2: Agents Communicating
Step 2.1: Create Two Agents
python
# Alice
requests.post(f"{BASE}/api/v3/agent/register", json={
    "id": "alice", "name": "Alice", "model": "qwen2.5-coder:latest"
})

# Bob
requests.post(f"{BASE}/api/v3/agent/register", json={
    "id": "bob", "name": "Bob", "model": "qwen2.5-coder:latest"
})
Step 2.2: Discover
python
# Alice discovers agents with "process_text" capability
result = requests.post(f"{BASE}/api/v3/discover", json={
    "capabilities": ["process_text"]
}).json()

print(f"Found: {result['agents']}")
Step 2.3: Send Message
python
message = requests.post(f"{BASE}/api/v3/message", json={
    "type": "PROPOSE",
    "sender": "alice",
    "recipient": "bob",
    "payload": {
        "task": "Process this text: 'Hello Vireo!'",
        "format": "text"
    }
}).json()

print(f"✅ Message sent: {message['message_id']}")
Step 2.4: WebSocket Real-time
javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('✅ Connected!');
    socket.emit('message', {
        type: 'PROPOSE',
        sender: 'alice',
        recipient: 'bob',
        payload: { task: 'Hello!' }
    });
});

socket.on('message_ack', (data) => {
    console.log('📨 ACK:', data);
});
Part 3: Contracts & Negotiation
Step 3.1: Create Contract
python
contract = requests.post(f"{BASE}/api/v3/propose", json={
    "contract_id": "contract-001",
    "parties": ["alice", "bob"],
    "terms": {
        "max_tokens": 5000,
        "timeout_sec": 120,
        "max_rounds": 10
    },
    "obligations": {
        "alice": {
            "action": "process_text",
            "input": {"text": "AI is the future"}
        },
        "bob": {
            "action": "analyze_sentiment",
            "input": {"text": "$ref.alice.result"}
        }
    },
    "condition": "sentiment_score > 0.5",
    "on_failure": "escalate"
}).json()

contract_id = contract['contract']['id']
print(f"✅ Contract: {contract_id}")
Step 3.2: Negotiate Terms
python
negotiation = requests.post(f"{BASE}/api/v3/negotiate", json={
    "contract_id": contract_id,
    "proposal": {
        "max_tokens": 3000,  # Counter-offer
        "timeout_sec": 90
    }
}).json()

print(f"🤝 Negotiation: {negotiation['status']}")
Step 3.3: Commit & Sign
python
commit = requests.post(f"{BASE}/api/v3/commit", json={
    "contract_id": contract_id,
    "signatures": ["alice_sig_123", "bob_sig_456"]
}).json()

print(f"📜 Committed: {commit['contract']['status']}")
Step 3.4: Execute
python
execution = requests.post(f"{BASE}/api/v3/execute", json={
    "contract_id": contract_id,
    "executor": "alice"
}).json()

execution_id = execution['execution_id']
print(f"⚡ Executed: {execution_id}")
Step 3.5: Verify
python
verification = requests.post(f"{BASE}/api/v3/verify", json={
    "contract_id": contract_id,
    "execution_id": execution_id
}).json()

print(f"✅ Verified: {verification['verified']}")
Step 3.6: Complete
python
done = requests.post(f"{BASE}/api/v3/done", json={
    "contract_id": contract_id
}).json()

print(f"🏁 Done: {done['status']}")
Part 4: Formal Verification
Step 4.1: Verify Contract Correctness
python
verification = requests.post(f"{BASE}/api/v3/formal/verify", json={
    "contract": {
        "id": "contract-001",
        "parties": ["alice", "bob"],
        "terms": {"max_tokens": 5000},
        "obligations": {
            "alice": {"action": "process_text"},
            "bob": {"action": "analyze_sentiment"}
        }
    },
    "properties": ["safety", "liveness", "fairness"]
}).json()

if verification['verified']:
    print("✅ Contract is mathematically correct!")
else:
    print("❌ Contract has issues:", verification['details'])
Step 4.2: Check Invariants
python
invariants = requests.post(f"{BASE}/api/v3/formal/check", json={
    "contract": contract['contract'],
    "invariants": [
        "max_tokens >= 0",
        "timeout_sec > 0",
        "parties != []"
    ]
}).json()

print(f"🧠 Invariants: {invariants['all_valid']}")
Step 4.3: Python Formal Verification
python
from core.protocol.formal_verifier import FormalVerifier

verifier = FormalVerifier()

contract = {
    "id": "contract-001",
    "parties": ["alice", "bob"],
    "terms": {"max_tokens": 5000}
}

verified = verifier.verify_contract(contract)
print(f"✅ Formal verification: {verified}")

# Get detailed proof
proof = verifier.get_proof()
print(f"📝 Proof: {proof[:200]}...")
Part 5: DIDs & Trust
Step 5.1: Create DIDs
python
# Alice's DID
alice_did = requests.post(f"{BASE}/api/v3/did/create", json={
    "name": "alice"
}).json()

# Bob's DID
bob_did = requests.post(f"{BASE}/api/v3/did/create", json={
    "name": "bob"
}).json()

print(f"Alice DID: {alice_did['did']}")
print(f"Bob DID: {bob_did['did']}")
Step 5.2: Establish Trust
python
trust = requests.post(f"{BASE}/api/v3/trust/establish", json={
    "agent_a": alice_did['did'],
    "agent_b": bob_did['did']
}).json()

print(f"🔐 Trust: {trust['success']}")
Step 5.3: Check Reputation
python
reputation = requests.get(
    f"{BASE}/api/v3/trust/reputation/{alice_did['did']}"
).json()

print(f"⭐ Alice reputation: {reputation['reputation']}")
Step 5.4: Issue Verifiable Credential
python
vc = requests.post(f"{BASE}/api/v3/vc/issue", json={
    "issuer": "did:vireo:trust-authority",
    "subject": alice_did['did'],
    "claims": {
        "capability": "process_text",
        "level": "expert",
        "expires": "2027-12-31"
    }
}).json()

print(f"📜 VC issued: {vc['vc_id']}")
Step 5.5: Verify VC
python
verified_vc = requests.post(f"{BASE}/api/v3/vc/verify", json={
    "vc_id": vc['vc_id']
}).json()

print(f"✅ VC verified: {verified_vc['verified']}")
Part 6: WASM Runtime
Step 6.1: Build WASM
bash
# Install wasm-pack if not installed
cargo install wasm-pack

# Build WASM
./scripts/build_wasm.sh
Step 6.2: Compile Vireo to WASM
python
code = """
agent vision {
    capability analyze_images {
        input: image: bytes
        output: result: string
        action: "Analyzing: {image}"
    }
}
"""

wasm = requests.post(f"{BASE}/api/v3/wasm/compile", json={
    "code": code
}).json()

print(f"⚡ WASM size: {wasm['wasm_size']} bytes")
Step 6.3: Execute WASM
python
execution = requests.post(f"{BASE}/api/v3/wasm/execute", json={
    "wasm_module": wasm['wasm_module'],
    "params": {"image": "base64_encoded_image"}
}).json()

print(f"📤 Result: {execution['result']}")
Step 6.4: Browser Integration
html
<!DOCTYPE html>
<html>
<head>
    <title>Vireo WASM Demo</title>
</head>
<body>
    <div id="app">
        <h1>🌿 Vireo WASM</h1>
        <button id="run">Run Agent</button>
        <pre id="output"></pre>
    </div>
    
    <script type="module">
        import init, { VireoAgent } from './web/wasm/vireo.js';
        
        const runBtn = document.getElementById('run');
        const output = document.getElementById('output');
        
        runBtn.addEventListener('click', async () => {
            try {
                await init();
                const agent = new VireoAgent('wasm-agent');
                const result = await agent.propose({
                    contract_id: 'wasm-test',
                    task: 'Analyze image'
                });
                output.textContent = JSON.stringify(result, null, 2);
            } catch (error) {
                output.textContent = '❌ Error: ' + error.message;
            }
        });
    </script>
</body>
</html>
Part 7: Rust SDK
Step 7.1: Setup Rust Project
bash
# Create new Rust project
cargo new vireo-agent
cd vireo-agent

# Add dependency
echo 'vireo = { path = "../sdk/rust" }' >> Cargo.toml
Step 7.2: Create Agent
rust
// src/main.rs
use vireo::{Agent, Protocol, WireFormat};
use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create agent
    let agent = Agent::new("rust-agent-1")
        .with_did("did:vireo:rust-agent-1")
        .register()
        .await?;
    
    println!("✅ Rust agent: {}", agent.id());
    
    // Create proposal
    let proposal = agent.propose(
        "agent-2",
        json!({
            "contract_id": "rust-contract",
            "terms": {"max_tokens": 5000}
        })
    ).await?;
    
    println!("📝 Proposal: {:?}", proposal);
    
    // Negotiate
    let contract = agent.negotiate(&proposal).await?;
    println!("📜 Contract: {:?}", contract);
    
    // Commit
    let committed = agent.commit(&contract).await?;
    println!("✅ Committed");
    
    // Execute
    let result = agent.execute(&committed).await?;
    println!("⚡ Result: {:?}", result);
    
    // Verify
    let verified = agent.verify(&committed).await?;
    println!("✅ Verified: {}", verified);
    
    Ok(())
}
Step 7.3: Run
bash
cargo run --release
Step 7.4: Performance Comparison
bash
# Run benchmarks
cargo bench

# Compare with Python
python scripts/benchmark_models.py
Part 8: MCP Integration
Step 8.1: List MCP Tools
bash
curl http://localhost:5000/api/v3/mcp/tools
Step 8.2: Invoke Tool
python
result = requests.post(f"{BASE}/api/v3/mcp/invoke", json={
    "tool": "analyze_data",
    "params": {
        "data": [1, 2, 3, 4, 5],
        "method": "statistical"
    }
}).json()

print(f"📊 Analysis: {result['result']}")
Step 8.3: Get MCP Context
python
context = requests.post(f"{BASE}/api/v3/mcp/context", json={
    "agent_id": "alice"
}).json()

print(f"📋 Context: {context['context']}")
Step 8.4: Custom MCP Tool
python
# Register custom tool
requests.post(f"{BASE}/api/v3/mcp/register", json={
    "name": "custom_analyzer",
    "description": "Custom data analyzer",
    "input_schema": {
        "type": "object",
        "properties": {
            "data": {"type": "array"},
            "threshold": {"type": "number"}
        }
    }
})
Part 9: Advanced Lifecycle
Full Lifecycle with Error Handling
python
def run_full_lifecycle():
    try:
        # 1. DISCOVER
        agents = discover_agents(["analyze"])
        if not agents:
            raise Exception("No agents found")
        
        # 2. PROPOSE
        proposal = propose_contract(agents[0])
        
        # 3. NEGOTIATE
        negotiated = negotiate_contract(proposal['id'])
        if negotiated['status'] == 'rejected':
            raise Exception("Negotiation rejected")
        
        # 4. COMMIT
        committed = commit_contract(proposal['id'])
        
        # 5. EXECUTE
        executed = execute_contract(proposal['id'])
        if executed['status'] == 'failed':
            # 6. ESCALATE
            escalate_contract(proposal['id'], "Execution failed")
            return
        
        # 7. VERIFY
        verified = verify_execution(proposal['id'], executed['id'])
        if not verified['verified']:
            escalate_contract(proposal['id'], "Verification failed")
            return
        
        # 8. DONE
        done = complete_contract(proposal['id'])
        print(f"✅ Lifecycle complete: {done['status']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Escalate
        escalate_contract(proposal['id'], str(e))
State Machine
python
from core.protocol.state import ProtocolState, State

# Create state machine
machine = ProtocolState()

# Add states
machine.add_state(State.DISCOVER)
machine.add_state(State.PROPOSE)
machine.add_state(State.NEGOTIATE)
machine.add_state(State.COMMIT)
machine.add_state(State.EXECUTE)
machine.add_state(State.VERIFY)
machine.add_state(State.ESCALATE)
machine.add_state(State.DONE)

# Add transitions
machine.add_transition(State.DISCOVER, State.PROPOSE)
machine.add_transition(State.PROPOSE, State.NEGOTIATE)
machine.add_transition(State.NEGOTIATE, State.COMMIT)
machine.add_transition(State.COMMIT, State.EXECUTE)
machine.add_transition(State.EXECUTE, State.VERIFY)
machine.add_transition(State.VERIFY, State.DONE)
machine.add_transition(State.VERIFY, State.ESCALATE, condition="failed")

# Use
machine.transition(State.PROPOSE)  # Move to propose
Part 10: Production Deployment
Step 10.1: Docker Deployment
dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "api/server.py", "--production"]
bash
# Build and run
docker build -t vireo:v3 .
docker run -p 5000:5000 vireo:v3
Step 10.2: Docker Compose
yaml
# docker-compose.yml
version: '3.8'

services:
  vireo-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./keys:/app/keys

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
Step 10.3: Environment Variables
bash
# .env
PORT=5000
DEBUG=False
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=*
MISTRAL_API_KEY=your-key
OPENAI_API_KEY=your-key
Step 10.4: Monitoring
bash
# Health check endpoint
curl http://localhost:5000/api/health

# Metrics
curl http://localhost:5000/api/v3/metrics

# Logs
docker logs -f vireo-api
Step 10.5: Performance Tuning
python
# config.yaml
server:
  workers: 4
  max_connections: 1000
  timeout: 30

redis:
  pool_size: 10
  max_retries: 3

wasm:
  cache_size: 100
  max_memory: 256MB

rust:
  enabled: true
  threads: 4
🎯 Summary
You've learned:

✅ Creating agents

✅ Agent communication

✅ Contracts & negotiation

✅ Formal verification

✅ DIDs & federated trust

✅ WASM runtime

✅ Rust SDK

✅ MCP integration

✅ Advanced lifecycle

✅ Production deployment

📚 Next Steps
Read API Reference

Explore Wire Format

Join GitHub Discussions

Contribute to the project

🌿 Vireo v3.0.0 — The World's First AI-to-AI Communication Language