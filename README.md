# 🌿 Vireo — The World's First AI-to-AI Communication Language

**One Language. All AI. Unlimited Future.**

> 🚧 **Status: Stable Release (v1.4.2)**  
> Core language and protocol are stable. Multi-agent system with 8 roles is fully implemented.
> LLM integration with 5+ providers works. Real cryptography Ed25519 integrated.
> Ready for production testing and feedback.

[![Version](https://img.shields.io/badge/version-1.4.1-blue.svg)](https://github.com/serhohro/vireo-ai-communicator-api)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![LLM](https://img.shields.io/badge/LLM-5%2B%20Providers-purple.svg)](PROTOCOL.md)
[![Agents](https://img.shields.io/badge/Multi--Agent-8%20Roles-9f7aea.svg)](PROTOCOL.md)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Crypto](https://img.shields.io/badge/Crypto-Ed25519-orange.svg)](PROTOCOL.md)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🌍 What is Vireo?

**Vireo** is the world's first programming language designed specifically for **autonomous AI-to-AI communication**.

It enables AI agents to:
- ✅ Generate code through LLMs (Ollama, Claude, GPT-4, Gemini, Mistral)
- ✅ Negotiate tasks (Propose → Commit → Reject → Negotiate)
- ✅ Execute code through the built-in interpreter
- ✅ Return results — **without human intervention**
- ✅ Sign and verify messages with **Ed25519 cryptography**

---

## 🤖 AI Models That Can Generate and Interpret Vireo

| Model | Status |
|-------|--------|
| **ChatGPT (OpenAI)** | ✅ Can generate/interpret through prompting |
| **Claude (Anthropic)** | ✅ Can generate/interpret through prompting |
| **Gemini (Google)** | ✅ Can generate/interpret through prompting |
| **Llama (Meta)** | ✅ Can generate/interpret through prompting |
| **Mistral AI** | ✅ Can generate/interpret through prompting |
| **Qwen (Alibaba)** | ✅ Can generate/interpret through prompting |
| **All Future AI** | 🟡 Designed to be interpretable by AI models |

📚 [Full AI model evaluations →](docs/validation/)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-to-AI Communication** | Autonomous negotiation without human intervention |
| 🎭 **Multi-Agent System** | 8 specialized roles + Master Agent with orchestration |
| 📡 **5+ LLM Providers** | Ollama, Gemini, Claude, OpenAI, Mistral |
| 📊 **Built-in Tensors** | 50+ native tensor operations with autodiff |
| 🧠 **Neural Networks** | Built-in layers (Dense, Conv2D, MaxPool2D, BatchNorm, Dropout) |
| 🔗 **Protocol Layer** | Propose → Commit → Execute → Done state machine |
| 🔨 **Compiler** | Vireo → Python code compilation |
| 🌐 **API Server** | RESTful API with 20+ endpoints |
| 🎨 **Web Interface** | Beautiful UI with 8 tabs and autonomous negotiation visualization |
| 🔐 **Real Cryptography** | Ed25519 key generation, signing, verification, Trust Protocol |
| 📈 **Training** | Full training pipeline with metrics |
| 💻 **VS Code Plugin** | Syntax highlighting and snippets |
| 🆓 **Free Tier** | Ollama (local) + Gemini (free tier) |

---

## 🎭 Multi-Agent System with Roles

| Role | Icon | Description | Capabilities |
|------|------|-------------|--------------|
| **Master** | 🎯 | Coordinator | Orchestration, task distribution |
| **Vision** | 👁️ | Computer Vision | Image processing, object detection |
| **NLP** | 🧠 | Language Processing | Text analysis, sentiment, translation |
| **Analyst** | 📊 | Data Analysis | Statistics, predictive modeling |
| **Researcher** | 🧬 | Research | Ideation, experimentation |
| **Executor** | ⚡ | Execution | Code execution, model training |
| **Guardian** | 🛡️ | Security | Code validation, quality assurance |
| **Teacher** | 📚 | Education | Explanation, mentoring |
| **Quantum** | 🔬 | Quantum Computing | Quantum circuits, QML, simulation |

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
📡 Supported LLM Providers
Provider	Cost	Quality	Speed	Local
Ollama	🆓 Free	⭐⭐⭐	⚡⚡⚡	✅ Yes
Gemini	🆓 Free	⭐⭐⭐⭐	⚡⚡⚡⚡	❌ No
Mistral	💰 Paid	⭐⭐⭐⭐	⚡⚡⚡⚡	❌ No
Claude	💰 Paid	⭐⭐⭐⭐⭐	⚡⚡⚡	❌ No
OpenAI	💰 Paid	⭐⭐⭐⭐⭐	⚡⚡⚡⚡	❌ No
🔐 Security & Trust
Vireo includes real Ed25519 cryptography for secure AI-to-AI communication:

🔑 Key Generation — Ed25519 public/private key pairs

🔏 Signing — Digital signatures for messages

🔐 Verification — Verify message authenticity and integrity

🧪 Trust Protocol — Zero-trust protocol for agent communication

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
3. Multi-Agent System (Python)
python
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
📊 Comparison
Feature	Python	Rust	Vireo
AI-to-AI Protocol	❌	❌	✅ Built-in
5+ LLM Providers	⚠️ Libraries	❌	✅ Built-in
Multi-Agent System	❌	❌	✅ Built-in
Autonomous Agents	❌	❌	✅ Built-in
Built-in Tensors + Autodiff	⚠️ Libraries	❌	✅ Built-in
Real Cryptography	⚠️ Libraries	⚠️ Libraries	✅ Built-in
Ease of Use	✅ High	❌ Low	✅ High
Local Execution	✅ Yes	✅ Yes	✅ Yes
🚧 What's in Development
🔨 LSTM Support — Adding recurrent layers

🔨 JIT Compilation — LLVM backend for performance

🔨 GPU Support — CUDA/ROCm acceleration

🔨 WebAssembly — WASM compilation for sandboxed execution

🔨 ONNX Integration — Model interoperability

📚 Documentation
PROTOCOL.md — Full AI-to-AI protocol documentation

CONTRIBUTING.md — How to contribute

ROADMAP.md — Development roadmap

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
