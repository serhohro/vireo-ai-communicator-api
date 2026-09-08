#!/usr/bin/env python3
"""
Interoperability Tests: Rust ↔ TypeScript

Tests that Rust and TypeScript implementations are interoperable.
"""

import pytest
import json
import sys
import subprocess
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestRustTSInterop:
    """Rust ↔ TypeScript interoperability tests."""
    
    @pytest.fixture
    def rust_binary(self):
        """Get the Rust test binary path."""
        rust_bin = Path(__file__).parent.parent.parent / "sdk" / "rust" / "target" / "debug" / "test_runner"
        if not rust_bin.exists():
            rust_bin = Path(__file__).parent.parent.parent / "sdk" / "rust" / "target" / "release" / "test_runner"
        return rust_bin
        
    @pytest.fixture
    def ts_test_path(self):
        """Get the TypeScript test path."""
        return Path(__file__).parent.parent.parent / "sdk" / "typescript" / "dist" / "test_runner.js"
    
    def test_rust_available(self, rust_binary):
        """Test that Rust binary is available."""
        if not rust_binary.exists():
            pytest.skip("Rust test binary not found")
            
    def test_ts_available(self, ts_test_path):
        """Test that TypeScript test runner is available."""
        if not ts_test_path.exists():
            pytest.skip("TypeScript test runner not found")
            
    def test_serialization_roundtrip(self, rust_binary, ts_test_path):
        """Test serialization roundtrip between Rust and TypeScript."""
        if not rust_binary.exists() or not ts_test_path.exists():
            pytest.skip("Required binaries not found")
            
        test_data = {"rust_to_ts": "test", "number": 123}
        
        # Rust serializes
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            temp_path = f.name
            
        try:
            result = subprocess.run(
                [str(rust_binary), "serialize", json.dumps(test_data), temp_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Rust failed: {result.stderr}"
            
            # Read binary and convert to hex for TypeScript
            with open(temp_path, "rb") as f:
                rust_binary_data = f.read()
            rust_hex = rust_binary_data.hex()
            
            # TypeScript deserializes
            result = subprocess.run(
                ["node", str(ts_test_path), "deserialize", rust_hex],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"TypeScript failed: {result.stderr}"
            
            ts_data = json.loads(result.stdout)
            assert ts_data["rust_to_ts"] == "test"
            assert ts_data["number"] == 123
        finally:
            Path(temp_path).unlink(missing_ok=True)
            
    def test_ts_serializes_rust_deserializes(self, rust_binary, ts_test_path):
        """Test TypeScript serializes and Rust deserializes."""
        if not rust_binary.exists() or not ts_test_path.exists():
            pytest.skip("Required binaries not found")
            
        test_data = {"ts_to_rust": "test", "value": 456}
        
        # TypeScript serializes
        result = subprocess.run(
            ["node", str(ts_test_path), "serialize", json.dumps(test_data)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"TypeScript failed: {result.stderr}"
        
        ts_hex = result.stdout.strip()
        ts_binary = bytes.fromhex(ts_hex)
        
        # Write to temp file for Rust
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(ts_binary)
            temp_path = f.name
            
        try:
            # Rust deserializes
            result = subprocess.run(
                [str(rust_binary), "deserialize", temp_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Rust failed: {result.stderr}"
            
            rust_data = json.loads(result.stdout)
            assert rust_data["ts_to_rust"] == "test"
            assert rust_data["value"] == 456
        finally:
            Path(temp_path).unlink(missing_ok=True)
            
    def test_canonical_consistency(self, rust_binary, ts_test_path):
        """Test canonical serialization consistency between Rust and TypeScript."""
        if not rust_binary.exists() or not ts_test_path.exists():
            pytest.skip("Required binaries not found")
            
        data = {"x": 10, "y": 20, "z": 30}
        
        # Rust canonical
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            temp_path = f.name
            
        try:
            result = subprocess.run(
                [str(rust_binary), "serialize_canonical", json.dumps(data), temp_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Rust failed: {result.stderr}"
            
            with open(temp_path, "rb") as f:
                rust_binary_data = f.read()
            rust_hex = rust_binary_data.hex()
            
            # TypeScript canonical hash
            result = subprocess.run(
                ["node", str(ts_test_path), "canonical_hash", rust_hex],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"TypeScript failed: {result.stderr}"
            
            ts_hash = result.stdout.strip()
            
            # Rust hash
            import hashlib
            rust_hash = hashlib.sha256(rust_binary_data).hexdigest()
            
            # Should be the same
            assert ts_hash == rust_hash
        finally:
            Path(temp_path).unlink(missing_ok=True)
            
    def test_message_consistency(self, rust_binary, ts_test_path):
        """Test message consistency between Rust and TypeScript."""
        if not rust_binary.exists() or not ts_test_path.exists():
            pytest.skip("Required binaries not found")
            
        message = {
            "version": "3.0.0",
            "type": "propose",
            "sender": "rust_agent",
            "recipient": "ts_agent",
            "payload": {"task": "test"}
        }
        
        # Rust creates message
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            temp_path = f.name
            
        try:
            result = subprocess.run(
                [str(rust_binary), "create_message", json.dumps(message), temp_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Rust failed: {result.stderr}"
            
            with open(temp_path, "rb") as f:
                rust_msg = f.read()
            rust_hex = rust_msg.hex()
            
            # TypeScript processes message
            result = subprocess.run(
                ["node", str(ts_test_path), "process_message", rust_hex],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"TypeScript failed: {result.stderr}"
            
            ts_response = json.loads(result.stdout)
            assert "type" in ts_response
        finally:
            Path(temp_path).unlink(missing_ok=True)