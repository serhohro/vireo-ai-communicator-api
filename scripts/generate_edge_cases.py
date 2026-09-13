#!/usr/bin/env python3
"""
Generate edge case test vectors for Vireo v3.0.0.

This script generates malformed and edge case binary files for testing.
Run with: python scripts/generate_edge_cases.py
"""

import os
import sys
import random
import struct
from pathlib import Path

# Додаємо шлях до кореня проєкту
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.crypto.ed25519 import generate_keypair
    from core.protocol.message import Message, Intent
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    print("⚠️  Warning: Core modules not found. Using fallback generators.")


def generate_malformed_magic():
    """Generate malformed message with invalid magic."""
    data = bytearray()
    data.extend(b"MALF")  # Invalid magic (should be "VIRE")
    data.extend(b"\x30\x00\x00\x00")
    data.extend(bytes([random.randint(0, 255) for _ in range(100)]))
    return bytes(data)


def generate_malformed_version():
    """Generate malformed message with invalid version."""
    data = bytearray()
    data.extend(b"VIRE")
    data.extend(b"\xFF\x00\x00\x00")  # Invalid version
    data.extend(bytes([random.randint(0, 255) for _ in range(100)]))
    return bytes(data)


def generate_malformed_truncated():
    """Generate malformed truncated message."""
    data = bytearray()
    data.extend(b"VIRE")
    data.extend(b"\x30\x00\x00\x00")
    data.extend(b"\x1d")
    data.extend(b"did:vireo:agent:alice")
    return bytes(data)


def generate_malformed_invalid_nonce():
    """Generate malformed message with invalid nonce length."""
    data = bytearray()
    data.extend(b"VIRE")
    data.extend(b"\x30\x00\x00\x00")
    data.extend(b"\x1d")
    data.extend(b"did:vireo:agent:alice")
    data.extend(b"\x1b")
    data.extend(b"did:vireo:agent:bob")
    data.extend(b"\x01")
    data.extend(b"\x00" * 8)
    data.extend(b"\x00" * 8)  # WRONG: 8 bytes instead of 16
    return bytes(data)


def generate_malformed_invalid_signature():
    """Generate malformed message with invalid signature length."""
    data = bytearray()
    data.extend(b"VIRE")
    data.extend(b"\x30\x00\x00\x00")
    data.extend(b"\x1d")
    data.extend(b"did:vireo:agent:alice")
    data.extend(b"\x1b")
    data.extend(b"did:vireo:agent:bob")
    data.extend(b"\x01")
    data.extend(b"\x00" * 8)
    data.extend(b"\x00" * 16)
    data.extend(b"\x09")
    data.extend(b"prop_001")
    data.extend(b"\x00" * 32)
    data.extend(b"\x00" * 32)  # WRONG: 32 bytes instead of 64
    return bytes(data)


def generate_malformed_empty():
    """Generate empty message."""
    return b""


def generate_malformed_random():
    """Generate random malformed message."""
    return bytes([random.randint(0, 255) for _ in range(random.randint(10, 200))])


def generate_malformed_extra_bytes():
    """Generate message with extra bytes at the end."""
    if HAS_CORE:
        try:
            private_key, public_key = generate_keypair()
            msg = Message.create(
                sender="did:vireo:agent:alice",
                recipient="did:vireo:agent:bob",
                intent=Intent.PROPOSE,
                proposal_id="test_prop",
                payload={"hello": "world"}
            )
            msg.sign(private_key)
            data = bytearray(msg.serialize())
            data.extend(b"\xFF" * 50)
            return bytes(data)
        except Exception:
            pass
    return generate_malformed_magic()


def generate_duplicate_keys():
    """Generate message with duplicate keys in payload."""
    if HAS_CORE:
        try:
            private_key, public_key = generate_keypair()
            msg = Message.create(
                sender="did:vireo:agent:alice",
                recipient="did:vireo:agent:bob",
                intent=Intent.PROPOSE,
                proposal_id="test_dup",
                payload={"a": 1, "a": 2}  # Duplicate key!
            )
            msg.sign(private_key)
            return msg.serialize()
        except Exception:
            pass
    
    # Fallback
    data = bytearray()
    data.extend(b"VIRE\x30\x00\x00\x00")
    data.extend(b"\x1d")
    data.extend(b"did:vireo:agent:alice")
    data.extend(b"\x1b")
    data.extend(b"did:vireo:agent:bob")
    data.extend(b"\x01")
    data.extend(b"\x00" * 8)
    data.extend(b"\x00" * 16)
    data.extend(b"\x09")
    data.extend(b"test_dup")
    data.extend(b"\x00" * 32)
    data.extend(b"\x00" * 64)
    return bytes(data)


def generate_edge_cases():
    """Generate all edge case test vectors."""
    
    # ВАЖЛИВО: використовуємо вашу структуру
    edge_dir = Path("specification/test_vectors/test_vectors/edge_cases")
    edge_dir.mkdir(parents=True, exist_ok=True)
    
    generators = {
        "malformed.bin": ("Invalid magic (MALF instead of VIRE)", generate_malformed_magic),
        "malformed_v2.bin": ("Invalid version (0xFF instead of 0x30)", generate_malformed_version),
        "malformed_v3.bin": ("Truncated message", generate_malformed_truncated),
        "malformed_v4.bin": ("Invalid nonce length (8 instead of 16)", generate_malformed_invalid_nonce),
        "malformed_v5.bin": ("Invalid signature length (32 instead of 64)", generate_malformed_invalid_signature),
        "malformed_v6.bin": ("Extra bytes at end", generate_malformed_extra_bytes),
        "malformed_v7.bin": ("Empty message", generate_malformed_empty),
        "malformed_v8.bin": ("Random data", generate_malformed_random),
        "duplicate_keys.bin": ("Duplicate keys in payload", generate_duplicate_keys),
    }
    
    print("=" * 60)
    print("🧪 Generating Edge Case Test Vectors")
    print("=" * 60)
    print(f"Output: {edge_dir.absolute()}")
    print()
    
    for filename, (description, generator) in generators.items():
        filepath = edge_dir / filename
        try:
            data = generator()
            with open(filepath, "wb") as f:
                f.write(data)
            print(f"✅ {filename} ({len(data)} bytes)")
            print(f"   {description}")
        except Exception as e:
            print(f"❌ {filename}: {e}")
    
    print()
    print("=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    generate_edge_cases()