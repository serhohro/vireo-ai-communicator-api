#!/usr/bin/env python3
"""
Vireo v3.1 — Conformance Test Vector Generator

Reads tests/conformance/vectors/*.json, fills in `expected_outputs`
using the Python SDK (core.crypto).

The Rust SDK must reproduce identical canonical_bytes, wire_hash,
and signature for the same inputs.

Usage:
    python scripts/generate_test_vectors.py
    python scripts/generate_test_vectors.py tests/conformance/vectors/001_propose_commit.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.crypto.canonical import canonical_wire_bytes  # noqa: E402
from core.crypto.blake2b import wire_hash, did_hash      # noqa: E402
from core.crypto.ed25519 import (                         # noqa: E402
    sign_vireo_message,
    verify_vireo_message,
)

VECTORS_DIR = ROOT / "tests" / "conformance" / "vectors"


def build_envelope(fields: dict) -> dict:
    """Build the envelope dict that canonical_wire_bytes expects."""
    nonce = bytes.fromhex(fields["nonce_hex"])
    if len(nonce) != 16:
        raise ValueError(f"nonce must be 16 bytes, got {len(nonce)}")

    return {
        "intent": fields["intent"],
        "timestamp_ms": fields["timestamp_ms"],
        "nonce": nonce,
        "sender_did_hash": did_hash(fields["sender_did"]),
        "recipient_did_hash": did_hash(fields["recipient_did"]),
        "payload": fields["payload"],
    }


def generate_one(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        vector = json.load(f)

    fields = vector["input_fields"]
    keys = vector["keys"]

    env = build_envelope(fields)
    canonical = canonical_wire_bytes(env)
    w_hash = wire_hash(canonical)
    signature = sign_vireo_message(keys["private_key_hex"], canonical)

    # Sanity check: verify the signature we just produced
    ok, err = verify_vireo_message(
        keys["public_key_hex"], canonical, signature
    )
    if not ok:
        raise RuntimeError(f"Self-verification failed: {err}")

    vector["expected_outputs"] = {
        "canonical_bytes_hex": canonical.hex(),
        "canonical_bytes_len": len(canonical),
        "wire_hash_hex": w_hash.hex(),
        "signature_hex": signature,
    }

    with path.open("w", encoding="utf-8") as f:
        json.dump(vector, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return vector["expected_outputs"]


def main():
    targets = (
        [Path(p) for p in sys.argv[1:]]
        if len(sys.argv) > 1
        else sorted(VECTORS_DIR.glob("*.json"))
    )

    if not targets:
        print(f"❌ No vectors found in {VECTORS_DIR}")
        sys.exit(1)

    print(f"🌿 Vireo v3.1 — generating {len(targets)} vector(s)\n")

    for path in targets:
        print(f"→ {path.name}")
        out = generate_one(path)
        print(f"   canonical: {out['canonical_bytes_len']} bytes")
        print(f"   wire_hash: {out['wire_hash_hex']}")
        print(f"   signature: {out['signature_hex'][:32]}…")
        print()

    print(f"✅ Done. {len(targets)} vector(s) updated.")


if __name__ == "__main__":
    main()