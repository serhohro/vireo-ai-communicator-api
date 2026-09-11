"""
Vireo API Routes v3.1 — full endpoint registration.
"""

from .server import (
    # UI
    home, web_interface, docs, api_docs, health,

    # Agents
    register_agent, list_agents, agent_status, add_capability,

    # Contracts
    propose_contract, execute_contract, verify_contract,

    # Wire
    send_message, protocol_version,

    # DID
    create_did, verify_did, get_did_doc,

    # Trust
    establish_trust, trust_challenge, trust_respond,

    # Providers
    list_providers,

    # LLM
    chat, auto_negotiate,

    # Crypto
    generate_keys, sign_message, verify_signature, test_trust,

    # Metrics
    metrics,
)


def register_routes(app):
    """Register all Vireo routes on the Flask app."""

    # UI
    app.add_url_rule("/", "home", home, methods=["GET"])
    app.add_url_rule("/web", "web_interface", web_interface, methods=["GET"])
    app.add_url_rule("/docs", "docs", docs, methods=["GET"])
    app.add_url_rule("/api/docs", "api_docs", api_docs, methods=["GET"])
    app.add_url_rule("/api/health", "health", health, methods=["GET"])

    # Agents
    app.add_url_rule("/api/v3/agent/register", "register_agent", register_agent, methods=["POST"])
    app.add_url_rule("/api/v3/agents", "list_agents", list_agents, methods=["GET"])
    app.add_url_rule("/api/v3/agent/<agent_id>/status", "agent_status", agent_status, methods=["GET"])
    app.add_url_rule("/api/v3/agent/<agent_id>/capability", "add_capability", add_capability, methods=["POST"])

    # Contracts
    app.add_url_rule("/api/v3/propose", "propose_contract", propose_contract, methods=["POST"])
    app.add_url_rule("/api/v3/execute", "execute_contract", execute_contract, methods=["POST"])
    app.add_url_rule("/api/v3/verify", "verify_contract", verify_contract, methods=["POST"])

    # Wire
    app.add_url_rule("/api/v3/message", "send_message", send_message, methods=["POST"])
    app.add_url_rule("/api/v3/protocol/version", "protocol_version", protocol_version, methods=["GET"])

    # DID
    app.add_url_rule("/api/v3/did/create", "create_did", create_did, methods=["POST"])
    app.add_url_rule("/api/v3/did/verify", "verify_did", verify_did, methods=["POST"])
    app.add_url_rule("/api/v3/did/<path:did>", "get_did_doc", get_did_doc, methods=["GET"])

    # Trust
    app.add_url_rule("/api/v3/trust/establish", "establish_trust", establish_trust, methods=["POST"])
    app.add_url_rule("/api/v3/trust/challenge", "trust_challenge", trust_challenge, methods=["POST"])
    app.add_url_rule("/api/v3/trust/respond", "trust_respond", trust_respond, methods=["POST"])

    # Providers
    app.add_url_rule("/api/providers", "list_providers", list_providers, methods=["GET"])

    # LLM
    app.add_url_rule("/api/chat", "chat", chat, methods=["POST"])
    app.add_url_rule("/api/llm/agent/<agent_id>/auto_negotiate", "auto_negotiate", auto_negotiate, methods=["POST"])

    # Crypto
    app.add_url_rule("/api/crypto/generate_keys", "generate_keys", generate_keys, methods=["POST"])
    app.add_url_rule("/api/crypto/sign", "sign_message", sign_message, methods=["POST"])
    app.add_url_rule("/api/crypto/verify", "verify_signature", verify_signature, methods=["POST"])
    app.add_url_rule("/api/crypto/test_trust", "test_trust", test_trust, methods=["POST"])

    # Metrics
    app.add_url_rule("/api/v3/metrics", "metrics", metrics, methods=["GET"])


__all__ = ["register_routes"]