// Vireo v3.0.0 — Agent (Rust SDK)
// AI Agent implementation for Vireo protocol

use crate::wire_format::{Message, Intent, Flags};
use crate::crypto::{sign, verify, generate_keypair};
use serde_json::Value;
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};
use rand::Rng;

/// Agent state machine states
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AgentState {
    /// Initial state - discovery
    Discover,
    /// Proposal sent
    Propose,
    /// Negotiation in progress
    Negotiate,
    /// Commitment made
    Commit,
    /// Execution in progress
    Execute,
    /// Verification in progress
    Verify,
    /// Completed successfully
    Done,
    /// Escalated to dispute resolution
    Escalate,
    /// Rejected
    Reject,
    /// Timed out
    Timeout,
}

impl AgentState {
    /// Check if state is terminal
    pub fn is_terminal(&self) -> bool {
        matches!(self, Self::Done | Self::Reject | Self::Timeout)
    }
    
    /// Check if escalation is possible
    pub fn can_escalate(&self) -> bool {
        !matches!(self, Self::Done | Self::Reject | Self::Timeout | Self::Escalate)
    }
}

impl std::fmt::Display for AgentState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            Self::Discover => "DISCOVER",
            Self::Propose => "PROPOSE",
            Self::Negotiate => "NEGOTIATE",
            Self::Commit => "COMMIT",
            Self::Execute => "EXECUTE",
            Self::Verify => "VERIFY",
            Self::Done => "DONE",
            Self::Escalate => "ESCALATE",
            Self::Reject => "REJECT",
            Self::Timeout => "TIMEOUT",
        };
        write!(f, "{}", s)
    }
}

/// Pending proposal data
#[derive(Debug, Clone)]
struct PendingProposal {
    recipient: String,
    contract: Value,
    timestamp: u64,
}

/// Agent configuration
#[derive(Debug, Clone)]
pub struct AgentConfig {
    /// Agent name
    pub name: String,
    /// Agent capabilities
    pub capabilities: Vec<String>,
    /// Timeout in seconds for each state
    pub timeouts: HashMap<AgentState, u64>,
}

impl Default for AgentConfig {
    fn default() -> Self {
        let mut timeouts = HashMap::new();
        timeouts.insert(AgentState::Discover, 30);
        timeouts.insert(AgentState::Propose, 60);
        timeouts.insert(AgentState::Negotiate, 120);
        timeouts.insert(AgentState::Commit, 30);
        timeouts.insert(AgentState::Execute, 300);
        timeouts.insert(AgentState::Verify, 60);
        timeouts.insert(AgentState::Escalate, 600);
        
        Self {
            name: "Vireo Agent".to_string(),
            capabilities: vec!["chat".to_string(), "execute".to_string()],
            timeouts,
        }
    }
}

/// Vireo AI Agent
#[derive(Debug)]
pub struct Agent {
    /// Agent ID
    pub id: String,
    /// Agent DID
    pub did: String,
    /// Agent configuration
    pub config: AgentConfig,
    /// Agent state
    state: AgentState,
    /// State entered at timestamp
    state_entered_at: u64,
    /// Private key (32 bytes)
    private_key: [u8; 32],
    /// Public key (32 bytes)
    public_key: [u8; 32],
    /// Pending proposals
    pending_proposals: HashMap<String, PendingProposal>,
    /// Executed tasks cache (for idempotency)
    executed_tasks: HashMap<String, bool>,
    /// Current counterparty
    counterparty: Option<String>,
    /// Current contract
    contract: Option<Value>,
}

impl Agent {
    /// Create a new agent with existing keys
    pub fn new(id: &str, private_key: [u8; 32], public_key: [u8; 32]) -> Self {
        Self {
            id: id.to_string(),
            did: format!("did:vireo:agent:{}", id),
            config: AgentConfig::default(),
            state: AgentState::Discover,
            state_entered_at: Self::current_time_ms(),
            private_key,
            public_key,
            pending_proposals: HashMap::new(),
            executed_tasks: HashMap::new(),
            counterparty: None,
            contract: None,
        }
    }
    
    /// Create a new agent with generated keys
    pub fn new_with_keys(id: &str) -> Self {
        let (private_key, public_key) = generate_keypair();
        Self::new(id, private_key, public_key)
    }
    
    /// Get current time in milliseconds
    fn current_time_ms() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_else(|_| std::time::Duration::from_secs(0))
            .as_millis() as u64
    }
    
    /// Get current time in seconds
    fn current_time_sec() -> u64 {
        Self::current_time_ms() / 1000
    }
    
    /// Generate a random nonce
    fn generate_nonce() -> [u8; 16] {
        let mut nonce = [0u8; 16];
        rand::thread_rng().fill(&mut nonce);
        nonce
    }
    
    /// Get the agent's current state
    pub fn get_state(&self) -> AgentState {
        self.state
    }
    
    /// Get the agent's state as string
    pub fn get_state_str(&self) -> String {
        self.state.to_string()
    }
    
    /// Check if the agent is in a terminal state
    pub fn is_complete(&self) -> bool {
        self.state.is_terminal()
    }
    
    /// Get agent's public key
    pub fn get_public_key(&self) -> [u8; 32] {
        self.public_key
    }
    
    /// Get agent's capabilities
    pub fn get_capabilities(&self) -> &[String] {
        &self.config.capabilities
    }
    
    /// Propose a contract to another agent
    pub fn propose(&self, recipient: &str, contract: Value) -> Message {
        let proposal_id = format!("prop_{}_{}", self.id, Self::current_time_ms());
        
        let mut msg = Message::new(
            self.did.clone(),
            format!("did:vireo:agent:{}", recipient),
            Intent::Propose,
            proposal_id,
            contract,
        );
        msg.sign(&self.private_key);
        msg
    }
    
    /// Commit to a proposal
    pub fn commit(&self, recipient: &str, proposal_id: &str) -> Message {
        let mut msg = Message::new(
            self.did.clone(),
            format!("did:vireo:agent:{}", recipient),
            Intent::Commit,
            proposal_id.to_string(),
            serde_json::json!({"status": "committed"}),
        );
        msg.sign(&self.private_key);
        msg
    }
    
    /// Execute a task
    pub fn execute(&self, recipient: &str, proposal_id: &str) -> Message {
        let mut msg = Message::new(
            self.did.clone(),
            format!("did:vireo:agent:{}", recipient),
            Intent::Execute,
            proposal_id.to_string(),
            serde_json::json!({"status": "executing"}),
        );
        msg.sign(&self.private_key);
        msg
    }
    
    /// Verify execution results
    pub fn verify(&self, recipient: &str, proposal_id: &str, result: Value) -> Message {
        let mut msg = Message::new(
            self.did.clone(),
            format!("did:vireo:agent:{}", recipient),
            Intent::Verify,
            proposal_id.to_string(),
            result,
        );
        msg.sign(&self.private_key);
        msg
    }
    
    /// Mark as done
    pub fn done(&self, recipient: &str, proposal_id: &str) -> Message {
        let mut msg = Message::new(
            self.did.clone(),
            format!("did:vireo:agent:{}", recipient),
            Intent::Done,
            proposal_id.to_string(),
            serde_json::json!({"status": "done"}),
        );
        msg.sign(&self.private_key);
        msg
    }
    
    /// Escalate a dispute
    pub fn escalate(&self, recipient: &str, proposal_id: &str, reason: &str) -> Message {
        let mut msg = Message::new(
            self.did.clone(),
            format!("did:vireo:agent:{}", recipient),
            Intent::Escalate,
            proposal_id.to_string(),
            serde_json::json!({"reason": reason}),
        );
        msg.sign(&self.private_key);
        msg
    }
    
    /// Reject a proposal
    pub fn reject(&self, recipient: &str, proposal_id: &str, reason: &str) -> Message {
        let mut msg = Message::new(
            self.did.clone(),
            format!("did:vireo:agent:{}", recipient),
            Intent::Reject,
            proposal_id.to_string(),
            serde_json::json!({"reason": reason}),
        );
        msg.sign(&self.private_key);
        msg
    }
    
    /// Process a received message
    pub fn receive(&mut self, message: &Message) -> Result<Option<Message>, String> {
        // Validate signature
        if !message.verify(&self.public_key) {
            return Err("Invalid signature".to_string());
        }
        
        // Validate timestamp
        if !message.is_timestamp_valid() {
            return Err("Invalid timestamp".to_string());
        }
        
        // Validate DIDs
        if !Message::validate_did(&message.sender) {
            return Err("Invalid sender DID".to_string());
        }
        if !Message::validate_did(&message.recipient) {
            return Err("Invalid recipient DID".to_string());
        }
        
        // Check idempotency
        let idempotency_key = format!("{}_{}", message.proposal_id, message.intent.to_byte());
        if self.executed_tasks.contains_key(&idempotency_key) {
            return Ok(None);
        }
        
        // Update state and route
        match message.intent {
            Intent::Propose => {
                self.transition(AgentState::Propose)?;
                self.counterparty = Some(message.sender.clone());
                self.contract = message.payload.clone();
                
                // Store pending proposal
                let proposal = PendingProposal {
                    recipient: message.sender.clone(),
                    contract: message.payload.clone().unwrap_or_default(),
                    timestamp: Self::current_time_sec(),
                };
                self.pending_proposals.insert(message.proposal_id.clone(), proposal);
                
                // Check if we can accept
                if self.can_accept(&message.payload) {
                    Ok(Some(self.commit(
                        &Self::extract_agent_id(&message.sender),
                        &message.proposal_id
                    )))
                } else {
                    Ok(Some(self.reject(
                        &Self::extract_agent_id(&message.sender),
                        &message.proposal_id,
                        "cannot_accept"
                    )))
                }
            }
            Intent::Commit => {
                if !self.pending_proposals.contains_key(&message.proposal_id) {
                    return Ok(Some(self.reject(
                        &Self::extract_agent_id(&message.sender),
                        &message.proposal_id,
                        "unknown_proposal"
                    )));
                }
                
                self.transition(AgentState::Commit)?;
                self.counterparty = Some(message.sender.clone());
                
                Ok(Some(self.execute(
                    &Self::extract_agent_id(&message.sender),
                    &message.proposal_id
                )))
            }
            Intent::Execute => {
                self.transition(AgentState::Execute)?;
                self.counterparty = Some(message.sender.clone());
                
                // Execute the task
                let result = self.do_execute(message.payload.clone());
                
                // Mark as executed for idempotency
                self.executed_tasks.insert(idempotency_key, true);
                
                Ok(Some(self.verify(
                    &Self::extract_agent_id(&message.sender),
                    &message.proposal_id,
                    result
                )))
            }
            Intent::Verify => {
                self.transition(AgentState::Verify)?;
                self.counterparty = Some(message.sender.clone());
                
                let is_valid = self.verify_result(message.payload.clone());
                
                if is_valid {
                    self.transition(AgentState::Done)?;
                    Ok(Some(self.done(
                        &Self::extract_agent_id(&message.sender),
                        &message.proposal_id
                    )))
                } else {
                    self.transition(AgentState::Escalate)?;
                    Ok(Some(self.escalate(
                        &Self::extract_agent_id(&message.sender),
                        &message.proposal_id,
                        "verification_failed"
                    )))
                }
            }
            Intent::Done => {
                self.transition(AgentState::Done)?;
                self.executed_tasks.insert(idempotency_key, true);
                self.pending_proposals.remove(&message.proposal_id);
                Ok(None)
            }
            Intent::Escalate => {
                self.transition(AgentState::Escalate)?;
                self.transition(AgentState::Done)?;
                Ok(Some(self.done(
                    &Self::extract_agent_id(&message.sender),
                    &message.proposal_id
                )))
            }
            Intent::Reject => {
                self.pending_proposals.remove(&message.proposal_id);
                Ok(None)
            }
            Intent::Timeout => {
                self.pending_proposals.remove(&message.proposal_id);
                Ok(None)
            }
        }
    }
    
    /// Check if agent can accept a proposal
    fn can_accept(&self, payload: &Option<Value>) -> bool {
        if let Some(payload) = payload {
            if let Some(capabilities) = payload.get("capabilities").and_then(|c| c.as_array()) {
                for cap in capabilities {
                    if let Some(cap_str) = cap.as_str() {
                        if !self.config.capabilities.contains(&cap_str.to_string()) {
                            return false;
                        }
                    }
                }
            }
        }
        true
    }
    
    /// Execute a task (override in subclasses)
    fn do_execute(&self, _payload: Option<Value>) -> Value {
        serde_json::json!({
            "status": "success",
            "output": "executed",
            "timestamp": Self::current_time_sec()
        })
    }
    
    /// Verify a result (override in subclasses)
    fn verify_result(&self, payload: Option<Value>) -> bool {
        if let Some(payload) = payload {
            if let Some(status) = payload.get("status").and_then(|s| s.as_str()) {
                return status == "success";
            }
        }
        false
    }
    
    /// Transition to a new state
    fn transition(&mut self, new_state: AgentState) -> Result<(), String> {
        // Check if transition is valid
        let valid_transitions = self.get_valid_transitions();
        
        if !valid_transitions.contains(&new_state) {
            return Err(format!(
                "Invalid transition: {} -> {}",
                self.state, new_state
            ));
        }
        
        self.state = new_state;
        self.state_entered_at = Self::current_time_ms();
        Ok(())
    }
    
    /// Get valid transitions from current state
    fn get_valid_transitions(&self) -> Vec<AgentState> {
        match self.state {
            AgentState::Discover => vec![AgentState::Propose, AgentState::Reject],
            AgentState::Propose => vec![AgentState::Negotiate, AgentState::Commit, AgentState::Reject, AgentState::Timeout],
            AgentState::Negotiate => vec![AgentState::Propose, AgentState::Commit, AgentState::Reject, AgentState::Timeout],
            AgentState::Commit => vec![AgentState::Execute, AgentState::Reject, AgentState::Timeout],
            AgentState::Execute => vec![AgentState::Verify, AgentState::Timeout, AgentState::Reject],
            AgentState::Verify => vec![AgentState::Done, AgentState::Escalate, AgentState::Timeout],
            AgentState::Done => vec![],
            AgentState::Escalate => vec![AgentState::Done],
            AgentState::Reject => vec![],
            AgentState::Timeout => vec![],
        }
    }
    
    /// Extract agent ID from DID
    fn extract_agent_id(did: &str) -> String {
        did.split(':').last().unwrap_or("unknown").to_string()
    }
    
    /// Check if the agent has timed out
    pub fn check_timeout(&self) -> Option<AgentState> {
        if self.state.is_terminal() {
            return None;
        }
        
        let timeout = self.config.timeouts.get(&self.state).copied().unwrap_or(60);
        let elapsed = (Self::current_time_ms() - self.state_entered_at) / 1000;
        
        if elapsed > timeout {
            Some(AgentState::Timeout)
        } else {
            None
        }
    }
    
    /// Check timeout and transition if needed
    pub fn check_timeout_and_transition(&mut self) -> Result<(), String> {
        if let Some(new_state) = self.check_timeout() {
            self.transition(new_state)?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    
    #[test]
    fn test_agent_creation() {
        let agent = Agent::new_with_keys("test-agent");
        assert_eq!(agent.id, "test-agent");
        assert_eq!(agent.did, "did:vireo:agent:test-agent");
        assert_eq!(agent.get_state(), AgentState::Discover);
        assert!(!agent.is_complete());
    }
    
    #[test]
    fn test_propose() {
        let agent = Agent::new_with_keys("alice");
        let contract = json!({"task": "test"});
        
        let msg = agent.propose("bob", contract.clone());
        
        assert_eq!(msg.sender, agent.did);
        assert_eq!(msg.recipient, "did:vireo:agent:bob");
        assert_eq!(msg.intent, Intent::Propose);
        assert_eq!(msg.payload, Some(contract));
    }
    
    #[test]
    fn test_full_flow() -> Result<(), String> {
        let mut alice = Agent::new_with_keys("alice");
        let mut bob = Agent::new_with_keys("bob");
        
        // Alice proposes to Bob
        let propose = alice.propose("bob", json!({"task": "test"}));
        let response = bob.receive(&propose)?;
        
        // Bob should commit
        assert!(response.is_some());
        let commit = response.unwrap();
        assert_eq!(commit.intent, Intent::Commit);
        assert_eq!(commit.recipient, alice.did);
        
        // Alice receives commit
        let response = alice.receive(&commit)?;
        assert!(response.is_some());
        let execute = response.unwrap();
        assert_eq!(execute.intent, Intent::Execute);
        assert_eq!(execute.recipient, bob.did);
        
        // Bob receives execute
        let response = bob.receive(&execute)?;
        assert!(response.is_some());
        let verify = response.unwrap();
        assert_eq!(verify.intent, Intent::Verify);
        assert_eq!(verify.recipient, alice.did);
        
        // Alice receives verify
        let response = alice.receive(&verify)?;
        assert!(response.is_some());
        let done = response.unwrap();
        assert_eq!(done.intent, Intent::Done);
        assert_eq!(done.recipient, bob.did);
        
        // Bob receives done
        let response = bob.receive(&done)?;
        assert!(response.is_none());
        
        assert_eq!(alice.get_state(), AgentState::Done);
        assert_eq!(bob.get_state(), AgentState::Done);
        
        Ok(())
    }
    
    #[test]
    fn test_reject_proposal() -> Result<(), String> {
        let mut alice = Agent::new_with_keys("alice");
        let mut bob = Agent::new_with_keys("bob");
        
        // Bob proposes with capability Alice doesn't have
        let propose = bob.propose("alice", json!({"capabilities": ["unknown"]}));
        let response = alice.receive(&propose)?;
        
        assert!(response.is_some());
        let reject = response.unwrap();
        assert_eq!(reject.intent, Intent::Reject);
        assert_eq!(reject.recipient, bob.did);
        
        Ok(())
    }
    
    #[test]
    fn test_idempotency() -> Result<(), String> {
        let mut alice = Agent::new_with_keys("alice");
        let mut bob = Agent::new_with_keys("bob");
        
        let propose = alice.propose("bob", json!({"task": "test"}));
        let commit = bob.receive(&propose)?.unwrap();
        let execute = alice.receive(&commit)?.unwrap();
        let verify = bob.receive(&execute)?.unwrap();
        let done = alice.receive(&verify)?.unwrap();
        bob.receive(&done)?;
        
        // Try to process the same message again
        let response = bob.receive(&propose)?;
        assert!(response.is_none());
        
        Ok(())
    }
}