# ============================================================
# VIREO CONTRACT — Resource Invariants
# ============================================================

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import time
import uuid
import json
from datetime import datetime


@dataclass
class Contract:
    """
    Vireo Contract — resource invariants and verification rules.
    
    Attributes:
        max_tokens: Maximum tokens allowed for execution
        max_cost_usd: Maximum cost in USD
        timeout_sec: Maximum execution time in seconds
        max_rounds: Maximum negotiation rounds
        max_memory_mb: Maximum memory usage in MB
        allowed_actions: List of allowed action types
        required_approvals: Number of approvals required (multi-sig)
        contract_id: Unique contract identifier
        signed_by: List of agents who signed this contract
        condition: Optional condition expression (string)
        invariant: Optional invariant expression (string)
        verify: Optional verification expression (string)
    """
    
    max_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None
    timeout_sec: Optional[int] = None
    max_rounds: Optional[int] = None
    max_memory_mb: Optional[int] = None
    allowed_actions: List[str] = field(default_factory=list)
    required_approvals: int = 1
    contract_id: str = field(default_factory=lambda: f"contract-{uuid.uuid4().hex[:8]}")
    signed_by: List[Dict[str, str]] = field(default_factory=list)
    condition: Optional[str] = None
    invariant: Optional[str] = None
    verify: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    
    def validate(self, proposal: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a proposal against this contract.
        
        Fixed: Uses `is not None` instead of truthiness to handle 0 values correctly.
        """
        # ✅ FIXED: max_tokens=0 now properly rejects all tokens
        if self.max_tokens is not None:
            tokens = proposal.get("tokens", 0)
            if tokens > self.max_tokens:
                return False, f"Token limit exceeded: {tokens} > {self.max_tokens}"
        
        # ✅ FIXED: max_cost_usd=0 now properly rejects all costs
        if self.max_cost_usd is not None:
            cost = proposal.get("cost", 0.0)
            if cost > self.max_cost_usd:
                return False, f"Cost limit exceeded: ${cost} > ${self.max_cost_usd}"
        
        # ✅ FIXED: timeout_sec=0 now properly rejects
        if self.timeout_sec is not None:
            estimated_time = proposal.get("estimated_time_sec", 0)
            if estimated_time > self.timeout_sec:
                return False, f"Time limit exceeded: {estimated_time}s > {self.timeout_sec}s"
        
        # ✅ FIXED: max_rounds now actually checked
        if self.max_rounds is not None:
            rounds = proposal.get("rounds", 0)
            if rounds > self.max_rounds:
                return False, f"Round limit exceeded: {rounds} > {self.max_rounds}"
        
        # ✅ FIXED: max_memory_mb now checked
        if self.max_memory_mb is not None:
            memory = proposal.get("memory_mb", 0)
            if memory > self.max_memory_mb:
                return False, f"Memory limit exceeded: {memory}MB > {self.max_memory_mb}MB"
        
        # Check allowed actions
        if self.allowed_actions:
            action = proposal.get("action", "")
            if action and action not in self.allowed_actions:
                return False, f"Action '{action}' not allowed. Allowed: {self.allowed_actions}"
        
        # ✅ FIXED: Check required approvals
        if self.required_approvals > 1:
            approvals = proposal.get("approvals", 0)
            if approvals < self.required_approvals:
                return False, f"Not enough approvals: {approvals} < {self.required_approvals}"
        
        # Check condition if present
        if self.condition:
            # TODO: Implement expression evaluator for conditions
            # For now, store and validate that it exists
            if not self.condition.strip():
                return False, "Condition is empty"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary for serialization."""
        return {
            "contract_id": self.contract_id,
            "max_tokens": self.max_tokens,
            "max_cost_usd": self.max_cost_usd,
            "timeout_sec": self.timeout_sec,
            "max_rounds": self.max_rounds,
            "max_memory_mb": self.max_memory_mb,
            "allowed_actions": self.allowed_actions,
            "required_approvals": self.required_approvals,
            "signed_by": self.signed_by,
            "condition": self.condition,
            "invariant": self.invariant,
            "verify": self.verify,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Contract":
        """Create contract from dictionary."""
        return cls(**data)
    
    def sign(self, agent_id: str, signature: str) -> None:
        """
        Sign this contract with agent's signature.
        
        Args:
            agent_id: ID of the agent signing
            signature: Cryptographic signature (base64)
        """
        self.signed_by.append({
            "agent": agent_id,
            "signature": signature,
            "timestamp": time.time()
        })
    
    def is_signed_by(self, agent_id: str) -> bool:
        """Check if a specific agent has signed this contract."""
        return any(s["agent"] == agent_id for s in self.signed_by)
    
    def get_signed_count(self) -> int:
        """Get number of signatures on this contract."""
        return len(self.signed_by)
    
    def is_fully_signed(self) -> bool:
        """Check if contract has all required approvals."""
        return len(self.signed_by) >= self.required_approvals
    
    def to_json(self) -> str:
        """Serialize contract to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Contract":
        """Deserialize contract from JSON."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class Proposal:
    """
    A proposal from one agent to another.
    """
    id: str
    sender: str
    recipient: str
    task: str
    code: str
    reasoning: str
    contract: Contract
    timestamp: float = field(default_factory=time.time)
    status: str = "proposed"  # proposed | negotiated | committed | rejected | executed | verified
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "task": self.task,
            "code": self.code,
            "reasoning": self.reasoning,
            "contract": self.contract.to_dict(),
            "timestamp": self.timestamp,
            "status": self.status
        }
    
    def to_proposal_dict(self) -> Dict[str, Any]:
        """Convert to the format expected by Contract.validate()."""
        return {
            "tokens": len(self.code) // 4,  # Rough estimate
            "cost": 0.0,
            "estimated_time_sec": 30,
            "rounds": 0,
            "memory_mb": 0,
            "action": self.task.split()[0] if self.task else "",
            "approvals": self.contract.get_signed_count()
        }
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate this proposal against its own contract."""
        return self.contract.validate(self.to_proposal_dict())
    
    def is_valid(self) -> bool:
        """Check if proposal is valid."""
        valid, _ = self.validate()
        return valid


def create_default_contract() -> Contract:
    """Create a default contract with sensible limits."""
    return Contract(
        max_tokens=1000,
        max_cost_usd=0.05,
        timeout_sec=30,
        max_rounds=3,
        max_memory_mb=1024,
        allowed_actions=["train_model", "predict", "evaluate", "generate_code"],
        required_approvals=1
    )


def create_contract_with_limits(
    max_tokens: int = 1000,
    max_cost_usd: float = 0.05,
    timeout_sec: int = 30,
    max_rounds: int = 3,
    max_memory_mb: int = 1024,
    allowed_actions: List[str] = None
) -> Contract:
    """Create a contract with custom limits."""
    return Contract(
        max_tokens=max_tokens,
        max_cost_usd=max_cost_usd,
        timeout_sec=timeout_sec,
        max_rounds=max_rounds,
        max_memory_mb=max_memory_mb,
        allowed_actions=allowed_actions or ["train_model", "predict", "evaluate", "generate_code"],
        required_approvals=1
    )


def create_multisig_contract(
    required_approvals: int = 2,
    max_tokens: int = 5000,
    max_cost_usd: float = 0.10,
    timeout_sec: int = 60
) -> Contract:
    """Create a multi-signature contract requiring multiple approvals."""
    return Contract(
        max_tokens=max_tokens,
        max_cost_usd=max_cost_usd,
        timeout_sec=timeout_sec,
        max_rounds=5,
        max_memory_mb=2048,
        required_approvals=required_approvals,
        allowed_actions=["train_model", "predict", "evaluate", "generate_code"]
    )