"""
Crypto benchmark: BLAKE2b vs SHA-256, Ed25519 sign/verify.

Run:
    python -m benches.wire_perf.bench_crypto
"""

import hashlib
import json
import statistics
import time

from core.crypto.ed25519 import (
    generate_keypair, sign_vireo_message, verify_vireo_message,
)
from core.crypto.blake2b import blake2b_256


def bench_hash(func, data, iterations=1000):
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        func(data)
        times.append(time.perf_counter_ns() - start)
    return {"mean_ns": statistics.mean(times), "median_ns": statistics.median(times)}


def main():
    data = b"x" * 1024
    blake = bench_hash(blake2b_256, data)
    sha = bench_hash(lambda d: hashlib.sha256(d).digest(), data)

    kp = generate_keypair()
    msg = b"sample message for signing"

    sig_times = []
    for _ in range(1000):
        start = time.perf_counter_ns()
        sig = sign_vireo_message(kp["private_key_hex"], msg)
        sig_times.append(time.perf_counter_ns() - start)

    ver_times = []
    for _ in range(1000):
        start = time.perf_counter_ns()
        verify_vireo_message(kp["public_key_hex"], msg, sig)
        ver_times.append(time.perf_counter_ns() - start)

    print(json.dumps({
        "hash_1kb": {
            "blake2b_256_mean_ns": blake["mean_ns"],
            "sha256_mean_ns": sha["mean_ns"],
            "speedup_blake_vs_sha": round(sha["mean_ns"] / blake["mean_ns"], 2),
        },
        "ed25519": {
            "sign_mean_ns": statistics.mean(sig_times),
            "verify_mean_ns": statistics.mean(ver_times),
        },
    }, indent=2))


if __name__ == "__main__":
    main()