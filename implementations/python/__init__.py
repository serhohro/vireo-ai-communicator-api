# ============================================================
# VIREO PYTHON IMPLEMENTATION
# ============================================================
"""
Vireo Python implementation package.

This package contains the reference implementation of Vireo in Python.
It provides the core runtime, protocol, and agent functionality.
"""

from .runtime import VireoRuntime, ExecutionResult, RuntimeConfig

__all__ = [
    'VireoRuntime',
    'ExecutionResult',
    'RuntimeConfig',
]