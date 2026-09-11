"""
Verifier Agent v3.1 — real verification with evidence.
"""

from protocol.agent import Agent
from core.crypto.hashing import blake2b_256
import json


class VerifierAgent(Agent):
    def verify_evidence(self, contract: dict, evidence: dict) -> dict:
        terms = contract.get("terms", {})
        checks = []
        all_passed = True

        if "max_tokens" in terms:
            actual = evidence.get("output", {}).get("tokens_used", 0)
            passed = actual <= terms["max_tokens"]
            checks.append({
                "check": "max_tokens",
                "expected": terms["max_tokens"],
                "actual": actual,
                "passed": passed,
            })
            all_passed &= passed

        if "timeout_sec" in terms:
            elapsed = (evidence.get("executed_at", 0) - contract.get("created_at", 0)) / 1000
            passed = elapsed <= terms["timeout_sec"]
            checks.append({
                "check": "timeout_sec",
                "expected": terms["timeout_sec"],
                "actual": elapsed,
                "passed": passed,
            })
            all_passed &= passed

        if "result_hash" in terms:
            passed = evidence.get("result_hash") == terms["result_hash"]
            checks.append({
                "check": "result_hash",
                "expected": terms["result_hash"],
                "actual": evidence.get("result_hash"),
                "passed": passed,
            })
            all_passed &= passed

        return {
            "verified": all_passed,
            "checks": checks,
            "verified_at": int(__import__("time").time() * 1000),
        }