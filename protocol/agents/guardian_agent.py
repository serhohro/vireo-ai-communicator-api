"""
Vireo Guardian Agent

Protocol enforcement and security guardian agent.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from ..agent import Agent, AgentConfig
from core.protocol import Message, Protocol, State
from core.crypto import ed25519, blake2b
from core.identity import DID, TrustBootstrap

logger = logging.getLogger(__name__)


class GuardianConfig(AgentConfig):
    """Configuration for Guardian agent."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capabilities = ["guardian", "security", "verification", "audit"]
        self.enforce_protocol: bool = kwargs.get("enforce_protocol", True)
        self.enforce_signatures: bool = kwargs.get("enforce_signatures", True)
        self.enforce_nonces: bool = kwargs.get("enforce_nonces", True)
        self.rate_limit: int = kwargs.get("rate_limit", 100)
        self.rate_window: int = kwargs.get("rate_window", 60)
        self.audit_log: bool = kwargs.get("audit_log", True)
        self.trust_threshold: float = kwargs.get("trust_threshold", 0.5)
        self.auto_escalate: bool = kwargs.get("auto_escalate", True)


class GuardianAgent(Agent):
    """
    Guardian Agent for protocol enforcement and security.
    
    Responsibilities:
    - Enforce protocol compliance
    - Verify signatures and nonces
    - Rate limiting and DoS protection
    - Audit logging
    - Trust verification
    - Escalation handling
    """
    
    def __init__(self, config: GuardianConfig):
        super().__init__(config)
        self.guardian_config = config
        
        # Rate limiting
        self._rate_counts: Dict[str, List[float]] = {}
        
        # Trust bootstrap
        self.trust_bootstrap = TrustBootstrap()
        
        # Audit log
        self._audit_log: List[Dict[str, Any]] = []
        self._max_audit_size = 10000
        
        # Blocked agents
        self._blocked_agents: set = set()
        
        # Configure
        self._setup_handlers()
        
        logger.info(f"Guardian Agent initialized: {self.id}")
    
    def _setup_handlers(self) -> None:
        """Setup message handlers."""
        self.on_message("*", self._guardian_intercept)
        self.on_message("escalate", self._handle_escalate)
        self.on_message("verify", self._handle_verify)
    
    # ============================================================
    # Guardian Intercept
    # ============================================================
    
    async def _guardian_intercept(self, message: Message) -> Optional[Message]:
        """
        Intercept all messages for security checking.
        
        This is the main guard function that validates all messages.
        """
        # Check blocklist
        if message.sender in self._blocked_agents:
            logger.warning(f"Blocked agent attempted communication: {message.sender}")
            return self._create_error_response(
                message,
                "agent_blocked",
                "Your agent is blocked from communication"
            )
        
        # Rate limit check
        if self.guardian_config.rate_limit > 0:
            if not self._check_rate_limit(message.sender):
                logger.warning(f"Rate limit exceeded for: {message.sender}")
                return self._create_error_response(
                    message,
                    "rate_limit_exceeded",
                    f"Rate limit exceeded. Max {self.guardian_config.rate_limit} per {self.guardian_config.rate_window}s"
                )
        
        # Signature verification
        if self.guardian_config.enforce_signatures:
            if not self._verify_message_signature(message):
                logger.warning(f"Invalid signature from: {message.sender}")
                return self._create_error_response(
                    message,
                    "invalid_signature",
                    "Message signature verification failed"
                )
        
        # Nonce verification
        if self.guardian_config.enforce_nonces:
            if not self._verify_nonce(message):
                logger.warning(f"Invalid nonce from: {message.sender}")
                return self._create_error_response(
                    message,
                    "invalid_nonce",
                    "Invalid or replayed nonce"
                )
        
        # Trust verification
        if self.guardian_config.trust_threshold > 0:
            if not await self._verify_trust(message.sender):
                logger.warning(f"Low trust score for: {message.sender}")
                return self._create_error_response(
                    message,
                    "low_trust",
                    f"Trust score below threshold ({self.guardian_config.trust_threshold})"
                )
        
        # Audit logging
        if self.guardian_config.audit_log:
            self._log_audit(message, "passed")
        
        # Protocol enforcement
        if self.guardian_config.enforce_protocol:
            if not self._enforce_protocol(message):
                logger.warning(f"Protocol violation from: {message.sender}")
                return self._create_error_response(
                    message,
                    "protocol_violation",
                    "Protocol state violation detected"
                )
        
        # Allow message to proceed
        return None  # None means continue processing
    
    # ============================================================
    # Security Checks
    # ============================================================
    
    def _check_rate_limit(self, agent_id: str) -> bool:
        """Check if agent has exceeded rate limit."""
        if agent_id not in self._rate_counts:
            self._rate_counts[agent_id] = []
        
        now = datetime.now().timestamp()
        window_start = now - self.guardian_config.rate_window
        
        # Clean old entries
        self._rate_counts[agent_id] = [
            t for t in self._rate_counts[agent_id]
            if t >= window_start
        ]
        
        # Check limit
        if len(self._rate_counts[agent_id]) >= self.guardian_config.rate_limit:
            return False
        
        # Record
        self._rate_counts[agent_id].append(now)
        return True
    
    def _verify_message_signature(self, message: Message) -> bool:
        """Verify message signature."""
        if not message.signature:
            return False
        
        try:
            # Get public key
            public_key = self.key_manager.get_public_key(message.sender)
            if not public_key:
                return False
            
            # Verify
            data = message.to_bytes_without_signature()
            return ed25519.Ed25519.verify(data, message.signature, public_key)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def _verify_nonce(self, message: Message) -> bool:
        """Verify nonce for replay protection."""
        if not message.nonce:
            return False
        
        # Check if nonce already used
        if hasattr(self, '_used_nonces'):
            if message.nonce in self._used_nonces:
                return False
            self._used_nonces.add(message.nonce)
        else:
            self._used_nonces = set()
            self._used_nonces.add(message.nonce)
        
        return True
    
    async def _verify_trust(self, agent_id: str) -> bool:
        """Verify agent trust score."""
        try:
            score = await self.trust_bootstrap.get_trust_score(agent_id)
            return score >= self.guardian_config.trust_threshold
        except Exception as e:
            logger.error(f"Trust verification error: {e}")
            return False
    
    def _enforce_protocol(self, message: Message) -> bool:
        """Enforce protocol state machine."""
        # Check if message type is valid for current state
        # This is a simplified check
        valid_transitions = {
            "idle": ["propose", "discover", "heartbeat"],
            "propose": ["commit", "cancel", "heartbeat"],
            "commit": ["execute", "escalate", "heartbeat"],
            "execute": ["verify", "escalate", "done", "heartbeat"],
            "verify": ["done", "escalate", "heartbeat"],
            "escalate": ["done", "cancel", "heartbeat"],
            "done": ["heartbeat"],
            "cancel": ["heartbeat"],
        }
        
        # Get current state from protocol
        current_state = self.protocol.get_state().lower()
        if current_state not in valid_transitions:
            return True  # Unknown state, allow
        
        if message.type not in valid_transitions[current_state]:
            # Check if it's a valid message type
            if message.type in ["error", "heartbeat"]:
                return True
            return False
        
        return True
    
    # ============================================================
    # Special Handlers
    # ============================================================
    
    async def _handle_escalate(self, message: Message) -> Optional[Message]:
        """Handle escalation messages."""
        logger.warning(f"Escalation received from {message.sender}")
        
        # Log escalation
        self._log_audit(message, "escalation")
        
        # Notify admin
        await self._notify_admin(message)
        
        # Auto-escalate if configured
        if self.guardian_config.auto_escalate:
            # Forward to arbitrator
            await self._forward_to_arbitrator(message)
        
        return Message(
            type="escalate_response",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "status": "received",
                "timestamp": datetime.now().isoformat(),
                "action": "escalation_handled",
                "details": {
                    "case_id": f"ESC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "priority": "high",
                }
            }
        )
    
    async def _handle_verify(self, message: Message) -> Optional[Message]:
        """Handle verification requests."""
        # Verify the message payload
        data_to_verify = message.payload.get("data")
        signature = message.payload.get("signature")
        agent_id = message.payload.get("agent_id")
        
        if not data_to_verify or not signature or not agent_id:
            return self._create_error_response(
                message,
                "invalid_verification_request",
                "Missing data, signature, or agent_id"
            )
        
        # Get public key
        public_key = self.key_manager.get_public_key(agent_id)
        if not public_key:
            return self._create_error_response(
                message,
                "agent_not_found",
                f"Public key not found for {agent_id}"
            )
        
        # Verify
        is_valid = ed25519.Ed25519.verify(
            data_to_verify.encode() if isinstance(data_to_verify, str) else data_to_verify,
            signature,
            public_key
        )
        
        return Message(
            type="verify_response",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "verified": is_valid,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    # ============================================================
    # Blocklist Management
    # ============================================================
    
    def block_agent(self, agent_id: str, reason: str = None) -> None:
        """Block an agent."""
        self._blocked_agents.add(agent_id)
        logger.info(f"Blocked agent: {agent_id} ({reason or 'No reason provided'})")
        
        if self.guardian_config.audit_log:
            self._log_audit(
                {"sender": agent_id, "type": "block"},
                "block"
            )
    
    def unblock_agent(self, agent_id: str) -> None:
        """Unblock an agent."""
        if agent_id in self._blocked_agents:
            self._blocked_agents.remove(agent_id)
            logger.info(f"Unblocked agent: {agent_id}")
    
    def is_blocked(self, agent_id: str) -> bool:
        """Check if an agent is blocked."""
        return agent_id in self._blocked_agents
    
    # ============================================================
    # Audit Logging
    # ============================================================
    
    def _log_audit(self, message: Any, action: str) -> None:
        """Log an audit entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "agent_id": getattr(message, 'sender', 'unknown'),
            "message_id": getattr(message, 'id', 'unknown'),
            "message_type": getattr(message, 'type', 'unknown'),
        }
        
        self._audit_log.append(entry)
        
        # Trim log
        if len(self._audit_log) > self._max_audit_size:
            self._audit_log = self._audit_log[-self._max_audit_size:]
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        return self._audit_log[-limit:]
    
    def clear_audit_log(self) -> None:
        """Clear audit log."""
        self._audit_log.clear()
    
    # ============================================================
    # Helpers
    # ============================================================
    
    def _create_error_response(self, original: Message, code: str, message: str) -> Message:
        """Create an error response."""
        return Message(
            type="error",
            sender=self.id,
            recipient=original.sender,
            in_response_to=original.id,
            payload={
                "error": {
                    "code": code,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "guardian_id": self.id,
                }
            }
        )
    
    async def _notify_admin(self, message: Message) -> None:
        """Notify admin about escalation."""
        # Placeholder for admin notification
        logger.info(f"Admin notification: Escalation from {message.sender}")
    
    async def _forward_to_arbitrator(self, message: Message) -> None:
        """Forward escalation to arbitrator."""
        # Placeholder for forwarding
        logger.info(f"Forwarding escalation to arbitrator")