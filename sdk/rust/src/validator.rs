// Vireo v3.0.0 — Validator (Rust SDK)
// Message validation and sandbox level 1 implementation

use crate::wire_format::{Message, Intent};
use crate::crypto::{verify, validate_public_key, validate_signature};
use std::collections::HashSet;
use std::time::{SystemTime, UNIX_EPOCH};
use crate::{TIMESTAMP_WINDOW_MS, NONCE_SIZE, SIGNATURE_SIZE, HASH_SIZE};

/// Validation result
#[derive(Debug, Clone, PartialEq)]
pub enum ValidationResult {
    /// Validation passed
    Valid,
    /// Validation failed with reason
    Invalid(String),
}

/// Validator for Vireo messages (Sandbox Level 1)
#[derive(Debug)]
pub struct Validator {
    /// Maximum number of nonces to cache
    max_nonce_cache: usize,
    /// Nonce cache for replay protection
    nonce_cache: HashSet<String>,
    /// Timestamp window in milliseconds
    timestamp_window_ms: u64,
}

impl Validator {
    /// Create a new validator with default settings
    pub fn new() -> Self {
        Self {
            max_nonce_cache: 10000,
            nonce_cache: HashSet::new(),
            timestamp_window_ms: TIMESTAMP_WINDOW_MS,
        }
    }
    
    /// Create a new validator with custom settings
    pub fn with_settings(
        max_nonce_cache: usize,
        timestamp_window_ms: u64,
    ) -> Self {
        Self {
            max_nonce_cache,
            nonce_cache: HashSet::new(),
            timestamp_window_ms,
        }
    }
    
    /// Validate a message
    pub fn validate(
        &mut self,
        message: &Message,
        public_key: &[u8; 32],
    ) -> ValidationResult {
        // 1. Validate public key format
        if !validate_public_key(public_key) {
            return ValidationResult::Invalid("Invalid public key".to_string());
        }
        
        // 2. Validate signature
        if !verify(&message.canonical_hash(), &message.signature, public_key) {
            return ValidationResult::Invalid("Invalid signature".to_string());
        }
        
        // 3. Validate timestamp
        if !self.validate_timestamp(message) {
            return ValidationResult::Invalid("Invalid timestamp".to_string());
        }
        
        // 4. Validate nonce (replay protection)
        if !self.validate_nonce(message) {
            return ValidationResult::Invalid("Replayed nonce".to_string());
        }
        
        // 5. Validate DIDs
        if !Self::validate_did(&message.sender) {
            return ValidationResult::Invalid("Invalid sender DID".to_string());
        }
        if !Self::validate_did(&message.recipient) {
            return ValidationResult::Invalid("Invalid recipient DID".to_string());
        }
        
        // 6. Validate intent
        if !Self::validate_intent(message.intent) {
            return ValidationResult::Invalid("Invalid intent".to_string());
        }
        
        // 7. Validate payload hash (if payload is present)
        if let Some(payload) = &message.payload {
            if !self.validate_payload_hash(payload, &message.payload_hash) {
                return ValidationResult::Invalid("Payload hash mismatch".to_string());
            }
        }
        
        // 8. Validate nonce format
        if !self.validate_nonce_format(&message.nonce) {
            return ValidationResult::Invalid("Invalid nonce format".to_string());
        }
        
        // 9. Validate message size
        let serialized = message.serialize();
        if serialized.len() > crate::MAX_MESSAGE_SIZE {
            return ValidationResult::Invalid("Message too large".to_string());
        }
        
        ValidationResult::Valid
    }
    
    /// Validate timestamp
    fn validate_timestamp(&self, message: &Message) -> bool {
        if !message.is_timestamp_valid() {
            return false;
        }
        
        // Check that timestamp is within window
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_else(|_| std::time::Duration::from_secs(0))
            .as_millis() as u64;
        
        let diff = if now >= message.timestamp_ms {
            now - message.timestamp_ms
        } else {
            message.timestamp_ms - now
        };
        
        diff <= self.timestamp_window_ms
    }
    
    /// Validate nonce (replay protection)
    fn validate_nonce(&mut self, message: &Message) -> bool {
        let nonce_key = format!("{}:{}", message.sender, hex::encode(message.nonce));
        
        if self.nonce_cache.contains(&nonce_key) {
            return false;
        }
        
        // Add nonce to cache
        self.nonce_cache.insert(nonce_key);
        
        // Trim cache if needed
        if self.nonce_cache.len() > self.max_nonce_cache {
            self.trim_cache();
        }
        
        true
    }
    
    /// Trim nonce cache
    fn trim_cache(&mut self) {
        // Simple trim: remove half the cache
        let to_remove = self.nonce_cache.len() / 2;
        let mut iter = self.nonce_cache.iter();
        for _ in 0..to_remove {
            if let Some(key) = iter.next() {
                self.nonce_cache.remove(key);
            }
        }
    }
    
    /// Validate nonce format
    fn validate_nonce_format(&self, nonce: &[u8; NONCE_SIZE]) -> bool {
        // Check that nonce is not all zeros
        if nonce.iter().all(|&b| b == 0) {
            return false;
        }
        
        // Check that nonce is not all ones
        if nonce.iter().all(|&b| b == 0xFF) {
            return false;
        }
        
        true
    }
    
    /// Validate DID format
    pub fn validate_did(did: &str) -> bool {
        did.starts_with("did:vireo:agent:") && did.len() > "did:vireo:agent:".len()
    }
    
    /// Validate intent
    pub fn validate_intent(intent: Intent) -> bool {
        matches!(
            intent,
            Intent::Propose
                | Intent::Commit
                | Intent::Execute
                | Intent::Verify
                | Intent::Done
                | Intent::Escalate
                | Intent::Reject
                | Intent::Timeout
        )
    }
    
    /// Validate payload hash
    pub fn validate_payload_hash(&self, payload: &serde_json::Value, expected_hash: &[u8; HASH_SIZE]) -> bool {
        use blake2::Blake2b512;
        use digest::Digest;
        
        let payload_json = match serde_json::to_string(payload) {
            Ok(s) => s,
            Err(_) => return false,
        };
        
        let hash = Blake2b512::digest(payload_json.as_bytes());
        let mut computed_hash = [0u8; HASH_SIZE];
        computed_hash.copy_from_slice(&hash[..HASH_SIZE]);
        
        computed_hash == *expected_hash
    }
    
    /// Validate message structure
    pub fn validate_structure(message: &Message) -> ValidationResult {
        // Check version
        if message.version != crate::PROTOCOL_VERSION {
            return ValidationResult::Invalid("Unsupported version".to_string());
        }
        
        // Check sender length
        if message.sender.len() > 255 {
            return ValidationResult::Invalid("Sender too long".to_string());
        }
        
        // Check recipient length
        if message.recipient.len() > 255 {
            return ValidationResult::Invalid("Recipient too long".to_string());
        }
        
        // Check proposal ID length
        if message.proposal_id.len() > 255 {
            return ValidationResult::Invalid("Proposal ID too long".to_string());
        }
        
        // Check that sender and recipient are not the same
        if message.sender == message.recipient {
            return ValidationResult::Invalid("Sender and recipient cannot be the same".to_string());
        }
        
        ValidationResult::Valid
    }
    
    /// Validate a public key
    pub fn validate_public_key(key: &[u8; 32]) -> bool {
        validate_public_key(key)
    }
    
    /// Validate a signature
    pub fn validate_signature(sig: &[u8; SIGNATURE_SIZE]) -> bool {
        validate_signature(sig)
    }
}

impl Default for Validator {
    fn default() -> Self {
        Self::new()
    }
}

/// Batch validator for multiple messages
#[derive(Debug)]
pub struct BatchValidator {
    validator: Validator,
    results: Vec<ValidationResult>,
}

impl BatchValidator {
    /// Create a new batch validator
    pub fn new() -> Self {
        Self {
            validator: Validator::new(),
            results: Vec::new(),
        }
    }
    
    /// Validate multiple messages
    pub fn validate_batch(
        &mut self,
        messages: &[(Message, [u8; 32])],
    ) -> &[ValidationResult] {
        self.results.clear();
        
        for (message, public_key) in messages {
            let result = self.validator.validate(message, public_key);
            self.results.push(result);
        }
        
        &self.results
    }
    
    /// Clear results
    pub fn clear(&mut self) {
        self.results.clear();
    }
    
    /// Get all results
    pub fn get_results(&self) -> &[ValidationResult] {
        &self.results
    }
    
    /// Check if all messages are valid
    pub fn all_valid(&self) -> bool {
        self.results.iter().all(|r| matches!(r, ValidationResult::Valid))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::crypto::generate_keypair;
    use crate::wire_format::{Message, Intent, Flags};
    use serde_json::json;
    
    #[test]
    fn test_validator_new() {
        let validator = Validator::new();
        assert_eq!(validator.max_nonce_cache, 10000);
        assert_eq!(validator.timestamp_window_ms, TIMESTAMP_WINDOW_MS);
        assert!(validator.nonce_cache.is_empty());
    }
    
    #[test]
    fn test_validate_valid_message() -> Result<(), String> {
        let (priv_key, pub_key) = generate_keypair();
        
        let mut msg = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"hello": "world"}),
        );
        
        // Generate nonce and sign
        msg.nonce = crate::crypto::generate_nonce();
        msg.sign(&priv_key);
        
        let mut validator = Validator::new();
        let result = validator.validate(&msg, &pub_key);
        
        assert!(matches!(result, ValidationResult::Valid));
        Ok(())
    }
    
    #[test]
    fn test_validate_invalid_signature() -> Result<(), String> {
        let (priv_key, pub_key) = generate_keypair();
        let (_, wrong_pub_key) = generate_keypair();
        
        let mut msg = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"hello": "world"}),
        );
        msg.nonce = crate::crypto::generate_nonce();
        msg.sign(&priv_key);
        
        let mut validator = Validator::new();
        let result = validator.validate(&msg, &wrong_pub_key);
        
        assert!(matches!(result, ValidationResult::Invalid(_)));
        Ok(())
    }
    
    #[test]
    fn test_validate_replay_attack() -> Result<(), String> {
        let (priv_key, pub_key) = generate_keypair();
        
        let mut msg = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"hello": "world"}),
        );
        msg.nonce = crate::crypto::generate_nonce();
        msg.sign(&priv_key);
        
        let mut validator = Validator::new();
        
        // First validation should pass
        let result1 = validator.validate(&msg, &pub_key);
        assert!(matches!(result1, ValidationResult::Valid));
        
        // Second validation should fail (replay)
        let result2 = validator.validate(&msg, &pub_key);
        assert!(matches!(result2, ValidationResult::Invalid(ref s) if s.contains("Replayed")));
        
        Ok(())
    }
    
    #[test]
    fn test_validate_invalid_did() -> Result<(), String> {
        let (priv_key, pub_key) = generate_keypair();
        
        let mut msg = Message::new(
            "invalid-did".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"hello": "world"}),
        );
        msg.nonce = crate::crypto::generate_nonce();
        msg.sign(&priv_key);
        
        let mut validator = Validator::new();
        let result = validator.validate(&msg, &pub_key);
        
        assert!(matches!(result, ValidationResult::Invalid(ref s) if s.contains("DID")));
        Ok(())
    }
    
    #[test]
    fn test_validate_payload_hash() -> Result<(), String> {
        let validator = Validator::new();
        let payload = json!({"hello": "world"});
        
        // Valid hash
        assert!(validator.validate_payload_hash(&payload, &Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            payload.clone(),
        ).payload_hash));
        
        // Invalid hash
        let mut msg = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            payload.clone(),
        );
        msg.payload_hash = [1u8; HASH_SIZE];
        assert!(!validator.validate_payload_hash(&payload, &msg.payload_hash));
        
        Ok(())
    }
    
    #[test]
    fn test_batch_validator() {
        let (priv_key1, pub_key1) = generate_keypair();
        let (priv_key2, pub_key2) = generate_keypair();
        
        let mut msg1 = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"hello": "world"}),
        );
        msg1.nonce = crate::crypto::generate_nonce();
        msg1.sign(&priv_key1);
        
        let mut msg2 = Message::new(
            "did:vireo:agent:charlie".to_string(),
            "did:vireo:agent:dave".to_string(),
            Intent::Commit,
            "prop_002".to_string(),
            json!({"status": "ok"}),
        );
        msg2.nonce = crate::crypto::generate_nonce();
        msg2.sign(&priv_key2);
        
        let mut batch = BatchValidator::new();
        let results = batch.validate_batch(&[
            (msg1.clone(), pub_key1),
            (msg2.clone(), pub_key2),
        ]);
        
        assert_eq!(results.len(), 2);
        assert!(matches!(results[0], ValidationResult::Valid));
        assert!(matches!(results[1], ValidationResult::Valid));
    }
}