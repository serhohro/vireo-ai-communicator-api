# ============================================================
# LAYER 3 — AI Protocol: Context versioning + conflict resolution
# ============================================================

from __future__ import annotations

import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ConflictStrategy(str, Enum):
    LAST_WRITE_WINS = "last_write_wins"
    REJECT_ON_CONFLICT = "reject_on_conflict"


@dataclass
class ConflictError(Exception):
    key: str
    expected_version: int
    actual_version: int

    def __str__(self) -> str:
        return (
            f"conflict on '{self.key}': write expected version "
            f"{self.expected_version}, but current version is {self.actual_version}"
        )


class ContextStore:
    def __init__(self, strategy: ConflictStrategy = ConflictStrategy.REJECT_ON_CONFLICT):
        self._lock = threading.Lock()
        self._data: Dict[str, Any] = {}
        self._versions: Dict[str, int] = {}
        self.strategy = strategy

    def read(self, key: str) -> tuple[Optional[Any], int]:
        with self._lock:
            return self._data.get(key), self._versions.get(key, 0)

    def write(self, key: str, value: Any, expected_version: int) -> int:
        with self._lock:
            current_version = self._versions.get(key, 0)
            if current_version != expected_version:
                if self.strategy == ConflictStrategy.REJECT_ON_CONFLICT:
                    raise ConflictError(key, expected_version, current_version)
            new_version = current_version + 1
            self._data[key] = value
            self._versions[key] = new_version
            return new_version