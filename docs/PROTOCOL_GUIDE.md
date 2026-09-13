# Vireo Protocol Guide

Deep dive into the A2A (Agent-to-Agent) Protocol.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Protocol Architecture](#protocol-architecture)
3. [Message Types](#message-types)
4. [State Machine](#state-machine)
5. [Negotiation Flow](#negotiation-flow)
6. [Security](#security)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## Overview

Vireo A2A Protocol is a secure, reliable communication protocol for AI agents. It enables:

- **Discovery**: Agents find each other
- **Negotiation**: Agents agree on contracts
- **Execution**: Tasks are performed
- **Verification**: Results are verified
- **Escalation**: Disputes are resolved

### Protocol Principles

> *"Don't prove that Vireo can run more AI models. Prove that Vireo can make independently implemented AI agents interoperable."* — ChatGPT

> *"Standards are born from open specifications, not single repositories."* — Perplexity

---

## Protocol Architecture
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │
│ │ Agents │ │ Contracts │ │ Business Logic │ │
│ └─────────────┘ └─────────────┘ └────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ PROTOCOL LAYER │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │
│ │ State │ │ Message │ │ Verification │ │
│ │ Machine │ │ Routing │ │ │ │
│ └─────────────┘ └─────────────┘ └────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ SECURITY LAYER │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │
│ │ Ed25519 │ │ DIDs │ │ Trust Bootstrap │ │
│ └─────────────┘ └─────────────┘ └────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ TRANSPORT LAYER │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │
│ │ WebSocket │ │ gRPC │ │ HTTP │ │
│ └─────────────┘ └─────────────┘ └────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

text

---

## Message Types

### Message Structure

```json
{
    "version": "3.0.0",
    "type": "propose",
    "id": "msg_1234567890",
    "sender": "did:vireo:alice",
    "recipient": "did:vireo:bob",
    "timestamp": 1700000000,
    "nonce": "n_abcdef123",
    "payload": {
        "task": "analyze_code",
        "parameters": {
            "language": "python",
            "depth": "full"
        }
    },
    "signature": "sig_abcdef1234567890"
}
Core Message Types
Type	Description	Direction
propose	Initiate negotiation	Initiator → Responder
commit	Accept proposal	Responder → Initiator
execute	Execute task	Either
verify	Verify execution	Either
escalate	Escalate dispute	Either
done	Complete task	Either
error	Error occurred	Either
Extended Message Types
Type	Description
discover	Discover agent capabilities
negotiate	Negotiate contract terms
ack	Acknowledge message receipt
heartbeat	Keep connection alive
status	Report status update
cancel	Cancel pending operation
State Machine
States
vireo
state IDLE {
    description: "Initial state"
    transitions: ["PROPOSE"]
}

state PROPOSE {
    description: "Proposal sent"
    transitions: ["COMMIT", "CANCEL"]
}

state COMMIT {
    description: "Proposal accepted"
    transitions: ["EXECUTE", "ESCALATE"]
}

state EXECUTE {
    description: "Executing task"
    transitions: ["VERIFY", "ESCALATE"]
}

state VERIFY {
    description: "Verifying result"
    transitions: ["DONE", "ESCALATE"]
}

state ESCALATE {
    description: "Dispute resolution"
    transitions: ["DONE", "CANCEL"]
}

state DONE {
    description: "Task completed"
    transitions: []
}

state CANCEL {
    description: "Task cancelled"
    transitions: []
}
State Diagram
text
                    ┌──────────────┐
                    │              │
                    │     IDLE     │
                    │              │
                    └──────┬───────┘
                           │ propose
                           ▼
                    ┌──────────────┐
                    │              │
                    │   PROPOSE    │
                    │              │
                    └──────┬───────┘
                           │ commit
                           ▼
                    ┌──────────────┐
                    │              │
                    │    COMMIT    │
                    │              │
                    └──────┬───────┘
                           │ execute
                           ▼
                    ┌──────────────┐
                    │              │
                    │   EXECUTE    │
                    │              │
                    └──────┬───────┘
                           │ verify
                           ▼
                    ┌──────────────┐
                    │              │
                    │    VERIFY    │◄─────┐
                    │              │      │
                    └──────┬───────┘      │
                           │ done         │
                           ▼              │
                    ┌──────────────┐      │
                    │              │      │
                    │     DONE     │      │
                    │              │      │
                    └──────────────┘      │
                                         │
                    ┌──────────────┐      │
                    │              │      │
                    │   ESCALATE   │──────┘
                    │              │
                    └──────────────┘
State Transition Rules
vireo
// TLA+ Specification
Transition = {
    "IDLE": {
        "propose": "PROPOSE",
        "cancel": "CANCEL"
    },
    "PROPOSE": {
        "commit": "COMMIT",
        "cancel": "CANCEL"
    },
    "COMMIT": {
        "execute": "EXECUTE",
        "escalate": "ESCALATE"
    },
    "EXECUTE": {
        "verify": "VERIFY",
        "escalate": "ESCALATE",
        "done": "DONE"  // Direct completion
    },
    "VERIFY": {
        "done": "DONE",
        "escalate": "ESCALATE"
    },
    "ESCALATE": {
        "done": "DONE",
        "cancel": "CANCEL"
    },
    "DONE": {},
    "CANCEL": {}
}
Negotiation Flow
Simple Negotiation
vireo
// Agent A (Initiator)
Agent A sends PROPOSE → Agent B
    {
        task: "data_analysis",
        price: 50,
        deadline: "2024-12-31"
    }

// Agent B (Responder)
Agent B sends COMMIT → Agent A
    {
        accepted: true,
        counter_offer: {
            price: 75,
            deadline: "2024-12-20"
        }
    }

// Agent A
Agent A sends EXECUTE → Agent B
    {
        data: "dataset.csv",
        parameters: {
            analysis_type: "statistical"
        }
    }

// Agent B
Agent B sends VERIFY → Agent A
    {
        result: "analysis_complete",
        metrics: {
            processing_time: 45.2,
            memory_used: 2.3
        }
    }

// Agent A
Agent A sends DONE → Agent B
    {
        status: "success",
        payment: 75
    }
Complex Negotiation with Escalation
vireo
// Phase 1: Initial Negotiation
Agent A → PROPOSE → Agent B
Agent B → COUNTER → Agent A
Agent A → COUNTER → Agent B
Agent B → COMMIT → Agent A

// Phase 2: Execution
Agent A → EXECUTE → Agent B
Agent B → EXECUTING → Agent A
Agent B → VERIFY → Agent A

// Phase 3: Dispute
Agent A → ESCALATE → Agent B
    {
        reason: "Quality below agreement",
        evidence: [
            "incorrect_data",
            "delayed_response"
        ]
    }

// Phase 4: Resolution
Agent B → ESCALATE_RESPONSE → Agent A
    {
        resolution: "partial_refund",
        amount: 25,
        reason: "Quality issue acknowledged"
    }

// Phase 5: Completion
Agent A → DONE → Agent B
    {
        status: "resolved",
        payment: 50
    }
Security
Message Signing
vireo
// Sign message
let message = {
    type: "propose",
    payload: {
        task: "analysis"
    },
    sender: did_alice,
    recipient: did_bob
}

let signature = crypto.sign(
    data: message,
    private_key: alice_private_key
)

message.signature = signature

// Verify message
let valid = crypto.verify(
    data: message,
    signature: message.signature,
    public_key: bob_public_key
)
Trust Bootstrap
vireo
// Initial trust establishment
let trust = trust_bootstrap(
    method: "web-of-trust",
    witnesses: [
        "did:vireo:trusted1",
        "did:vireo:trusted2",
        "did:vireo:trusted3"
    ],
    threshold: 2  // At least 2 witnesses needed
)

// Check trust
let trusted = trust.verify(agent_id: "did:vireo:new_agent")

// Update trust
trust.update(
    agent_id: "did:vireo:new_agent",
    trust_score: 0.85,
    reason: "Successful negotiations"
)
Replay Protection
vireo
// Nonce generation
let nonce = crypto.generate_nonce()

// Message with nonce
let message = {
    type: "propose",
    nonce: nonce,
    payload: { task: "analysis" }
}

// Check nonce
let nonce_manager = NonceManager()

// Verify nonce uniqueness
if nonce_manager.check_nonce(nonce) {
    // Process message
    nonce_manager.record_nonce(nonce)
} else {
    // Replay attack detected
    respond({
        type: "error",
        payload: {
            error: "Invalid nonce",
            code: "REPLAY_DETECTED"
        }
    })
}
Error Handling
Error Types
vireo
// Standard errors
ERROR_UNKNOWN = "unknown_error"
ERROR_INVALID_STATE = "invalid_state"
ERROR_INVALID_MESSAGE = "invalid_message"
ERROR_INVALID_SIGNATURE = "invalid_signature"
ERROR_NONCE_REPLAY = "nonce_replay"
ERROR_TIMEOUT = "timeout"
ERROR_NOT_FOUND = "not_found"
ERROR_PERMISSION = "permission_denied"
ERROR_UNSUPPORTED = "unsupported_operation"
ERROR_BUSY = "agent_busy"
ERROR_LIMIT = "rate_limit"
Error Response
vireo
// Error message format
{
    type: "error",
    payload: {
        error: {
            code: "invalid_state",
            message: "Cannot process PROPOSE in COMMIT state",
            details: {
                current_state: "COMMIT",
                attempted_type: "propose",
                allowed_types: ["execute", "escalate"]
            }
        }
    },
    id: "msg_1234567890",
    sender: "did:vireo:agent",
    timestamp: 1700000000
}
Retry Logic
vireo
// Retry configuration
let retry_config = {
    max_retries: 3,
    initial_delay: 1,  // seconds
    max_delay: 60,    // seconds
    backoff_factor: 2
}

// Retry function
fn retry_operation(operation: fn() -> Message) -> Message {
    for attempt in 0..retry_config.max_retries {
        try {
            let result = operation()
            return result
        } catch error {
            if error.type == "timeout" and attempt < retry_config.max_retries {
                let delay = min(
                    retry_config.initial_delay * pow(2, attempt),
                    retry_config.max_delay
                )
                sleep(delay)
                continue
            }
            return error_message(error)
        }
    }
    return error_message("Max retries exceeded")
}
Best Practices
1. Message Design
vireo
// DO: Clear, consistent message structure
message Propose {
    version: "3.0.0"
    type: "propose"
    id: generate_id()
    sender: get_did()
    recipient: peer_did
    timestamp: now()
    payload: {
        task: clear_task_name,
        parameters: {
            param1: value1,
            param2: value2
        },
        contract: {
            price: 100,
            deadline: "2024-12-31",
            terms: ["quality", "timeliness"]
        }
    },
    signature: sign(payload)
}

// DON'T: Ambiguous, inconsistent structure
message BadPropose {
    type: "request"
    data: {task: "something", params: [...]}
    // Missing required fields
}
2. State Management
vireo
// DO: Track state explicitly
let state = {
    current_state: "IDLE",
    history: [],
    context: {
        message_id: null,
        offer: null,
        attempts: 0
    }
}

// DO: Validate transitions
fn validate_transition(from: string, to: string) -> bool {
    return allowed_transitions[from].includes(to)
}

// DO: Handle all states
match state.current_state {
    "IDLE" => handle_idle()
    "PROPOSE" => handle_propose()
    "COMMIT" => handle_commit()
    "EXECUTE" => handle_execute()
    "VERIFY" => handle_verify()
    "ESCALATE" => handle_escalate()
    "DONE" => handle_done()
    "CANCEL" => handle_cancel()
    _ => handle_unknown()
}
3. Security Best Practices
vireo
// DO: Always verify signatures
if not verify_signature(message) {
    reject("Invalid signature")
    return
}

// DO: Check nonce for replay attacks
if not nonce_manager.check(message.nonce) {
    reject("Replay attack detected")
    return
}

// DO: Validate message schema
if not validate_schema(message) {
    reject("Invalid message format")
    return
}

// DO: Rate limiting
if rate_limiter.is_limited(sender_did) {
    reject("Rate limit exceeded")
    return
}
4. Performance Optimization
vireo
// DO: Batch operations
let batch = {
    operations: [
        {type: "verify", data: data1},
        {type: "verify", data: data2},
        {type: "verify", data: data3}
    ]
}

// DO: Cache results
let cache = Cache(size: 1000, ttl: 300)
let cached_result = cache.get(cache_key)
if cached_result {
    return cached_result
}

// DO: Use async operations
let futures = [
    async_process(data1),
    async_process(data2),
    async_process(data3)
]
let results = await_all(futures)
5. Error Handling
vireo
// DO: Return meaningful errors
respond({
    type: "error",
    payload: {
        error: {
            code: "VALIDATION_FAILED",
            message: "Invalid parameter: 'price' must be positive",
            field: "price",
            attempted_value: -10
        }
    }
})

// DO: Log errors
logger.error("Validation failed", {
    field: "price",
    value: -10,
    context: message_context
})

// DO: Graceful degradation
if service_unavailable() {
    let fallback = get_fallback_response()
    respond(fallback)
}
Protocol Extensions
Guardian Agent Protocol
vireo
// Guardian Agent ensures protocol compliance
agent Guardian {
    on message "propose" {
        // Check if proposal is valid
        let validation = validate_proposal(message)
        
        if validation.valid {
            // Forward to target
            forward(message)
        } else {
            // Reject invalid proposal
            respond({
                type: "reject",
                payload: {
                    reason: validation.reason,
                    suggestions: validation.suggestions
                }
            })
        }
    }
}
MCP (Model Context Protocol)
vireo
// MCP integration
import mcp

let mcp_server = mcp.Server(
    name: "Vireo MCP Server",
    version: "1.0.0"
)

mcp_server.add_tool(
    name: "analyze_code",
    description: "Analyze code for security issues",
    handler: analyze_code
)

mcp_server.add_resource(
    name: "security_rules",
    type: "ruleset",
    handler: get_security_rules
)
🔗 Next Steps
Security Guide

API Reference

Deployment Guide

Examples

🆘 Need Help?
Join our Discord

Open an Issue

Check the Specification