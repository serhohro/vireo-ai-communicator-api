🌿 VIREO v3.0.0 — COMPLETE USER GUIDE
The World's First AI-to-AI Communication Language

📋 TABLE OF CONTENTS
What is Vireo?

Quick Start

Working with Agents

Working with Contracts

Autonomous AI-to-AI Communication

DIDs & Federated Trust

Open Wire Protocol

Security & Cryptography

LLM Providers

API Reference

PowerShell Commands

Python Code Examples

1. WHAT IS VIREO?
Vireo is a programming language + protocol + runtime for autonomous AI-to-AI communication, negotiation, and coordination.

Key Features
Feature	Description
🧠 Language	Formal grammar (EBNF) for AI communication
🌐 Protocol	Open Wire Protocol — binary, 10x faster than JSON
🔐 Security	DIDs + Ed25519 signatures for trust
📜 Contracts	Smart contracts with formal verification (SMT)
🤝 Trust	Federated trust — no central authority
🇪🇺 European	Priority support for EU LLMs (Mistral, Aleph Alpha, Cohere)
⚡ Fast	Create AI agents in seconds
2. QUICK START
Installation
bash
# Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-4.git
cd vireo-ai-communicator-4

# Install dependencies
pip install -r requirements.txt

# Start the server
python api/server.py
Open in Browser
text
http://localhost:5000/web
Create Your First Agent in 5 Seconds
bash
curl -X POST http://localhost:5000/api/v3/agent/register \
  -H "Content-Type: application/json" \
  -d '{"id": "my-first-agent"}'
3. WORKING WITH AGENTS
Create an Agent
Via Web Interface
Open http://localhost:5000/web

Go to 🧠 Agents tab

Enter Agent ID (e.g., my-agent)

Click 📝 Register v3

Via API (curl)
bash
curl -X POST http://localhost:5000/api/v3/agent/register \
  -H "Content-Type: application/json" \
  -d '{"id": "agent-1"}'
Via API (PowerShell)
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" `
  -ContentType "application/json" `
  -Body '{"id": "agent-1"}'
Via Python
python
import requests

response = requests.post(
    "http://localhost:5000/api/v3/agent/register",
    json={"id": "agent-1"}
)
print(response.json())
Add Capabilities to an Agent
Via Web Interface
Go to 🧠 Agents tab

Enter capability name (e.g., analyze_data)

Click 📌 Add Capability

Via API
bash
curl -X POST http://localhost:5000/api/v3/agent/agent-1/capability \
  -H "Content-Type: application/json" \
  -d '{"name": "analyze_data"}'
List All Agents
bash
curl http://localhost:5000/api/v3/agents
Check Agent Status
bash
curl http://localhost:5000/api/v3/agent/agent-1/status
4. WORKING WITH CONTRACTS
Create a Contract
Via Web Interface
Go to 📜 Contracts tab

Fill in:

Parties: agent-1, agent-2

Max Tokens: 1000

Timeout: 60

Click 📝 Create v3

Via API
bash
curl -X POST http://localhost:5000/api/v3/propose \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "contract-1",
    "parties": ["agent-1", "agent-2"],
    "terms": {"max_tokens": 1000, "timeout_sec": 60}
  }'
Execute a Contract
bash
curl -X POST http://localhost:5000/api/v3/execute \
  -H "Content-Type: application/json" \
  -d '{"contract_id": "contract-1"}'
Verify a Contract
bash
curl -X POST http://localhost:5000/api/v3/verify \
  -H "Content-Type: application/json" \
  -d '{"contract_id": "contract-1"}'
List All Contracts
bash
curl http://localhost:5000/api/v3/contracts
Get Contract Details
bash
curl http://localhost:5000/api/v3/contracts/contract-1
5. AUTONOMOUS AI-TO-AI COMMUNICATION
Via Web Interface
Open http://localhost:5000/web

Go to 🤖 Autonomous tab

Fill in:

Agent (Proposer): agent-1

Agent (Executor): agent-2

LLM Provider: Select a provider

Task Description: Describe the task

Click 🚀 Start Negotiation

Via API
bash
curl -X POST http://localhost:5000/api/llm/agent/agent-1/auto_negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "agent-2",
    "task": "Create a neural network for MNIST classification",
    "provider": "ollama"
  }'
Available LLM Providers
Provider	ID	Type	Country
Ollama	ollama	🦙 Local	Local
Mistral AI	mistral	🇪🇺 EU	France
Aleph Alpha	aleph_alpha	🇪🇺 EU	Germany
Cohere	cohere	🇪🇺 EU	Switzerland
Qwen AI	qwen	🌍 Global	China
OpenAI GPT	openai	🌍 Global	USA
Claude	claude	🌍 Global	USA
Gemini	gemini	🌍 Global	USA
6. DIDs & FEDERATED TRUST
Create a DID
bash
curl -X POST http://localhost:5000/api/v3/did/create \
  -H "Content-Type: application/json" \
  -d '{"name": "agent-1"}'
Verify a DID
bash
curl -X POST http://localhost:5000/api/v3/did/verify \
  -H "Content-Type: application/json" \
  -d '{"did": "did:vireo:agent-1-1"}'
Establish Trust Between Agents
bash
curl -X POST http://localhost:5000/api/v3/trust/establish \
  -H "Content-Type: application/json" \
  -d '{
    "agent_a": "did:vireo:agent-1-1",
    "agent_b": "did:vireo:agent-2-1"
  }'
7. OPEN WIRE PROTOCOL
Get Protocol Version
bash
curl http://localhost:5000/api/v3/protocol/version
Send a Message
bash
curl -X POST http://localhost:5000/api/v3/message \
  -H "Content-Type: application/json" \
  -d '{
    "type": "PROPOSE",
    "sender": "agent-1",
    "recipient": "agent-2",
    "payload": {"text": "Hello from Open Wire!"}
  }'
8. SECURITY & CRYPTOGRAPHY
Generate Ed25519 Keys
bash
curl -X POST http://localhost:5000/api/crypto/generate_keys
Sign a Message
bash
curl -X POST http://localhost:5000/api/crypto/sign \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Vireo v3.0.0!"}'
Verify a Signature
bash
curl -X POST http://localhost:5000/api/crypto/verify \
  -H "Content-Type: application/json" \
  -d '{
    "signature": "your_signature_here",
    "message": "Hello Vireo v3.0.0!"
  }'
Test Trust Protocol
bash
curl -X POST http://localhost:5000/api/crypto/test_trust
9. LLM PROVIDERS
List All Providers
bash
curl http://localhost:5000/api/providers
Setup Ollama (Local)
bash
# Start Ollama
ollama serve

# List available models
ollama list

# Pull a model
ollama pull qwen2.5-coder:latest
Setup Mistral AI (European)
Add to .env:

text
MISTRAL_API_KEY=your-api-key-here
Setup Aleph Alpha (European)
Add to .env:

text
ALEPH_ALPHA_API_KEY=your-api-key-here
Setup OpenAI GPT
Add to .env:

text
OPENAI_API_KEY=your-api-key-here
10. API REFERENCE
Core Endpoints
Method	Endpoint	Description
GET	/	Home
GET	/web	Web Interface
GET	/docs	Documentation
GET	/api/health	Health Check
GET	/api/docs	API Documentation
Agents
Method	Endpoint	Description
POST	/api/v3/agent/register	Register Agent
GET	/api/v3/agents	List Agents
GET	/api/v3/agent/<id>/status	Agent Status
POST	/api/v3/agent/<id>/capability	Add Capability
Contracts
Method	Endpoint	Description
POST	/api/v3/propose	Create Contract
GET	/api/v3/contracts	List Contracts
GET	/api/v3/contracts/<id>	Get Contract
POST	/api/v3/execute	Execute Contract
POST	/api/v3/verify	Verify Contract
DIDs & Trust
Method	Endpoint	Description
POST	/api/v3/did/create	Create DID
POST	/api/v3/did/verify	Verify DID
POST	/api/v3/trust/establish	Establish Trust
Protocol
Method	Endpoint	Description
GET	/api/v3/protocol/version	Protocol Version
POST	/api/v3/message	Send Message
Autonomous
Method	Endpoint	Description
POST	/api/llm/agent/<id>/auto_negotiate	Autonomous Negotiation
Security
Method	Endpoint	Description
POST	/api/crypto/generate_keys	Generate Keys
POST	/api/crypto/sign	Sign Message
POST	/api/crypto/verify	Verify Signature
POST	/api/crypto/test_trust	Test Trust
Monitoring
Method	Endpoint	Description
GET	/api/v3/metrics	Metrics
11. POWERSHELL COMMANDS
Quick Reference
Command	Description
.\start_vireo.bat	Start the server
Invoke-RestMethod -Uri "http://localhost:5000/api/health"	Check server health
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/agents"	List agents
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/metrics"	Get metrics
Invoke-RestMethod -Uri "http://localhost:5000/api/providers"	List LLM providers
Complete Workflow
powershell
# 1. Start the server
.\start_vireo.bat

# 2. Create agents
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" -ContentType "application/json" -Body '{"id": "alice"}'
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" -ContentType "application/json" -Body '{"id": "bob"}'

# 3. Add capabilities
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/alice/capability" -ContentType "application/json" -Body '{"name": "analyze"}'
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/bob/capability" -ContentType "application/json" -Body '{"name": "process"}'

# 4. Create contract
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/propose" -ContentType "application/json" -Body '{"contract_id": "c1", "parties": ["alice", "bob"], "terms": {"max_tokens": 1000}}'

# 5. Execute contract
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/execute" -ContentType "application/json" -Body '{"contract_id": "c1"}'

# 6. Verify contract
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/verify" -ContentType "application/json" -Body '{"contract_id": "c1"}'

# 7. Autonomous communication
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/llm/agent/alice/auto_negotiate" -ContentType "application/json" -Body '{"recipient": "bob", "task": "Analyze data", "provider": "ollama"}'

# 8. Check metrics
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/metrics"
12. PYTHON CODE EXAMPLES
Full Workflow in Python
python
import requests
import json

BASE_URL = "http://localhost:5000"

# ============================================================
# 1. CREATE AGENTS
# ============================================================

def create_agent(agent_id):
    response = requests.post(
        f"{BASE_URL}/api/v3/agent/register",
        json={"id": agent_id}
    )
    return response.json()

# Create two agents
print("Creating agents...")
create_agent("alice")
create_agent("bob")

# ============================================================
# 2. ADD CAPABILITIES
# ============================================================

def add_capability(agent_id, capability):
    response = requests.post(
        f"{BASE_URL}/api/v3/agent/{agent_id}/capability",
        json={"name": capability}
    )
    return response.json()

print("Adding capabilities...")
add_capability("alice", "analyze")
add_capability("bob", "process")

# ============================================================
# 3. LIST AGENTS
# ============================================================

def list_agents():
    response = requests.get(f"{BASE_URL}/api/v3/agents")
    return response.json()

print("Listing agents...")
agents = list_agents()
print(json.dumps(agents, indent=2))

# ============================================================
# 4. CREATE CONTRACT
# ============================================================

def create_contract(contract_id, parties, terms):
    response = requests.post(
        f"{BASE_URL}/api/v3/propose",
        json={
            "contract_id": contract_id,
            "parties": parties,
            "terms": terms
        }
    )
    return response.json()

print("Creating contract...")
contract = create_contract(
    "c1",
    ["alice", "bob"],
    {"max_tokens": 1000, "timeout_sec": 60}
)
print(json.dumps(contract, indent=2))

# ============================================================
# 5. EXECUTE CONTRACT
# ============================================================

def execute_contract(contract_id):
    response = requests.post(
        f"{BASE_URL}/api/v3/execute",
        json={"contract_id": contract_id}
    )
    return response.json()

print("Executing contract...")
execution = execute_contract("c1")
print(json.dumps(execution, indent=2))

# ============================================================
# 6. VERIFY CONTRACT
# ============================================================

def verify_contract(contract_id):
    response = requests.post(
        f"{BASE_URL}/api/v3/verify",
        json={"contract_id": contract_id}
    )
    return response.json()

print("Verifying contract...")
verification = verify_contract("c1")
print(json.dumps(verification, indent=2))

# ============================================================
# 7. AUTONOMOUS COMMUNICATION
# ============================================================

def auto_negotiate(sender, recipient, task, provider="ollama"):
    response = requests.post(
        f"{BASE_URL}/api/llm/agent/{sender}/auto_negotiate",
        json={
            "recipient": recipient,
            "task": task,
            "provider": provider
        }
    )
    return response.json()

print("Starting autonomous negotiation...")
result = auto_negotiate(
    "alice",
    "bob",
    "Create a neural network for MNIST classification"
)
print(json.dumps(result, indent=2))

# ============================================================
# 8. CHECK METRICS
# ============================================================

def get_metrics():
    response = requests.get(f"{BASE_URL}/api/v3/metrics")
    return response.json()

print("Getting metrics...")
metrics = get_metrics()
print(json.dumps(metrics, indent=2))
DIDs and Trust in Python
python
# ============================================================
# 9. CREATE DID
# ============================================================

def create_did(name):
    response = requests.post(
        f"{BASE_URL}/api/v3/did/create",
        json={"name": name}
    )
    return response.json()

print("Creating DID...")
did = create_did("alice")
print(json.dumps(did, indent=2))

# ============================================================
# 10. VERIFY DID
# ============================================================

def verify_did(did):
    response = requests.post(
        f"{BASE_URL}/api/v3/did/verify",
        json={"did": did}
    )
    return response.json()

print("Verifying DID...")
verification = verify_did(did["did"])
print(json.dumps(verification, indent=2))

# ============================================================
# 11. ESTABLISH TRUST
# ============================================================

def establish_trust(agent_a, agent_b):
    response = requests.post(
        f"{BASE_URL}/api/v3/trust/establish",
        json={"agent_a": agent_a, "agent_b": agent_b}
    )
    return response.json()

print("Establishing trust...")
trust = establish_trust(did["did"], "did:vireo:bob-1")
print(json.dumps(trust, indent=2))
Security in Python
python
# ============================================================
# 12. GENERATE KEYS
# ============================================================

def generate_keys():
    response = requests.post(f"{BASE_URL}/api/crypto/generate_keys")
    return response.json()

print("Generating keys...")
keys = generate_keys()
print(json.dumps(keys, indent=2))

# ============================================================
# 13. SIGN MESSAGE
# ============================================================

def sign_message(message):
    response = requests.post(
        f"{BASE_URL}/api/crypto/sign",
        json={"message": message}
    )
    return response.json()

print("Signing message...")
signature = sign_message("Hello Vireo v3.0.0!")
print(json.dumps(signature, indent=2))

# ============================================================
# 14. VERIFY SIGNATURE
# ============================================================

def verify_signature(signature, message):
    response = requests.post(
        f"{BASE_URL}/api/crypto/verify",
        json={"signature": signature, "message": message}
    )
    return response.json()

print("Verifying signature...")
verification = verify_signature(signature["full_signature"], "Hello Vireo v3.0.0!")
print(json.dumps(verification, indent=2))
📋 AVAILABLE URLs
URL	Description
http://localhost:5000/	API Home
http://localhost:5000/web	Web Interface
http://localhost:5000/docs	Documentation
http://localhost:5000/api/health	Health Check
http://localhost:5000/api/docs	API Documentation
http://localhost:5000/api/v3/metrics	Metrics
🛑 HOW TO STOP
Press Ctrl+C in the PowerShell window where the server is running.

🌿 THE NORTH STAR
"Don't prove that Vireo can run more AI models. Prove that Vireo can make independently implemented AI agents interoperable."

🌿 Vireo v3.0.0 — The World's First AI-to-AI Communication Language 🚀