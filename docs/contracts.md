# Vireo Contracts

**Version:** v1.4.3

This document describes the contract system in Vireo — a powerful mechanism for resource management, trust, and verification in AI-to-AI communication.

---

## 📋 ЗМІСТ

1. [Overview](#overview)
2. [Basic Contracts](#basic-contracts)
3. [Contract Fields](#contract-fields)
4. [Conditions](#conditions)
5. [Contract Validation](#contract-validation)
6. [Contract Execution](#contract-execution)
7. [Advanced Contracts](#advanced-contracts)
8. [Best Practices](#best-practices)

---

## 1. Overview

Contracts in Vireo define **resource limits**, **permissions**, and **validation rules** for AI-to-AI communication. They ensure that agents cannot exceed agreed-upon limits and provide a mechanism for trust verification.

### Why Contracts?

| Problem | Solution |
|---------|----------|
| Agents consuming unlimited tokens | `max_tokens` limit |
| Agents running indefinitely | `timeout_sec` limit |
| Agents exceeding budget | `max_cost_usd` limit |
| Unauthorized actions | `allowed_actions` list |
| Malicious agents | Cryptographic signing and verification |

---

## 2. Basic Contracts

### Simple Contract

```vireo
contract SimpleContract {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.05
    timeout_sec: Int = 30
    max_rounds: Int = 3
    allowed_actions: List[String] = ["train_model", "predict"]
}
Usage
vireo
// Create contract
let contract = SimpleContract {
    max_tokens: 500,
    timeout_sec: 10
}

// Propose with contract
propose Agent {
    task = "Train MNIST"
    contract = contract
}

// Execute with contract
execute Agent {
    contract = contract
    result = train_model("MNIST")
}
3. Contract Fields
Standard Fields
Field	Type	Default	Description
max_tokens	Int	1000	Maximum tokens for execution
max_cost_usd	Float	0.05	Maximum cost in USD
timeout_sec	Int	30	Execution timeout in seconds
max_rounds	Int	3	Maximum negotiation rounds
allowed_actions	List[String]	[]	List of allowed actions
Custom Fields
vireo
contract CustomContract {
    max_tokens: Int = 1000
    priority: String = "high"
    requires_approval: Bool = true
    data_sensitivity: String = "confidential"
    allowed_senders: List[String] = ["agent-vision", "agent-nlp"]
}
Field Types
Type	Description	Example
Int	Integer number	1000
Float	Floating point	0.05
String	Text string	"high"
Bool	Boolean	true
List[Type]	List of values	["train_model", "predict"]
4. Conditions
Basic Conditions
vireo
contract ConditionalContract {
    max_tokens: Int = 500
    timeout_sec: Int = 10
    requires_approval: Bool = true
    
    condition {
        if max_tokens > 200 {
            requires_approval = true
        } else {
            requires_approval = false
        }
    }
}
Complex Conditions
vireo
contract ComplexContract {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.10
    timeout_sec: Int = 60
    risk_level: String = "medium"
    requires_encryption: Bool = false
    requires_audit: Bool = false
    
    condition {
        if risk_level == "high" {
            max_cost_usd = 0.05
            requires_encryption = true
            requires_audit = true
        } else if risk_level == "medium" {
            requires_audit = true
        }
        
        if max_tokens > 2000 {
            timeout_sec = 120
            requires_approval = true
        }
    }
}
Nested Conditions
vireo
contract NestedContract {
    max_tokens: Int = 500
    data_type: String = "medical"
    region: String = "eu"
    
    condition {
        if data_type == "medical" {
            requires_encryption = true
            
            if region == "eu" {
                requires_gdpr = true
                max_tokens = 1000
            }
        }
    }
}
5. Contract Validation
Manual Validation
vireo
fn validate_contract(contract) {
    // Check basic fields
    if contract.max_tokens <= 0 {
        return error("max_tokens must be positive")
    }
    
    if contract.timeout_sec <= 0 {
        return error("timeout_sec must be positive")
    }
    
    if contract.max_cost_usd < 0 {
        return error("max_cost_usd must be non-negative")
    }
    
    // Check allowed actions
    if length(contract.allowed_actions) == 0 {
        return warning("No allowed actions specified")
    }
    
    return success("Contract is valid")
}
Automatic Validation
vireo
// Automatic validation on propose
propose Agent {
    task = "Train model"
    contract = Contract {
        max_tokens: 1000,
        timeout_sec: 30
    }
    // Contract is automatically validated
}

// Automatic validation on execute
execute Agent {
    contract = Contract {
        max_tokens: 1000,
        timeout_sec: 30
    }
    // Contract is automatically validated before execution
}
6. Contract Execution
Execution with Contract
vireo
fn execute_with_contract(task, contract) {
    // Validate contract
    let validation = validate_contract(contract)
    if validation != success {
        return error("Contract validation failed: " + validation)
    }
    
    // Execute with limits
    let result = execute_with_limits(task, contract)
    
    return result
}
Resource Monitoring
vireo
fn execute_with_limits(task, contract) {
    let start_time = time.now()
    let tokens_used = 0
    let cost = 0.0
    
    while time.now() - start_time < contract.timeout_sec {
        // Execute step
        let step_result = execute_step(task)
        
        // Update usage
        tokens_used = tokens_used + step_result.tokens
        cost = cost + step_result.cost
        
        // Check limits
        if tokens_used > contract.max_tokens {
            return error("Token limit exceeded")
        }
        
        if cost > contract.max_cost_usd {
            return error("Cost limit exceeded")
        }
    }
    
    return success({
        tokens_used: tokens_used,
        cost: cost,
        time_taken: time.now() - start_time
    })
}
7. Advanced Contracts
Multi-Signature Contract
vireo
contract MultiSigContract {
    max_tokens: Int = 1000
    timeout_sec: Int = 30
    required_signatures: Int = 2
    signers: List[String] = ["agent-vision", "agent-nlp", "agent-analyst"]
    
    condition {
        if required_signatures > length(signers) {
            error("More signatures required than signers available")
        }
    }
}
Escrow Contract
vireo
contract EscrowContract {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.10
    timeout_sec: Int = 60
    escrow_agent: String = "guardian-agent"
    release_conditions: List[String] = [
        "task_completed",
        "quality_verified",
        "report_generated"
    ]
    
    condition {
        if length(release_conditions) < 2 {
            requires_manual_release = true
        }
    }
}
Time-Limited Contract
vireo
contract TimeLimitedContract {
    max_tokens: Int = 500
    start_time: String = "2026-08-29T12:00:00Z"
    end_time: String = "2026-08-30T12:00:00Z"
    
    condition {
        let now = time.now()
        if now < start_time {
            error("Contract not yet active")
        }
        if now > end_time {
            error("Contract has expired")
        }
    }
}
Performance-Based Contract
vireo
contract PerformanceContract {
    max_tokens: Int = 2000
    timeout_sec: Int = 120
    min_accuracy: Float = 0.95
    max_latency_ms: Int = 100
    
    condition {
        if min_accuracy < 0.8 {
            requires_approval = true
        }
        if max_latency_ms > 200 {
            max_tokens = 1000
        }
    }
}
8. Best Practices
1. Always Set Reasonable Limits
vireo
// Good
contract GoodContract {
    max_tokens: Int = 1000
    timeout_sec: Int = 30
}

// Bad (no limits)
contract BadContract {
    // No limits set
}
2. Use Conditions for Dynamic Behavior
vireo
contract DynamicContract {
    max_tokens: Int = 1000
    data_size: Int = 1000
    
    condition {
        if data_size > 10000 {
            max_tokens = 5000
            timeout_sec = 120
        }
    }
}
3. Validate Contracts Early
vireo
// Validate before proposal
fn propose_with_validation(agent, task, contract) {
    let validation = validate_contract(contract)
    if validation != success {
        return error("Contract invalid: " + validation)
    }
    propose agent { task: task, contract: contract }
}
4. Log Contract Violations
vireo
fn execute_safely(task, contract) {
    let result = try_execute(task, contract)
    
    if result.status == "error" {
        log_contract_violation(contract, result.error)
        notify_guardian(contract, result.error)
    }
    
    return result
}
5. Use Guardian Agent for High-Security Contracts
vireo
contract HighSecurityContract {
    max_tokens: Int = 100
    timeout_sec: Int = 10
    requires_guardian: Bool = true
    
    condition {
        if requires_guardian {
            approve_execution()
        }
    }
}

execute ExecutorAgent {
    contract = HighSecurityContract {
        max_tokens: 50,
        timeout_sec: 5,
        requires_guardian: true
    }
    result = sensitive_operation()
    inform(GuardianAgent, result)
}
📋 CONTRACT CHECKLIST
Before deploying a contract, verify:

□ max_tokens is set and positive
□ timeout_sec is set and positive
□ max_cost_usd is set and non-negative
□ allowed_actions are specified
□ Conditions are logically sound
□ Contract is validated before use
□ Contract is logged for audit
□ Guardian agent is notified of violations
🔗 RELATED DOCUMENTATION
PROTOCOL.md — Full protocol specification

syntax.md — Complete language syntax

agents.md — Agent documentation

security.md — Security documentation