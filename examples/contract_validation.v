// ============================================================
// CONTRACT VALIDATION EXAMPLE
// Демонстрація валідації контрактів у Vireo
// ============================================================

// ============================================================
// 1. ВИЗНАЧЕННЯ КОНТРАКТІВ
// ============================================================

// Простий контракт з обмеженнями
contract SimpleContract {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.05
    timeout_sec: Int = 30
    max_rounds: Int = 3
    allowed_actions: List[String] = ["train_model", "predict", "evaluate"]
}

// Контракт з умовами
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

// Складний контракт для фінансових операцій
contract FinancialContract {
    max_tokens: Int = 2000
    max_cost_usd: Float = 0.10
    timeout_sec: Int = 60
    max_rounds: Int = 5
    allowed_actions: List[String] = ["analyze_data", "predict_trend", "generate_report"]
    risk_level: String = "medium"
    
    condition {
        if risk_level == "high" {
            max_cost_usd = 0.05
            requires_approval = true
        }
    }
}

// Контракт для медичних даних
contract MedicalContract {
    max_tokens: Int = 5000
    timeout_sec: Int = 120
    requires_encryption: Bool = true
    requires_audit: Bool = true
    allowed_senders: List[String] = ["agent-vision", "agent-nlp", "agent-analyst"]
    data_type: String = "medical_image"
    
    condition {
        if data_type == "medical_image" {
            requires_encryption = true
            max_tokens = 10000
        }
    }
}

// ============================================================
// 2. АГЕНТИ З КОНТРАКТАМИ
// ============================================================

agent ProposerAgent {
    identity: "did:key:z6MkhaXk1BZ4fGqFqQrZ..."
    capability propose_contract()
    capability negotiate_terms()
    capability sign_agreement()
}

agent ExecutorAgent {
    identity: "did:key:z6Mkhw9nBAwZ..."
    capability execute_contract()
    capability validate_contract()
    capability report_result()
}

agent GuardianAgent {
    identity: "did:key:z6Mki7k1BZ4fGqFqQrZ..."
    capability validate_security()
    capability check_compliance()
    capability audit_execution()
}

// ============================================================
// 3. ПЕРЕГОВОРИ З КОНТРАКТАМИ
// ============================================================

negotiation ContractNegotiation {
    party Proposer: ProposerAgent
    party Executor: ExecutorAgent
    party Guardian: GuardianAgent
    
    timeout = 30s
    max_rounds = 5
    
    on offer(contract: SimpleContract) {
        // Перевірка контракту
        if contract.max_tokens <= 1000 {
            // Приймаємо
            accept()
        } else if negotiation.round < negotiation.max_rounds {
            // Пропонуємо зустрічну пропозицію
            propose(counter_offer)
        } else {
            // Відхиляємо
            reject("Contract limits too high")
        }
    }
    
    on offer(contract: ConditionalContract) {
        // Перевірка умов
        if contract.requires_approval {
            // Запитуємо підтвердження
            request_approval()
        } else {
            accept()
        }
    }
    
    on offer(contract: MedicalContract) {
        // Медичні контракти вимагають додаткової перевірки
        if contract.requires_encryption && contract.requires_audit {
            // Перевірка Guardian
            guardian_check()
            accept()
        } else {
            reject("Medical contract requires encryption and audit")
        }
    }
}

// ============================================================
// 4. ВАЛІДАЦІЯ КОНТРАКТІВ
// ============================================================

// Функція валідації контракту
fn validate_contract(contract) {
    // Перевірка базових полів
    if contract.max_tokens <= 0 {
        return error("max_tokens must be positive")
    }
    
    if contract.timeout_sec <= 0 {
        return error("timeout_sec must be positive")
    }
    
    if contract.max_cost_usd < 0 {
        return error("max_cost_usd must be non-negative")
    }
    
    // Перевірка дозволених дій
    if length(contract.allowed_actions) == 0 {
        return warning("No allowed actions specified")
    }
    
    return success("Contract is valid")
}

// Функція виконання контракту
fn execute_contract(contract, task) {
    // Перевірка контракту
    let validation = validate_contract(contract)
    
    if validation != success {
        return error("Contract validation failed: " + validation)
    }
    
    // Виконання в межах контракту
    let result = execute_with_limits(task, contract)
    
    return result
}

// ============================================================
// 5. ПРОПОЗИЦІЇ З КОНТРАКТАМИ
// ============================================================

propose ProposerAgent {
    task = "Train neural network on MNIST dataset"
    contract = SimpleContract {
        max_tokens: 500,
        timeout_sec: 20,
        max_rounds: 2
    }
}

propose ProposerAgent {
    task = "Analyze medical images"
    contract = MedicalContract {
        max_tokens: 3000,
        timeout_sec: 60,
        requires_encryption: true,
        requires_audit: true,
        data_type: "medical_image"
    }
}

propose ProposerAgent {
    task = "Financial market prediction"
    contract = FinancialContract {
        max_tokens: 1500,
        max_cost_usd: 0.08,
        risk_level: "high"
    }
}

// ============================================================
// 6. ВИКОНАННЯ
// ============================================================

execute ExecutorAgent {
    contract = SimpleContract {
        max_tokens: 500,
        timeout_sec: 20
    }
    result = train_model("MNIST")
    inform(ProposerAgent, result)
}

execute ExecutorAgent {
    contract = MedicalContract {
        requires_encryption: true,
        requires_audit: true
    }
    result = analyze_images()
    inform(ProposerAgent, result)
}

// ============================================================
// 7. АУДИТ ТА ЗВІТНІСТЬ
// ============================================================

// Логування виконання контракту
fn log_contract_execution(contract, result) {
    print("Contract execution:")
    print("  Tokens used: " + result.tokens_used)
    print("  Time taken: " + result.time_taken + "s")
    print("  Cost: $" + result.cost)
    print("  Status: " + result.status)
}

// Звіт про контракт
fn generate_contract_report(contracts) {
    let total_tokens = 0
    let total_cost = 0.0
    
    for contract in contracts {
        total_tokens = total_tokens + contract.tokens_used
        total_cost = total_cost + contract.cost
    }
    
    print("Contract Report:")
    print("  Total contracts: " + length(contracts))
    print("  Total tokens: " + total_tokens)
    print("  Total cost: $" + total_cost)
}

// ============================================================
// 8. ПРИКЛАД ВИКОРИСТАННЯ
// ============================================================

// Створення та валідація контракту
let contract = SimpleContract {
    max_tokens: 800,
    timeout_sec: 25,
    max_rounds: 3,
    allowed_actions: ["train_model", "predict"]
}

let validation = validate_contract(contract)
print("Validation: " + validation)

// Пропозиція з контрактом
propose ProposerAgent {
    task = "Train MNIST with 2 layers"
    contract = contract
}

// Виконання
execute ExecutorAgent {
    contract = contract
    result = train_model("MNIST", epochs=10)
}

// Звіт
log_contract_execution(contract, result)

// ============================================================
// 9. ТЕСТИ ВАЛІДАЦІЇ
// ============================================================

// Тест 1: Валідний контракт
let test1 = SimpleContract {
    max_tokens: 1000,
    timeout_sec: 30
}
assert(validate_contract(test1) == success)

// Тест 2: Невалідний контракт (max_tokens = 0)
let test2 = SimpleContract {
    max_tokens: 0,
    timeout_sec: 30
}
assert(validate_contract(test2) != success)

// Тест 3: Контракт з умовами
let test3 = ConditionalContract {
    max_tokens: 300,
    timeout_sec: 15
}
assert(test3.requires_approval == true)

// Тест 4: Медичний контракт
let test4 = MedicalContract {
    max_tokens: 2000,
    requires_encryption: true,
    requires_audit: true
}
assert(test4.requires_encryption == true)
assert(test4.requires_audit == true)

// ============================================================
// 10. ВИСНОВОК
// ============================================================

print("✅ All contract validation tests passed!")
print("📋 Contract system is ready for production use")

// Output:
// ✅ All contract validation tests passed!
// 📋 Contract system is ready for production use