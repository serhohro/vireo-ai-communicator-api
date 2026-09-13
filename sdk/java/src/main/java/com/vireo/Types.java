package com.vireo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Vireo Type Definitions
 * 
 * Core types for Vireo communication protocol
 */
public class Types {

    // ============================================================
    // VIREO VALUE TYPES
    // ============================================================

    public enum VireoType {
        NULL, BOOLEAN, INTEGER, FLOAT, STRING, BINARY,
        ARRAY, OBJECT, TIMESTAMP, DURATION, URI, UUID,
        DID, SIGNATURE, PUBLIC_KEY, PRIVATE_KEY, HASH, NONCE, VERSION
    }

    public static class VireoValue<T> {
        private VireoType type;
        private T value;

        public VireoValue() {}

        public VireoValue(VireoType type, T value) {
            this.type = type;
            this.value = value;
        }

        public VireoType getType() { return type; }
        public void setType(VireoType type) { this.type = type; }
        
        public T getValue() { return value; }
        public void setValue(T value) { this.value = value; }
    }

    public static class VireoObject extends java.util.HashMap<String, VireoValue<?>> {}

    public static class VireoArray extends java.util.ArrayList<VireoValue<?>> {}

    // ============================================================
    // MESSAGE TYPES
    // ============================================================

    public enum MessageType {
        PROPOSE, COMMIT, EXECUTE, VERIFY, ESCALATE, DONE,
        FAILED, TIMEOUT, ACK, NACK, QUERY, RESPONSE, ERROR
    }

    public static class MessageHeader {
        private MessageType type;
        private String version;
        private String messageId;
        private Instant timestamp;
        private String sender;
        private String receiver;
        private String correlationId;
        private String replyTo;
        private String nonce;
        private String signature;
        private int ttlSeconds;
        private int priority;
        private List<String> flags;

        // Getters and Setters
        public MessageType getType() { return type; }
        public void setType(MessageType type) { this.type = type; }

        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }

        public String getMessageId() { return messageId; }
        public void setMessageId(String messageId) { this.messageId = messageId; }

        public Instant getTimestamp() { return timestamp; }
        public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

        public String getSender() { return sender; }
        public void setSender(String sender) { this.sender = sender; }

        public String getReceiver() { return receiver; }
        public void setReceiver(String receiver) { this.receiver = receiver; }

        public String getCorrelationId() { return correlationId; }
        public void setCorrelationId(String correlationId) { this.correlationId = correlationId; }

        public String getReplyTo() { return replyTo; }
        public void setReplyTo(String replyTo) { this.replyTo = replyTo; }

        public String getNonce() { return nonce; }
        public void setNonce(String nonce) { this.nonce = nonce; }

        public String getSignature() { return signature; }
        public void setSignature(String signature) { this.signature = signature; }

        public int getTtlSeconds() { return ttlSeconds; }
        public void setTtlSeconds(int ttlSeconds) { this.ttlSeconds = ttlSeconds; }

        public int getPriority() { return priority; }
        public void setPriority(int priority) { this.priority = priority; }

        public List<String> getFlags() { return flags; }
        public void setFlags(List<String> flags) { this.flags = flags; }

        public boolean isExpired() {
            if (timestamp == null) return false;
            return Instant.now().isAfter(timestamp.plusSeconds(ttlSeconds));
        }
    }

    public static class MessageBody {
        private String contentType;
        private VireoValue<?> data;
        private Map<String, Object> metadata;
        private String schemaUri;
        private int size;

        public String getContentType() { return contentType; }
        public void setContentType(String contentType) { this.contentType = contentType; }

        public VireoValue<?> getData() { return data; }
        public void setData(VireoValue<?> data) { this.data = data; }

        public Map<String, Object> getMetadata() { return metadata; }
        public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }

        public String getSchemaUri() { return schemaUri; }
        public void setSchemaUri(String schemaUri) { this.schemaUri = schemaUri; }

        public int getSize() { return size; }
        public void setSize(int size) { this.size = size; }
    }

    public static class MessageEnvelope {
        private MessageHeader header;
        private MessageBody body;

        public MessageHeader getHeader() { return header; }
        public void setHeader(MessageHeader header) { this.header = header; }

        public MessageBody getBody() { return body; }
        public void setBody(MessageBody body) { this.body = body; }

        public boolean isValid() {
            if (header == null) return false;
            return !header.isExpired();
        }
    }

    // ============================================================
    // PROTOCOL STATES
    // ============================================================

    public enum ProtocolState {
        INIT, PROPOSE, COMMIT, EXECUTE, VERIFY, ESCALATE, DONE, FAILED, TIMEOUT, PAUSED
    }

    // ============================================================
    // AGENT TYPES
    // ============================================================

    public enum AgentRole {
        MASTER, WORKER, EXECUTOR, GUARDIAN, RESEARCHER, ANALYST, TEACHER, CUSTOM
    }

    public static class AgentInfo {
        private String agentId;
        private String name;
        private AgentRole role;
        private List<String> capabilities;
        private String description;
        private byte[] publicKey;

        public String getAgentId() { return agentId; }
        public void setAgentId(String agentId) { this.agentId = agentId; }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }

        public AgentRole getRole() { return role; }
        public void setRole(AgentRole role) { this.role = role; }

        public List<String> getCapabilities() { return capabilities; }
        public void setCapabilities(List<String> capabilities) { this.capabilities = capabilities; }

        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }

        public byte[] getPublicKey() { return publicKey; }
        public void setPublicKey(byte[] publicKey) { this.publicKey = publicKey; }
    }

    // ============================================================
    // CONTRACT TYPES
    // ============================================================

    public enum ContractStatus {
        DRAFT, PROPOSED, ACCEPTED, COMMITTED, EXECUTING, EXECUTED, VERIFIED, FAILED
    }

    public static class Terms {
        private Integer maxTokens;
        private Integer timeoutSec;
        private Double maxCostUsd;
        private Integer maxRounds;
        private String deadline;

        public Integer getMaxTokens() { return maxTokens; }
        public void setMaxTokens(Integer maxTokens) { this.maxTokens = maxTokens; }

        public Integer getTimeoutSec() { return timeoutSec; }
        public void setTimeoutSec(Integer timeoutSec) { this.timeoutSec = timeoutSec; }

        public Double getMaxCostUsd() { return maxCostUsd; }
        public void setMaxCostUsd(Double maxCostUsd) { this.maxCostUsd = maxCostUsd; }

        public Integer getMaxRounds() { return maxRounds; }
        public void setMaxRounds(Integer maxRounds) { this.maxRounds = maxRounds; }

        public String getDeadline() { return deadline; }
        public void setDeadline(String deadline) { this.deadline = deadline; }
    }

    public static class Obligation {
        private String action;
        private Map<String, Object> input;
        private Map<String, Object> output;
        private List<String> dependsOn;

        public String getAction() { return action; }
        public void setAction(String action) { this.action = action; }

        public Map<String, Object> getInput() { return input; }
        public void setInput(Map<String, Object> input) { this.input = input; }

        public Map<String, Object> getOutput() { return output; }
        public void setOutput(Map<String, Object> output) { this.output = output; }

        public List<String> getDependsOn() { return dependsOn; }
        public void setDependsOn(List<String> dependsOn) { this.dependsOn = dependsOn; }
    }

    public static class Contract {
        private String contractId;
        private List<String> parties;
        private Terms terms;
        private Map<String, Obligation> obligations;
        private String condition;
        private String onFailure;
        private Map<String, String> signatures;
        private ContractStatus status;
        private Instant createdAt;
        private Instant updatedAt;

        public String getContractId() { return contractId; }
        public void setContractId(String contractId) { this.contractId = contractId; }

        public List<String> getParties() { return parties; }
        public void setParties(List<String> parties) { this.parties = parties; }

        public Terms getTerms() { return terms; }
        public void setTerms(Terms terms) { this.terms = terms; }

        public Map<String, Obligation> getObligations() { return obligations; }
        public void setObligations(Map<String, Obligation> obligations) { this.obligations = obligations; }

        public String getCondition() { return condition; }
        public void setCondition(String condition) { this.condition = condition; }

        public String getOnFailure() { return onFailure; }
        public void setOnFailure(String onFailure) { this.onFailure = onFailure; }

        public Map<String, String> getSignatures() { return signatures; }
        public void setSignatures(Map<String, String> signatures) { this.signatures = signatures; }

        public ContractStatus getStatus() { return status; }
        public void setStatus(ContractStatus status) { this.status = status; }

        public Instant getCreatedAt() { return createdAt; }
        public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

        public Instant getUpdatedAt() { return updatedAt; }
        public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
    }

    // ============================================================
    // VALIDATION
    // ============================================================

    public static class ValidationResult {
        private boolean valid;
        private List<String> errors;

        public boolean isValid() { return valid; }
        public void setValid(boolean valid) { this.valid = valid; }

        public List<String> getErrors() { return errors; }
        public void setErrors(List<String> errors) { this.errors = errors; }
    }

    // ============================================================
    // REPUTATION
    // ============================================================

    public static class ReputationScore {
        private String entityId;
        private double score;
        private String level;
        private int totalEvents;
        private int positiveEvents;
        private int negativeEvents;
        private Instant lastUpdate;
        private Map<String, Double> factors;
        private double confidence;

        public String getEntityId() { return entityId; }
        public void setEntityId(String entityId) { this.entityId = entityId; }

        public double getScore() { return score; }
        public void setScore(double score) { this.score = score; }

        public String getLevel() { return level; }
        public void setLevel(String level) { this.level = level; }

        public int getTotalEvents() { return totalEvents; }
        public void setTotalEvents(int totalEvents) { this.totalEvents = totalEvents; }

        public int getPositiveEvents() { return positiveEvents; }
        public void setPositiveEvents(int positiveEvents) { this.positiveEvents = positiveEvents; }

        public int getNegativeEvents() { return negativeEvents; }
        public void setNegativeEvents(int negativeEvents) { this.negativeEvents = negativeEvents; }

        public Instant getLastUpdate() { return lastUpdate; }
        public void setLastUpdate(Instant lastUpdate) { this.lastUpdate = lastUpdate; }

        public Map<String, Double> getFactors() { return factors; }
        public void setFactors(Map<String, Double> factors) { this.factors = factors; }

        public double getConfidence() { return confidence; }
        public void setConfidence(double confidence) { this.confidence = confidence; }
    }

    public static class ReputationEvent {
        private String id;
        private String entityId;
        private String eventType;
        private String factor;
        private double weight;
        private Instant timestamp;
        private String description;
        private Map<String, Object> metadata;

        public String getId() { return id; }
        public void setId(String id) { this.id = id; }

        public String getEntityId() { return entityId; }
        public void setEntityId(String entityId) { this.entityId = entityId; }

        public String getEventType() { return eventType; }
        public void setEventType(String eventType) { this.eventType = eventType; }

        public String getFactor() { return factor; }
        public void setFactor(String factor) { this.factor = factor; }

        public double getWeight() { return weight; }
        public void setWeight(double weight) { this.weight = weight; }

        public Instant getTimestamp() { return timestamp; }
        public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }

        public Map<String, Object> getMetadata() { return metadata; }
        public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
    }
}