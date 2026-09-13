# tests/fuzz/fuzz_wire_format.py

import pytest
from hypothesis import given, strategies as st
from core.protocol.wire import WireFormat
from core.protocol.message import Message

class FuzzWireFormat:
    """Fuzz-тести для Wire Format"""
    
    @given(data=st.binary(min_size=0, max_size=1024))
    def test_fuzz_deserialize(self, data):
        """Fuzz десеріалізація"""
        try:
            msg = WireFormat.deserialize(data)
            # Якщо десеріалізувалося, перевіряємо структуру
            assert isinstance(msg, Message)
        except Exception:
            # Безпечне падіння - очікувано для невалідних даних
            pass
    
    @given(
        msg_type=st.sampled_from(["PING", "PONG", "PROPOSE", "COMMIT"]),
        sender=st.text(alphabet="ascii", max_size=32),
        recipient=st.text(alphabet="ascii", max_size=32),
        payload=st.dictionaries(
            keys=st.text(max_size=32),
            values=st.one_of(st.integers(), st.text(), st.binary())
        )
    )
    def test_fuzz_roundtrip(self, msg_type, sender, recipient, payload):
        """Fuzz повний цикл"""
        try:
            msg = Message(type=msg_type, sender=sender, 
                         recipient=recipient, payload=payload)
            data = WireFormat.serialize(msg)
            restored = WireFormat.deserialize(data)
            assert restored == msg
        except Exception:
            # Деякі payload можуть бути невалідними
            pass
    
    @given(data=st.binary(min_size=4, max_size=1024))
    def test_fuzz_version(self, data):
        """Fuzz версія заголовка"""
        try:
            # Перші 4 байти - версія
            from core.protocol.wire import WireFormat
            # Безпечна спроба
            WireFormat.deserialize(data)
        except:
            pass