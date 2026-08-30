// ============================================================
// STANDARD LIBRARY: NETWORK OPERATIONS
// ============================================================
// Version: 1.4.3
// ============================================================

// ============================================================
// HTTP
// ============================================================

// GET запит
fn http_get(url) {
    return HTTP.get(url)
}

// POST запит
fn http_post(url, data) {
    return HTTP.post(url, data)
}

// PUT запит
fn http_put(url, data) {
    return HTTP.put(url, data)
}

// DELETE запит
fn http_delete(url) {
    return HTTP.delete(url)
}

// HTTP заголовки
fn http_headers(headers) {
    return set_headers(headers)
}

// ============================================================
// ТРАНСПОРТ
// ============================================================

// Відправка через InMemory
fn send_inmemory(channel, message) {
    return InMemory.send(channel, message)
}

// Відправка через Redis
fn send_redis(channel, message) {
    return Redis.send(channel, message)
}

// Відправка через Kafka
fn send_kafka(topic, message) {
    return Kafka.send(topic, message)
}

// Відправка через NATS
fn send_nats(subject, message) {
    return NATS.send(subject, message)
}

// Підписка на канал
fn subscribe(channel, handler) {
    return Transport.subscribe(channel, handler)
}

// ============================================================
// АГЕНТСЬКИЙ ТРАНСПОРТ
// ============================================================

// Відправка пропозиції
fn send_proposal(agent_id, proposal) {
    let channel = "agent." + agent_id + ".proposals"
    return send(channel, proposal)
}

// Відправка коміту
fn send_commit(agent_id, commit) {
    let channel = "agent." + agent_id + ".commits"
    return send(channel, commit)
}

// Відправка відхилення
fn send_reject(agent_id, reject) {
    let channel = "agent." + agent_id + ".rejects"
    return send(channel, reject)
}

// Відправка інформації
fn send_inform(agent_id, inform) {
    let channel = "agent." + agent_id + ".informs"
    return send(channel, inform)
}

// Отримання повідомлень
fn receive_messages(agent_id) {
    let channel = "agent." + agent_id + ".inbox"
    return receive(channel)
}

// ============================================================
// API
// ============================================================

// REST API виклик
fn api_call(method, url, data, headers) {
    return HTTP.request(method, url, data, headers)
}

// GraphQL запит
fn graphql_query(url, query, variables) {
    return GraphQL.query(url, query, variables)
}

// WebSocket з'єднання
fn websocket_connect(url) {
    return WebSocket.connect(url)
}

// ============================================================
// КОНФІГУРАЦІЯ
// ============================================================

// Встановлення таймауту
fn set_timeout(seconds) {
    return Transport.set_timeout(seconds)
}

// Встановлення ретраїв
fn set_retries(count) {
    return Transport.set_retries(count)
}

// Встановлення проксі
fn set_proxy(url) {
    return Transport.set_proxy(url)
}

// ============================================================
// МОНІТОРИНГ
// ============================================================

// Статистика мережі
fn network_stats() {
    return {
        messages_sent: get_messages_sent(),
        messages_received: get_messages_received(),
        errors: get_errors(),
        avg_latency: get_avg_latency()
    }
}

// Статус з'єднання
fn connection_status() {
    return get_connection_status()
}

// ============================================================
// УТИЛІТИ
// ============================================================

// Перевірка з'єднання
fn ping(host, port) {
    return Network.ping(host, port)
}

// DNS запит
fn dns_lookup(host) {
    return Network.dns_lookup(host)
}

// IP адреса
fn get_ip() {
    return Network.get_ip()
}