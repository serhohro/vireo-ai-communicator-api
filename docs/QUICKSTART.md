# 🌿 Vireo v3.0.0 — Quick Start Guide

**5 minutes to your first AI-to-AI communication**

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-4.git
cd vireo-ai-communicator-4

# Install Python dependencies
pip install -e ".[all]"

# Start the server
python api/server.py
🤖 Your First Agent
1. Create an Agent
python
import requests

BASE_URL = "http://localhost:5000"

# Create agent
response = requests.post(f"{BASE_URL}/api/v3/agent/register", json={
    "id": "my-first-agent",
    "name": "Explorer Agent",
    "model": "qwen2.5-coder:latest"
})
print(response.json())
2. Add a Capability
python
# Add capability
requests.post(f"{BASE_URL}/api/v3/agent/my-first-agent/capability", json={
    "name": "analyze",
    "description": "Analyze any data"
})
3. Discover Other Agents
python
# Discover agents with specific capabilities
agents = requests.post(f"{BASE_URL}/api/v3/discover", json={
    "capabilities": ["analyze"]
})
print(f"Found {len(agents.json()['agents'])} agents")
📜 Your First Contract
1. Create a Contract
python
contract = requests.post(f"{BASE_URL}/api/v3/propose", json={
    "contract_id": "contract-001",
    "parties": ["my-first-agent", "another-agent"],
    "terms": {
        "max_tokens": 1000,
        "timeout_sec": 60
    },
    "obligations": {
        "my-first-agent": {
            "action": "analyze",
            "input": {"data": "sample_data"}
        }
    }
})
print(f"✅ Contract created: {contract.json()['contract']['id']}")
2. Formal Verification
python
# Verify contract mathematically
verified = requests.post(f"{BASE_URL}/api/v3/formal/verify", json={
    "contract": contract.json()['contract']
})
print(f"✅ Contract verified: {verified.json()['verified']}")
3. Execute
python
# Execute contract
execution = requests.post(f"{BASE_URL}/api/v3/execute", json={
    "contract_id": "contract-001",
    "executor": "my-first-agent"
})
print(f"✅ Executed: {execution.json()['execution_id']}")
🔐 Create a DID
python
# Create decentralized identity
did = requests.post(f"{BASE_URL}/api/v3/did/create", json={
    "name": "my-first-agent"
})
print(f"✅ DID: {did.json()['did']}")
⚡ WASM in Browser
1. Build WASM
bash
./scripts/build_wasm.sh
2. Use in HTML
html
<!DOCTYPE html>
<html>
<body>
    <h1>🌿 Vireo v3.0.0</h1>
    <div id="status"></div>
    
    <script type="module">
        import init from './web/wasm/vireo.js';
        
        const { VireoAgent } = await init();
        const agent = new VireoAgent('web-agent');
        document.getElementById('status').textContent = '✅ Agent ready!';
    </script>
</body>
</html>
🦀 Rust Agent
1. Install Rust SDK
bash
cd sdk/rust
cargo build --release
2. Create Agent
rust
use vireo::Agent;

#[tokio::main]
async fn main() {
    let agent = Agent::new("rust-agent")
        .register()
        .await
        .unwrap();
    
    println!("✅ Rust agent: {}", agent.id());
}
📊 Check Status
bash
# Health check
curl http://localhost:5000/api/health

# List agents
curl http://localhost:5000/api/v3/agents

# Metrics
curl http://localhost:5000/api/v3/metrics
🎯 Next Steps
Read the Tutorial — Complete step-by-step guide

Explore API Reference — All endpoints

Learn Wire Format — Binary protocol

Join the community — GitHub Discussions

🌿 Vireo v3.0.0 — The World's First AI-to-AI Communication Language
