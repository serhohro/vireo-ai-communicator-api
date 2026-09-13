# [file name]: src/crypto/ed25519.py
# ============================================================
# ED25519 CRYPTOGRAPHY
# ============================================================
"""
Ed25519 cryptographic operations for Vireo.

Provides:
- Key pair generation
- Signing and verification
- Serialization/deserialization
"""

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization
import base64
import hashlib
import logging
from typing import Tuple, Optional

logger = logging.getLogger("vireo.crypto.ed25519")


class Ed25519Crypto:
    """Ed25519 криптографічні операції."""
    
    @staticmethod
    def generate_key_pair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        """
        Генерує пару ключів.
        
        Returns:
            Tuple[Ed25519PrivateKey, Ed25519PublicKey]: (private_key, public_key)
        """
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        logger.info("✅ Ed25519 key pair generated")
        return private_key, public_key
    
    @staticmethod
    def sign(private_key: Ed25519PrivateKey, data: bytes) -> bytes:
        """
        Підписує дані.
        
        Args:
            private_key: Приватний ключ
            data: Дані для підпису
            
        Returns:
            bytes: Підпис
        """
        return private_key.sign(data)
    
    @staticmethod
    def verify(public_key: Ed25519PublicKey, signature: bytes, data: bytes) -> bool:
        """
        Перевіряє підпис.
        
        Args:
            public_key: Публічний ключ
            signature: Підпис
            data: Дані для перевірки
            
        Returns:
            bool: True якщо підпис валідний
        """
        try:
            public_key.verify(signature, data)
            return True
        except Exception as e:
            logger.warning(f"❌ Signature verification failed: {e}")
            return False
    
    @staticmethod
    def serialize_private_key(private_key: Ed25519PrivateKey) -> str:
        """Серіалізує приватний ключ в PEM."""
        return base64.b64encode(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        ).decode()
    
    @staticmethod
    def serialize_public_key(public_key: Ed25519PublicKey) -> str:
        """Серіалізує публічний ключ в PEM."""
        return base64.b64encode(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        ).decode()
    
    @staticmethod
    def deserialize_private_key(data: str) -> Ed25519PrivateKey:
        """Десеріалізує приватний ключ з PEM."""
        return serialization.load_pem_private_key(
            base64.b64decode(data),
            password=None
        )
    
    @staticmethod
    def deserialize_public_key(data: str) -> Ed25519PublicKey:
        """Десеріалізує публічний ключ з PEM."""
        return serialization.load_pem_public_key(
            base64.b64decode(data)
        )
    
    @staticmethod
    def hash_data(data: bytes) -> str:
        """Обчислює SHA-256 хеш даних."""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sign_message(private_key: Ed25519PrivateKey, message: str) -> str:
        """Підписує текстове повідомлення."""
        signature = Ed25519Crypto.sign(private_key, message.encode())
        return base64.b64encode(signature).decode()
    
    @staticmethod
    def verify_message(public_key: Ed25519PublicKey, message: str, signature: str) -> bool:
        """Перевіряє підпис текстового повідомлення."""
        sig_bytes = base64.b64decode(signature)
        return Ed25519Crypto.verify(public_key, sig_bytes, message.encode())


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Генерація ключів
    private_key, public_key = Ed25519Crypto.generate_key_pair()
    
    # Підпис повідомлення
    message = "Hello, Vireo!"
    signature = Ed25519Crypto.sign_message(private_key, message)
    
    print(f"📝 Message: {message}")
    print(f"🔑 Signature: {signature[:32]}...")
    
    # Перевірка підпису
    is_valid = Ed25519Crypto.verify_message(public_key, message, signature)
    print(f"✅ Signature valid: {is_valid}")