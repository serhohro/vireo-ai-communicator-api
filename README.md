markdown
# 🌿 Vireo — The World's First AI-to-AI Communication Language

**Vireo is a programming language + protocol for secure AI-to-AI communication, negotiation, and coordination.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-v2.0.1-green.svg)](CHANGELOG.md)

---

## 🎯 Vision

> **"LLMs provide intelligence. Vireo provides structure, execution, verification and interoperability."**

Vireo enables autonomous AI agents to:
- **Discover** each other's capabilities
- **Negotiate** contracts and terms
- **Execute** tasks collaboratively
- **Verify** results cryptographically
- **Escalate** issues when needed

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-api.git
cd vireo-ai-communicator-3

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Start the system
python start_vireo.bat
# Or: python api/server.py
Write Your First Agent
python
from protocol.agents.base_agent import BaseAgent
from protocol.contract import Contract

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="analyst", capabilities=["analyze", "report"])
    
    def analyze(self, data):
        return {"result": f"Analysis of {data}"}

# Create and run agent
agent = MyAgent()
agent.start()
Write a Vireo Program
vireo
// hello_world.v
agent "greeter" {
    capability "greet" {
        input: name: string
        output: message: string
        action: "Hello, {name}!"
    }
}

contract "greeting_contract" {
    parties: [greeter, client]
    terms: {
        max_tokens: 100
        timeout_sec: 30
    }
}

## 📖 Learn More

- **[QUICKSTART.md](docs/QUICKSTART.md)** — Get started in 5 minutes
- **[TUTORIAL.md](docs/TUTORIAL.md)** — Complete tutorial with 5 parts
- **[HOW_TO_USE.md](HOW_TO_USE.md)** — Full guide on how to work with Vireo 🆕
- **[EU_LLM_GUIDE.md](docs/EU_LLM_GUIDE.md)** — European LLM providers
     execute greet("World") -> result

🏗️ Architecture
text
┌─────────────────────────────────────────────────────────────┐
│                        Application                          │
├─────────────────────────────────────────────────────────────┤
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │   Agent A   │    │   Agent B   │    │   Agent C   │     │
│   │  (Python)   │    │   (Rust)    │    │   (JS)      │     │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│          │                  │                  │            │
│          └──────────────────┼──────────────────┘            │
│                             │                               │
│                   ┌─────────▼─────────┐                     │
│                   │   Vireo Protocol  │                     │
│                   │  (Control Plane)  │                     │
│                   └─────────┬─────────┘                     │
│                             │                               │
│          ┌──────────────────┼──────────────────┐            │
│          │                  │                  │            │
│   ┌──────▼──────┐   ┌───────▼───────┐   ┌──────▼──────┐     │
│   │   LLM       │   │   Transport   │   │   Crypto    │     │
│   │  (Reasoning)│   │  (A2A/MCP)    │   │  (Ed25519)  │     │
│   └─────────────┘   └───────────────┘   └─────────────┘     │
├─────────────────────────────────────────────────────────────┤
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Specification: LANGUAGE.md · PROTOCOL.md · AST.md  │   │
│   │  WIRE_FORMAT.md · CONTRACTS.md · TRUST_BOOTSTRAP.md │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
🔄 Lifecycle

DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE
     │              │            │            │            │
     ├→ REJECTED   ├→ REJECTED  ├→ CANCELLED ├→ FAILED   ├→ ESCALATED
     └→ TIMEOUT     └→ TIMEOUT   └→ TIMEOUT    └→ TIMEOUT
📁 Project Structure

vireo-ai-communicator-3/
├── README.md                 # This file
├── CHANGELOG.md              # Release notes
├── ROADMAP.md                # Development roadmap
├── PROTOCOL.md               # Protocol specification
├── SECURITY.md               # Security model
├── GOVERNANCE.md             # Governance & RFC process
├── AI_EVALUATIONS.md         # AI model evaluations
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── start_vireo.bat           # Startup script
│
├── specification/            # 📋 Formal specifications
│   ├── LANGUAGE.md
│   ├── PROTOCOL.md
│   ├── AST.md
│   ├── WIRE_FORMAT.md
│   ├── CONTRACTS.md
│   ├── TRUST_BOOTSTRAP.md
│   └── INTEROPERABILITY.md
│
├── core/                     # 🧠 Core implementation
│   ├── agent/                # Agent base & registry
│   ├── protocol/             # Protocol states & messages
│   ├── contract/             # Contract validation
│   ├── capability/           # Capability discovery
│   ├── identity/             # Identity & trust bootstrap
│   ├── execution/            # Execution runner
│   └── verification/         # Verification engine
│
├── language/                 # 📝 Vireo language
│   ├── grammar.lark          # Formal grammar
│   ├── parser.py             # Parser
│   ├── ast.py                # AST nodes
│   ├── codegen.py            # Code generator
│   ├── validator.py          # AST validator
│   └── stdlib/               # Standard library
│
├── protocol/                 # 🔌 Protocol implementation
│   ├── agents/               # Agent implementations
│   ├── transport/            # Redis, In-Memory
│   ├── llm_provider.py       # LLM integrations
│   └── llm_provider_eu.py    # 🇪🇺 European LLMs
│
├── api/                      # 🌐 REST API
│   ├── server.py             # FastAPI server
│   ├── routes.py             # API routes
│   └── models.py             # Pydantic models
│
├── docs/                     # 📚 Documentation
│   ├── QUICKSTART.md
│   ├── TUTORIAL.md
│   ├── EU_LLM_GUIDE.md
│   └── ...
│
├── evaluations/              # 📊 AI evaluations 
│   ├── ChatGPT.md            
│   ├── Perplexity.md
│   ├── Gemini.md
│   ├── Mistral.md
│   ├── Qwen.md
│   ├── Claude.md
│   └── Kimi.md
│
└── examples/                 # 💡 Example programs
    ├── hello_world.v
    ├── neural_network.v
    ├── agent_negotiation.v
    ├── multi_agent_medical.v
    └── ...
🗺️ Roadmap
Phase	Description	Status
v1.4.5	Hardening: 7 critical fixes, VERIFY/ESCALATE	✅ Done
v2.0.1	Specification: Formal language & protocol specs	🚧 In Progress
v2.1	Core: Trust Bootstrap, Core Agent, Verification	📅 Planned
v2.2	Interoperability: Python SDK, TypeScript SDK, Rust	📅 Planned
v3.0	Production: WASM runtime, GPU support, MCP	📅 Planned

🤖 AI Evaluations
Vireo has been evaluated by 7 leading AI models:

Model	Key Insight
ChatGPT	"Control plane, not just another framework"
Perplexity	"Standards are born from open specifications"
Gemini	"WASM runtime for true interoperability"
Mistral	"Only solution combining language + runtime + protocol"
Qwen	"Let PyTorch handle tensors; let Vireo handle trust"
Claude	"Change the code, then tell me, in that order"
Kimi	"Technical depth: VERIFY/ESCALATE, Trust Bootstrap"
See AI_EVALUATIONS.md for full details.

🔐 Security
Ed25519 cryptographic signatures

Trust Bootstrap Protocol for identity verification

Contract validation before execution

Sandboxing for untrusted code

Key rotation support

🌍 European AI Independence
Vireo natively supports European LLM providers:

🇫🇷 Mistral AI

🇩🇪 Aleph Alpha

🇨🇭 Cohere

🇬🇧 Stability AI

🇫🇷 LightOn

See EU_LLM_GUIDE.md

🤝 Contributing
We welcome contributions! Please see:

CONTRIBUTING.md — How to contribute

GOVERNANCE.md — RFC process & governance

CODE_OF_CONDUCT.md — Code of conduct

📄 License
Copyright © 2026 Serhii Hr

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

See LICENSE for details.

🔗 Links
GitHub: github.com/serhohro/vireo-ai-communicator-api

Issues: github.com/serhohro/vireo-ai-communicator-api/issues

Documentation: docs/

License: Apache 2.0