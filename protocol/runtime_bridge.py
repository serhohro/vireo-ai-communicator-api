# ============================================================
# VIREO RUNTIME BRIDGE
# ============================================================
"""
Runtime bridge between Vireo protocol and execution engine.

Provides:
- Async execution of Vireo code
- Bridge between protocol layer and runtime
- Support for different executors (Python, WASM, etc.)
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of code execution."""
    status: str  # success, error, timeout
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used_mb: float = 0.0


class RuntimeBridge:
    """
    Bridge between Vireo protocol and runtime engine.
    
    Features:
    - Async execution
    - Multiple executor support
    - Timeout handling
    - Resource tracking
    """
    
    def __init__(self, default_timeout: int = 60):
        self.default_timeout = default_timeout
        self._executors: Dict[str, Callable] = {}
        self._default_executor: Optional[Callable] = None
        self._history: list = []
    
    def register_executor(self, name: str, executor: Callable[[str], Awaitable[Any]]) -> None:
        """
        Register an async executor.
        
        Args:
            name: Executor name
            executor: Async function that takes code and returns result
        """
        self._executors[name] = executor
        if self._default_executor is None:
            self._default_executor = executor
        logger.info(f"✅ Registered executor: {name}")
    
    def set_default_executor(self, name: str) -> None:
        """Set default executor by name."""
        if name not in self._executors:
            raise ValueError(f"Executor not found: {name}")
        self._default_executor = self._executors[name]
        logger.info(f"✅ Default executor set to: {name}")
    
    async def execute(self, code: str, 
                      executor_name: Optional[str] = None,
                      timeout_sec: Optional[int] = None) -> ExecutionResult:
        """
        Execute Vireo code asynchronously.
        
        Args:
            code: Vireo code to execute
            executor_name: Name of executor to use
            timeout_sec: Timeout in seconds (overrides default)
        
        Returns:
            ExecutionResult with status, result, and metrics
        """
        # Select executor
        executor = self._default_executor
        if executor_name and executor_name in self._executors:
            executor = self._executors[executor_name]
        
        if executor is None:
            return ExecutionResult(
                status="error",
                error="No executor registered"
            )
        
        timeout = timeout_sec or self.default_timeout
        import time
        start_time = time.time()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                executor(code),
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            execution_result = ExecutionResult(
                status="success",
                result=result,
                execution_time=execution_time
            )
            
            self._history.append(execution_result)
            return execution_result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return ExecutionResult(
                status="timeout",
                error=f"Execution timed out after {timeout}s",
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                status="error",
                error=str(e),
                execution_time=execution_time
            )
    
    async def execute_with_contract(self, code: str, 
                                    contract: Any,
                                    executor_name: Optional[str] = None) -> ExecutionResult:
        """
        Execute code with contract validation.
        
        Args:
            code: Vireo code to execute
            contract: Contract with resource limits
            executor_name: Name of executor to use
        
        Returns:
            ExecutionResult with status, result, and metrics
        """
        # Validate contract first
        if contract:
            from .contract import Contract
            if isinstance(contract, Contract):
                # Check resource limits
                if contract.max_tokens is not None:
                    # Estimate tokens from code length
                    estimated_tokens = len(code) // 4
                    if estimated_tokens > contract.max_tokens:
                        return ExecutionResult(
                            status="error",
                            error=f"Token limit exceeded: {estimated_tokens} > {contract.max_tokens}"
                        )
                
                if contract.timeout_sec is not None:
                    timeout_sec = contract.timeout_sec
                else:
                    timeout_sec = self.default_timeout
            else:
                timeout_sec = self.default_timeout
        else:
            timeout_sec = self.default_timeout
        
        # Execute with contract timeout
        return await self.execute(code, executor_name, timeout_sec)
    
    def get_history(self) -> list:
        """Get execution history."""
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self._history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total = len(self._history)
        success = sum(1 for r in self._history if r.status == "success")
        errors = sum(1 for r in self._history if r.status == "error")
        timeouts = sum(1 for r in self._history if r.status == "timeout")
        
        avg_time = 0.0
        if total > 0:
            avg_time = sum(r.execution_time for r in self._history) / total
        
        return {
            "total_executions": total,
            "success": success,
            "errors": errors,
            "timeouts": timeouts,
            "avg_execution_time": avg_time,
            "executors": list(self._executors.keys())
        }
    
    def list_executors(self) -> list:
        """List registered executors."""
        return list(self._executors.keys())


# ============================================================
# DEFAULT EXECUTOR
# ============================================================

def _default_python_executor(code: str) -> Awaitable[Any]:
    """Default Python executor."""
    import asyncio
    
    async def execute():
        # Simple executor - can be extended
        try:
            # Use exec with captured output
            import io
            import sys
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                exec(code, {}, {})
            
            output = f.getvalue()
            return {"output": output, "status": "success"}
        except Exception as e:
            return {"output": "", "error": str(e), "status": "error"}
    
    return execute()


def create_runtime_bridge() -> RuntimeBridge:
    """Create a RuntimeBridge with default executor."""
    bridge = RuntimeBridge()
    
    # Register default executor
    bridge.register_executor("python", _default_python_executor)
    
    return bridge


# ============================================================
# SINGLETON
# ============================================================

_default_bridge: Optional[RuntimeBridge] = None


def get_runtime_bridge() -> RuntimeBridge:
    """Get the global RuntimeBridge instance."""
    global _default_bridge
    if _default_bridge is None:
        _default_bridge = create_runtime_bridge()
    return _default_bridge


def real_vireo_executor(code: str) -> Any:
    """
    Real Vireo executor (synchronous wrapper for bridge).
    
    This is used by the Agent class for synchronous execution.
    """
    import asyncio
    
    bridge = get_runtime_bridge()
    
    # Run async execution synchronously
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new task
            future = asyncio.ensure_future(bridge.execute(code))
            return asyncio.run_coroutine_threadsafe(future, loop).result()
        else:
            return loop.run_until_complete(bridge.execute(code))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(bridge.execute(code))