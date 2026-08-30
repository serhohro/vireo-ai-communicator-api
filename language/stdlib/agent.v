// ============================================================
// STANDARD LIBRARY: AGENTS
// ============================================================
// Version: 1.4.3
// ============================================================

// ============================================================
// ВИЗНАЧЕННЯ АГЕНТІВ
// ============================================================

// Створення агента
fn create_agent(id, model, capabilities) {
    agent id {
        identity: "did:key:" + id
        capabilities: capabilities
        model: model
    }
}

// Реєстрація агента
fn register_agent(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return register(agent)
}

// Отримання агента
fn get_agent(id) {
    return find_agent(id)
}

// Список агентів
fn list_agents() {
    return get_all_agents()
}

// ============================================================
// КОМУНІКАЦІЯ
// ============================================================

// Пропозиція
fn propose(agent_id, task, contract=None) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.propose(task, contract)
}

// Підтвердження
fn commit(agent_id, proposal_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.commit(proposal_id)
}

// Відхилення
fn reject(agent_id, proposal_id, reason="") {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.reject(proposal_id, reason)
}

// Виконання
fn execute(agent_id, proposal_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.execute(proposal_id)
}

// Інформування
fn inform(agent_id, recipient, message) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.inform(recipient, message)
}

// ============================================================
// МОЖЛИВОСТІ
// ============================================================

// Додавання можливості
fn add_capability(agent_id, name, description="") {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.add_capability(name, description)
}

// Перевірка можливості
fn has_capability(agent_id, name) {
    let agent = get_agent(agent_id)
    if agent == None {
        return false
    }
    return agent.has_capability(name)
}

// Список можливостей
fn get_capabilities(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.get_capabilities()
}

// ============================================================
// СТАН АГЕНТА
// ============================================================

// Отримання статусу
fn get_status(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.get_status()
}

// Отримання історії
fn get_history(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.get_history()
}

// Отримання розмов
fn get_conversations(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.get_conversations()
}

// ============================================================
// УПРАВЛІННЯ АГЕНТАМИ
// ============================================================

// Активація агента
fn activate(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.activate()
}

// Деактивація агента
fn deactivate(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.deactivate()
}

// Видалення агента
fn delete_agent(agent_id) {
    let agent = get_agent(agent_id)
    if agent == None {
        return error("Agent not found")
    }
    return agent.delete()
}

// ============================================================
// МАЙСТЕР-АГЕНТ
// ============================================================

// Створення майстра
fn create_master(name) {
    return MasterAgent(name)
}

// Реєстрація агентів у майстра
fn register_agents(master, agents) {
    return master.register_agents(agents)
}

// Оркестрація
fn orchestrate(master, task) {
    return master.orchestrate(task)
}

// Розподіл завдань
fn distribute_tasks(master, tasks) {
    return master.distribute_tasks(tasks)
}

// Моніторинг прогресу
fn monitor_progress(master, task_id) {
    return master.monitor_progress(task_id)
}