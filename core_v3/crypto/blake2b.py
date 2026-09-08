"""
BLAKE2b Implementation

BLAKE2b hash function for Vireo.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

import hashlib
from typing import Optional


class BLAKE2b:
    """BLAKE2b hash operations."""
    
    DEFAULT_DIGEST_SIZE = 32
    MAX_DIGEST_SIZE = 64
    
    @staticmethod
    def hash(data: bytes, digest_size: int = DEFAULT_DIGEST_SIZE) -> bytes:
        """Compute BLAKE2b hash."""
        if digest_size < 1 or digest_size > BLAKE2b.MAX_DIGEST_SIZE:
            raise ValueError(f"Digest size must be between 1 and {BLAKE2b.MAX_DIGEST_SIZE}")
        
        try:
            # Try blake2b from hashlib (Python 3.6+)
            return hashlib.blake2b(data, digest_size=digest_size).digest()
        except AttributeError:
            # Fallback: use SHA-256 (not ideal but works for compatibility)
            # In production, use a proper blake2b implementation
            return hashlib.sha256(data).digest()[:digest_size]
    
    @staticmethod
    def hexdigest(data: bytes, digest_size: int = DEFAULT_DIGEST_SIZE) -> str:
        """Compute BLAKE2b hash as hex string."""
        return BLAKE2b.hash(data, digest_size).hex()
    
    @staticmethod
    def is_available() -> bool:
        """Check if blake2b is available."""
        return hasattr(hashlib, 'blake2b')
    
    @staticmethod
    def hash_object(digest_size: int = DEFAULT_DIGEST_SIZE):
        """Create a BLAKE2b hash object for streaming."""
        if hasattr(hashlib, 'blake2b'):
            return hashlib.blake2b(digest_size=digest_size)
        else:
            # Fallback to SHA-256
            return hashlib.sha256()
    
    @staticmethod
    def hash_file(path: str, digest_size: int = DEFAULT_DIGEST_SIZE) -> bytes:
        """Compute BLAKE2b hash of a file."""
        hasher = BLAKE2b.hash_object(digest_size)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.digest()