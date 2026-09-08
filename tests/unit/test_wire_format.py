# tests/unit/test_wire_format.py

import pytest
import struct
from core.protocol.wire import WireFormat
from core.protocol.message import Message

class TestWireFormatUnit:
    """Юніт-тести для Wire Format"""
    
    def test_empty_message(self):
        """Порожнє повідомлення"""
        msg = Message(type="PING")
        wire = WireFormat.serialize(msg)
        restored = WireFormat.deserialize(wire)
        assert restored.type == "PING"
    
    def test_large_payload(self):
        """Великий payload (>1MB)"""
        payload = {"data": "x" * 1024 * 1024}  # 1MB
        msg = Message(type="EXECUTE", payload=payload)
        wire = WireFormat.serialize(msg)
        restored = WireFormat.deserialize(wire)
        assert len(restored.payload["data"]) == 1024 * 1024
    
    def test_unicode_payload(self):
        """Unicode в payload"""
        msg = Message(
            type="PROPOSE",
            payload={"message": "Привіт Vireo 🌿"}
        )
        wire = WireFormat.serialize(msg)
        restored = WireFormat.deserialize(wire)
        assert restored.payload["message"] == "Привіт Vireo 🌿"
    
    def test_binary_payload(self):
        """Бінарні дані в payload"""
        msg = Message(
            type="EXECUTE",
            payload={"binary": b"\x00\x01\x02\x03"}
        )
        wire = WireFormat.serialize(msg)
        restored = WireFormat.deserialize(wire)
        assert restored.payload["binary"] == b"\x00\x01\x02\x03"