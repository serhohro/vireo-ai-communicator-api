"""Verification Engine for Vireo v2.0.1"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import base64
import logging

from ..contract.contract import Contract
from ..contract.validator import ContractValidator

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Verification status"""
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"


@dataclass
class VerificationResult:
    """Verification result"""
    status: VerificationStatus
    proof: Optional[str] = None
    errors: List[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.details is None:
            self.details = {}


class Verifier:
    """Verifies contract execution"""
    
    def __init__(self):
        self._validator = ContractValidator()
        self._logger = logging.getLogger(__name__)
    
    def verify_contract(self, contract: Contract, results: Dict[str, Any]) -> VerificationResult:
        """Verify contract execution"""
        errors = []
        details = {}
        
        # 1. Validate contract
        contract_errors = self._validator.validate(contract)
        if contract_errors:
            errors.extend(contract_errors)
            return VerificationResult(
                status=VerificationStatus.FAILED,
                errors=errors,
                details={"contract_validation_errors": contract_errors}
            )
        
        # 2. Verify signatures
        for party in contract.parties:
            if party not in contract.signatures:
                errors.append(f"Missing signature from {party}")
                details[f"{party}_signature"] = "missing"
            else:
                # In production, verify signature cryptographically
                details[f"{party}_signature"] = "present"
        
        if errors:
            return VerificationResult(
                status=VerificationStatus.FAILED,
                errors=errors,
                details=details
            )
        
        # 3. Verify outputs match obligations
        for party, obligation in contract.obligations.items():
            if obligation.output:
                for field, expected in obligation.output.items():
                    if party not in results:
                        errors.append(f"No results from {party}")
                        continue
                    
                    result = results[party]
                    if result.get("success", False):
                        result_data = result.get("result", {})
                        if field not in result_data:
                            errors.append(f"Missing output field '{field}' from {party}")
                            details[f"{party}_output_{field}"] = "missing"
        
        # 4. Verify constraints
        if contract.terms:
            total_tokens = 0
            for party, result in results.items():
                if result.get("success", False):
                    tokens = result.get("result", {}).get("tokens", 0)
                    total_tokens += tokens
            
            if contract.terms.max_tokens is not None:
                if total_tokens > contract.terms.max_tokens:
                    errors.append(
                        f"Token limit exceeded: {total_tokens} > {contract.terms.max_tokens}"
                    )
                    details["total_tokens"] = total_tokens
        
        # 5. Generate proof
        if not errors:
            proof_data = {
                "contract_id": contract.contract_id,
                "parties": contract.parties,
                "results": results,
                "verified_at": "2026-01-15T10:30:00Z"
            }
            proof_json = json.dumps(proof_data, sort_keys=True)
            proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
            
            return VerificationResult(
                status=VerificationStatus.PASSED,
                proof=proof_hash,
                details=details
            )
        
        return VerificationResult(
            status=VerificationStatus.FAILED,
            errors=errors,
            details=details
        )
    
    def verify_execution_result(self, contract: Contract, result: Dict[str, Any]) -> VerificationResult:
        """Verify a single execution result"""
        errors = []
        details = {}
        
        # Check contract status
        if contract.status not in ["executing", "verifying"]:
            errors.append("Contract not in executing/verifying state")
        
        # Check all parties executed
        for party in contract.parties:
            if party not in result:
                errors.append(f"Party {party} did not execute")
                details[f"{party}_executed"] = False
        
        return VerificationResult(
            status=VerificationStatus.PASSED if not errors else VerificationStatus.FAILED,
            errors=errors,
            details=details
        )
    
    def generate_verification_report(self, verification_result: VerificationResult) -> Dict[str, Any]:
        """Generate a human-readable verification report"""
        return {
            "status": verification_result.status.value,
            "passed": verification_result.status == VerificationStatus.PASSED,
            "errors": verification_result.errors,
            "details": verification_result.details,
            "proof": verification_result.proof,
            "timestamp": "2026-01-15T10:30:00Z"
        }