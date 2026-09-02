```markdown
# 🔐 Vireo Trust Bootstrap Protocol

**Version:** 2.0.1  
**Status:** Draft  
**Last Updated:** 2026-01-15

---

## 1. Overview

The Trust Bootstrap Protocol establishes initial trust between agents before any contract negotiation or execution.

### Goals

1. **Identity Verification** — Confirm agent identity
2. **Public Key Exchange** — Share cryptographic keys
3. **Trust Establishment** — Build mutual trust
4. **Secure Communication** — Enable encrypted messaging

---

## 2. Trust Model

### Agent Identity

Each agent has a unique identity consisting of:

```python
@dataclass
class AgentIdentity:
    agent_id: str          # Unique identifier
    public_key: bytes      # Ed25519 public key
    capabilities: List[str] # Agent capabilities
    metadata: Dict[str, Any] # Additional metadata
Trust Levels
Level	Description
None	No trust, agent unknown
Partial	Identity verified, not fully trusted
Full	Identity verified and trusted
Bridged	Trusted via intermediary
3. Bootstrap Flow
text
┌────────────┐                      ┌────────────┐
│   Agent A  │                      │   Agent B  │
└─────┬──────┘                      └─────┬──────┘
      │                                    │
      │  1. DISCOVER (public_key)          │
      ├───────────────────────────────────►│
      │                                    │
      │  2. DISCOVER_RESPONSE (public_key) │
      │◄───────────────────────────────────┤
      │                                    │
      │  3. CHALLENGE (nonce)              │
      ├───────────────────────────────────►│
      │                                    │
      │  4. CHALLENGE_RESPONSE (signature) │
      │◄───────────────────────────────────┤
      │                                    │
      │  5. VERIFY (public_key)            │
      ├───────────────────────────────────►│
      │                                    │
      │  6. VERIFY_RESPONSE (trust_level)  │
      │◄───────────────────────────────────┤
      │                                    │
      │  7. ESTABLISHED (trust)            │
      ├───────────────────────────────────►│
      │◄───────────────────────────────────┤
4. Protocol Messages
DISCOVER
json
{
  "type": "DISCOVER",
  "sender_id": "agent-123",
  "payload": {
    "public_key": "base64_encoded_pubkey",
    "capabilities": ["analyze", "report"],
    "trust_level_required": "full",
    "challenge": "base64_nonce"
  }
}
DISCOVER_RESPONSE
json
{
  "type": "DISCOVER_RESPONSE",
  "sender_id": "agent-456",
  "recipient_id": "agent-123",
  "payload": {
    "public_key": "base64_encoded_pubkey",
    "capabilities": ["process", "verify"],
    "trust_level": "partial"
  }
}
CHALLENGE
json
{
  "type": "CHALLENGE",
  "sender_id": "agent-123",
  "recipient_id": "agent-456",
  "payload": {
    "nonce": "base64_nonce",
    "timestamp": "2026-01-15T10:30:00Z",
    "requires_verification": true
  }
}
CHALLENGE_RESPONSE
json
{
  "type": "CHALLENGE_RESPONSE",
  "sender_id": "agent-456",
  "recipient_id": "agent-123",
  "payload": {
    "nonce": "base64_nonce",
    "signature": "base64_signature",
    "public_key": "base64_pubkey"
  }
}
VERIFY
json
{
  "type": "VERIFY",
  "sender_id": "agent-123",
  "recipient_id": "agent-456",
  "payload": {
    "public_key": "base64_pubkey",
    "challenge": "base64_challenge",
    "response": "base64_response"
  }
}
VERIFY_RESPONSE
json
{
  "type": "VERIFY_RESPONSE",
  "sender_id": "agent-456",
  "recipient_id": "agent-123",
  "payload": {
    "verified": true,
    "trust_level": "full",
    "expires_at": "2026-02-15T10:30:00Z"
  }
}
ESTABLISHED
json
{
  "type": "ESTABLISHED",
  "sender_id": "agent-123",
  "recipient_id": "agent-456",
  "payload": {
    "trust_level": "full",
    "session_id": "session-789",
    "encryption_key": "base64_key"
  }
}
5. Verification Logic
Challenge-Response Verification
python
def verify_challenge_response(
    agent_id: str,
    public_key: bytes,
    nonce: bytes,
    signature: bytes,
    timestamp: str
) -> bool:
    # 1. Check timestamp (max 5 minutes old)
    if is_timestamp_expired(timestamp, max_age=300):
        return False
    
    # 2. Verify nonce not reused
    if is_nonce_used(nonce):
        return False
    
    # 3. Verify signature
    message = agent_id.encode() + nonce + timestamp.encode()
    if not verify_signature(public_key, signature, message):
        return False
    
    # 4. Mark nonce as used
    mark_nonce_used(nonce)
    
    return True
Public Key Verification
python
def verify_public_key(agent_id: str, public_key: bytes) -> bool:
    # 1. Check against known registry
    if is_public_key_known(agent_id, public_key):
        return True
    
    # 2. Check against certificate authority
    if verify_with_ca(agent_id, public_key):
        return True
    
    # 3. Check via trust chain
    if verify_trust_chain(agent_id, public_key):
        return True
    
    return False
6. Trust Storage
Redis Schema
redis
# Store agent identity
HSET agent:{agent_id} {
    "public_key": "base64_pubkey",
    "capabilities": "analyze,report",
    "trust_level": "full",
    "created_at": "2026-01-15T10:30:00Z",
    "last_seen": "2026-01-15T10:30:00Z"
}

# Store trust relationships
HSET trust:{agent_id}:{peer_id} {
    "trust_level": "full",
    "established_at": "2026-01-15T10:30:00Z",
    "expires_at": "2026-02-15T10:30:00Z"
}

# Store used nonces (prevent replay)
SADD used_nonces:{agent_id} {nonce}
EXPIRE used_nonces:{agent_id} 3600
7. Trust Revocation
Revocation Triggers
Key Compromise — Private key exposed

Agent Misbehavior — Violation of protocol

Expiration — Trust level expired

Manual — Human operator revokes

Revocation Flow
json
{
  "type": "REVOKE",
  "sender_id": "agent-123",
  "recipient_id": "agent-456",
  "payload": {
    "reason": "key_compromised",
    "public_key": "base64_old_pubkey",
    "new_public_key": "base64_new_pubkey"
  }
}
8. Security Considerations
Attack Vectors
Attack	Mitigation
Replay Attack	Nonce + timestamp validation
MITM Attack	Challenge-response + signatures
Identity Spoofing	Public key verification
Key Compromise	Key rotation + revocation
Man-in-the-Middle	TLS + signatures
Best Practices
Use TLS for all communication

Rotate keys regularly (every 30 days)

Validate all signatures before trust

Monitor for suspicious activity

Implement rate limiting for trust requests

Store keys securely (HSM or secure enclave)

9. Implementation Example
python
class TrustBootstrapProtocol:
    def __init__(self, agent_id: str, private_key: bytes, public_key: bytes):
        self.agent_id = agent_id
        self.private_key = private_key
        self.public_key = public_key
        self.trusted_peers = {}
        self.nonce_cache = set()
    
    def send_discover(self, peer_id: str) -> dict:
        return {
            "type": "DISCOVER",
            "sender_id": self.agent_id,
            "payload": {
                "public_key": base64.b64encode(self.public_key).decode(),
                "capabilities": ["analyze", "report"]
            }
        }
    
    def receive_discover(self, message: dict) -> dict:
        peer_id = message["sender_id"]
        peer_pubkey = base64.b64decode(message["payload"]["public_key"])
        
        # Generate challenge
        nonce = generate_nonce()
        
        return {
            "type": "CHALLENGE",
            "sender_id": self.agent_id,
            "recipient_id": peer_id,
            "payload": {
                "nonce": base64.b64encode(nonce).decode(),
                "timestamp": get_iso_timestamp()
            }
        }
    
    def receive_challenge(self, message: dict) -> dict:
        nonce = base64.b64decode(message["payload"]["nonce"])
        timestamp = message["payload"]["timestamp"]
        
        # Sign nonce
        message_to_sign = nonce + timestamp.encode()
        signature = self.private_key.sign(message_to_sign)
        
        return {
            "type": "CHALLENGE_RESPONSE",
            "sender_id": self.agent_id,
            "recipient_id": message["sender_id"],
            "payload": {
                "nonce": base64.b64encode(nonce).decode(),
                "signature": base64.b64encode(signature).decode(),
                "public_key": base64.b64encode(self.public_key).decode()
            }
        }
    
    def receive_challenge_response(self, message: dict) -> bool:
        peer_id = message["sender_id"]
        nonce = base64.b64decode(message["payload"]["nonce"])
        signature = base64.b64decode(message["payload"]["signature"])
        peer_pubkey = base64.b64decode(message["payload"]["public_key"])
        
        # Verify signature
        message_to_verify = nonce + get_iso_timestamp().encode()
        if not verify_signature(peer_pubkey, signature, message_to_verify):
            return False
        
        # Mark as trusted
        self.trusted_peers[peer_id] = {
            "public_key": peer_pubkey,
            "trust_level": "full",
            "established_at": get_iso_timestamp()
        }
        
        return True
    
    def get_trust_level(self, peer_id: str) -> str:
        if peer_id not in self.trusted_peers:
            return "none"
        return self.trusted_peers[peer_id]["trust_level"]
10. Future Extensions
Certificate Authority — Centralized trust root

Trust Delegation — Delegate trust to other agents

Reputation System — Dynamic trust based on behavior

Zero-Knowledge Proofs — Privacy-preserving verification

Decentralized Identity — DID/VC integration