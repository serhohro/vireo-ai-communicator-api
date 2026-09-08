// Vireo v3.0.0 — Rust SDK Library
// The World's First AI-to-AI Communication Language

#![deny(missing_docs)]
#![deny(unsafe_code)]
#![warn(clippy::all, clippy::pedantic)]

//! Vireo — The World's First AI-to-AI Communication Language
//!
//! This crate provides the Rust implementation of the Vireo protocol,
//! enabling secure AI-to-AI communication, negotiation, and coordination.
//!
//! # Example
//!
//! ```rust
//! use vireo::{Agent, Message, Intent};
//! use serde_json::json;
//!
//! # fn main() -> Result<(), Box<dyn std::error::Error>> {
//! let (private_key, public_key) = vireo::crypto::generate_keypair();
//! let agent = Agent::new("agent-001", private_key, public_key);
//!
//! let msg = agent.propose("agent-002", json!({"task": "Hello, World!"}));
//! let serialized = msg.serialize();
//!
//! let deserialized = Message::deserialize(&serialized)?;
//! assert_eq!(msg.sender, deserialized.sender);
//! # Ok(())
//! # }
//! ```

pub mod agent;
pub mod crypto;
pub mod validator;
pub mod wire_format;

// Re-export core types
pub use agent::Agent;
pub use crypto::{generate_keypair, sign, verify, KeyPair};
pub use validator::{Validator, ValidationResult};
pub use wire_format::{Flags, Intent, Message};

// Re-export dependencies for convenience
pub use serde;
pub use serde_json;

/// Current version of the Vireo protocol
pub const VERSION: &str = "3.0.0";

/// Protocol magic bytes
pub const MAGIC: &[u8; 4] = b"VIRE";

/// Protocol version byte
pub const PROTOCOL_VERSION: u8 = 0x30;

/// Nonce size in bytes
pub const NONCE_SIZE: usize = 16;

/// Signature size in bytes (Ed25519)
pub const SIGNATURE_SIZE: usize = 64;

/// Hash size in bytes (BLAKE2b)
pub const HASH_SIZE: usize = 32;

/// Maximum message size (1MB)
pub const MAX_MESSAGE_SIZE: usize = 1024 * 1024;

/// Timestamp window for replay protection (5 minutes in milliseconds)
pub const TIMESTAMP_WINDOW_MS: u64 = 300_000;

/// Pre-configured test vectors for conformance testing
pub mod test_vectors {
    /// Test vector for PROPOSE intent
    pub const PROPOSE_VECTOR: &[u8] = include_bytes!("../../specification/test_vectors/propose_v3_0.bin");
    
    /// Test vector for COMMIT intent
    pub const COMMIT_VECTOR: &[u8] = include_bytes!("../../specification/test_vectors/commit_v3_0.bin");
    
    /// Test vector for EXECUTE intent
    pub const EXECUTE_VECTOR: &[u8] = include_bytes!("../../specification/test_vectors/execute_v3_0.bin");
    
    /// Test vector for VERIFY intent
    pub const VERIFY_VECTOR: &[u8] = include_bytes!("../../specification/test_vectors/verify_v3_0.bin");
    
    /// Test vector for DONE intent
    pub const DONE_VECTOR: &[u8] = include_bytes!("../../specification/test_vectors/done_v3_0.bin");
    
    /// Test vector for ESCALATE intent
    pub const ESCALATE_VECTOR: &[u8] = include_bytes!("../../specification/test_vectors/escalate_v3_0.bin");
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_version() {
        assert_eq!(VERSION, "3.0.0");
        assert_eq!(PROTOCOL_VERSION, 0x30);
        assert_eq!(MAGIC, b"VIRE");
    }

    #[test]
    fn test_constants() {
        assert_eq!(NONCE_SIZE, 16);
        assert_eq!(SIGNATURE_SIZE, 64);
        assert_eq!(HASH_SIZE, 32);
        assert_eq!(MAX_MESSAGE_SIZE, 1024 * 1024);
        assert_eq!(TIMESTAMP_WINDOW_MS, 300_000);
    }

    #[test]
    fn test_basic_agent_flow() -> Result<(), Box<dyn std::error::Error>> {
        let (priv_key, pub_key) = crypto::generate_keypair();
        let agent = Agent::new("test-agent", priv_key, pub_key);
        
        let contract = json!({
            "name": "TestContract",
            "terms": {"max_tokens": 1000}
        });
        
        let msg = agent.propose("recipient-agent", contract);
        let serialized = msg.serialize();
        let deserialized = Message::deserialize(&serialized)?;
        
        assert_eq!(msg.sender, deserialized.sender);
        assert_eq!(msg.recipient, deserialized.recipient);
        assert_eq!(msg.intent, deserialized.intent);
        
        Ok(())
    }
}