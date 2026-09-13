# tests/unit/test_crypto.py

import pytest
from core.crypto.ed25519 import Ed25519
from core.crypto.blake2b import Blake2b
from core.crypto.hash import hash_message

class TestCrypto:
    """Тести криптографічних функцій"""
    
    def test_ed25519_deterministic(self):
        """Детерміністична генерація ключів"""
        seed = b"test_seed_32_bytes_long_!!"
        key1 = Ed25519.generate_keypair_from_seed(seed)
        key2 = Ed25519.generate_keypair_from_seed(seed)
        assert key1[0] == key2[0]  # Приватні ключі однакові
        assert key1[1] == key2[1]  # Публічні ключі однакові
    
    def test_blake2b_with_key(self):
        """Blake2b з ключем"""
        data = b"test"
        key = b"secret_key"
        h1 = Blake2b.hash(data, key=key)
        h2 = Blake2b.hash(data, key=key)
        assert h1 == h2
    
    def test_blake2b_different_data(self):
        """Різні дані -> різні хеші"""
        h1 = Blake2b.hash(b"test1")
        h2 = Blake2b.hash(b"test2")
        assert h1 != h2
    
    def test_hash_message_canonical(self):
        """Канонічний хеш повідомлення"""
        msg1 = {"type": "COMMIT", "data": {"a": 1}}
        msg2 = {"type": "COMMIT", "data": {"a": 1}}
        h1 = hash_message(msg1)
        h2 = hash_message(msg2)
        assert h1 == h2
    
    def test_hash_message_different_order(self):
        """Різний порядок полів -> однаковий хеш"""
        # Канонічне сортування ключів
        msg1 = {"a": 1, "b": 2}
        msg2 = {"b": 2, "a": 1}
        h1 = hash_message(msg1)
        h2 = hash_message(msg2)
        assert h1 == h2