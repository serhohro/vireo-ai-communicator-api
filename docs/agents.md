```markdown
# 🎭 Multi-Agent System Guide

## Overview

Vireo provides a complete multi-agent system with 8 specialized roles and a Master Agent for orchestration.

---

## Agent Roles

| Role | Icon | Description | Capabilities |
|------|------|-------------|--------------|
| **Master** | 🎯 | Coordinator | Orchestration, task distribution |
| **Vision** | 👁️ | Computer Vision | Image processing, object detection |
| **NLP** | 🧠 | Language Processing | Text analysis, sentiment, translation |
| **Analyst** | 📊 | Data Analysis | Statistics, predictive modeling |
| **Researcher** | 🧬 | Research | Ideation, experimentation |
| **Executor** | ⚡ | Execution | Code execution, model training |
| **Guardian** | 🛡️ | Security | Code validation, quality assurance |
| **Teacher** | 📚 | Education | Explanation, mentoring |
| **Quantum** | 🔬 | Quantum Computing | Quantum circuits, QML, simulation |

---

## Creating Agents

### Python API

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
Custom Roles
python
from protocol.agents import AgentRole, RoleAgent

custom_role = AgentRole(
    name="Custom",
    description="Custom agent role",
    capabilities=["custom_capability"],
    system_prompt_template="You are a Custom agent..."
)

agent = RoleAgent("custom-agent", custom_role)
Orchestration
Simple Orchestration
python
result = master.orchestrate("Create a medical image analysis system")
Complex Orchestration
python
task = """
Create a complete medical image analysis system:
1. Analyze medical images (Vision)
2. Process doctor notes (NLP)
3. Analyze patient data (Analyst)
4. Validate safety (Guardian)
5. Generate report (Executor)
"""

result = master.orchestrate(task)

print(f"Status: {result['status']}")
print(f"Completed: {result['summary']['completed']}/{result['summary']['total_subtasks']}")
Agent Communication
Propose → Commit → Execute
python
# Agent proposes task
proposal = vision.propose("agent-training", payload={"code": "..."})

# Agent commits to task
training.commit(proposal)

# Result is delivered via INFORM
def on_inform(agent, msg):
    print(f"Result: {msg.payload}")
Capability Discovery
python
# Query capabilities
vision.query_capabilities("agent-training")

# Handle response
def on_capabilities(agent, msg):
    caps = msg.payload["capabilities"]
    print(f"Capabilities: {caps}")
State Machine
text
NEW → PROPOSED → COMMITTED → RUNNING → DONE
        │            │           │
        ├→ REJECTED  ├→ CANCELLED├→ FAILED
        ├→ TIMEOUT               ├→ TIMEOUT
        └→ CANCELLED             └→ CANCELLED
Example: Full Multi-Agent System
python
from protocol.agents import (
    MasterAgent,
    create_vision_agent,
    create_nlp_agent,
    create_analyst_agent,
    create_executor_agent,
    create_guardian_agent,
)

# Create all agents
master = MasterAgent("master")
vision = create_vision_agent()
nlp = create_nlp_agent()
analyst = create_analyst_agent()
executor = create_executor_agent()
guardian = create_guardian_agent()

# Register agents
master.register_agents([vision, nlp, analyst, executor, guardian])

# Complex task
task = """
Build a complete healthcare AI system:
1. Analyze medical images (Vision)
2. Process doctor notes (NLP)
3. Analyze patient data (Analyst)
4. Validate safety (Guardian)
5. Generate treatment plan (Executor)
"""

result = master.orchestrate(task)
Next Steps
Protocol Guide

LLM Integration