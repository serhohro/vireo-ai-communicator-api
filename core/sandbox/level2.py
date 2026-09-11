"""Vireo Sandbox Level 2 - WASM.

NOT IMPLEMENTED IN v3.1. Planned for v3.2.
"""

from typing import Any


class Level2Sandbox:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Level2Sandbox (WASM isolation) is not implemented in v3.1. "
            "Planned for v3.2. See ROADMAP.md."
        )

    def check(self, ast: Any) -> bool:
        raise NotImplementedError("Level2Sandbox not implemented.")

    def safe_execute(self, ast: Any, executor) -> Any:
        raise NotImplementedError("Level2Sandbox not implemented.")


__all__ = ["Level2Sandbox"]