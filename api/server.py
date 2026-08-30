# ============================================================
# VIREO API SERVER v1.4.3
# Flask REST API сервер
# The World's First AI-to-AI Communication Language
# ============================================================

__version__ = "1.4.3"

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Додаємо корінь проекту до шляху
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .routes import api_bp
    from .models import HealthResponse
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure routes.py and models.py exist in the same directory")
    sys.exit(1)


def create_app(config: dict = None) -> Flask:
    """
    Створює Flask додаток з конфігурацією.
    
    Args:
        config: Словник конфігурації
        
    Returns:
        Flask: Налаштований Flask додаток
    """
    app = Flask(__name__)
    
    # Базові налаштування
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vireo-secret-key')
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Застосовуємо кастомну конфігурацію
    if config:
        app.config.update(config)
    
    # CORS
    CORS(app)
    
    # Реєструємо API Blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # ===== ГОЛОВНА СТОРІНКА =====
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
                "/health",
                "/api/health",
                "/api/status",
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
                "/api/crypto/test_trust"
            ]
        })
    
    # ===== ВЕБ-ІНТЕРФЕЙС =====
    @app.route('/web')
    def web_interface():
        """Веб-інтерфейс."""
        # Шукаємо файл у кількох місцях
        possible_paths = [
            Path('web_interface.html'),
            Path(__file__).parent.parent / 'web_interface.html',
            Path('.').absolute() / 'web_interface.html'
        ]
        
        for path in possible_paths:
            if path.exists():
                return send_from_directory(str(path.parent), path.name)
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>🌿 Vireo Web Interface</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: #e2e8f0;
                    padding: 20px;
                }
                .container {
                    text-align: center;
                    background: rgba(255,255,255,0.05);
                    backdrop-filter: blur(10px);
                    border-radius: 24px;
                    padding: 50px 40px;
                    border: 1px solid rgba(255,255,255,0.1);
                    max-width: 600px;
                }
                .logo { font-size: 4em; margin-bottom: 10px; }
                h1 { font-size: 2.5em; background: linear-gradient(135deg, #48bb78, #667eea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .subtitle { color: #a0aec0; font-size: 1.2em; margin-bottom: 20px; }
                .error { color: #fc8181; background: rgba(245,101,101,0.1); padding: 15px; border-radius: 10px; border: 1px solid #fc8181; }
                .version { color: #48bb78; margin-top: 20px; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🌿</div>
                <h1>Vireo</h1>
                <p class="subtitle">The World's First AI-to-AI Communication Language</p>
                <div class="error">⚠️ web_interface.html not found</div>
                <p style="color:#718096; margin-top:20px;">Please place web_interface.html in the project root.</p>
                <div class="version">v1.4.3</div>
            </div>
        </body>
        </html>
        """, 404
    
    # ===== ДОКУМЕНТАЦІЯ =====
    @app.route('/docs')
    def docs():
        """Документація."""
        possible_paths = [
            Path('README.md'),
            Path(__file__).parent.parent / 'README.md',
            Path('.').absolute() / 'README.md'
        ]
        
        for path in possible_paths:
            if path.exists():
                return send_from_directory(str(path.parent), path.name)
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>📚 Vireo Documentation</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: #e2e8f0;
                    padding: 20px;
                }
                .container {
                    text-align: center;
                    background: rgba(255,255,255,0.05);
                    backdrop-filter: blur(10px);
                    border-radius: 24px;
                    padding: 50px 40px;
                    border: 1px solid rgba(255,255,255,0.1);
                    max-width: 600px;
                }
                h1 { font-size: 2.5em; background: linear-gradient(135deg, #48bb78, #667eea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .subtitle { color: #a0aec0; font-size: 1.2em; margin-bottom: 20px; }
                .error { color: #fc8181; background: rgba(245,101,101,0.1); padding: 15px; border-radius: 10px; border: 1px solid #fc8181; }
                .version { color: #48bb78; margin-top: 20px; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 Vireo Documentation</h1>
                <p class="subtitle">The World's First AI-to-AI Communication Language</p>
                <div class="error">⚠️ README.md not found</div>
                <p style="color:#718096; margin-top:20px;">Please place README.md in the project root.</p>
                <div class="version">v1.4.3</div>
            </div>
        </body>
        </html>
        """, 404
    
    # ===== HEALTH CHECK =====
    @app.route('/health')
    def health():
        """Health check."""
        return HealthResponse().to_dict()
    
    return app


# ============================================================
# ГОЛОВНИЙ ДОДАТОК
# ============================================================

app = create_app()


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🌿 VIREO API SERVER v1.4.3")
    print("The World's First AI-to-AI Communication Language")
    print("=" * 60)
    print(f"📍 Server: http://localhost:5000")
    print(f"🌐 Web:    http://localhost:5000/web")
    print(f"📚 Docs:   http://localhost:5000/docs")
    print(f"📡 API:    http://localhost:5000/api")
    print(f"🔐 Health: http://localhost:5000/health")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )