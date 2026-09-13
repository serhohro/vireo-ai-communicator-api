
```markdown
# 🧠 LLM Integration Guide

## Overview

Vireo integrates with 5+ LLM providers for autonomous code generation and decision making.

---

## Supported Providers

| Provider | Cost | Quality | Speed | Local |
|----------|------|---------|-------|-------|
| **Ollama** | 🆓 Free | ⭐⭐⭐ | ⚡⚡⚡ | ✅ Yes |
| **Gemini** | 🆓 Free | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | ❌ No |
| **Mistral** | 💰 Paid | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | ❌ No |
| **Claude** | 💰 Paid | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | ❌ No |
| **OpenAI** | 💰 Paid | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ | ❌ No |

---

## Configuration

### .env File

```bash
# Provider selection
LLM_PROVIDER=ollama

# Ollama (free, local)
OLLAMA_MODEL=qwen2.5-coder:latest
OLLAMA_HOST=http://localhost:11434

# Claude (paid)
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-sonnet-20241022

# OpenAI (paid)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Gemini (free tier)
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash

# Mistral (paid)
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-small-latest
Using LLM Providers
Python API
python
from protocol.llm_provider import create_llm_provider

# Create provider
provider = create_llm_provider("ollama")

# Generate response
result = provider.generate(
    system_prompt="You are a helpful assistant.",
    user_prompt="Generate Vireo code for MNIST.",
    task="code generation"
)

print(result["content"])
JSON Generation
python
result = provider.generate_json(
    system_prompt="Respond with JSON only.",
    user_prompt='{"task": "weather_prediction"}'
)

data = result["data"]
print(data)
LLM Agents
Creating LLM Agent
python
from protocol.llm_agent import create_llm_agent

agent = create_llm_agent("agent-vision", provider="ollama")

# Register capability
agent.register_capability("generate_code", "Generates Vireo code")

# Ask for proposal
proposal = agent.ask_for_proposal("Create a neural network", agent.capabilities)

# Ask for decision
decision = agent.ask_for_decision(proposal_code, reasoning)
Autonomous Negotiation
python
result = agent.auto_negotiate(
    recipient_id="agent-training",
    task_description="Create a neural network for MNIST"
)

print(f"Decision: {result['decision']['decision']}")
print(f"Code: {result['proposal']['code']}")
Provider Selection
Manual Selection
python
provider = create_llm_provider("claude")
Auto Selection
python
# Uses LLM_PROVIDER from .env
provider = create_llm_provider()
Hybrid Mode
python
# Simple tasks → Ollama, complex → Claude
provider = create_llm_provider("hybrid")
Error Handling
python
try:
    result = provider.generate(system_prompt, user_prompt)
    if result["status"] == "error":
        print(f"Error: {result['message']}")
except Exception as e:
    print(f"Exception: {e}")
Next Steps
Cryptography

Agents Guide