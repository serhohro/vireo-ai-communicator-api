# tests/interop/test_python_rust.py

import pytest
import subprocess
import json
from core.protocol.wire import WireFormat
from core.protocol.message import Message

class TestPythonRustInterop:
    """Тести сумісності Python ↔ Rust"""
    
    RUST_BINARY = "target/debug/vireo_cli"
    
    @pytest.fixture
    def rust_available(self):
        """Перевірка наявності Rust бінарника"""
        try:
            subprocess.run([self.RUST_BINARY, "--version"], 
                         capture_output=True, check=True)
            return True
        except:
            return False
    
    def test_rust_serialize_python_deserialize(self, rust_available):
        """Rust серіалізує, Python десеріалізує"""
        if not rust_available:
            pytest.skip("Rust binary not available")
        
        # Rust генерує повідомлення
        result = subprocess.run(
            [self.RUST_BINARY, "serialize", '{"type":"PING"}'],
            capture_output=True
        )
        data = result.stdout
        msg = WireFormat.deserialize(data)
        assert msg.type == "PING"
    
    def test_python_serialize_rust_deserialize(self, rust_available):
        """Python серіалізує, Rust десеріалізує"""
        if not rust_available:
            pytest.skip("Rust binary not available")
        
        msg = Message(type="PONG", sender="python", recipient="rust")
        data = WireFormat.serialize(msg)
        
        result = subprocess.run(
            [self.RUST_BINARY, "deserialize"],
            input=data,
            capture_output=True
        )
        output = json.loads(result.stdout)
        assert output["type"] == "PONG"