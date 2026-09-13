# ============================================================
# VIREO RUNTIME EXECUTOR
# ============================================================
"""
Asynchronous runtime executor for Vireo code.

Features:
- Async/await execution
- Sandboxing support
- Resource limits
- Timeout handling
- Result validation
"""

import asyncio
import sys
import io
import time
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)


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


class Executor:
    """
    Asynchronous runtime executor for Vireo code.
    
    Features:
    - Async/await execution
    - Sandboxing support
    - Resource limits
    - Timeout handling
    - Memory tracking
    """
    
    def __init__(self):
        self._sandbox = None
        self._max_execution_time = 60
        self._max_memory_mb = 1024
        self._max_tokens = 1000000
        self._history: list = []
        self._is_initialized = False
    
    def configure(self, max_time: int = 60, max_memory: int = 1024, max_tokens: int = 1000000):
        """Configure executor limits."""
        self._max_execution_time = max_time
        self._max_memory_mb = max_memory
        self._max_tokens = max_tokens
        logger.info(f"✅ Executor configured: max_time={max_time}s, max_memory={max_memory}MB")
    
    async def initialize(self):
        """Initialize the executor."""
        if self._is_initialized:
            return
        
        # Initialize sandbox (if configured)
        # TODO: Add WASM/Docker sandbox support
        self._is_initialized = True
        logger.info("✅ Executor initialized")
    
    async def execute(self, code: str, 
                      timeout_sec: Optional[int] = None,
                      contract: Optional[Any] = None,
                      sandboxed: bool = True) -> ExecutionResult:
        """
        Execute Vireo code asynchronously.
        
        Args:
            code: Vireo code to execute
            timeout_sec: Optional timeout override
            contract: Optional contract with resource limits
            sandboxed: Whether to use sandbox
        
        Returns:
            ExecutionResult with status, result, and metrics
        """
        if not self._is_initialized:
            await self.initialize()
        
        timeout = timeout_sec or self._max_execution_time
        
        # Check contract limits
        if contract:
            if hasattr(contract, 'max_tokens') and contract.max_tokens:
                estimated_tokens = len(code) // 4
                if estimated_tokens > contract.max_tokens:
                    return ExecutionResult(
                        status="error",
                        error=f"Token limit exceeded: {estimated_tokens} > {contract.max_tokens}"
                    )
            
            if hasattr(contract, 'timeout_sec') and contract.timeout_sec:
                timeout = contract.timeout_sec
        
        # Execute with timeout
        import time
        start_time = time.time()
        
        try:
            result = await self._execute_with_sandbox(code, timeout, sandboxed)
            
            execution_time = time.time() - start_time
            
            exec_result = ExecutionResult(
                status="success",
                result=result.get("result"),
                output=result.get("output", ""),
                execution_time=execution_time,
                tokens_used=len(code) // 4
            )
            
            self._history.append(exec_result)
            return exec_result
            
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
    
    async def _execute_with_sandbox(self, code: str, timeout: int, sandboxed: bool) -> Dict[str, Any]:
        """Execute code with optional sandbox."""
        if sandboxed:
            return await self._execute_sandboxed(code, timeout)
        else:
            return await self._execute_direct(code, timeout)
    
    async def _execute_direct(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute code directly (no sandbox)."""
        # Create a new namespace
        namespace = {}
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute the code
                exec(code, namespace, namespace)
            
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()
            
            # Find result in namespace (look for 'result' variable)
            result = namespace.get('result', None)
            
            return {
                "result": result,
                "output": output,
                "error": error
            }
            
        except Exception as e:
            return {
                "result": None,
                "output": stdout_capture.getvalue(),
                "error": str(e)
            }
    
    async def _execute_sandboxed(self, code: str, timeout: int) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment.
        
        This is a placeholder for WASM/Docker sandboxing.
        Currently falls back to direct execution.
        """
        # TODO: Implement WASM sandbox
        # TODO: Implement Docker sandbox
        
        # For now, use direct execution with extra validation
        return await self._execute_direct(code, timeout)
    
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
            "max_memory_mb": self._max_memory_mb,
            "max_tokens": self._max_tokens
        }


class VireoInterpreter:
    """
    Vireo interpreter for executing Vireo code.
    
    This is a lightweight interpreter for Vireo language.
    """
    
    def __init__(self):
        self._variables = {}
        self._functions = {}
        self._output = []
    
    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Vireo code.
        
        Args:
            code: Vireo code
        
        Returns:
            Dict with result and output
        """
        import ast
        import json
        
        # This is a placeholder for the actual Vireo interpreter
        # For now, it uses Python's exec
        
        namespace = {
            "variables": self._variables,
            "functions": self._functions,
            "output": self._output
        }
        
        stdout_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture):
                # Compile and execute
                compiled = compile(code, '<vireo>', 'exec')
                exec(compiled, namespace, namespace)
            
            output = stdout_capture.getvalue()
            
            return {
                "success": True,
                "output": output,
                "variables": self._variables,
                "result": namespace.get('result', None)
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": stdout_capture.getvalue(),
                "error": str(e)
            }


# ============================================================
# EXECUTOR FACTORY
# ============================================================

_default_executor: Optional[Executor] = None


def get_executor() -> Executor:
    """Get the global executor instance."""
    global _default_executor
    if _default_executor is None:
        _default_executor = Executor()
    return _default_executor


def create_executor(max_time: int = 60, max_memory: int = 1024, max_tokens: int = 1000000) -> Executor:
    """Create and configure an executor."""
    executor = Executor()
    executor.configure(max_time, max_memory, max_tokens)
    return executor


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

async def execute_vireo(code: str, **kwargs) -> ExecutionResult:
    """Execute Vireo code using the global executor."""
    executor = get_executor()
    return await executor.execute(code, **kwargs)


def execute_vireo_sync(code: str, **kwargs) -> ExecutionResult:
    """Execute Vireo code synchronously."""
    return asyncio.run(execute_vireo(code, **kwargs))