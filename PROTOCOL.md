# VIREO-A2A Protocol (Layer 3)

> ⚠️ **Статус: Протокол готовий, LLM-інтеграція в розробці**  
> Поточна версія демонструє повну інфраструктуру координації агентів.  
> Автономні рішення через LLM API — експериментальний функціонал.

---

## 📋 Протокол координації агентів

Цей документ описує протокольний шар, доданий поверх існуючого **DSL (Layer 1)** та **Runtime (Layer 2)**.

### ✅ Реалізовано повністю:
- [x] **Message envelope** (формат повідомлень)
- [x] **Speech acts** (`PROPOSE`, `COMMIT`, `REJECT`, `INFORM`, ...)
- [x] **Dialogue state machine** (`NEW` → `PROPOSED` → `COMMITTED` → `DONE`)
- [x] **Capability discovery** (`QUERY_CAPABILITIES` / `INFORM_CAPABILITIES`)
- [x] **Context versioning** (optimistic concurrency control)
- [x] **HMAC-SHA256 signatures**
- [x] **InMemoryEventBus** (transport)
- [x] **Multi-Agent System with Roles** (8 specialized roles)

### 🚧 В розробці:
- [ ] Інтеграція з Claude API для автономних рішень
- [ ] Інтеграція з OpenAI API (GPT-4)
- [ ] Повний цикл переговорів без участі людини
- [ ] Розподілений транспорт (Redis/Kafka/NATS)
- [ ] Асиметричні підписи (Ed25519)
- [ ] Персистентність стану діалогів

---

## 🎭 Multi-Agent System with Roles

### Agent Roles

Vireo provides **8 specialized agent roles** plus the **Master** coordinator:

| Role | Icon | Description | Capabilities |
| :--- | :---: | :--- | :--- |
| **Master** | 🎯 | Coordinator | Orchestration, task distribution, agent management |
| **Vision** | 👁️ | Computer Vision | Image processing, object detection, face recognition |
| **NLP** | 🧠 | Language Processing | Text analysis, sentiment, translation, entity extraction |
| **Analyst** | 📊 | Data Analysis | Statistics, predictive modeling, visualization |
| **Researcher** | 🧬 | Research | Ideation, experimentation, knowledge synthesis |
| **Executor** | ⚡ | Execution | Code execution, model training, report generation |
| **Guardian** | 🛡️ | Security | Code validation, quality assurance, risk assessment |
| **Teacher** | 📚 | Education | Explanation, mentoring, knowledge sharing |
| **Quantum** | 🔬 | Quantum Computing | Quantum circuits, QML, simulation, optimization |

---

### How Multi-Agent Collaboration Works

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
✅ Complete system ready!
```

---

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
```

---

### Custom Roles

```python
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
```
