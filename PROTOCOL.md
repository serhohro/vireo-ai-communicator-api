[file name]: PROTOCOL.md
VIREO-A2A Protocol (Layer 3)
🚧 Status: Protocol Ready — LLM Integration Working
Current version demonstrates complete agent coordination infrastructure. Autonomous decisions via LLM API — implemented and tested.

📋 Agent Coordination Protocol
This document describes the protocol layer added on top of the existing DSL (Layer 1) and Runtime (Layer 2).

✅ Fully Implemented:
 Message envelope (message format)
 Speech acts (PROPOSE, COMMIT, REJECT, INFORM, NEGOTIATE)
 Dialogue state machine (NEW → PROPOSED → COMMITTED → DONE)
 Capability discovery (QUERY_CAPABILITIES / INFORM_CAPABILITIES)
 Context versioning (optimistic concurrency control)
 HMAC-SHA256 signatures
 InMemoryEventBus (transport)
 Multi-Agent System with Roles (8 specialized roles)
 LLM Integration (5+ providers)
 Autonomous negotiation (propose → commit → execute → done)
 Negotiate with counter-offers
 Contract system with resource invariants
 Guardian Agent for security validation
🚧 In Development:
 Distributed transport (Redis/Kafka/NATS)
 Asymmetric signatures (Ed25519)
 Dialogue state persistence
 WebAssembly compilation
 Formal verification (TLA+)
🎭 Multi-Agent System with Roles
Agent Roles
Vireo provides 8 specialized agent roles plus the Master coordinator:

Role	Icon	Description	Capabilities
Master	🎯	Coordinator	Orchestration, task distribution, agent management
Vision	👁️	Computer Vision	Image processing, object detection, face recognition
NLP	🧠	Language Processing	Text analysis, sentiment, translation, entity extraction
Analyst	📊	Data Analysis	Statistics, predictive modeling, visualization
Researcher	🧬	Research	Ideation, experimentation, knowledge synthesis
Executor	⚡	Execution	Code execution, model training, report generation
Guardian	🛡️	Security	Code validation, quality assurance, risk assessment
Teacher	📚	Education	Explanation, mentoring, knowledge sharing
Quantum	🔬	Quantum Computing	Quantum circuits, QML, simulation, optimization
How Multi-Agent Collaboration Works
User: "Create a medical image analysis system" ↓ 🎯 MASTER analyzes the task ↓ ┌─────────────────────────────────────────────────────┐ │ 👁️ Vision: "Analyze medical images" │ │ 🧠 NLP: "Process doctor notes" │ │ 📊 Analyst: "Analyze patient data" │ │ 🛡️ Guardian: "Validate safety" │ │ ⚡ Executor: "Generate report" │ └─────────────────────────────────────────────────────┘ ↓ ✅ Complete system ready!

text

Creating Agents with Roles
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
vision = create_vision_agent("agent-vision")
nlp = create_nlp_agent("agent-nlp")
analyst = create_analyst_agent("agent-analyst")
executor = create_executor_agent("agent-executor")

# Register all agents
master.register_agents([vision, nlp, analyst, executor])

# Orchestrate a complex task
result = master.orchestrate("Create a medical image analysis system")
Custom Roles
python
from protocol.agents import AgentRole, RoleAgent

# Define custom role
custom_role = AgentRole(
    name="Custom",
    description="Custom agent role",
    capabilities=["custom_capability_1", "custom_capability_2"],
    system_prompt_template="You are a Custom agent..."
)

# Create agent with custom role
agent = RoleAgent("custom-agent", custom_role)
📨 Message Format
json
{
  "protocol": "VIREO-A2A",
  "version": "1.0",
  "message_id": "msg-a1b2c3d4",
  "conversation_id": "conv-9956c9ec",
  "sender": { "id": "agent-vision", "model": "gpt-5" },
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
Compact Wire Format (Dual-Representation)
json
{
  "p": "VIREO-A2A",
  "v": "1.0",
  "i": "msg-a1b2c3d4",
  "c": "conv-9956c9ec",
  "s": { "id": "agent-vision", "m": "gpt-5" },
  "r": { "id": "agent-training", "m": null },
  "t": "propose",
  "d": { "code": "train MNIST { epochs: 10 }" }
}
🗣️ Speech Acts (Intent)
Intent	Значение
REQUEST	"выполни X"
PROPOSE	"предлагаю сделать X"
QUERY	"какой статус / значение X?"
INFORM	"сообщаю факт / результат"
REJECT	"отклоняю предложение/запрос"
COMMIT	"принимаю предложение, обязуюсь выполнить"
CANCEL	"отменяю ранее принятое обязательство"
NEGOTIATE	"предлагаю изменить условия"
QUERY_CAPABILITIES	"что ты умеешь?"
INFORM_CAPABILITIES	"вот список моих возможностей"
⚙️ Dialogue State Machine
text
NEW → PROPOSED → COMMITTED → RUNNING → DONE
        │            │           │
        ├→ REJECTED  ├→ CANCELLED├→ FAILED
        ├→ TIMEOUT               ├→ TIMEOUT
        └→ CANCELLED             └→ CANCELLED
Each conversation_id has its own state. Invalid transitions (e.g., NEW → RUNNING bypassing PROPOSED/COMMITTED) throw InvalidTransition — this ensures both agents follow the same negotiation protocol.

Extended State Machine (with Negotiate)
text
PROPOSE → VALIDATE → REVIEW → COMMIT → EXECUTE → VERIFY → DONE
                                  ↓
                               REJECT
                                  ↓
                              TIMEOUT
                                  ↓
                              ROLLBACK
🔐 Security & Trust
HMAC Signatures (Symmetric)
python
from protocol import trust

# Sign message
trust.attach_signature(message, secret)

# Verify signature
is_valid = trust.verify(message, secret)
Nonce Protection (Replay Attacks)
python
from protocol.trust import NonceManager

manager = NonceManager(ttl=60)
nonce, timestamp = manager.generate()
is_valid = manager.validate(nonce, timestamp)
Permissions & Identity
python
from protocol.trust import Identity, Permission, TrustManager

# Create identity
identity = Identity(
    id="agent-vision",
    public_key="0x1234...",
    permissions=[Permission.READ, Permission.EXECUTE],
    trust_level=0.9
)

# Register with TrustManager
tm = TrustManager(secret="shared-secret")
tm.register_identity(identity)

# Check permissions
if tm.check_permission("agent-vision", Permission.EXECUTE):
    # Agent can execute
    pass
Zero-Trust Protocol
python
from protocol.trust import TrustManager

tm = TrustManager(secret="shared-secret", ttl=30)

# Create trusted payload
payload = tm.create_trusted_payload(
    {"task": "weather_prediction"},
    agent_id="agent-vision"
)

# Verify payload
is_valid, data = tm.verify_trusted_payload(payload)
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
Master Agent coordinates 8 specialized agents.

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
Multi-Agent Roles	✅ Yes (8 roles)	❌ No	✅ Yes
Contracts	✅ Yes	❌ No	❌ No
Guardian Agent	✅ Yes	❌ No	❌ No
🚀 Next Version Priorities
Distributed Transport — Redis/Kafka/NATS

Full Negotiation Cycle — negotiate with counter-offers

Asymmetric Signatures — Ed25519

State Persistence — Save dialogue state

WebAssembly — WASM compilation for sandboxed execution

🔗 Links
PROTOCOL.md (main)

Agents Guide

LLM Integration

Cryptography

Formal Specification

🌿 Vireo — A Language Designed for AI-to-AI Communication
