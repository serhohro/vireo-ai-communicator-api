package vireo

import "fmt"

// ============================================================
// VIREO ERRORS
// ============================================================

type VireoError struct {
    Code    string                 `json:"code"`
    Message string                 `json:"message"`
    Details map[string]interface{} `json:"details"`
}

func (e *VireoError) Error() string {
    return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

func NewVireoError(code, message string, details map[string]interface{}) *VireoError {
    return &VireoError{
        Code:    code,
        Message: message,
        Details: details,
    }
}

// ============================================================
// SPECIFIC ERRORS
// ============================================================

func NewProtocolError(message string, details map[string]interface{}) *VireoError {
    return NewVireoError("VIREO_1000", message, details)
}

func NewStateError(message string, currentState, expectedState string) *VireoError {
    details := map[string]interface{}{}
    if currentState != "" {
        details["current_state"] = currentState
    }
    if expectedState != "" {
        details["expected_state"] = expectedState
    }
    return NewVireoError("VIREO_1010", message, details)
}

func NewVersionError(message, expected, actual string) *VireoError {
    details := map[string]interface{}{}
    if expected != "" {
        details["expected"] = expected
    }
    if actual != "" {
        details["actual"] = actual
    }
    return NewVireoError("VIREO_1020", message, details)
}

func NewNonceError(message, nonce string) *VireoError {
    details := map[string]interface{}{}
    if nonce != "" {
        details["nonce"] = nonce
    }
    return NewVireoError("VIREO_1030", message, details)
}

func NewMessageError(message, field string, value interface{}) *VireoError {
    details := map[string]interface{}{}
    if field != "" {
        details["field"] = field
    }
    if value != nil {
        details["value"] = value
    }
    return NewVireoError("VIREO_1040", message, details)
}

func NewCryptoError(message string, details map[string]interface{}) *VireoError {
    return NewVireoError("VIREO_2000", message, details)
}

func NewSignatureError(message, signer string) *VireoError {
    details := map[string]interface{}{}
    if signer != "" {
        details["signer"] = signer
    }
    return NewVireoError("VIREO_2010", message, details)
}

func NewKeyError(message, keyID string) *VireoError {
    details := map[string]interface{}{}
    if keyID != "" {
        details["key_id"] = keyID
    }
    return NewVireoError("VIREO_2020", message, details)
}

func NewValidationError(message, path string) *VireoError {
    details := map[string]interface{}{}
    if path != "" {
        details["path"] = path
    }
    return NewVireoError("VIREO_3000", message, details)
}

func NewSerializationError(message, path string) *VireoError {
    details := map[string]interface{}{}
    if path != "" {
        details["path"] = path
    }
    return NewVireoError("VIREO_3010", message, details)
}

func NewIdentityError(message, did string) *VireoError {
    details := map[string]interface{}{}
    if did != "" {
        details["did"] = did
    }
    return NewVireoError("VIREO_4000", message, details)
}

func NewTrustError(message, did string) *VireoError {
    details := map[string]interface{}{}
    if did != "" {
        details["did"] = did
    }
    return NewVireoError("VIREO_4010", message, details)
}

func NewSandboxError(message string, details map[string]interface{}) *VireoError {
    return NewVireoError("VIREO_5000", message, details)
}

func NewConfigError(message, key string) *VireoError {
    details := map[string]interface{}{}
    if key != "" {
        details["key"] = key
    }
    return NewVireoError("VIREO_6000", message, details)
}

func NewNotFoundError(message, resourceType string) *VireoError {
    details := map[string]interface{}{}
    if resourceType != "" {
        details["resource_type"] = resourceType
    }
    return NewVireoError("VIREO_7000", message, details)
}

func NewPermissionError(message, action string) *VireoError {
    details := map[string]interface{}{}
    if action != "" {
        details["action"] = action
    }
    return NewVireoError("VIREO_8000", message, details)
}

func NewInternalError(message string) *VireoError {
    return NewVireoError("VIREO_9000", message, nil)
}