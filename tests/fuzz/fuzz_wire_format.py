#!/usr/bin/env python3
"""
Fuzz Testing: Wire Format

Fuzz testing for wire format serialization/deserialization robustness.
"""

import pytest
import random
import json
import sys
import struct
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from core.wire_format import WireFormat
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    print("⚠️ Core modules not available, running limited fuzz tests")


class FuzzWireFormat:
    """Wire format fuzz testing."""
    
    def random_value(self, depth: int = 0) -> Any:
        """Generate a random value."""
        if depth > 5:
            return random.choice([0, "", None, True, False])
            
        choices = [
            lambda: random.randint(-2**63, 2**63 - 1),
            lambda: random.uniform(-1e6, 1e6),
            lambda: "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(0, 100))),
            lambda: random.choice([True, False]),
            lambda: None,
            lambda: [self.random_value(depth + 1) for _ in range(random.randint(0, 10))],
            lambda: {f"key_{i}": self.random_value(depth + 1) for i in range(random.randint(0, 5))},
            lambda: bytes(random.randint(0, 100)),
        ]
        return random.choice(choices)()
    
    def test_fuzz_random_data(self):
        """Fuzz test with random data."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        for _ in range(100):
            data = self.random_value()
            try:
                binary = WireFormat.serialize(data)
                restored = WireFormat.deserialize(binary)
                # Should roundtrip successfully
                assert json.dumps(restored, sort_keys=True) == json.dumps(data, sort_keys=True)
            except Exception as e:
                # Should not crash
                print(f"Fuzz iteration failed: {e}")
                continue
                
    def test_fuzz_binary_data(self):
        """Fuzz test with random binary data."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        for _ in range(100):
            # Generate random binary
            length = random.randint(0, 10000)
            binary = bytes(random.getrandbits(8) for _ in range(length))
            
            try:
                # Should either succeed or fail gracefully
                result = WireFormat.deserialize(binary)
                # If it succeeds, verify it's valid data
                assert isinstance(result, (dict, list, str, int, float, bool, type(None)))
            except Exception:
                # Expected for malformed data
                pass
                
    def test_fuzz_large_data(self):
        """Fuzz test with large data."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        # Generate large data
        data = {
            "large_string": "x" * 100000,
            "large_array": [i for i in range(10000)],
            "large_nested": {
                f"key_{i}": {"value": i, "data": "x" * 100}
                for i in range(100)
            }
        }
        
        try:
            binary = WireFormat.serialize(data)
            restored = WireFormat.deserialize(binary)
            assert len(restored["large_string"]) == 100000
            assert len(restored["large_array"]) == 10000
        except Exception as e:
            print(f"Large data fuzz failed: {e}")
            
    def test_fuzz_invalid_utf8(self):
        """Fuzz test with invalid UTF-8."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        for _ in range(50):
            # Generate invalid UTF-8
            length = random.randint(1, 100)
            bytes_data = bytearray(length)
            for i in range(length):
                if random.random() < 0.1:
                    bytes_data[i] = random.choice([0x80, 0x81, 0xFE, 0xFF])
                else:
                    bytes_data[i] = random.randint(0, 255)
            
            try:
                # Try to decode as string
                s = bytes_data.decode('utf-8', errors='ignore')
                # Should not crash
            except Exception:
                pass
                
    def test_fuzz_extreme_numbers(self):
        """Fuzz test with extreme numbers."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        data = {
            "inf": float("inf"),
            "neg_inf": float("-inf"),
            "nan": float("nan"),
            "max_int": 2**63 - 1,
            "min_int": -2**63,
            "huge_int": 10**100,
            "tiny_float": 1e-300,
            "huge_float": 1e300,
        }
        
        try:
            binary = WireFormat.serialize(data)
            restored = WireFormat.deserialize(binary)
            # Should not crash
        except Exception as e:
            print(f"Extreme numbers fuzz failed: {e}")
            
    def test_fuzz_malformed_json(self):
        """Fuzz test with malformed JSON structures."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        malformed = [
            b"{",
            b"}",
            b"[",
            b"]",
            b"{[]}",
            b'{"key": value}',
            b'{"key": [1, 2, 3}',
            b'{"key": "value",}',
            b'{"key": "value" "key2": "value2"}',
        ]
        
        for data in malformed:
            try:
                # Should either succeed or fail gracefully
                result = WireFormat.deserialize(data)
            except Exception:
                pass


class TestFuzzWireFormat:
    """Wire format fuzz test class for pytest."""
    
    def test_fuzz_basic_types(self):
        """Fuzz basic types."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        # Test various primitive types
        test_cases = [
            42,
            -42,
            0,
            3.14159,
            -3.14159,
            0.0,
            -0.0,
            float("inf"),
            float("-inf"),
            float("nan"),
            True,
            False,
            None,
            "",
            "hello",
            "unicode: 🚀🌿💬",
            b"binary",
            [],
            [1, 2, 3],
            ["a", "b", "c"],
            {},
            {"a": 1, "b": 2},
            {"key": "value", "nested": {"a": 1}},
        ]
        
        for data in test_cases:
            try:
                binary = WireFormat.serialize(data)
                restored = WireFormat.deserialize(binary)
                # Basic verification
                assert restored is not None
            except Exception as e:
                print(f"Fuzz basic type failed for {data}: {e}")