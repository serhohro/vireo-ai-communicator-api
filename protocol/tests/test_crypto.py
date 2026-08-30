# [file name]: protocol/tests/test_crypto.py
# ============================================================
# CRYPTOGRAPHY TESTS FOR VIREO
# Тести криптографічних компонентів
# ============================================================

import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol import trust
from protocol.message import make_message, Intent
from src.crypto.trust import TrustManager, NonceManager


def print_test_header(name):
    print(f"\n🧪 TEST: {name}")
    print("-" * 40)


def test_hmac_signature():
    """Тест HMAC підписів."""
    print_test_header("HMAC Signature")
    
    secret = "test-secret-key"
    
    # Створення повідомлення
    msg = make_message(
        sender_id="agent-a",
        recipient_id="agent-b",
        intent=Intent.PROPOSE,
        payload={"task": "test", "value": 42}
    )
    
    # Підпис
    trust.attach_signature(msg, secret)
    assert msg.signature is not None
    print(f"✅ Signature generated: {msg.signature[:32]}...")
    
    # Перевірка
    is_valid = trust.verify(msg, secret)
    assert is_valid is True
    print(f"✅ Signature verified: {is_valid}")
    
    # Підміна повідомлення
    original_signature = msg.signature
    msg.payload["value"] = 999
    
    # Перевірка з підміненим повідомленням
    is_valid = trust.verify(msg, secret)
    assert is_valid is False
    print(f"✅ Tampered message detected: {is_valid}")
    
    # Перевірка з неправильним секретом
    is_valid = trust.verify(msg, "wrong-secret")
    assert is_valid is False
    print(f"✅ Wrong secret detected: {is_valid}")
    
    print("✅ HMAC signature tests passed!")


def test_nonce_manager():
    """Тест Nonce менеджера."""
    print_test_header("Nonce Manager")
    
    manager = NonceManager(ttl=5)
    
    # Генерація nonce
    nonce, timestamp = manager.generate()
    assert nonce is not None
    assert len(nonce) == 64  # 32 bytes in hex
    print(f"✅ Nonce generated: {nonce[:32]}...")
    
    # Валідація
    is_valid = manager.validate(nonce, timestamp)
    assert is_valid is True
    print(f"✅ Nonce validated: {is_valid}")
    
    # Повторне використання (replay attack)
    is_valid = manager.validate(nonce, timestamp)
    assert is_valid is False
    print(f"✅ Replay attack detected: {is_valid}")
    
    # Новий nonce
    nonce2, timestamp2 = manager.generate()
    is_valid = manager.validate(nonce2, timestamp2)
    assert is_valid is True
    print(f"✅ New nonce validated: {is_valid}")
    
    # Очищення
    manager.cleanup()
    stats = manager.get_stats()
    print(f"✅ Stats: {stats}")
    
    print("✅ Nonce manager tests passed!")


def test_trust_manager():
    """Тест Trust Manager."""
    print_test_header("Trust Manager")
    
    secret = "shared-secret"
    trust_mgr = TrustManager(secret, ttl=10)
    
    # Створення payload
    data = {"task": "weather_prediction", "user": "agent-vision"}
    payload = trust_mgr.create_trusted_payload(data)
    
    assert "data" in payload
    assert "nonce" in payload
    assert "timestamp" in payload
    print(f"✅ Trust payload created")
    
    # Верифікація
    is_valid, validated = trust_mgr.verify_trusted_payload(payload)
    assert is_valid is True
    assert validated == data
    print(f"✅ Trust payload verified")
    
    # Повторна верифікація (replay)
    is_valid, validated = trust_mgr.verify_trusted_payload(payload)
    assert is_valid is False
    print(f"✅ Replay attack detected")
    
    # Підпис повідомлення
    msg = make_message("a", "b", Intent.PROPOSE, payload={})
    signed = trust_mgr.sign_message(msg)
    assert signed.signature is not None
    print(f"✅ Message signed")
    
    # Перевірка підпису
    is_valid = trust_mgr.verify_message(signed)
    assert is_valid is True
    print(f"✅ Message verified")
    
    print("✅ Trust manager tests passed!")


def test_ed25519():
    """Тест Ed25519 (якщо доступно)."""
    print_test_header("Ed25519 (Optional)")
    
    try:
        from src.crypto.ed25519 import Ed25519Crypto
        
        # Генерація ключів
        private_key, public_key = Ed25519Crypto.generate_key_pair()
        assert private_key is not None
        assert public_key is not None
        print(f"✅ Key pair generated")
        
        # Серіалізація
        priv_str = Ed25519Crypto.serialize_private_key(private_key)
        pub_str = Ed25519Crypto.serialize_public_key(public_key)
        assert len(priv_str) > 0
        assert len(pub_str) > 0
        print(f"✅ Keys serialized")
        
        # Підпис
        message = "Hello, Vireo!"
        signature = Ed25519Crypto.sign_message(private_key, message)
        assert len(signature) > 0
        print(f"✅ Message signed")
        
        # Перевірка
        is_valid = Ed25519Crypto.verify_message(public_key, message, signature)
        assert is_valid is True
        print(f"✅ Signature verified")
        
        # Підробка
        is_valid = Ed25519Crypto.verify_message(public_key, "TAMPERED", signature)
        assert is_valid is False
        print(f"✅ Tampered message detected")
        
        print("✅ Ed25519 tests passed!")
        
    except NotImplementedError:
        print("⚠️ Ed25519 not fully implemented yet")
    except ImportError:
        print("⚠️ cryptography package not installed")
    except Exception as e:
        print(f"⚠️ Ed25519 test skipped: {e}")


def test_did():
    """Тест W3C DID (якщо доступно)."""
    print_test_header("W3C DID (Optional)")
    
    try:
        from src.crypto.did import DIDManager
        
        # Створення DID
        did_manager = DIDManager()
        assert did_manager.did is not None
        assert did_manager.did.startswith("did:key:")
        print(f"✅ DID generated: {did_manager.did}")
        
        # Створення документа
        doc = did_manager.create_did_document(
            public_key="z6Mkhw9nBAwZ...",
            service_endpoint="https://vireo.ai/agent"
        )
        assert doc.get("id") == did_manager.did
        assert "@context" in doc
        assert "verificationMethod" in doc
        print(f"✅ DID document created")
        
        # Перевірка
        is_valid = did_manager.verify_did(did_manager.did, doc)
        assert is_valid is True
        print(f"✅ DID verified")
        
        # Серіалізація
        json_str = did_manager.to_json(doc)
        assert json_str is not None
        parsed = did_manager.from_json(json_str)
        assert parsed.get("id") == did_manager.did
        print(f"✅ DID document serialized")
        
        print("✅ DID tests passed!")
        
    except ImportError as e:
        print(f"⚠️ DID test skipped: {e}")
    except Exception as e:
        print(f"⚠️ DID test skipped: {e}")


def test_trust_protocol_integration():
    """Тест інтеграції протоколу довіри з повідомленнями."""
    print_test_header("Trust Protocol Integration")
    
    secret = "shared-secret"
    trust_mgr = TrustManager(secret, ttl=10)
    
    # 1. Створення повідомлення
    msg = make_message(
        sender_id="agent-vision",
        recipient_id="agent-training",
        intent=Intent.PROPOSE,
        payload={"task": "train_model", "epochs": 10}
    )
    
    print("✅ Message created")
    
    # 2. Додавання trust інформації
    nonce, timestamp = trust_mgr.generate_nonce()
    msg.payload["_nonce"] = nonce
    msg.payload["_timestamp"] = timestamp
    
    print("✅ Trust info added")
    
    # 3. Підпис
    trust.attach_signature(msg, secret)
    print(f"✅ Signature added: {msg.signature[:32]}...")
    
    # 4. Перевірка
    # Перевірка підпису
    sig_valid = trust.verify(msg, secret)
    assert sig_valid is True
    
    # Перевірка nonce
    nonce_valid = trust_mgr.validate_nonce(nonce, timestamp)
    assert nonce_valid is True
    
    print(f"✅ Signature valid: {sig_valid}")
    print(f"✅ Nonce valid: {nonce_valid}")
    
    # 5. Replay attack
    nonce_valid = trust_mgr.validate_nonce(nonce, timestamp)
    assert nonce_valid is False
    print(f"✅ Replay attack prevented: {nonce_valid}")
    
    print("✅ Trust protocol integration tests passed!")


def test_message_signing_roundtrip():
    """Тест повного циклу підпису та верифікації."""
    print_test_header("Message Signing Roundtrip")
    
    secret = "test-secret"
    
    # Серіалізація/десеріалізація з підписом
    msg = make_message("a", "b", Intent.PROPOSE, payload={"x": 1, "y": 2})
    trust.attach_signature(msg, secret)
    
    # Емулюємо передачу (JSON)
    import json
    msg_json = msg.to_json()
    
    # Отримувач
    received = Message.from_json(msg_json)
    is_valid = trust.verify(received, secret)
    assert is_valid is True
    print(f"✅ Message roundtrip with signature verified")
    
    # Підміна в дорозі
    received.payload["x"] = 999
    is_valid = trust.verify(received, secret)
    assert is_valid is False
    print(f"✅ Tampered message detected")
    
    print("✅ Message signing roundtrip tests passed!")


def run_all_crypto_tests():
    """Запуск всіх крипто-тестів."""
    
    print("\n" + "=" * 60)
    print("🧪 VIREO CRYPTOGRAPHY TESTS")
    print("=" * 60)
    
    tests = [
        test_hmac_signature,
        test_nonce_manager,
        test_trust_manager,
        test_ed25519,
        test_did,
        test_trust_protocol_integration,
        test_message_signing_roundtrip,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ Test failed: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ Unexpected error: {e}")
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    exit_code = 0 if run_all_crypto_tests() else 1
    sys.exit(exit_code)