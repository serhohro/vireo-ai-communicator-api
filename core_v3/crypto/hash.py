"""
Hash Utilities

Hash functions and utilities for Vireo.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from enum import Enum
from typing import Union, Optional, Dict, Any

from .blake2b import BLAKE2b
from ..errors import VireoCryptoError


class HashAlgorithm(Enum):
    """Supported hash algorithms."""
    BLAKE2B = "blake2b"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    KECCAK256 = "keccak256"
    
    @classmethod
    def from_string(cls, value: str) -> HashAlgorithm:
        try:
            return cls(value.lower())
        except ValueError:
            raise VireoCryptoError(f"Unsupported hash algorithm: {value}")


class Hash:
    """Hash utilities."""
    
    @staticmethod
    def compute(
        data: bytes,
        algorithm: Union[str, HashAlgorithm] = HashAlgorithm.BLAKE2B,
        **kwargs
    ) -> bytes:
        """Compute hash using specified algorithm."""
        if isinstance(algorithm, str):
            algorithm = HashAlgorithm.from_string(algorithm)
        
        if algorithm == HashAlgorithm.BLAKE2B:
            digest_size = kwargs.get('digest_size', BLAKE2b.DEFAULT_DIGEST_SIZE)
            return BLAKE2b.hash(data, digest_size)
        elif algorithm == HashAlgorithm.SHA256:
            import hashlib
            return hashlib.sha256(data).digest()
        elif algorithm == HashAlgorithm.SHA384:
            import hashlib
            return hashlib.sha384(data).digest()
        elif algorithm == HashAlgorithm.SHA512:
            import hashlib
            return hashlib.sha512(data).digest()
        elif algorithm == HashAlgorithm.KECCAK256:
            try:
                from Crypto.Hash import keccak
                keccak_hash = keccak.new(digest_bits=256, data=data)
                return keccak_hash.digest()
            except ImportError:
                # Fallback to SHA3-256
                import hashlib
                return hashlib.sha3_256(data).digest()
        else:
            raise VireoCryptoError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def hexdigest(data: bytes, algorithm: Union[str, HashAlgorithm] = HashAlgorithm.BLAKE2B, **kwargs) -> str:
        """Compute hash as hex string."""
        return Hash.compute(data, algorithm, **kwargs).hex()
    
    @staticmethod
    def compute_object(data: bytes) -> bytes:
        """Compute hash using BLAKE2b (default)."""
        return Hash.compute(data)
    
    @staticmethod
    def compute_digest(data: bytes) -> bytes:
        """Compute BLAKE2b hash (default)."""
        return Hash.compute(data)
    
    @staticmethod
    def compute_hex(data: bytes) -> str:
        """Compute BLAKE2b hash as hex string."""
        return Hash.hexdigest(data)
    
    @staticmethod
    def derive_id(data: bytes, prefix: str = "", length: int = 16) -> str:
        """Derive an ID from data."""
        hash_bytes = Hash.compute(data)
        return f"{prefix}{hash_bytes[:length].hex()}"
    
    @staticmethod
    def is_valid_hash(hex_string: str, algorithm: Union[str, HashAlgorithm] = HashAlgorithm.BLAKE2B) -> bool:
        """Check if a string is a valid hash hex string."""
        try:
            bytes.fromhex(hex_string)
            return True
        except ValueError:
            return False