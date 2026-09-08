package vireo

import (
    "time"
    "github.com/google/uuid"
)

// ============================================================
// VIREO VALUE TYPES
// ============================================================

type VireoType string

const (
    TypeNull      VireoType = "null"
    TypeBoolean   VireoType = "boolean"
    TypeInteger   VireoType = "integer"
    TypeFloat     VireoType = "float"
    TypeString    VireoType = "string"
    TypeBinary    VireoType = "binary"
    TypeArray     VireoType = "array"
    TypeObject    VireoType = "object"
    TypeTimestamp VireoType = "timestamp"
    TypeDuration  VireoType = "duration"
    TypeURI       VireoType = "uri"
    TypeUUID      VireoType = "uuid"
    TypeDID       VireoType = "did"
    TypeSignature VireoType = "signature"
    TypePublicKey VireoType = "public_key"
    TypePrivateKey VireoType = "private_key"
    TypeHash      VireoType = "hash"
    TypeNonce     VireoType = "nonce"
    TypeVersion   VireoType = "version"
)

type VireoValue struct {
    Type  VireoType   `json:"type"`
    Value interface{} `json:"value"`
}

type VireoObject map[string]VireoValue
type VireoArray []VireoValue

// ============================================================
// MESSAGE TYPES
// ============================================================

type MessageType string

const (
    MsgPropose  MessageType = "propose"
    MsgCommit   MessageType = "commit"
    MsgExecute  MessageType = "execute"
    MsgVerify   MessageType = "verify"
    MsgEscalate MessageType = "escalate"
    MsgDone     MessageType = "done"
    MsgFailed   MessageType = "failed"
    MsgTimeout  MessageType = "timeout"
    MsgAck      MessageType = "ack"
    MsgNack     MessageType = "nack"
    MsgQuery    MessageType = "query"
    MsgResponse MessageType = "response"
    MsgError    MessageType = "error"
)

type MessageHeader struct {
    Type          MessageType `json:"type"`
    Version       string      `json:"version"`
    MessageID     string      `json:"message_id"`
    Timestamp     time.Time   `json:"timestamp"`
    Sender        string      `json:"sender"`
    Receiver      *string     `json:"receiver,omitempty"`
    CorrelationID *string     `json:"correlation_id,omitempty"`
    ReplyTo       *string     `json:"reply_to,omitempty"`
    Nonce         *string     `json:"nonce,omitempty"`
    Signature     *string     `json:"signature,omitempty"`
    TTLSeconds    int         `json:"ttl_seconds"`
    Priority      int         `json:"priority"`
    Flags         []string    `json:"flags"`
}

type MessageBody struct {
    ContentType string                 `json:"content_type"`
    Data        VireoValue             `json:"data"`
    Metadata    map[string]interface{} `json:"metadata"`
    SchemaURI   *string                `json:"schema_uri,omitempty"`
    Size        int                    `json:"size"`
}

type MessageEnvelope struct {
    Header MessageHeader `json:"header"`
    Body   *MessageBody  `json:"body,omitempty"`
}

// ============================================================
// PROTOCOL STATES
// ============================================================

type ProtocolState string

const (
    StateInit     ProtocolState = "init"
    StatePropose  ProtocolState = "propose"
    StateCommit   ProtocolState = "commit"
    StateExecute  ProtocolState = "execute"
    StateVerify   ProtocolState = "verify"
    StateEscalate ProtocolState = "escalate"
    StateDone     ProtocolState = "done"
    StateFailed   ProtocolState = "failed"
    StateTimeout  ProtocolState = "timeout"
    StatePaused   ProtocolState = "paused"
)

// ============================================================
// AGENT TYPES
// ============================================================

type AgentRole string

const (
    RoleMaster    AgentRole = "master"
    RoleWorker    AgentRole = "worker"
    RoleExecutor  AgentRole = "executor"
    RoleGuardian  AgentRole = "guardian"
    RoleResearcher AgentRole = "researcher"
    RoleAnalyst   AgentRole = "analyst"
    RoleTeacher   AgentRole = "teacher"
    RoleCustom    AgentRole = "custom"
)

type AgentInfo struct {
    AgentID      string      `json:"agent_id"`
    Name         string      `json:"name"`
    Role         AgentRole   `json:"role"`
    Capabilities []string    `json:"capabilities"`
    Description  string      `json:"description"`
    PublicKey    []byte      `json:"public_key,omitempty"`
}

type AgentCapability struct {
    Name        string                      `json:"name"`
    Description string                      `json:"description"`
    Handler     func(args ...interface{}) (interface{}, error) `json:"-"`
}

// ============================================================
// CONTRACT TYPES
// ============================================================

type ContractStatus string

const (
    StatusDraft     ContractStatus = "draft"
    StatusProposed  ContractStatus = "proposed"
    StatusAccepted  ContractStatus = "accepted"
    StatusCommitted ContractStatus = "committed"
    StatusExecuting ContractStatus = "executing"
    StatusExecuted  ContractStatus = "executed"
    StatusVerified  ContractStatus = "verified"
    StatusFailed    ContractStatus = "failed"
)

type Terms struct {
    MaxTokens   *int     `json:"max_tokens,omitempty"`
    TimeoutSec  *int     `json:"timeout_sec,omitempty"`
    MaxCostUSD  *float64 `json:"max_cost_usd,omitempty"`
    MaxRounds   *int     `json:"max_rounds,omitempty"`
    Deadline    *string  `json:"deadline,omitempty"`
}

type Obligation struct {
    Action    string                 `json:"action"`
    Input     map[string]interface{} `json:"input"`
    Output    map[string]interface{} `json:"output,omitempty"`
    DependsOn []string               `json:"depends_on"`
}

type Contract struct {
    ContractID  string                   `json:"contract_id"`
    Parties     []string                 `json:"parties"`
    Terms       Terms                    `json:"terms"`
    Obligations map[string]Obligation    `json:"obligations"`
    Condition   *string                  `json:"condition,omitempty"`
    OnFailure   string                   `json:"on_failure"`
    Signatures  map[string]string        `json:"signatures"`
    Status      ContractStatus           `json:"status"`
    CreatedAt   time.Time                `json:"created_at"`
    UpdatedAt   *time.Time               `json:"updated_at,omitempty"`
}

// ============================================================
// CRYPTO TYPES
// ============================================================

type KeyPair struct {
    PublicKey  []byte `json:"public_key"`
    PrivateKey []byte `json:"private_key"`
    Algorithm  string `json:"algorithm"`
}

type KeyUsage string

const (
    KeyUsageSigning     KeyUsage = "signing"
    KeyUsageEncryption  KeyUsage = "encryption"
    KeyUsageAuth        KeyUsage = "auth"
    KeyUsageAgreement   KeyUsage = "agreement"
    KeyUsageVerification KeyUsage = "verification"
)

type KeyState string

const (
    KeyStateActive   KeyState = "active"
    KeyStateRevoked  KeyState = "revoked"
    KeyStateExpired  KeyState = "expired"
    KeyStateSuspended KeyState = "suspended"
)

type KeyMetadata struct {
    ID           string     `json:"id"`
    Algorithm    string     `json:"algorithm"`
    Usage        KeyUsage   `json:"usage"`
    State        KeyState   `json:"state"`
    Created      time.Time  `json:"created"`
    Expires      *time.Time `json:"expires,omitempty"`
    RevokedAt    *time.Time `json:"revoked_at,omitempty"`
    RevokedReason *string   `json:"revoked_reason,omitempty"`
    Issuer       *string    `json:"issuer,omitempty"`
    Labels       []string   `json:"labels"`
}

// ============================================================
// VALIDATION
// ============================================================

type ValidationResult struct {
    Valid  bool     `json:"valid"`
    Errors []string `json:"errors"`
}

// ============================================================
// REPUTATION
// ============================================================

type ReputationScore struct {
    EntityID       string             `json:"entity_id"`
    Score          float64            `json:"score"`
    Level          string             `json:"level"`
    TotalEvents    int                `json:"total_events"`
    PositiveEvents int                `json:"positive_events"`
    NegativeEvents int                `json:"negative_events"`
    LastUpdate     time.Time          `json:"last_update"`
    Factors        map[string]float64 `json:"factors"`
    Confidence     float64            `json:"confidence"`
}

type ReputationEvent struct {
    ID          string                 `json:"id"`
    EntityID    string                 `json:"entity_id"`
    EventType   string                 `json:"event_type"`
    Factor      string                 `json:"factor"`
    Weight      float64                `json:"weight"`
    Timestamp   time.Time              `json:"timestamp"`
    Description *string                `json:"description,omitempty"`
    Metadata    map[string]interface{} `json:"metadata"`
}