# Vireo Contracts Specification v3.0.0

## Overview

Contracts define agreements between AI agents in the Vireo ecosystem. They specify the terms, conditions, obligations, and penalties that govern agent interactions.

## Contract Structure

```vireo
contract MyContract {
    // Metadata
    name: string = "MyContract"
    version: string = "3.0.0"
    
    // Terms
    terms: map<string, any> = {
        "max_tokens": 1000,
        "timeout_sec": 30,
        "verify_timeout_sec": 15,
        "max_rounds": 3,
        "budget": 1000.50
    }
    
    // Conditions (must be satisfied)
    conditions: array<Condition> = [
        { type: "balance", min: 1000 },
        { type: "capability", requires: ["chat", "execute"] }
    ]
    
    // Obligations (actions to perform)
    obligations: array<Obligation> = [
        { 
            action: "execute_task", 
            deadline: "2026-09-10T00:00:00Z",
            retry_count: 3
        },
        { 
            action: "submit_report", 
            deadline: "2026-09-11T00:00:00Z" 
        }
    ]
    
    // Penalties (for violations)
    penalties: array<Penalty> = [
        { type: "fine", amount: 100 },
        { type: "reputation", deduction: 10 }
    ]
    
    // Verification rule
    verify: string = "result.accuracy > 0.9"
}
Field Specifications
Metadata
Field	Type	Required	Description
name	string	✅	Contract name
version	string	✅	Semantic version
Terms
Field	Type	Default	Description
max_tokens	int	1000	Maximum tokens allowed
timeout_sec	int	30	Timeout in seconds
verify_timeout_sec	int	15	Verification timeout
max_rounds	int	3	Maximum negotiation rounds
budget	float	0	Budget for execution
Conditions
Conditions are predicates that must be true for the contract to be valid.

Types:

balance — Minimum balance required

capability — Required agent capabilities

reputation — Minimum reputation score

time — Time-based condition

custom — Custom condition (expression)

Example:

vireo
conditions: array<Condition> = [
    { type: "balance", min: 1000 },
    { type: "capability", requires: ["chat", "execute"] },
    { type: "reputation", min: 80 },
    { type: "time", before: "2026-09-10T00:00:00Z" }
]
Obligations
Obligations are actions that must be performed.

Fields:

Field	Type	Required	Description
action	string	✅	Action to perform
deadline	string	❌	Deadline (ISO 8601)
retry_count	int	❌	Number of retries (default: 0)
Example:

vireo
obligations: array<Obligation> = [
    { 
        action: "execute_task", 
        deadline: "2026-09-10T00:00:00Z",
        retry_count: 3
    }
]
Penalties
Penalties for contract violations.

Types:

fine — Monetary penalty

reputation — Reputation deduction

suspension — Temporary suspension

termination — Contract termination

Example:

vireo
penalties: array<Penalty> = [
    { type: "fine", amount: 100 },
    { type: "reputation", deduction: 10 },
    { type: "suspension", duration: 3600 }
]
Contract Validation
Syntax Validation
Must have a name

Must have a version

Terms must be a map

Conditions must be an array

Obligations must be an array

Penalties must be an array

Semantic Validation
max_tokens >= 1

timeout_sec >= 1

verify_timeout_sec >= 1

max_rounds >= 1

Conditions must reference valid types

Obligations must have valid actions

Cryptographic Validation
Contract signed by all parties

Contract hash included in messages

Contract Lifecycle
text
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐
│ PROPOSE │───►│ NEGOTIATE│───►│  COMMIT  │───►│ EXECUTE  │───►│ VERIFY  │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └─────────┘
     │              │               │               │               │
     │              │               │               │               │
     ▼              ▼               ▼               ▼               ▼
 ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
 │  REJECT  │  │  REJECT  │  │  REJECT  │  │  TIMEOUT │  │  ESCALATE│
 └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
Phases
PROPOSE — Agent proposes contract

NEGOTIATE — Agents negotiate terms

COMMIT — Agents commit to contract

EXECUTE — Agents execute obligations

VERIFY — Results are verified

DONE — Contract completed

Contract Verification
Verification Rules
vireo
verify: string = "result.accuracy > 0.9"
Supported operators:

Comparison: >, <, >=, <=, ==, !=

Logical: &&, ||, !

Arithmetic: +, -, *, /

Example rules:

vireo
verify: string = "result.accuracy > 0.9 && result.completion_time < 60"
verify: string = "result.status == 'success'"
verify: string = "result.output > 0 && result.output < 100"
Verification Failure
When verification fails:

Agent may escalate the contract

Guardian Agent intervenes

Penalties may be applied

Contract may be renegotiated

Contract Serialization
JSON Format
json
{
    "name": "MyContract",
    "version": "3.0.0",
    "terms": {
        "max_tokens": 1000,
        "timeout_sec": 30
    },
    "conditions": [
        {"type": "balance", "min": 1000}
    ],
    "obligations": [
        {"action": "execute_task", "deadline": "2026-09-10T00:00:00Z"}
    ],
    "penalties": [
        {"type": "fine", "amount": 100}
    ],
    "verify": "result.accuracy > 0.9"
}
Binary Format
Contracts can be serialized to canonical binary format:

Sort fields by key

UTF-8 encode strings

Use BLAKE2b for hashing

Sign with Ed25519

Examples
Simple Contract
vireo
contract GreetingContract {
    name: string = "GreetingContract"
    version: string = "1.0.0"
    terms: map<string, any> = {
        "message": "Hello, World!",
        "timeout_sec": 10
    }
    conditions: array<Condition> = [
        { type: "capability", requires: ["chat"] }
    ]
    obligations: array<Obligation> = [
        { action: "send_greeting", deadline: "2026-09-10T00:00:00Z" }
    ]
    penalties: array<Penalty> = [
        { type: "reputation", deduction: 5 }
    ]
    verify: string = "result.status == 'sent'"
}
Complex Contract
vireo
contract MLTrainingContract {
    name: string = "MLTrainingContract"
    version: string = "3.0.0"
    terms: map<string, any> = {
        "max_tokens": 10000,
        "timeout_sec": 3600,
        "verify_timeout_sec": 300,
        "max_rounds": 5,
        "budget": 5000.0,
        "dataset": "imagenet",
        "model": "resnet50",
        "epochs": 100
    }
    conditions: array<Condition> = [
        { type: "capability", requires: ["train_model", "gpu"] },
        { type: "reputation", min: 90 }
    ]
    obligations: array<Obligation> = [
        { 
            action: "train_model", 
            deadline: "2026-09-10T00:00:00Z",
            retry_count: 3
        },
        { 
            action: "report_metrics", 
            deadline: "2026-09-11T00:00:00Z" 
        }
    ]
    penalties: array<Penalty> = [
        { type: "fine", amount: 500 },
        { type: "reputation", deduction: 20 },
        { type: "suspension", duration: 86400 }
    ]
    verify: string = "result.accuracy > 0.95 && result.loss < 0.1"
}