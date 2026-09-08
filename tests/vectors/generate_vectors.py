#!/usr/bin/env python3
"""
Generate Test Vectors for tests/vectors/
"""

import json
import struct
import hashlib
from pathlib import Path
from datetime import datetime


def encode_canonical(data):
    if data is None:
        return b"\x00"
    elif isinstance(data, bool):
        return b"\x01" if data else b"\x00"
    elif isinstance(data, int):
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
        return encode_canonical(len(encoded)) + encoded
    elif isinstance(data, bytes):
        return encode_canonical(len(data)) + data
    elif isinstance(data, list):
        result = encode_canonical(len(data))
        for item in data:
            result += encode_canonical(item)
        return result
    elif isinstance(data, dict):
        items = sorted(data.items())
        result = encode_canonical(len(items))
        for key, value in items:
            result += encode_canonical(key)
            result += encode_canonical(value)
        return result
    else:
        return json.dumps(data, default=str).encode()


def save_vector(filename, data, vectors_dir):
    filepath = vectors_dir / filename
    binary = encode_canonical(data)
    with open(filepath, "wb") as f:
        f.write(binary)
    meta_path = filepath.with_suffix(".json")
    with open(meta_path, "w") as f:
        json.dump({
            "filename": filename,
            "size": len(binary),
            "hash": hashlib.sha256(binary).hexdigest(),
            "data": data,
            "generated": datetime.now().isoformat(),
            "version": "3.0.0"
        }, f, indent=2)
    return binary


def main():
    vectors_dir = Path(__file__).parent
    print("🌿 Generating Vireo v3.0.0 Test Vectors")
    print("=" * 60)
    
    propose_data = {
        "version": "3.0.0",
        "type": "propose",
        "id": "msg_1234567890",
        "sender": "did:vireo:alice",
        "recipient": "did:vireo:bob",
        "timestamp": 1700000000,
        "nonce": "n_abcdef123",
        "payload": {
            "task": "analyze_code",
            "parameters": {"language": "python", "depth": "full"},
            "contract": {"price": 100, "deadline": "2024-12-31", "terms": ["quality", "timeliness"]}
        }
    }
    save_vector("propose_v3_0.bin", propose_data, vectors_dir)
    print("  ✓ propose_v3_0.bin")
    
    commit_data = {
        "version": "3.0.0",
        "type": "commit",
        "id": "msg_1234567891",
        "sender": "did:vireo:bob",
        "recipient": "did:vireo:alice",
        "timestamp": 1700000001,
        "nonce": "n_abcdef124",
        "payload": {"accepted": True, "counter_offer": {"price": 75, "deadline": "2024-12-20"}, "signature": "sig_commit_123456"}
    }
    save_vector("commit_v3_0.bin", commit_data, vectors_dir)
    print("  ✓ commit_v3_0.bin")
    
    execute_data = {
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
            "parameters": {"analysis_type": "statistical", "confidence": 0.95},
            "context": {"workflow_id": "wf_abc123", "step": 3}
        }
    }
    save_vector("execute_v3_0.bin", execute_data, vectors_dir)
    print("  ✓ execute_v3_0.bin")
    
    verify_data = {
        "version": "3.0.0",
        "type": "verify",
        "id": "msg_1234567893",
        "sender": "did:vireo:bob",
        "recipient": "did:vireo:alice",
        "timestamp": 1700000003,
        "nonce": "n_abcdef126",
        "payload": {
            "result": "analysis_complete",
            "metrics": {"processing_time": 45.2, "memory_used": 2.3, "accuracy": 0.97},
            "evidence": ["data_validation", "model_validation"]
        }
    }
    save_vector("verify_v3_0.bin", verify_data, vectors_dir)
    print("  ✓ verify_v3_0.bin")
    
    escalate_data = {
        "version": "3.0.0",
        "type": "escalate",
        "id": "msg_1234567894",
        "sender": "did:vireo:alice",
        "recipient": "did:vireo:bob",
        "timestamp": 1700000004,
        "nonce": "n_abcdef127",
        "payload": {
            "reason": "Quality below agreement",
            "evidence": ["incorrect_data", "delayed_response"],
            "resolution": "partial_refund",
            "amount": 25,
            "arbitrator": "did:vireo:arbitrator"
        }
    }
    save_vector("escalate_v3_0.bin", escalate_data, vectors_dir)
    print("  ✓ escalate_v3_0.bin")
    
    done_data = {
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
    save_vector("done_v3_0.bin", done_data, vectors_dir)
    print("  ✓ done_v3_0.bin")
    
    edge_dir = vectors_dir / "edge_cases"
    edge_dir.mkdir(exist_ok=True)
    
    unicode_data = {
        "version": "3.0.0",
        "type": "test",
        "payload": {
            "text": "Café résumé naïve",
            "unicode": "你好世界🌍",
            "emoji": "🚀🌿💬",
            "nfc": "\u00E9",
            "nfd": "\u0065\u0301"
        }
    }
    save_vector("edge_cases/unicode_nfc.bin", unicode_data, vectors_dir)
    print("  ✓ edge_cases/unicode_nfc.bin")
    
    float_data = {
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
    save_vector("edge_cases/float_negative_zero.bin", float_data, vectors_dir)
    print("  ✓ edge_cases/float_negative_zero.bin")
    
    big_int_data = {
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
    save_vector("edge_cases/big_int.bin", big_int_data, vectors_dir)
    print("  ✓ edge_cases/big_int.bin")
    
    duplicate_data = {"version": "3.0.0", "type": "test", "payload": {"key": "second"}}
    save_vector("edge_cases/duplicate_keys.bin", duplicate_data, vectors_dir)
    print("  ✓ edge_cases/duplicate_keys.bin")
    
    malformed_cases = [
        ("malformed.bin", {"version": "3.0.0", "type": None, "payload": {}}),
        ("malformed_v2.bin", {"version": "3.0.0", "type": "unknown_type", "payload": {}}),
        ("malformed_v3.bin", {"version": "3.0.0", "type": "propose", "payload": "not_an_object"}),
        ("malformed_v4.bin", {"version": "3.0.0", "type": "propose", "payload": {"field": "object"}}),
        ("malformed_v5.bin", {"version": "3.0.0", "type": "propose", "payload": {"binary": "binary_data"}}),
        ("malformed_v6.bin", {"version": "invalid", "type": "propose", "payload": {}}),
        ("malformed_v7.bin", {"type": "propose", "payload": {}}),
        ("malformed_v8.bin", {"version": "3.0.0", "payload": {}}),
    ]
    for filename, data in malformed_cases:
        save_vector(f"edge_cases/{filename}", data, vectors_dir)
        print(f"  ✓ edge_cases/{filename}")
    
    metadata = {
        "version": "3.0.0",
        "generated": datetime.now().isoformat(),
        "total_vectors": 6,
        "total_edge_cases": 13,
        "description": "Vireo v3.0.0 Test Vectors",
        "vectors": ["propose_v3_0.bin", "commit_v3_0.bin", "execute_v3_0.bin", "verify_v3_0.bin", "escalate_v3_0.bin", "done_v3_0.bin"],
        "edge_cases": [
            "edge_cases/unicode_nfc.bin", "edge_cases/float_negative_zero.bin", "edge_cases/big_int.bin",
            "edge_cases/duplicate_keys.bin", "edge_cases/malformed.bin", "edge_cases/malformed_v2.bin",
            "edge_cases/malformed_v3.bin", "edge_cases/malformed_v4.bin", "edge_cases/malformed_v5.bin",
            "edge_cases/malformed_v6.bin", "edge_cases/malformed_v7.bin", "edge_cases/malformed_v8.bin"
        ]
    }
    with open(vectors_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ All test vectors generated successfully!")
    print(f"   Location: {vectors_dir}")
    print(f"   Total vectors: {len(metadata['vectors'])}")
    print(f"   Edge cases: {len(metadata['edge_cases'])}")


if __name__ == "__main__":
    main()