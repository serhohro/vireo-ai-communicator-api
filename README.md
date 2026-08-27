# 🌿 Vireo — The World's First AI-to-AI Communication Language

**An open-source programming language and protocol designed specifically for autonomous AI-agent communication, negotiation, contracts, and coordination.**

> 🧪 **Status: Active Development (v1.4.2)**  
> Core language, interpreter, protocol foundations, and multi-agent system are implemented.
> LLM integration with 5+ providers works. Cryptographic primitives are in place.
> Currently in active development — community feedback and contributions are welcome.

[![Version](https://img.shields.io/badge/version-1.4.2-blue.svg)](https://github.com/serhohro/vireo-ai-communicator-api)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![LLM](https://img.shields.io/badge/LLM-5%2B%20Providers-purple.svg)](PROTOCOL.md)
[![Agents](https://img.shields.io/badge/Multi--Agent-7%2B%20Roles-9f7aea.svg)](PROTOCOL.md)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Crypto](https://img.shields.io/badge/Crypto-Ed25519%20Primitives-orange.svg)](PROTOCOL.md)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🌍 What is Vireo?

**Vireo** is an open-source experimental programming language and protocol designed specifically for **autonomous AI-to-AI communication, negotiation, contracts, and coordination**.

It enables AI agents to:
- ✅ Generate code through LLMs (Ollama, Gemini, Claude, OpenAI, Mistral)
- ✅ Negotiate tasks (Propose → Commit → Reject → Negotiate)
- ✅ Execute code through the built-in interpreter
- ✅ Return results — **without human intervention**
- ✅ Use cryptographic primitives for secure messaging

**Current Version:** v1.4.2 (Experimental)
**License:** Apache 2.0

---

## 🎯 Core Concept

Vireo explores a different approach to AI-agent coordination:

> **Treat AI-to-AI communication, negotiation, trust, contracts, and execution as first-class programming concepts.**

Instead of:
Python application → framework → SDK → API → custom coordination code

text

Vireo enables:
Agent → Capability → Proposal → Contract → Negotiation → Authorization → Execution → Result

text

---

## 📊 Project Status (v1.4.2)

### ✅ Implemented (Working)

| Component | Status | Location |
|-----------|--------|----------|
| Vireo Interpreter | ✅ Implemented | `vireo_interpreter.py` |
| Vireo → Python Compiler | ✅ Implemented | `vireo_compiler.py` |
| Tensor Operations | ✅ Implemented | `tensor_ops.py` |
| Neural Network Layers | ✅ Implemented | Conv2D, MaxPool2D, BatchNorm, Flatten |
| Message Protocol | ✅ Implemented | `protocol/message.py` |
| State Machine | ✅ Implemented | `protocol/state.py` |
| Contracts (max_tokens, max_cost, timeout) | ✅ Implemented | `protocol/contract.py` |
| Capability Registry | ✅ Implemented | `protocol/capabilities.py` |
| Context Versioning | ✅ Implemented | `protocol/conflict.py` |
| HMAC Signatures | ✅ Implemented | `protocol/trust.py` |
| Nonce/Replay Protection | ✅ Implemented | `src/crypto/trust.py` |
| Ed25519 Primitives (keygen, sign, verify) | ✅ Implemented | `src/crypto/ed25519.py` |
| 5+ LLM Providers | ✅ Implemented | Ollama, Claude, OpenAI, Gemini, Mistral |
| Master Agent | ✅ Implemented | `protocol/agents/master_agent.py` |
| 7 Specialized Roles | ✅ Implemented | Vision, NLP, Analyst, Researcher, Executor, Guardian, Teacher |
| MCP Adapter | ✅ Implemented | `src/adapters/mcp_server.py` |
| LangChain Adapter | ✅ Implemented | `src/adapters/langchain.py` |
| Redis/Kafka/NATS Transport | ✅ Implemented | `src/transport/` |
| Web Interface | ✅ Implemented | 8 tabs in `web_interface.html` |
| REST API | ✅ Implemented | `api_server.py` |

### 🚧 In Development

| Component | Status | Target |
|-----------|--------|--------|
| Ed25519 Protocol Integration | 🟡 Partial | v1.5.0 |
| DID (Decentralized Identifiers) | 🟡 Partial | v1.5.0 |
| Autonomous Distributed Negotiation | 🟡 Partial | v1.5.0 |
| Quantum Role | 🔵 Planned | v1.5.0 |
| JIT Compilation (Native) | 🟠 Mock | v1.6.0 |
| WASM Compilation | 🟠 Mock | v1.6.0 |
| GPU Acceleration | 🟡 Partial | v1.6.0 |
| TLA+ Formal Verification | 🔵 Planned | v2.0.0 |
| Independent Runtime (Rust) | 🔵 Planned | v2.0.0 |

---

## 🔍 Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🤖 **AI-to-AI Communication** | Autonomous negotiation without human intervention | ✅ |
| 🎭 **Multi-Agent System** | 7+ specialized roles + Master Agent | ✅ |
| 📡 **5+ LLM Providers** | Ollama, Gemini, Claude, OpenAI, Mistral | ✅ |
| 📊 **Built-in Tensors** | 50+ native tensor operations | ✅ |
| 🧠 **Neural Networks** | Built-in layers (Dense, Conv2D, MaxPool2D, BatchNorm, Dropout) | ✅ |
| 🔗 **Protocol Layer** | Propose → Commit → Execute → Done state machine | ✅ |
| 🔨 **Compiler** | Vireo → Python code compilation | ✅ |
| 🌐 **API Server** | RESTful API with 20+ endpoints | ✅ |
| 🎨 **Web Interface** | 8 tabs with autonomous negotiation visualization | ✅ |
| 🔐 **Cryptography Primitives** | Ed25519 key generation, signing, verification | ✅ |
| 🧪 **Trust Protocol** | HMAC signatures, nonce protection | ✅ |
| 🆓 **Free Tier** | Ollama (local) + Gemini (free tier) | ✅ |
| ⚡ **JIT Compilation** | LLVM backend for performance | 🚧 |
| 🌍 **WASM** | WebAssembly compilation for sandboxed execution | 🚧 |

---

## 🎭 Multi-Agent System with Roles

| Role | Icon | Description | Status |
|------|------|-------------|--------|
| **Master** | 🎯 | Coordinator | ✅ |
| **Vision** | 👁️ | Computer Vision | ✅ |
| **NLP** | 🧠 | Language Processing | ✅ |
| **Analyst** | 📊 | Data Analysis | ✅ |
| **Researcher** | 🧬 | Research | ✅ |
| **Executor** | ⚡ | Execution | ✅ |
| **Guardian** | 🛡️ | Security | ✅ |
| **Teacher** | 📚 | Education | ✅ |
| **Quantum** | 🔬 | Quantum Computing | 🚧 Planned |

### Creating Agents with Roles

```python
from protocol.agents import (
    MasterAgent,
    create_vision_agent,
    create_nlp_agent,
    create_analyst_agent,
    create_executor_agent,
)

master = MasterAgent("master")
vision = create_vision_agent()
nlp = create_nlp_agent()
analyst = create_analyst_agent()
executor = create_executor_agent()

master.register_agents([vision, nlp, analyst, executor])
result = master.orchestrate("Create a medical image analysis system")
---
📡 Supported LLM Providers
Provider	Cost	   Quality	    Speed	      Local	Status
Ollama	    🆓 Free	  ⭐⭐⭐	   ⚡⚡⚡	      ✅ Yes	✅
Gemini	    🆓 Free	  ⭐⭐⭐⭐	⚡⚡⚡⚡	  ❌ No	✅
Mistral	    💰 Paid	  ⭐⭐⭐⭐	⚡⚡⚡⚡	  ❌ No	✅
Claude	    💰 Paid	  ⭐⭐⭐⭐⭐	⚡⚡⚡	      ❌ No	✅
OpenAI	    💰 Paid	  ⭐⭐⭐⭐⭐	⚡⚡⚡⚡	  ❌ No	✅
---
🔐 Security & Trust
Vireo includes cryptographic primitives for secure AI-to-AI communication:

🔑 Ed25519 Primitives — Key generation, signing, verification (implemented)

🔏 HMAC Signatures — Symmetric message authentication (implemented)

🔐 Nonce Protection — Replay attack prevention (implemented)

🧪 Trust Protocol — Identity and trust primitives (in development)

🔬 DID — Decentralized Identifiers (in development)

🚀 Quick Start
bash
# 1. Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-api.git
cd vireo-ai-communicator-api

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure LLM (free option)
ollama pull qwen2.5-coder:latest

# 4. Run the API server
python api_server.py
# OR Windows batch script
start_vireo.bat

# 5. Open web interface
# http://localhost:5000/web
---
💻 Example Code
1. Neural Network Training
vireo
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
    loss CrossEntropy
    optimizer Adam(lr=0.001)
}

train MNIST {
    data = "mnist"
    epochs = 10
    batch_size = 64
    lr = 0.001
}

predict MNIST {
    data = "test"
}

evaluate MNIST {
    data = "test"
    metrics = [accuracy, precision, recall, f1]
}
2. Autonomous Agent Negotiation
vireo
agent WeatherAgent {
    identity: "did:key:z6MkhaXk1BZ4fGqFqQrZ..."
}

contract ComputeAgreement {
    payload: TaskPayload,
    max_price_tokens: Int,
    deadline_sec: Int
}

negotiation SecureComputeNegotiation {
    party Initiator: WeatherAgent
    party Provider: ComputeProvider

    timeout = 10s
    max_rounds = 5

    on offer(Agreement: ComputeAgreement) {
        if Agreement.max_price_tokens <= 500 {
            accept(Agreement)
        } else if negotiation.round < negotiation.max_rounds {
            propose(counter_offer)
        } else {
            reject("Price limit exceeded")
        }
    }
}
---
📊 Comparison: Python vs Vireo
Aspect	                    Python (PyTorch)	    Vireo
Lines of Code	            30+ lines	            5 lines
External Libraries	        3+ required	            None (built-in)
Data Loading	            Manual	                Built-in
Training Loop	            Manual	                Declarative
Agent Communication	        ❌ Not built-in	        ✅ Built-in
Cryptography	            ❌ External library	    ✅ Built-in Primitives
Multi-Agent Orchestration	❌ Custom code needed	✅ Built-in (7+ roles + Master)
---
📚 Documentation
PROTOCOL.md — Full AI-to-AI protocol specification

CONTRIBUTING.md — How to contribute

ROADMAP.md — Development roadmap

TROUBLESHOOTING.md — Common issues and solutions

API docs — Local documentation at http://localhost:5000/docs

🤝 How to Contribute
⭐ Star the repository

🍴 Fork the project

📝 Write code in Vireo

🗣️ Share with the world

📄 License
Apache 2.0 — Free and Open Source

👨‍💻 Author
Serhii (serhohro)

GitHub: @serhohro

🌿 Vireo — A Language Designed for AI-to-AI Communication
