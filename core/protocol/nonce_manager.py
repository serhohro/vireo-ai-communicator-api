"""
Vireo Nonce Manager v3.1 — replay protection.

Phase 1: SQLite persistent store with TTL.
Phase 2 (future): sliding window bitmap for hot paths.
"""

import sqlite3
import threading
import time
from typing import Optional

from core.config import config


class NonceManager:
    """
    Thread-safe SQLite-backed nonce store.

    Usage:
        nm = NonceManager()
        ok, err = nm.check_and_store(nonce, sender_id, timestamp_ms)
        if not ok:
            raise ReplayError(err)
    """

    def __init__(self, path: Optional[str] = None):
        self.path = path or config.NONCE_DB_PATH
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS nonces (
                nonce      BLOB NOT NULL,
                sender_id  BLOB NOT NULL,
                timestamp  INTEGER NOT NULL,
                PRIMARY KEY (nonce, sender_id)
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_nonces_ts ON nonces(timestamp)"
        )
        self._conn.commit()
        self._last_cleanup = time.time()

    def check_and_store(
        self,
        nonce: bytes,
        sender_id: bytes,
        timestamp_ms: int,
    ) -> tuple[bool, Optional[str]]:
        if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != config.NONCE_BYTES:
            return False, f"nonce must be {config.NONCE_BYTES} bytes"

        now_ms = int(time.time() * 1000)
        if abs(now_ms - timestamp_ms) > config.MAX_CLOCK_SKEW_MS:
            return False, "timestamp outside tolerance"

        with self._lock:
            cur = self._conn.execute(
                "SELECT 1 FROM nonces WHERE nonce=? AND sender_id=?",
                (bytes(nonce), bytes(sender_id)),
            )
            if cur.fetchone():
                return False, "nonce replay detected"

            try:
                self._conn.execute(
                    "INSERT INTO nonces (nonce, sender_id, timestamp) VALUES (?, ?, ?)",
                    (bytes(nonce), bytes(sender_id), timestamp_ms),
                )
                self._conn.commit()
            except sqlite3.IntegrityError:
                return False, "nonce replay detected (race)"

            self._maybe_cleanup()
            return True, None

    def _maybe_cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup < 3600:
            return
        cutoff_ms = int((now - config.NONCE_TTL_SEC) * 1000)
        self._conn.execute("DELETE FROM nonces WHERE timestamp < ?", (cutoff_ms,))
        self._conn.commit()
        self._last_cleanup = now

    def cleanup(self) -> int:
        cutoff_ms = int((time.time() - config.NONCE_TTL_SEC) * 1000)
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM nonces WHERE timestamp < ?", (cutoff_ms,)
            )
            self._conn.commit()
            self._last_cleanup = time.time()
            return cur.rowcount

    def count(self) -> int:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(*) FROM nonces")
            return cur.fetchone()[0]

    def close(self) -> None:
        with self._lock:
            self._conn.close()


# Module-level singleton (lazy)
_default: Optional[NonceManager] = None
_default_lock = threading.Lock()


def get_nonce_manager() -> NonceManager:
    global _default
    if _default is None:
        with _default_lock:
            if _default is None:
                _default = NonceManager()
    return _default