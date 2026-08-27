# VIREO-A2A Protocol (Layer 3)

> 🧪 **Status: Protocol Foundations Implemented — LLM Integration Working**
> Core protocol layers, state machine, capability discovery, contracts, and multi-agent orchestration are implemented.
> LLM-driven autonomous negotiation works with 5+ providers.
> Cryptographic primitives are in place; full protocol integration in progress.

---

## 📋 Agent Coordination Protocol

This document describes the protocol layer added on top of the existing DSL (Layer 1) and Runtime (Layer 2).

### ✅ Fully Implemented:

- [x] Message envelope (message format)
- [x] Speech acts (PROPOSE, COMMIT, REJECT, INFORM, NEGOTIATE)
- [x] Dialogue state machine (NEW → PROPOSED → COMMITTED → DONE)
- [x] Capability discovery (QUERY_CAPABILITIES / INFORM_CAPABILITIES)
- [x] Context versioning (optimistic concurrency control)
- [x] HMAC-SHA256 signatures
- [x] InMemoryEventBus (transport)
- [x] Multi-Agent System with Roles (7 specialized roles + Master, Quantum planned)
- [x] LLM Integration (5+ providers)
- [x] Autonomous negotiation (propose → commit → execute → done)
- [x] Negotiate with counter-offers (partial)
- [x] Contract system with resource invariants
- [x] Guardian Agent for security validation
- [x] Ed25519 cryptographic primitives (key generation, signing, verification)

### 🚧 In Development:

- [ ] Distributed transport (Redis/Kafka/NATS) — code exists, integration partial
- [ ] Ed25519 protocol integration — planned v1.5.0
- [ ] Dialogue state persistence — planned v1.5.0
- [ ] DID (Decentralized Identifiers) — partial, planned v1.5.0
- [ ] WebAssembly compilation — mock, planned v1.6.0
- [ ] Formal verification (TLA+) — planned v2.0.0

---

## 🎭 Multi-Agent System with Roles

### Agent Roles

Vireo provides **7 specialized agent roles** plus the **Master coordinator** (Quantum role planned):

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

---

## 🔐 Security & Trust

Vireo includes cryptographic primitives for secure AI-to-AI communication:

| Component | Status | Details |
|-----------|--------|---------|
| HMAC Signatures | ✅ Implemented | Symmetric signing |
| Nonce Protection | ✅ Implemented | Replay attack prevention |
| Ed25519 Primitives | ✅ Implemented | Key generation, signing, verification |
| Ed25519 Protocol Integration | 🚧 In Development | Planned for v1.5.0 |
| DID Implementation | 🚧 In Development | Planned for v1.5.0 |
| Zero-Trust Protocol | 🚧 In Development | Planned for v1.5.0 |
| State Persistence | 🔵 Planned | Planned for v1.5.0 |

---

## 📊 Comparison: Vireo vs MCP vs A2A

| Feature | Vireo | MCP (Anthropic) | A2A (Google) |
|---------|-------|-----------------|--------------|
| Own Language | ✅ Yes | ❌ No | ❌ No |
| Protocol | ✅ Yes | ✅ Yes | ✅ Yes |
| Runtime | ✅ Yes | ❌ No | ❌ No |
| Tensors + Autodiff | ✅ Yes | ❌ No | ❌ No |
| Open Source | ✅ Yes | ✅ Yes | ❌ No |
| Free | ✅ Yes | ✅ Yes | ❌ No |
| Local Execution | ✅ Yes (Ollama) | ⚠️ Partial | ❌ No |
| Multi-Agent Roles | ✅ Yes (7 roles + Master) | ❌ No | ✅ Yes |
| Contracts | ✅ Yes | ❌ No | ❌ No |
| Guardian Agent | ✅ Yes | ❌ No | ❌ No |

---

## 📋 Contracts (Resource Invariants)

```python
from protocol.contract import Contract, Proposal, create_default_contract

# Create contract with limits
contract = Contract(
    max_tokens=500,
    max_cost_usd=0.01,
    timeout_sec=30,
    max_rounds=3,
    allowed_actions=["train_model", "predict"]
)

# Validate proposal
is_valid, error = contract.validate(proposal)
🧪 Demonstrations
1. Basic Demo (Manual Control) ✅
bash
python protocol/examples/two_agent_demo.py
Human controls agents via code. Shows protocol operation.

2. Autonomous LLM Demo ✅
bash
python protocol/examples/llm_agent_demo.py
Agents use LLM (Ollama, Claude, GPT-4, Gemini, Mistral) for decisions.
Status: ✅ Working with 5+ providers.

3. Multi-Agent Demo with Roles ✅
bash
python protocol/examples/multi_agent_demo.py
Master Agent coordinates 7+ specialized agents.

4. Negotiation Demo 🆕
bash
python protocol/examples/negotiation_demo.py
Full negotiation cycle with counter-offers.

5. MCP Demo 🆕
bash
python protocol/examples/mcp_demo.py
Integration with Model Context Protocol.

🚀 Next Version Priorities
Ed25519 Protocol Integration — v1.5.0

DID Implementation — v1.5.0

Distributed Transport — Redis/Kafka/NATS (integration) — v1.5.0

State Persistence — v1.5.0

WebAssembly — v1.6.0

Formal Verification (TLA+) — v2.0.0

🔗 Links
PROTOCOL.md (main)

Agents Guide

LLM Integration

Cryptography

Formal Specification

🌿 Vireo — A Language Designed for AI-to-AI Communication
