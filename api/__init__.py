"""
Vireo API Package v3.1

REST API for Vireo AI agents.

App factory pattern:
    from api import create_app
    app = create_app()
    app.run(host="0.0.0.0", port=5000)

Entry point:
    python -m api.server
"""

from flask import Flask
from flask_cors import CORS

from .routes import register_routes
from .middleware import register_middleware
from .auth import AuthManager, AuthContext, require_auth, require_api_key


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask app with all routes registered.
    """
    app = Flask(
        __name__,
        static_folder="../web",
        static_url_path="/static",
    )
    CORS(app)

    register_middleware(app)
    register_routes(app)

    return app


__all__ = [
    "create_app",
    "AuthManager",
    "AuthContext",
    "require_auth",
    "require_api_key",
]

__version__ = "3.1.0"