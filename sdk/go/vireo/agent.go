package vireo

import (
    "fmt"
    "sync"
    "time"
)

// ============================================================
// AGENT STATE MACHINE
// ============================================================

type AgentState string

const (
    StateIdle        AgentState = "idle"
    StateDiscovering AgentState = "discovering"
    StateProposing   AgentState = "proposing"
    StateNegotiating AgentState = "negotiating"
    StateCommitting  AgentState = "committing"
    StateExecuting   AgentState = "executing"
    StateVerifying   AgentState = "verifying"
    StateDone        AgentState = "done"
    StateError       AgentState = "error"
)

type StateMachine struct {
    State     AgentState              `json:"state"`
    History   []AgentState            `json:"history"`
    Context   map[string]interface{}  `json:"context"`
    StartedAt time.Time               `json:"started_at"`
    UpdatedAt time.Time               `json:"updated_at"`
    mu        sync.RWMutex
}

func NewStateMachine() *StateMachine {
    return &StateMachine{
        State:     StateIdle,
        History:   []AgentState{},
        Context:   make(map[string]interface{}),
        StartedAt: time.Now().UTC(),
        UpdatedAt: time.Now().UTC(),
    }
}

func (sm *StateMachine) GetState() AgentState {
    sm.mu.RLock()
    defer sm.mu.RUnlock()
    return sm.State
}

func (sm *StateMachine) SetState(state AgentState) {
    sm.mu.Lock()
    defer sm.mu.Unlock()
    sm.History = append(sm.History, sm.State)
    sm.State = state
    sm.UpdatedAt = time.Now().UTC()
}

func (sm *StateMachine) Reset() {
    sm.mu.Lock()
    defer sm.mu.Unlock()
    sm.State = StateIdle
    sm.History = []AgentState{}
    sm.Context = make(map[string]interface{})
    sm.StartedAt = time.Now().UTC()
    sm.UpdatedAt = time.Now().UTC()
}

func (sm *StateMachine) GetHistory() []AgentState {
    sm.mu.RLock()
    defer sm.mu.RUnlock()
    history := make([]AgentState, len(sm.History))
    copy(history, sm.History)
    return history
}

func (sm *StateMachine) GetSummary() map[string]interface{} {
    sm.mu.RLock()
    defer sm.mu.RUnlock()
    return map[string]interface{}{
        "state":      sm.State,
        "history":    sm.History,
        "context":    sm.Context,
        "started_at": sm.StartedAt,
        "updated_at": sm.UpdatedAt,
    }
}

// ============================================================
// VIREO AGENT
// ============================================================

type VireoAgent struct {
    agentID      string
    name         string
    role         AgentRole
    capabilities map[string]AgentCapability
    stateMachine *StateMachine
    validator    *Validator
    listeners    map[string][]func(...interface{})
    handlers     map[MessageType]func(*MessageEnvelope) error
    mu           sync.RWMutex
}

type AgentConfig struct {
    Name string
    Role AgentRole
}

func NewVireoAgent(config AgentConfig) *VireoAgent {
    agentID := fmt.Sprintf("agent-%x", time.Now().UnixNano()&0xFFFFFFFF)

    agent := &VireoAgent{
        agentID:      agentID,
        name:         config.Name,
        role:         config.Role,
        capabilities: make(map[string]AgentCapability),
        stateMachine: NewStateMachine(),
        validator:    NewValidator(),
        listeners:    make(map[string][]func(...interface{})),
        handlers:     make(map[MessageType]func(*MessageEnvelope) error),
    }

    // Register default handlers
    agent.registerDefaultHandlers()

    return agent
}

// ============================================================
// AGENT INFO
// ============================================================

func (a *VireoAgent) GetAgentID() string {
    return a.agentID
}

func (a *VireoAgent) GetName() string {
    return a.name
}

func (a *VireoAgent) GetRole() AgentRole {
    return a.role
}

func (a *VireoAgent) GetState() AgentState {
    return a.stateMachine.GetState()
}

func (a *VireoAgent) GetInfo() AgentInfo {
    a.mu.RLock()
    defer a.mu.RUnlock()

    caps := make([]string, 0, len(a.capabilities))
    for name := range a.capabilities {
        caps = append(caps, name)
    }

    return AgentInfo{
        AgentID:      a.agentID,
        Name:         a.name,
        Role:         a.role,
        Capabilities: caps,
        Description:  fmt.Sprintf("Vireo agent: %s", a.name),
    }
}

// ============================================================
// CAPABILITIES
// ============================================================

func (a *VireoAgent) RegisterCapability(name, description string, handler func(...interface{}) (interface{}, error)) error {
    a.mu.Lock()
    defer a.mu.Unlock()

    if _, exists := a.capabilities[name]; exists {
        return NewKeyError(fmt.Sprintf("Capability '%s' already registered", name), "")
    }

    a.capabilities[name] = AgentCapability{
        Name:        name,
        Description: description,
        Handler:     handler,
    }

    return nil
}

func (a *VireoAgent) HasCapability(name string) bool {
    a.mu.RLock()
    defer a.mu.RUnlock()
    _, exists := a.capabilities[name]
    return exists
}

func (a *VireoAgent) GetCapabilities() []string {
    a.mu.RLock()
    defer a.mu.RUnlock()

    caps := make([]string, 0, len(a.capabilities))
   