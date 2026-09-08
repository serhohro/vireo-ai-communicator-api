// ============================================================
// STANDARD LIBRARY: SECURITY
// ============================================================
// Version: 3.0.0
// ============================================================

// ============================================================
// АУТЕНТИФІКАЦІЯ
// ============================================================

// Перевірка паролю
fn check_password(password, hash) {
    return Password.verify(password, hash)
}

// Хешування паролю
fn hash_password(password) {
    return Password.hash(password)
}

// Створення токену
fn create_token(data, secret) {
    let payload = {
        data: data,
        exp: time.now() + 3600
    }
    return JWT.sign(payload, secret)
}

// Верифікація токену
fn verify_token(token, secret) {
    let payload = JWT.verify(token, secret)
    if payload == None {
        return error("Invalid token")
    }
    if payload.exp < time.now() {
        return error("Token expired")
    }
    return success(payload.data)
}

// ============================================================
// ДОЗВОЛИ
// ============================================================

// Перевірка дозволу
fn has_permission(agent, action, resource) {
    let permissions = get_permissions(agent)
    return permissions.contains(action + ":" + resource)
}

// Додавання дозволу
fn add_permission(agent, action, resource) {
    let permissions = get_permissions(agent)
    permissions.append(action + ":" + resource)
    return set_permissions(agent, permissions)
}

// Видалення дозволу
fn remove_permission(agent, action, resource) {
    let permissions = get_permissions(agent)
    let target = action + ":" + resource
    permissions.remove(target)
    return set_permissions(agent, permissions)
}

// ============================================================
// РОЛІ
// ============================================================

// Додавання ролі
fn add_role(agent, role) {
    let roles = get_roles(agent)
    roles.append(role)
    return set_roles(agent, roles)
}

// Видалення ролі
fn remove_role(agent, role) {
    let roles = get_roles(agent)
    roles.remove(role)
    return set_roles(agent, roles)
}

// Перевірка ролі
fn has_role(agent, role) {
    let roles = get_roles(agent)
    return roles.contains(role)
}

// ============================================================
// ШИФРУВАННЯ
// ============================================================

// AES шифрування
fn aes_encrypt(data, key) {
    return AES.encrypt(data, key)
}

// AES дешифрування
fn aes_decrypt(data, key) {
    return AES.decrypt(data, key)
}

// RSA шифрування
fn rsa_encrypt(data, public_key) {
    return RSA.encrypt(data, public_key)
}

// RSA дешифрування
fn rsa_decrypt(data, private_key) {
    return RSA.decrypt(data, private_key)
}

// ============================================================
// ХЕШУВАННЯ
// ============================================================

// SHA256
fn sha256(data) {
    return SHA256.hash(data)
}

// SHA512
fn sha512(data) {
    return SHA512.hash(data)
}

// BLAKE2b
fn blake2b(data) {
    return BLAKE2b.hash(data)
}

// ============================================================
// АУДИТ
// ============================================================

// Логування дії
fn audit_log(action, agent, resource, result) {
    return Audit.log({
        action: action,
        agent: agent,
        resource: resource,
        result: result,
        timestamp: time.now()
    })
}

// Отримання логів
fn get_audit_logs(agent=None, action=None) {
    let logs = Audit.get_logs()
    if agent != None {
        logs = filter(logs, { it.agent == agent })
    }
    if action != None {
        logs = filter(logs, { it.action == action })
    }
    return logs
}