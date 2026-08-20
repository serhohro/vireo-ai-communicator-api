# 🟢 Vireo — A Language Designed for AI-to-AI Communication

**One Language. All AI. Unlimited Future.**

> **Note:** Vireo is currently in active development (v0.4.0). While the syntax is stable and AI models can generate Vireo code through prompting, the full protocol for AI-to-AI communication is still evolving. We welcome contributions and feedback!

[![GitHub stars](https://img.shields.io/github/stars/serhohro/vireo-ai-communicator-api?style=for-the-badge)](https://github.com/serhohro/vireo-ai-communicator-api/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/serhohro/vireo-ai-communicator-api?style=for-the-badge)](https://github.com/serhohro/vireo-ai-communicator-api/network/members)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)

---

## 🌍 What is Vireo?

**Vireo is a programming language designed specifically for AI-to-AI communication.**

It is designed to enable:
- ✅ **ChatGPT, Claude, Gemini, Llama** to generate and interpret Vireo code through prompting
- ✅ **Humans** to easily communicate with AI
- ✅ **Private & local** execution of AI models
- ✅ **Built-in** tensors and automatic differentiation

---

## 🤖 AI Models That Can Generate and Interpret Vireo

| Model | Status |
|-------|--------|
| ChatGPT (OpenAI) | ✅ Can generate/interpret through prompting |
| Claude (Anthropic) | ✅ Can generate/interpret through prompting |
| Gemini (Google) | ✅ Can generate/interpret through prompting |
| Llama (Meta) | ✅ Can generate/interpret through prompting |
| All Future AI | 🟡 Designed to be interpretable by AI models |

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Communication** | Designed for AI-to-AI communication |
| 📊 **Built-in Tensors** | 50+ native tensor operations |
| 🧠 **Autodifferentiation** | Automatic gradient computation |
| 🔗 **Neural Networks** | Built-in layers and activations |
| 🔨 **Compiler** | Vireo → Python code compilation |
| 🌐 **API Server** | RESTful API for integration |
| 🎨 **Web Interface** | Beautiful and user-friendly UI |
| 💾 **Model Saver** | Save and load trained models |
| 🔮 **Predict** | Inference API for trained models |
| 📈 **Evaluate** | Model evaluation with metrics |
| 📊 **Metrics** | Accuracy, precision, recall, f1 |
| 💻 **Device** | GPU/CPU selection |
| 💾 **Checkpoint** | Auto-save models during training |
| 📂 **Dataset** | Dataset definition (MNIST, CIFAR10) |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-api.git
cd vireo-ai-communicator

# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py

# Open web interface
# http://localhost:5000/docs

# Or run demo
run.bat

💻 Example Code
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
    loss CrossEntropy
    optimizer Adam(lr=0.001)
    device GPU
}

train MNIST {
    data = "mnist"
    epochs = 10
    batch_size = 64
    validation = 0.2
    early_stopping = true
    patience = 3
    checkpoint = "mnist.vireo"
}

load "mnist.vireo"

predict MNIST {
    data = "test"
    model = "mnist"
}

evaluate MNIST {
    data = "test"
    metrics = [accuracy, precision, recall, f1]
}

## 📊 Comparison

| Feature | Python | Rust | Vireo |
|---------|--------|------|-------|
| AI Integration | Via prompting | Via prompting | **Native design** |
| Execution Speed | Medium | High | **High** |
| Ease of Use | High | Low | **High** |
| Built-in Tensors | Via libraries | Via libraries | **Built-in** |
| Automatic Differentiation | Via libraries | No | **Built-in** |
| Local Execution | Yes | Yes | **Yes** |
| AI Communication | No | No | **Native design** |
🤝 How to Contribute
⭐ Star the repository

🍴 Fork the project

📝 Write code in Vireo

🗣️ Share with the world

📄 License
Apache 2.0 — Free and Open Source

👨‍💻 Author
serhohro

GitHub: @serhohro
