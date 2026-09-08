// Vireo v3.0.0 — Crypto (Rust SDK)
// Ed25519 signatures and cryptographic utilities

use ed25519_dalek::{SigningKey, VerifyingKey, Signature, Signer, Verifier};
use rand::rngs::OsRng;
use blake2::{Blake2b512, Digest};
use crate::{HASH_SIZE, SIGNATURE_SIZE};

/// Key pair containing private and public keys
#[derive(Debug, Clone, Copy)]
pub struct KeyPair {
    /// Private key (32 bytes)
    pub private_key: [u8; 32],
    /// Public key (32 bytes)
    pub public_key: [u8; 32],
}

impl KeyPair {
    /// Generate a new key pair
    pub fn generate() -> Self {
        let signing_key = SigningKey::generate(&mut OsRng);
        let verifying_key = signing_key.verifying_key();
        
        Self {
            private_key: signing_key.to_bytes(),
            public_key: verifying_key.to_bytes(),
        }
    }
    
    /// Sign a message with the private key
    pub fn sign(&self, message: &[u8]) -> [u8; SIGNATURE_SIZE] {
        let signing_key = SigningKey::from_bytes(&self.private_key);
        let signature: Signature = signing_key.sign(message);
        signature.to_bytes()
    }
    
    /// Verify a signature with the public key
    pub fn verify(&self, message: &[u8], signature: &[u8; SIGNATURE_SIZE]) -> bool {
        let verifying_key = match VerifyingKey::from_bytes(&self.public_key) {
            Ok(key) => key,
            Err(_) => return false,
        };
        let sig = match Signature::from_bytes(signature) {
            Ok(s) => s,
            Err(_) => return false,
        };
        verifying_key.verify(message, &sig).is_ok()
    }
}

/// Generate a new Ed25519 key pair
pub fn generate_keypair() -> ([u8; 32], [u8; 32]) {
    let keypair = KeyPair::generate();
    (keypair.private_key, keypair.public_key)
}

/// Sign a message with Ed25519
pub fn sign(message: &[u8], private_key: &[u8; 32]) -> [u8; SIGNATURE_SIZE] {
    let signing_key = SigningKey::from_bytes(private_key);
    let signature: Signature = signing_key.sign(message);
    signature.to_bytes()
}

/// Verify an Ed25519 signature
pub fn verify(message: &[u8], signature: &[u8; SIGNATURE_SIZE], public_key: &[u8; 32]) -> bool {
    let verifying_key = match VerifyingKey::from_bytes(public_key) {
        Ok(key) => key,
        Err(_) => return false,
    };
    let sig = match Signature::from_bytes(signature) {
        Ok(s) => s,
        Err(_) => return false,
    };
    verifying_key.verify(message, &sig).is_ok()
}

/// Compute BLAKE2b hash (32 bytes)
pub fn blake2b_hash(data: &[u8]) -> [u8; HASH_SIZE] {
    let mut hasher = Blake2b512::new();
    hasher.update(data);
    let result = hasher.finalize();
    let mut hash = [0u8; HASH_SIZE];
    hash.copy_from_slice(&result[..HASH_SIZE]);
    hash
}

/// Compute BLAKE2b hash with key
pub fn blake2b_hash_with_key(data: &[u8], key: &[u8]) -> [u8; HASH_SIZE] {
    use blake2::Blake2b;
    
    let mut hasher = Blake2b::<blake2::digest::typenum::U32>::new_with_key(key)
        .expect("Failed to create BLAKE2b with key");
    hasher.update(data);
    let result = hasher.finalize();
    let mut hash = [0u8; HASH_SIZE];
    hash.copy_from_slice(&result[..HASH_SIZE]);
    hash
}

/// Constant-time comparison of two byte arrays
pub fn secure_compare(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    
    let mut result = 0u8;
    for (x, y) in a.iter().zip(b.iter()) {
        result |= x ^ y;
    }
    result == 0
}

/// Generate a random nonce (16 bytes)
pub fn generate_nonce() -> [u8; 16] {
    use rand::Rng;
    let mut nonce = [0u8; 16];
    rand::thread_rng().fill(&mut nonce);
    nonce
}

/// Convert a hex string to bytes
pub fn hex_to_bytes(hex: &str) -> Result<Vec<u8>, String> {
    if hex.len() % 2 != 0 {
        return Err("Invalid hex string: odd length".to_string());
    }
    
    (0..hex.len())
        .step_by(2)
        .map(|i| {
            u8::from_str_radix(&hex[i..i + 2], 16)
                .map_err(|e| format!("Invalid hex: {}", e))
        })
        .collect()
}

/// Convert bytes to hex string
pub fn bytes_to_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

/// Validate a public key (32 bytes)
pub fn validate_public_key(key: &[u8; 32]) -> bool {
    // Check that the key is not all zeros
    if key.iter().all(|&b| b == 0) {
        return false;
    }
    
    // Try to create a verifying key
    VerifyingKey::from_bytes(key).is_ok()
}

/// Validate a private key (32 bytes)
pub fn validate_private_key(key: &[u8; 32]) -> bool {
    // Check that the key is not all zeros
    if key.iter().all(|&b| b == 0) {
        return false;
    }
    
    // Try to create a signing key
    let signing_key = SigningKey::from_bytes(key);
    let verifying_key = signing_key.verifying_key();
    
    // Check that the public key derived from private is valid
    validating_verifying_key(&verifying_key.to_bytes())
}

/// Validate a signature (64 bytes)
pub fn validate_signature(signature: &[u8; SIGNATURE_SIZE]) -> bool {
    // Check that the signature is not all zeros
    if signature.iter().all(|&b| b == 0) {
        return false;
    }
    
    Signature::from_bytes(signature).is_ok()
}

/// Validate a verifying key
fn validating_verifying_key(key: &[u8; 32]) -> bool {
    VerifyingKey::from_bytes(key).is_ok()
}

/// Derive public key from private key
pub fn public_key_from_private(private_key: &[u8; 32]) -> [u8; 32] {
    let signing_key = SigningKey::from_bytes(private_key);
    signing_key.verifying_key().to_bytes()
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_keypair_generation() {
        let keypair = KeyPair::generate();
        assert!(validate_private_key(&keypair.private_key));
        assert!(validate_public_key(&keypair.public_key));
    }
    
    #[test]
    fn test_sign_verify() {
        let keypair = KeyPair::generate();
        let message = b"Hello, Vireo!";
        
        let signature = keypair.sign(message);
        assert!(validate_signature(&signature));
        assert!(keypair.verify(message, &signature));
        
        // Wrong message
        assert!(!keypair.verify(b"Wrong message", &signature));
        
        // Wrong signature
        let mut bad_signature = signature;
        bad_signature[0] = (bad_signature[0] + 1) % 255;
        assert!(!keypair.verify(message, &bad_signature));
    }
    
    #[test]
    fn test_blake2b_hash() {
        let data = b"Hello, Vireo!";
        let hash1 = blake2b_hash(data);
        let hash2 = blake2b_hash(data);
        
        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), HASH_SIZE);
        
        let hash3 = blake2b_hash(b"Different");
        assert_ne!(hash1, hash3);
    }
    
    #[test]
    fn test_blake2b_with_key() {
        let data = b"Hello, Vireo!";
        let key = b"secret_key_123";
        
        let hash1 = blake2b_hash_with_key(data, key);
        let hash2 = blake2b_hash_with_key(data, key);
        
        assert_eq!(hash1, hash2);
        
        let hash3 = blake2b_hash_with_key(data, b"different_key");
        assert_ne!(hash1, hash3);
    }
    
    #[test]
    fn test_secure_compare() {
        let a = b"secret_key";
        let b = b"secret_key";
        let c = b"different_key";
        
        assert!(secure_compare(a, b));
        assert!(!secure_compare(a, c));
        
        // Different lengths
        assert!(!secure_compare(a, &b[..5]));
    }
    
    #[test]
    fn test_hex_conversion() {
        let original = b"Hello, Vireo!";
        let hex = bytes_to_hex(original);
        let restored = hex_to_bytes(&hex).unwrap();
        
        assert_eq!(original.to_vec(), restored);
    }
    
    #[test]
    fn test_public_key_from_private() {
        let keypair = KeyPair::generate();
        let derived = public_key_from_private(&keypair.private_key);
        assert_eq!(derived, keypair.public_key);
    }
}