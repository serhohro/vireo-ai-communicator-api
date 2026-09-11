"""
Vireo Key Manager v3.1.

Handles key generation, storage, rotation, and revocation.
"""

import json
import os
import threading
import time
from pathlib import Path
from typing import Optional

from core.crypto.ed25519 import generate_keypair


class KeyManager:
    def __init__(self, path: str = "keys.json"):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._keys: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._keys = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self._keys = {}

    def _save(self) -> None:
        try:
            self.path.write_text(json.dumps(self._keys, indent=2), encoding="utf-8")
        except Exception:
            pass

    def generate(self, agent_id: str) -> dict:
        with self._lock:
            kp = generate_keypair()
            kp["agent_id"] = agent_id
            kp["created_at"] = int(time.time() * 1000)
            kp["revoked"] = False
            self._keys[agent_id] = kp
            self._save()
            return kp

    def get(self, agent_id: str) -> Optional[dict]:
        with self._lock:
            kp = self._keys.get(agent_id)
            if kp and not kp.get("revoked"):
                return kp
            return None

    def revoke(self, agent_id: str) -> bool:
        with self._lock:
            kp = self._keys.get(agent_id)
            if not kp:
                return False
            kp["revoked"] = True
            kp["revoked_at"] = int(time.time() * 1000)
            self._save()
            return True

    def rotate(self, agent_id: str) -> dict:
        with self._lock:
            old = self._keys.get(agent_id)
            if old:
                old["revoked"] = True
                old["revoked_at"] = int(time.time() * 1000)
            new = generate_keypair()
            new["agent_id"] = agent_id
            new["created_at"] = int(time.time() * 1000)
            new["revoked"] = False
            new["rotated_from"] = old.get("created_at") if old else None
            self._keys[agent_id] = new
            self._save()
            return new

    def list(self) -> list[dict]:
        with self._lock:
            return list(self._keys.values())