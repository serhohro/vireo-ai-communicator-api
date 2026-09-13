"""Vireo Sandbox Level 3 - Container isolation.

NOT IMPLEMENTED IN v3.1. Planned for v3.2+.
"""

from typing import Any


class Level3Sandbox:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Level3Sandbox (container isolation) is not implemented in v3.1. "
            "Planned for v3.2+. See ROADMAP.md."
        )

    def check(self, ast: Any) -> bool:
        raise NotImplementedError("Level3Sandbox not implemented.")

    def safe_execute(self, ast: Any, executor) -> Any:
        raise NotImplementedError("Level3Sandbox not implemented.")


__all__ = ["Level3Sandbox"]