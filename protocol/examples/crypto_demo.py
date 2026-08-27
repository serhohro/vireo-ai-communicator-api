# [file name]: protocol/examples/crypto_demo.py
# ============================================================
# CRYPTOGRAPHY DEMO
# Демонстрація криптографічних можливостей Vireo
# ============================================================

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol import trust
from protocol.message import Message, make_message, Intent
from src.crypto.ed25519 import Ed25519Crypto
from src.crypto.did import DIDManager
from src.crypto.trust import TrustManager

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("vireo.crypto_demo")


def print_separator():
    print("\n" + "=" * 60)


def hmac_demo():
    """Демонстрація HMAC підписів."""
    
    print_separator()
    print("🔐 HMAC SIGNATURE DEMO")
    print("   Symmetric key signing")
    print("=" * 60)
    
    secret = "my-shared-secret-key"
    
    # Створюємо повідомлення
    msg = make_message(
        sender_id="agent-vision",
        recipient_id="agent-training",
        intent=Intent.PROPOSE,
        payload={"dsl": "vireo", "code": "model MNIST { layer Dense(784, 128) }"}
    )
    
    print(f"\n📝 Original message:")
    print(f"   Sender: {msg.sender.id}")
    print(f"   Recipient: {msg.recipient.id}")
    print(f"   Intent: {msg.intent.value}")
    print(f"   Payload: {msg.payload}")
    print(f"   Signature: {msg.signature or 'None'}")
    
    # Підписуємо
    trust.attach_signature(msg, secret)
    print(f"\n🔑 Signed message:")
    print(f"   Signature: {msg.signature[:32]}...")
    
    # Перевіряємо
    is_valid = trust.verify(msg, secret)
    print(f"\n✅ Signature valid: {is_valid}")
    
    # Підміна повідомлення
    msg.payload["code"] = "model HACKED { ... }"
    is_valid = trust.verify(msg, secret)
    print(f"\n⚠️ After tampering, signature valid: {is_valid}")


def ed25519_demo():
    """Демонстрація Ed25519 підписів."""
    
    print_separator()
    print("🔐 ED25519 SIGNATURE DEMO")
    print("   Asymmetric key signing")
    print("=" * 60)
    
    try:
        # Генерація ключів
        private_key, public_key = Ed25519Crypto.generate_key_pair()
        print(f"\n🔑 Key pair generated:")
        print(f"   Private key: {Ed25519Crypto.serialize_private_key(private_key)[:32]}...")
        print(f"   Public key: {Ed25519Crypto.serialize_public_key(public_key)[:32]}...")
        
        # Підпис повідомлення
        message = "Hello, Vireo! This is a secure message."
        signature = Ed25519Crypto.sign_message(private_key, message)
        print(f"\n📝 Message: {message}")
        print(f"🔑 Signature: {signature[:32]}...")
        
        # Перевірка підпису
        is_valid = Ed25519Crypto.verify_message(public_key, message, signature)
        print(f"\n✅ Signature valid: {is_valid}")
        
        # Підроблене повідомлення
        tampered = "Hello, Vireo! This is a TAMPERED message."
        is_valid = Ed25519Crypto.verify_message(public_key, tampered, signature)
        print(f"\n⚠️ Tampered message valid: {is_valid}")
        
    except NotImplementedError:
        print("⚠️ Ed25519 support coming soon")
        print("   Install: cryptography>=41.0.0")


def did_demo():
    """Демонстрація W3C DID."""
    
    print_separator()
    print("🔐 W3C DID DEMO")
    print("   Decentralized Identifiers")
    print("=" * 60)
    
    try:
        # Створення DID
        did_manager = DIDManager()
        print(f"\n🔑 DID generated: {did_manager.did}")
        
        # Створення DID документа
        public_key = "z6Mkhw9nBAwZ..."
        doc = did_manager.create_did_document(public_key, "https://vireo.ai/agent")
        print(f"\n📄 DID Document:")
        print(json.dumps(doc, indent=2))
        
        # Перевірка
        is_valid = did_manager.verify_did(did_manager.did, doc)
        print(f"\n✅ DID valid: {is_valid}")
        
    except Exception as e:
        print(f"⚠️ DID demo error: {e}")


def nonce_demo():
    """Демонстрація захисту від replay attacks."""
    
    print_separator()
    print("🔐 NONCE REPLAY PROTECTION")
    print("   Prevent replay attacks")
    print("=" * 60)
    
    trust_manager = TrustManager(ttl=10)
    
    # Створення payload
    data = {"task": "weather_prediction", "user": "agent-vision"}
    payload = trust_manager.create_trusted_payload(data)
    
    print(f"\n📦 Payload created:")
    print(f"   Data: {payload['data']}")
    print(f"   Nonce: {payload['nonce'][:32]}...")
    print(f"   Timestamp: {payload['timestamp']}")
    
    # Перша перевірка (валідна)
    is_valid, validated = trust_manager.verify_trusted_payload(payload)
    print(f"\n✅ First validation: {is_valid}")
    
    # Друга перевірка (replay attack)
    is_valid, validated = trust_manager.verify_trusted_payload(payload)
    print(f"⚠️ Second validation (replay): {is_valid} (should be False)")
    
    # Створення нового payload
    new_payload = trust_manager.create_trusted_payload({"task": "new_task"})
    is_valid, validated = trust_manager.verify_trusted_payload(new_payload)
    print(f"\n✅ New payload validation: {is_valid}")


def trust_protocol_demo():
    """Демонстрація повного протоколу довіри."""
    
    print_separator()
    print("🔐 FULL TRUST PROTOCOL DEMO")
    print("   HMAC + Nonce + Verification")
    print("=" * 60)
    
    secret = "shared-secret"
    trust_manager = TrustManager(secret, ttl=30)
    
    # 1. Створення повідомлення
    msg = make_message(
        sender_id="agent-vision",
        recipient_id="agent-training",
        intent=Intent.PROPOSE,
        payload={"task": "train_model", "epochs": 10}
    )
    
    print(f"\n📝 Original message:")
    print(f"   {msg.sender.id} → {msg.recipient.id}")
    print(f"   Intent: {msg.intent.value}")
    print(f"   Payload: {msg.payload}")
    
    # 2. Додаємо trust інформацію
    nonce, timestamp = trust_manager.generate_nonce()
    msg.payload["_nonce"] = nonce
    msg.payload["_timestamp"] = timestamp
    
    # 3. Підписуємо
    trust.attach_signature(msg, secret)
    print(f"\n🔑 Signed and protected:")
    print(f"   Nonce: {nonce[:32]}...")
    print(f"   Signature: {msg.signature[:32]}...")
    
    # 4. Перевіряємо на стороні отримувача
    print(f"\n✅ Verifying on recipient side...")
    
    # Перевіряємо підпис
    sig_valid = trust.verify(msg, secret)
    print(f"   Signature valid: {sig_valid}")
    
    # Перевіряємо nonce
    nonce_valid = trust_manager.validate_nonce(nonce, timestamp)
    print(f"   Nonce valid: {nonce_valid}")
    
    # 5. Підсумок
    print(f"\n📊 Security status: {'✅ SECURE' if sig_valid and nonce_valid else '⚠️ INSECURE'}")


def main():
    """Головна функція."""
    
    print("\n" + "=" * 60)
    print("🌿 VIREO CRYPTOGRAPHY DEMO")
    print("   Security and Trust Layer")
    print("=" * 60)
    
    print("\nSelect demo:")
    print("  1. HMAC Signatures (symmetric)")
    print("  2. Ed25519 Signatures (asymmetric)")
    print("  3. W3C DID (Decentralized Identifiers)")
    print("  4. Nonce Replay Protection")
    print("  5. Full Trust Protocol")
    print("  6. All demos")
    
    choice = input("\n👉 Choice [1-6]: ").strip() or "1"
    
    if choice == "1":
        hmac_demo()
    elif choice == "2":
        ed25519_demo()
    elif choice == "3":
        did_demo()
    elif choice == "4":
        nonce_demo()
    elif choice == "5":
        trust_protocol_demo()
    elif choice == "6":
        hmac_demo()
        ed25519_demo()
        did_demo()
        nonce_demo()
        trust_protocol_demo()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()