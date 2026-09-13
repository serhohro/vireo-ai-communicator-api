//! Cryptography for Vireo v3.1
//!
//! - Ed25519 signatures (RFC 8032)
//! - BLAKE2b-256 hashing (RFC 7693)

use blake2::{Blake2b, Digest, digest::consts::U32};
use ed25519_dalek::{SigningKey, VerifyingKey, Signature, Signer, Verifier};
use rand::rngs::OsRng;

type Blake2b256 = Blake2b<U32>;

/// BLAKE2b-256 hash of arbitrary bytes.
pub fn blake2b_256(data: &[u8]) -> [u8; 32] {
    let mut hasher = Blake2b256::new();
    hasher.update(data);
    let result = hasher.finalize();
    let mut out = [0u8; 32];
    out.copy_from_slice(&result);
    out
}

/// Hash of the opaque payload inside the envelope.
pub fn payload_hash(payload_bytes: &[u8]) -> [u8; 32] {
    blake2b_256(payload_bytes)
}

/// Hash of the canonical wire bytes. This is what Ed25519 signs.
pub fn wire_hash(canonical_bytes: &[u8]) -> [u8; 32] {
    blake2b_256(canonical_bytes)
}

/// Hash of a DID string for the wire header.
pub fn did_hash(did_string: &str) -> [u8; 32] {
    blake2b_256(did_string.as_bytes())
}

/// Ed25519 keypair.
pub struct Keypair {
    pub private_key_hex: String,
    pub public_key_hex: String,
}

/// Generate a fresh Ed25519 keypair.
pub fn generate_keypair() -> Keypair {
    let signing_key = SigningKey::generate(&mut OsRng);
    let verifying_key = signing_key.verifying_key();
    Keypair {
        private_key_hex: hex::encode(signing_key.to_bytes()),
        public_key_hex: hex::encode(verifying_key.to_bytes()),
    }
}

/// Sign canonical wire bytes with Ed25519.
pub fn sign_vireo_message(
    private_key_hex: &str,
    canonical_bytes: &[u8],
) -> Result<String, CryptoError> {
    let private_bytes = hex::decode(private_key_hex)
        .map_err(|_| CryptoError::InvalidPrivateKey)?;
    if private_bytes.len() != 32 {
        return Err(CryptoError::InvalidPrivateKey);
    }
    let mut arr = [0u8; 32];
    arr.copy_from_slice(&private_bytes);
    let signing_key = SigningKey::from_bytes(&arr);

    let h = wire_hash(canonical_bytes);
    let signature = signing_key.sign(&h);
    Ok(hex::encode(signature.to_bytes()))
}

/// Verify an Ed25519 signature over canonical wire bytes.
pub fn verify_vireo_message(
    public_key_hex: &str,
    canonical_bytes: &[u8],
    signature_hex: &str,
) -> Result<(), CryptoError> {
    let public_bytes = hex::decode(public_key_hex)
        .map_err(|_| CryptoError::InvalidPublicKey)?;
    if public_bytes.len() != 32 {
        return Err(CryptoError::InvalidPublicKey);
    }
    let mut arr = [0u8; 32];
    arr.copy_from_slice(&public_bytes);
    let verifying_key = VerifyingKey::from_bytes(&arr)
        .map_err(|_| CryptoError::InvalidPublicKey)?;

    let sig_bytes = hex::decode(signature_hex)
        .map_err(|_| CryptoError::InvalidSignature)?;
    if sig_bytes.len() != 64 {
        return Err(CryptoError::InvalidSignature);
    }
    let mut sig_arr = [0u8; 64];
    sig_arr.copy_from_slice(&sig_bytes);
    let signature = Signature::from_bytes(&sig_arr);

    let h = wire_hash(canonical_bytes);
    verifying_key.verify(&h, &signature)
        .map_err(|_| CryptoError::SignatureMismatch)
}

#[derive(Debug, thiserror::Error)]
pub enum CryptoError {
    #[error("Invalid private key")]
    InvalidPrivateKey,
    #[error("Invalid public key")]
    InvalidPublicKey,
    #[error("Invalid signature")]
    InvalidSignature,
    #[error("Signature does not match")]
    SignatureMismatch,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_blake2b_deterministic() {
        assert_eq!(blake2b_256(b"hello"), blake2b_256(b"hello"));
    }

    #[test]
    fn test_blake2b_different() {
        assert_ne!(blake2b_256(b"a"), blake2b_256(b"b"));
    }

    #[test]
    fn test_sign_and_verify() {
        let kp = generate_keypair();
        let msg = b"test message";
        let sig = sign_vireo_message(&kp.private_key_hex, msg).unwrap();
        assert!(verify_vireo_message(&kp.public_key_hex, msg, &sig).is_ok());
    }

    #[test]
    fn test_verify_wrong_key() {
        let kp1 = generate_keypair();
        let kp2 = generate_keypair();
        let msg = b"test";
        let sig = sign_vireo_message(&kp1.private_key_hex, msg).unwrap();
        assert!(verify_vireo_message(&kp2.public_key_hex, msg, &sig).is_err());
    }

    #[test]
    fn test_did_hash() {
        let h = did_hash("did:vireo:alice");
        assert_eq!(h.len(), 32);
    }
}