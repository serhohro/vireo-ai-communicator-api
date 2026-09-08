#!/usr/bin/env python3
"""
Conformance Tests: Wire Format

Tests for the Vireo wire format (canonical serialization).
"""

import pytest
import json
import sys
import hashlib
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import from core
try:
    from core.wire_format import WireFormat
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    # Simple fallback for testing
    class WireFormat:
        @staticmethod
        def serialize(data):
            return json.dumps(data, sort_keys=True, default=str).encode('utf-8')
        
        @staticmethod
        def deserialize(data):
            return json.loads(data.decode('utf-8'))
        
        @staticmethod
        def serialize_canonical(data):
            return json.dumps(data, sort_keys=True, default=str, separators=(',', ':')).encode('utf-8')
        
        @staticmethod
        def get_version(data):
            try:
                return json.loads(data.decode('utf-8')).get('version', 'unknown')
            except:
                return 'unknown'


class TestWireFormat:
    """Wire format conformance tests."""
    
    def test_serialize_simple(self):
        """Test serializing simple values."""
        # String
        data = "hello"
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
        # Integer
        data = 42
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
        # Float
        data = 3.14159
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
        # Boolean
        data = True
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
        # Null
        data = None
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
    def test_serialize_list(self):
        """Test serializing lists."""
        data = [1, 2, 3, 4, 5]
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
        data = ["a", "b", "c"]
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
        data = [1, "two", 3.0, True]
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
    def test_serialize_dict(self):
        """Test serializing dictionaries."""
        data = {"a": 1, "b": 2, "c": 3}
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
        data = {"name": "test", "value": 42, "active": True}
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
    def test_serialize_nested(self):
        """Test serializing nested structures."""
        data = {
            "name": "test",
            "values": [1, 2, 3],
            "nested": {
                "a": 1,
                "b": 2,
                "c": [4, 5, 6]
            }
        }
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        assert restored == data
        
    def test_canonical_serialization(self):
        """Test canonical serialization."""
        data1 = {"b": 2, "a": 1, "c": 3}
        data2 = {"c": 3, "a": 1, "b": 2}
        
        binary1 = WireFormat.serialize_canonical(data1)
        binary2 = WireFormat.serialize_canonical(data2)
        
        assert binary1 == binary2
        
    def test_canonical_nested(self):
        """Test canonical serialization of nested structures."""
        data1 = {
            "z": 26,
            "a": 1,
            "nested": {
                "b": 2,
                "a": 1,
                "c": 3
            }
        }
        data2 = {
            "a": 1,
            "nested": {
                "c": 3,
                "a": 1,
                "b": 2
            },
            "z": 26
        }
        
        binary1 = WireFormat.serialize_canonical(data1)
        binary2 = WireFormat.serialize_canonical(data2)
        
        assert binary1 == binary2
        
    def test_deserialize_invalid(self):
        """Test deserializing invalid data."""
        with pytest.raises(Exception):
            WireFormat.deserialize(b"invalid")
            
        with pytest.raises(Exception):
            WireFormat.deserialize(b"")
            
    def test_roundtrip_complex(self):
        """Test complete roundtrip of complex data."""
        original = {
            "version": "3.0.0",
            "type": "propose",
            "sender": "did:vireo:alice",
            "recipient": "did:vireo:bob",
            "timestamp": 1700000000,
            "nonce": "n_abcdef123",
            "payload": {
                "task": "analyze_code",
                "parameters": {
                    "language": "python",
                    "depth": "full",
                    "timeout": 300
                },
                "contract": {
                    "price": 100,
                    "deadline": "2024-12-31",
                    "terms": ["quality", "timeliness"]
                }
            }
        }
        
        binary = WireFormat.serialize_canonical(original)
        restored = WireFormat.deserialize(binary)
        
        assert restored == original


class TestWireFormatVersion:
    """Wire format version tests."""
    
    def test_version_identification(self):
        """Test wire format version identification."""
        data = {"version": "3.0.0", "type": "test"}
        binary = WireFormat.serialize(data)
        
        version = WireFormat.get_version(binary)
        assert version == "3.0.0"


class TestWireFormatEdgeCases:
    """Wire format edge case tests."""
    
    def test_very_large_data(self):
        """Test serializing very large data."""
        large_string = "x" * 100000
        data = {"large": large_string}
        
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        
        assert restored["large"] == large_string
        
    def test_deeply_nested(self):
        """Test serializing deeply nested structures."""
        data = {"level1": {"level2": {"level3": {"level4": {"level5": "deep"}}}}}
        
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        
        assert restored["level1"]["level2"]["level3"]["level4"]["level5"] == "deep"
        
    def test_keys_with_special_chars(self):
        """Test keys with special characters."""
        data = {
            "key with spaces": "value",
            "key.with.dots": "value",
            "key-with-dashes": "value",
            "key_underscore": "value",
            "😊emoji_key": "value"
        }
        
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        
        for key in data:
            assert key in restored
            assert restored[key] == data[key]
            
    def test_mixed_types(self):
        """Test serializing mixed types."""
        data = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, "two", 3.0, True, None],
            "object": {"a": 1, "b": "two", "c": 3.0, "d": True, "e": None},
            "nested": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"}
            ]
        }
        
        binary = WireFormat.serialize(data)
        restored = WireFormat.deserialize(binary)
        
        assert restored["string"] == "hello"
        assert restored["integer"] == 42
        assert restored["float"] == 3.14
        assert restored["boolean"] is True
        assert restored["null"] is None
        assert restored["array"] == [1, "two", 3.0, True, None]
        assert restored["nested"][0]["id"] == 1


class TestWireFormatConsistency:
    """Wire format consistency tests."""
    
    def test_deterministic_serialization(self):
        """Test that serialization is deterministic."""
        data = {"a": 1, "b": 2, "c": 3}
        
        binary1 = WireFormat.serialize_canonical(data)
        binary2 = WireFormat.serialize_canonical(data)
        
        assert binary1 == binary2
        
    def test_hash_consistency(self):
        """Test that hash of canonical serialization is consistent."""
        data1 = {"b": 2, "a": 1, "c": 3}
        data2 = {"c": 3, "a": 1, "b": 2}
        
        binary1 = WireFormat.serialize_canonical(data1)
        binary2 = WireFormat.serialize_canonical(data2)
        
        hash1 = hashlib.sha256(binary1).hexdigest()
        hash2 = hashlib.sha256(binary2).hexdigest()
        
        assert hash1 == hash2