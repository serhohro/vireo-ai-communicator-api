markdown
# 📘 Vireo — How to Work with Vireo

## Environment Comparison & Recommendations

---

## 1. ENVIRONMENT COMPARISON

| Feature | **Pure Python** | **Vireo** | **Terminal + Vireo** | **Jupyter + Vireo** | **Colab + Vireo** |
|---------|-----------------|-----------|----------------------|---------------------|-------------------|
| **Complexity** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| **Visualization** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Interactivity** | ❌ | ✅ | ⭐ | ✅ | ✅ |
| **AI Agents** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Contracts** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Cryptography** | ⭐ | ✅ | ✅ | ✅ | ✅ |
| **Documentation** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| **Cloud Access** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 2. WHAT'S BEST?

### 🏆 **For Developers: Vireo + Jupyter Lab**
- Result visualization
- Interactive agent work
- Experiment documentation

### 🏆 **For Quick Testing: Terminal + Vireo**
- Fast startup
- Minimal dependencies
- Ideal for CI/CD

### 🏆 **For Research: Google Colab + Vireo**
- Free GPU
- Cloud access
- Fast sharing

### 🏆 **For Production: Pure Python + Vireo API**
- Maximum performance
- Full control
- Optimization

---

## 3. HOW TO WORK

### 🖥️ **Pure Python + Vireo (Recommended)**

**Create `vireo_client.py`:**

```python
# ============================================================
# VIREO CLIENT — Working with Vireo from Pure Python
# ============================================================

import requests
import json
from typing import Optional, Dict, Any

class VireoClient:
    """Client for working with Vireo API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.agents = {}
    
    def register_agent(self, agent_id: str, model: str = "qwen2.5-coder:latest") -> Dict:
        """Register an agent."""
        response = requests.post(
            f"{self.base_url}/api/agent/register",
            json={"id": agent_id, "model": model}
        )
        return response.json()
    
    def auto_negotiate(self, sender: str, recipient: str, task: str, provider: str = "mistral") -> Dict:
        """Autonomous communication."""
        response = requests.post(
            f"{self.base_url}/api/llm/agent/{sender}/auto_negotiate",
            json={"recipient": recipient, "task": task, "provider": provider}
        )
        return response.json()
    
    def execute_code(self, code: str) -> Dict:
        """Execute Vireo code."""
        response = requests.post(
            f"{self.base_url}/api/interpreter",
            json={"code": code}
        )
        return response.json()
    
    def create_contract(self, parties: list, terms: dict, obligations: dict) -> Dict:
        """Create a contract."""
        response = requests.post(
            f"{self.base_url}/api/v2/contracts",
            json={"parties": parties, "terms": terms, "obligations": obligations}
        )
        return response.json()
    
    def execute_contract(self, contract_id: str) -> Dict:
        """Execute a contract."""
        response = requests.post(f"{self.base_url}/api/v2/contracts/{contract_id}/execute")
        return response.json()
    
    def verify_contract(self, contract_id: str) -> Dict:
        """Verify a contract."""
        response = requests.post(f"{self.base_url}/api/v2/contracts/{contract_id}/verify")
        return response.json()

# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    client = VireoClient()
    
    # 1. Register agents
    client.register_agent("agent-1")
    client.register_agent("agent-2")
    
    # 2. Autonomous communication
    result = client.auto_negotiate(
        sender="agent-1",
        recipient="agent-2",
        task="Create a Python function for quicksort"
    )
    print("✅ Negotiation:", result.get("decision", {}).get("decision"))
    
    # 3. Create contract
    contract = client.create_contract(
        parties=["agent-1", "agent-2"],
        terms={"max_tokens": 1000, "timeout_sec": 60},
        obligations={
            "agent-1": {"action": "analyze", "input": {"data": "test"}},
            "agent-2": {"action": "report", "input": {"analysis": "$ref.agent-1.result"}}
        }
    )
    print("✅ Contract:", contract.get("contract_id"))
    
    # 4. Execute contract
    if contract.get("contract_id"):
        result = client.execute_contract(contract["contract_id"])
        print("✅ Execution:", result.get("execution", {}).get("status"))
        
        verification = client.verify_contract(contract["contract_id"])
        print("✅ Verification:", verification.get("verification", {}).get("verified"))
💻 Terminal + Vireo
bash
# Start server
python api_server.py

# Health check
curl http://localhost:5000/health

# List providers
curl http://localhost:5000/api/providers

# Register agent
curl -X POST http://localhost:5000/api/agent/register \
  -H "Content-Type: application/json" \
  -d '{"id": "my-agent", "model": "qwen2.5-coder:latest"}'

# Autonomous communication
curl -X POST http://localhost:5000/api/llm/agent/agent-vision/auto_negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "agent-training",
    "task": "Create a neural network",
    "provider": "mistral"
  }'

# Execute code
curl -X POST http://localhost:5000/api/interpreter \
  -H "Content-Type: application/json" \
  -d '{"code": "let x = 5; print(x)"}'

# Create contract
curl -X POST http://localhost:5000/api/v2/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "parties": ["agent-1", "agent-2"],
    "terms": {"max_tokens": 1000, "timeout_sec": 60}
  }'
📓 Jupyter Lab + Vireo
Create notebook vireo_notebook.ipynb:

python
# ============================================================
# Vireo v2.0.2 — Jupyter Lab Client
# ============================================================

import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:5000"

# ============================================================
# 1. HEALTH CHECK
# ============================================================

response = requests.get(f"{BASE_URL}/health")
data = response.json()
print(f"✅ Server: {data['status']}")
print(f"📌 Version: {data['version']}")

# ============================================================
# 2. PROVIDERS
# ============================================================

response = requests.get(f"{BASE_URL}/api/providers")
data = response.json()

providers_df = pd.DataFrame([
    {"Provider": p, "Models": ", ".join(data.get("models", {}).get(p, []))}
    for p in data.get("providers", [])
])
print(providers_df)

# ============================================================
# 3. AUTONOMOUS COMMUNICATION
# ============================================================

def negotiate(task, provider="mistral"):
    """Run autonomous negotiation."""
    # Register agents
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-1"})
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-2"})
    
    response = requests.post(
        f"{BASE_URL}/api/llm/agent/agent-1/auto_negotiate",
        json={"recipient": "agent-2", "task": task, "provider": provider}
    )
    return response.json()

# Test tasks
tasks = [
    "Create a neural network for MNIST classification",
    "Write a Python function for quicksort",
    "Generate a report about climate change"
]

results = []
for task in tasks:
    result = negotiate(task)
    results.append({
        "task": task,
        "decision": result.get("decision", {}).get("decision"),
        "status": result.get("status")
    })

df = pd.DataFrame(results)
print(df)

# ============================================================
# 4. VISUALIZATION
# ============================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Status
status_counts = df['status'].value_counts()
ax1.bar(status_counts.index, status_counts.values)
ax1.set_title('Task Status Distribution')
ax1.set_xlabel('Status')
ax1.set_ylabel('Count')

# Decision
decision_counts = df['decision'].value_counts()
ax2.bar(decision_counts.index, decision_counts.values)
ax2.set_title('Decision Distribution')
ax2.set_xlabel('Decision')
ax2.set_ylabel('Count')

plt.tight_layout()
plt.show()

# ============================================================
# 5. CRYPTOGRAPHY
# ============================================================

# Generate keys
response = requests.post(f"{BASE_URL}/api/crypto/generate_keys")
keys = response.json()
print(f"🔑 Public Key: {keys.get('public_key', 'N/A')[:20]}...")

# Sign
response = requests.post(
    f"{BASE_URL}/api/crypto/sign",
    json={"message": "Hello, Jupyter!"}
)
signature = response.json()
print(f"✍️ Signature: {signature.get('signature', 'N/A')[:20]}...")

# ============================================================
# 6. CONTRACTS
# ============================================================

contract_data = {
    "parties": ["agent-1", "agent-2"],
    "terms": {
        "max_tokens": 1000,
        "timeout_sec": 60
    },
    "obligations": {
        "agent-1": {
            "action": "analyze",
            "input": {"task": "Analyze data"}
        },
        "agent-2": {
            "action": "report",
            "input": {"analysis": "$ref.agent-1.result"}
        }
    }
}

response = requests.post(f"{BASE_URL}/api/v2/contracts", json=contract_data)
contract = response.json()
print(f"✅ Contract: {contract.get('contract_id', 'N/A')}")

if contract.get("contract_id"):
    contract_id = contract["contract_id"]
    
    # Execute
    response = requests.post(f"{BASE_URL}/api/v2/contracts/{contract_id}/execute")
    execution = response.json()
    print(f"✅ Execution: {execution.get('execution', {}).get('status')}")
    
    # Verify
    response = requests.post(f"{BASE_URL}/api/v2/contracts/{contract_id}/verify")
    verification = response.json()
    print(f"✅ Verification: {verification.get('verification', {}).get('verified')}")
🚀 Google Colab + Vireo
Create notebook in Colab:

python
# ============================================================
# Vireo v2.0.2 — Google Colab Client
# ============================================================

# Install dependencies (if needed)
!pip install requests

import requests
import pandas as pd
import matplotlib.pyplot as plt

# Configuration (local server or ngrok)
BASE_URL = "http://localhost:5000"  # or your ngrok URL

# ============================================================
# 1. HEALTH CHECK
# ============================================================

response = requests.get(f"{BASE_URL}/health")
print(f"✅ Server: {response.json()}")

# ============================================================
# 2. AUTONOMOUS COMMUNICATION
# ============================================================

def negotiate(task):
    """Run autonomous negotiation."""
    # Register agents
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-1"})
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-2"})
    
    response = requests.post(
        f"{BASE_URL}/api/llm/agent/agent-1/auto_negotiate",
        json={"recipient": "agent-2", "task": task, "provider": "mistral"}
    )
    return response.json()

# Test tasks
tasks = [
    "Create a neural network for MNIST classification",
    "Write a Python function for quicksort"
]

for task in tasks:
    result = negotiate(task)
    print(f"📝 Task: {task}")
    print(f"✅ Decision: {result.get('decision', {}).get('decision')}")
    print("-" * 50)

# ============================================================
# 3. VISUALIZATION
# ============================================================

plt.figure(figsize=(8, 4))
plt.bar(["Task 1", "Task 2"], [1, 1])
plt.title("Task Completion")
plt.ylabel("Status")
plt.show()

# ============================================================
# 4. CRYPTOGRAPHY
# ============================================================

# Generate keys
response = requests.post(f"{BASE_URL}/api/crypto/generate_keys")
keys = response.json()
print(f"🔑 Keys generated: {keys.get('status')}")

# Sign
response = requests.post(
    f"{BASE_URL}/api/crypto/sign",
    json={"message": "Hello, Colab!"}
)
signature = response.json()
print(f"✍️ Signature: {signature.get('status')}")
4. COMPARISON TABLE
Criterion	Pure Python	Vireo	Terminal + Vireo	Jupyter + Vireo	Colab + Vireo
AI Agents	❌	✅	✅	✅	✅
Contracts	❌	✅	✅	✅	✅
Cryptography	⭐	✅	✅	✅	✅
Autonomy	❌	✅	✅	✅	✅
Visualization	❌	❌	❌	✅	✅
Interactivity	❌	❌	⭐	✅	✅
Cloud Access	❌	❌	❌	❌	✅
Speed	⭐⭐⭐	⭐⭐	⭐⭐	⭐⭐	⭐
5. CONCLUSION
Purpose	Best Option
Production	Pure Python + Vireo API
Research	Jupyter Lab + Vireo
Testing	Terminal + Vireo
Learning	Google Colab + Vireo
Quick Prototypes	Vireo Web Interface
With Vireo you get AI agents, contracts, and cryptography — in any environment! 🚀

🌿 Vireo — The World's First AI-to-AI Communication Language. 🚀