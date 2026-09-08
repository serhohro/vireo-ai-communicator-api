// ============================================================
// STANDARD LIBRARY: PROTOCOL OPERATIONS
// ============================================================
// Version: 3.0.0
// ============================================================

// ============================================================
// СТАН
// ============================================================

// Стани протоколу
let STATE_INIT = "init"
let STATE_PROPOSE = "propose"
let STATE_COMMIT = "commit"
let STATE_EXECUTE = "execute"
let STATE_VERIFY = "verify"
let STATE_ESCALATE = "escalate"
let STATE_DONE = "done"
let STATE_FAILED = "failed"
let STATE_TIMEOUT = "timeout"

// ============================================================
// ПОВІДОМЛЕННЯ
// ============================================================

// Створення повідомлення
fn create_message(type, sender, recipient, payload) {
    return {
        type: type,
        sender: sender,
        recipient: recipient,
        payload: payload,
        timestamp: time.now(),
        id: generate_uuid()
    }
}

// Підпис повідомлення
fn sign_message(message, private_key) {
    let data = message.payload
    let signature = sign(data, private_key)
    message.signature = signature
    return message
}

// Верифікація повідомлення
fn verify_message(message, public_key) {
    return verify(message.payload, message.signature, public_key)
}

// ============================================================
// ВІДПРАВКА
// ============================================================

// Відправка повідомлення
fn send_message(channel, message) {
    return Transport.send(channel, message)
}

// Відправка з підписом
fn send_signed(channel, message, private_key) {
    let signed = sign_message(message, private_key)
    return send_message(channel, signed)
}

// Відправка з очікуванням відповіді
fn send_and_wait(channel, message, timeout=30) {
    send_message(channel, message)
    return receive_response(channel, message.id, timeout)
}

// ============================================================
// ОТРИМАННЯ
// ============================================================

// Отримання повідомлення
fn receive_message(channel) {
    return Transport.receive(channel)
}

// Підписка на канал
fn subscribe(channel, handler) {
    return Transport.subscribe(channel, handler)
}

// Відписка від каналу
fn unsubscribe(channel, handler) {
    return Transport.unsubscribe(channel, handler)
}

// ============================================================
// ПРОТОКОЛ
// ============================================================

// Створення протоколу
fn create_protocol(name, initial_state) {
    return {
        name: name,
        state: initial_state,
        history: [],
        context: {}
    }
}

// Перехід стану
fn transition(protocol, event, context={}) {
    let old_state = protocol.state
    let new_state = calculate_next_state(old_state, event)
    
    if new_state == None {
        return error("Invalid transition")
    }
    
    protocol.state = new_state
    protocol.history.append({
        from: old_state,
        to: new_state,
        event: event,
        context: context,
        timestamp: time.now()
    })
    
    return success(new_state)
}

// Перевірка стану
fn is_state(protocol, state) {
    return protocol.state == state
}

// Перевірка термінального стану
fn is_terminal(protocol) {
    return protocol.state in [STATE_DONE, STATE_FAILED, STATE_TIMEOUT]
}

// Отримання історії
fn get_history(protocol) {
    return protocol.history
}

// ============================================================
// НЕЙТРАЛІЗАЦІЯ
// ============================================================

// Створення пропозиції
fn propose(protocol, proposal) {
    if !is_state(protocol, STATE_INIT) {
        return error("Invalid state for proposal")
    }
    
    let message = create_message("proposal", protocol.name, "", proposal)
    return transition(protocol, "propose", {message: message})
}

// Підтвердження
fn commit(protocol, proposal_id) {
    if !is_state(protocol, STATE_PROPOSE) {
        return error("Invalid state for commit")
    }
    
    return transition(protocol, "commit", {proposal_id: proposal_id})
}

// Виконання
fn execute(protocol, task) {
    if !is_state(protocol, STATE_COMMIT) {
        return error("Invalid state for execute")
    }
    
    return transition(protocol, "execute", {task: task})
}

// Верифікація
fn verify(protocol, result) {
    if !is_state(protocol, STATE_EXECUTE) {
        return error("Invalid state for verify")
    }
    
    if result.success {
        return transition(protocol, "verify", {result: result})
    } else {
        return transition(protocol, "escalate", {result: result})
    }
}

// Завершення
fn done(protocol, result) {
    if !is_state(protocol, STATE_VERIFY) {
        return error("Invalid state for done")
    }
    
    return transition(protocol, "done", {result: result})
}

// Відхилення
fn reject(protocol, reason) {
    return transition(protocol, "failed", {reason: reason})
}