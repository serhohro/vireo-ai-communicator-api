markdown
# Vireo State Machine v3.0.0

## Overview

Vireo uses a formal state machine for agent communication.

## States
┌─────────┐ ┌─────────┐ ┌───────────┐ ┌────────┐ ┌─────────┐ ┌────────┐ ┌────────┐
│ DISCOVER │ ──► │ PROPOSE │ ──► │ NEGOTIATE │ ──► │ COMMIT │ ──► │ EXECUTE │ ──► │ VERIFY │ ──► │ DONE │
└─────────┘ └─────────┘ └───────────┘ └────────┘ └─────────┘ └────────┘ └────────┘
│ │ │ │ │ │ │
│ │ │ │ │ │ │
└───────────────┴───────────────┴───────────────┴───────────────┴───────────────┴───────────────┘
(All states can escalate to ESCALATE)

text

## Transitions

| From | To | Condition |
|------|----|-----------|
| DISCOVER | PROPOSE | Agent found |
| PROPOSE | NEGOTIATE | Proposal accepted |
| PROPOSE | REJECT | Proposal rejected |
| NEGOTIATE | COMMIT | Agreement reached |
| NEGOTIATE | REJECT | Negotiation failed |
| COMMIT | EXECUTE | Contract signed |
| COMMIT | REJECT | Contract rejected |
| EXECUTE | VERIFY | Execution complete |
| EXECUTE | TIMEOUT | Execution timed out |
| VERIFY | DONE | Verification passed |
| VERIFY | ESCALATE | Verification failed |
| * | ESCALATE | Dispute |
| ESCALATE | DONE | Resolved |

## Timeouts

| State | Timeout |
|-------|---------|
| DISCOVER | 30s |
| PROPOSE | 60s |
| NEGOTIATE | 120s |
| COMMIT | 30s |
| EXECUTE | 300s |
| VERIFY | 60s |
| DONE | ∞ |
| ESCALATE | 600s |

## Guardian Agent

The Guardian Agent monitors all transactions and intervenes when:
- Timeout occurs
- Dispute is escalated
- Fraud is detected

## Formal Specification

See `protocol.tla+` for TLA+ formal specification.