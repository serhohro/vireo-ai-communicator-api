package com.vireo;

import java.util.HashMap;
import java.util.Map;

/**
 * Vireo Error Classes
 */
public class Errors {

    public static class VireoException extends Exception {
        private final String code;
        private final Map<String, Object> details;

        public VireoException(String code, String message) {
            this(code, message, new HashMap<>());
        }

        public VireoException(String code, String message, Map<String, Object> details) {
            super(message);
            this.code = code;
            this.details = details != null ? details : new HashMap<>();
        }

        public String getCode() { return code; }
        public Map<String, Object> getDetails() { return details; }

        @Override
        public String toString() {
            return String.format("[%s] %s", code, getMessage());
        }
    }

    public static class ProtocolException extends VireoException {
        public ProtocolException(String message) {
            this(message, new HashMap<>());
        }
        public ProtocolException(String message, Map<String, Object> details) {
            super("VIREO_1000", message, details);
        }
    }

    public static class StateException extends VireoException {
        public StateException(String message, String currentState, String expectedState) {
            super("VIREO_1010", message, createDetails(currentState, expectedState));
        }
        private static Map<String, Object> createDetails(String current, String expected) {
            Map<String, Object> details = new HashMap<>();
            if (current != null) details.put("current_state", current);
            if (expected != null) details.put("expected_state", expected);
            return details;
        }
    }

    public static class VersionException extends VireoException {
        public VersionException(String message, String expected, String actual) {
            super("VIREO_1020", message, createDetails(expected, actual));
        }
        private static Map<String, Object> createDetails(String expected, String actual) {
            Map<String, Object> details = new HashMap<>();
            if (expected != null) details.put("expected", expected);
            if (actual != null) details.put("actual", actual);
            return details;
        }
    }

    public static class NonceException extends VireoException {
        public NonceException(String message, String nonce) {
            super("VIREO_1030", message, createDetails(nonce));
        }
        private static Map<String, Object> createDetails(String nonce) {
            Map<String, Object> details = new HashMap<>();
            if (nonce != null) details.put("nonce", nonce);
            return details;
        }
    }

    public static class MessageException extends VireoException {
        public MessageException(String message, String field, Object value) {
            super("VIREO_1040", message, createDetails(field, value));
        }
        private static Map<String, Object> createDetails(String field, Object value) {
            Map<String, Object> details = new HashMap<>();
            if (field != null) details.put("field", field);
            if (value != null) details.put("value", value);
            return details;
        }
    }

    public static class CryptoException extends VireoException {
        public CryptoException(String message) {
            this(message, new HashMap<>());
        }
        public CryptoException(String message, Map<String, Object> details) {
            super("VIREO_2000", message, details);
        }
    }

    public static class SignatureException extends CryptoException {
        public SignatureException(String message, String signer) {
            super(message, createDetails(signer));
        }
        private static Map<String, Object> createDetails(String signer) {
            Map<String, Object> details = new HashMap<>();
            if (signer != null) details.put("signer", signer);
            return details;
        }
    }

    public static class KeyException extends CryptoException {
        public KeyException(String message, String keyId) {
            super(message, createDetails(keyId));
        }
        private static Map<String, Object> createDetails(String keyId) {
            Map<String, Object> details = new HashMap<>();
            if (keyId != null) details.put("key_id", keyId);
            return details;
        }
    }

    public static class ValidationException extends VireoException {
        public ValidationException(String message, String path) {
            super("VIREO_3000", message, createDetails(path));
        }
        private static Map<String, Object> createDetails(String path) {
            Map<String, Object> details = new HashMap<>();
            if (path != null) details.put("path", path);
            return details;
        }
    }

    public static class SerializationException extends ValidationException {
        public SerializationException(String message, String path) {
            super(message, path);
        }
        @Override
        public String getCode() { return "VIREO_3010"; }
    }

    public static class IdentityException extends VireoException {
        public IdentityException(String message, String did) {
            super("VIREO_4000", message, createDetails(did));
        }
        private static Map<String, Object> createDetails(String did) {
            Map<String, Object> details = new HashMap<>();
            if (did != null) details.put("did", did);
            return details;
        }
    }

    public static class TrustException extends IdentityException {
        public TrustException(String message, String did) {
            super(message, did);
        }
        @Override
        public String getCode() { return "VIREO_4010"; }
    }

    public static class SandboxException extends VireoException {
        public SandboxException(String message) {
            this(message, new HashMap<>());
        }
        public SandboxException(String message, Map<String, Object> details) {
            super("VIREO_5000", message, details);
        }
    }

    public static class ConfigException extends VireoException {
        public ConfigException(String message, String key) {
            super("VIREO_6000", message, createDetails(key));
        }
        private static Map<String, Object> createDetails(String key) {
            Map<String, Object> details = new HashMap<>();
            if (key != null) details.put("key", key);
            return details;
        }
    }

    public static class NotFoundException extends VireoException {
        public NotFoundException(String message, String resourceType) {
            super("VIREO_7000", message, createDetails(resourceType));
        }
        private static Map<String, Object> createDetails(String resourceType) {
            Map<String, Object> details = new HashMap<>();
            if (resourceType != null) details.put("resource_type", resourceType);
            return details;
        }
    }

    public static class PermissionException extends VireoException {
        public PermissionException(String message, String action) {
            super("VIREO_8000", message, createDetails(action));
        }
        private static Map<String, Object> createDetails(String action) {
            Map<String, Object> details = new HashMap<>();
            if (action != null) details.put("action", action);
            return details;
        }
    }

    public static class InternalException extends VireoException {
        public InternalException(String message) {
            super("VIREO_9000", message);
        }
    }
}