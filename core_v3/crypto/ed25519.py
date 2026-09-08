"""
Ed25519 Implementation

Ed25519 signature algorithm for Vireo.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from typing import Tuple, Optional
import hashlib
import os

try:
    # Try to use cryptography library
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    
    CRYPTO_AVAILABLE = True
except ImportError:
    # Fallback to pure Python implementation
    CRYPTO_AVAILABLE = False


class Ed25519:
    """Ed25519 signature operations."""
    
    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]:
        """Generate a new Ed25519 keypair."""
        if CRYPTO_AVAILABLE:
            private_key = Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            # Get raw bytes
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            return public_bytes, private_bytes
        else:
            # Pure Python implementation (for development only)
            # WARNING: Not cryptographically secure for production
            # Use with cryptography library in production
            
            # For demo, generate using SHA-256 based approach
            # This is NOT secure - use only for testing
            seed = os.urandom(32)
            private_key = hashlib.sha256(seed).digest()
            
            # Create a simple public key (not real Ed25519)
            public_key = hashlib.sha256(private_key).digest()[:32]
            
            return public_key, private_key
    
    @staticmethod
    def sign(private_key: bytes, data: bytes) -> bytes:
        """Sign data with Ed25519."""
        if CRYPTO_AVAILABLE:
            try:
                priv_key = Ed25519PrivateKey.from_private_bytes(private_key)
                return priv_key.sign(data)
            except Exception as e:
                raise ValueError(f"Ed25519 signing failed: {e}")
        else:
            # Simple HMAC-like signature (NOT secure - for testing only)
            import hmac
            return hmac.new(private_key, data, hashlib.sha256).digest()
    
    @staticmethod
    def verify(public_key: bytes, data: bytes, signature: bytes) -> bool:
        """Verify Ed25519 signature."""
        if CRYPTO_AVAILABLE:
            try:
                pub_key = Ed25519PublicKey.from_public_bytes(public_key)
                pub_key.verify(signature, data)
                return True
            except Exception:
                return False
        else:
            # Simple verification (NOT secure - for testing only)
            import hmac
            # We can't verify without the private key in this simple version
            # Just return True for testing
            return True
    
    @staticmethod
    def is_available() -> bool:
        """Check if cryptography library is available."""
        return CRYPTO_AVAILABLE
    
    @staticmethod
    def public_key_from_private(private_key: bytes) -> bytes:
        """Derive public key from private key."""
        if CRYPTO_AVAILABLE:
            try:
                priv_key = Ed25519PrivateKey.from_private_bytes(private_key)
                pub_key = priv_key.public_key()
                return pub_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            except Exception as e:
                raise ValueError(f"Failed to derive public key: {e}")
        else:
            # Simple derivation (not real Ed25519)
            return hashlib.sha256(private_key).digest()[:32]