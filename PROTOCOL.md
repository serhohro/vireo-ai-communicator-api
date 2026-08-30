# 🌿 VIREO-A2A Protocol (Layer 3)

> 🧪 **Status: Protocol Foundations Implemented — LLM Integration Working (v1.4.3)**
> Core protocol layers, state machine, capability discovery, contracts, and multi-agent orchestration are implemented.
> LLM-driven autonomous negotiation works with 5+ providers.
> Cryptographic primitives are in place; full protocol integration in progress.
> **Vireo is a LANGUAGE, not just a protocol.**

---

## 📋 Agent Coordination Protocol

This document describes the protocol layer added on top of the existing DSL (Layer 1) and Runtime (Layer 2) — part of the **Vireo programming language**.

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
- [x] Formal language grammar (`language/grammar.lark`)
- [x] Standard library (`language/stdlib/`)

### 🚧 In Development:

- [ ] Distributed transport (Redis/Kafka/NATS) — code exists, integration partial
- [ ] Ed25519 protocol integration — planned v1.5.0
- [ ] Dialogue state persistence — planned v1.5.0
- [ ] DID (Decentralized Identifiers) — partial, planned v1.5.0
- [ ] WebAssembly compilation — mock, planned v1.6.0
- [ ] Formal verification (TLA+) — planned v2.0.0
- [ ] Full parser and compiler — planned v1.5.0

---

## 🏗️ Architectural Advantages

### Deterministic State Machine

Enforcing state transitions (NEW → PROPOSED → COMMITTED → DONE) directly inside the protocol prevents protocol drift and unexpected execution loops. This ensures that both agents follow the same negotiation semantics, eliminating the non-determinism that plagues prompt-based agent coordination.

**Why it matters:** Non-deterministic agent behavior is one of the biggest challenges in production multi-agent systems. Vireo's state machine guarantees that every conversation follows a predictable, verifiable path.

### Native Cryptographic Identity & Contracts

Embedding Ed25519 asymmetric signatures and resource invariants (max_tokens, timeout_sec) natively guarantees non-repudiation and prevents runaway agent execution costs.

**Why it matters:** When agents execute autonomously, you need cryptographic proof of who authorized what, and hard limits on resource consumption. Vireo makes these first-class protocol concepts rather than optional middleware.

### Dual Wire Format

Offering standard human-readable JSON alongside a compact key format optimizes both LLM parsing and token-constrained transport efficiency.

**Why it matters:** LLMs consume tokens, and every token costs money. Vireo's compact format reduces wire overhead while keeping the full semantic richness of the protocol for human-readable debugging and LLM comprehension.

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
📨 Message Format
json
{
  "protocol": "VIREO-A2A",
  "version": "1.0",
  "message_id": "msg-a1b2c3d4",
  "conversation_id": "conv-9956c9ec",
  "sender": { "id": "agent-vision", "model": "qwen2.5-coder" },
  "recipient": { "id": "agent-training", "model": null },
  "intent": "propose",
  "payload": {
    "dsl": "vireo",
    "code": "train MNIST { epochs: 10 }",
    "reasoning": "Simple MNIST classifier"
  },
  "constraints": { "timeout_sec": 120, "max_tokens": 1000 },
  "context_version": null,
  "proposal_id": null,
  "timestamp": 1787385246.235,
  "signature": null
}
Compact Wire Format
json
{
  "p": "VIREO-A2A",
  "v": "1.0",
  "i": "msg-a1b2c3d4",
  "c": "conv-9956c9ec",
  "s": { "id": "agent-vision", "m": "qwen2.5-coder" },
  "r": { "id": "agent-training", "m": null },
  "t": "propose",
  "d": { "code": "train MNIST { epochs: 10 }" }
}
🗣️ Speech Acts (Intent)
Intent	Meaning
REQUEST	"Execute X"
PROPOSE	"I propose to do X"
QUERY	"What is the status/value of X?"
INFORM	"I inform the fact/result"
REJECT	"I reject the proposal/request"
COMMIT	"I accept the proposal and commit"
CANCEL	"I cancel a previously accepted commitment"
NEGOTIATE	"I propose to change the terms"
QUERY_CAPABILITIES	"What can you do?"
INFORM_CAPABILITIES	"Here is my list of capabilities"
⚙️ Dialogue State Machine
text
NEW → PROPOSED → COMMITTED → RUNNING → DONE
        │            │           │
        ├→ REJECTED  ├→ CANCELLED├→ FAILED
        ├→ TIMEOUT               ├→ TIMEOUT
        └→ CANCELLED             └→ CANCELLED
Each conversation_id has its own state. Invalid transitions (e.g., NEW → RUNNING bypassing PROPOSED/COMMITTED) throw InvalidTransition — this ensures both agents follow the same negotiation protocol.

🔐 Security & Trust
Vireo includes cryptographic primitives for secure AI-to-AI communication:

Component	Status	Details
HMAC Signatures	✅ Implemented	Symmetric signing
Nonce Protection	✅ Implemented	Replay attack prevention
Ed25519 Primitives	✅ Implemented	Key generation, signing, verification
Ed25519 Protocol Integration	🚧 In Development	Planned for v1.5.0
DID Implementation	🚧 In Development	Planned for v1.5.0
Zero-Trust Protocol	🚧 In Development	Planned for v1.5.0
State Persistence	🔵 Planned	Planned for v1.5.0
HMAC Signatures
python
from protocol import trust

# Sign message
trust.attach_signature(message, secret)

# Verify signature
is_valid = trust.verify(message, secret)
Nonce Protection
python
from protocol.trust import NonceManager

manager = NonceManager(ttl=60)
nonce, timestamp = manager.generate()
is_valid = manager.validate(nonce, timestamp)
Permissions & Identity
python
from protocol.trust import Identity, Permission, TrustManager

identity = Identity(
    id="agent-vision",
    public_key="0x1234...",
    permissions=[Permission.READ, Permission.EXECUTE],
    trust_level=0.9
)

tm = TrustManager(secret="shared-secret")
tm.register_identity(identity)

if tm.check_permission("agent-vision", Permission.EXECUTE):
    # Agent can execute
    pass
📋 Contracts (Resource Invariants)
python
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
Contract Example in Vireo Language
vireo
contract Agreement {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.05
    timeout_sec: Int = 30
    max_rounds: Int = 3
    allowed_actions: List[String] = ["train_model", "predict"]
}
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

📊 Comparison: Vireo vs MCP vs A2A
Feature	Vireo	MCP (Anthropic)	A2A (Google)
Own Language	✅ Yes	❌ No	❌ No
Protocol	✅ Yes	✅ Yes	✅ Yes
Runtime	✅ Yes	❌ No	❌ No
Tensors + Autodiff	✅ Yes	❌ No	❌ No
Open Source	✅ Yes	✅ Yes	❌ No
Free	✅ Yes	✅ Yes	❌ No
Local Execution	✅ Yes (Ollama)	⚠️ Partial	❌ No
Multi-Agent Roles	✅ Yes (7 roles + Master)	❌ No	✅ Yes
Contracts	✅ Yes	❌ No	❌ No
Guardian Agent	✅ Yes	❌ No	❌ No
Formal Language	✅ Yes	❌ No	❌ No
🚀 Next Version Priorities
Priority	Feature	Target
1	Ed25519 Protocol Integration	v1.5.0
2	DID Implementation	v1.5.0
3	Distributed Transport (Redis/Kafka/NATS)	v1.5.0
4	State Persistence	v1.5.0
5	Full Parser & Compiler	v1.5.0
6	WebAssembly	v1.6.0
7	Formal Verification (TLA+)	v2.0.0
🔗 Links
PROTOCOL.md — This document

README.md — Project overview

language/syntax.md — Language syntax

docs/contracts.md — Contracts documentation

docs/security.md — Security documentation