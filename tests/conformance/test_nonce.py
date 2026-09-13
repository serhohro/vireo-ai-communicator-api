"""Vireo v3.1 nonce replay protection tests."""

import time
import tempfile
import os
import pytest

from core.protocol.nonce_manager import NonceManager


@pytest.fixture
def store():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    nm = NonceManager(path)
    yield nm
    nm.close()
    try:
        os.unlink(path)
    except OSError:
        pass


class TestNonceStore:
    def test_fresh(self, store):
        ok, err = store.check_and_store(b"\x00" * 16, b"\x01" * 32, int(time.time() * 1000))
        assert ok and err is None

    def test_replay(self, store):
        nonce = b"\xab" * 16
        sender = b"\xcd" * 32
        ts = int(time.time() * 1000)
        assert store.check_and_store(nonce, sender, ts)[0]
        ok, err = store.check_and_store(nonce, sender, ts)
        assert not ok
        assert "replay" in err.lower()

    def test_bad_nonce_length(self, store):
        ok, err = store.check_and_store(b"short", b"\x01" * 32, int(time.time() * 1000))
        assert not ok

    def test_old_timestamp(self, store):
        old = int(time.time() * 1000) - 10 * 60 * 1000
        ok, err = store.check_and_store(b"\x00" * 16, b"\x01" * 32, old)
        assert not ok
        assert "tolerance" in err

    def test_count(self, store):
        ts = int(time.time() * 1000)
        for i in range(5):
            store.check_and_store(bytes([i]) * 16, b"\x01" * 32, ts)
        assert store.count() == 5
