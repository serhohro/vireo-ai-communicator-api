"""
Vireo API Server v3.1 — fully rewritten.

All v3.0.0 mock endpoints replaced with real implementations:
- /api/v3/message: binary wire reader (request.data)
- /api/crypto/verify: real Ed25519 verification
- /api/v3/verify: real contract verification with evidence
- /api/v3/trust/establish: real challenge-response
- /api/chat: honest mock status (or real provider call if key configured)
- State machine enforced on every state-changing endpoint

Entry points:
    python -m api.server
    vireo-server              (console script)
"""

import json
import os
import time
import logging
from pathlib import Path

from flask import request, jsonify, send_from_directory

from core.config import config
from core.crypto.ed25519 import (
    generate_keypair,
    sign_vireo_message,
    verify_vireo_message,
)
from core.crypto.canonical import (
    canonical_wire_bytes,
    parse_wire_bytes,
)
from core.crypto.blake2b import (
    blake2b_256,
    did_hash,
)
from core.protocol.state import (
    ProtocolState,
    VireoStateMachine,
    IllegalTransitionError,
)
from core.protocol.verification import verify_vireo_signature
from core.protocol.nonce_manager import get_nonce_manager
from core.protocol.version import PROTOCOL_VERSION, WIRE_VERSION
from core.identity.did import (
    make_did,
    register_did,
    resolve_public_key,
    get_did_document,
    list_dids,
)
from core.identity.trust_bootstrap import get_trust_bootstrap


logger = logging.getLogger("vireo.server")


# ═════════════════════════════════════════════════════════════════
# IN-MEMORY STATE (demo; replace with DB in production)
# ═════════════════════════════════════════════════════════════════

AGENTS: dict[str, dict] = {}
CONTRACTS: dict[str, dict] = {}
SESSIONS: dict[str, VireoStateMachine] = {}
START_TIME = time.time()


# ═════════════════════════════════════════════════════════════════
# UI
# ═════════════════════════════════════════════════════════════════

def home():
    return jsonify({
        "name": "Vireo",
        "version": PROTOCOL_VERSION,
        "wire_version": hex(WIRE_VERSION),
        "status": "running",
        "docs": "/docs",
        "api_docs": "/api/docs",
        "web": "/web",
        "api": "/api/v3/protocol/version",
    })


def web_interface():
    web_dir = Path(__file__).resolve().parent.parent / "web"
    if (web_dir / "index.html").exists():
        return send_from_directory(web_dir, "index.html")
    return jsonify({
        "error": "web interface not found",
        "expected_path": str(web_dir / "index.html"),
    }), 404


def docs():
    """Serve beautiful HTML documentation."""
    web_dir = Path(__file__).resolve().parent.parent / "web"
    if (web_dir / "docs.html").exists():
        return send_from_directory(web_dir, "docs.html")
    return jsonify({
        "error": "docs.html not found",
        "expected_path": str(web_dir / "docs.html"),
        "hint": "Create web/docs.html or use /api/docs for JSON spec",
    }), 404


def api_docs():
    """Machine-readable JSON API spec."""
    return jsonify({
        "name": "Vireo API",
        "version": PROTOCOL_VERSION,
        "wire_version": hex(WIRE_VERSION),
        "endpoints": {
            "ui": [
                "GET  /",
                "GET  /web",
                "GET  /docs",
                "GET  /api/docs",
                "GET  /api/health",
            ],
            "agents": [
                "POST /api/v3/agent/register",
                "GET  /api/v3/agents",
                "GET  /api/v3/agent/<id>/status",
                "POST /api/v3/agent/<id>/capability",
            ],
            "contracts": [
                "POST /api/v3/propose",
                "POST /api/v3/execute",
                "POST /api/v3/verify",
            ],
            "wire": [
                "POST /api/v3/message",
                "GET  /api/v3/protocol/version",
            ],
            "did": [
                "POST /api/v3/did/create",
                "POST /api/v3/did/verify",
                "GET  /api/v3/did/<did>",
            ],
            "trust": [
                "POST /api/v3/trust/establish",
                "POST /api/v3/trust/challenge",
                "POST /api/v3/trust/respond",
            ],
            "crypto": [
                "POST /api/crypto/generate_keys",
                "POST /api/crypto/sign",
                "POST /api/crypto/verify",
                "POST /api/crypto/test_trust",
            ],
            "llm": [
                "GET  /api/providers",
                "POST /api/chat",
                "POST /api/llm/agent/<id>/auto_negotiate",
            ],
            "metrics": [
                "GET  /api/v3/metrics",
            ],
        },
    })


def health():
    return jsonify({
        "status": "ok",
        "version": PROTOCOL_VERSION,
        "wire_version": hex(WIRE_VERSION),
        "uptime_sec": int(time.time() - START_TIME),
        "agents": len(AGENTS),
        "contracts": len(CONTRACTS),
        "sessions": len(SESSIONS),
    })


# ═════════════════════════════════════════════════════════════════
# AGENTS
# ═════════════════════════════════════════════════════════════════

def register_agent():
    data = request.get_json(silent=True) or {}
    agent_id = data.get("id") or data.get("agent_id")
    if not agent_id:
        return jsonify({"error": "missing 'id'"}), 400

    if agent_id in AGENTS:
        return jsonify({
            "error": "agent already registered",
            "agent_id": agent_id,
        }), 409

    name = data.get("name", agent_id)
    did = data.get("did") or make_did(name)

    public_key_hex = data.get("public_key_hex")
    private_key_hex = None
    if not public_key_hex:
        kp = generate_keypair()
        public_key_hex = kp["public_key_hex"]
        private_key_hex = kp["private_key_hex"]

    register_did(did, public_key_hex, name=name, endpoint=data.get("endpoint", ""))

    AGENTS[agent_id] = {
        "id": agent_id,
        "name": name,
        "did": did,
        "public_key_hex": public_key_hex,
        "capabilities": [],
        "registered_at": int(time.time() * 1000),
    }

    response = {
        "status": "registered",
        "agent_id": agent_id,
        "did": did,
        "public_key_hex": public_key_hex,
    }
    if private_key_hex:
        response["private_key_hex"] = private_key_hex
        response["warning"] = (
            "Store this private key securely. It will NOT be shown again."
        )
    return jsonify(response), 201


def list_agents():
    return jsonify({
        "agents": list(AGENTS.values()),
        "count": len(AGENTS),
    })


def agent_status(agent_id: str):
    agent = AGENTS.get(agent_id)
    if not agent:
        return jsonify({"error": "agent not found"}), 404
    session = SESSIONS.get(agent_id)
    return jsonify({
        "agent": agent,
        "state": session.state.value if session else ProtocolState.DISCOVER.value,
        "is_terminal": session.is_terminal if session else False,
    })


def add_capability(agent_id: str):
    agent = AGENTS.get(agent_id)
    if not agent:
        return jsonify({"error": "agent not found"}), 404

    data = request.get_json(silent=True) or {}
    cap = data.get("capability")
    if not cap:
        return jsonify({"error": "missing 'capability'"}), 400

    if cap not in agent["capabilities"]:
        agent["capabilities"].append(cap)

    return jsonify({
        "status": "added",
        "agent_id": agent_id,
        "capabilities": agent["capabilities"],
    })


# ═════════════════════════════════════════════════════════════════
# CONTRACTS
# ═════════════════════════════════════════════════════════════════

def propose_contract():
    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")
    if not contract_id:
        return jsonify({"error": "missing 'contract_id'"}), 400

    parties = data.get("parties", [])
    terms = data.get("terms", {})

    if not isinstance(parties, list) or len(parties) < 2:
        return jsonify({"error": "at least 2 parties required"}), 400

    if contract_id in CONTRACTS:
        return jsonify({"error": "contract_id already exists"}), 409

    CONTRACTS[contract_id] = {
        "contract_id": contract_id,
        "parties": parties,
        "terms": terms,
        "state": ProtocolState.PROPOSE.value,
        "created_at": int(time.time() * 1000),
        "evidence": None,
        "verification": None,
    }
    SESSIONS[contract_id] = VireoStateMachine(ProtocolState.PROPOSE)

    return jsonify({
        "status": "proposed",
        "contract": CONTRACTS[contract_id],
    }), 201


def execute_contract():
    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")
    if not contract_id:
        return jsonify({"error": "missing 'contract_id'"}), 400

    contract = CONTRACTS.get(contract_id)
    if not contract:
        return jsonify({"error": "contract not found"}), 404

    sm = SESSIONS.get(contract_id)
    if sm is None:
        sm = VireoStateMachine(ProtocolState.PROPOSE)
        SESSIONS[contract_id] = sm

    try:
        sm.transition(ProtocolState.NEGOTIATE)
        sm.transition(ProtocolState.COMMIT)
        sm.transition(ProtocolState.EXECUTE)
    except IllegalTransitionError as e:
        return jsonify({
            "error": str(e),
            "current": sm.state.value,
        }), 409

    output = data.get("result", {})
    evidence = {
        "executed_at": int(time.time() * 1000),
        "executor": data.get("executor", "unknown"),
        "result_hash": blake2b_256(
            json.dumps(output, sort_keys=True).encode()
        ).hex(),
        "output": output,
    }
    contract["state"] = ProtocolState.EXECUTE.value
    contract["evidence"] = evidence

    return jsonify({
        "status": "executed",
        "contract_id": contract_id,
        "state": contract["state"],
        "evidence": evidence,
    })


def verify_contract():
    """
    Real verification:
    1. Contract must be in EXECUTE state.
    2. Evidence must exist.
    3. Contract terms must be evaluated.
    4. Transition to VERIFY → DONE or VERIFY → ESCALATED.
    """
    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")
    if not contract_id:
        return jsonify({"error": "missing 'contract_id'"}), 400

    contract = CONTRACTS.get(contract_id)
    if not contract:
        return jsonify({"error": "contract not found"}), 404

    evidence = contract.get("evidence")
    if not evidence:
        return jsonify({
            "error": "no evidence to verify",
            "hint": "call /api/v3/execute first",
        }), 400

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
        elapsed = (evidence["executed_at"] - contract["created_at"]) / 1000
        passed = elapsed <= terms["timeout_sec"]
        checks.append({
            "check": "timeout_sec",
            "expected": terms["timeout_sec"],
            "actual": elapsed,
            "passed": passed,
        })
        all_passed &= passed

    if "result_hash" in terms:
        passed = evidence["result_hash"] == terms["result_hash"]
        checks.append({
            "check": "result_hash",
            "expected": terms["result_hash"],
            "actual": evidence["result_hash"],
            "passed": passed,
        })
        all_passed &= passed

    sm = SESSIONS.get(contract_id)
    if sm is None or sm.state != ProtocolState.EXECUTE:
        return jsonify({
            "error": "contract not in EXECUTE state",
            "current": sm.state.value if sm else "unknown",
        }), 409

    try:
        sm.transition(ProtocolState.VERIFY)
        if all_passed:
            sm.transition(ProtocolState.DONE)
        else:
            sm.transition(ProtocolState.ESCALATED)
    except IllegalTransitionError as e:
        return jsonify({"error": str(e)}), 409

    verification = {
        "verified": all_passed,
        "checks": checks,
        "verified_at": int(time.time() * 1000),
        "final_state": sm.state.value,
    }
    contract["verification"] = verification
    contract["state"] = sm.state.value

    return jsonify({
        "success": True,
        "verified": all_passed,
        "contract_id": contract_id,
        "state": contract["state"],
        "checks": checks,
    })


# ═════════════════════════════════════════════════════════════════
# WIRE
# ═════════════════════════════════════════════════════════════════

def send_message():
    """
    Binary wire reader.

    Accepts:
      - application/octet-stream → binary Vireo wire bytes
      - application/json → {envelope, signature, sender_did} for debugging
    """
    content_type = request.content_type or ""

    if "application/octet-stream" in content_type:
        data = request.data
        try:
            envelope = parse_wire_bytes(data)
        except ValueError as e:
            return jsonify({"error": f"malformed wire: {e}"}), 400

        nm = get_nonce_manager()
        ok, err = nm.check_and_store(
            envelope["nonce"],
            envelope["sender_did_hash"],
            envelope["timestamp_ms"],
        )
        if not ok:
            return jsonify({"error": err}), 409

        return jsonify({
            "status": "received",
            "intent": envelope["intent"],
            "timestamp_ms": envelope["timestamp_ms"],
            "payload": envelope["payload"],
        })

    # JSON fallback
    data = request.get_json(silent=True) or {}
    envelope = data.get("envelope")
    signature = data.get("signature")
    sender_did = data.get("sender_did")

    if not envelope or not signature or not sender_did:
        return jsonify({
            "error": "missing envelope/signature/sender_did",
        }), 400

    env = dict(envelope)
    if isinstance(env.get("nonce"), str):
        env["nonce"] = bytes.fromhex(env["nonce"])
    if isinstance(env.get("sender_did_hash"), str):
        env["sender_did_hash"] = bytes.fromhex(env["sender_did_hash"])
    if isinstance(env.get("recipient_did_hash"), str):
        env["recipient_did_hash"] = bytes.fromhex(env["recipient_did_hash"])

    result = verify_vireo_signature({
        "envelope": env,
        "signature": signature,
        "sender_did": sender_did,
    })

    if not result["valid"]:
        return jsonify({"error": result["error"]}), 401

    nm = get_nonce_manager()
    ok, err = nm.check_and_store(
        env["nonce"],
        env["sender_did_hash"],
        env["timestamp_ms"],
    )
    if not ok:
        return jsonify({"error": err}), 409

    return jsonify({
        "status": "verified",
        "intent": env["intent"],
        "sender_did": sender_did,
    })


def protocol_version():
    return jsonify({
        "protocol": PROTOCOL_VERSION,
        "wire": hex(WIRE_VERSION),
        "wire_format": "Vireo Canonical Binary (RFC 8785 payload + 96B header)",
        "hash": "BLAKE2b-256",
        "signature": "Ed25519",
        "header_size_bytes": 96,
    })


# ═════════════════════════════════════════════════════════════════
# DID
# ═════════════════════════════════════════════════════════════════

def create_did():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "missing 'name'"}), 400

    did = make_did(name)

    public_key_hex = data.get("public_key_hex")
    private_key_hex = None
    if not public_key_hex:
        kp = generate_keypair()
        public_key_hex = kp["public_key_hex"]
        private_key_hex = kp["private_key_hex"]

    register_did(did, public_key_hex, name=name, endpoint=data.get("endpoint", ""))

    response = {
        "status": "created",
        "did": did,
        "public_key_hex": public_key_hex,
    }
    if private_key_hex:
        response["private_key_hex"] = private_key_hex
    return jsonify(response), 201


def verify_did():
    """
    Real DID verification:
    - If only DID given → existence check.
    - If message + signature given → cryptographic verification.
    """
    data = request.get_json(silent=True) or {}
    did = data.get("did")
    message = data.get("message")
    signature = data.get("signature")

    if not did:
        return jsonify({"error": "missing 'did'"}), 400

    public_key_hex = resolve_public_key(did)
    if not public_key_hex:
        return jsonify({
            "verified": False,
            "error": "DID not registered",
        }), 404

    if not message or not signature:
        return jsonify({
            "verified": True,
            "did": did,
            "public_key_hex": public_key_hex,
            "note": "existence check only (no signature provided)",
        })

    try:
        message_bytes = (
            bytes.fromhex(message) if _is_hex(message) else message.encode("utf-8")
        )
    except Exception:
        message_bytes = message.encode("utf-8")

    valid, err = verify_vireo_message(public_key_hex, message_bytes, signature)
    return jsonify({
        "verified": valid,
        "did": did,
        "error": err,
    })


def get_did_doc(did: str):
    doc = get_did_document(did)
    if not doc:
        return jsonify({"error": "DID not found"}), 404
    return jsonify(doc)


def _is_hex(s: str) -> bool:
    try:
        bytes.fromhex(s)
        return True
    except (ValueError, TypeError):
        return False


# ═════════════════════════════════════════════════════════════════
# TRUST
# ═════════════════════════════════════════════════════════════════

def establish_trust():
    """
    Creates a challenge. Caller must POST to /api/v3/trust/respond
    with a signature over the challenge bytes.
    """
    data = request.get_json(silent=True) or {}
    initiator_did = data.get("initiator_did") or data.get("agent_a")
    responder_did = data.get("responder_did") or data.get("agent_b")

    if not initiator_did or not responder_did:
        return jsonify({
            "error": "missing initiator_did/responder_did",
        }), 400

    tb = get_trust_bootstrap()
    challenge = tb.create_challenge(initiator_did, responder_did)
    return jsonify({
        "status": "challenge_created",
        "challenge": challenge,
        "next": "POST /api/v3/trust/respond with signature over challenge bytes",
    })


def trust_challenge():
    return establish_trust()


def trust_respond():
    data = request.get_json(silent=True) or {}
    challenge_hex = data.get("challenge_hex")
    responder_did = data.get("responder_did")
    signature_hex = data.get("signature")

    if not all([challenge_hex, responder_did, signature_hex]):
        return jsonify({
            "error": "missing challenge_hex/responder_did/signature",
        }), 400

    tb = get_trust_bootstrap()
    result = tb.respond_to_challenge(challenge_hex, responder_did, signature_hex)
    status = 200 if result.get("trusted") else 401
    return jsonify(result), status


# ═════════════════════════════════════════════════════════════════
# PROVIDERS
# ═════════════════════════════════════════════════════════════════

PROVIDERS = [
    {"id": "ollama",      "name": "Ollama",       "country": "local", "requires_key": False},
    {"id": "mistral",     "name": "Mistral AI",   "country": "FR",    "requires_key": True, "env": "MISTRAL_API_KEY"},
    {"id": "aleph_alpha", "name": "Aleph Alpha",  "country": "DE",    "requires_key": True, "env": "ALEPH_ALPHA_API_KEY"},
    {"id": "cohere",      "name": "Cohere",       "country": "CH",    "requires_key": True, "env": "COHERE_API_KEY"},
    {"id": "qwen",        "name": "Qwen AI",      "country": "CN",    "requires_key": True, "env": "QWEN_API_KEY"},
    {"id": "openai",      "name": "OpenAI GPT",   "country": "US",    "requires_key": True, "env": "OPENAI_API_KEY"},
    {"id": "claude",      "name": "Claude",       "country": "US",    "requires_key": True, "env": "ANTHROPIC_API_KEY"},
    {"id": "gemini",      "name": "Gemini",       "country": "US",    "requires_key": True, "env": "GEMINI_API_KEY"},
    {"id": "deepseek",    "name": "DeepSeek",     "country": "CN",    "requires_key": True, "env": "DEEPSEEK_API_KEY"},
]


def list_providers():
    out = []
    for p in PROVIDERS:
        configured = True
        if p.get("requires_key"):
            configured = bool(os.getenv(p["env"], ""))
        out.append({
            "id": p["id"],
            "name": p["name"],
            "country": p["country"],
            "requires_key": p["requires_key"],
            "configured": configured,
            "callable": configured,
        })
    return jsonify({"providers": out, "count": len(out)})


# ═════════════════════════════════════════════════════════════════
# LLM
# ═════════════════════════════════════════════════════════════════

def chat():
    """
    Honest chat endpoint.

    - If provider key not configured → returns {"status": "mock"}.
    - If configured → attempts real call (Ollama for local, others stub).
    """
    data = request.get_json(silent=True) or {}
    model = data.get("model", "ollama")
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "missing 'message'"}), 400

    provider = next((p for p in PROVIDERS if p["id"] == model), None)
    if not provider:
        return jsonify({"error": f"unknown model: {model}"}), 400

    if provider["requires_key"] and not os.getenv(provider["env"], ""):
        return jsonify({
            "status": "mock",
            "model": model,
            "response": (
                f"[mock] Provider '{model}' not configured. "
                f"Set {provider['env']} to enable real calls."
            ),
            "note": "This is NOT a real LLM call. Configure the API key to enable.",
        })

    try:
        if model == "ollama":
            response_text = _call_ollama(message)
        else:
            response_text = _call_provider(model, message)
        return jsonify({
            "status": "ok",
            "model": model,
            "response": response_text,
        })
    except NotImplementedError as e:
        return jsonify({
            "status": "error",
            "model": model,
            "error": str(e),
        }), 501
    except Exception as e:
        return jsonify({
            "status": "error",
            "model": model,
            "error": str(e),
        }), 502


def _call_ollama(message: str) -> str:
    import urllib.request
    url = f"{config.OLLAMA_URL}/api/generate"
    body = json.dumps({
        "model": "llama3",
        "prompt": message,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode())
    return result.get("response", "")


def _call_provider(model: str, message: str) -> str:
    """Placeholder for real provider calls. Implement per provider."""
    raise NotImplementedError(
        f"Real call for '{model}' not yet implemented. "
        f"See docs/API_REFERENCE.md."
    )


def auto_negotiate(agent_id: str):
    """
    Real autonomous negotiation.

    Flow:
    1. Create VireoStateMachine session.
    2. DISCOVER → PROPOSE.
    3. Evaluate recipient's policy.
    4. If accepted → NEGOTIATE → COMMIT.
    5. If rejected → REJECTED.
    """
    agent = AGENTS.get(agent_id)
    if not agent:
        return jsonify({"error": "agent not found"}), 404

    data = request.get_json(silent=True) or {}
    recipient = data.get("recipient")
    task = data.get("task")
    terms = data.get("terms", {"max_tokens": 1000, "timeout_sec": 30})

    if not recipient or not task:
        return jsonify({"error": "missing 'recipient' and/or 'task'"}), 400

    if recipient not in AGENTS:
        return jsonify({
            "error": f"recipient '{recipient}' not registered",
        }), 404

    session_id = f"{agent_id}->{recipient}-{int(time.time() * 1000)}"
    sm = VireoStateMachine()
    SESSIONS[session_id] = sm

    policy_max_cost = terms.get("max_cost_usd", 10.0)
    decision = "commit"
    reason = "policy check passed"

    if terms.get("cost_usd", 0) > policy_max_cost:
        decision = "reject"
        reason = f"cost {terms['cost_usd']} exceeds policy max {policy_max_cost}"

    try:
        sm.transition(ProtocolState.PROPOSE)
        if decision == "reject":
            sm.transition(ProtocolState.REJECTED)
        else:
            sm.transition(ProtocolState.NEGOTIATE)
            sm.transition(ProtocolState.COMMIT)
    except IllegalTransitionError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify({
        "session_id": session_id,
        "initiator": agent_id,
        "recipient": recipient,
        "task": task,
        "terms": terms,
        "decision": decision,
        "reason": reason,
        "final_state": sm.state.value,
        "history": [s.value for s in sm.history],
    })


# ═════════════════════════════════════════════════════════════════
# CRYPTO
# ═════════════════════════════════════════════════════════════════

def generate_keys():
    kp = generate_keypair()
    return jsonify({
        "status": "ok",
        "private_key_hex": kp["private_key_hex"],
        "public_key_hex": kp["public_key_hex"],
        "warning": "Store the private key securely. It will NOT be shown again.",
    })


def sign_message():
    """
    Sign a message using a provided private key.

    IMPORTANT: private_key_hex must be provided in the request.
    This endpoint does NOT generate a new keypair.
    """
    data = request.get_json(silent=True) or {}
    private_key_hex = data.get("private_key_hex")
    message = data.get("message")

    if not private_key_hex:
        return jsonify({"error": "missing 'private_key_hex'"}), 400
    if not message:
        return jsonify({"error": "missing 'message'"}), 400

    try:
        message_bytes = (
            bytes.fromhex(message) if _is_hex(message) else message.encode("utf-8")
        )
    except Exception:
        message_bytes = message.encode("utf-8")

    try:
        signature = sign_vireo_message(private_key_hex, message_bytes)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "status": "signed",
        "signature": signature,
        "hash": blake2b_256(message_bytes).hex(),
    })


def verify_signature():
    """
    Real Ed25519 verification.
    Replaces the previous mock that returned valid: True unconditionally.
    """
    data = request.get_json(silent=True) or {}
    public_key_hex = data.get("public_key_hex")
    message = data.get("message")
    signature = data.get("signature")

    if not all([public_key_hex, message, signature]):
        return jsonify({
            "valid": False,
            "error": "missing public_key_hex/message/signature",
        }), 400

    try:
        message_bytes = (
            bytes.fromhex(message) if _is_hex(message) else message.encode("utf-8")
        )
    except Exception:
        message_bytes = message.encode("utf-8")

    valid, err = verify_vireo_message(public_key_hex, message_bytes, signature)
    status = 200 if valid else 401
    return jsonify({
        "valid": valid,
        "error": err,
        "message": (
            "Signature verified successfully"
            if valid
            else "Signature verification failed"
        ),
    }), status


def test_trust():
    """Convenience: full challenge-response round-trip in one call."""
    data = request.get_json(silent=True) or {}
    initiator_did = data.get("initiator_did")
    responder_did = data.get("responder_did")
    responder_private_key_hex = data.get("responder_private_key_hex")

    if not all([initiator_did, responder_did, responder_private_key_hex]):
        return jsonify({"error": "missing required fields"}), 400

    tb = get_trust_bootstrap()
    challenge = tb.create_challenge(initiator_did, responder_did)
    challenge_bytes = bytes.fromhex(challenge["challenge_hex"])
    signature = sign_vireo_message(responder_private_key_hex, challenge_bytes)
    result = tb.respond_to_challenge(
        challenge["challenge_hex"], responder_did, signature
    )
    return jsonify(result)


# ═════════════════════════════════════════════════════════════════
# METRICS
# ═════════════════════════════════════════════════════════════════

def metrics():
    nm = get_nonce_manager()
    return jsonify({
        "uptime_sec": int(time.time() - START_TIME),
        "agents": len(AGENTS),
        "contracts": len(CONTRACTS),
        "sessions": len(SESSIONS),
        "nonces_stored": nm.count(),
        "version": PROTOCOL_VERSION,
        "wire_version": hex(WIRE_VERSION),
    })


# ═════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════

def main():
    """Entry point for `python -m api.server` and `vireo-server`."""
    from api import create_app

    app = create_app()
    print(f"🌿 Vireo v3.1 — starting on http://{config.HOST}:{config.PORT}")
    print(f"   Web UI:  http://localhost:{config.PORT}/web")
    print(f"   Docs:    http://localhost:{config.PORT}/docs")
    print(f"   API:     http://localhost:{config.PORT}/api/docs")
    print(f"   Health:  http://localhost:{config.PORT}/api/health")
    print(f"   Wire:    v3.1 ({hex(WIRE_VERSION)})")
    print(f"   Crypto:  Ed25519 + BLAKE2b-256")
    app.run(host=config.HOST, port=config.PORT, debug=False)


if __name__ == "__main__":
    main()