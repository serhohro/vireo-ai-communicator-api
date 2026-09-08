"""
Vireo Verifier Agent

Specialized agent for result verification and validation.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

from ..agent import Agent, AgentConfig
from core.protocol import Message
from core.crypto import ed25519, blake2b

logger = logging.getLogger(__name__)


class VerifierConfig(AgentConfig):
    """Configuration for Verifier agent."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capabilities = ["verifier", "validation", "audit"]
        self.verification_timeout: int = kwargs.get("verification_timeout", 60)
        self.require_multiple_verifiers: int = kwargs.get("require_multiple_verifiers", 1)
        self.verification_threshold: float = kwargs.get("verification_threshold", 0.8)
        self.max_verification_attempts: int = kwargs.get("max_verification_attempts", 3)
        self.enable_audit_trail: bool = kwargs.get("enable_audit_trail", True)


class VerifierAgent(Agent):
    """
    Verifier Agent for result verification.
    
    Capabilities:
    - Result verification
    - Multi-verifier consensus
    - Audit trail
    - Validation rules
    - Integrity checking
    """
    
    def __init__(self, config: VerifierConfig):
        super().__init__(config)
        self.verifier_config = config
        
        # Verification records
        self._verifications: Dict[str, Dict[str, Any]] = {}
        self._validation_rules: Dict[str, Callable] = {}
        
        # Audit trail
        self._audit_trail: List[Dict[str, Any]] = []
        
        # Setup handlers
        self._setup_handlers()
        
        logger.info(f"Verifier Agent initialized: {self.id}")
    
    def _setup_handlers(self) -> None:
        """Setup message handlers."""
        self.on_message("verify", self._handle_verify)
        self.on_message("verify_result", self._handle_verify_result)
        self.on_message("validation_status", self._handle_validation_status)
    
    # ============================================================
    # Verification Handlers
    # ============================================================
    
    async def _handle_verify(self, message: Message) -> Optional[Message]:
        """Handle verification request."""
        verification_id = message.payload.get("verification_id", f"ver_{int(datetime.now().timestamp())}_{self.id[:8]}")
        data = message.payload.get("data")
        expected = message.payload.get("expected")
        verification_type = message.payload.get("type", "integrity")
        
        if data is None:
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "error": "No data provided for verification",
                    "verification_id": verification_id,
                }
            )
        
        # Store verification record
        record = {
            "id": verification_id,
            "type": verification_type,
            "data": data,
            "expected": expected,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "requester": message.sender,
            "message_id": message.id,
            "attempts": 0,
            "verifications": [],
        }
        
        self._verifications[verification_id] = record
        
        # Perform verification
        result = await self._perform_verification(record)
        
        record["status"] = "completed"
        record["completed_at"] = datetime.now().isoformat()
        record["result"] = result
        
        # Audit trail
        if self.verifier_config.enable_audit_trail:
            self._add_audit_entry(record, result)
        
        # Check if multiple verifiers needed
        if self.verifier_config.require_multiple_verifiers > 1:
            return Message(
                type="verification_partial",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "verification_id": verification_id,
                    "status": "partial",
                    "result": result,
                    "verifiers_needed": self.verifier_config.require_multiple_verifiers,
                    "verifiers_done": 1,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        
        return Message(
            type="verification_result",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "verification_id": verification_id,
                "verified": result.get("verified", False),
                "score": result.get("score", 0),
                "details": result.get("details", {}),
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    async def _handle_verify_result(self, message: Message) -> Optional[Message]:
        """Handle external verification result."""
        verification_id = message.payload.get("verification_id")
        verifier_id = message.payload.get("verifier_id")
        result = message.payload.get("result", {})
        
        if verification_id not in self._verifications:
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "error": f"Verification not found: {verification_id}",
                }
            )
        
        record = self._verifications[verification_id]
        
        # Add verification
        record["verifications"].append({
            "verifier": verifier_id,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Check if we have enough verifications
        if len(record["verifications"]) >= self.verifier_config.require_multiple_verifiers:
            # Combine results
            combined = self._combine_verifications(record["verifications"])
            record["combined_result"] = combined
            record["status"] = "completed"
            record["completed_at"] = datetime.now().isoformat()
            
            return Message(
                type="verification_final",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "verification_id": verification_id,
                    "verified": combined.get("verified", False),
                    "score": combined.get("score", 0),
                    "verifiers": len(record["verifications"]),
                    "details": combined.get("details", {}),
                    "timestamp": datetime.now().isoformat(),
                }
            )
        
        return Message(
            type="verification_pending",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "verification_id": verification_id,
                "verifiers_received": len(record["verifications"]),
                "verifiers_needed": self.verifier_config.require_multiple_verifiers,
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    async def _handle_validation_status(self, message: Message) -> Optional[Message]:
        """Handle validation status request."""
        verification_id = message.payload.get("verification_id")
        
        if verification_id not in self._verifications:
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "error": f"Verification not found: {verification_id}",
                }
            )
        
        record = self._verifications[verification_id]
        
        return Message(
            type="validation_status",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "verification_id": verification_id,
                "status": record.get("status"),
                "verified": record.get("result", {}).get("verified", False),
                "score": record.get("result", {}).get("score", 0),
                "timestamp": record.get("completed_at"),
            }
        )
    
    # ============================================================
    # Verification Logic
    # ============================================================
    
    async def _perform_verification(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Perform verification based on type."""
        verification_type = record.get("type", "integrity")
        
        if verification_type == "integrity":
            return self._verify_integrity(record)
        elif verification_type == "signature":
            return self._verify_signature(record)
        elif verification_type == "schema":
            return self._verify_schema(record)
        elif verification_type == "custom":
            return self._verify_custom(record)
        else:
            return {
                "verified": False,
                "score": 0,
                "details": {
                    "error": f"Unknown verification type: {verification_type}"
                }
            }
    
    def _verify_integrity(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data integrity using hash."""
        data = record.get("data")
        expected = record.get("expected")
        
        # Calculate hash
        if isinstance(data, str):
            data_bytes = data.encode()
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, sort_keys=True).encode()
        else:
            data_bytes = str(data).encode()
        
        # Use BLAKE2b
        actual = blake2b.blake2b(data_bytes)
        actual_hex = actual.hex()
        
        verified = actual_hex == expected
        
        return {
            "verified": verified,
            "score": 1.0 if verified else 0.0,
            "details": {
                "algorithm": "BLAKE2b",
                "expected": expected,
                "actual": actual_hex,
                "verified": verified,
            }
        }
    
    def _verify_signature(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Verify cryptographic signature."""
        data = record.get("data")
        expected = record.get("expected")  # {signature, public_key}
        
        if not expected or "signature" not in expected or "public_key" not in expected:
            return {
                "verified": False,
                "score": 0,
                "details": {"error": "Missing signature or public key"}
            }
        
        try:
            if isinstance(data, str):
                data_bytes = data.encode()
            elif isinstance(data, dict):
                data_bytes = json.dumps(data, sort_keys=True).encode()
            else:
                data_bytes = str(data).encode()
            
            signature = bytes.fromhex(expected["signature"])
            public_key = bytes.fromhex(expected["public_key"])
            
            verified = ed25519.Ed25519.verify(
                data_bytes,
                signature,
                public_key
            )
            
            return {
                "verified": verified,
                "score": 1.0 if verified else 0.0,
                "details": {
                    "algorithm": "Ed25519",
                    "verified": verified,
                }
            }
        except Exception as e:
            return {
                "verified": False,
                "score": 0,
                "details": {"error": str(e)}
            }
    
    def _verify_schema(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data against schema."""
        data = record.get("data")
        expected = record.get("expected")  # schema definition
        
        if not expected:
            return {
                "verified": False,
                "score": 0,
                "details": {"error": "Missing schema"}
            }
        
        try:
            # Simple schema validation
            errors = []
            for field, field_type in expected.items():
                if field not in data:
                    errors.append(f"Missing field: {field}")
                else:
                    if not isinstance(data[field], field_type):
                        errors.append(f"Invalid type for {field}: expected {field_type}")
            
            verified = len(errors) == 0
            score = 1.0 - (len(errors) / len(expected)) if expected else 0
            
            return {
                "verified": verified,
                "score": max(0, score),
                "details": {
                    "errors": errors,
                    "verified": verified,
                }
            }
        except Exception as e:
            return {
                "verified": False,
                "score": 0,
                "details": {"error": str(e)}
            }
    
    def _verify_custom(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Perform custom verification."""
        data = record.get("data")
        expected = record.get("expected")
        
        # Use custom validation rules
        if "rule_name" in expected:
            rule_name = expected["rule_name"]
            if rule_name in self._validation_rules:
                try:
                    result = self._validation_rules[rule_name](data, expected.get("params", {}))
                    return {
                        "verified": result.get("verified", False),
                        "score": result.get("score", 0),
                        "details": result.get("details", {})
                    }
                except Exception as e:
                    return {
                        "verified": False,
                        "score": 0,
                        "details": {"error": str(e)}
                    }
        
        return {
            "verified": False,
            "score": 0,
            "details": {"error": "No matching validation rule"}
        }
    
    def _combine_verifications(self, verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple verification results."""
        scores = []
        details = []
        verified_count = 0
        
        for v in verifications:
            result = v.get("result", {})
            if result.get("verified", False):
                verified_count += 1
            scores.append(result.get("score", 0))
            details.append(result.get("details", {}))
        
        avg_score = sum(scores) / len(scores) if scores else 0
        threshold = self.verifier_config.verification_threshold
        
        return {
            "verified": avg_score >= threshold,
            "score": avg_score,
            "details": {
                "verifications": len(verifications),
                "verified_count": verified_count,
                "scores": scores,
                "details": details,
                "threshold": threshold,
            }
        }
    
    # ============================================================
    # Validation Rules
    # ============================================================
    
    def register_validation_rule(self, name: str, rule: Callable) -> None:
        """
        Register a custom validation rule.
        
        Args:
            name: Rule name
            rule: Function that takes (data, params) and returns dict with verified, score, details
        """
        self._validation_rules[name] = rule
        logger.info(f"Registered validation rule: {name}")
    
    def unregister_validation_rule(self, name: str) -> bool:
        """Unregister a validation rule."""
        if name in self._validation_rules:
            del self._validation_rules[name]
            return True
        return False
    
    # ============================================================
    # Audit Trail
    # ============================================================
    
    def _add_audit_entry(self, record: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Add an audit entry."""
        entry = {
            "id": record.get("id"),
            "type": record.get("type"),
            "status": record.get("status"),
            "verified": result.get("verified", False),
            "score": result.get("score", 0),
            "timestamp": datetime.now().isoformat(),
            "requester": record.get("requester"),
            "details": result.get("details", {}),
        }
        self._audit_trail.append(entry)
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail entries."""
        return self._audit_trail[-limit:]
    
    def clear_audit_trail(self) -> None:
        """Clear audit trail."""
        self._audit_trail.clear()
    
    # ============================================================
    # Public Methods
    # ============================================================
    
    def get_verification(self, verification_id: str) -> Optional[Dict[str, Any]]:
        """Get verification record."""
        return self._verifications.get(verification_id)
    
    def list_verifications(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List verification records."""
        verifications = []
        for vid, record in self._verifications.items():
            if status and record.get("status") != status:
                continue
            verifications.append({
                "id": vid,
                "type": record.get("type"),
                "status": record.get("status"),
                "verified": record.get("result", {}).get("verified", False),
                "score": record.get("result", {}).get("score", 0),
                "created_at": record.get("created_at"),
            })
        return verifications
    
    def get_stats(self) -> Dict[str, Any]:
        """Get verification statistics."""
        total = len(self._verifications)
        verified = sum(1 for r in self._verifications.values() 
                       if r.get("result", {}).get("verified", False))
        failed = total - verified
        
        return {
            "total": total,
            "verified": verified,
            "failed": failed,
            "success_rate": (verified / total * 100) if total > 0 else 0,
            "audit_size": len(self._audit_trail),
        }