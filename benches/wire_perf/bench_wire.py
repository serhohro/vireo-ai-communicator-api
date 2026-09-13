"""
Wire performance benchmark: JSON vs Vireo canonical binary.

Run:
    python -m benches.wire_perf.bench_wire --profile=all
"""

import argparse
import json
import statistics
import time

from core.crypto.canonical import canonical_wire_bytes
from core.crypto.blake2b import did_hash


PROFILES = {
    "small": {
        "intent": "COMMIT",
        "timestamp_ms": 1773168000000,
        "nonce": bytes(16),
        "sender_did_hash": did_hash("did:vireo:alice"),
        "recipient_did_hash": did_hash("did:vireo:bob"),
        "payload": {"ok": True},
    },
    "medium": {
        "intent": "PROPOSE",
        "timestamp_ms": 1773168000000,
        "nonce": bytes(16),
        "sender_did_hash": did_hash("did:vireo:alice"),
        "recipient_did_hash": did_hash("did:vireo:bob"),
        "payload": {
            "contract": {"max_tokens": 1000, "timeout_sec": 30},
            "task": "analyze_data",
            "capabilities": ["translate", "summarize", "classify"],
        },
    },
    "large": {
        "intent": "EXECUTE",
        "timestamp_ms": 1773168000000,
        "nonce": bytes(16),
        "sender_did_hash": did_hash("did:vireo:alice"),
        "recipient_did_hash": did_hash("did:vireo:bob"),
        "payload": {"tensor": list(range(50000))},
    },
}


def bench_json(envelope, iterations=1000):
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        data = json.dumps({
            "intent": envelope["intent"],
            "timestamp_ms": envelope["timestamp_ms"],
            "nonce": envelope["nonce"].hex(),
            "sender_did_hash": envelope["sender_did_hash"].hex(),
            "recipient_did_hash": envelope["recipient_did_hash"].hex(),
            "payload": envelope["payload"],
        }, separators=(",", ":")).encode("utf-8")
        times.append(time.perf_counter_ns() - start)
    return {
        "mean_ns": statistics.mean(times),
        "median_ns": statistics.median(times),
        "p99_ns": sorted(times)[int(len(times) * 0.99)],
        "size_bytes": len(data),
    }


def bench_vireo(envelope, iterations=1000):
    times = []
    size = 0
    for _ in range(iterations):
        start = time.perf_counter_ns()
        data = canonical_wire_bytes(envelope)
        times.append(time.perf_counter_ns() - start)
        size = len(data)
    return {
        "mean_ns": statistics.mean(times),
        "median_ns": statistics.median(times),
        "p99_ns": sorted(times)[int(len(times) * 0.99)],
        "size_bytes": size,
    }


def run_profile(name):
    env = PROFILES[name]
    json_r = bench_json(env)
    vireo_r = bench_vireo(env)
    speedup = json_r["mean_ns"] / vireo_r["mean_ns"] if vireo_r["mean_ns"] else 0
    return {
        "profile": name,
        "json": json_r,
        "vireo": vireo_r,
        "speedup": round(speedup, 2),
        "size_ratio": round(json_r["size_bytes"] / vireo_r["size_bytes"], 2) if vireo_r["size_bytes"] else 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="all", choices=["all", *PROFILES.keys()])
    parser.add_argument("--iterations", type=int, default=1000)
    args = parser.parse_args()

    profiles = PROFILES.keys() if args.profile == "all" else [args.profile]
    results = [run_profile(p) for p in profiles]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()