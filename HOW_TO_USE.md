markdown
# 🌿 How to Work with Vireo — Complete Guide

**Version:** 2.0.1  
**Last Updated:** 2026-09-02

---

## 📋 Table of Contents

1. [Installation](#1-installation)
2. [Starting the Server](#2-starting-the-server)
3. [Web Interface](#3-web-interface)
4. [Creating Agents](#4-creating-agents)
5. [Adding Capabilities](#5-adding-capabilities)
6. [Autonomous Communication](#6-autonomous-communication)
7. [Creating Contracts](#7-creating-contracts)
8. [Working with LLM Providers](#8-working-with-llm-providers)
9. [API Endpoints](#9-api-endpoints)
10. [Examples](#10-examples)
11. [FAQ](#11-faq)

---

## 1. Installation

### Requirements
- Python 3.9+
- Redis (for multi-agent communication)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-api.git
cd vireo-ai-communicator-3

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
# Edit .env with your API keys

# 4. Start Redis (if using)
redis-server
2. Starting the Server
Method 1: Via start_vireo.bat (Windows)
Simply double-click start_vireo.bat

Method 2: Via Command Line
bash
python api_server.py
Method 3: Via PowerShell
powershell
python api_server.py
After starting:
text
🌿 VIREO API SERVER v2.0.1
📍 Server: http://localhost:5000
🌐 Web:    http://localhost:5000/web
📚 Docs:   http://localhost:5000/docs
📡 API:    http://localhost:5000/api/health
📖 API Docs: http://localhost:5000/api/docs
3. Web Interface
Open in browser: http://localhost:5000/web

Available Tabs:
Tab	Description
🤖 Autonomous	Autonomous AI-to-AI communication
🧠 Agents	Agent management
📜 Contracts	Create and execute contracts
▶️ Execute	Execute Vireo code
🧠 Neural	Create neural networks
📡 Providers	List of LLM providers
💬 Chat	Chat with AI models
🎭 Roles	Agent roles
🔐 Security	Cryptography & security
🧠 Models	Model management
4. Creating Agents
Via Web Interface:
Go to 🧠 Agents tab

Enter Agent ID (e.g., agent-vision)

Enter Model (e.g., qwen2.5-coder:latest)

Click 📝 Register

Via API (curl):
bash
curl -X POST http://localhost:5000/api/agent/register \
  -H "Content-Type: application/json" \
  -d '{"id": "agent-vision", "model": "qwen2.5-coder:latest"}'
Via Python:
python
import requests

response = requests.post(
    'http://localhost:5000/api/agent/register',
    json={'id': 'agent-vision', 'model': 'qwen2.5-coder:latest'}
)
print(response.json())
5. Adding Capabilities
Via Web Interface:
On 🧠 Agents tab find your agent

In Capability name field enter name (e.g., analyze_images)

Click 📌 Add Capability

Via API:
bash
curl -X POST http://localhost:5000/api/agent/agent-vision/capability \
  -H "Content-Type: application/json" \
  -d '{"name": "analyze_images", "description": "Analyze medical images"}'
List Agents:
bash
curl http://localhost:5000/api/agent/list
Agent Status:
bash
curl http://localhost:5000/api/agent/agent-vision/status
6. Autonomous Communication
Via Web Interface:
Go to 🤖 Autonomous tab

Select:

Agent (Proposer): agent-vision

Agent (Executor): agent-training

LLM Provider: 🔥 Mistral AI

Task Description: Create a neural network for MNIST classification

Click 🚀 Start Autonomous Negotiation

Via API:
bash
curl -X POST http://localhost:5000/api/llm/agent/agent-vision/auto_negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "agent-training",
    "task": "Create a neural network for MNIST classification",
    "provider": "mistral"
  }'
7. Creating Contracts
Via Web Interface:
Go to 📜 Contracts tab

Fill in fields:

Parties: agent-vision, agent-training

Max Tokens: 1000

Timeout: 60

Obligations: (JSON)

Click 📝 Create Contract

Via API:
bash
curl -X POST http://localhost:5000/api/v2/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "parties": ["agent-vision", "agent-training"],
    "terms": {"max_tokens": 1000, "timeout_sec": 60},
    "obligations": {
      "agent-vision": {
        "action": "analyze_images",
        "input": {"image": "MNIST_sample.png"}
      },
      "agent-training": {
        "action": "train_model",
        "input": {"data": "$ref.agent-vision.result"}
      }
    }
  }'
Execute Contract:
bash
curl -X POST http://localhost:5000/api/v2/contracts/contract-1/execute
Verify Contract:
bash
curl -X POST http://localhost:5000/api/v2/contracts/contract-1/verify
8. Working with LLM Providers
Available Providers:
Provider	Models	Type
Ollama	qwen2.5-coder:latest, llama3.1:latest	🆓 Local
Mistral AI	mistral-large-latest, mistral-medium-latest	🇪🇺 European
OpenAI	gpt-4, gpt-4-turbo, gpt-3.5-turbo	💰 Paid
Gemini	gemini-1.5-pro	🌟 Google
Claude	claude-3-sonnet-20241022	💰 Anthropic
Get Provider List:
bash
curl http://localhost:5000/api/providers
Using Mistral AI:
bash
curl -X POST http://localhost:5000/api/mistral/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain AI-to-AI communication", "model": "mistral-large-latest"}'
9. API Endpoints
Main Endpoints:
Method	URL	Description
GET	/	Home page
GET	/web	Web interface
GET	/api/health	Health check
GET	/api/providers	List LLM providers
POST	/api/agent/register	Register agent
GET	/api/agent/list	List agents
GET	/api/agent/{id}/status	Agent status
POST	/api/agent/{id}/capability	Add capability
POST	/api/llm/agent/{id}/auto_negotiate	Autonomous communication
POST	/api/v2/contracts	Create contract
GET	/api/v2/contracts/{id}	Get contract
POST	/api/v2/contracts/{id}/execute	Execute contract
POST	/api/v2/contracts/{id}/verify	Verify contract
POST	/api/crypto/generate_keys	Generate keys
POST	/api/crypto/sign	Sign message
GET	/models/list	List models
10. Examples
Example 1: Create Agent with Capability
python
import requests

# Create agent
requests.post('http://localhost:5000/api/agent/register',
    json={'id': 'analyst', 'model': 'qwen2.5-coder:latest'})

# Add capability
requests.post('http://localhost:5000/api/agent/analyst/capability',
    json={'name': 'analyze_data', 'description': 'Data analysis'})
Example 2: Autonomous Communication
python
import requests

response = requests.post(
    'http://localhost:5000/api/llm/agent/agent-vision/auto_negotiate',
    json={
        'recipient': 'agent-training',
        'task': 'Create a neural network',
        'provider': 'mistral'
    }
)
print(response.json())
Example 3: Contract
python
import requests

# Create contract
contract = requests.post('http://localhost:5000/api/v2/contracts',
    json={
        'parties': ['agent-vision', 'agent-training'],
        'terms': {'max_tokens': 1000},
        'obligations': {
            'agent-vision': {'action': 'analyze_images', 'input': {}},
            'agent-training': {'action': 'train_model', 'input': {}}
        }
    }
).json()

contract_id = contract['contract_id']

# Execute
requests.post(f'http://localhost:5000/api/v2/contracts/{contract_id}/execute')

# Verify
requests.post(f'http://localhost:5000/api/v2/contracts/{contract_id}/verify')
11. FAQ
❓ How to add a new LLM provider?
Add the provider to protocol/llm_provider.py and update .env.

❓ Where are keys stored?
Keys are stored in the keys/ folder (created automatically).

❓ How to reset all data?
Delete files: keys/, restart server (clears _agents, _contracts).

❓ Can I use it without Redis?
Yes, use In-Memory transport (default).

❓ How to add a new agent role?
Add role in core/roles.py and update the ROLES dictionary.

📚 Additional Resources
QUICKSTART.md — Quick Start

TUTORIAL.md — Full Tutorial

README.md — Overview

PROTOCOL.md — Protocol Specification

🌿 Vireo v2.0.1 — The World's First AI-to-AI Communication Language