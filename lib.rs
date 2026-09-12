//! Vireo v3.1 — Rust SDK
//!
//! The world's first AI-to-AI communication language
//! with built-in Ed25519, DIDs, and contract lifecycle.

pub mod crypto;
pub mod wire_format;
pub mod validator;
pub mod agent;

pub use crypto::{
    blake2b_256, did_hash, generate_keypair, payload_hash,
    sign_vireo_message, verify_vireo_message, wire_hash,
    CryptoError, Keypair,
};

pub use wire_format::{
    canonical_wire_bytes, parse_wire_bytes, Envelope, WireError,
    HEADER_SIZE, INTENT, WIRE_MAGIC, WIRE_VERSION,
};

pub use validator::validate_envelope;

pub use agent::Agent;

pub const PROTOCOL_VERSION: &str = "3.1";
pub const WIRE_VERSION_HEX: &str = "0x0301";

pub fn version() -> &'static str {
    PROTOCOL_VERSION
}