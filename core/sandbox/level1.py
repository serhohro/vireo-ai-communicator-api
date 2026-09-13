"""Vireo Sandbox Level 1 - AST validation + operation whitelist.

Only implemented level in v3.1.
"""

from typing import Any


ALLOWED_OPERATIONS = frozenset({
    "add", "sub", "mul", "div", "mod", "pow", "neg",
    "eq", "neq", "lt", "gt", "lte", "gte",
    "and", "or", "not",
    "if", "else", "while", "for", "return", "break", "continue",
    "list", "dict", "index", "slice", "len",
    "propose", "negotiate", "commit", "execute", "verify",
    "sign", "verify_signature", "hash", "print",
})

FORBIDDEN_OPERATIONS = frozenset({
    "import", "from", "eval", "exec", "compile",
    "open", "read", "write", "os", "sys", "subprocess",
    "socket", "requests", "urllib",
    "__import__", "globals", "locals", "vars",
})


class SandboxViolationError(Exception):
    def __init__(self, operation: str, reason: str):
        super().__init__(f"Sandbox violation: {operation} - {reason}")
        self.operation = operation
        self.reason = reason


def validate_ast(ast: Any) -> None:
    operations = _extract_operations(ast)
    for op in operations:
        if op in FORBIDDEN_OPERATIONS:
            raise SandboxViolationError(op, "forbidden operation")
        if op not in ALLOWED_OPERATIONS:
            raise SandboxViolationError(op, "operation not in whitelist")


def _extract_operations(ast: Any) -> set:
    ops = set()
    if isinstance(ast, dict):
        if "op" in ast:
            ops.add(ast["op"])
        if "type" in ast:
            ops.add(ast["type"])
        for v in ast.values():
            ops |= _extract_operations(v)
    elif isinstance(ast, list):
        for item in ast:
            ops |= _extract_operations(item)
    elif hasattr(ast, "__dict__"):
        for v in vars(ast).values():
            ops |= _extract_operations(v)
    return ops


class Level1Sandbox:
    def __init__(self):
        self.violations: list = []

    def check(self, ast: Any) -> bool:
        validate_ast(ast)
        return True

    def safe_execute(self, ast: Any, executor) -> Any:
        validate_ast(ast)
        return executor(ast)


__all__ = [
    "Level1Sandbox", "validate_ast", "SandboxViolationError",
    "ALLOWED_OPERATIONS", "FORBIDDEN_OPERATIONS",
]