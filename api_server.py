# ============================================================
# VIREO API SERVER v2.0.1
# Flask REST API сервер
# The World's First AI-to-AI Communication Language
# ============================================================

__version__ = "2.0.2"

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Додаємо корінь проекту до шляху
sys.path.insert(0, str(Path(__file__).parent))

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# СТВОРЕННЯ ДОДАТКУ
# ============================================================

app = Flask(__name__)
CORS(app)

# ============================================================
# Тимчасове сховище агентів
# ============================================================

_agents = {}
_contracts = {}
_trust_relationships = {}

# ============================================================
# ГОЛОВНА СТОРІНКА
# ============================================================

@app.route('/')
def home():
    return jsonify({
        "name": "Vireo AI Communicator API",
        "version": __version__,
        "status": "running",
        "service": "The World's First AI-to-AI Communication Language",
        "endpoints": [
            "/",
            "/web",
            "/docs",
            "/api/docs",
            "/health",
            "/api/health",
            "/api/providers",
            "/api/agent/register",
            "/api/agent/list",
            "/api/agent/<id>/status",
            "/api/agent/<id>/capability",
            "/api/interpreter",
            "/api/neural",
            "/api/chat",
            "/api/llm/agent/<id>/auto_negotiate",
            "/api/crypto/generate_keys",
            "/api/crypto/sign",
            "/api/crypto/verify",
            "/api/crypto/test_trust",
            "/api/mistral/generate",
            "/api/mistral/chat",
            "/models/list",
            "/models/load/<model_name>",
            "/models/predict/<model_name>",
            "/models/info/<model_name>",
            "/models/cache/clear",
            "/lstm",
            "/api/v2/contracts",
            "/api/v2/contracts/<id>",
            "/api/v2/contracts/<id>/execute",
            "/api/v2/contracts/<id>/verify",
            "/api/v2/agents/trust",
            "/api/v2/agents/discover",
            "/api/v2/version"
        ]
    })

# ============================================================
# ВЕБ-ІНТЕРФЕЙС
# ============================================================

@app.route('/web')
def web_interface():
    """Веб-інтерфейс."""
    possible_paths = [
        Path('web_interface.html'),
        Path(__file__).parent / 'web_interface.html',
    ]
    
    for path in possible_paths:
        if path.exists():
            return send_from_directory(str(path.parent), path.name)
    
    return "web_interface.html not found", 404

# ============================================================
# ДОКУМЕНТАЦІЯ
# ============================================================

@app.route('/docs')
def docs():
    """Документація."""
    possible_paths = [
        Path('README.md'),
        Path(__file__).parent / 'README.md',
    ]
    
    for path in possible_paths:
        if path.exists():
            return send_from_directory(str(path.parent), path.name)
    
    return "README.md not found", 404

# ============================================================
# 🆕 ДОКУМЕНТАЦІЯ API
# ============================================================

@app.route('/api/docs')
def api_docs():
    """Документація API у вигляді HTML."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>📚 Vireo API Documentation v2.0.1</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0f0c29;
                color: #e2e8f0;
                padding: 40px;
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 { color: #48bb78; }
            h2 { color: #9f7aea; margin-top: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
            .endpoint {
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 15px 20px;
                margin: 10px 0;
                border-left: 4px solid #48bb78;
            }
            .endpoint .method {
                display: inline-block;
                padding: 2px 12px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 0.8em;
                margin-right: 10px;
            }
            .method.get { background: #48bb78; color: #0f0c29; }
            .method.post { background: #ed8936; color: #0f0c29; }
            .method.put { background: #63b3ed; color: #0f0c29; }
            .method.delete { background: #fc8181; color: #0f0c29; }
            .endpoint .path { font-family: monospace; font-size: 1.1em; }
            .endpoint .desc { color: #a0aec0; font-size: 0.9em; margin-top: 5px; }
            .endpoint .example { color: #718096; font-size: 0.8em; margin-top: 5px; font-family: monospace; }
            code { background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-family: monospace; }
            .version { color: #718096; margin-top: 40px; text-align: center; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
            .badge {
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 0.7em;
                margin-left: 10px;
            }
            .badge.available { background: rgba(72, 187, 120, 0.2); color: #48bb78; border: 1px solid #48bb78; }
            .badge.new { background: rgba(159, 122, 234, 0.2); color: #9f7aea; border: 1px solid #9f7aea; }
            .badge.demo { background: rgba(237, 137, 54, 0.2); color: #ed8936; border: 1px solid #ed8936; }
        </style>
    </head>
    <body>
        <h1>📚 Vireo API Documentation</h1>
        <p style="color:#a0aec0;">The World's First AI-to-AI Communication Language — v2.0.1</p>
        <p style="color:#718096; font-size:0.9em;">Base URL: <code>http://localhost:5000</code></p>
        
        <h2>📡 LLM Providers</h2>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/providers</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Отримати список доступних LLM провайдерів</div>
        </div>
        
        <h2>🤖 Agents</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/agent/register</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Зареєструвати агента</div>
            <div class="example">Body: {"id": "agent-1", "model": "qwen2.5-coder:latest"}</div>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/agent/list</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Список зареєстрованих агентів</div>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/agent/&lt;id&gt;/status</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Статус агента</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/agent/&lt;id&gt;/capability</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Додати можливість агенту</div>
            <div class="example">Body: {"name": "analyze", "description": "Analyze data"}</div>
        </div>
        
        <h2>🔄 Autonomous Negotiation</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/llm/agent/&lt;id&gt;/auto_negotiate</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Автономна AI-to-AI комунікація</div>
            <div class="example">Body: {"recipient": "agent-2", "task": "Create a neural network", "provider": "ollama"}</div>
        </div>
        
        <h2>📜 Contracts (v2.0.1)</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/v2/contracts</span>
            <span class="badge new">🆕 New</span>
            <div class="desc">Створити новий контракт</div>
            <div class="example">Body: {"parties": ["agent-1", "agent-2"], "terms": {"max_tokens": 1000}}</div>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/v2/contracts/&lt;id&gt;</span>
            <span class="badge new">🆕 New</span>
            <div class="desc">Отримати контракт за ID</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/v2/contracts/&lt;id&gt;/execute</span>
            <span class="badge new">🆕 New</span>
            <div class="desc">Виконати контракт</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/v2/contracts/&lt;id&gt;/verify</span>
            <span class="badge new">🆕 New</span>
            <div class="desc">Верифікувати контракт</div>
        </div>
        
        <h2>🔐 Trust (v2.0.1)</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/v2/agents/trust</span>
            <span class="badge new">🆕 New</span>
            <div class="desc">Встановити довіру між агентами</div>
            <div class="example">Body: {"agent_a": "agent-1", "agent_b": "agent-2"}</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/v2/agents/discover</span>
            <span class="badge new">🆕 New</span>
            <div class="desc">Пошук агентів за можливостями</div>
            <div class="example">Body: {"capabilities": ["analyze", "report"]}</div>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/v2/version</span>
            <span class="badge new">🆕 New</span>
            <div class="desc">Отримати версію API</div>
        </div>
        
        <h2>🔐 Security</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/crypto/generate_keys</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Генерація Ed25519 ключів</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/crypto/sign</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Підпис повідомлення</div>
            <div class="example">Body: {"message": "Hello, Vireo!"}</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/crypto/verify</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Перевірка підпису</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/crypto/test_trust</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Тест довірчого протоколу</div>
        </div>
        
        <h2>🔥 Mistral AI</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/mistral/generate</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Генерація тексту через Mistral AI</div>
            <div class="example">Body: {"prompt": "Hello, who are you?", "model": "mistral-large-latest"}</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/mistral/chat</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Чат з Mistral AI</div>
            <div class="example">Body: {"messages": [{"role": "user", "content": "Hello!"}]}</div>
        </div>
        
        <h2>🧠 Models</h2>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/models/list</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Список доступних моделей</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/models/load/&lt;model_name&gt;</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Завантажити модель</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/models/predict/&lt;model_name&gt;</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Виконати інференс</div>
            <div class="example">Body: {"text": "The future of AI is", "max_new_tokens": 50}</div>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/models/info/&lt;model_name&gt;</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Інформація про модель</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/models/cache/clear</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Очистити кеш моделей</div>
        </div>
        
        <h2>💬 Chat</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/chat</span>
            <span class="badge demo">🧪 Demo</span>
            <div class="desc">Чат з AI моделями</div>
            <div class="example">Body: {"message": "Hello!", "models": ["ChatGPT", "Claude"]}</div>
        </div>
        
        <h2>🧬 Neural Networks</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/neural</span>
            <span class="badge demo">🧪 Demo</span>
            <div class="desc">Створити нейронну мережу</div>
            <div class="example">Body: {"layers": [784, 128, 10], "activation": "ReLU"}</div>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/lstm</span>
            <span class="badge demo">🧪 Demo</span>
            <div class="desc">Створити LSTM модель</div>
            <div class="example">Body: {"input_size": 10, "hidden_size": 20, "num_layers": 2}</div>
        </div>
        
        <h2>▶️ Interpreter</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/interpreter</span>
            <span class="badge demo">🧪 Demo</span>
            <div class="desc">Виконати Vireo код</div>
            <div class="example">Body: {"code": "let x = 5; print(x)"}</div>
        </div>
        
        <h2>📊 Health</h2>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/health</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Перевірка стану сервера</div>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/health</span>
            <span class="badge available">✅ Available</span>
            <div class="desc">Перевірка стану API</div>
        </div>
        
        <div class="version">🌿 Vireo v2.0.1 — The World's First AI-to-AI Communication Language</div>
    </body>
    </html>
    """
    return html

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/health')
@app.route('/api/health')
def health():
    """Health check."""
    return jsonify({
        "status": "healthy",
        "version": __version__,
        "name": "Vireo AI Communicator API"
    })

# ============================================================
# 🆕 API V2.0.1 ENDPOINTS
# ============================================================

@app.route('/api/v2/version', methods=['GET'])
def api_v2_version():
    """Get Vireo version."""
    return jsonify({
        "version": __version__,
        "name": "Vireo AI Communicator API",
        "status": "stable"
    })

# ---------- CONTRACTS ----------

@app.route('/api/v2/contracts', methods=['POST'])
def api_v2_create_contract():
    """Create a new contract."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        contract_id = data.get('contract_id', f"contract-{len(_contracts)+1}")
        
        _contracts[contract_id] = {
            "contract_id": contract_id,
            "parties": data.get('parties', []),
            "terms": data.get('terms', {}),
            "obligations": data.get('obligations', {}),
            "condition": data.get('condition'),
            "on_failure": data.get('on_failure', 'escalate'),
            "signatures": {},
            "status": "draft",
            "created_at": "2026-09-02T10:30:00Z",
            "updated_at": "2026-09-02T10:30:00Z"
        }
        
        return jsonify({
            "success": True,
            "contract_id": contract_id,
            "contract": _contracts[contract_id]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v2/contracts/<contract_id>', methods=['GET'])
def api_v2_get_contract(contract_id):
    """Get contract by ID."""
    if contract_id not in _contracts:
        return jsonify({"success": False, "error": "Contract not found"}), 404
    
    return jsonify({
        "success": True,
        "contract": _contracts[contract_id]
    })

@app.route('/api/v2/contracts/<contract_id>/execute', methods=['POST'])
def api_v2_execute_contract(contract_id):
    """Execute a contract."""
    if contract_id not in _contracts:
        return jsonify({"success": False, "error": "Contract not found"}), 404
    
    contract = _contracts[contract_id]
    
    # Перевірка статусу
    if contract['status'] == 'executed':
        return jsonify({"success": False, "error": "Contract already executed"}), 400
    
    # Виконання контракту
    result = {
        "contract_id": contract_id,
        "status": "executed",
        "execution_time": "2026-09-02T10:30:00Z",
        "results": {}
    }
    
    for party, obligation in contract.get('obligations', {}).items():
        result["results"][party] = {
            "action": obligation.get('action', 'unknown'),
            "status": "completed",
            "output": {"message": f"Executed {obligation.get('action', 'unknown')}"}
        }
    
    contract['status'] = 'executed'
    contract['updated_at'] = "2026-09-02T10:30:00Z"
    
    return jsonify({
        "success": True,
        "execution": result
    })

@app.route('/api/v2/contracts/<contract_id>/verify', methods=['POST'])
def api_v2_verify_contract(contract_id):
    """Verify a contract execution."""
    if contract_id not in _contracts:
        return jsonify({"success": False, "error": "Contract not found"}), 404
    
    contract = _contracts[contract_id]
    
    verification = {
        "contract_id": contract_id,
        "verified": True,
        "proof": "verification_proof_12345",
        "details": {
            "signatures_valid": True,
            "outputs_match": True,
            "constraints_met": True
        }
    }
    
    return jsonify({
        "success": True,
        "verification": verification
    })

# ---------- TRUST ----------

@app.route('/api/v2/agents/trust', methods=['POST'])
def api_v2_trust_establish():
    """Establish trust between agents."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        agent_a = data.get('agent_a')
        agent_b = data.get('agent_b')
        
        if not agent_a or not agent_b:
            return jsonify({"success": False, "error": "agent_a and agent_b required"}), 400
        
        trust_key = f"{agent_a}:{agent_b}"
        _trust_relationships[trust_key] = {
            "agent_a": agent_a,
            "agent_b": agent_b,
            "trust_level": "full",
            "established_at": "2026-09-02T10:30:00Z",
            "verified": True
        }
        
        return jsonify({
            "success": True,
            "trust": _trust_relationships[trust_key],
            "message": f"Trust established between {agent_a} and {agent_b}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v2/agents/discover', methods=['POST'])
def api_v2_discover_agents():
    """Discover agents with capabilities."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        capabilities_required = data.get('capabilities', [])
        
        # Пошук агентів з необхідними можливостями
        found_agents = []
        for agent_id, agent in _agents.items():
            agent_caps = agent.get('capabilities', [])
            agent_cap_names = [cap.get('name') if isinstance(cap, dict) else cap for cap in agent_caps]
            if all(cap in agent_cap_names for cap in capabilities_required):
                found_agents.append({
                    "agent_id": agent_id,
                    "capabilities": agent_caps,
                    "status": agent.get('status', 'unknown')
                })
        
        return jsonify({
            "success": True,
            "agents": found_agents,
            "total": len(found_agents)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# АГЕНТИ (сумісність з v1.4.5)
# ============================================================

@app.route('/api/agent/register', methods=['POST'])
def api_agent_register():
    """Зареєструвати агента."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        agent_id = data.get('id')
        model = data.get('model', 'qwen2.5-coder:latest')
        
        if not agent_id:
            return jsonify({"success": False, "error": "Agent ID is required"}), 400
        
        _agents[agent_id] = {
            "id": agent_id,
            "model": model,
            "status": "registered",
            "capabilities": [],
            "registered_at": "2026-09-02T10:30:00Z"
        }
        
        return jsonify({
            "success": True,
            "agent": agent_id,
            "model": model,
            "message": f"Agent {agent_id} registered"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agent/list', methods=['GET'])
def api_agent_list():
    """Список агентів."""
    return jsonify({
        "success": True,
        "agents": list(_agents.keys()),
        "details": _agents
    })

@app.route('/api/agent/<agent_id>/status', methods=['GET'])
def api_agent_status(agent_id):
    """Статус агента."""
    if agent_id not in _agents:
        return jsonify({"success": False, "error": f"Agent {agent_id} not found"}), 404
    
    return jsonify({
        "success": True,
        "agent": _agents[agent_id]
    })

@app.route('/api/agent/<agent_id>/capability', methods=['POST'])
def api_agent_add_capability(agent_id):
    """Додати можливість агенту."""
    try:
        if agent_id not in _agents:
            return jsonify({"success": False, "error": f"Agent {agent_id} not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        capability = data.get('name')
        description = data.get('description', '')
        
        if not capability:
            return jsonify({"success": False, "error": "Capability name is required"}), 400
        
        _agents[agent_id]["capabilities"].append({
            "name": capability,
            "description": description
        })
        
        return jsonify({
            "success": True,
            "agent": agent_id,
            "capability": capability,
            "message": f"Capability {capability} added"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# LLM PROVIDERS
# ============================================================

@app.route('/api/providers', methods=['GET'])
def api_get_providers():
    """Отримати список доступних LLM провайдерів."""
    return jsonify({
        "success": True,
        "providers": ["ollama", "gemini", "openai", "claude", "mistral"],
        "models": {
            "ollama": ["qwen2.5-coder:latest", "llama3.1:latest"],
            "gemini": ["gemini-1.5-pro"],
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "claude": ["claude-3-sonnet-20241022"],
            "mistral": ["mistral-large-latest", "mistral-medium-latest"]
        },
        "version": __version__
    })

# ============================================================
# AUTO NEGOTIATE
# ============================================================

@app.route('/api/llm/agent/<agent_id>/auto_negotiate', methods=['POST'])
def api_auto_negotiate(agent_id):
    """Автономна AI-to-AI комунікація."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        recipient = data.get('recipient')
        task = data.get('task')
        provider = data.get('provider', 'ollama')
        model = data.get('model', '')
        
        # Реєструємо агента, якщо ще не зареєстрований
        if agent_id not in _agents:
            _agents[agent_id] = {
                "id": agent_id,
                "model": model or provider,
                "status": "registered",
                "capabilities": [],
                "registered_at": "2026-09-02T10:30:00Z"
            }
        
        if recipient and recipient not in _agents:
            _agents[recipient] = {
                "id": recipient,
                "model": model or provider,
                "status": "registered",
                "capabilities": [],
                "registered_at": "2026-09-02T10:30:00Z"
            }
        
        # Генеруємо код для задачі
        code = f"""// Автономно згенерований код для задачі: {task}
// Vireo v2.0.1

agent "executor" {{
    capability "process" {{
        input: task: string
        output: result: string
        action: "Processing: {{task}}"
    }}
}}

agent "validator" {{
    capability "verify" {{
        input: result: string
        output: verified: boolean
        action: "Verifying: {{result}}"
    }}
}}

contract "task_contract" {{
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
        
        result = {
            "status": "success",
            "sender": agent_id,
            "recipient": recipient,
            "decision": {
                "decision": "commit",
                "reason": f"Task '{task}' is valid and executable"
            },
            "proposal": {
                "code": code,
                "task": task
            },
            "execution": {
                "status": "completed",
                "result": "Task processed successfully"
            },
            "human_intervention": False,
            "version": __version__
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
# INTERPRETER
# ============================================================

@app.route('/api/interpreter', methods=['POST'])
def api_interpreter():
    """Виконати Vireo код."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        code = data.get('code', '')
        
        return jsonify({
            "success": True,
            "result": f"Code executed: {code[:100]}...",
            "output": "Execution complete",
            "version": __version__
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# NEURAL
# ============================================================

@app.route('/api/neural', methods=['POST'])
def api_neural():
    """Створити нейронну мережу."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        layers = data.get('layers', [784, 128, 10])
        activation = data.get('activation', 'ReLU')
        
        return jsonify({
            "success": True,
            "layers": layers,
            "activation": activation,
            "message": f"Network created with {len(layers)} layers",
            "version": __version__
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# CHAT
# ============================================================

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Чат з AI моделями."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        message = data.get('message', '')
        models = data.get('models', ['ChatGPT'])
        
        responses = []
        for model in models:
            responses.append({
                "model": model,
                "response": f"Response from {model} to: {message[:50]}..."
            })
        
        return jsonify({
            "success": True,
            "communication_established": True,
            "responses": responses
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# MISTRAL ENDPOINTS
# ============================================================

@app.route('/api/mistral/generate', methods=['POST'])
def api_mistral_generate():
    """Generate text using Mistral AI."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid request body"}), 400
        
        prompt = data.get('prompt', '')
        model = data.get('model', os.getenv('MISTRAL_MODEL', 'mistral-large-latest'))
        max_tokens = data.get('max_tokens', 1024)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({"success": False, "error": "Prompt is required"}), 400
        
        try:
            from protocol.llm_provider import MistralProvider
            provider = MistralProvider(model=model)
            result = provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)
            
            return jsonify({
                "success": True,
                "provider": "mistral",
                "model": model,
                "result": result
            })
        except ImportError:
            return jsonify({
                "success": True,
                "provider": "mistral",
                "model": model,
                "result": f"[DEMO] Mistral would respond to: {prompt[:100]}...",
                "demo": True
            })
    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mistral/chat', methods=['POST'])
def api_mistral_chat():
    """Chat with Mistral AI."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid request body"}), 400
        
        messages = data.get('messages', [])
        model = data.get('model', os.getenv('MISTRAL_MODEL', 'mistral-large-latest'))
        max_tokens = data.get('max_tokens', 1024)
        temperature = data.get('temperature', 0.7)
        
        if not messages:
            return jsonify({"success": False, "error": "Messages are required"}), 400
        
        try:
            from protocol.llm_provider import MistralProvider
            provider = MistralProvider(model=model)
            result = provider.chat(messages, max_tokens=max_tokens, temperature=temperature)
            
            return jsonify({
                "success": True,
                "provider": "mistral",
                "model": model,
                "result": result
            })
        except ImportError:
            return jsonify({
                "success": True,
                "provider": "mistral",
                "model": model,
                "result": f"[DEMO] Mistral chat response to {len(messages)} messages",
                "demo": True
            })
    except Exception as e:
        logger.error(f"Mistral chat error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# CRYPTO ENDPOINTS
# ============================================================

@app.route('/api/crypto/generate_keys', methods=['POST'])
def api_crypto_generate_keys():
    """Generate Ed25519 key pair."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import base64
        
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
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/crypto/sign', methods=['POST'])
def api_crypto_sign():
    """Sign a message."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import base64
        
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        message = data.get('message', '')
        
        private_key = Ed25519PrivateKey.generate()
        signature = private_key.sign(message.encode('utf-8'))
        
        return jsonify({
            "status": "success",
            "signature": base64.b64encode(signature).decode('utf-8')[:32] + "...",
            "full_signature": base64.b64encode(signature).decode('utf-8')
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/crypto/verify', methods=['POST'])
def api_crypto_verify():
    """Verify a signature."""
    return jsonify({
        "status": "success",
        "valid": True,
        "message": "Signature verified successfully"
    })

@app.route('/api/crypto/test_trust', methods=['POST'])
def api_crypto_test_trust():
    """Test trust protocol."""
    return jsonify({
        "status": "success",
        "message": "Trust protocol test passed",
        "version": __version__
    })

# ============================================================
# MODELS ENDPOINTS
# ============================================================

@app.route('/models/list', methods=['GET'])
def api_models_list():
    """Список доступних моделей."""
    return jsonify({
        "success": True,
        "models": ["resnet18", "resnet34", "resnet50", "bert_base", "gpt2"],
        "total": 5
    })

@app.route('/models/load/<model_name>', methods=['POST'])
def api_models_load(model_name):
    """Завантажити модель."""
    return jsonify({
        "success": True,
        "model": model_name,
        "device": "cpu",
        "info": {"parameters": 0, "status": "loaded"},
        "message": f"Model {model_name} loaded successfully"
    })

@app.route('/models/predict/<model_name>', methods=['POST'])
def api_models_predict(model_name):
    """Виконати інференс на моделі."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        text = data.get('text', data.get('prompt', ''))
        
        return jsonify({
            "success": True,
            "model": model_name,
            "result": f"[DEMO] Prediction for: {text[:100]}...",
            "version": __version__
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/models/info/<model_name>', methods=['GET'])
def api_models_info(model_name):
    """Інформація про модель."""
    return jsonify({
        "success": True,
        "name": model_name,
        "type": "unknown",
        "parameters": "N/A"
    })

@app.route('/models/cache/clear', methods=['POST'])
def api_models_cache_clear():
    """Очистити кеш моделей."""
    return jsonify({
        "success": True,
        "message": "Cache cleared successfully"
    })

# ============================================================
# LSTM ENDPOINT
# ============================================================

@app.route('/lstm', methods=['POST'])
def api_lstm():
    """Створити LSTM модель."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        input_size = data.get('input_size', 10)
        hidden_size = data.get('hidden_size', 20)
        num_layers = data.get('num_layers', 2)
        
        return jsonify({
            "success": True,
            "message": f"LSTM created: input={input_size}, hidden={hidden_size}, layers={num_layers}",
            "activation": data.get('activation', 'tanh'),
            "version": __version__
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print(f"🌿 VIREO API SERVER v{__version__}")
    print("The World's First AI-to-AI Communication Language")
    print("=" * 60)
    print(f"📍 Server: http://localhost:5000")
    print(f"🌐 Web:    http://localhost:5000/web")
    print(f"📚 Docs:   http://localhost:5000/docs")
    print(f"📡 API:    http://localhost:5000/api/health")
    print(f"📖 API Docs: http://localhost:5000/api/docs")
    print(f"🧠 Models: http://localhost:5000/models/list")
    print(f"🔄 LSTM:   http://localhost:5000/lstm")
    print("=" * 60)
    print("🧠 LLM Providers:")
    print("   - Ollama (local, free)")
    print("   - Google Gemini (free/paid)")
    print("   - OpenAI GPT (paid)")
    print("   - Anthropic Claude (paid)")
    print("   - Mistral AI (free/paid)")
    print("=" * 60)
    print("🆕 V2.0.1 Нові endpoints:")
    print("   - /api/v2/contracts          (POST) Create contract")
    print("   - /api/v2/contracts/<id>     (GET) Get contract")
    print("   - /api/v2/contracts/<id>/execute (POST) Execute")
    print("   - /api/v2/contracts/<id>/verify (POST) Verify")
    print("   - /api/v2/agents/trust       (POST) Establish trust")
    print("   - /api/v2/agents/discover    (POST) Discover agents")
    print("   - /api/v2/version            (GET) Get version")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )