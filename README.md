🌿 Vireo — The World's First AI-to-AI Communication Language
Version: v1.4.5

Vireo is the first programming language designed specifically for autonomous AI-to-AI communication, negotiation, and collaboration — without human intervention.

🧪 Status: Research Prototype (v1.4.5)
The language core, interpreter, and multi-agent system are implemented. Protocol foundations are in active development. The autonomous negotiation flow (propose → commit → execute → inform) is working. The transport layer (Redis) is being integrated for distributed communication.

---
## 🌍 What is Vireo?

**Vireo is a programming language — not just a protocol.**

Unlike protocols (MCP, A2A) that only define how machines talk, Vireo gives AI agents a **complete language** to communicate, negotiate, and execute.

| Protocols (MCP, A2A)            | Vireo (Language)            |
|----------------------           |------------------           |
| Agent discovery & communication | Agent intent & coordination |
| Tool access & context           | Contracts & negotiation     |
| Message passing                 | Executable semantics        |
| Transport layer                 | Control plane               |
| For machines                    | For humans AND machines     |
---
## ✨ Features
- **🌐 Programming Language** — Full language with formal grammar
- **🧠 5+ LLM Providers** — Ollama, Gemini, Claude, OpenAI, Mistral
- **🎭 8 Agent Roles** — Master, Vision, NLP, Analyst, Researcher, Executor, Guardian, Teacher
- **🔐 Ed25519 Cryptography** — Real cryptographic identity and signatures
- **📜 Formal Grammar** — Lark-based grammar for Vireo language
- **🔄 Autonomous Negotiation** — propose → commit → execute → inform
- **📊 Tensor Operations** — Built-in tensor and neural network support
- **🧠 Pretrained Models** — ResNet, BERT, GPT-2 via PyTorch/Transformers
- **🌍 Multi-Language** — 🇺🇦 Ukrainian and 🇬🇧 English

---

## 🚀 Quick Examples

### Neural Network in 5 Lines
```vireo
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
}
Agent Negotiation
vireo
agent Vision {
    capability image_analysis
    role analyst
}

agent Training {
    capability model_training
    role executor
}

negotiate Vision -> Training {
    propose "Analyze 1000 images"
    commit "Training model on dataset"
    inform "Accuracy: 94.5%"
}
Tensor Operations
vireo
let a = Tensor([1, 2, 3])
let b = Tensor([4, 5, 6])
let c = a + b          // Tensor([5, 7, 9])
let d = a.matmul(b.T)  // Matrix multiplication
print(d)
🚀 Getting Started
Quick Start
bash
# Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-api.git

# Install dependencies
pip install -r requirements.txt

# Run the server
python api_server.py
Run with Docker
bash
docker-compose up
Use the Web Interface
Open http://localhost:5000/web

Windows Users
Double-click start_vireo.bat

📁 Project Structure
text
vireo-ai-communicator-3/
├── api_server.py          # Main Flask server
├── web_interface.html     # Web UI
├── start_vireo.bat        # Windows launcher
├── language/              # 🌐 Language core
│   ├── grammar.lark       # Formal grammar
│   ├── syntax.md          # Language syntax
│   ├── stdlib/            # Standard library
│   └── examples/          # Language examples
├── protocol/              # 🔗 Protocol layer
│   ├── agent.py           # Agent implementation
│   ├── llm_provider.py    # LLM providers
│   └── transport/         # Transport layer
└── src/                   # 🛠️ Core components
    ├── crypto/            # Ed25519 cryptography
    └── runtime/           # Runtime engine
📚 Documentation
Document	Description
README.md	Project overview (this file)
PROTOCOL.md	Protocol specification
language/syntax.md	Language syntax
CHANGELOG.md	Version history
ROADMAP.md	Development roadmap
CONTRIBUTING.md	Contributing guide
SECURITY.md	Security policy

🤝 Community Feedback
We welcome feedback from the AI community. If you've tried Vireo, we'd love to hear your thoughts — whether positive or critical. Open an issue or reach out via GitHub Discussions.

🤝 Contributing
We welcome contributions! Vireo is open source and community-driven.

Fork the repository
Create a feature branch
Make your changes
Submit a pull request
See CONTRIBUTING.md for details.

📊 Version History
Version	Date	Focus
v1.4.3	2026-08-29	Language-First — Formal grammar, stdlib, examples
v1.4.2	2026-08-28	Cryptography & Protocol — Ed25519, trust, 8 agents
v1.4.1	2026-08-27	Initial Release — Tensor, interpreter, API
🧠 Pretrained Models (NEW in v1.4.3)
Vireo now supports real pretrained models:

ResNet (18, 34, 50, 101, 152) — image classification

BERT (base, large) — text embeddings

GPT-2 (small, medium, large, XL) — text generation

Requirements:

bash
pip install torch torchvision transformers
Example:

python
from pretrained import load_model

# Load ResNet
model = load_model("resnet18")
result = model.predict(image)

# Load BERT
model = load_model("bert_base")
embeddings = model.predict("Hello, Vireo!")

# Load GPT-2
model = load_model("gpt2")
text = model.predict("The future of AI is")

🔗 Links
GitHub: https://github.com/serhohro/vireo-ai-communicator-api

Dev.to: https://dev.to/sergo_8bd8626184a6e9dafa2/meet-vireo

Author: Serhii (serhohro)

📄 License
Apache 2.0 — see LICENSE for details.
