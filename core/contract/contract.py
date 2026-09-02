"""Contract definition for Vireo v2.0.1"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


@dataclass
class Terms:
    """Contract terms"""
    max_tokens: Optional[int] = None
    timeout_sec: Optional[int] = None
    max_cost_usd: Optional[float] = None
    max_rounds: Optional[int] = None
    deadline: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate terms"""
        errors = []
        
        if self.max_tokens is not None and self.max_tokens <= 0:
            errors.append("max_tokens must be positive")
        
        if self.timeout_sec is not None and self.timeout_sec <= 0:
            errors.append("timeout_sec must be positive")
        
        if self.max_cost_usd is not None and self.max_cost_usd < 0:
            errors.append("max_cost_usd must be non-negative")
        
        if self.max_rounds is not None and self.max_rounds <= 0:
            errors.append("max_rounds must be positive")
        
        return errors


@dataclass
class Obligation:
    """Contract obligation for a party"""
    action: str
    input: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    depends_on: List[str] = field(default_factory=list)


@dataclass
class Contract:
    """Vireo contract"""
    
    contract_id: Optional[str] = None
    parties: List[str] = field(default_factory=list)
    terms: Optional[Terms] = None
    obligations: Dict[str, Obligation] = field(default_factory=dict)
    condition: Optional[str] = None
    on_failure: str = "escalate"
    signatures: Dict[str, str] = field(default_factory=dict)
    status: str = "draft"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.contract_id is None:
            self.contract_id = f"contract-{uuid.uuid4().hex[:8]}"
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if self.terms is None:
            self.terms = Terms()
    
    def validate(self) -> List[str]:
        """Validate contract"""
        errors = []
        
        # Check parties
        if len(self.parties) < 2:
            errors.append("At least 2 parties required")
        
        # Check terms
        if self.terms:
            errors.extend(self.terms.validate())
        
        # Check obligations
        for party, obligation in self.obligations.items():
            if party not in self.parties:
                errors.append(f"Party '{party}' not in parties list")
            
            if not obligation.action:
                errors.append(f"Obligation for '{party}' missing action")
        
        # Check signatures
        for party in self.parties:
            if party not in self.signatures:
                errors.append(f"Missing signature from '{party}'")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if contract is valid"""
        return len(self.validate()) == 0
    
    def add_signature(self, party: str, signature: str) -> bool:
        """Add a signature"""
        if party not in self.parties:
            return False
        self.signatures[party] = signature
        return True
    
    def is_signed(self) -> bool:
        """Check if all parties signed"""
        return all(party in self.signatures for party in self.parties)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "contract_id": self.contract_id,
            "parties": self.parties,
            "terms": {
                "max_tokens": self.terms.max_tokens if self.terms else None,
                "timeout_sec": self.terms.timeout_sec if self.terms else None,
                "max_cost_usd": self.terms.max_cost_usd if self.terms else None,
                "max_rounds": self.terms.max_rounds if self.terms else None,
                "deadline": self.terms.deadline if self.terms else None
            } if self.terms else {},
            "obligations": {
                party: {
                    "action": obl.action,
                    "input": obl.input,
                    "output": obl.output,
                    "depends_on": obl.depends_on
                }
                for party, obl in self.obligations.items()
            },
            "condition": self.condition,
            "on_failure": self.on_failure,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        """Create from dict"""
        terms_data = data.get("terms", {})
        terms = Terms(
            max_tokens=terms_data.get("max_tokens"),
            timeout_sec=terms_data.get("timeout_sec"),
            max_cost_usd=terms_data.get("max_cost_usd"),
            max_rounds=terms_data.get("max_rounds"),
            deadline=terms_data.get("deadline")
        )
        
        obligations = {}
        for party, obl_data in data.get("obligations", {}).items():
            obligations[party] = Obligation(
                action=obl_data.get("action", ""),
                input=obl_data.get("input", {}),
                output=obl_data.get("output"),
                depends_on=obl_data.get("depends_on", [])
            )
        
        return cls(
            contract_id=data.get("contract_id"),
            parties=data.get("parties", []),
            terms=terms,
            obligations=obligations,
            condition=data.get("condition"),
            on_failure=data.get("on_failure", "escalate"),
            signatures=data.get("signatures", {}),
            status=data.get("status", "draft"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )