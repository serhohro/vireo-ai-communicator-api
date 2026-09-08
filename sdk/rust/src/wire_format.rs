// Vireo v3.0.0 — Wire Format (Rust)
// Canonical binary message format implementation

use crate::{MAGIC, PROTOCOL_VERSION, NONCE_SIZE, SIGNATURE_SIZE, HASH_SIZE, MAX_MESSAGE_SIZE};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

/// Protocol intent codes
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[repr(u8)]
pub enum Intent {
    /// Propose a contract or action
    Propose = 0x01,
    /// Commit to a proposal
    Commit = 0x02,
    /// Execute a task
    Execute = 0x03,
    /// Verify execution results
    Verify = 0x04,
    /// Mark as done
    Done = 0x05,
    /// Escalate a dispute
    Escalate = 0x06,
    /// Reject a proposal
    Reject = 0x07,
    /// Timeout occurred
    Timeout = 0x08,
}

impl Intent {
    /// Convert from byte to Intent
    pub fn from_byte(byte: u8) -> Option<Self> {
        match byte {
            0x01 => Some(Self::Propose),
            0x02 => Some(Self::Commit),
            0x03 => Some(Self::Execute),
            0x04 => Some(Self::Verify),
            0x05 => Some(Self::Done),
            0x06 => Some(Self::Escalate),
            0x07 => Some(Self::Reject),
            0x08 => Some(Self::Timeout),
            _ => None,
        }
    }
    
    /// Convert to byte
    pub fn to_byte(self) -> u8 {
        self as u8
    }
}

/// Message flags
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Flags {
    /// Message is compressed
    pub compressed: bool,
    /// Message is encrypted
    pub encrypted: bool,
}

impl Flags {
    /// Default flags (none)
    pub const NONE: Self = Self {
        compressed: false,
        encrypted: false,
    };
    
    /// Convert flags to byte
    pub fn to_byte(&self) -> u8 {
        let mut b = 0u8;
        if self.compressed {
            b |= 0x01;
        }
        if self.encrypted {
            b |= 0x02;
        }
        b
    }
    
    /// Convert from byte to flags
    pub fn from_byte(b: u8) -> Self {
        Self {
            compressed: (b & 0x01) != 0,
            encrypted: (b & 0x02) != 0,
        }
    }
}

/// Vireo canonical protocol message
///
/// # Binary Format
/// ```text
/// ┌────────────────────────────────────────────────────────────┐
/// │ Header: Magic(4) + Version(1) + Flags(1) + Reserved(2)   │
/// ├────────────────────────────────────────────────────────────┤
/// │ Sender:    Length(1) + UTF-8 bytes                       │
/// │ Recipient: Length(1) + UTF-8 bytes                       │
/// │ Intent:    1 byte                                        │
/// │ Timestamp: 8 bytes (u64, ms since epoch)                 │
/// │ Nonce:     16 bytes                                      │
/// │ ProposalID: Length(1) + UTF-8 bytes                      │
/// │ PayloadHash: 32 bytes (BLAKE2b)                          │
/// │ Signature: 64 bytes (Ed25519)                            │
/// └────────────────────────────────────────────────────────────┘
/// ```
#[derive(Debug, Clone)]
pub struct Message {
    /// Protocol version (0x30 for v3.0)
    pub version: u8,
    /// Message flags
    pub flags: Flags,
    /// Sender DID
    pub sender: String,
    /// Recipient DID
    pub recipient: String,
    /// Message intent
    pub intent: Intent,
    /// Timestamp in milliseconds since Unix epoch
    pub timestamp_ms: u64,
    /// Random nonce (16 bytes)
    pub nonce: [u8; NONCE_SIZE],
    /// Proposal ID
    pub proposal_id: String,
    /// BLAKE2b hash of payload (32 bytes)
    pub payload_hash: [u8; HASH_SIZE],
    /// Ed25519 signature (64 bytes)
    pub signature: [u8; SIGNATURE_SIZE],
    /// Optional payload (not serialized)
    pub payload: Option<serde_json::Value>,
}

impl Message {
    /// Create a new message
    pub fn new(
        sender: String,
        recipient: String,
        intent: Intent,
        proposal_id: String,
        payload: serde_json::Value,
    ) -> Self {
        let timestamp_ms = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_else(|_| std::time::Duration::from_secs(0))
            .as_millis() as u64;
        
        // Compute payload hash
        let payload_json = serde_json::to_string(&payload)
            .unwrap_or_else(|_| "{}".to_string());
        
        use blake2::Blake2b512;
        use digest::Digest;
        let hash = Blake2b512::digest(payload_json.as_bytes());
        let mut payload_hash = [0u8; HASH_SIZE];
        payload_hash.copy_from_slice(&hash[..HASH_SIZE]);
        
        Self {
            version: PROTOCOL_VERSION,
            flags: Flags::NONE,
            sender,
            recipient,
            intent,
            timestamp_ms,
            nonce: [0u8; NONCE_SIZE],
            proposal_id,
            payload_hash,
            signature: [0u8; SIGNATURE_SIZE],
            payload: Some(payload),
        }
    }
    
    /// Compute canonical hash for signing
    pub fn canonical_hash(&self) -> [u8; HASH_SIZE] {
        let mut parts = Vec::new();
        parts.extend_from_slice(MAGIC);
        parts.push(self.version);
        parts.push(self.flags.to_byte());
        parts.extend_from_slice(&[0, 0]); // Reserved
        
        // Sender
        parts.push(self.sender.len() as u8);
        parts.extend_from_slice(self.sender.as_bytes());
        
        // Recipient
        parts.push(self.recipient.len() as u8);
        parts.extend_from_slice(self.recipient.as_bytes());
        
        // Intent
        parts.push(self.intent.to_byte());
        
        // Timestamp
        parts.extend_from_slice(&self.timestamp_ms.to_be_bytes());
        
        // Nonce
        parts.extend_from_slice(&self.nonce);
        
        // Proposal ID
        parts.push(self.proposal_id.len() as u8);
        parts.extend_from_slice(self.proposal_id.as_bytes());
        
        // Payload hash
        parts.extend_from_slice(&self.payload_hash);
        
        use blake2::Blake2b512;
        use digest::Digest;
        let hash = Blake2b512::digest(&parts);
        let mut result = [0u8; HASH_SIZE];
        result.copy_from_slice(&hash[..HASH_SIZE]);
        result
    }
    
    /// Serialize message to canonical binary format
    pub fn serialize(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(256);
        
        // Header
        bytes.extend_from_slice(MAGIC);
        bytes.push(self.version);
        bytes.push(self.flags.to_byte());
        bytes.extend_from_slice(&[0, 0]); // Reserved
        
        // Sender
        bytes.push(self.sender.len() as u8);
        bytes.extend_from_slice(self.sender.as_bytes());
        
        // Recipient
        bytes.push(self.recipient.len() as u8);
        bytes.extend_from_slice(self.recipient.as_bytes());
        
        // Intent
        bytes.push(self.intent.to_byte());
        
        // Timestamp
        bytes.extend_from_slice(&self.timestamp_ms.to_be_bytes());
        
        // Nonce
        bytes.extend_from_slice(&self.nonce);
        
        // Proposal ID
        bytes.push(self.proposal_id.len() as u8);
        bytes.extend_from_slice(self.proposal_id.as_bytes());
        
        // Payload hash
        bytes.extend_from_slice(&self.payload_hash);
        
        // Signature
        bytes.extend_from_slice(&self.signature);
        
        bytes
    }
    
    /// Deserialize from canonical binary format
    pub fn deserialize(data: &[u8]) -> Result<Self, String> {
        if data.len() < 8 {
            return Err("Message too short".to_string());
        }
        
        if data.len() > MAX_MESSAGE_SIZE {
            return Err(format!("Message too large: {} bytes", data.len()));
        }
        
        let mut offset = 0;
        
        // Magic
        let magic = &data[offset..offset + 4];
        if magic != MAGIC {
            return Err(format!("Invalid magic: {:?}", magic));
        }
        offset += 4;
        
        // Version
        let version = data[offset];
        if version != PROTOCOL_VERSION {
            return Err(format!("Unsupported version: {}", version));
        }
        offset += 1;
        
        // Flags
        let flags = Flags::from_byte(data[offset]);
        offset += 1;
        offset += 2; // Reserved
        
        // Sender
        if offset >= data.len() {
            return Err("Invalid message: missing sender".to_string());
        }
        let sender_len = data[offset] as usize;
        offset += 1;
        if offset + sender_len > data.len() {
            return Err("Invalid message: sender truncated".to_string());
        }
        let sender = String::from_utf8_lossy(&data[offset..offset + sender_len]).to_string();
        offset += sender_len;
        
        // Recipient
        if offset >= data.len() {
            return Err("Invalid message: missing recipient".to_string());
        }
        let recipient_len = data[offset] as usize;
        offset += 1;
        if offset + recipient_len > data.len() {
            return Err("Invalid message: recipient truncated".to_string());
        }
        let recipient = String::from_utf8_lossy(&data[offset..offset + recipient_len]).to_string();
        offset += recipient_len;
        
        // Intent
        if offset >= data.len() {
            return Err("Invalid message: missing intent".to_string());
        }
        let intent = Intent::from_byte(data[offset])
            .ok_or_else(|| format!("Invalid intent: {}", data[offset]))?;
        offset += 1;
        
        // Timestamp
        if offset + 8 > data.len() {
            return Err("Invalid message: missing timestamp".to_string());
        }
        let timestamp_ms = u64::from_be_bytes(
            data[offset..offset + 8]
                .try_into()
                .map_err(|_| "Invalid timestamp".to_string())?
        );
        offset += 8;
        
        // Nonce
        if offset + NONCE_SIZE > data.len() {
            return Err("Invalid message: missing nonce".to_string());
        }
        let mut nonce = [0u8; NONCE_SIZE];
        nonce.copy_from_slice(&data[offset..offset + NONCE_SIZE]);
        offset += NONCE_SIZE;
        
        // Proposal ID
        if offset >= data.len() {
            return Err("Invalid message: missing proposal ID".to_string());
        }
        let proposal_id_len = data[offset] as usize;
        offset += 1;
        if offset + proposal_id_len > data.len() {
            return Err("Invalid message: proposal ID truncated".to_string());
        }
        let proposal_id = String::from_utf8_lossy(&data[offset..offset + proposal_id_len]).to_string();
        offset += proposal_id_len;
        
        // Payload hash
        if offset + HASH_SIZE > data.len() {
            return Err("Invalid message: missing payload hash".to_string());
        }
        let mut payload_hash = [0u8; HASH_SIZE];
        payload_hash.copy_from_slice(&data[offset..offset + HASH_SIZE]);
        offset += HASH_SIZE;
        
        // Signature
        if offset + SIGNATURE_SIZE > data.len() {
            return Err("Invalid message: missing signature".to_string());
        }
        let mut signature = [0u8; SIGNATURE_SIZE];
        signature.copy_from_slice(&data[offset..offset + SIGNATURE_SIZE]);
        offset += SIGNATURE_SIZE;
        
        Ok(Self {
            version,
            flags,
            sender,
            recipient,
            intent,
            timestamp_ms,
            nonce,
            proposal_id,
            payload_hash,
            signature,
            payload: None,
        })
    }
    
    /// Verify the message signature
    pub fn verify(&self, public_key: &[u8; 32]) -> bool {
        let hash = self.canonical_hash();
        crate::crypto::verify(&hash, &self.signature, public_key)
    }
    
    /// Sign the message with a private key
    pub fn sign(&mut self, private_key: &[u8; 32]) {
        let hash = self.canonical_hash();
        self.signature = crate::crypto::sign(&hash, private_key);
    }
    
    /// Check if timestamp is within the allowed window
    pub fn is_timestamp_valid(&self) -> bool {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_else(|_| std::time::Duration::from_secs(0))
            .as_millis() as u64;
        
        let diff = if now >= self.timestamp_ms {
            now - self.timestamp_ms
        } else {
            self.timestamp_ms - now
        };
        
        diff <= crate::TIMESTAMP_WINDOW_MS
    }
    
    /// Validate DID format
    pub fn validate_did(did: &str) -> bool {
        did.starts_with("did:vireo:agent:") && did.len() > "did:vireo:agent:".len()
    }
}

impl Default for Message {
    fn default() -> Self {
        Self {
            version: PROTOCOL_VERSION,
            flags: Flags::NONE,
            sender: String::new(),
            recipient: String::new(),
            intent: Intent::Propose,
            timestamp_ms: 0,
            nonce: [0u8; NONCE_SIZE],
            proposal_id: String::new(),
            payload_hash: [0u8; HASH_SIZE],
            signature: [0u8; SIGNATURE_SIZE],
            payload: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::crypto::generate_keypair;
    use serde_json::json;
    
    #[test]
    fn test_serialize_deserialize() {
        let (priv_key, pub_key) = generate_keypair();
        
        let mut msg = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"hello": "world"}),
        );
        msg.sign(&priv_key);
        
        let serialized = msg.serialize();
        let deserialized = Message::deserialize(&serialized).unwrap();
        
        assert_eq!(msg.version, deserialized.version);
        assert_eq!(msg.sender, deserialized.sender);
        assert_eq!(msg.recipient, deserialized.recipient);
        assert_eq!(msg.intent, deserialized.intent);
        assert_eq!(msg.timestamp_ms, deserialized.timestamp_ms);
        assert_eq!(msg.proposal_id, deserialized.proposal_id);
        
        // Verify signature
        assert!(deserialized.verify(&pub_key));
    }
    
    #[test]
    fn test_canonical_hash() {
        let msg1 = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"a": 1, "b": 2}),
        );
        
        let msg2 = Message::new(
            "did:vireo:agent:alice".to_string(),
            "did:vireo:agent:bob".to_string(),
            Intent::Propose,
            "prop_001".to_string(),
            json!({"b": 2, "a": 1}),
        );
        
        assert_eq!(msg1.canonical_hash(), msg2.canonical_hash());
    }
    
    #[test]
    fn test_intent_conversion() {
        assert_eq!(Intent::Propose.to_byte(), 0x01);
        assert_eq!(Intent::Commit.to_byte(), 0x02);
        assert_eq!(Intent::Execute.to_byte(), 0x03);
        assert_eq!(Intent::Verify.to_byte(), 0x04);
        assert_eq!(Intent::Done.to_byte(), 0x05);
        assert_eq!(Intent::Escalate.to_byte(), 0x06);
        assert_eq!(Intent::Reject.to_byte(), 0x07);
        assert_eq!(Intent::Timeout.to_byte(), 0x08);
        
        assert_eq!(Intent::from_byte(0x01), Some(Intent::Propose));
        assert_eq!(Intent::from_byte(0x99), None);
    }
    
    #[test]
    fn test_flags() {
        let flags = Flags {
            compressed: true,
            encrypted: true,
        };
        let byte = flags.to_byte();
        assert_eq!(byte, 0x03);
        
        let restored = Flags::from_byte(byte);
        assert_eq!(restored.compressed, true);
        assert_eq!(restored.encrypted, true);
    }
    
    #[test]
    fn test_did_validation() {
        assert!(Message::validate_did("did:vireo:agent:alice"));
        assert!(Message::validate_did("did:vireo:agent:bob"));
        assert!(!Message::validate_did("invalid"));
        assert!(!Message::validate_did("did:vireo:agent:"));
    }
}