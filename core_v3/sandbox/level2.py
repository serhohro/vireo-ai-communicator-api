"""
Sandbox Level 2

Extended sandbox with additional capabilities.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

import sys
import io
import json
import math
import random
import datetime
from typing import Optional, Dict, Any, List, Set, Callable
from dataclasses import dataclass
from pathlib import Path

from .level1 import SandboxLevel1, SandboxResult
from ..config import get_config
from ..errors import VireoSandboxError


class SandboxLevel2(SandboxLevel1):
    """
    Level 2 Sandbox - Extended capabilities.
    
    - All Level 1 restrictions
    - Additional safe imports (math, json, random, datetime, collections)
    - Basic data structure operations
    - No file system access
    - No network access
    - Still sandboxed
    """
    
    ALLOWED_IMPORTS = {
        'math': math,
        'json': json,
        'random': random,
        'datetime': datetime,
        'collections': __import__('collections'),
        'itertools': __import__('itertools'),
        'functools': __import__('functools'),
        'typing': __import__('typing'),
    }
    
    # Additional allowed builtins
    EXTRA_BUILTINS = [
        'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
        'any', 'all', 'sum', 'min', 'max', 'len', 'range', 'slice',
        'isinstance', 'issubclass', 'hasattr', 'getattr', 'setattr',
        'delattr', 'dir', 'id', 'hash', 'memoryview',
        'complex', 'object', 'property', 'staticmethod', 'classmethod',
        'super', 'bool', 'int', 'float', 'str', 'list', 'dict', 'set', 
        'tuple', 'bytes', 'bytearray', 'frozenset',
    ]
    
    def __init__(self, timeout_seconds: Optional[float] = None):
        config = get_config()
        self.timeout_seconds = timeout_seconds or config.sandbox.max_execution_time_seconds
        self.max_memory_mb = config.sandbox.max_memory_mb
        self._sandboxed_globals = self._create_sandboxed_globals()
    
    def _create_sandboxed_globals(self) -> Dict[str, Any]:
        """Create sandboxed globals dictionary with additional imports."""
        # Start with Level 1 safe builtins
        safe_builtins = {}
        for name in self.ALLOWED_BUILTINS + self.EXTRA_BUILTINS:
            if hasattr(__builtins__, name):
                safe_builtins[name] = getattr(__builtins__, name)
        
        # Create globals with safe builtins and allowed imports
        globals_dict = {
            '__builtins__': safe_builtins,
            '__name__': '__sandbox__',
            '__file__': '<sandbox>',
        }
        
        # Add allowed imports
        for name, module in self.ALLOWED_IMPORTS.items():
            globals_dict[name] = module
        
        return globals_dict
    
    def execute_expression(self, expression: str, context: Optional[Dict[str, Any]] = None) -> SandboxResult:
        """Execute a single expression in the sandbox."""
        import time
        from threading import Timer
        
        start_time = time.time()
        result = None
        error = None
        timed_out = False
        
        # Prepare globals
        globals_dict = self._sandboxed_globals.copy()
        if context:
            globals_dict.update(context)
        
        # Parse and validate expression
        try:
            import ast
            tree = ast.parse(expression, mode='eval')
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
        
        def timeout_handler():
            nonlocal timed_out
            timed_out = True
        
        timer = Timer(self.timeout_seconds, timeout_handler)
        timer.daemon = True
        
        try:
            timer.start()
            
            # Compile and evaluate
            compiled = compile(tree, '<sandbox>', 'eval')
            result = eval(compiled, globals_dict)
        
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