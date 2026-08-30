// ============================================================
// STANDARD LIBRARY: CONTRACTS
// ============================================================
// Version: 1.4.3
// ============================================================

// ============================================================
// ВИЗНАЧЕННЯ КОНТРАКТІВ
// ============================================================

// Створення контракту
fn create_contract(name, params) {
    contract name {
        max_tokens: params.max_tokens
        max_cost_usd: params.max_cost_usd
        timeout_sec: params.timeout_sec
        max_rounds: params.max_rounds
        allowed_actions: params.allowed_actions
    }
}

// Контракт за замовчуванням
fn default_contract() {
    contract DefaultContract {
        max_tokens: 1000
        max_cost_usd: 0.05
        timeout_sec: 30
        max_rounds: 3
        allowed_actions: ["train_model", "predict", "evaluate"]
    }
}

// ============================================================
// ВАЛІДАЦІЯ КОНТРАКТІВ
// ============================================================

// Валідація контракту
fn validate_contract(contract) {
    let errors = []
    
    // Перевірка полів
    if contract.max_tokens == None || contract.max_tokens <= 0 {
        errors.append("max_tokens must be positive")
    }
    
    if contract.timeout_sec == None || contract.timeout_sec <= 0 {
        errors.append("timeout_sec must be positive")
    }
    
    if contract.max_cost_usd == None || contract.max_cost_usd < 0 {
        errors.append("max_cost_usd must be non-negative")
    }
    
    if contract.max_rounds == None || contract.max_rounds < 1 {
        errors.append("max_rounds must be at least 1")
    }
    
    if length(errors) == 0 {
        return success("Contract is valid")
    } else {
        return error(errors)
    }
}

// Перевірка умов
fn check_conditions(contract) {
    if contract.condition != None {
        return evaluate_condition(contract.condition)
    }
    return true
}

// ============================================================
// ВИКОНАННЯ КОНТРАКТІВ
// ============================================================

// Виконання з контрактом
fn execute_with_contract(task, contract) {
    let validation = validate_contract(contract)
    if validation != success {
        return error("Contract validation failed")
    }
    
    let result = execute_with_limits(task, contract)
    return result
}

// Виконання з обмеженнями
fn execute_with_limits(task, contract) {
    let start_time = time.now()
    let tokens_used = 0
    let cost = 0.0
    let rounds = 0
    
    while rounds < contract.max_rounds {
        // Виконання кроку
        let step_result = execute_step(task)
        
        // Оновлення використання
        tokens_used = tokens_used + step_result.tokens
        cost = cost + step_result.cost
        rounds = rounds + 1
        
        // Перевірка лімітів
        if tokens_used > contract.max_tokens {
            return error("Token limit exceeded")
        }
        
        if cost > contract.max_cost_usd {
            return error("Cost limit exceeded")
        }
        
        let elapsed = time.now() - start_time
        if elapsed > contract.timeout_sec {
            return error("Timeout exceeded")
        }
        
        // Перевірка дозволених дій
        if step_result.action not in contract.allowed_actions {
            return error("Action not allowed: " + step_result.action)
        }
        
        // Перевірка завершення
        if step_result.is_complete {
            break
        }
    }
    
    return success({
        tokens_used: tokens_used,
        cost: cost,
        rounds: rounds,
        time_taken: time.now() - start_time,
        result: step_result
    })
}

// ============================================================
// МОНІТОРИНГ КОНТРАКТІВ
// ============================================================

// Моніторинг виконання
fn monitor_contract(contract, execution_id) {
    let status = get_execution_status(execution_id)
    return {
        contract: contract,
        status: status,
        tokens_used: status.tokens_used,
        cost: status.cost,
        time_remaining: contract.timeout_sec - status.elapsed
    }
}

// Логування контракту
fn log_contract(contract, result) {
    print("Contract execution:")
    print("  Tokens used: " + result.tokens_used)
    print("  Cost: $" + result.cost)
    print("  Time: " + result.time_taken + "s")
    print("  Status: " + result.status)
}

// ============================================================
// СПЕЦІАЛЬНІ КОНТРАКТИ
// ============================================================

// Фінансовий контракт
fn financial_contract(budget) {
    contract FinancialContract {
        max_tokens: 500
        max_cost_usd: budget * 0.1
        timeout_sec: 60
        max_rounds: 5
        allowed_actions: ["analyze_data", "predict_trend", "generate_report"]
    }
}

// Медичний контракт
fn medical_contract() {
    contract MedicalContract {
        max_tokens: 5000
        timeout_sec: 120
        requires_encryption: true
        requires_audit: true
        allowed_actions: ["analyze_medical_data", "detect_anomalies", "generate_diagnosis"]
    }
}

// Складний контракт
fn complex_contract(params) {
    contract ComplexContract {
        max_tokens: params.max_tokens
        max_cost_usd: params.budget
        timeout_sec: params.timeout
        max_rounds: params.rounds
        allowed_actions: params.actions
        requires_approval: params.approval
        risk_level: params.risk
    }
}

// ============================================================
// УТИЛІТИ
// ============================================================

// Копіювання контракту
fn copy_contract(contract) {
    return Contract(contract)
}

// Об'єднання контрактів
fn merge_contracts(c1, c2) {
    contract MergedContract {
        max_tokens: min(c1.max_tokens, c2.max_tokens)
        max_cost_usd: min(c1.max_cost_usd, c2.max_cost_usd)
        timeout_sec: min(c1.timeout_sec, c2.timeout_sec)
        max_rounds: min(c1.max_rounds, c2.max_rounds)
        allowed_actions: intersection(c1.allowed_actions, c2.allowed_actions)
    }
}

// Розширення контракту
fn extend_contract(contract, extensions) {
    contract ExtendedContract {
        max_tokens: extensions.max_tokens ?? contract.max_tokens
        max_cost_usd: extensions.max_cost_usd ?? contract.max_cost_usd
        timeout_sec: extensions.timeout_sec ?? contract.timeout_sec
        max_rounds: extensions.max_rounds ?? contract.max_rounds
        allowed_actions: contract.allowed_actions + extensions.actions
    }
}