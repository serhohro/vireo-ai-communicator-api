"""
Layer 3 — AI Protocol: Intent / Speech Acts
"""

from enum import Enum


class Intent(str, Enum):
    REQUEST = "request"
    PROPOSE = "propose"
    QUERY = "query"
    INFORM = "inform"
    REJECT = "reject"
    COMMIT = "commit"
    CANCEL = "cancel"
    NEGOTIATE = "negotiate"
    QUERY_CAPABILITIES = "query_capabilities"
    INFORM_CAPABILITIES = "inform_capabilities"


def parse_intent_line(line: str) -> dict:
    parts = line.strip().split()
    if not parts:
        raise ValueError("empty intent line")

    intent_str, *kv_parts = parts
    try:
        intent = Intent(intent_str)
    except ValueError:
        raise ValueError(f"unknown intent: {intent_str!r}")

    params = {}
    for kv in kv_parts:
        if "=" not in kv:
            raise ValueError(f"malformed argument: {kv!r}")
        key, value = kv.split("=", 1)
        params[key] = value

    return {"intent": intent, "params": params}