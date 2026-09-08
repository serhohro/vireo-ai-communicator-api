#!/usr/bin/env python3
"""
Interoperability Tests: Python ↔ TypeScript

Tests that Python and TypeScript implementations are interoperable.
"""

import pytest
import json
import sys
import subprocess
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import core
try:
    from core.wire_format import WireFormat
    from core.protocol import Message
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    print("⚠️ Core modules not available, running limited tests")


class TestPythonTSInterop:
    """Python ↔ TypeScript interoperability tests."""
    
    @pytest.fixture
    def ts_test_path(self):
        """Get the TypeScript test path."""
        return Path(__file__).parent.parent.parent / "sdk" / "typescript" / "dist" / "test_runner.js"
    
    def test_ts_available(self, ts_test_path):
        """Test that TypeScript test runner is available."""
        if not ts_test_path.exists():
            pytest.skip("TypeScript test runner not found. Build with: cd sdk/typescript && npm run build")
            
    def test_serialization_roundtrip(self, ts_test_path):
        """Test serialization roundtrip between Python and TypeScript."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
        if not ts_test_path.exists():
            pytest.skip("TypeScript test runner not found")
            
        # Python serializes
        data = {"test": "data", "number": 42, "array": [1, 2, 3]}
        py_binary = WireFormat.serialize(data).hex()
        
        # Run TypeScript deserialization
        result = subprocess.run(
            ["node", str(ts_test_path), "deserialize", py_binary],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"TypeScript failed: {result.stderr}"
        
        ts_data = json.loads(result.stdout)
        assert ts_data["test"] == "data"
        assert ts_data["number"] == 42
        assert ts_data["array"] == [1, 2, 3]
        
    def test_ts_serializes_python_deserializes(self, ts_test_path):
        """Test TypeScript serializes and Python deserializes."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
        if not ts_test_path.exists():
            pytest.skip("TypeScript test runner not found")
            
        test_data = {"ts": "data", "value": 100}
        
        # TypeScript serializes
        result = subprocess.run(
            ["node", str(ts_test_path), "serialize", json.dumps(test_data)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"TypeScript failed: {result.stderr}"
        
        ts_hex = result.stdout.strip()
        ts_binary = bytes.fromhex(ts_hex)
        
        # Python deserializes
        py_data = WireFormat.deserialize(ts_binary)
        assert py_data["ts"] == "data"
        assert py_data["value"] == 100
        
    def test_message_roundtrip(self, ts_test_path):
        """Test message roundtrip between Python and TypeScript."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
        if not ts_test_path.exists():
            pytest.skip("TypeScript test runner not found")
            
        # Python creates message
        msg = Message(
            type="propose",
            sender="python_agent",
            recipient="ts_agent",
            payload={"task": "test_interop"}
        )
        py_hex = msg.to_bytes().hex()
        
        # TypeScript processes message
        result = subprocess.run(
            ["node", str(ts_test_path), "process_message", py_hex],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"TypeScript failed: {result.stderr}"
        
        ts_response = json.loads(result.stdout)
        assert "type" in ts_response
        assert "payload" in ts_response
        
    def test_canonical_consistency(self, ts_test_path):
        """Test canonical serialization consistency."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
        if not ts_test_path.exists():
            pytest.skip("TypeScript test runner not found")
            
        data = {"b": 2, "a": 1, "c": 3}
        
        # Python canonical
        py_binary = WireFormat.serialize_canonical(data)
        py_hex = py_binary.hex()
        
        # TypeScript should produce same canonical form
        result = subprocess.run(
            ["node", str(ts_test_path), "canonical_hash", py_hex],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        
        ts_hash = result.stdout.strip()
        
        # Python hash
        import hashlib
        py_hash = hashlib.sha256(py_binary).hexdigest()
        
        # Should be the same
        assert ts_hash == py_hash