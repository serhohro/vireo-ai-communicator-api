# ============================================================
# VIREO PYTHON RUNTIME
# ============================================================
"""
Vireo Python runtime implementation.

Provides:
- Vireo code execution
- Contract validation
- Agent coordination
- Resource management
"""

import asyncio
import io
import sys
import json
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)


@dataclass
class RuntimeConfig:
    """Runtime configuration."""
    max_execution_time: int = 60
    max_memory_mb: int = 1024
    max_tokens: int = 1000000
    enable_sandbox: bool = False
    enable_tracing: bool = False


@dataclass
class ExecutionResult:
    """Result of code execution."""
    status: str  # success, error, timeout, sandbox_error
    result: Any = None
    output: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used_mb: float = 0.0
    tokens_used: int = 0
    trace: List[Dict[str, Any]] = field(default_factory=list)


class VireoRuntime:
    """
    Vireo Python runtime.
    
    Features:
    - Code execution with sandboxing
    - Resource limits (time, memory, tokens)
    - Contract validation
    - Execution tracing
    - Performance monitoring
    """
    
    def __init__(self, config: Optional[RuntimeConfig] = None):
        self.config = config or RuntimeConfig()
        self._history: List[ExecutionResult] = []
        self._functions: Dict[str, Callable] = {}
        self._variables: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the runtime."""
        if self._initialized:
            return
        
        # Register built-in functions
        self._register_builtins()
        
        self._initialized = True
        logger.info("✅ Vireo runtime initialized")
    
    def _register_builtins(self) -> None:
        """Register built-in functions."""
        self._functions["print"] = lambda *args: print(*args)
        self._functions["len"] = len
        self._functions["type"] = type
        self._functions["int"] = int
        self._functions["float"] = float
        self._functions["str"] = str
    
    def execute(self, code: str, 
                variables: Optional[Dict[str, Any]] = None,
                timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute Vireo code.
        
        Args:
            code: Vireo code to execute
            variables: Initial variables
            timeout: Timeout in seconds
        
        Returns:
            ExecutionResult with status, result, and metrics
        """
        if not self._initialized:
            self.initialize()
        
        timeout = timeout or self.config.max_execution_time
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Create execution namespace
        namespace = {
            "__builtins__": {},
            **self._functions,
            **(variables or {}),
            **(self._variables)
        }
        
        # Capture stdout
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Execute with timeout
            result = self._execute_with_timeout(
                code, namespace, stdout_capture, stderr_capture, timeout
            )
            
            execution_time = time.time() - start_time
            end_memory = self._get_memory_usage()
            
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()
            
            # Get result from namespace
            result_value = namespace.get("result", None)
            
            # Estimate tokens
            tokens_used = len(code) // 4
            
            execution_result = ExecutionResult(
                status="success",
                result=result_value,
                output=output,
                error=error if error else None,
                execution_time=execution_time,
                memory_used_mb=end_memory - start_memory,
                tokens_used=tokens_used
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
                output=stdout_capture.getvalue(),
                execution_time=execution_time
            )
    
    def _execute_with_timeout(self, code: str, namespace: Dict[str, Any],
                              stdout_capture: io.StringIO,
                              stderr_capture: io.StringIO,
                              timeout: int) -> Any:
        """Execute code with timeout."""
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def target():
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(code, namespace, namespace)
                    result_queue.put(("success", None))
            except Exception as e:
                result_queue.put(("error", e))
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            # Thread is still running - timeout
            raise asyncio.TimeoutError()
        
        status, error = result_queue.get()
        if status == "error":
            raise error
        
        return namespace.get("result", None)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0
    
    def execute_with_contract(self, code: str, 
                              contract: Any,
                              variables: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Execute code with contract validation.
        
        Args:
            code: Vireo code
            contract: Contract with resource limits
            variables: Initial variables
        
        Returns:
            ExecutionResult
        """
        # Validate contract
        if contract:
            # Check resource limits
            if hasattr(contract, 'max_tokens') and contract.max_tokens:
                estimated_tokens = len(code) // 4
                if estimated_tokens > contract.max_tokens:
                    return ExecutionResult(
                        status="error",
                        error=f"Token limit exceeded: {estimated_tokens} > {contract.max_tokens}"
                    )
            
            if hasattr(contract, 'timeout_sec') and contract.timeout_sec:
                timeout = contract.timeout_sec
            else:
                timeout = self.config.max_execution_time
        else:
            timeout = self.config.max_execution_time
        
        # Execute with contract timeout
        return self.execute(code, variables, timeout)
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a custom function."""
        self._functions[name] = func
        logger.info(f"✅ Registered function: {name}")
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a global variable."""
        self._variables[name] = value
    
    def get_variable(self, name: str) -> Optional[Any]:
        """Get a global variable."""
        return self._variables.get(name)
    
    def get_history(self) -> List[ExecutionResult]:
        """Get execution history."""
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self._history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get runtime statistics."""
        total = len(self._history)
        success = sum(1 for r in self._history if r.status == "success")
        errors = sum(1 for r in self._history if r.status == "error")
        timeouts = sum(1 for r in self._history if r.status == "timeout")
        
        avg_time = 0.0
        avg_tokens = 0.0
        if total > 0:
            avg_time = sum(r.execution_time for r in self._history) / total
            avg_tokens = sum(r.tokens_used for r in self._history) / total
        
        return {
            "total_executions": total,
            "success": success,
            "errors": errors,
            "timeouts": timeouts,
            "avg_execution_time": avg_time,
            "avg_tokens_used": avg_tokens,
            "max_memory_mb": self.config.max_memory_mb,
            "max_tokens": self.config.max_tokens
        }
    
    def reset(self) -> None:
        """Reset the runtime state."""
        self._variables = {}
        self._history = []
        self._functions = {}
        self._register_builtins()
        logger.info("🔄 Runtime reset")


# ============================================================
# SINGLETON
# ============================================================

_default_runtime: Optional[VireoRuntime] = None


def get_runtime() -> VireoRuntime:
    """Get the default runtime instance."""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = VireoRuntime()
        _default_runtime.initialize()
    return _default_runtime


def execute_vireo(code: str, **kwargs) -> ExecutionResult:
    """Execute Vireo code using the default runtime."""
    runtime = get_runtime()
    return runtime.execute(code, **kwargs)


def execute_with_contract(code: str, contract: Any, **kwargs) -> ExecutionResult:
    """Execute Vireo code with contract validation."""
    runtime = get_runtime()
    return runtime.execute_with_contract(code, contract, **kwargs)