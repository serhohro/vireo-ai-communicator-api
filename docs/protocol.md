
```markdown
# 🔗 Protocol Guide

## Overview

Vireo-A2A is a communication protocol for autonomous AI agents.

---

## Architecture
┌─────────────────────────────────────────────────────────────┐
│ VIREO-A2A PROTOCOL │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: DSL (model, train, predict) │
│ Layer 2: Runtime (Tensor, Autograd, CNN) │
│ Layer 3: Protocol (PROPOSE, COMMIT, REJECT, INFORM) │
│ Layer 4: Transport (InMemoryEventBus, Redis/Kafka) │
└─────────────────────────────────────────────────────────────┘

text

---

## Message Format

```json
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
Speech Acts (Intents)
Intent	Description
propose	Propose a task
commit	Commit to execute
reject	Reject a proposal
inform	Inform result
query_capabilities	Query agent capabilities
inform_capabilities	Respond with capabilities
cancel	Cancel a task
negotiate	Negotiate terms
State Machine
text
NEW → PROPOSED → COMMITTED → RUNNING → DONE
        │            │           │
        ├→ REJECTED  ├→ CANCELLED├→ FAILED
        ├→ TIMEOUT               ├→ TIMEOUT
        └→ CANCELLED             └→ CANCELLED
Capability Discovery
python
# Register capability
agent.register_capability("train_model", description="Trains models")

# Query capabilities
agent.query_capabilities("agent-training")

# Response
def on_capabilities(agent, msg):
    capabilities = msg.payload["capabilities"]
Trust & Security
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
Transport
InMemoryEventBus
python
from protocol import InMemoryEventBus

bus = InMemoryEventBus()
bus.publish("channel", message)
bus.subscribe("channel", handler)
Redis (Future)
python
from src.transport import RedisEventBus

bus = RedisEventBus("redis://localhost:6379")
bus.connect()
bus.publish("channel", message)
bus.subscribe("channel", handler)
Example: Full Negotiation
python
from protocol import Agent, InMemoryEventBus, Intent

# Create agents
bus = InMemoryEventBus()
agent_a = Agent("agent-a", bus)
agent_b = Agent("agent-b", bus)

# Propose task
proposal = agent_a.propose("agent-b", payload={"task": "train_model"})

# Commit to task
agent_b.commit(proposal)

# Receive result
def on_inform(agent, msg):
    print(f"Result: {msg.payload}")

agent_a.on(Intent.INFORM, on_inform)
Next Steps
LLM Integration

Cryptography