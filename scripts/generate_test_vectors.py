#!/usr/bin/env python3
"""
Generate Test Vectors for Vireo v3.0.0

Generates binary test vectors for cross-implementation conformance testing.
Includes canonical serialization, signatures, and edge cases.
"""

import os
import sys
import json
import struct
import hashlib
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.crypto import ed25519, blake2b
    from core.protocol import Message, Protocol
except ImportError:
    print("Warning: core modules not available. Generating basic vectors only.")
    ed25519 = None
    blake2b = None


class TestVectorGenerator:
    """Generate test vectors for Vireo conformance testing."""
    
    def __init__(self, output_dir: str = "specification/test_vectors"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create edge cases directory
        self.edge_dir = self.output_dir / "edge_cases"
        self.edge_dir.mkdir(exist_ok=True)
        
        self.vectors = []
        self.edge_cases = []
        
    def generate_all(self):
        """Generate all test vectors."""
        print("🌿 Generating Vireo v3.0.0 Test Vectors")
        print("=" * 60)
        
        # Protocol messages
        self.generate_propose_vector()
        self.generate_commit_vector()
        self.generate_execute_vector()
        self.generate_verify_vector()
        self.generate_escalate_vector()
        self.generate_done_vector()
        
        # Edge cases
        self.generate_unicode_nfc_edge()
        self.generate_float_negative_zero_edge()
        self.generate_big_int_edge()
        self.generate_duplicate_keys_edge()
        self.generate_malformed_vectors()
        
        # Generate metadata
        self.generate_metadata()
        
        print("\n" + "=" * 60)
        print(f"✅ Generated {len(self.vectors)} test vectors")
        print(f"   - {len(self.vectors)} protocol vectors")
        print(f"   - {len(self.edge_cases)} edge cases")
        print(f"   Location: {self.output_dir}")
    
    def generate_propose_vector(self):
        """Generate PROPOSE message vector."""
        data = {
            "version": "3.0.0",
            "type": "propose",
            "id": "msg_1234567890",
            "sender": "did:vireo:alice",
            "recipient": "did:vireo:bob",
            "timestamp": 1700000000,
            "nonce": "n_abcdef123",
            "payload": {
                "task": "analyze_code",
                "parameters": {
                    "language": "python",
                    "depth": "full"
                },
                "contract": {
                    "price": 100,
                    "deadline": "2024-12-31",
                    "terms": ["quality", "timeliness"]
                }
            }
        }
        self._write_vector("propose_v3_0.bin", data)
    
    def generate_commit_vector(self):
        """Generate COMMIT message vector."""
        data = {
            "version": "3.0.0",
            "type": "commit",
            "id": "msg_1234567891",
            "sender": "did:vireo:bob",
            "recipient": "did:vireo:alice",
            "timestamp": 1700000001,
            "nonce": "n_abcdef124",
            "payload": {
                "accepted": True,
                "counter_offer": {
                    "price": 75,
                    "deadline": "2024-12-20"
                },
                "signature": "sig_commit_123456"
            }
        }
        self._write_vector("commit_v3_0.bin", data)
    
    def generate_execute_vector(self):
        """Generate EXECUTE message vector."""
        data = {
            "version": "3.0.0",
            "type": "execute",
            "id": "msg_1234567892",
            "sender": "did:vireo:alice",
            "recipient": "did:vireo:bob",
            "timestamp": 1700000002,
            "nonce": "n_abcdef125",
            "payload": {
                "task_id": "task_001",
                "data": "dataset.csv",
                "parameters": {
                    "analysis_type": "statistical",
                    "confidence": 0.95
                },
                "context": {
                    "workflow_id": "wf_abc123",
                    "step": 3
                }
            }
        }
        self._write_vector("execute_v3_0.bin", data)
    
    def generate_verify_vector(self):
        """Generate VERIFY message vector."""
        data = {
            "version": "3.0.0",
            "type": "verify",
            "id": "msg_1234567893",
            "sender": "did:vireo:bob",
            "recipient": "did:vireo:alice",
            "timestamp": 1700000003,
            "nonce": "n_abcdef126",
            "payload": {
                "result": "analysis_complete",
                "metrics": {
                    "processing_time": 45.2,
                    "memory_used": 2.3,
                    "accuracy": 0.97
                },
                "evidence": [
                    "data_validation",
                    "model_validation"
                ]
            }
        }
        self._write_vector("verify_v3_0.bin", data)
    
    def generate_escalate_vector(self):
        """Generate ESCALATE message vector."""
        data = {
            "version": "3.0.0",
            "type": "escalate",
            "id": "msg_1234567894",
            "sender": "did:vireo:alice",
            "recipient": "did:vireo:bob",
            "timestamp": 1700000004,
            "nonce": "n_abcdef127",
            "payload": {
                "reason": "Quality below agreement",
                "evidence": [
                    "incorrect_data",
                    "delayed_response"
                ],
                "resolution": "partial_refund",
                "amount": 25,
                "arbitrator": "did:vireo:arbitrator"
            }
        }
        self._write_vector("escalate_v3_0.bin", data)
    
    def generate_done_vector(self):
        """Generate DONE message vector."""
        data = {
            "version": "3.0.0",
            "type": "done",
            "id": "msg_1234567895",
            "sender": "did:vireo:bob",
            "recipient": "did:vireo:alice",
            "timestamp": 1700000005,
            "nonce": "n_abcdef128",
            "payload": {
                "status": "success",
                "payment": 75,
                "completed_at": 1700000010,
                "receipt": "rcpt_123456",
                "feedback": "Task completed successfully"
            }
        }
        self._write_vector("done_v3_0.bin", data)
    
    def generate_unicode_nfc_edge(self):
        """Generate Unicode NFC edge case."""
        data = {
            "version": "3.0.0",
            "type": "test",
            "payload": {
                "text": "Café résumé naïve",
                "unicode": "你好世界🌍",
                "emoji": "🚀🌿💬",
                "nfc": "\u00E9",  # é (NFC)
                "nfd": "\u0065\u0301"  # e + combining acute (NFD)
            }
        }
        self._write_edge_case("unicode_nfc.bin", data)
    
    def generate_float_negative_zero_edge(self):
        """Generate float negative zero edge case."""
        data = {
            "version": "3.0.0",
            "type": "test",
            "payload": {
                "positive_zero": 0.0,
                "negative_zero": -0.0,
                "infinity": float("inf"),
                "negative_infinity": float("-inf"),
                "nan": float("nan"),
                "values": [0.0, -0.0, 1.0, -1.0]
            }
        }
        self._write_edge_case("float_negative_zero.bin", data)
    
    def generate_big_int_edge(self):
        """Generate big integer edge case."""
        data = {
            "version": "3.0.0",
            "type": "test",
            "payload": {
                "small": 42,
                "large": 2**63 - 1,
                "larger": 2**128,
                "huge": 2**256,
                "negative": -2**63,
                "list": [1, 2**64, 2**128, 2**256]
            }
        }
        self._write_edge_case("big_int.bin", data)
    
    def generate_duplicate_keys_edge(self):
        """Generate duplicate keys edge case."""
        data = {
            "version": "3.0.0",
            "type": "test",
            "payload": {
                "key": "first",
                "key": "second",  # Duplicate key - should be handled by canonical serialization
                "nested": {
                    "key": "nested_first",
                    "key": "nested_second"
                }
            }
        }
        self._write_edge_case("duplicate_keys.bin", data)
    
    def generate_malformed_vectors(self):
        """Generate malformed message edge cases."""
        malformed_cases = [
            ("malformed.bin", {"version": "3.0.0", "type": None, "payload": {}}),
            ("malformed_v2.bin", {"version": "3.0.0", "type": "unknown_type", "payload": {}}),
            ("malformed_v3.bin", {"version": "3.0.0", "type": "propose", "payload": "not_an_object"}),
            ("malformed_v4.bin", {"version": "3.0.0", "type": "propose", "payload": {"field": object()}}),
            ("malformed_v5.bin", {"version": "3.0.0", "type": "propose", "payload": {"binary": b"\x00\x01\x02"}}),
            ("malformed_v6.bin", {"version": "invalid", "type": "propose", "payload": {}}),
            ("malformed_v7.bin", {"type": "propose", "payload": {}}),  # Missing version
            ("malformed_v8.bin", {"version": "3.0.0", "payload": {}}),  # Missing type
        ]
        
        for filename, data in malformed_cases:
            self._write_edge_case(filename, data, is_malformed=True)
    
    def _write_vector(self, filename: str, data: Dict[str, Any]):
        """Write a test vector to file."""
        filepath = self.output_dir / filename
        
        # Generate binary representation
        binary_data = self._encode_canonical(data)
        
        # Generate hash and signature if available
        if blake2b:
            hash_value = blake2b.blake2b(binary_data)
        else:
            hash_value = hashlib.sha256(binary_data).digest()
        
        # Write file
        with open(filepath, "wb") as f:
            f.write(binary_data)
        
        # Store metadata
        self.vectors.append({
            "filename": filename,
            "size": len(binary_data),
            "hash": hash_value.hex() if isinstance(hash_value, bytes) else hash_value.hex(),
            "type": data.get("type", "unknown"),
            "timestamp": datetime.now().isoformat()
        })
        
        # Also write JSON metadata
        meta_path = filepath.with_suffix(".meta.json")
        with open(meta_path, "w") as f:
            json.dump({
                "filename": filename,
                "size": len(binary_data),
                "hash": hash_value.hex() if isinstance(hash_value, bytes) else hash_value.hex(),
                "type": data.get("type", "unknown"),
                "data": data,
                "generated": datetime.now().isoformat(),
                "version": "3.0.0"
            }, f, indent=2)
        
        print(f"  ✓ {filename} ({len(binary_data)} bytes)")
    
    def _write_edge_case(self, filename: str, data: Dict[str, Any], is_malformed: bool = False):
        """Write an edge case test vector."""
        filepath = self.edge_dir / filename
        
        try:
            binary_data = self._encode_canonical(data)
        except Exception as e:
            # For malformed cases, write raw data
            binary_data = json.dumps(data, default=str).encode()
        
        with open(filepath, "wb") as f:
            f.write(binary_data)
        
        self.edge_cases.append({
            "filename": filename,
            "size": len(binary_data),
            "is_malformed": is_malformed,
            "type": data.get("type", "edge_case")
        })
        
        print(f"  ✓ {filename} (edge case)")
    
    def _encode_canonical(self, data: Any) -> bytes:
        """Encode data in canonical binary format."""
        if data is None:
            return b"\x00"
        elif isinstance(data, bool):
            return b"\x01" if data else b"\x00"
        elif isinstance(data, int):
            # Variable-length integer encoding
            if data == 0:
                return b"\x00"
            negative = data < 0
            value = abs(data)
            result = bytearray()
            while value > 0:
                result.append(value & 0x7F)
                value >>= 7
            if negative:
                result[0] |= 0x80
            return bytes(result)
        elif isinstance(data, float):
            return struct.pack(">d", data)
        elif isinstance(data, str):
            encoded = data.encode("utf-8")
            length = len(encoded)
            return self._encode_canonical(length) + encoded
        elif isinstance(data, bytes):
            return self._encode_canonical(len(data)) + data
        elif isinstance(data, list):
            result = self._encode_canonical(len(data))
            for item in data:
                result += self._encode_canonical(item)
            return result
        elif isinstance(data, dict):
            # Sort keys for canonical representation
            items = sorted(data.items())
            result = self._encode_canonical(len(items))
            for key, value in items:
                result += self._encode_canonical(key)
                result += self._encode_canonical(value)
            return result
        else:
            # Fallback to JSON
            return json.dumps(data, default=str).encode()
    
    def generate_metadata(self):
        """Generate metadata file for all test vectors."""
        metadata = {
            "version": "3.0.0",
            "generated": datetime.now().isoformat(),
            "total_vectors": len(self.vectors),
            "total_edge_cases": len(self.edge_cases),
            "vectors": self.vectors,
            "edge_cases": self.edge_cases,
            "description": "Vireo v3.0.0 Conformance Test Vectors"
        }
        
        meta_path = self.output_dir / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n  ✓ metadata.json")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Vireo test vectors")
    parser.add_argument(
        "-o", "--output",
        default="specification/test_vectors",
        help="Output directory for test vectors"
    )
    parser.add_argument(
        "--edge-only",
        action="store_true",
        help="Generate only edge cases"
    )
    
    args = parser.parse_args()
    
    generator = TestVectorGenerator(args.output)
    
    if args.edge_only:
        generator.generate_unicode_nfc_edge()
        generator.generate_float_negative_zero_edge()
        generator.generate_big_int_edge()
        generator.generate_duplicate_keys_edge()
        generator.generate_malformed_vectors()
        generator.generate_metadata()
    else:
        generator.generate_all()


if __name__ == "__main__":
    main()