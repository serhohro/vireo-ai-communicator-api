//! Vireo Envelope Validator v3.1

use crate::wire_format::{intent_to_id, Envelope};

/// Basic structural validation.
pub fn validate_envelope(env: &Envelope) -> Result<(), String> {
    // Intent must be known
    if intent_to_id(&env.intent).is_none() {
        return Err(format!("unknown intent: {}", env.intent));
    }

    // Timestamp must be positive
    if env.timestamp_ms == 0 {
        return Err("timestamp_ms must be > 0".to_string());
    }

    // Nonce must not be all zeros (weak check — caller should use random)
    if env.nonce == [0u8; 16] {
        return Err("nonce must not be all zeros".to_string());
    }

    // Payload must be an object
    if !env.payload.is_object() {
        return Err("payload must be a JSON object".to_string());
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn valid() -> Envelope {
        Envelope {
            intent: "PROPOSE".to_string(),
            timestamp_ms: 1773168000000,
            nonce: [1u8; 16],
            sender_did_hash: [1u8; 32],
            recipient_did_hash: [2u8; 32],
            payload: json!({"task": "test"}),
        }
    }

    #[test]
    fn test_valid() {
        assert!(validate_envelope(&valid()).is_ok());
    }

    #[test]
    fn test_unknown_intent() {
        let mut env = valid();
        env.intent = "INVALID".to_string();
        assert!(validate_envelope(&env).is_err());
    }

    #[test]
    fn test_zero_nonce() {
        let mut env = valid();
        env.nonce = [0u8; 16];
        assert!(validate_envelope(&env).is_err());
    }

    #[test]
    fn test_bad_payload() {
        let mut env = valid();
        env.payload = json!("string");
        assert!(validate_envelope(&env).is_err());
    }
}