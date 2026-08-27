# ============================================================
# VIREO CONTRACT — Resource Invariants
# ============================================================

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import time


@dataclass
class Contract:
    max_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None
    timeout_sec: Optional[int] = None
    max_rounds: Optional[int] = None
    max_memory_mb: Optional[int] = None
    allowed_actions: List[str] = field(default_factory=list)
    required_approvals: int = 1
    
    def validate(self, proposal: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        if self.max_tokens:
            tokens = proposal.get("tokens", 0)
            if tokens > self.max_tokens:
                return False, f"Token limit exceeded: {tokens} > {self.max_tokens}"
        if self.max_cost_usd:
            cost = proposal.get("cost", 0)
            if cost > self.max_cost_usd:
                return False, f"Cost limit exceeded: ${cost} > ${self.max_cost_usd}"
        if self.timeout_sec:
            estimated_time = proposal.get("estimated_time_sec", 0)
            if estimated_time > self.timeout_sec:
                return False, f"Time limit exceeded: {estimated_time}s > {self.timeout_sec}s"
        if self.allowed_actions:
            action = proposal.get("action", "")
            if action and action not in self.allowed_actions:
                return False, f"Action '{action}' not allowed"
        return True, None


@dataclass
class Proposal:
    id: str
    sender: str
    recipient: str
    task: str
    code: str
    reasoning: str
    contract: Contract
    timestamp: float = field(default_factory=time.time)
    status: str = "proposed"


def create_default_contract() -> Contract:
    return Contract(
        max_tokens=1000,
        max_cost_usd=0.05,
        timeout_sec=30,
        max_rounds=3,
        allowed_actions=["train_model", "predict", "evaluate", "generate_code"]
    )