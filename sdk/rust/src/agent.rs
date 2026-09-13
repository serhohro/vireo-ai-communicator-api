//! Vireo Agent v3.1
//!
//! Base agent with DID + Ed25519 keypair.

use crate::crypto::{did_hash, generate_keypair, sign_vireo_message, Keypair, verify_vireo_message};
use crate::wire_format::{canonical_wire_bytes, Envelope};
use base64::Engine;
use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use serde_json::Value;

/// Vireo Agent.
pub struct Agent {
    pub id: String,
    pub name: String,
    pub did: String,
    pub keypair: Keypair,
}

impl Agent {
    /// Create a new agent with a fresh Ed25519 keypair.
    pub fn new(id: &str, name: &str) -> Self {
        let keypair = generate_keypair();
        let did = make_did(name);
        Self {
            id: id.to_string(),
            name: name.to_string(),
            did,
            keypair,
        }
    }

    /// Build an envelope.
    pub fn build_envelope(
        &self,
        intent: &str,
        recipient_did: &str,
        timestamp_ms: u64,
        nonce: [u8; 16],
        payload: Value,
    ) -> Envelope {
        Envelope {
            intent: intent.to_string(),
            timestamp_ms,
            nonce,
            sender_did_hash: did_hash(&self.did),
            recipient_did_hash: did_hash(recipient_did),
            payload,
        }
    }

    /// Sign an envelope's canonical bytes.
    pub fn sign(&self, env: &Envelope) -> Result<String, String> {
        let canonical = canonical_wire_bytes(env).map_err(|e| e.to_string())?;
        sign_vireo_message(&self.keypair.private_key_hex, &canonical)
            .map_err(|e| e.to_string())
    }

    /// Verify a signed envelope from another agent.
    pub fn verify(
        &self,
        sender_public_key_hex: &str,
        env: &Envelope,
        signature_hex: &str,
    ) -> Result<(), String> {
        let canonical = canonical_wire_bytes(env).map_err(|e| e.to_string())?;
        verify_vireo_message(sender_public_key_hex, &canonical, signature_hex)
            .map_err(|e| e.to_string())
    }
}

/// Derive a Vireo DID from an agent name.
pub fn make_did(name: &str) -> String {
    let h = did_hash(name);
    let encoded = URL_SAFE_NO_PAD.encode(h);
    format!("did:vireo:{}", encoded)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_make_did() {
        let did = make_did("agent:alice");
        assert!(did.starts_with("did:vireo:"));
    }

    #[test]
    fn test_agent_sign_verify() {
        let alice = Agent::new("alice", "agent:alice");
        let bob = Agent::new("bob", "agent:bob");

        let env = alice.build_envelope(
            "PROPOSE",
            &bob.did,
            1773168000000,
            [1u8; 16],
            json!({"task": "test"}),
        );

        let sig = alice.sign(&env).unwrap();
        let result = bob.verify(&alice.keypair.public_key_hex, &env, &sig);
        assert!(result.is_ok());
    }

    #[test]
    fn test_agent_wrong_signer() {
        let alice = Agent::new("alice", "agent:alice");
        let bob = Agent::new("bob", "agent:bob");
        let eve = Agent::new("eve", "agent:eve");

        let env = alice.build_envelope(
            "PROPOSE",
            &bob.did,
            1773168000000,
            [1u8; 16],
            json!({"task": "test"}),
        );

        let sig = eve.sign(&env).unwrap();
        assert!(bob.verify(&alice.keypair.public_key_hex, &env, &sig).is_err());
    }
}