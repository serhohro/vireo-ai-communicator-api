```markdown
# 🔐 Cryptography Guide

## Overview

Vireo provides a comprehensive security and trust layer for AI-to-AI communication.

---

## HMAC Signatures

### Signing Messages

```python
from protocol import trust
from protocol.message import make_message, Intent

msg = make_message("a", "b", Intent.PROPOSE, payload={"x": 1})

# Sign
trust.attach_signature(msg, "shared-secret")
print(f"Signature: {msg.signature}")

# Verify
is_valid = trust.verify(msg, "shared-secret")
print(f"Valid: {is_valid}")
Nonce Protection
Preventing Replay Attacks
python
from protocol.trust import NonceManager

manager = NonceManager(ttl=60)

# Generate nonce
nonce, timestamp = manager.generate()

# Validate (first time — valid)
is_valid = manager.validate(nonce, timestamp)
print(f"Valid: {is_valid}")  # True

# Validate (second time — replay attack)
is_valid = manager.validate(nonce, timestamp)
print(f"Valid: {is_valid}")  # False
Ed25519 Signatures
Key Generation
python
from src.crypto.ed25519 import Ed25519Crypto

# Generate key pair
private_key, public_key = Ed25519Crypto.generate_key_pair()

# Serialize keys
priv_str = Ed25519Crypto.serialize_private_key(private_key)
pub_str = Ed25519Crypto.serialize_public_key(public_key)
Sign and Verify
python
# Sign message
message = "Hello, Vireo!"
signature = Ed25519Crypto.sign_message(private_key, message)

# Verify signature
is_valid = Ed25519Crypto.verify_message(public_key, message, signature)
print(f"Valid: {is_valid}")
W3C DID
Create DID
python
from src.crypto.did import DIDManager

manager = DIDManager()
print(f"DID: {manager.did}")
Create DID Document
python
doc = manager.create_did_document(
    public_key="z6Mkhw9nBAwZ...",
    service_endpoint="https://vireo.ai/agent"
)

print(manager.to_json(doc))
Trust Protocol
Zero-Trust Communication
python
from src.crypto.trust import TrustManager

manager = TrustManager(secret="shared-secret", ttl=30)

# Create trusted payload
payload = manager.create_trusted_payload({"task": "weather_prediction"})

# Verify payload
is_valid, data = manager.verify_trusted_payload(payload)
print(f"Valid: {is_valid}")
print(f"Data: {data}")
Full Security Demo
python
from protocol import trust
from src.crypto.trust import TrustManager

# Setup
secret = "shared-secret"
trust_mgr = TrustManager(secret, ttl=10)

# Create message
msg = make_message("a", "b", Intent.PROPOSE, payload={"task": "train"})

# Add nonce
nonce, timestamp = trust_mgr.generate_nonce()
msg.payload["_nonce"] = nonce
msg.payload["_timestamp"] = timestamp

# Sign
trust.attach_signature(msg, secret)

# Verify on recipient side
sig_valid = trust.verify(msg, secret)
nonce_valid = trust_mgr.validate_nonce(nonce, timestamp)

if sig_valid and nonce_valid:
    print("✅ Message is secure")
else:
    print("❌ Security check failed")
Next Steps
LLM Integration

Agents Guide