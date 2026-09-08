"""
Sandbox Level 3

Advanced sandbox with limited filesystem access.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

import os
import io
import sys
import tempfile
from typing import Optional, Dict, Any, List, Set, Callable
from pathlib import Path
from contextlib import contextmanager

from .level2 import SandboxLevel2, SandboxResult
from ..config import get_config
from ..errors import VireoSandboxError


class SandboxLevel3(SandboxLevel2):
    """
    Level 3 Sandbox - Advanced with limited FS access.
    
    - All Level 2 capabilities
    - Limited filesystem access (temp directory only)
    - No network access
    - Subprocess execution disabled
    - Enhanced security
    """
    
    def __init__(
        self,
        timeout_seconds: Optional[float] = None,
        temp_dir: Optional[str] = None,
    ):
        config = get_config()
        self.timeout_seconds = timeout_seconds or config.sandbox.max_execution_time_seconds
        self.max_memory_mb = config.sandbox.max_memory_mb
        
        # Setup temp directory
        if temp_dir:
            self.temp_dir = Path(temp_dir)
        else:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="vireo_sandbox_"))
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Track created files
        self._created_files: Set[Path] = set()
        
        # Setup sandboxed globals
        self._sandboxed_globals = self._create_sandboxed_globals()
    
    def _create_sandboxed_globals(self) -> Dict[str, Any]:
        """Create sandboxed globals with file access restricted to temp dir."""
        globals_dict = super()._create_sandboxed_globals()
        
        # Add safe file operations
        globals_dict['_sandbox_temp_dir'] = str(self.temp_dir)
        
        # Safe open function
        def safe_open(path: str, mode: str = 'r', *args, **kwargs):
            """Open file with path validation."""
            # Only allow read/write in temp directory
            full_path = Path(path)
            if not full_path.is_absolute():
                full_path = self.temp_dir / path
            
            # Check if path is within temp directory
            try:
                full_path.resolve().relative_to(self.temp_dir.resolve())
            except ValueError:
                raise VireoSandboxError(f"Access denied: {path} outside sandbox")
            
            # Track created files
            if mode in ['w', 'x', 'a']:
                self._created_files.add(full_path)
            
            # Open file
            return open(str(full_path), mode, *args, **kwargs)
        
        globals_dict['open'] = safe_open
        
        # Add temp directory info
        globals_dict['SANDBOX_TEMP'] = str(self.temp_dir)
        globals_dict['SANDBOX_TEMP_DIR'] = str(self.temp_dir)
        
        # Add file utilities
        globals_dict['list_files'] = lambda: [
            str(p.relative_to(self.temp_dir)) 
            for p in self.temp_dir.iterdir() 
            if p.is_file()
        ]
        
        globals_dict['read_file'] = self._safe_read_file
        globals_dict['write_file'] = self._safe_write_file
        globals_dict['delete_file'] = self._safe_delete_file
        
        return globals_dict
    
    def _safe_read_file(self, path: str) -> str:
        """Safe file read."""
        full_path = self._validate_path(path)
        with open(full_path, 'r') as f:
            return f.read()
    
    def _safe_write_file(self, path: str, content: str) -> None:
        """Safe file write."""
        full_path = self._validate_path(path)
        self._created_files.add(full_path)
        with open(full_path, 'w') as f:
            f.write(content)
    
    def _safe_delete_file(self, path: str) -> bool:
        """Safe file delete."""
        full_path = self._validate_path(path)
        if full_path.exists():
            full_path.unlink()
            if full_path in self._created_files:
                self._created_files.remove(full_path)
            return True
        return False
    
    def _validate_path(self, path: str) -> Path:
        """Validate path is within sandbox temp directory."""
        full_path = Path(path)
        if not full_path.is_absolute():
            full_path = self.temp_dir / path
        
        # Check if path is within temp directory
        try:
            full_path.resolve().relative_to(self.temp_dir.resolve())
        except ValueError:
            raise VireoSandboxError(f"Access denied: {path} outside sandbox")
        
        return full_path
    
    def cleanup(self) -> None:
        """Clean up created files."""
        import shutil
        for path in self._created_files:
            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass
        
        # Remove temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def get_file_list(self) -> List[str]:
        """Get list of files in sandbox temp directory."""
        return [
            str(p.relative_to(self.temp_dir)) 
            for p in self.temp_dir.iterdir() 
            if p.is_file()
        ]
    
    def get_file_content(self, path: str) -> str:
        """Get content of a file in the sandbox."""
        full_path = self._validate_path(path)
        if not full_path.exists():
            raise VireoSandboxError(f"File not found: {path}")
        with open(full_path, 'r') as f:
            return f.read()
    
    def execute_with_files(
        self,
        code: str,
        files: Dict[str, str],
        context: Optional[Dict[str, Any]] = None,
    ) -> SandboxResult:
        """
        Execute code with input files.
        
        Args:
            code: Python code to execute
            files: Dictionary of filename -> content to create in sandbox
            context: Optional context variables
        """
        # Create files
        for filename, content in files.items():
            self._safe_write_file(filename, content)
        
        # Execute code
        return self.execute(code, context)
    
    def execute_and_get_files(self, code: str) -> SandboxResult:
        """Execute code and return any created files."""
        # Execute code
        result = self.execute(code)
        
        # Collect created files
        if result.success:
            files = {}
            for path in self._created_files:
                if path.exists():
                    with open(path, 'r') as f:
                        files[str(path.relative_to(self.temp_dir))] = f.read()
            result.metadata['created_files'] = files
        
        return result