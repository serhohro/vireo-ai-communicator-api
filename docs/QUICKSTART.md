markdown
# 🚀 Vireo Quickstart — 5 Minutes

## What is Vireo?

Vireo is a **programming language + protocol** for autonomous AI-to-AI communication. It allows AI agents to discover capabilities, negotiate tasks, sign cryptographic contracts, execute tasks, and verify results.

**Protocols tell agents HOW to talk. Vireo gives them WHAT to say.**

---

## 1. Install Vireo

```bash
# Clone the repository
git clone https://github.com/serhohro/vireo-ai-communicator-api.git
cd vireo-ai-communicator-api

# Install dependencies
pip install -r requirements.txt

# Run the server
python api_server.py
2. Write Your First Agent
Create a file hello.v:

vireo
// ============================================================
// Hello Vireo — Your First Agent
// ============================================================

agent Hello {
    capability greet
    role assistant
}

contract Greeting {
    max_tokens: Int = 100
    verify { result.words > 0 }
}

negotiate Hello -> Hello {
    propose "Say hello to the world"
    commit "I will say hello"
    execute "print('Hello, Vireo!')"
    inform "Done"
}
3. Run It
Via Web Interface
Open http://localhost:5000/web

Go to "Execute" tab

Paste the code above

Click "Execute"

Via API
bash
curl -X POST http://localhost:5000/api/interpreter \
  -H "Content-Type: application/json" \
  -d '{"code": "agent Hello { capability greet role assistant }"}'
4. Write a Neural Network
vireo
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
}

train MNIST {
    epochs: 10
    batch_size: 32
    learning_rate: 0.001
}

evaluate MNIST
5. Autonomous Agent Negotiation
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
    negotiate "Need more tokens"
    commit "Training model on dataset"
    execute "Process images"
    verify "Check accuracy > 0.9"
    inform "Accuracy: 94.5%"
}
6. What's Next?
Full Tutorial — Complete step-by-step guide

Language Reference — Full language syntax

Protocol Reference — Agent communication protocol

Examples — More code examples

🌿 Vireo — The World's First AI-to-AI Communication Language. 🚀