package com.vireo;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;

/**
 * Vireo Agent
 * 
 * Core agent implementation for Vireo communication
 */
public class Agent {

    private final String agentId;
    private final String name;
    private final Types.AgentRole role;
    private final Map<String, Capability> capabilities = new ConcurrentHashMap<>();
    private final StateMachine stateMachine;
    private final Validator validator;
    private final Map<String, List<EventListener>> listeners = new ConcurrentHashMap<>();
    private final Map<Types.MessageType, MessageHandler> handlers = new ConcurrentHashMap<>();

    // ============================================================
    // INNER CLASSES
    // ============================================================

    public interface Capability {
        String getName();
        String getDescription();
        Object execute(Object... args) throws Exception;
    }

    public interface MessageHandler {
        void handle(Types.MessageEnvelope envelope) throws Exception;
    }

    public interface EventListener {
        void onEvent(String event, Object... args);
    }

    public static class StateMachine {
        private Types.AgentState state;
        private final List<Types.AgentState> history;
        private final Map<String, Object> context;
        private Instant startedAt;
        private Instant updatedAt;

        public StateMachine() {
            this.state = Types.AgentState.IDLE;
            this.history = new ArrayList<>();
            this.context = new ConcurrentHashMap<>();
            this.startedAt = Instant.now();
            this.updatedAt = Instant.now();
        }

        public synchronized Types.AgentState getState() { return state; }
        public synchronized List<Types.AgentState> getHistory() { return new ArrayList<>(history); }
        public synchronized Map<String, Object> getContext() { return new HashMap<>(context); }

        public synchronized void setState(Types.AgentState newState) {
            history.add(state);
            state = newState;
            updatedAt = Instant.now();
        }

        public synchronized void reset() {
            state = Types.AgentState.IDLE;
            history.clear();
            context.clear();
            startedAt = Instant.now();
            updatedAt = Instant.now();
        }

        public Map<String, Object> getSummary() {
            Map<String, Object> summary = new LinkedHashMap<>();
            summary.put("state", state);
            summary.put("history", new ArrayList<>(history));
            summary.put("context", new HashMap<>(context));
            summary.put("started_at", startedAt);
            summary.put("updated_at", updatedAt);
            return summary;
        }
    }

    // ============================================================
    // CONSTRUCTOR
    // ============================================================

    public Agent(String name) {
        this(name, Types.AgentRole.WORKER);
    }

    public Agent(String name, Types.AgentRole role) {
        this.agentId = "agent-" + UUID.randomUUID().toString().substring(0, 8);
        this.name = name;
        this.role = role;
        this.stateMachine = new StateMachine();
        this.validator = Validator.defaultValidator();
        registerDefaultHandlers();
    }

    // ============================================================
    // GETTERS
    // ============================================================

    public String getAgentId() { return agentId; }
    public String getName() { return name; }
    public Types.AgentRole getRole() { return role; }
    public Types.AgentState getState() { return stateMachine.getState(); }

    public Types.AgentInfo getInfo() {
        Types.AgentInfo info = new Types.AgentInfo();
        info.setAgentId(agentId);
        info.setName(name);
        info.setRole(role);
        info.setCapabilities(new ArrayList<>(capabilities.keySet()));
        info.setDescription("Vireo agent: " + name);
        return info;
    }

    // ============================================================
    // CAPABILITIES
    // ============================================================

    public void registerCapability(String name, String description, Function<Object[], Object> handler) {
        if (capabilities.containsKey(name)) {
            throw new RuntimeException("Capability '" + name + "' already registered");
        }
        capabilities.put(name, new Capability() {
            @Override public String getName() { return name; }
            @Override public String getDescription() { return description; }
            @Override public Object execute(Object... args) throws Exception {
                return handler.apply(args);
            }
        });
    }

    public boolean hasCapability(String name) {
        return capabilities.containsKey(name);
    }

    public List<String> getCapabilities() {
        return new ArrayList<>(capabilities.keySet());
    }

    public Object executeCapability(String name, Object... args) throws Exception {
        Capability cap = capabilities.get(name);
        if (cap == null) {
            throw new Errors.KeyException("Capability '" + name + "' not found", name);
        }
        try {
            return cap.execute(args);
        } catch (Exception e) {
            throw new Exception("Capability execution failed: " + e.getMessage(), e);
        }
    }

    // ============================================================
    // MESSAGE HANDLING
    // ============================================================

    public void on(Types.MessageType type, MessageHandler handler) {
        handlers.put(type, handler);
    }

    public void addListener(String event, EventListener listener) {
        listeners.computeIfAbsent(event, k -> new ArrayList<>()).add(listener);
    }

    protected void emit(String event, Object... args) {
        List<EventListener> list = listeners.get(event);
        if (list != null) {
            for (EventListener listener : list) {
                try {
                    listener.onEvent(event, args);
                } catch (Exception e) {
                    // Log error but continue
                }
            }
        }
    }

    protected void updateState(Types.AgentState newState) {
        stateMachine.setState(newState);
        emit("stateChange", newState);
    }

    public Types.MessageEnvelope handleMessage(Types.MessageEnvelope envelope) throws Exception {
        // Validate
        Types.ValidationResult validation = validator.validate(envelope);
        if (!validation.isValid()) {
            throw new Errors.MessageException(
                "Invalid message: " + String.join(", ", validation.getErrors()),
                null, null
            );
        }

        emit("message", envelope);

        // Handle by type
        MessageHandler handler = handlers.get(envelope.getHeader().getType());
        if (handler != null) {
            handler.handle(envelope);
        }

        updateState(Types.AgentState.valueOf(envelope.getHeader().getType().name()));

        return null;
    }

    // ============================================================
    // MESSAGE CREATION
    // ============================================================

    public Types.MessageEnvelope propose(String recipient, String task, Object contract) {
        updateState(Types.AgentState.PROPOSING);

        Types.MessageEnvelope envelope = createEnvelope(Types.MessageType.PROPOSE, recipient);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("task", task);
        if (contract != null) data.put("contract", contract);

        Types.VireoValue<Map<String, Object>> value = new Types.VireoValue<>(Types.VireoType.OBJECT, data);
        envelope.getBody().setData(value);

        emit("proposed", envelope);
        return envelope;
    }

    public Types.MessageEnvelope commit(String proposalId) {
        updateState(Types.AgentState.COMMITTING);

        Types.MessageEnvelope envelope = createEnvelope(Types.MessageType.COMMIT, null);
        envelope.getHeader().setCorrelationId(proposalId);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("proposal_id", proposalId);
        data.put("status", "committed");

        Types.VireoValue<Map<String, Object>> value = new Types.VireoValue<>(Types.VireoType.OBJECT, data);
        envelope.getBody().setData(value);

        emit("committed", envelope);
        return envelope;
    }

    public Types.MessageEnvelope execute(String proposalId, Object input) throws Exception {
        updateState(Types.AgentState.EXECUTING);

        // Execute capability
        Object result = executeCapability("execute", input);

        Types.MessageEnvelope envelope = createEnvelope(Types.MessageType.EXECUTE, null);
        envelope.getHeader().setCorrelationId(proposalId);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("proposal_id", proposalId);
        data.put("result", result);

        Types.VireoValue<Map<String, Object>> value = new Types.VireoValue<>(Types.VireoType.OBJECT, data);
        envelope.getBody().setData(value);

        emit("executed", envelope);
        return envelope;
    }

    public Types.MessageEnvelope verify(String executionId, Object result) {
        updateState(Types.AgentState.VERIFYING);

        Types.MessageEnvelope envelope = createEnvelope(Types.MessageType.VERIFY, null);
        envelope.getHeader().setCorrelationId(executionId);

        boolean isValid = result != null && 
            result instanceof Map && 
            "success".equals(((Map<?, ?>) result).get("status"));

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("execution_id", executionId);
        data.put("verified", isValid);
        data.put("result", result);

        Types.VireoValue<Map<String, Object>> value = new Types.VireoValue<>(Types.VireoType.OBJECT, data);
        envelope.getBody().setData(value);

        emit("verified", envelope);
        return envelope;
    }

    public Types.MessageEnvelope escalate(String issueId, String reason) {
        updateState(Types.AgentState.ERROR);

        Types.MessageEnvelope envelope = createEnvelope(Types.MessageType.ESCALATE, null);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("issue_id", issueId);
        data.put("reason", reason);

        Types.VireoValue<Map<String, Object>> value = new Types.VireoValue<>(Types.VireoType.OBJECT, data);
        envelope.getBody().setData(value);

        emit("escalated", envelope);
        return envelope;
    }

    public Types.MessageEnvelope done(Object result) {
        updateState(Types.AgentState.DONE);

        Types.MessageEnvelope envelope = createEnvelope(Types.MessageType.DONE, null);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("result", result);
        data.put("completed_at", Instant.now().toString());

        Types.VireoValue<Map<String, Object>> value = new Types.VireoValue<>(Types.VireoType.OBJECT, data);
        envelope.getBody().setData(value);

        emit("done", envelope);
        return envelope;
    }

    // ============================================================
    // UTILITY METHODS
    // ============================================================

    private Types.MessageEnvelope createEnvelope(Types.MessageType type, String recipient) {
        Types.MessageHeader header = new Types.MessageHeader();
        header.setType(type);
        header.setVersion("3.0.0");
        header.setMessageId(UUID.randomUUID().toString());
        header.setTimestamp(Instant.now());
        header.setSender(agentId);
        header.setReceiver(recipient);
        header.setTtlSeconds(300);
        header.setPriority(0);
        header.setFlags(new ArrayList<>());

        Types.MessageBody body = new Types.MessageBody();
        body.setContentType("application/json");
        body.setMetadata(new HashMap<>());
        body.setSize(0);

        Types.MessageEnvelope envelope = new Types.MessageEnvelope();
        envelope.setHeader(header);
        envelope.setBody(body);

        return envelope;
    }

    private void registerDefaultHandlers() {
        // Default handlers for basic messages
        on(Types.MessageType.PROPOSE, envelope -> {
            emit("proposeReceived", envelope);
        });
        on(Types.MessageType.COMMIT, envelope -> {
            emit("commitReceived", envelope);
        });
        on(Types.MessageType.EXECUTE, envelope -> {
            emit("executeReceived", envelope);
        });
        on(Types.MessageType.VERIFY, envelope -> {
            emit("verifyReceived", envelope);
        });
        on(Types.MessageType.DONE, envelope -> {
            emit("doneReceived", envelope);
        });
        on(Types.MessageType.ESCALATE, envelope -> {
            emit("escalateReceived", envelope);
        });
    }

    public void reset() {
        stateMachine.reset();
        emit("reset");
    }

    public Map<String, Object> getStateSummary() {
        return stateMachine.getSummary();
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("agent_id", agentId);
        map.put("name", name);
        map.put("role", role);
        map.put("capabilities", getCapabilities());
        map.put("state", getState());
        map.put("info", getInfo());
        return map;
    }

    @Override
    public String toString() {
        return String.format("Agent(%s, %s, role=%s, state=%s)",
                agentId, name, role, getState());
    }
}