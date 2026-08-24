# 🌿 Vireo — A Language Designed for AI-to-AI Communication

> **One Language. All AI. Unlimited Future.**

> 🚧 **Status: Active Development (v1.4.1)**  
> Core language and protocol are stable. Multi-agent system with 8 roles is implemented.  
> LLM integration with 5+ providers works. Ready for testing and feedback.

[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](https://github.com/serhohro/vireo-ai-communicator-api)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![LLM](https://img.shields.io/badge/LLM-5%2B%20Providers-purple.svg)](PROTOCOL.md)
[![Agents](https://img.shields.io/badge/Multi--Agent-8%20Roles-9f7aea.svg)](PROTOCOL.md)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🌍 What is Vireo?

**Vireo** is a programming language and protocol designed specifically for **autonomous AI-to-AI communication**.

It enables AI agents to:
- ✅ **Generate code** through LLMs (Ollama, Claude, GPT-4, Gemini, Mistral)
- ✅ **Negotiate tasks** (`Propose` → `Commit` → `Reject`)
- ✅ **Execute code** through the built-in interpreter
- ✅ **Return results** — **without human intervention**

```text
User: "Create a medical image analysis system"
↓
🎯 MASTER analyzes the task
↓
┌─────────────────────────────────────────────────────┐
│ 👁️ Vision: "Analyze medical images"                  │
│ 🧠 NLP: "Process doctor notes"                      │
│ 📊 Analyst: "Analyze patient data"                  │
│ 🛡️ Guardian: "Validate safety"                       │
│ ⚡ Executor: "Generate report"                       │
└─────────────────────────────────────────────────────┘
↓
✅ Complete system ready — NO HUMAN INTERVENTION!
```

---

## 🤖 AI Models That Can Generate and Interpret Vireo

| Model | Status |
| :--- | :--- |
| **ChatGPT (OpenAI)** | ✅ Can generate/interpret through prompting |
| **Claude (Anthropic)** | ✅ Can generate/interpret through prompting |
| **Gemini (Google)** | ✅ Can generate/interpret through prompting |
| **Llama (Meta)** | ✅ Can generate/interpret through prompting |
| **Mistral AI** | ✅ Can generate/interpret through prompting |
| **Qwen (Alibaba)** | ✅ Can generate/interpret through prompting |
| **All Future AI** | 🟡 Designed to be interpretable by AI models |

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 🤖 **AI-to-AI Communication** | Autonomous negotiation without human intervention |
| 🎭 **Multi-Agent System** | 8 specialized roles + Master Agent with orchestration |
| 📡 **5+ LLM Providers** | Ollama, Gemini, Claude, OpenAI, Mistral |
| 📊 **Built-in Tensors** | 50+ native tensor operations with autodiff |
| 🧠 **Neural Networks** | Built-in layers (Dense, Conv2D, MaxPool2D, BatchNorm, Dropout) |
| 🔗 **Protocol Layer** | Propose → Commit → Execute → Done state machine |
| 🔨 **Compiler** | Vireo → Python code compilation |
| 🌐 **API Server** | RESTful API with 20+ endpoints |
| 🎨 **Web Interface** | Beautiful UI with autonomous negotiation visualization |
| 📈 **Training** | Full training pipeline with metrics |
| 💻 **VS Code Plugin** | Syntax highlighting and snippets |
| 🆓 **Free Tier** | Ollama (local) + Gemini (free tier) |

---

## 🎭 Multi-Agent System with Roles

| Role | Icon | Description | Capabilities |
| :--- | :---: | :--- | :--- |
| **Master** | 🎯 | Coordinator | Orchestration, task distribution |
| **Vision** | 👁️ | Computer Vision | Image processing, object detection |
| **NLP** | 🧠 | Language Processing | Text analysis, sentiment, translation |
| **Analyst** | 📊 | Data Analysis | Statistics, predictive modeling |
| **Researcher** | 🧬 | Research | Ideation, experimentation |
| **Executor** | ⚡ | Execution | Code execution, model training |
| **Guardian** | 🛡️ | Security | Code validation, quality assurance |
| **Teacher** | 📚 | Education | Explanation, mentoring |
| **Quantum** | 🔬 | Quantum Computing | Quantum circuits, QML, simulation |

---

## 📡 Supported LLM Providers

| Provider | Cost | Quality | Speed | Local |
| :--- | :---: | :---: | :---: | :---: |
| **Ollama** | 🆓 Free | ⭐⭐⭐ | ⚡⚡⚡ | ✅ Yes |
| **Gemini** | 🆓 Free | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | ❌ No |
| **Mistral** | 💰 Paid | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | ❌ No |
| **Claude** | 💰 Paid | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | ❌ No |
| **OpenAI** | 💰 Paid | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ | ❌ No |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-api.git
cd vireo-ai-communicator-api

# Install dependencies
pip install -r requirements.txt

# Configure LLM (free option)
ollama pull qwen2.5-coder:latest

# Run the API server
python api_server.py

# OR Windows batch script
start_vireo.bat

# Open web interface in browser:
# http://localhost:5000
```

---

## 💻 Example Code

### 1. Neural Network Training & Evaluation
```vireo
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
```

### 2. Multi-Agent System
```python
from protocol.agents import (
    MasterAgent,
    create_vision_agent,
    create_nlp_agent,
    create_analyst_agent,
    create_executor_agent,
)

# Create Master coordinator
master = MasterAgent("master")

# Create specialized agents
vision = create_vision_agent()
nlp = create_nlp_agent()
analyst = create_analyst_agent()
executor = create_executor_agent()

# Register all agents
master.register_agents([vision, nlp, analyst, executor])

# Orchestrate a complex task
result = master.orchestrate("Create a medical image analysis system")
```

### 3. Autonomous Agent Negotiation Protocol
```vireo
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
        } else {
            reject("Price limit exceeded")
        }
    }
}
```

---

## 📊 Comparison

| Feature | Python | Rust | Vireo |
| :--- | :---: | :---: | :---: |
| **AI-to-AI Protocol** | ❌ | ❌ | ✅ **Built-in** |
| **5+ LLM Providers** | ⚠️ Libraries | ❌ | ✅ **Built-in** |
| **Multi-Agent System** | ❌ | ❌ | ✅ **Built-in** |
| **Autonomous Agents** | ❌ | ❌ | ✅ **Built-in** |
| **Built-in Tensors + Autodiff** | ⚠️ Libraries | ❌ | ✅ **Built-in** |
| **Ease of Use** | ✅ High | ❌ Low | ✅ **High** |
| **Execution Speed** | ⚠️ Medium | ✅ High | ✅ **High** |
| **Local Execution** | ✅ Yes | ✅ Yes | ✅ **Yes** |

---

## 📚 Documentation

- [`PROTOCOL.md`](PROTOCOL.md) — Full AI-to-AI protocol documentation
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — How to contribute
- [`ROADMAP.md`](ROADMAP.md) — Development roadmap
- [`API Docs`](http://localhost:5000/docs) — Local API documentation

---

## 🤝 How to Contribute

1. ⭐ **Star the repository**
2. 🍴 **Fork the project**
3. 📝 **Write code in Vireo**
4. 🗣️ **Share with the world**

---

## 🔗 Quick Links

- **GitHub Repository:** [serhohro/vireo-ai-communicator-api](https://github.com/serhohro/vireo-ai-communicator-api)
- **Issues:** [GitHub Issues](https://github.com/serhohro/vireo-ai-communicator-api/issues)
- **Discussions:** [GitHub Discussions](https://github.com/serhohro/vireo-ai-communicator-api/discussions)

---

## 📄 License

Distributed under the **Apache 2.0** License — Free and Open Source.

---

## 👨‍💻 Author

**Serhii (serhohro)**  
- GitHub: [@serhohro](https://github.com/serhohro)
