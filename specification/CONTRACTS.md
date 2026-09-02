```markdown
# 📜 Vireo Contract Specification

**Version:** 2.0.1  
**Status:** Draft  
**Last Updated:** 2026-01-15

---

## 1. Overview

Contracts are the central mechanism in Vireo for defining agreements between agents. They specify:

- **Parties**: Which agents are involved
- **Terms**: Constraints and limits
- **Obligations**: What each party must do
- **Conditions**: When the contract is valid
- **On Failure**: What happens if something goes wrong

---

## 2. Contract Structure

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_id` | string | ✅ | Unique identifier |
| `parties` | string[] | ✅ | Agent IDs involved |
| `terms` | Terms | ✅ | Contract terms |
| `obligations` | object | ✅ | Per-party obligations |
| `condition` | string | ❌ | Condition expression |
| `on_failure` | string | ❌ | Failure handling |
| `signatures` | object | ❌ | Signatures from parties |
| `status` | string | ❌ | Contract status |
| `created_at` | string | ❌ | Creation timestamp |
| `updated_at` | string | ❌ | Last update timestamp |

### Terms

| Field | Type | Description |
|-------|------|-------------|
| `max_tokens` | integer | Maximum tokens for LLM calls |
| `timeout_sec` | integer | Timeout in seconds |
| `max_cost_usd` | float | Maximum cost in USD |
| `max_rounds` | integer | Maximum negotiation rounds |
| `deadline` | string | Deadline (ISO 8601) |

### Obligation

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | Capability name to execute |
| `input` | object | Input parameters |
| `output` | object | Expected output |
| `depends_on` | string[] | Dependencies on other obligations |

---

## 3. Contract Lifecycle
┌────────────┐
│ DRAFT │ ← Initial creation
└─────┬──────┘
│
▼
┌────────────┐
│ PROPOSED │ ← Proposed to parties
└─────┬──────┘
│
▼
┌────────────┐
│ ACCEPTED │ ← All parties accepted
└─────┬──────┘
│
▼
┌────────────┐
│ COMMITTED│ ← All parties signed
└─────┬──────┘
│
▼
┌────────────┐
│ EXECUTING │ ← Being executed
└─────┬──────┘
│
▼
┌────────────┐
│ VERIFYING │ ← Being verified
└─────┬──────┘
│
▼
┌────────────┐
│ DONE │ ← Complete
└────────────┘

text

### Error States

| Status | Description |
|--------|-------------|
| `REJECTED` | Rejected by a party |
| `CANCELLED` | Cancelled by one party |
| `FAILED` | Execution failed |
| `ESCALATED` | Escalated for review |
| `TIMEOUT` | Timed out |
| `DISPUTED` | Dispute between parties |

---

## 4. Contract Validation

### Validation Rules

```python
def validate_contract(contract: Contract) -> List[ValidationError]:
    errors = []
    
    # 1. Check required fields
    if not contract.parties:
        errors.append("At least 2 parties required")
    
    # 2. Check terms
    if contract.terms.max_tokens is not None and contract.terms.max_tokens <= 0:
        errors.append("max_tokens must be positive")
    
    if contract.terms.timeout_sec is not None and contract.terms.timeout_sec <= 0:
        errors.append("timeout_sec must be positive")
    
    if contract.terms.max_cost_usd is not None and contract.terms.max_cost_usd < 0:
        errors.append("max_cost_usd must be non-negative")
    
    # 3. Check obligations
    for party, obligation in contract.obligations.items():
        if party not in contract.parties:
            errors.append(f"Party {party} not in parties list")
        
        if not obligation.action:
            errors.append(f"Obligation for {party} missing action")
        
        # Check input types match capability
        capability = get_capability(obligation.action)
        if capability:
            for param, value in obligation.input.items():
                if param not in capability.inputs:
                    errors.append(f"Unknown input '{param}' for action '{obligation.action}'")
    
    # 4. Check signatures
    for party in contract.parties:
        if party not in contract.signatures:
            errors.append(f"Missing signature from {party}")
    
    return errors
5. Contract Execution
Execution Flow
python
def execute_contract(contract: Contract) -> ExecutionResult:
    # 1. Validate contract
    errors = validate_contract(contract)
    if errors:
        return ExecutionResult(status="FAILED", errors=errors)
    
    # 2. Check condition
    if contract.condition and not evaluate_condition(contract.condition):
        return ExecutionResult(status="CANCELLED", reason="Condition not met")
    
    # 3. Execute obligations
    results = {}
    for party, obligation in contract.obligations.items():
        try:
            result = execute_capability(
                agent=party,
                capability=obligation.action,
                inputs=resolve_references(obligation.input, results)
            )
            results[party] = result
        except Exception as e:
            if contract.on_failure == "escalate":
                return ExecutionResult(status="ESCALATED", error=str(e))
            elif contract.on_failure == "retry":
                # Retry logic
                pass
            else:
                return ExecutionResult(status="FAILED", error=str(e))
    
    # 4. Verify results
    verification = verify_execution(contract, results)
    if not verification.verified:
        return ExecutionResult(status="VERIFY_FAILED", proof=verification.proof)
    
    return ExecutionResult(status="DONE", results=results)
6. Contract Verification
Verification Process
python
def verify_execution(contract: Contract, results: Dict[str, Any]) -> VerificationResult:
    # 1. Verify signatures
    for party in contract.parties:
        if not verify_signature(
            contract.contract_id,
            contract.signatures[party],
            get_public_key(party)
        ):
            return VerificationResult(verified=False, reason=f"Invalid signature from {party}")
    
    # 2. Verify outputs match contract
    for party, obligation in contract.obligations.items():
        if obligation.output:
            for field, expected in obligation.output.items():
                if field not in results[party]:
                    return VerificationResult(
                        verified=False,
                        reason=f"Missing output field '{field}' from {party}"
                    )
    
    # 3. Verify constraints
    total_tokens = sum(result.get("tokens", 0) for result in results.values())
    if contract.terms.max_tokens and total_tokens > contract.terms.max_tokens:
        return VerificationResult(
            verified=False,
            reason=f"Token limit exceeded: {total_tokens} > {contract.terms.max_tokens}"
        )
    
    # 4. Generate proof
    proof = generate_verification_proof(contract, results)
    
    return VerificationResult(verified=True, proof=proof)
7. Contract Templates
Template: Service Agreement
json
{
  "contract_id": "uuid",
  "parties": ["service_provider", "client"],
  "terms": {
    "max_tokens": 1000,
    "timeout_sec": 60
  },
  "obligations": {
    "service_provider": {
      "action": "provide_service",
      "input": {"request": "$ref.client.request"}
    },
    "client": {
      "action": "pay",
      "input": {"amount": "$ref.service_provider.cost"}
    }
  },
  "on_failure": "escalate"
}
Template: Data Exchange
json
{
  "contract_id": "uuid",
  "parties": ["data_provider", "data_consumer"],
  "terms": {
    "max_tokens": 5000,
    "timeout_sec": 120,
    "max_cost_usd": 10.0
  },
  "obligations": {
    "data_provider": {
      "action": "provide_data",
      "input": {"dataset": "$ref.data_consumer.requested_dataset"},
      "output": {"data": "$ref.provided_data"}
    },
    "data_consumer": {
      "action": "process_data",
      "input": {"data": "$ref.data_provider.data"},
      "output": {"result": "$ref.processed_result"}
    }
  },
  "condition": "data_provider.data.valid == true",
  "on_failure": "escalate"
}
Template: Negotiation
json
{
  "contract_id": "uuid",
  "parties": ["buyer", "seller"],
  "terms": {
    "max_tokens": 500,
    "timeout_sec": 300,
    "max_rounds": 10
  },
  "obligations": {
    "buyer": {
      "action": "negotiate",
      "input": {"min_price": 0, "max_price": "$ref.seller.max_price"}
    },
    "seller": {
      "action": "negotiate",
      "input": {"min_price": "$ref.buyer.max_price", "max_price": 100}
    }
  },
  "condition": "buyer.max_price >= seller.min_price",
  "on_failure": "cancel"
}
8. Contract Storage
Redis Schema
redis
# Store contract
HSET contract:{contract_id} {
    "contract_id": "...",
    "parties": "agent1,agent2",
    "status": "DRAFT",
    "terms": "{...}",
    "obligations": "{...}",
    "created_at": "..."
}

# Index by party
SADD contracts:party:{party_id} {contract_id}

# Index by status
SADD contracts:status:{status} {contract_id}
9. Security
Contract Security Rules
No Self-Executing Contracts: Contracts must be explicitly executed

No Unbounded Operations: All operations must have limits

No External Code Execution: Only Vireo capabilities

No Unauthorized Access: Only parties can access contract

No Double-Spending: Each contract can only be executed once

10. Examples
Medical Analysis Contract
vireo
contract "medical_analysis" {
    parties: [radiologist_agent, report_agent]
    terms: {
        max_tokens: 2000
        timeout_sec: 180
        max_cost_usd: 15.0
    }
    obligations: {
        radiologist_agent: {
            action: analyze_image
            input: {
                image_url: "s3://medical/scan_20260115.dcm"
                model: "covid-19-detection"
            }
            output: {
                diagnosis: $ref.diagnosis
                confidence: $ref.confidence
            }
        }
        report_agent: {
            action: generate_report
            input: {
                diagnosis: $ref.radiologist_agent.diagnosis
                confidence: $ref.radiologist_agent.confidence
                patient_id: "P-12345"
            }
            output: {
                report_url: $ref.report_url
            }
        }
    }
    condition: radiologist_agent.confidence > 0.90
    on_failure: "escalate"
}
Financial Trading Contract
vireo
contract "trade_execution" {
    parties: [trader_agent, exchange_agent]
    terms: {
        max_tokens: 1000
        timeout_sec: 10
        max_cost_usd: 1000.0
    }
    obligations: {
        trader_agent: {
            action: submit_order
            input: {
                symbol: "AAPL"
                quantity: 100
                limit_price: 250.00
                order_type: "LIMIT"
            }
            output: {
                order_id: $ref.order_id
            }
        }
        exchange_agent: {
            action: execute_order
            input: {
                order_id: $ref.trader_agent.order_id
            }
            output: {
                execution_price: $ref.price
                executed_quantity: $ref.qty
                status: $ref.status
            }
        }
    }
    condition: exchange_agent.status == "FILLED"
    on_failure: "escalate"
}