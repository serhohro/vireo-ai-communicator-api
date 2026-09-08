"""
Sandbox Level 1

Basic sandbox with fundamental restrictions.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

import sys
import io
import contextlib
import traceback
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
import ast

from ..errors import VireoSandboxError, VireoSandboxTimeout
from ..config import get_config


@dataclass
class SandboxResult:
    """Result of sandbox execution."""
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0
    memory_used: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SandboxLevel1:
    """
    Level 1 Sandbox - Basic restrictions.
    
    - No file system access
    - No network access
    - Limited builtins
    - Timeout protection
    - Memory limits (optional)
    """
    
    ALLOWED_BUILTINS = [
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
        'chr', 'dict', 'divmod', 'enumerate', 'filter', 'float', 'format',
        'frozenset', 'hex', 'int', 'iter', 'len', 'list', 'map', 'max',
        'min', 'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
        'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum', 
        'tuple', 'zip', 'type', 'isinstance', 'issubclass', 'hasattr',
        'getattr', 'setattr', 'delattr', 'dir', 'id', 'hash', 'memoryview',
        'complex', 'object', 'property', 'staticmethod', 'classmethod',
        'super', 'bool', 'int', 'float', 'str', 'list', 'dict', 'set', 
        'tuple', 'bytes', 'bytearray', 'frozenset',
    ]
    
    DISALLOWED_NAMES = [
        '__import__', 'exec', 'eval', 'compile', 'open', 'input',
        'breakpoint', 'globals', 'locals', 'vars', 'dir',
    ]
    
    def __init__(self, timeout_seconds: Optional[float] = None):
        config = get_config()
        self.timeout_seconds = timeout_seconds or config.sandbox.max_execution_time_seconds
        self.max_memory_mb = config.sandbox.max_memory_mb
        self._sandboxed_globals = self._create_sandboxed_globals()
    
    def _create_sandboxed_globals(self) -> Dict[str, Any]:
        """Create sandboxed globals dictionary."""
        # Start with safe builtins
        safe_builtins = {}
        for name in self.ALLOWED_BUILTINS:
            if hasattr(__builtins__, name):
                safe_builtins[name] = getattr(__builtins__, name)
        
        # Create globals with only safe builtins
        return {
            '__builtins__': safe_builtins,
            '__name__': '__sandbox__',
            '__file__': '<sandbox>',
        }
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> SandboxResult:
        """
        Execute code in the sandbox.
        
        Args:
            code: Python code to execute
            context: Optional context variables
        
        Returns:
            SandboxResult with execution details
        """
        import time
        import signal
        from threading import Timer
        
        start_time = time.time()
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        # Prepare globals
        globals_dict = self._sandboxed_globals.copy()
        if context:
            globals_dict.update(context)
        
        # Setup locals
        locals_dict = {}
        
        # Add output capture
        globals_dict['_sandbox_output'] = output_buffer
        
        # Parse and validate code
        try:
            tree = ast.parse(code)
            self._validate_ast(tree)
        except SyntaxError as e:
            return SandboxResult(
                success=False,
                output="",
                error=f"Syntax error: {e}",
                duration=0.0,
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                output="",
                error=f"Validation error: {e}",
                duration=0.0,
            )
        
        # Execute with timeout
        result = None
        error = None
        timed_out = False
        
        def timeout_handler():
            nonlocal timed_out
            timed_out = True
        
        timer = Timer(self.timeout_seconds, timeout_handler)
        timer.daemon = True
        
        try:
            timer.start()
            
            # Redirect stdout/stderr
            with contextlib.redirect_stdout(output_buffer), \
                 contextlib.redirect_stderr(error_buffer):
                
                # Compile and execute
                compiled = compile(tree, '<sandbox>', 'exec')
                exec(compiled, globals_dict, locals_dict)
                
                # Get result from locals
                result = locals_dict.get('_result', None)
        
        except Exception as e:
            error = traceback.format_exc()
        
        finally:
            timer.cancel()
        
        duration = time.time() - start_time
        
        # Check for timeout
        if timed_out:
            return SandboxResult(
                success=False,
                output=output_buffer.getvalue(),
                error="Execution timed out",
                duration=duration,
            )
        
        # Check for errors
        if error:
            return SandboxResult(
                success=False,
                output=output_buffer.getvalue(),
                error=error,
                duration=duration,
            )
        
        return SandboxResult(
            success=True,
            output=output_buffer.getvalue(),
            error=None,
            duration=duration,
            metadata={
                "result": result,
                "locals": locals_dict,
            }
        )
    
    def _validate_ast(self, node: ast.AST) -> None:
        """Validate AST for disallowed constructs."""
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if child.id in self.DISALLOWED_NAMES:
                    raise VireoSandboxError(f"Disallowed name: {child.id}")
            
            elif isinstance(child, ast.Import):
                for name in child.names:
                    if name.name in self.DISALLOWED_NAMES or name.name.startswith('_'):
                        raise VireoSandboxError(f"Disallowed import: {name.name}")
            
            elif isinstance(child, ast.ImportFrom):
                if child.module in self.DISALLOWED_NAMES or (child.module and child.module.startswith('_')):
                    raise VireoSandboxError(f"Disallowed import: {child.module}")
            
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in self.DISALLOWED_NAMES:
                        raise VireoSandboxError(f"Disallowed function call: {child.func.id}")
                elif isinstance(child.func, ast.Attribute):
                    # Check for dangerous attribute access
                    if isinstance(child.func.value, ast.Name):
                        if child.func.value.id in ['sys', 'os', 'subprocess']:
                            raise VireoSandboxError(f"Disallowed module access: {child.func.value.id}")
    
    def execute_function(self, func: Callable, *args, **kwargs) -> SandboxResult:
        """Execute a function in the sandbox."""
        import time
        from threading import Timer
        
        start_time = time.time()
        result = None
        error = None
        timed_out = False
        
        def timeout_handler():
            nonlocal timed_out
            timed_out = True
        
        timer = Timer(self.timeout_seconds, timeout_handler)
        timer.daemon = True
        
        try:
            timer.start()
            result = func(*args, **kwargs)
        except Exception as e:
            error = traceback.format_exc()
        finally:
            timer.cancel()
        
        duration = time.time() - start_time
        
        if timed_out:
            return SandboxResult(
                success=False,
                output="",
                error="Execution timed out",
                duration=duration,
            )
        
        if error:
            return SandboxResult(
                success=False,
                output="",
                error=error,
                duration=duration,
            )
        
        return SandboxResult(
            success=True,
            output=str(result),
            error=None,
            duration=duration,
            metadata={"result": result},
        )