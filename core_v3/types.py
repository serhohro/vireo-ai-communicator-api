"""
Vireo Core Types

Type definitions for the Vireo language and protocol.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import uuid
import hashlib
from datetime import datetime, timedelta
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple, Set, Iterator
from decimal import Decimal
from pathlib import Path


class VireoType(Enum):
    """Vireo type system enumeration."""
    NULL = 0
    BOOLEAN = 1
    INTEGER = 2
    FLOAT = 3
    STRING = 4
    BINARY = 5
    ARRAY = 6
    OBJECT = 7
    TIMESTAMP = 8
    DURATION = 9
    URI = 10
    UUID = 11
    DID = 12
    SIGNATURE = 13
    PUBLIC_KEY = 14
    PRIVATE_KEY = 15
    HASH = 16
    NONCE = 17
    VERSION = 18
    CUSTOM = 99


class VireoValue:
    """Base class for all Vireo values."""
    
    def __init__(self, value: Any, type_: VireoType):
        self._value = value
        self._type = type_
    
    @property
    def value(self) -> Any:
        return self._value
    
    @property
    def type(self) -> VireoType:
        return self._type
    
    def __repr__(self) -> str:
        return f"VireoValue(type={self._type.name}, value={repr(self._value)})"
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VireoValue):
            return False
        return self._type == other._type and self._value == other._value
    
    def __hash__(self) -> int:
        return hash((self._type, self._value))


class VireoNull(VireoValue):
    """Null value."""
    
    def __init__(self):
        super().__init__(None, VireoType.NULL)
    
    def __repr__(self) -> str:
        return "VireoNull()"


class VireoBoolean(VireoValue):
    """Boolean value."""
    
    def __init__(self, value: bool):
        super().__init__(value, VireoType.BOOLEAN)
    
    @property
    def value(self) -> bool:
        return self._value
    
    def __repr__(self) -> str:
        return f"VireoBoolean({self._value})"


class VireoInteger(VireoValue):
    """Integer value (arbitrary precision)."""
    
    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value)}")
        super().__init__(value, VireoType.INTEGER)
    
    @property
    def value(self) -> int:
        return self._value
    
    def __repr__(self) -> str:
        return f"VireoInteger({self._value})"


class VireoFloat(VireoValue):
    """Float value (IEEE 754 double)."""
    
    def __init__(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected float, got {type(value)}")
        super().__init__(float(value), VireoType.FLOAT)
    
    @property
    def value(self) -> float:
        return self._value
    
    def __repr__(self) -> str:
        return f"VireoFloat({self._value})"


class VireoString(VireoValue):
    """String value (UTF-8, NFC normalized)."""
    
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value)}")
        # Normalize to NFC
        import unicodedata
        value = unicodedata.normalize('NFC', value)
        super().__init__(value, VireoType.STRING)
    
    @property
    def value(self) -> str:
        return self._value
    
    def __len__(self) -> int:
        return len(self._value)
    
    def __repr__(self) -> str:
        return f"VireoString({repr(self._value)})"


class VireoBinary(VireoValue):
    """Binary data."""
    
    def __init__(self, value: bytes):
        if not isinstance(value, bytes):
            raise TypeError(f"Expected bytes, got {type(value)}")
        super().__init__(value, VireoType.BINARY)
    
    @property
    def value(self) -> bytes:
        return self._value
    
    def __len__(self) -> int:
        return len(self._value)
    
    def hex(self) -> str:
        return self._value.hex()
    
    def __repr__(self) -> str:
        return f"VireoBinary({self.hex()[:20]}...)" if len(self._value) > 20 else f"VireoBinary({self.hex()})"


class VireoArray(VireoValue):
    """Array of Vireo values."""
    
    def __init__(self, values: Optional[List[VireoValue]] = None):
        if values is None:
            values = []
        if not isinstance(values, list):
            raise TypeError(f"Expected list, got {type(values)}")
        for v in values:
            if not isinstance(v, VireoValue):
                raise TypeError(f"Expected VireoValue, got {type(v)}")
        super().__init__(values, VireoType.ARRAY)
    
    @property
    def value(self) -> List[VireoValue]:
        return self._value
    
    def __len__(self) -> int:
        return len(self._value)
    
    def __getitem__(self, index: int) -> VireoValue:
        return self._value[index]
    
    def __iter__(self) -> Iterator[VireoValue]:
        return iter(self._value)
    
    def append(self, value: VireoValue) -> None:
        self._value.append(value)
    
    def __repr__(self) -> str:
        return f"VireoArray({self._value})"


class VireoObject(VireoValue):
    """Object with named fields."""
    
    def __init__(self, fields: Optional[Dict[str, VireoValue]] = None):
        if fields is None:
            fields = {}
        if not isinstance(fields, dict):
            raise TypeError(f"Expected dict, got {type(fields)}")
        for key, value in fields.items():
            if not isinstance(key, str):
                raise TypeError(f"Expected str key, got {type(key)}")
            if not isinstance(value, VireoValue):
                raise TypeError(f"Expected VireoValue, got {type(value)}")
        super().__init__(fields, VireoType.OBJECT)
    
    @property
    def value(self) -> Dict[str, VireoValue]:
        return self._value
    
    def __getitem__(self, key: str) -> VireoValue:
        return self._value[key]
    
    def __setitem__(self, key: str, value: VireoValue) -> None:
        if not isinstance(value, VireoValue):
            raise TypeError(f"Expected VireoValue, got {type(value)}")
        self._value[key] = value
    
    def get(self, key: str, default: Optional[VireoValue] = None) -> Optional[VireoValue]:
        return self._value.get(key, default)
    
    def keys(self) -> Set[str]:
        return set(self._value.keys())
    
    def __repr__(self) -> str:
        return f"VireoObject({self._value})"


class VireoTimestamp(VireoValue):
    """Timestamp with timezone information."""
    
    def __init__(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError(f"Expected datetime, got {type(value)}")
        if value.tzinfo is None:
            # Assume UTC
            value = value.replace(tzinfo=datetime.timezone.utc)
        super().__init__(value, VireoType.TIMESTAMP)
    
    @property
    def value(self) -> datetime:
        return self._value
    
    @classmethod
    def now(cls) -> VireoTimestamp:
        return cls(datetime.now(datetime.timezone.utc))
    
    @classmethod
    def from_iso(cls, iso_string: str) -> VireoTimestamp:
        dt = datetime.fromisoformat(iso_string)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return cls(dt)
    
    def isoformat(self) -> str:
        return self._value.isoformat()
    
    def to_unix(self) -> float:
        return self._value.timestamp()
    
    def __repr__(self) -> str:
        return f"VireoTimestamp({self.isoformat()})"


class VireoDuration(VireoValue):
    """Duration (time interval)."""
    
    def __init__(self, value: timedelta):
        if not isinstance(value, timedelta):
            raise TypeError(f"Expected timedelta, got {type(value)}")
        super().__init__(value, VireoType.DURATION)
    
    @property
    def value(self) -> timedelta:
        return self._value
    
    @classmethod
    def from_seconds(cls, seconds: float) -> VireoDuration:
        return cls(timedelta(seconds=seconds))
    
    @classmethod
    def from_milliseconds(cls, ms: float) -> VireoDuration:
        return cls(timedelta(milliseconds=ms))
    
    def total_seconds(self) -> float:
        return self._value.total_seconds()
    
    def __repr__(self) -> str:
        return f"VireoDuration({self.total_seconds()}s)"


class VireoURI(VireoValue):
    """URI/URL value."""
    
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value)}")
        # Basic URI validation
        if not any(value.startswith(scheme) for scheme in 
                  ['http://', 'https://', 'did:', 'urn:', 'mailto:', 'ftp://']):
            # Not strict validation - allow any string
            pass
        super().__init__(value, VireoType.URI)
    
    @property
    def value(self) -> str:
        return self._value
    
    @property
    def scheme(self) -> Optional[str]:
        if '://' in self._value:
            return self._value.split('://')[0]
        if ':' in self._value:
            return self._value.split(':')[0]
        return None
    
    def __repr__(self) -> str:
        return f"VireoURI({repr(self._value)})"


class VireoUUID(VireoValue):
    """UUID value."""
    
    def __init__(self, value: Union[str, uuid.UUID]):
        if isinstance(value, str):
            value = uuid.UUID(value)
        if not isinstance(value, uuid.UUID):
            raise TypeError(f"Expected UUID, got {type(value)}")
        super().__init__(value, VireoType.UUID)
    
    @property
    def value(self) -> uuid.UUID:
        return self._value
    
    @classmethod
    def random(cls) -> VireoUUID:
        return cls(uuid.uuid4())
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"VireoUUID({repr(str(self._value))})"


class VireoDID(VireoValue):
    """Decentralized Identifier (DID)."""
    
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value)}")
        # Basic DID validation: did:method:identifier
        if not value.startswith('did:'):
            raise ValueError(f"Invalid DID: {value} - must start with 'did:'")
        if len(value.split(':')) < 3:
            raise ValueError(f"Invalid DID: {value} - must have method and identifier")
        super().__init__(value, VireoType.DID)
    
    @property
    def value(self) -> str:
        return self._value
    
    @property
    def method(self) -> str:
        parts = self._value.split(':')
        return parts[1] if len(parts) >= 3 else ''
    
    @property
    def identifier(self) -> str:
        parts = self._value.split(':')
        return ':'.join(parts[2:]) if len(parts) >= 3 else ''
    
    @classmethod
    def from_components(cls, method: str, identifier: str) -> VireoDID:
        return cls(f"did:{method}:{identifier}")
    
    def __repr__(self) -> str:
        return f"VireoDID({repr(self._value)})"


class VireoSignature(VireoValue):
    """Cryptographic signature."""
    
    def __init__(self, value: bytes):
        if not isinstance(value, bytes):
            raise TypeError(f"Expected bytes, got {type(value)}")
        if len(value) not in [64, 128]:  # Ed25519: 64, ECDSA: 64, RSA: variable
            # Still allow other lengths but warn
            pass
        super().__init__(value, VireoType.SIGNATURE)
    
    @property
    def value(self) -> bytes:
        return self._value
    
    def hex(self) -> str:
        return self._value.hex()
    
    def __repr__(self) -> str:
        return f"VireoSignature({self.hex()[:20]}...)" if len(self._value) > 20 else f"VireoSignature({self.hex()})"


class VireoPublicKey(VireoValue):
    """Public key."""
    
    def __init__(self, value: bytes, algorithm: str = "Ed25519"):
        if not isinstance(value, bytes):
            raise TypeError(f"Expected bytes, got {type(value)}")
        self._algorithm = algorithm
        super().__init__(value, VireoType.PUBLIC_KEY)
    
    @property
    def value(self) -> bytes:
        return self._value
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
    
    def hex(self) -> str:
        return self._value.hex()
    
    def __repr__(self) -> str:
        return f"VireoPublicKey(algorithm={self._algorithm}, hex={self.hex()[:20]}...)"


class VireoPrivateKey(VireoValue):
    """Private key (never serialized)."""
    
    def __init__(self, value: bytes, algorithm: str = "Ed25519"):
        if not isinstance(value, bytes):
            raise TypeError(f"Expected bytes, got {type(value)}")
        self._algorithm = algorithm
        super().__init__(value, VireoType.PRIVATE_KEY)
    
    @property
    def value(self) -> bytes:
        return self._value
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
    
    def hex(self) -> str:
        return self._value.hex()
    
    def __repr__(self) -> str:
        return f"VireoPrivateKey(algorithm={self._algorithm}, <private>)" 


class VireoHash(VireoValue):
    """Cryptographic hash."""
    
    def __init__(self, value: bytes, algorithm: str = "BLAKE2b"):
        if not isinstance(value, bytes):
            raise TypeError(f"Expected bytes, got {type(value)}")
        self._algorithm = algorithm
        super().__init__(value, VireoType.HASH)
    
    @property
    def value(self) -> bytes:
        return self._value
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
    
    def hex(self) -> str:
        return self._value.hex()
    
    def __repr__(self) -> str:
        return f"VireoHash(algorithm={self._algorithm}, hex={self.hex()[:20]}...)"


class VireoNonce(VireoValue):
    """Nonce for replay protection."""
    
    def __init__(self, value: bytes):
        if not isinstance(value, bytes):
            raise TypeError(f"Expected bytes, got {type(value)}")
        if len(value) != 24:
            raise ValueError(f"Nonce must be 24 bytes, got {len(value)}")
        super().__init__(value, VireoType.NONCE)
    
    @property
    def value(self) -> bytes:
        return self._value
    
    def hex(self) -> str:
        return self._value.hex()
    
    @classmethod
    def random(cls) -> VireoNonce:
        import os
        return cls(os.urandom(24))
    
    def __repr__(self) -> str:
        return f"VireoNonce({self.hex()})"


class VireoVersion(VireoValue):
    """Version representation."""
    
    def __init__(self, major: int, minor: int, patch: int, prerelease: Optional[str] = None):
        self._major = major
        self._minor = minor
        self._patch = patch
        self._prerelease = prerelease
        super().__init__(self._to_string(), VireoType.VERSION)
    
    def _to_string(self) -> str:
        version = f"{self._major}.{self._minor}.{self._patch}"
        if self._prerelease:
            version += f"-{self._prerelease}"
        return version
    
    @property
    def value(self) -> str:
        return self._to_string()
    
    @property
    def major(self) -> int:
        return self._major
    
    @property
    def minor(self) -> int:
        return self._minor
    
    @property
    def patch(self) -> int:
        return self._patch
    
    @property
    def prerelease(self) -> Optional[str]:
        return self._prerelease
    
    @classmethod
    def parse(cls, version_str: str) -> VireoVersion:
        import re
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?$'
        match = re.match(pattern, version_str)
        if not match:
            raise ValueError(f"Invalid version string: {version_str}")
        major, minor, patch, prerelease = match.groups()
        return cls(int(major), int(minor), int(patch), prerelease)
    
    @classmethod
    def current(cls) -> VireoVersion:
        return cls(3, 0, 0)
    
    def __lt__(self, other: VireoVersion) -> bool:
        if self._major != other._major:
            return self._major < other._major
        if self._minor != other._minor:
            return self._minor < other._minor
        if self._patch != other._patch:
            return self._patch < other._patch
        # Prerelease handling (semver rules)
        if self._prerelease and not other._prerelease:
            return True
        if not self._prerelease and other._prerelease:
            return False
        if self._prerelease and other._prerelease:
            return self._prerelease < other._prerelease
        return False
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VireoVersion):
            return False
        return (self._major == other._major and 
                self._minor == other._minor and 
                self._patch == other._patch and
                self._prerelease == other._prerelease)
    
    def __repr__(self) -> str:
        return f"VireoVersion({self._to_string()})"


# Type conversion utilities

def to_vireo_value(value: Any) -> VireoValue:
    """Convert Python value to VireoValue."""
    if value is None:
        return VireoNull()
    elif isinstance(value, bool):
        return VireoBoolean(value)
    elif isinstance(value, int):
        return VireoInteger(value)
    elif isinstance(value, float):
        return VireoFloat(value)
    elif isinstance(value, str):
        return VireoString(value)
    elif isinstance(value, bytes):
        return VireoBinary(value)
    elif isinstance(value, datetime):
        return VireoTimestamp(value)
    elif isinstance(value, timedelta):
        return VireoDuration(value)
    elif isinstance(value, uuid.UUID):
        return VireoUUID(value)
    elif isinstance(value, list):
        return VireoArray([to_vireo_value(v) for v in value])
    elif isinstance(value, dict):
        return VireoObject({k: to_vireo_value(v) for k, v in value.items()})
    elif isinstance(value, VireoValue):
        return value
    else:
        raise TypeError(f"Cannot convert {type(value)} to VireoValue")


def from_vireo_value(value: VireoValue) -> Any:
    """Convert VireoValue to Python value."""
    if isinstance(value, VireoNull):
        return None
    elif isinstance(value, VireoBoolean):
        return value.value
    elif isinstance(value, VireoInteger):
        return value.value
    elif isinstance(value, VireoFloat):
        return value.value
    elif isinstance(value, VireoString):
        return value.value
    elif isinstance(value, VireoBinary):
        return value.value
    elif isinstance(value, VireoArray):
        return [from_vireo_value(v) for v in value.value]
    elif isinstance(value, VireoObject):
        return {k: from_vireo_value(v) for k, v in value.value.items()}
    elif isinstance(value, VireoTimestamp):
        return value.value
    elif isinstance(value, VireoDuration):
        return value.value
    elif isinstance(value, VireoURI):
        return value.value
    elif isinstance(value, VireoUUID):
        return value.value
    elif isinstance(value, VireoDID):
        return value.value
    elif isinstance(value, VireoSignature):
        return value.value
    elif isinstance(value, VireoPublicKey):
        return value.value
    elif isinstance(value, VireoPrivateKey):
        return value.value
    elif isinstance(value, VireoHash):
        return value.value
    elif isinstance(value, VireoNonce):
        return value.value
    elif isinstance(value, VireoVersion):
        return value.value
    else:
        raise TypeError(f"Cannot convert {type(value)} from VireoValue")