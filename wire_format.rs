//! Vireo Wire Format v3.1
//!
//! 96-byte Big-Endian header + RFC 8785 JCS payload.
//!
//! Layout:
//! ```text
//! +----------------------------------------------+
//! | Header (96 bytes)                            |
//! |  Magic           4B   "VIRE"                 |
//! |  Version         2B   0x0301 (v3.1)          |
//! |  Intent          2B   uint16 enum            |
//! |  Timestamp       8B   uint64 ms              |
//! |  Nonce          16B   random                 |
//! |  Sender hash    32B   BLAKE2b-256            |
//! |  Recipient hash 32B   BLAKE2b-256            |
//! +----------------------------------------------+
//! | Payload Length   4B   uint32                 |
//! | Payload          var  RFC 8785 JCS JSON      |
//! +----------------------------------------------+
//! ```

use serde_json::Value;
use std::collections::BTreeMap;

pub const WIRE_MAGIC: [u8; 4] = *b"VIRE";
pub const WIRE_VERSION: u16 = 0x0301;
pub const HEADER_SIZE: usize = 96;

pub const INTENT: &[(&str, u16)] = &[
    ("DISCOVER",  1),
    ("PROPOSE",   2),
    ("NEGOTIATE", 3),
    ("COMMIT",    4),
    ("REJECT",    5),
    ("EXECUTE",   6),
    ("VERIFY",    7),
    ("DONE",      8),
    ("ESCALATED", 9),
    ("CANCELLED", 10),
    ("FAILED",    11),
    ("TIMEOUT",   12),
];

pub fn intent_to_id(intent: &str) -> Option<u16> {
    INTENT.iter().find(|(n, _)| *n == intent).map(|(_, i)| *i)
}

pub fn id_to_intent(id: u16) -> Option<&'static str> {
    INTENT.iter().find(|(_, i)| *i == id).map(|(n, _)| *n)
}

/// Vireo envelope for wire encoding.
#[derive(Debug, Clone)]
pub struct Envelope {
    pub intent: String,
    pub timestamp_ms: u64,
    pub nonce: [u8; 16],
    pub sender_did_hash: [u8; 32],
    pub recipient_did_hash: [u8; 32],
    pub payload: Value,
}

/// Build the canonical Vireo wire bytes.
pub fn canonical_wire_bytes(env: &Envelope) -> Result<Vec<u8>, WireError> {
    let intent_id = intent_to_id(&env.intent)
        .ok_or_else(|| WireError::UnknownIntent(env.intent.clone()))?;

    let mut out = Vec::with_capacity(HEADER_SIZE + 64);

    // ── Header (96 bytes) ─────────────────────────────
    out.extend_from_slice(&WIRE_MAGIC);                       // 4B
    out.extend_from_slice(&WIRE_VERSION.to_be_bytes());       // 2B
    out.extend_from_slice(&intent_id.to_be_bytes());          // 2B
    out.extend_from_slice(&env.timestamp_ms.to_be_bytes());   // 8B
    out.extend_from_slice(&env.nonce);                        // 16B
    out.extend_from_slice(&env.sender_did_hash);              // 32B
    out.extend_from_slice(&env.recipient_did_hash);           // 32B

    debug_assert_eq!(out.len(), HEADER_SIZE);

    // ── Payload section ───────────────────────────────
    let payload_bytes = jcs_serialize(&env.payload)?;
    out.extend_from_slice(&(payload_bytes.len() as u32).to_be_bytes());
    out.extend_from_slice(&payload_bytes);

    Ok(out)
}

/// RFC 8785 JSON Canonicalization Scheme.
///
/// - Keys sorted lexicographically by Unicode code point
/// - No whitespace outside strings
/// - UTF-8 encoding
pub fn jcs_serialize(value: &Value) -> Result<Vec<u8>, WireError> {
    let canonical = canonicalize(value);
    serde_json::to_vec(&canonical)
        .map_err(|e| WireError::Serialization(e.to_string()))
}

fn canonicalize(value: &Value) -> Value {
    match value {
        Value::Object(map) => {
            let mut sorted = BTreeMap::new();
            for (k, v) in map {
                sorted.insert(k.clone(), canonicalize(v));
            }
            Value::Object(sorted.into_iter().collect())
        }
        Value::Array(arr) => Value::Array(arr.iter().map(canonicalize).collect()),
        other => other.clone(),
    }
}

/// Parse canonical wire bytes into an envelope.
pub fn parse_wire_bytes(data: &[u8]) -> Result<Envelope, WireError> {
    if data.len() < HEADER_SIZE + 4 {
        return Err(WireError::TooShort(data.len()));
    }

    let mut offset = 0;

    let magic = &data[offset..offset + 4];
    if magic != &WIRE_MAGIC {
        return Err(WireError::BadMagic);
    }
    offset += 4;

    let version = u16::from_be_bytes([data[offset], data[offset + 1]]);
    if version != WIRE_VERSION {
        return Err(WireError::BadVersion(version));
    }
    offset += 2;

    let intent_id = u16::from_be_bytes([data[offset], data[offset + 1]]);
    let intent = id_to_intent(intent_id)
        .ok_or(WireError::UnknownIntentId(intent_id))?
        .to_string();
    offset += 2;

    let timestamp_ms = u64::from_be_bytes([
        data[offset], data[offset + 1], data[offset + 2], data[offset + 3],
        data[offset + 4], data[offset + 5], data[offset + 6], data[offset + 7],
    ]);
    offset += 8;

    let mut nonce = [0u8; 16];
    nonce.copy_from_slice(&data[offset..offset + 16]);
    offset += 16;

    let mut sender_did_hash = [0u8; 32];
    sender_did_hash.copy_from_slice(&data[offset..offset + 32]);
    offset += 32;

    let mut recipient_did_hash = [0u8; 32];
    recipient_did_hash.copy_from_slice(&data[offset..offset + 32]);
    offset += 32;

    let payload_len = u32::from_be_bytes([
        data[offset], data[offset + 1], data[offset + 2], data[offset + 3],
    ]) as usize;
    offset += 4;

    if data.len() < offset + payload_len {
        return Err(WireError::TruncatedPayload);
    }

    let payload: Value = serde_json::from_slice(&data[offset..offset + payload_len])
        .map_err(|e| WireError::Deserialization(e.to_string()))?;

    Ok(Envelope {
        intent,
        timestamp_ms,
        nonce,
        sender_did_hash,
        recipient_did_hash,
        payload,
    })
}

#[derive(Debug, thiserror::Error)]
pub enum WireError {
    #[error("Wire message too short: {0} bytes")]
    TooShort(usize),
    #[error("Bad magic bytes")]
    BadMagic,
    #[error("Unsupported version: {0:#06x}")]
    BadVersion(u16),
    #[error("Unknown intent: {0}")]
    UnknownIntent(String),
    #[error("Unknown intent id: {0}")]
    UnknownIntentId(u16),
    #[error("Truncated payload")]
    TruncatedPayload,
    #[error("Serialization error: {0}")]
    Serialization(String),
    #[error("Deserialization error: {0}")]
    Deserialization(String),
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn sample() -> Envelope {
        Envelope {
            intent: "PROPOSE".to_string(),
            timestamp_ms: 1773168000000,
            nonce: [0u8; 16],
            sender_did_hash: [1u8; 32],
            recipient_did_hash: [2u8; 32],
            payload: json!({"task": "test"}),
        }
    }

    #[test]
    fn test_header_size() {
        let wire = canonical_wire_bytes(&sample()).unwrap();
        assert!(wire.len() >= HEADER_SIZE + 4);
    }

    #[test]
    fn test_magic() {
        let wire = canonical_wire_bytes(&sample()).unwrap();
        assert_eq!(&wire[0..4], b"VIRE");
    }

    #[test]
    fn test_version() {
        let wire = canonical_wire_bytes(&sample()).unwrap();
        let v = u16::from_be_bytes([wire[4], wire[5]]);
        assert_eq!(v, WIRE_VERSION);
    }

    #[test]
    fn test_roundtrip() {
        let env = sample();
        let wire = canonical_wire_bytes(&env).unwrap();
        let parsed = parse_wire_bytes(&wire).unwrap();
        assert_eq!(parsed.intent, env.intent);
        assert_eq!(parsed.timestamp_ms, env.timestamp_ms);
        assert_eq!(parsed.payload, env.payload);
    }

    #[test]
    fn test_bad_magic() {
        let mut wire = canonical_wire_bytes(&sample()).unwrap();
        wire[0] = b'X';
        assert!(matches!(parse_wire_bytes(&wire), Err(WireError::BadMagic)));
    }

    #[test]
    fn test_jcs_sorts_keys() {
        let out = jcs_serialize(&json!({"b": 1, "a": 2})).unwrap();
        assert_eq!(out, b"{\"a\":2,\"b\":1}");
    }

    #[test]
    fn test_intent_mapping() {
        assert_eq!(intent_to_id("PROPOSE"), Some(2));
        assert_eq!(id_to_intent(2), Some("PROPOSE"));
        assert_eq!(intent_to_id("UNKNOWN"), None);
    }
}