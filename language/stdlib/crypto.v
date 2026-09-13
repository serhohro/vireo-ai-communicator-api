// ============================================================
// STANDARD LIBRARY: CRYPTOGRAPHY
// ============================================================
// Version: 1.4.3
// ============================================================

// ============================================================
// КЛЮЧІ
// ============================================================

// Генерація ключів
fn generate_keys() {
    let private_key = Ed25519.generate_private_key()
    let public_key = private_key.public_key()
    return {
        private: private_key,
        public: public_key
    }
}

// Завантаження ключів
fn load_keys(private_key, public_key) {
    return {
        private: private_key,
        public: public_key
    }
}

// Збереження ключів
fn save_keys(keys, path) {
    return save_to_file(keys, path)
}

// ============================================================
// ПІДПИС
// ============================================================

// Підпис повідомлення
fn sign(message, private_key) {
    return Ed25519.sign(message, private_key)
}

// Верифікація підпису
fn verify(message, signature, public_key) {
    return Ed25519.verify(message, signature, public_key)
}

// Перевірка підпису з помилкою
fn verify_or_error(message, signature, public_key) {
    let result = verify(message, signature, public_key)
    if result == false {
        return error("Signature verification failed")
    }
    return success("Signature verified")
}

// ============================================================
// ДІД (DECENTRALIZED IDENTIFIERS)
// ============================================================

// Створення DID
fn create_did(public_key) {
    let did = "did:key:" + base58_encode(public_key)
    return did
}

// Створення DID документа
fn create_did_document(did, public_key) {
    return {
        "@context": "https://www.w3.org/ns/did/v1",
        "id": did,
        "verificationMethod": [{
            "id": did + "#key-1",
            "type": "Ed25519VerificationKey2020",
            "controller": did,
            "publicKeyMultibase": public_key
        }],
        "authentication": [did + "#key-1"],
        "assertionMethod": [did + "#key-1"],
        "capabilityInvocation": [did + "#key-1"],
        "capabilityDelegation": [did + "#key-1"]
    }
}

// Верифікація DID
fn verify_did(did, document) {
    return document.id == did
}

// ============================================================
// ДОВІРА
// ============================================================

// Створення довіреного пейлоаду
fn create_trusted_payload(data, agent_id, private_key) {
    let nonce = generate_nonce()
    let timestamp = time.now()
    let payload = {
        data: data,
        nonce: nonce,
        timestamp: timestamp,
        agent_id: agent_id
    }
    let signature = sign(payload, private_key)
    return {
        payload: payload,
        signature: signature
    }
}

// Верифікація довіреного пейлоаду
fn verify_trusted_payload(trusted_payload, public_key) {
    let payload = trusted_payload.payload
    let signature = trusted_payload.signature
    
    // Перевірка підпису
    let valid = verify(payload, signature, public_key)
    if valid == false {
        return error("Invalid signature")
    }
    
    // Перевірка nonce
    let nonce_valid = validate_nonce(payload.nonce)
    if nonce_valid == false {
        return error("Invalid nonce")
    }
    
    // Перевірка часу
    let now = time.now()
    if now - payload.timestamp > 60 {
        return error("Payload expired")
    }
    
    return success(payload.data)
}

// ============================================================
// ШИФРУВАННЯ
// ============================================================

// Симетричне шифрування
fn encrypt(data, key) {
    return AES.encrypt(data, key)
}

// Симетричне дешифрування
fn decrypt(data, key) {
    return AES.decrypt(data, key)
}

// Хешування
fn hash(data) {
    return SHA256.hash(data)
}

// HMAC
fn hmac(data, key) {
    return HMAC.sha256(data, key)
}

// ============================================================
// ВЕРИФІКАЦІЯ
// ============================================================

// Верифікація контракту
fn verify_contract(contract, signature, public_key) {
    return verify(contract, signature, public_key)
}

// Верифікація агента
fn verify_agent(agent_id, signature, public_key) {
    return verify(agent_id, signature, public_key)
}

// Верифікація повідомлення
fn verify_message(message, signature, public_key) {
    return verify(message, signature, public_key)
}

// ============================================================
// УТИЛІТИ
// ============================================================

// Генерація nonce
fn generate_nonce() {
    return random_bytes(32)
}

// Валідація nonce
fn validate_nonce(nonce) {
    let cache = get_nonce_cache()
    if nonce in cache {
        return false
    }
    cache.add(nonce)
    return true
}

// Base58 кодування
fn base58_encode(data) {
    return Base58.encode(data)
}

// Base58 декодування
fn base58_decode(data) {
    return Base58.decode(data)
}

// Перевірка наявності ключів
fn has_keys(agent_id) {
    return get_public_key(agent_id) != None
}