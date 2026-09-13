"""Vireo Reputation v3.1 — simple in-memory reputation tracker."""

import threading
import time


class Reputation:
    def __init__(self):
        self._scores: dict[str, dict] = {}
        self._lock = threading.Lock()

    def record(self, did: str, success: bool, weight: float = 1.0) -> None:
        with self._lock:
            entry = self._scores.setdefault(did, {
                "success": 0, "failure": 0, "score": 0.5,
                "updated_at": 0,
            })
            if success:
                entry["success"] += 1
            else:
                entry["failure"] += 1
            total = entry["success"] + entry["failure"]
            entry["score"] = entry["success"] / total if total else 0.5
            entry["updated_at"] = int(time.time() * 1000)

    def get(self, did: str) -> dict:
        with self._lock:
            return self._scores.get(did, {"score": 0.5, "success": 0, "failure": 0})

    def list(self) -> list[dict]:
        with self._lock:
            return [{"did": k, **v} for k, v in self._scores.items()]