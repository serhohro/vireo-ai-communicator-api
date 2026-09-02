"""Execution Runner for Vireo v2.0.1"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import logging
import asyncio
import time

from ..contract.contract import Contract
from ..contract.validator import ContractValidator

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """Execution result"""
    status: ExecutionStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class ExecutionRunner:
    """Executes contracts and capabilities"""
    
    def __init__(self):
        self._executors: Dict[str, Callable] = {}
        self._validator = ContractValidator()
        self._logger = logging.getLogger(__name__)
    
    def register_executor(self, capability: str, func: Callable) -> None:
        """Register a capability executor"""
        self._executors[capability] = func
        self._logger.info(f"Registered executor for: {capability}")
    
    def execute_capability(self, capability: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability"""
        if capability not in self._executors:
            raise ValueError(f"Unknown capability: {capability}")
        
        self._logger.info(f"Executing capability: {capability}")
        try:
            result = self._executors[capability](**inputs)
            return {"success": True, "result": result}
        except Exception as e:
            self._logger.error(f"Execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_contract(self, contract: Contract, context: Dict[str, Any] = None) -> ExecutionResult:
        """Execute a contract"""
        context = context or {}
        start_time = time.time()
        
        # Validate contract
        if not self._validator.can_execute(contract, context):
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error="Contract validation failed",
                start_time=start_time,
                end_time=time.time()
            )
        
        # Execute obligations
        results = {}
        for party, obligation in contract.obligations.items():
            if obligation.depends_on:
                # Check dependencies
                deps_ready = all(dep in results for dep in obligation.depends_on)
                if not deps_ready:
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        error=f"Missing dependencies for {party}: {obligation.depends_on}",
                        start_time=start_time,
                        end_time=time.time()
                    )
            
            # Execute
            result = self.execute_capability(
                obligation.action,
                obligation.input
            )
            results[party] = result
            
            if not result.get("success", False):
                if contract.on_failure == "escalate":
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        error=f"Escalated: {result.get('error', 'Unknown error')}",
                        start_time=start_time,
                        end_time=time.time()
                    )
                else:
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        error=result.get("error", "Unknown error"),
                        start_time=start_time,
                        end_time=time.time()
                    )
        
        return ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            result=results,
            start_time=start_time,
            end_time=time.time()
        )
    
    async def execute_contract_async(self, contract: Contract, timeout_sec: Optional[int] = None) -> ExecutionResult:
        """Execute a contract asynchronously"""
        timeout = timeout_sec or contract.terms.timeout_sec or 60
        
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self.execute_contract, contract),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error=f"Execution timed out after {timeout} seconds"
            )