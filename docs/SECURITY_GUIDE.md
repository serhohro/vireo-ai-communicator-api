# 🔐 Vireo v3.0.0 — Security Guide

**Comprehensive security guide for Vireo v3.0.0**

---

## 📚 Table of Contents

1. [Overview](#1-overview)
2. [Cryptography](#2-cryptography)
3. [Identity Management (DIDs)](#3-identity-management-dids)
4. [Federated Trust](#4-federated-trust)
5. [Trust Bootstrap](#5-trust-bootstrap)
6. [Message Security](#6-message-security)
7. [Secure Communication](#7-secure-communication)
8. [Zero-Knowledge Proofs (ZK-SNARKs)](#8-zero-knowledge-proofs-zk-snarks)
9. [Key Rotation](#9-key-rotation)
10. [Security Best Practices](#10-security-best-practices)
11. [Threat Modeling](#11-threat-modeling)
12. [Compliance](#12-compliance)
13. [Audit Logging](#13-audit-logging)
14. [Incident Response](#14-incident-response)

---

## 1. Overview

### Security Principles

> *"Let PyTorch handle the tensors; let Vireo handle the trust."* — Qwen

> *"The real challenge isn't signing — it's key discovery and trust bootstrapping."* — Kimi

### Three Pillars of Vireo Security
┌─────────────────────────────────────────────────────┐
│ VIREO SECURITY │
├─────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │ IDENTITY │ │ TRUST │ │ INTEGRITY ││
│ │ │ │ │ │ ││
│ │ • DIDs │ │ • Federated│ │ • Ed25519 ││
│ │ • VCs │ │ • Reputation│ │ • ZK-SNARKs││
│ │ • DID Doc │ │ • Web of │ │ • Canonical││
│ │ │ │ Trust │ │ Hashing ││
│ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────┘

text

### Security Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **L1** | Basic validation | Development, testing |
| **L2** | Signed messages | Production, internal |
| **L3** | DIDs + VCs | Enterprise, regulated |
| **L4** | ZK-SNARKs | Privacy-preserving, financial |

---

## 2. Cryptography

### 2.1 Ed25519 Signatures

Ed25519 is the primary signature scheme for Vireo v3.0.0.

```python
from core.crypto.ed25519 import Ed25519
import base64

# Generate key pair
private_key, public_key = Ed25519.generate_keypair()
print(f"Private: {base64.b64encode(private_key).decode()[:16]}...")
print(f"Public: {base64.b64encode(public_key).decode()[:16]}...")

# Sign a message
message = b"Hello, Vireo v3.0.0!"
signature = Ed25519.sign(private_key, message)
print(f"Signature: {base64.b64encode(signature).decode()[:32]}...")

# Verify signature
is_valid = Ed25519.verify(public_key, message, signature)
assert is_valid, "❌ Signature verification failed!"
print("✅ Signature verified successfully!")
2.2 Blake2b Hashing
Blake2b is used for canonical hashing and contract verification.

python
from core.crypto.blake2b import Blake2b

# Hash data
data = b"Contract data to hash"
hash_bytes = Blake2b.hash(data)
print(f"Hash: {hash_bytes.hex()}")

# Hash with key (for HMAC)
key = b"secret_key"
hmac = Blake2b.hash(data, key=key)
print(f"HMAC: {hmac.hex()}")

# Canonical hash of JSON
from core.crypto.hash import canonical_hash

obj = {
    "type": "CONTRACT",
    "id": "123",
    "terms": {"max_tokens": 1000}
}
canonical = canonical_hash(obj)
print(f"Canonical: {canonical.hex()}")
2.3 Key Storage
python
from core.identity.key_manager import KeyManager

# Initialize key manager
km = KeyManager(storage_path="keys/")

# Store key
km.store_key("agent-1", private_key, public_key)

# Retrieve key
priv, pub = km.get_key("agent-1")

# List keys
keys = km.list_keys()
print(f"Keys: {keys}")

# Delete key
km.delete_key("agent-1")
2.4 Cryptographic Best Practices
python
# ✅ DO: Use proper key generation
private, public = Ed25519.generate_keypair()

# ❌ DON'T: Use weak seeds or hardcoded keys
# private = b"hardcoded_key"  # NEVER DO THIS!

# ✅ DO: Use secure random for nonces
from core.crypto.nonce import generate_nonce
nonce = generate_nonce()

# ❌ DON'T: Reuse nonces
# nonce = b"same_nonce"  # NEVER DO THIS!

# ✅ DO: Verify signatures before processing
if Ed25519.verify(public_key, message, signature):
    process_message(message)
else:
    reject_message("Invalid signature")

# ❌ DON'T: Process without verification
# process_message(message)  # NEVER DO THIS!
3. Identity Management (DIDs)
3.1 What are DIDs?
Decentralized Identifiers (DIDs) are self-sovereign identities:

No central authority

Owned by the agent

Cryptographically verifiable

Privacy-preserving

text
did:vireo:agent-1-abc123
│   │      │
│   │      └─ Unique ID
│   └──────── Method (vireo)
└──────────── DID Scheme
3.2 Create a DID
python
from core.identity.did import DID

# Create a new DID
did = DID.create(
    name="agent-1",
    method="vireo",
    public_key=public_key
)

print(f"DID: {did.id}")
print(f"Public Key: {did.public_key[:32]}...")

# DID Document
doc = did.to_document()
print(json.dumps(doc, indent=2))
DID Document Example:

json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:vireo:agent-1-abc123",
  "verificationMethod": [{
    "id": "did:vireo:agent-1-abc123#key-1",
    "type": "Ed25519VerificationKey2020",
    "publicKeyMultibase": "z6Mk..."
  }],
  "authentication": ["did:vireo:agent-1-abc123#key-1"],
  "assertionMethod": ["did:vireo:agent-1-abc123#key-1"],
  "capabilityDelegation": ["did:vireo:agent-1-abc123#key-1"],
  "capabilityInvocation": ["did:vireo:agent-1-abc123#key-1"],
  "service": [{
    "id": "did:vireo:agent-1-abc123#vireo",
    "type": "VireoAgent",
    "serviceEndpoint": "http://localhost:5000"
  }]
}
3.3 Verify a DID
python
from core.identity.did_resolver import DIDResolver

# Create resolver
resolver = DIDResolver()

# Resolve DID
doc = resolver.resolve("did:vireo:agent-1-abc123")
print(f"Resolved: {doc['id']}")

# Verify DID
is_valid = resolver.verify("did:vireo:agent-1-abc123")
print(f"✅ DID valid: {is_valid}")

# Verify with proof
proof = {
    "type": "Ed25519Signature2020",
    "created": "2026-09-06T10:30:00Z",
    "verificationMethod": "did:vireo:agent-1-abc123#key-1",
    "proofPurpose": "authentication"
}
is_valid = resolver.verify_proof("did:vireo:agent-1-abc123", proof)
print(f"✅ Proof valid: {is_valid}")
3.4 Verifiable Credentials (VCs)
python
from core.identity.vc import VerifiableCredential, VCIssuer

# Create VC issuer
issuer = VCIssuer(private_key)

# Issue credential
vc = issuer.issue(
    subject="did:vireo:agent-1-abc123",
    claims={
        "capability": "analyze_images",
        "level": "expert",
        "expires": "2027-12-31"
    }
)

print(f"VC ID: {vc['id']}")
print(f"Subject: {vc['credentialSubject']['id']}")

# Verify VC
from core.identity.vc import VCVerifier

verifier = VCVerifier()
is_valid = verifier.verify(vc)
print(f"✅ VC valid: {is_valid}")
3.5 DID Discovery
python
# Discover agents by DID
from core.identity.discovery import DIDDiscovery

discovery = DIDDiscovery()

# Find agents with specific capability
agents = discovery.find_by_capability("analyze_images")
print(f"Found {len(agents)} agents")

# Find agents by reputation
agents = discovery.find_by_reputation(min_score=0.8)
print(f"Found {len(agents)} trusted agents")

# Find agent by DID
agent = discovery.resolve("did:vireo:agent-1-abc123")
print(f"Agent: {agent}")
4. Federated Trust
4.1 What is Federated Trust?
No central authority — trust is distributed

Reputation-based — trust is earned

Verifiable Credentials — trust is provable

Web of Trust — trust is transitive

4.2 Trust Graph
python
from core.identity.federated_trust import FederatedTrust

# Initialize trust system
trust = FederatedTrust()

# Add trust relationship
trust.add_relationship(
    truster="did:vireo:agent-1-abc123",
    trustee="did:vireo:agent-2-def456",
    level=0.9
)

# Get trust score
score = trust.get_trust_score("did:vireo:agent-2-def456")
print(f"Trust score: {score}")

# Get transitive trust
distance = trust.get_trust_distance(
    "did:vireo:agent-1-abc123",
    "did:vireo:agent-3-ghi789"
)
print(f"Trust distance: {distance}")
4.3 Reputation Management
python
from core.identity.reputation import ReputationManager

# Initialize reputation
reputation = ReputationManager()

# Update reputation based on interactions
reputation.update(
    did="did:vireo:agent-2-def456",
    interaction="contract_execution",
    success=True
)

# Get reputation
score = reputation.get_score("did:vireo:agent-2-def456")
print(f"Reputation: {score}")

# Get history
history = reputation.get_history("did:vireo:agent-2-def456")
print(f"History: {len(history)} events")
4.4 Trust Bootstrap
python
from core.identity.trust_bootstrap import TrustBootstrap

# Initialize bootstrap
bootstrap = TrustBootstrap()

# Bootstrap from known trust anchors
anchors = [
    "did:vireo:trust-authority-1",
    "did:vireo:trust-authority-2"
]
trusted = bootstrap.bootstrap(anchors=anchors)
print(f"Trusted agents: {len(trusted)}")

# Verify chain of trust
chain = bootstrap.verify_chain(
    "did:vireo:agent-1-abc123",
    "did:vireo:agent-3-ghi789"
)
print(f"Chain length: {len(chain)}")
5. Trust Bootstrap
5.1 Initial Trust Setup
python
from core.identity.trust_bootstrap import TrustBootstrap
from core.crypto.ed25519 import Ed25519

# Step 1: Generate trust anchor key
anchor_private, anchor_public = Ed25519.generate_keypair()

# Step 2: Create trust anchor
anchor = TrustBootstrap.create_anchor(
    name="Vireo Trust Authority",
    public_key=anchor_public
)

# Step 3: Bootstrap new agent
agent_private, agent_public = Ed25519.generate_keypair()
agent_did = "did:vireo:agent-1-abc123"

# Issue trust certificate
cert = TrustBootstrap.issue_certificate(
    anchor_private=anchor_private,
    subject=agent_did,
    public_key=agent_public
)

# Step 4: Verify certificate
is_valid = TrustBootstrap.verify_certificate(
    certificate=cert,
    anchor_public=anchor_public
)
print(f"✅ Certificate valid: {is_valid}")
5.2 Whitelist (Legacy) vs Federated Trust
Feature	Whitelist	Federated Trust
Central authority	✅ Required	❌ Not required
Scalability	❌ Limited	✅ Unlimited
Privacy	❌ Exposed	✅ Privacy-preserving
Revocation	❌ Complex	✅ Simple via VCs
Cross-domain	❌ Hard	✅ Easy
5.3 Migration from Whitelist to Federated Trust
python
# Step 1: Export existing whitelist
from core.identity.trust_bootstrap import migrate_from_whitelist

whitelist = ["agent-1", "agent-2", "agent-3"]

# Step 2: Create DIDs for whitelisted agents
dids = migrate_from_whitelist(whitelist)

# Step 3: Issue Verifiable Credentials
for agent in dids:
    vc = TrustBootstrap.issue_vc(
        subject=agent,
        claims={"whitelisted": True}
    )

print(f"✅ Migrated {len(dids)} agents to federated trust")
6. Message Security
6.1 Signing Messages
python
from core.protocol.message import Message
from core.crypto.ed25519 import Ed25519
from core.crypto.hash import canonical_hash

# Create message
msg = Message(
    type="PROPOSE",
    sender="agent-1",
    recipient="agent-2",
    payload={"contract_id": "123"}
)

# Sign message
private_key, public_key = Ed25519.generate_keypair()
signature = msg.sign(private_key)

# Send message with signature
msg.signature = signature
msg.public_key = public_key

# Verify on receipt
is_valid = msg.verify()
print(f"✅ Message valid: {is_valid}")
6.2 Message Integrity
python
# Verify message hasn't been tampered
def verify_message_integrity(msg):
    # 1. Check signature
    if not msg.verify():
        return False, "Invalid signature"
    
    # 2. Check timestamp (prevent replay)
    if msg.timestamp < time.time() - 3600:
        return False, "Message too old"
    
    # 3. Check nonce (prevent replay)
    from core.protocol.nonce_manager import NonceManager
    nm = NonceManager()
    if nm.is_used(msg.nonce):
        return False, "Nonce already used"
    
    # 4. Check payload integrity
    hash = canonical_hash(msg.payload)
    if hash != msg.payload_hash:
        return False, "Payload hash mismatch"
    
    return True, "Message verified"
6.3 Nonce Management
python
from core.protocol.nonce_manager import NonceManager

# Initialize nonce manager
nm = NonceManager(storage="redis://localhost:6379")

# Generate nonce
nonce = nm.generate()
print(f"Nonce: {nonce}")

# Check if nonce was used
if nm.is_used(nonce):
    print("❌ Nonce already used (replay attack detected!)")
else:
    print("✅ Fresh nonce")
    nm.mark_used(nonce)
7. Secure Communication
7.1 TLS/HTTPS
python
# Enable TLS in server
from api.server import create_app

app = create_app()

# Run with TLS
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=443,
        ssl_context=("cert.pem", "key.pem")
    )
7.2 End-to-End Encryption
python
from core.crypto.e2ee import E2EE

# Generate session key
e2ee = E2EE()
session_key = e2ee.generate_session_key()

# Encrypt message
encrypted = e2ee.encrypt(
    message=b"Sensitive data",
    recipient_public_key=recipient_public
)

# Decrypt message
decrypted = e2ee.decrypt(
    encrypted=encrypted,
    private_key=private_key
)
print(f"Decrypted: {decrypted}")
7.3 Secure Transport Protocols
python
# WebSocket with TLS (wss://)
from protocol.transport.websocket import SecureWebSocketTransport

transport = SecureWebSocketTransport(
    url="wss://localhost:5000/ws",
    tls=True,
    verify_cert=True
)

# gRPC with TLS
from protocol.transport.grpc import SecureGRPCTransport

transport = SecureGRPCTransport(
    address="localhost:50051",
    use_tls=True,
    ca_cert="ca.pem"
)

# Redis with TLS
from protocol.transport.redis import SecureRedisTransport

transport = SecureRedisTransport(
    url="rediss://localhost:6379",
    ssl_cert_reqs="required"
)
8. Zero-Knowledge Proofs (ZK-SNARKs)
8.1 What are ZK-SNARKs?
Zero-Knowledge Succinct Non-Interactive Argument of Knowledge

Prove you know something without revealing it

Succinct: Small proof size

Non-interactive: No back-and-forth

Zero-knowledge: Reveals nothing except truth

8.2 ZK-SNARK in Vireo
python
from core.crypto.zk_snarks import ZKProver, ZKVerifier

# Setup
prover = ZKProver()
verifier = ZKVerifier()

# Create proof (e.g., prove age > 18 without revealing age)
witness = {
    "age": 25,
    "min_age": 18
}
circuit = """
def main(age, min_age):
    return age >= min_age
"""

# Generate proof
proof = prover.prove(
    circuit=circuit,
    witness=witness,
    public_inputs=["min_age"]
)

# Verify proof
is_valid = verifier.verify(
    proof=proof,
    public_inputs={"min_age": 18}
)
print(f"✅ ZK proof valid: {is_valid}")
8.3 Use Cases
python
# 1. Prove capability without revealing identity
proof = prover.prove_capability(
    did="did:vireo:agent-1-abc123",
    capability="analyze_images"
)

# 2. Prove reputation without revealing history
proof = prover.prove_reputation(
    did="did:vireo:agent-1-abc123",
    min_score=0.8
)

# 3. Prove compliance without revealing data
proof = prover.prove_compliance(
    data=encrypted_data,
    regulation="GDPR"
)
9. Key Rotation
9.1 Why Rotate Keys?
Compromise: If key is leaked

Best practice: Regular rotation

Compliance: Regulatory requirements

Forward secrecy: Past messages stay safe

9.2 Key Rotation Process
python
from core.identity.key_manager import KeyManager
from core.crypto.ed25519 import Ed25519

# Initialize key manager
km = KeyManager()

# Rotate key
def rotate_key(agent_id):
    # 1. Generate new key
    new_private, new_public = Ed25519.generate_keypair()
    
    # 2. Sign new public key with old private key
    old_private, old_public = km.get_key(agent_id)
    signature = Ed25519.sign(old_private, new_public)
    
    # 3. Store new key
    km.store_key(agent_id, new_private, new_public)
    
    # 4. Store rotation proof
    km.store_rotation_proof(agent_id, {
        "old_public": old_public,
        "new_public": new_public,
        "signature": signature,
        "timestamp": time.time()
    })
    
    return new_public

# Rotate key
new_public = rotate_key("agent-1")
print(f"✅ Key rotated: {new_public[:32]}...")
9.3 Key Rotation Schedule
python
from core.identity.key_manager import KeyRotationPolicy

# Define policy
policy = KeyRotationPolicy(
    max_age_days=90,
    max_signatures=10000,
    require_approval=True
)

# Check if rotation needed
if policy.should_rotate("agent-1"):
    print("⚠️ Key rotation required")
    rotate_key("agent-1")
else:
    print("✅ Key still valid")
10. Security Best Practices
10.1 Development
python
# ✅ DO: Use environment variables for secrets
import os
PRIVATE_KEY = os.getenv("VIREO_PRIVATE_KEY")

# ❌ DON'T: Hardcode secrets
# PRIVATE_KEY = "my_secret_key"  # NEVER DO THIS!

# ✅ DO: Use secure random for salts, nonces
from secrets import token_bytes
salt = token_bytes(32)

# ❌ DON'T: Use weak randomness
# import random; salt = random.randbytes(32)  # NEVER DO THIS!

# ✅ DO: Validate all inputs
def process_message(msg):
    if not validate_schema(msg):
        raise ValueError("Invalid message format")
    if not verify_signature(msg):
        raise ValueError("Invalid signature")
    return process(msg)

# ❌ DON'T: Trust inputs blindly
# def process_message(msg): return process(msg)  # NEVER DO THIS!
10.2 Production
python
# ✅ DO: Use HTTPS in production
# ❌ DON'T: Use HTTP in production

# ✅ DO: Use rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/v3/message')
@limiter.limit("100 per minute")
def message():
    return process_message()

# ❌ DON'T: Allow unlimited requests

# ✅ DO: Log all security events
import logging
logger = logging.getLogger("security")

def log_security_event(event_type, details):
    logger.warning({
        "event": event_type,
        "details": details,
        "timestamp": time.time()
    })

# ❌ DON'T: Skip logging for security events
10.3 Deployment Checklist
yaml
Security Checklist:
  ✅ TLS/HTTPS enabled
  ✅ Secrets in environment variables
  ✅ Rate limiting configured
  ✅ Security logging enabled
  ✅ Regular key rotation
  ✅ DID verification enabled
  ✅ Federated trust configured
  ✅ ZK-SNARKs for sensitive data
  ✅ Audit trail enabled
  ✅ Incident response plan ready
11. Threat Modeling
11.1 Threat Actors
Actor	Threat	Mitigation
External Attacker	Message interception	TLS encryption
Internal Attacker	Message tampering	Signatures
Malicious Agent	Identity theft	DIDs + VCs
Replay Attacker	Message replay	Nonces + timestamps
MITM	Man-in-the-middle	Certificate pinning
DoS	Denial of service	Rate limiting
11.2 STRIDE Analysis
Threat	Description	Mitigation
Spoofing	Fake identity	DIDs + Signatures
Tampering	Message alteration	Signatures + Hashes
Repudiation	Deny actions	Audit logs + Signatures
Information Disclosure	Data leak	Encryption + ZK-SNARKs
Denial of Service	Service unavailable	Rate limiting + Fail2ban
Elevation of Privilege	Unauthorized access	Capability verification
11.3 Security Controls Matrix
python
# security_controls.yaml

controls:
  - id: SC-1
    name: "Cryptographic Signatures"
    implementation: "Ed25519"
    coverage: "All messages"
    
  - id: SC-2
    name: "Identity Verification"
    implementation: "DIDs + VCs"
    coverage: "All agents"
    
  - id: SC-3
    name: "Encryption"
    implementation: "TLS + E2EE"
    coverage: "Transport layer"
    
  - id: SC-4
    name: "Rate Limiting"
    implementation: "Flask-Limiter"
    coverage: "API endpoints"
    
  - id: SC-5
    name: "Audit Logging"
    implementation: "Structured logging"
    coverage: "All actions"
12. Compliance
12.1 GDPR Compliance
python
from core.compliance.gdpr import GDPRCompliance

# Ensure GDPR compliance
compliance = GDPRCompliance()

# Data minimization
compliance.minimize_data(data)

# Right to be forgotten
compliance.delete_agent_data("did:vireo:agent-1-abc123")

# Data portability
data = compliance.export_data("did:vireo:agent-1-abc123")
12.2 HIPAA Compliance (Healthcare)
python
from core.compliance.hipaa import HIPAACompliance

# Ensure HIPAA compliance
hipaa = HIPAACompliance()

# Encrypt PHI
encrypted = hipaa.encrypt_phi(patient_data)

# Audit access
hipaa.audit_access(
    agent="did:vireo:agent-1-abc123",
    resource="patient-123",
    action="read"
)
12.3 SOC2 Compliance
python
from core.compliance.soc2 import SOC2Compliance

# Ensure SOC2 compliance
soc2 = SOC2Compliance()

# Security controls
soc2.verify_controls()

# Audit trail
soc2.generate_audit_report()
13. Audit Logging
13.1 Audit Log Format
json
{
  "timestamp": "2026-09-06T10:30:00Z",
  "event_id": "evt-123",
  "event_type": "message_sent",
  "agent": "did:vireo:agent-1-abc123",
  "action": "propose_contract",
  "resource": "contract-123",
  "result": "success",
  "ip": "192.168.1.100",
  "signature": "0x1234...",
  "hash": "0x5678..."
}
13.2 Audit Log Implementation
python
from core.audit import AuditLogger

# Initialize audit logger
audit = AuditLogger(
    storage="elasticsearch://localhost:9200",
    retention_days=365
)

# Log security event
audit.log(
    event_type="security",
    details={
        "action": "key_rotation",
        "agent": "did:vireo:agent-1-abc123",
        "old_key": old_public[:16],
        "new_key": new_public[:16]
    }
)

# Query audit logs
events = audit.query(
    agent="did:vireo:agent-1-abc123",
    start_time="2026-09-01T00:00:00Z",
    end_time="2026-09-30T23:59:59Z"
)
print(f"Found {len(events)} events")
13.3 Audit Retention Policy
python
# retention_policy.yaml
retention:
  security_events: 1 year
  contract_events: 7 years
  key_rotation_events: 10 years
  audit_logs: 7 years
  access_logs: 90 days
14. Incident Response
14.1 Incident Response Plan
python
# Step 1: Detect incident
def detect_incident(event):
    if event['type'] == 'failed_authentication':
        return "Possible brute force attack"
    elif event['type'] == 'invalid_signature':
        return "Possible message tampering"
    elif event['type'] == 'rate_limit_exceeded':
        return "Possible DoS attack"
    return None

# Step 2: Respond
def respond_to_incident(incident_type):
    if incident_type == "Possible brute force attack":
        # Block IP
        block_ip(request.remote_addr)
        # Alert security team
        alert_security_team(incident_type)
    elif incident_type == "Possible message tampering":
        # Revoke key
        revoke_key(agent_id)
        # Log incident
        log_incident(incident_type)

# Step 3: Recover
def recover_from_incident(incident):
    # Rotate keys
    rotate_all_keys()
    # Reset trust
    reset_federated_trust()
    # Resume normal operations
    resume_operations()
14.2 Incident Response Template
yaml
incident_response:
  severity_levels:
    - level: "Critical"
      response_time: "15 minutes"
      actions:
        - "Isolate affected systems"
        - "Revoke compromised keys"
        - "Notify all agents"
    
    - level: "High"
      response_time: "1 hour"
      actions:
        - "Investigate incident"
        - "Rotate keys"
        - "Update firewall rules"
    
    - level: "Medium"
      response_time: "4 hours"
      actions:
        - "Log incident"
        - "Review audit trail"
        - "Update security controls"
    
    - level: "Low"
      response_time: "24 hours"
      actions:
        - "Document incident"
        - "Review lessons learned"
📚 Additional Resources
SECURITY.md — Security overview

PROTOCOL.md — Protocol specification

WIRE_FORMAT.md — Wire format

GOVERNANCE.md — Governance model

🔐 Quick Security Checklist
bash
# ✅ Verify DIDs
curl http://localhost:5000/api/v3/did/verify -d '{"did": "..."}'

# ✅ Check reputation
curl http://localhost:5000/api/v3/trust/reputation/did:vireo:agent-1

# ✅ Verify signatures
curl http://localhost:5000/api/v3/verify -d '{"contract_id": "..."}'

# ✅ Enable TLS
python api/server.py --tls cert.pem key.pem

# ✅ Configure rate limiting
export RATE_LIMIT="100/minute"

# ✅ Enable audit logging
export AUDIT_ENABLED=true
🌿 Vireo v3.0.0 — Security Guide