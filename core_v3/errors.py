"""
Vireo Error Definitions

Comprehensive error hierarchy for Vireo core.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from typing import Optional, Any, Dict, List


class VireoError(Exception):
    """Base exception for all Vireo errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or "VIREO_0000"
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class VireoProtocolError(VireoError):
    """Protocol-related errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        code = code or "VIREO_1000"
        super().__init__(message, code, details)


class VireoStateError(VireoProtocolError):
    """State machine errors."""
    
    def __init__(self, message: str, current_state: Optional[str] = None, expected_state: Optional[str] = None):
        details = {}
        if current_state:
            details["current_state"] = current_state
        if expected_state:
            details["expected_state"] = expected_state
        super().__init__(message, "VIREO_1010", details)


class VireoVersionError(VireoProtocolError):
    """Version mismatch errors."""
    
    def __init__(self, message: str, expected: Optional[str] = None, actual: Optional[str] = None):
        details = {}
        if expected:
            details["expected"] = expected
        if actual:
            details["actual"] = actual
        super().__init__(message, "VIREO_1020", details)


class VireoNonceError(VireoProtocolError):
    """Nonce validation errors."""
    
    def __init__(self, message: str, nonce: Optional[str] = None):
        details = {"nonce": nonce} if nonce else {}
        super().__init__(message, "VIREO_1030", details)


class VireoMessageError(VireoProtocolError):
    """Message validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = str(value)
        super().__init__(message, "VIREO_1040", details)


class VireoCryptoError(VireoError):
    """Cryptographic errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        code = code or "VIREO_2000"
        super().__init__(message, code, details)


class VireoSignatureError(VireoCryptoError):
    """Signature verification errors."""
    
    def __init__(self, message: str, signer: Optional[str] = None):
        details = {"signer": signer} if signer else {}
        super().__init__(message, "VIREO_2010", details)


class VireoKeyError(VireoCryptoError):
    """Key management errors."""
    
    def __init__(self, message: str, key_id: Optional[str] = None):
        details = {"key_id": key_id} if key_id else {}
        super().__init__(message, "VIREO_2020", details)


class VireoValidationError(VireoError):
    """Validation errors."""
    
    def __init__(self, message: str, path: Optional[str] = None, code: Optional[str] = None):
        details = {"path": path} if path else {}
        code = code or "VIREO_3000"
        super().__init__(message, code, details)


class VireoSerializationError(VireoValidationError):
    """Serialization/deserialization errors."""
    
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(message, path, "VIREO_3010")


class VireoIdentityError(VireoError):
    """Identity management errors."""
    
    def __init__(self, message: str, did: Optional[str] = None):
        details = {"did": did} if did else {}
        super().__init__(message, "VIREO_4000", details)


class VireoTrustError(VireoIdentityError):
    """Trust bootstrap errors."""
    
    def __init__(self, message: str, did: Optional[str] = None):
        super().__init__(message, did)
        self.code = "VIREO_4010"


class VireoSandboxError(VireoError):
    """Sandbox execution errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        code = code or "VIREO_5000"
        super().__init__(message, code, details)


class VireoSandboxTimeout(VireoSandboxError):
    """Sandbox timeout errors."""
    
    def __init__(self, message: str, timeout: Optional[float] = None):
        details = {"timeout": timeout} if timeout else {}
        super().__init__(message, "VIREO_5010", details)


class VireoSandboxResourceError(VireoSandboxError):
    """Sandbox resource limit errors."""
    
    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(message, "VIREO_5020", details)


class VireoConfigError(VireoError):
    """Configuration errors."""
    
    def __init__(self, message: str, key: Optional[str] = None):
        details = {"key": key} if key else {}
        super().__init__(message, "VIREO_6000", details)


class VireoNotFoundError(VireoError):
    """Resource not found errors."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(message, "VIREO_7000", details)


class VireoPermissionError(VireoError):
    """Permission/authorization errors."""
    
    def __init__(self, message: str, action: Optional[str] = None):
        details = {"action": action} if action else {}
        super().__init__(message, "VIREO_8000", details)


class VireoInternalError(VireoError):
    """Internal implementation errors."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        code = code or "VIREO_9000"
        super().__init__(message, code)


# Error registry for error code lookup

ERROR_REGISTRY: Dict[str, type] = {
    "VIREO_0000": VireoError,
    "VIREO_1000": VireoProtocolError,
    "VIREO_1010": VireoStateError,
    "VIREO_1020": VireoVersionError,
    "VIREO_1030": VireoNonceError,
    "VIREO_1040": VireoMessageError,
    "VIREO_2000": VireoCryptoError,
    "VIREO_2010": VireoSignatureError,
    "VIREO_2020": VireoKeyError,
    "VIREO_3000": VireoValidationError,
    "VIREO_3010": VireoSerializationError,
    "VIREO_4000": VireoIdentityError,
    "VIREO_4010": VireoTrustError,
    "VIREO_5000": VireoSandboxError,
    "VIREO_5010": VireoSandboxTimeout,
    "VIREO_5020": VireoSandboxResourceError,
    "VIREO_6000": VireoConfigError,
    "VIREO_7000": VireoNotFoundError,
    "VIREO_8000": VireoPermissionError,
    "VIREO_9000": VireoInternalError,
}


def create_error(code: str, message: str, **kwargs) -> VireoError:
    """Factory function to create error from code."""
    error_class = ERROR_REGISTRY.get(code, VireoError)
    return error_class(message, code, kwargs) if 'details' in kwargs else error_class(message, code)