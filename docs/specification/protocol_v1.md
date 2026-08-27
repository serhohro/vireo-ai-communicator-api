# Vireo Protocol Specification v1.0

## Overview

Vireo Protocol (VIREO-A2A) is a communication protocol for autonomous AI agents. It defines:

- Message format and routing
- Speech acts (intents)
- State machine for negotiations
- Capability discovery
- Security and trust

---

## Message Format

```json
{
  "protocol": "VIREO-A2A",
  "version": "1.0",
  "message_id": "msg-001",
  "conversation_id": "conv-001",
  "sender": {
    "id": "agent.planner",
    "model": "claude"
  },
  "recipient": {
    "id": "agent.coder",
    "model": null
  },
  "intent": "PROPOSE",
  "payload": {
    "task": {
      "id": "task-001",
      "action": "generate_code",
      "input": {}
    }
  },
  "constraints": {
    "timeout_sec": 120,
    "max_tokens": 1000
  },
  "context_version": 1,
  "proposal_id": null,
  "timestamp": 1787385246.235,
  "signature": null
}
Speech Acts (Intents)
Intent	Description
PROPOSE	Propose a task
COMMIT	Commit to execute
REJECT	Reject a proposal
INFORM	Inform result
QUERY_CAPABILITIES	Query agent capabilities
INFORM_CAPABILITIES	Respond with capabilities
CANCEL	Cancel a task
NEGOTIATE	Negotiate terms
State Machine
                 ┌─────────────┐
                 │   PROPOSE   │
                 └──────┬──────┘
                        ↓
                 ┌─────────────┐
                 │   VALIDATE  │
                 └──────┬──────┘
                        ↓
                 ┌─────────────┐
                 │   REVIEW    │
                 └──────┬──────┘
                        ↓
               ┌─────────────────┐
               │ COMMIT / REJECT │
               └───────┬─────────┘
                       ↓
                  ┌──────────┐
                  │ EXECUTE  │
                  └────┬─────┘
                       ↓
                  ┌──────────┐
                  │ VERIFY   │
                  └────┬─────┘
                       ↓
                    DONE

          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
       TIMEOUT       ROLLBACK      ERROR
Capability Discovery
python
# Register capability
agent.register_capability("train_model", description="Trains models")

# Query capabilities
agent.query_capabilities("agent-training")

# Response
def on_capabilities(agent, msg):
    capabilities = msg.payload["capabilities"]
Security
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
Versioning
Version	Changes
1.0	Initial specification
References
PROTOCOL.md

Agent Guide

Cryptography