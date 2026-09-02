"""Contract Validator for Vireo v2.0.1"""

from typing import List, Optional, Dict, Any
import logging

from .contract import Contract, Terms

logger = logging.getLogger(__name__)


class ContractValidator:
    """Validates contracts and contract terms"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    def validate(self, contract: Contract) -> List[str]:
        """Validate a contract"""
        errors = contract.validate()
        return errors
    
    def validate_terms(self, terms: Terms) -> List[str]:
        """Validate terms independently"""
        return terms.validate()
    
    def validate_obligations(self, contract: Contract) -> List[str]:
        """Validate obligations"""
        errors = []
        
        for party, obligation in contract.obligations.items():
            if party not in contract.parties:
                errors.append(f"Party '{party}' not in parties list")
            
            if not obligation.action:
                errors.append(f"Obligation for '{party}' missing action")
            
            # Check input types
            if obligation.input:
                for key, value in obligation.input.items():
                    if not key:
                        errors.append(f"Invalid input key for '{party}': {key}")
        
        return errors
    
    def check_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Check a condition against context"""
        if not condition:
            return True
        
        # Basic condition evaluation
        # This is a simplified implementation
        try:
            # Replace references
            expr = condition
            for key, value in context.items():
                if isinstance(value, (int, float, str, bool)):
                    expr = expr.replace(f"$ref.{key}", str(value))
                    expr = expr.replace(f"{{{key}}}", str(value))
            
            # Evaluate
            return eval(expr, {"__builtins__": {}}, {})
        except Exception as e:
            self._logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def can_execute(self, contract: Contract, context: Dict[str, Any]) -> bool:
        """Check if contract can be executed"""
        # Validate contract
        errors = self.validate(contract)
        if errors:
            self._logger.error(f"Contract validation failed: {errors}")
            return False
        
        # Check condition
        if not self.check_condition(contract.condition, context):
            self._logger.warning(f"Condition not met: {contract.condition}")
            return False
        
        # Check signatures
        if not contract.is_signed():
            self._logger.warning("Contract not fully signed")
            return False
        
        return True