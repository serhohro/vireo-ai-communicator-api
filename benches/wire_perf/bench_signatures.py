"""
Ed25519 signature benchmark for Vireo v3.1.

Measures:
- keypair generation
- message signing
- signature verification

Run:
    python -m benches.wire_perf.bench_signatures
"""

import json
import statistics
import time

from core.crypto.ed25519 import (
    generate_keypair, sign_vireo_message, verify_vireo_message,
)


ITERATIONS = 1000


def bench_keypair(iterations=1000):
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        generate_keypair()
        times.append(time.perf_counter_ns() - start)
    return {
        "mean_ns": statistics.mean(times),
        "median_ns": statistics.median(times),
        "p99_ns": sorted(times)[int(len(times) * 0.99)],
    }


def bench_sign(private_key_hex, message, iterations=1000):
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        sign_vireo_message(private_key_hex, message)
        times.append(time.perf_counter_ns() - start)
    return {
        "mean_ns": statistics.mean(times),
        "median_ns": statistics.median(times),
        "p99_ns": sorted(times)[int(len(times) * 0.99)],
    }


def bench_verify(public_key_hex, message, signature, iterations=1000):
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        verify_vireo_message(public_key_hex, message, signature)
        times.append(time.perf_counter_ns() - start)
    return {
        "mean_ns": statistics.mean(times),
        "median_ns": statistics.median(times),
        "p99_ns": sorted(times)[int(len(times) * 0.99)],
    }


def main():
    kp = generate_keypair()
    msg = b"sample message for signing benchmark"

    keypair_stats = bench_keypair()
    sign_stats = bench_sign(kp["private_key_hex"], msg)
    sig = sign_vireo_message(kp["private_key_hex"], msg)
    verify_stats = bench_verify(kp["public_key_hex"], msg, sig)

    print(json.dumps({
        "iterations": ITERATIONS,
        "keypair_generation": keypair_stats,
        "sign": sign_stats,
        "verify": verify_stats,
    }, indent=2))


if __name__ == "__main__":
    main()