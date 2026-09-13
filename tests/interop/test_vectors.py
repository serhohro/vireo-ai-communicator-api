# tests/interop/test_vectors.py

import pytest
import os
from core.protocol.wire import WireFormat
from core.protocol.message import Message

class TestVectors:
    """Тести для test_vectors"""
    
    VECTORS_DIR = os.path.join(os.path.dirname(__file__), "../vectors")
    
    def test_propose_vector(self):
        """Перевірка propose_v3_0.bin"""
        path = os.path.join(self.VECTORS_DIR, "propose_v3_0.bin")
        with open(path, "rb") as f:
            data = f.read()
        msg = WireFormat.deserialize(data)
        assert msg.type == "PROPOSE"
        assert "contract_id" in msg.payload
    
    def test_commit_vector(self):
        """Перевірка commit_v3_0.bin"""
        path = os.path.join(self.VECTORS_DIR, "commit_v3_0.bin")
        with open(path, "rb") as f:
            data = f.read()
        msg = WireFormat.deserialize(data)
        assert msg.type == "COMMIT"
        assert "signature" in msg.payload
    
    @pytest.mark.parametrize("vector_name", [
        "propose_v3_0", "commit_v3_0", "execute_v3_0",
        "verify_v3_0", "escalate_v3_0", "done_v3_0"
    ])
    def test_all_vectors(self, vector_name):
        """Всі вектори"""
        path = os.path.join(self.VECTORS_DIR, f"{vector_name}.bin")
        assert os.path.exists(path)
        data = open(path, "rb").read()
        msg = WireFormat.deserialize(data)
        assert msg.type == vector_name.split("_")[0].upper()
    
    def test_edge_case_unicode(self):
        """Unicode NFC нормалізація"""
        path = os.path.join(self.VECTORS_DIR, "edge_cases/unicode_nfc.bin")
        data = open(path, "rb").read()
        msg = WireFormat.deserialize(data)
        assert "text" in msg.payload
        # Перевірка нормалізації
        assert msg.payload["text"] == "café"  # NFC нормалізоване
    
    def test_edge_case_big_int(self):
        """Велике ціле число"""
        path = os.path.join(self.VECTORS_DIR, "edge_cases/big_int.bin")
        data = open(path, "rb").read()
        msg = WireFormat.deserialize(data)
        assert msg.payload["number"] > 2**64