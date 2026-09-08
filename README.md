# 🌿 Vireo AI Communicator API

> **The World's First AI-to-AI Communication Language**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Rust](https://img.shields.io/badge/Rust-1.70%2B-orange)](https://rust-lang.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-blue)](https://typescriptlang.org)
[![Version](https://img.shields.io/badge/version-3.0.0-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-100%2B-green)]()
[![Conformance](https://img.shields.io/badge/conformance-59%2B-green)]()

---

## 🎯 What is Vireo?

**Vireo** is a programming language + protocol + runtime for autonomous AI-to-AI communication, negotiation, and coordination.

> *"LLMs provide intelligence. Vireo provides structure, execution, verification and interoperability."*

### The Problem We Solve

Today, AI agents are **isolated silos**. They cannot:
- 🚫 Discover each other
- 🚫 Negotiate contracts
- 🚫 Execute coordinated tasks
- 🚫 Verify results
- 🚫 Build trust

**Vireo changes this.**

---

## 🌟 Key Features

### 🧠 Language
- **Formal Grammar** — EBNF specification with extensions for ML, Vision, NLP
- **Type System** — Static typing with inference
- **Extensions** — ML, Tensor, Vision, NLP as optional modules
- **Standard Library** — Math, Neural Networks, Protocol, Crypto, IO

### 🌐 Protocol
- **Binary Canonical Format** — Language-neutral, deterministic serialization
- **Ed25519 Signatures** — Cryptographic trust
- **DIDs (Decentralized Identifiers)** — Self-sovereign identity
- **State Machine** — DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE
- **VERIFY/ESCALATE** — Result verification and dispute resolution
- **Key Rotation** — Secure key lifecycle management
- **Replay Protection** — Nonces + timestamps

### ⚡ Runtime
- **JIT Compilation** — LLVM-based, 10-100x speedup for tensor ops
- **GPU Support** — CUDA, Metal, ROCm
- **WASM Backend** — Browser and edge deployment
- **3-Level Sandbox** — Validation → WASM → Docker
- **Async/Await** — Non-blocking communication

### 🔌 Integrations
- **6+ LLM Providers** — OpenAI, Anthropic, Mistral, Ollama, Hugging Face, Gemini
- **European LLMs** — Mistral, BLOOM, OpenChat, Phi-3, GPT4All
- **A2A Adapter** — Google's Agent-to-Agent protocol
- **MCP Adapter** — Anthropic's Model Context Protocol
- **gRPC/WebSocket/HTTP** — Multiple transport layers

### 🧪 Quality
- **100+ Tests** — Unit, conformance, integration, performance
- **59+ Conformance Tests** — Protocol compliance verification
- **Cross-Language Tests** — Python ↔ Rust ↔ TypeScript
- **Fuzzing** — Edge case discovery

---

## 🚀 Quick Start

### Installation

```bash
# Python
pip install vireo-ai

# Rust
cargo add vireo

# TypeScript
npm install vireo-ai
Hello World Agent
vireo
// hello_agent.vireo
agent HelloAgent {
    name = "hello-bot"
    capabilities = ["chat", "greet"]
}

fn main() {
    let agent = HelloAgent();
    let msg = agent.propose({
        intent: "greet",
        payload: { "message": "Hello, World!" }
    });
    agent.send(msg);
    agent.verify(msg);
}
📚 Documentation
Quick Start — 5-minute intro

Tutorial — Complete step-by-step guide

Language Guide — Full language reference

Protocol Guide — Protocol specification

API Reference — API documentation

🏆 The North Star
"Don't prove that Vireo can run more AI models. Prove that Vireo can make independently implemented AI agents interoperable."

The Test
"Two independently implemented agents, written in different languages, MUST be able to exchange canonical Vireo messages, verify their authenticity, perform identical valid state transitions, and produce equivalent protocol outcomes without sharing implementation code."

Can Python ↔ Rust ↔ TypeScript agents negotiate, execute, and verify a contract through Vireo?

If yes — Vireo works as a standard.

🔒 Security
Cryptographic Trust
Ed25519 signatures — Fast, secure, deterministic

DIDs — Decentralized Identifiers (did:vireo:agent:...)

Key Rotation — Secure key lifecycle

Trust Bootstrap — Whitelist + Ed25519

Sandboxing (3-Level)
Level 1 — Message validation (signature, schema, nonce)

Level 2 — WASM execution (isolated memory)

Level 3 — Docker containers (OS-level isolation)

📦 Implementations
Language	Status	Tests	Conformance
Python	✅ Production	100+	✅ 59+
Rust	✅ v3.0	80+	🚧 In progress
TypeScript	✅ v3.0	60+	🚧 In progress
Go	⏳ Planned	—	—
Java	⏳ Planned	—	—
🤝 Contributing
We welcome contributions!

Fork the repository

Create a feature branch

Write tests

Submit a PR

See CONTRIBUTING.md for details.

📄 License
Apache 2.0 — see LICENSE for details.