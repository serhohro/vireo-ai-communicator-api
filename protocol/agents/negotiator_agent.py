"""
Vireo Negotiator Agent

Specialized agent for contract negotiation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from ..agent import Agent, AgentConfig
from core.protocol import Message, Contract

logger = logging.getLogger(__name__)


class NegotiatorConfig(AgentConfig):
    """Configuration for Negotiator agent."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capabilities = ["negotiation", "contract", "escrow"]
        self.max_rounds: int = kwargs.get("max_rounds", 10)
        self.timeout_seconds: int = kwargs.get("timeout_seconds", 300)
        self.min_price: float = kwargs.get("min_price", 0)
        self.max_price: float = kwargs.get("max_price", 1000000)
        self.default_deadline: int = kwargs.get("default_deadline", 30)
        self.require_escrow: bool = kwargs.get("require_escrow", True)
        self.strategy: str = kwargs.get("strategy", "collaborative")  # competitive, collaborative, principled


class NegotiatorAgent(Agent):
    """
    Negotiator Agent for contract negotiation.
    
    Supports:
    - Multi-round negotiation
    - Collaborative and competitive strategies
    - Contract creation and signing
    - Escrow management
    - Counter-offer generation
    """
    
    def __init__(self, config: NegotiatorConfig):
        super().__init__(config)
        self.negotiator_config = config
        
        # Active negotiations
        self._negotiations: Dict[str, Dict[str, Any]] = {}
        
        # Contract templates
        self._templates: Dict[str, Dict[str, Any]] = {}
        
        # Setup handlers
        self._setup_handlers()
        
        logger.info(f"Negotiator Agent initialized: {self.id}")
    
    def _setup_handlers(self) -> None:
        """Setup message handlers."""
        self.on_message("propose", self._handle_propose)
        self.on_message("counter", self._handle_counter)
        self.on_message("accept", self._handle_accept)
        self.on_message("reject", self._handle_reject)
        self.on_message("sign", self._handle_sign)
        self.on_message("cancel", self._handle_cancel)
    
    # ============================================================
    # Negotiation Handlers
    # ============================================================
    
    async def _handle_propose(self, message: Message) -> Optional[Message]:
        """Handle proposal message."""
        negotiation_id = message.payload.get("negotiation_id")
        proposal = message.payload.get("proposal", {})
        terms = proposal.get("terms", {})
        
        if not negotiation_id:
            negotiation_id = f"neg_{int(datetime.now().timestamp())}_{message.sender[:8]}"
        
        # Validate proposal
        validation = self._validate_proposal(terms)
        if not validation["valid"]:
            return Message(
                type="reject",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "reason": validation["reason"],
                    "suggestions": validation["suggestions"],
                }
            )
        
        # Create negotiation
        negotiation = {
            "id": negotiation_id,
            "counterparty": message.sender,
            "status": "active",
            "round": 1,
            "proposal": proposal,
            "history": [{
                "round": 1,
                "from": message.sender,
                "proposal": proposal,
                "timestamp": datetime.now().isoformat(),
            }],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        self._negotiations[negotiation_id] = negotiation
        
        # Evaluate proposal
        evaluation = self._evaluate_proposal(terms)
        
        if evaluation["accepted"]:
            # Accept proposal
            negotiation["status"] = "accepted"
            return Message(
                type="accept",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "proposal": proposal,
                    "accepted": True,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            # Make counter-offer
            counter = self._generate_counter_offer(
                proposal=proposal,
                evaluation=evaluation
            )
            
            negotiation["round"] = 2
            negotiation["history"].append({
                "round": 2,
                "from": self.id,
                "proposal": counter,
                "timestamp": datetime.now().isoformat(),
            })
            
            return Message(
                type="counter",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "round": 2,
                    "proposal": counter,
                    "reason": evaluation["reason"],
                    "max_rounds": self.negotiator_config.max_rounds,
                }
            )
    
    async def _handle_counter(self, message: Message) -> Optional[Message]:
        """Handle counter-offer message."""
        negotiation_id = message.payload.get("negotiation_id")
        proposal = message.payload.get("proposal", {})
        terms = proposal.get("terms", {})
        
        if negotiation_id not in self._negotiations:
            return self._create_error_message(
                "negotiation_not_found",
                f"Negotiation {negotiation_id} not found",
                message.id
            )
        
        negotiation = self._negotiations[negotiation_id]
        
        # Check status
        if negotiation["status"] != "active":
            return Message(
                type="reject",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "reason": f"Negotiation status is {negotiation['status']}",
                }
            )
        
        # Check rounds
        if negotiation["round"] >= self.negotiator_config.max_rounds:
            return Message(
                type="reject",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "reason": "Max negotiation rounds exceeded",
                }
            )
        
        # Update negotiation
        negotiation["round"] += 1
        negotiation["updated_at"] = datetime.now().isoformat()
        negotiation["history"].append({
            "round": negotiation["round"],
            "from": message.sender,
            "proposal": proposal,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Evaluate
        evaluation = self._evaluate_proposal(terms)
        
        if evaluation["accepted"]:
            negotiation["status"] = "accepted"
            return Message(
                type="accept",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "proposal": proposal,
                    "accepted": True,
                    "round": negotiation["round"],
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            # Generate counter
            counter = self._generate_counter_offer(
                proposal=proposal,
                evaluation=evaluation
            )
            
            negotiation["history"].append({
                "round": negotiation["round"] + 1,
                "from": self.id,
                "proposal": counter,
                "timestamp": datetime.now().isoformat(),
            })
            
            return Message(
                type="counter",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "round": negotiation["round"] + 1,
                    "proposal": counter,
                    "reason": evaluation["reason"],
                    "max_rounds": self.negotiator_config.max_rounds,
                }
            )
    
    async def _handle_accept(self, message: Message) -> Optional[Message]:
        """Handle acceptance message."""
        negotiation_id = message.payload.get("negotiation_id")
        proposal = message.payload.get("proposal", {})
        
        if negotiation_id not in self._negotiations:
            return self._create_error_message(
                "negotiation_not_found",
                f"Negotiation {negotiation_id} not found",
                message.id
            )
        
        negotiation = self._negotiations[negotiation_id]
        
        if negotiation["status"] != "active":
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                payload={
                    "error": f"Negotiation already {negotiation['status']}",
                }
            )
        
        # Create contract
        contract = self._create_contract(
            negotiation_id=negotiation_id,
            proposal=proposal,
            parties=[self.id, message.sender]
        )
        
        negotiation["status"] = "accepted"
        negotiation["contract"] = contract
        negotiation["updated_at"] = datetime.now().isoformat()
        
        return Message(
            type="contract_ready",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "negotiation_id": negotiation_id,
                "contract": contract,
                "timestamp": datetime.now().isoformat(),
                "sign_required": True,
            }
        )
    
    async def _handle_reject(self, message: Message) -> Optional[Message]:
        """Handle rejection message."""
        negotiation_id = message.payload.get("negotiation_id")
        reason = message.payload.get("reason", "No reason provided")
        
        if negotiation_id in self._negotiations:
            self._negotiations[negotiation_id]["status"] = "rejected"
            self._negotiations[negotiation_id]["reason"] = reason
            self._negotiations[negotiation_id]["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"Negotiation {negotiation_id} rejected: {reason}")
        
        return None
    
    async def _handle_sign(self, message: Message) -> Optional[Message]:
        """Handle contract signing."""
        negotiation_id = message.payload.get("negotiation_id")
        signature = message.payload.get("signature")
        
        if negotiation_id not in self._negotiations:
            return self._create_error_message(
                "negotiation_not_found",
                f"Negotiation {negotiation_id} not found",
                message.id
            )
        
        negotiation = self._negotiations[negotiation_id]
        
        if "contract" not in negotiation:
            return self._create_error_message(
                "no_contract",
                "No contract available for signing",
                message.id
            )
        
        # Verify signature
        contract = negotiation["contract"]
        is_valid = self._verify_signature(contract, signature, message.sender)
        
        if not is_valid:
            return Message(
                type="signature_invalid",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "reason": "Invalid signature",
                }
            )
        
        # Record signature
        if "signatures" not in contract:
            contract["signatures"] = {}
        contract["signatures"][message.sender] = signature
        
        # Check if all parties signed
        all_signed = len(contract["signatures"]) >= len(contract["parties"])
        
        if all_signed:
            contract["status"] = "active"
            contract["activated_at"] = datetime.now().isoformat()
            negotiation["status"] = "contract_active"
            
            logger.info(f"Contract {contract['id']} fully signed and active")
        
        negotiation["updated_at"] = datetime.now().isoformat()
        
        return Message(
            type="contract_signed",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "negotiation_id": negotiation_id,
                "contract_id": contract.get("id"),
                "signatures": contract["signatures"],
                "all_signed": all_signed,
                "status": contract.get("status", "signed"),
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    async def _handle_cancel(self, message: Message) -> Optional[Message]:
        """Handle cancellation."""
        negotiation_id = message.payload.get("negotiation_id")
        reason = message.payload.get("reason", "Cancelled by user")
        
        if negotiation_id in self._negotiations:
            self._negotiations[negotiation_id]["status"] = "cancelled"
            self._negotiations[negotiation_id]["reason"] = reason
            self._negotiations[negotiation_id]["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"Negotiation {negotiation_id} cancelled: {reason}")
        
        return None
    
    # ============================================================
    # Negotiation Logic
    # ============================================================
    
    def _validate_proposal(self, terms: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a proposal."""
        issues = []
        suggestions = []
        
        # Check required fields
        required = ["price", "deadline", "scope"]
        for field in required:
            if field not in terms:
                issues.append(f"Missing required field: {field}")
                suggestions.append(f"Add '{field}' to proposal")
        
        # Validate price
        if "price" in terms:
            price = terms["price"]
            if price < self.negotiator_config.min_price:
                issues.append(f"Price {price} below minimum {self.negotiator_config.min_price}")
                suggestions.append(f"Increase price to at least {self.negotiator_config.min_price}")
            if price > self.negotiator_config.max_price:
                issues.append(f"Price {price} above maximum {self.negotiator_config.max_price}")
                suggestions.append(f"Decrease price to at most {self.negotiator_config.max_price}")
        
        # Validate deadline
        if "deadline" in terms:
            deadline = terms["deadline"]
            if deadline < 1:
                issues.append("Deadline must be at least 1 day")
                suggestions.append("Increase deadline to at least 1 day")
        
        return {
            "valid": len(issues) == 0,
            "reason": "; ".join(issues) if issues else "Valid proposal",
            "suggestions": suggestions,
        }
    
    def _evaluate_proposal(self, terms: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a proposal."""
        price = terms.get("price", 0)
        deadline = terms.get("deadline", self.negotiator_config.default_deadline)
        quality = terms.get("quality", "standard")
        priority = terms.get("priority", "normal")
        
        # Calculate desirability
        price_score = self._calculate_price_score(price)
        deadline_score = self._calculate_deadline_score(deadline)
        quality_score = self._calculate_quality_score(quality)
        
        total_score = (price_score + deadline_score + quality_score) / 3
        
        # Decision
        if total_score >= 0.8:
            return {
                "accepted": True,
                "score": total_score,
                "reason": "Excellent terms",
                "counter_offer": None,
            }
        elif total_score >= 0.6:
            # Accept with minor adjustments
            counter = self._adjust_counter_offer(terms, total_score)
            return {
                "accepted": False,
                "score": total_score,
                "reason": "Good terms with minor adjustments",
                "counter_offer": counter,
            }
        else:
            # Counter-offer
            counter = self._generate_counter_from_scratch(terms, total_score)
            return {
                "accepted": False,
                "score": total_score,
                "reason": "Proposal needs significant adjustment",
                "counter_offer": counter,
            }
    
    def _calculate_price_score(self, price: float) -> float:
        """Calculate price desirability score (0-1)."""
        if price <= 0:
            return 0.0
        
        # Target price is around 70% of max
        target = self.negotiator_config.max_price * 0.7
        if price <= target:
            return 1.0
        else:
            return max(0, 1.0 - (price - target) / (self.negotiator_config.max_price - target))
    
    def _calculate_deadline_score(self, deadline: int) -> float:
        """Calculate deadline desirability score (0-1)."""
        if deadline <= 0:
            return 0.0
        
        # Prefer shorter deadlines
        if deadline <= 7:
            return 1.0
        elif deadline <= 14:
            return 0.8
        elif deadline <= 30:
            return 0.6
        else:
            return max(0, 1.0 - (deadline - 30) / 100)
    
    def _calculate_quality_score(self, quality: str) -> float:
        """Calculate quality desirability score (0-1)."""
        quality_map = {
            "premium": 1.0,
            "high": 0.8,
            "standard": 0.6,
            "basic": 0.3,
            "minimal": 0.1,
        }
        return quality_map.get(quality.lower(), 0.5)
    
    def _generate_counter_offer(self, proposal: Dict, evaluation: Dict) -> Dict:
        """Generate a counter-offer based on evaluation."""
        terms = proposal.get("terms", {})
        counter_offer = evaluation.get("counter_offer")
        
        if counter_offer:
            # Use provided counter-offer
            return {
                "terms": counter_offer,
                "metadata": {
                    "counter_generated": True,
                    "strategy": self.negotiator_config.strategy,
                    "timestamp": datetime.now().isoformat(),
                }
            }
        
        # Generate from scratch
        return self._generate_counter_from_scratch(terms, evaluation["score"])
    
    def _generate_counter_from_scratch(self, terms: Dict, score: float) -> Dict:
        """Generate a counter-offer from scratch."""
        price = terms.get("price", 0)
        deadline = terms.get("deadline", self.negotiator_config.default_deadline)
        
        # Adjust based on strategy
        if self.negotiator_config.strategy == "competitive":
            price_multiplier = 1.3
            deadline_adjust = -5
        elif self.negotiator_config.strategy == "collaborative":
            price_multiplier = 1.1
            deadline_adjust = -2
        else:  # principled
            price_multiplier = 1.15
            deadline_adjust = -3
        
        counter_terms = {
            "price": min(price * price_multiplier, self.negotiator_config.max_price),
            "deadline": max(deadline + deadline_adjust, 1),
            "scope": terms.get("scope", "Standard scope"),
            "quality": terms.get("quality", "standard"),
            "priority": terms.get("priority", "normal"),
            "counter_offer": True,
        }
        
        # Add escrow if required
        if self.negotiator_config.require_escrow:
            counter_terms["escrow"] = True
        
        return {
            "terms": counter_terms,
            "metadata": {
                "counter_generated": True,
                "strategy": self.negotiator_config.strategy,
                "score": score,
                "timestamp": datetime.now().isoformat(),
            }
        }
    
    def _adjust_counter_offer(self, terms: Dict, score: float) -> Dict:
        """Adjust terms slightly for counter-offer."""
        counter_terms = terms.copy()
        
        # Slight adjustments
        if "price" in counter_terms:
            counter_terms["price"] = counter_terms["price"] * 1.05
        
        if "deadline" in counter_terms:
            counter_terms["deadline"] = max(counter_terms["deadline"] - 1, 1)
        
        counter_terms["counter_offer"] = True
        
        return {
            "terms": counter_terms,
            "metadata": {
                "counter_generated": True,
                "strategy": self.negotiator_config.strategy,
                "score": score,
                "adjustment": "minor",
                "timestamp": datetime.now().isoformat(),
            }
        }
    
    def _create_contract(self, negotiation_id: str, proposal: Dict, parties: List[str]) -> Dict:
        """Create a contract from negotiation results."""
        terms = proposal.get("terms", {})
        
        contract = {
            "id": f"ctr_{negotiation_id}",
            "parties": parties,
            "terms": terms,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=terms.get("deadline", 30))).isoformat(),
            "negotiation_id": negotiation_id,
            "metadata": {
                "version": "3.0.0",
                "escrow": self.negotiator_config.require_escrow,
                "strategy": self.negotiator_config.strategy,
            }
        }
        
        return contract
    
    def _verify_signature(self, contract: Dict, signature: str, agent_id: str) -> bool:
        """Verify contract signature."""
        # Simplified verification
        # In production, this would use actual cryptographic verification
        return len(signature) > 0 and len(signature) > 16
    
    # ============================================================
    # Public Methods
    # ============================================================
    
    def get_negotiation(self, negotiation_id: str) -> Optional[Dict[str, Any]]:
        """Get negotiation details."""
        return self._negotiations.get(negotiation_id)
    
    def list_negotiations(self) -> List[Dict[str, Any]]:
        """List all negotiations."""
        return [{
            "id": n["id"],
            "status": n["status"],
            "counterparty": n.get("counterparty"),
            "round": n.get("round", 1),
            "created_at": n.get("created_at"),
            "updated_at": n.get("updated_at"),
        } for n in self._negotiations.values()]
    
    def register_template(self, name: str, template: Dict[str, Any]) -> None:
        """Register a contract template."""
        self._templates[name] = template
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a contract template."""
        return self._templates.get(name)