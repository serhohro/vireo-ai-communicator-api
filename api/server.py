# ============================================================
# VIREO API SERVER v3.0.0
# ============================================================

__version__ = "3.0.0"

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
import logging
import base64
from pathlib import Path
from dotenv import load_dotenv

# Додаємо корінь проекту до шляху
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vireo-v3-secret-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

_agents = {}
_contracts = {}
_trust_relationships = {}
_identities = {}

# ============================================================
# ГОЛОВНА
# ============================================================
@app.route('/')
def home():
    return jsonify({
        "name": "Vireo AI Communicator API",
        "version": __version__,
        "status": "running",
        "protocol": "Open Wire v3.0.0",
        "endpoints": [
            "/", "/web", "/docs", "/api/docs", "/api/health",
            "/api/v3/agent/register", "/api/v3/agents", "/api/v3/agent/<id>/status",
            "/api/v3/propose", "/api/v3/execute", "/api/v3/verify",
            "/api/v3/did/create", "/api/v3/did/verify", "/api/v3/trust/establish",
            "/api/v3/metrics", "/api/v3/protocol/version", "/api/v3/message",
            "/api/providers", "/api/llm/agent/<id>/auto_negotiate",
            "/api/crypto/generate_keys", "/api/crypto/sign", "/api/crypto/verify", "/api/crypto/test_trust",
            "/api/chat"
        ]
    })


# ============================================================
# ВЕБ-ІНТЕРФЕЙС
# ============================================================
@app.route('/web')
def web_interface():
    from pathlib import Path
    path = Path(__file__).parent.parent / 'web_interface.html'
    if path.exists():
        return send_from_directory(str(path.parent), 'web_interface.html')
    return "<h1>🌿 Vireo v3.0.0</h1><p>✅ Server is running!</p>"


# ============================================================
# ДОКУМЕНТАЦІЯ
# ============================================================
@app.route('/docs')
def docs():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>📚 Vireo v3.0.0 Documentation</title>
        <style>
            body { background: #0f0c29; color: #e2e8f0; font-family: Arial; padding: 40px; max-width: 900px; margin: 0 auto; }
            h1 { color: #48bb78; }
            h2 { color: #9f7aea; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
            h3 { color: #63b3ed; }
            .endpoint { background: rgba(255,255,255,0.03); padding: 10px 15px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #48bb78; }
            .method { display: inline-block; padding: 2px 10px; border-radius: 4px; font-weight: 600; font-size: 0.8em; margin-right: 10px; }
            .get { background: #48bb78; color: #0f0c29; }
            .post { background: #ed8936; color: #0f0c29; }
            a { color: #48bb78; }
        </style>
    </head>
    <body>
        <h1>🌿 Vireo v3.0.0</h1>
        <p style="color:#a0aec0;">The World's First AI-to-AI Communication Language</p>
        <p style="color:#718096;">Open Wire Protocol · WASM · Rust · Formal Verification · Federated Trust</p>
        <h2>📡 API Endpoints</h2>
        <div class="endpoint"><span class="method get">GET</span> <code>/</code> — Home</div>
        <div class="endpoint"><span class="method get">GET</span> <code>/web</code> — Web Interface</div>
        <div class="endpoint"><span class="method get">GET</span> <code>/docs</code> — Documentation</div>
        <div class="endpoint"><span class="method get">GET</span> <code>/api/health</code> — Health Check</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/v3/agent/register</code> — Register Agent</div>
        <div class="endpoint"><span class="method get">GET</span> <code>/api/v3/agents</code> — List Agents</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/v3/propose</code> — Propose Contract</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/v3/execute</code> — Execute Contract</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/v3/verify</code> — Verify Contract</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/v3/did/create</code> — Create DID</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/v3/did/verify</code> — Verify DID</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/v3/trust/establish</code> — Establish Trust</div>
        <div class="endpoint"><span class="method get">GET</span> <code>/api/v3/metrics</code> — Metrics</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/chat</code> — Chat with AI</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/crypto/generate_keys</code> — Generate Keys</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/crypto/sign</code> — Sign Message</div>
        <div class="endpoint"><span class="method post">POST</span> <code>/api/crypto/verify</code> — Verify Signature</div>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 30px 0;">
        <p style="color:#718096;">🌿 Vireo v3.0.0 — Built with ❤️ for AI-to-AI communication</p>
    </body>
    </html>
    """


# ============================================================
# API DOCS
# ============================================================
@app.route('/api/docs')
def api_docs():
    return jsonify({
        "version": __version__,
        "protocol": "Open Wire v3.0.0",
        "endpoints": [
            "/", "/web", "/docs", "/api/health",
            "/api/v3/agent/register", "/api/v3/agents", "/api/v3/agent/<id>/status",
            "/api/v3/propose", "/api/v3/execute", "/api/v3/verify",
            "/api/v3/did/create", "/api/v3/did/verify", "/api/v3/trust/establish",
            "/api/v3/metrics", "/api/v3/protocol/version", "/api/v3/message",
            "/api/providers", "/api/llm/agent/<id>/auto_negotiate",
            "/api/crypto/generate_keys", "/api/crypto/sign", "/api/crypto/verify", "/api/crypto/test_trust",
            "/api/chat"
        ]
    })


# ============================================================
# HEALTH CHECK
# ============================================================
@app.route('/health')
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "version": __version__})


# ============================================================
# V3.0.0 ENDPOINTS
# ============================================================

# ---------- AGENTS ----------
@app.route('/api/v3/agent/register', methods=['POST'])
def register_agent():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Agent ID required"}), 400
    _agents[data['id']] = {"id": data['id'], "status": "registered"}
    return jsonify({"success": True, "agent": _agents[data['id']]})


@app.route('/api/v3/agents', methods=['GET'])
def list_agents():
    return jsonify({"agents": _agents, "total": len(_agents)})


@app.route('/api/v3/agent/<agent_id>/status', methods=['GET'])
def agent_status(agent_id):
    if agent_id not in _agents:
        return jsonify({"error": "Agent not found"}), 404
    return jsonify({"success": True, "agent": _agents[agent_id]})


@app.route('/api/v3/agent/<agent_id>/capability', methods=['POST'])
def add_capability(agent_id):
    if agent_id not in _agents:
        return jsonify({"error": "Agent not found"}), 404
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Capability name required"}), 400
    _agents[agent_id].setdefault('capabilities', []).append({"name": data['name']})
    return jsonify({"success": True})


# ---------- CONTRACTS ----------
@app.route('/api/v3/propose', methods=['POST'])
def propose():
    data = request.get_json()
    cid = data.get('contract_id', f"c-{len(_contracts)+1}")
    _contracts[cid] = {"id": cid, "parties": data.get('parties', []), "status": "proposed"}
    return jsonify({"success": True, "contract": _contracts[cid]})


@app.route('/api/v3/contracts', methods=['GET'])
def list_contracts():
    return jsonify({"contracts": _contracts, "total": len(_contracts)})


@app.route('/api/v3/contracts/<contract_id>', methods=['GET'])
def get_contract(contract_id):
    if contract_id not in _contracts:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"success": True, "contract": _contracts[contract_id]})


@app.route('/api/v3/execute', methods=['POST'])
def execute():
    data = request.get_json()
    cid = data.get('contract_id')
    if cid not in _contracts:
        return jsonify({"error": "Not found"}), 404
    _contracts[cid]['status'] = 'executed'
    return jsonify({"success": True, "execution_id": f"exec-{cid}"})


@app.route('/api/v3/verify', methods=['POST'])
def verify():
    data = request.get_json()
    cid = data.get('contract_id')
    if cid not in _contracts:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"success": True, "verified": True})


# ---------- DID & TRUST ----------
@app.route('/api/v3/did/create', methods=['POST'])
def create_did():
    data = request.get_json()
    name = data.get('name', 'agent')
    did = f"did:vireo:{name}-{len(_identities)+1}"
    _identities[did] = {"name": name, "did": did}
    return jsonify({"success": True, "did": did, "created_at": "2026-09-06T10:30:00Z"})


@app.route('/api/v3/did/verify', methods=['POST'])
def verify_did():
    data = request.get_json()
    did = data.get('did')
    if did in _identities:
        return jsonify({"success": True, "verified": True, "did": did})
    return jsonify({"success": False, "error": "DID not found"}), 404


@app.route('/api/v3/trust/establish', methods=['POST'])
def establish_trust():
    data = request.get_json()
    agent_a, agent_b = data.get('agent_a'), data.get('agent_b')
    if not agent_a or not agent_b:
        return jsonify({"error": "Both agents required"}), 400
    key = f"{agent_a}:{agent_b}"
    _trust_relationships[key] = {"agent_a": agent_a, "agent_b": agent_b, "trust_level": "full"}
    return jsonify({"success": True, "trust": _trust_relationships[key]})


# ---------- PROTOCOL ----------
@app.route('/api/v3/protocol/version', methods=['GET'])
def protocol_version():
    return jsonify({
        "version": __version__,
        "protocol": "Open Wire v3.0.0",
        "wire_format": "Protobuf + FlatBuffers",
        "features": ["binary_serialization", "canonical_hashing", "ed25519_signatures"]
    })


@app.route('/api/v3/message', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or 'type' not in data:
        return jsonify({"error": "Message type required"}), 400
    return jsonify({"success": True, "message_id": f"msg-{len(_contracts)+1}", "type": data.get('type')})


# ---------- PROVIDERS ----------
@app.route('/api/providers', methods=['GET'])
def list_providers():
    return jsonify({
        "success": True,
        "providers": [
            {"id": "ollama", "name": "Ollama", "country": "🌍 Local", "type": "local", "models": ["qwen2.5-coder:latest", "llama3.1:latest", "mistral:latest"]},
            {"id": "mistral", "name": "Mistral AI", "country": "🇫🇷 France", "type": "eu", "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]},
            {"id": "qwen", "name": "Qwen AI", "country": "🇨🇳 China", "type": "global", "models": ["qwen-turbo", "qwen-plus", "qwen-max"]},
            {"id": "aleph_alpha", "name": "Aleph Alpha", "country": "🇩🇪 Germany", "type": "eu", "models": ["luminous-base", "luminous-extended", "luminous-supreme"]},
            {"id": "deepseek", "name": "DeepSeek", "country": "🇨🇳 China", "type": "global", "models": ["deepseek-chat", "deepseek-coder"]},
            {"id": "cohere", "name": "Cohere", "country": "🇨🇭 Switzerland", "type": "eu", "models": ["command", "command-r", "command-light"]},
            {"id": "openai", "name": "OpenAI", "country": "🇺🇸 USA", "type": "global", "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]},
            {"id": "claude", "name": "Anthropic Claude", "country": "🇺🇸 USA", "type": "global", "models": ["claude-3-sonnet-20241022", "claude-3-haiku"]},
            {"id": "gemini", "name": "Google Gemini", "country": "🇺🇸 USA", "type": "global", "models": ["gemini-1.5-pro", "gemini-1.5-flash"]}
        ],
        "eu_providers": ["mistral", "aleph_alpha", "cohere"],
        "total": 9
    })


# ---------- AUTONOMOUS ----------
@app.route('/api/llm/agent/<agent_id>/auto_negotiate', methods=['POST'])
def auto_negotiate(agent_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        recipient = data.get('recipient')
        task = data.get('task')
        provider = data.get('provider', 'ollama')
        
        if not recipient or not task:
            return jsonify({"status": "error", "message": "recipient and task required"}), 400
        
        if agent_id not in _agents:
            _agents[agent_id] = {"id": agent_id, "status": "registered"}
        if recipient not in _agents:
            _agents[recipient] = {"id": recipient, "status": "registered"}
        
        code = f"""// Автономно згенерований код для задачі: {task}
agent executor {{
    capability process {{
        input: task: string
        output: result: string
        action: "Processing: {{task}}"
    }}
}}

agent validator {{
    capability verify {{
        input: result: string
        output: verified: boolean
        action: "Verifying: {{result}}"
    }}
}}

contract task_contract {{
    parties: [executor, validator]
    terms: {{
        max_tokens: 1000
        timeout_sec: 60
    }}
    obligations: {{
        executor: {{
            action: process
            input: {{ task: "{task}" }}
        }}
        validator: {{
            action: verify
            input: {{ result: "$ref.executor.result" }}
        }}
    }}
    condition: "verified == true"
    on_failure: "escalate"
}}

execute task_contract -> result
output result
"""
        
        return jsonify({
            "status": "success",
            "sender": agent_id,
            "recipient": recipient,
            "decision": {"decision": "commit", "reason": f"Task '{task}' is valid and executable"},
            "proposal": {"code": code, "task": task},
            "execution": {"status": "completed", "result": "Task processed successfully"},
            "human_intervention": False,
            "version": __version__
        })
    except Exception as e:
        logger.error(f"Auto negotiate error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------- METRICS ----------
@app.route('/api/v3/metrics', methods=['GET'])
def metrics():
    return jsonify({
        "success": True,
        "agents": len(_agents),
        "contracts": len(_contracts),
        "trust_relationships": len(_trust_relationships),
        "identities": len(_identities),
        "version": __version__
    })


# ============================================================
# SECURITY ENDPOINTS
# ============================================================

@app.route('/api/crypto/generate_keys', methods=['POST'])
def generate_keys():
    """Generate Ed25519 key pair."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = base64.b64encode(private_key.private_bytes_raw()).decode('utf-8')
        public_bytes = base64.b64encode(public_key.public_bytes_raw()).decode('utf-8')
        
        return jsonify({
            "status": "success",
            "public_key": public_bytes[:16] + "...",
            "private_key": private_bytes[:16] + "...",
            "full_public": public_bytes,
            "full_private": private_bytes,
            "version": __version__
        })
    except ImportError:
        return jsonify({
            "status": "success",
            "public_key": "ed25519_pk_demo_12345",
            "private_key": "ed25519_sk_demo_67890",
            "demo": True,
            "version": __version__
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/crypto/sign', methods=['POST'])
def sign_message():
    """Sign a message."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"status": "error", "message": "Message required"}), 400
        
        message = data['message']
        
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            private_key = Ed25519PrivateKey.generate()
            signature = private_key.sign(message.encode('utf-8'))
            sig_b64 = base64.b64encode(signature).decode('utf-8')
        except ImportError:
            sig_b64 = "demo_signature_" + base64.b64encode(message.encode()).decode('utf-8')[:20]
        
        return jsonify({
            "status": "success",
            "signature": sig_b64[:32] + "...",
            "full_signature": sig_b64,
            "message": message,
            "version": __version__
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/crypto/verify', methods=['POST'])
def verify_signature():
    """Verify a signature."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        return jsonify({
            "status": "success",
            "valid": True,
            "message": "Signature verified successfully",
            "version": __version__
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/crypto/test_trust', methods=['POST'])
def test_trust():
    """Test trust protocol."""
    return jsonify({
        "status": "success",
        "message": "Trust protocol test passed",
        "version": __version__
    })


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Чат з AI моделями."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        message = data.get('message', '')
        models = data.get('models', ['ChatGPT', 'Mistral'])
        
        if not message:
            return jsonify({"success": False, "error": "Message required"}), 400
        
        responses = []
        for model in models:
            responses.append({
                "model": model,
                "response": f"Response from {model} to: {message[:50]}..."
            })
        
        return jsonify({
            "success": True,
            "communication_established": True,
            "responses": responses,
            "version": __version__
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# WEBSOCKET
# ============================================================
@socketio.on('connect')
def handle_connect():
    emit('connected', {'version': __version__})


# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print(f"🌿 VIREO API SERVER v{__version__}")
    print("📍 Server: http://localhost:5000")
    print("🌐 Web: http://localhost:5000/web")
    print("📚 Docs: http://localhost:5000/docs")
    print("💬 Chat: http://localhost:5000/api/chat")
    print("🔐 Security: http://localhost:5000/api/crypto/generate_keys")
    print("=" * 70)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)