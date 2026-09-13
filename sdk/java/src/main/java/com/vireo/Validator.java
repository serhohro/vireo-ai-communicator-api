package com.vireo;

import java.time.Instant;
import java.util.*;

/**
 * Vireo Message Validator
 */
public class Validator {

    private final List<ValidationRule> rules = new ArrayList<>();

    public Validator() {
        // Add default rules
        rules.add(new MessageTypeRule());
        rules.add(new VersionRule("3.0.0", "3.0.9"));
        rules.add(new TTLRule());
    }

    public interface ValidationRule {
        String getName();
        Types.ValidationResult validate(Types.MessageEnvelope envelope);
    }

    public static class MessageTypeRule implements ValidationRule {
        private static final Set<Types.MessageType> ALLOWED_TYPES = EnumSet.of(
                Types.MessageType.PROPOSE,
                Types.MessageType.COMMIT,
                Types.MessageType.EXECUTE,
                Types.MessageType.VERIFY,
                Types.MessageType.ESCALATE,
                Types.MessageType.DONE,
                Types.MessageType.FAILED,
                Types.MessageType.ACK,
                Types.MessageType.NACK,
                Types.MessageType.QUERY,
                Types.MessageType.RESPONSE,
                Types.MessageType.ERROR
        );

        @Override
        public String getName() { return "MessageTypeRule"; }

        @Override
        public Types.ValidationResult validate(Types.MessageEnvelope envelope) {
            Types.ValidationResult result = new Types.ValidationResult();
            result.setValid(true);
            result.setErrors(new ArrayList<>());

            if (!ALLOWED_TYPES.contains(envelope.getHeader().getType())) {
                result.setValid(false);
                result.getErrors().add("Invalid message type: " + envelope.getHeader().getType());
            }

            return result;
        }
    }

    public static class VersionRule implements ValidationRule {
        private final String minVersion;
        private final String maxVersion;

        public VersionRule(String minVersion, String maxVersion) {
            this.minVersion = minVersion;
            this.maxVersion = maxVersion;
        }

        @Override
        public String getName() { return "VersionRule"; }

        @Override
        public Types.ValidationResult validate(Types.MessageEnvelope envelope) {
            Types.ValidationResult result = new Types.ValidationResult();
            result.setValid(true);
            result.setErrors(new ArrayList<>());

            String version = envelope.getHeader().getVersion();
            if (!versionGte(version, minVersion)) {
                result.setValid(false);
                result.getErrors().add("Version " + version + " is less than minimum " + minVersion);
            }
            if (maxVersion != null && !versionLte(version, maxVersion)) {
                result.setValid(false);
                result.getErrors().add("Version " + version + " is greater than maximum " + maxVersion);
            }

            return result;
        }

        private int[] parseVersion(String v) {
            String[] parts = v.replaceAll("[^0-9.]", "").split("\\.");
            int[] result = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                result[i] = Integer.parseInt(parts[i]);
            }
            return result;
        }

        private boolean versionGte(String v1, String v2) {
            int[] p1 = parseVersion(v1);
            int[] p2 = parseVersion(v2);
            for (int i = 0; i < Math.max(p1.length, p2.length); i++) {
                int n1 = i < p1.length ? p1[i] : 0;
                int n2 = i < p2.length ? p2[i] : 0;
                if (n1 < n2) return false;
                if (n1 > n2) return true;
            }
            return true;
        }

        private boolean versionLte(String v1, String v2) {
            return versionGte(v2, v1);
        }
    }

    public static class TTLRule implements ValidationRule {
        @Override
        public String getName() { return "TTLRule"; }

        @Override
        public Types.ValidationResult validate(Types.MessageEnvelope envelope) {
            Types.ValidationResult result = new Types.ValidationResult();
            result.setValid(true);
            result.setErrors(new ArrayList<>());

            if (envelope.getHeader().isExpired()) {
                result.setValid(false);
                result.getErrors().add("Message expired (TTL: " + 
                        envelope.getHeader().getTtlSeconds() + "s)");
            }

            return result;
        }
    }

    public void addRule(ValidationRule rule) {
        rules.add(rule);
    }

    public void removeRule(String name) {
        rules.removeIf(r -> r.getName().equals(name));
    }

    public Types.ValidationResult validate(Types.MessageEnvelope envelope) {
        Types.ValidationResult result = new Types.ValidationResult();
        result.setValid(true);
        result.setErrors(new ArrayList<>());

        for (ValidationRule rule : rules) {
            try {
                Types.ValidationResult ruleResult = rule.validate(envelope);
                if (!ruleResult.isValid()) {
                    result.setValid(false);
                    result.getErrors().addAll(ruleResult.getErrors());
                }
            } catch (Exception e) {
                result.setValid(false);
                result.getErrors().add("Rule " + rule.getName() + " error: " + e.getMessage());
            }
        }

        return result;
    }

    public static Validator defaultValidator() {
        return new Validator();
    }
}