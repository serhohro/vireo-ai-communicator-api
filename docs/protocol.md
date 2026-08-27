# VIREO-A2A Protocol (Layer 3)

> ⚠️ **Статус: Протокол готовий, LLM-інтеграція працює**  
> Поточна версія демонструє повну інфраструктуру координації агентів. 
> Автономні рішення через LLM API — реалізовано та протестовано.

---

## 📋 Протокол координації агентів

Цей документ описує протокольний шар, доданий поверх існуючого
DSL (Layer 1) та Runtime (Layer 2).

### ✅ Реалізовано повністю:
- [x] Message envelope (формат повідомлень)
- [x] Speech acts (PROPOSE, COMMIT, REJECT, INFORM, ...)
- [x] Dialogue state machine (NEW → PROPOSED → COMMITTED → DONE)
- [x] Capability discovery (QUERY_CAPABILITIES / INFORM_CAPABILITIES)
- [x] Context versioning (optimistic concurrency control)
- [x] HMAC-SHA256 signatures
- [x] InMemoryEventBus (transport)
- [x] Multi-Agent System with Roles (8 specialized roles)
- [x] LLM Integration (5+ providers)
- [x] Autonomous negotiation (propose → commit → execute → done)

### 🚧 В розробці:
- [ ] Розподілений транспорт (Redis/Kafka/NATS)
- [ ] Повний цикл переговорів (NEGOTIATE з контрпропозиціями)
- [ ] Асиметричні підписи (Ed25519)
- [ ] Персистентність стану діалогів
- [ ] WebAssembly компіляція

---

## 🎭 Multi-Agent System with Roles

### Agent Roles

Vireo provides **8 specialized agent roles** plus the **Master** coordinator:

| Role | Icon | Description | Capabilities |
|------|------|-------------|--------------|
| **Master** | 🎯 | Coordinator | Orchestration, task distribution, agent management |
| **Vision** | 👁️ | Computer Vision | Image processing, object detection, face recognition |
| **NLP** | 🧠 | Language Processing | Text analysis, sentiment, translation, entity extraction |
| **Analyst** | 📊 | Data Analysis | Statistics, predictive modeling, visualization |
| **Researcher** | 🧬 | Research | Ideation, experimentation, knowledge synthesis |
| **Executor** | ⚡ | Execution | Code execution, model training, report generation |
| **Guardian** | 🛡️ | Security | Code validation, quality assurance, risk assessment |
| **Teacher** | 📚 | Education | Explanation, mentoring, knowledge sharing |
| **Quantum** | 🔬 | Quantum Computing | Quantum circuits, QML, simulation, optimization |

### How Multi-Agent Collaboration Works
User: "Create a medical image analysis system"
↓
🎯 MASTER analyzes the task
↓
┌─────────────────────────────────────────────────────┐
│ 👁️ Vision: "Analyze medical images" │
│ 🧠 NLP: "Process doctor notes" │
│ 📊 Analyst: "Analyze patient data" │
│ 🛡️ Guardian: "Validate safety" │
│ ⚡ Executor: "Generate report" │
└─────────────────────────────────────────────────────┘
↓
✅ Complete system ready!

text

### Creating Agents with Roles

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
📨 Формат повідомлення
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
    "code": "train MNIST { epochs: 10 }"
  },
  "constraints": { "timeout_sec": 120 },
  "context_version": null,
  "proposal_id": null,
  "timestamp": 1787385246.235,
  "signature": null
}
🗣️ Speech acts (intent)
Intent	Значение
request	"выполни X"
propose	"предлагаю сделать X"
query	"какой статус / значение X?"
inform	"сообщаю факт / результат"
reject	"отклоняю предложение/запрос"
commit	"принимаю предложение, обязуюсь выполнить"
cancel	"отменяю ранее принятое обязательство"
negotiate	"предлагаю изменить условия"
query_capabilities	"что ты умеешь?"
inform_capabilities	"вот список моих возможностей"
⚙️ Машина станів діалогу
text
NEW → PROPOSED → COMMITTED → RUNNING → DONE
        │            │           │
        ├→ REJECTED  ├→ CANCELLED├→ FAILED
        ├→ TIMEOUT               ├→ TIMEOUT
        └→ CANCELLED             └→ CANCELLED
Каждый conversation_id имеет собственное состояние. Недопустимые переходы
(например, NEW → RUNNING в обход PROPOSED/COMMITTED) выбрасывают
InvalidTransition — это гарантирует, что оба агента следуют одному и тому
же протоколу переговоров, а не произвольному обмену сообщениями.

🔐 Довіра та безпека
HMAC Signatures
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
Permissions & Identity (в розробці)
python
# Планований синтаксис
agent WeatherAgent {
    identity: "did:key:z6Mkha..."
    public_key: "0x1234..."
    permissions: ["read", "execute"]
}
🧪 Демонстрації
1. Базове демо (ручне керування) ✅
bash
python protocol/examples/two_agent_demo.py
Людина керує агентами через код. Показує роботу протоколу.

2. Автономне демо з LLM ✅
bash
python protocol/examples/llm_agent_demo.py
Агенти використовують LLM (Ollama, Claude, GPT-4, Gemini, Mistral) для прийняття рішень.
Статус: ✅ Працює з 5+ провайдерами.

3. Multi-Agent демо з ролями ✅
bash
python protocol/examples/multi_agent_demo.py
Master Agent координує 8 спеціалізованих агентів.

4. MCP демо 🆕
bash
python protocol/examples/mcp_demo.py
Інтеграція з Model Context Protocol.

📊 Порівняння Vireo vs MCP vs A2A
Характеристика	Vireo	MCP (Anthropic)	A2A (Google)
Власна мова	✅ Так	❌ Ні	❌ Ні
Протокол	✅ Так	✅ Так	✅ Так
Runtime	✅ Так	❌ Ні	❌ Ні
Тензори + Autodiff	✅ Так	❌ Ні	❌ Ні
Відкритий код	✅ Так	✅ Так	❌ Ні
Безкоштовний	✅ Так	✅ Так	❌ Ні
Локальне виконання	✅ Так (Ollama)	⚠️ Частково	❌ Ні
Multi-Agent Roles	✅ Так (8 ролей)	❌ Ні	✅ Так
🚀 Пріоритети для наступних версій
Розподілений транспорт — Redis/Kafka/NATS

Повний цикл переговорів — negotiate з контрпропозиціями

Асиметричні підписи — Ed25519

Персистентність — збереження стану діалогів

🔗 Посилання
PROTOCOL.md (основний)

Agents Guide

LLM Integration

Cryptography

Formal Specification

🌿 Vireo — A Language Designed for AI-to-AI Communication