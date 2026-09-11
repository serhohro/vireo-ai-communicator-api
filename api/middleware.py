"""
Vireo API Middleware v3.1.

Registers:
- request timing
- response headers
- optional rate limiting (in-memory)
"""

import time
import logging
from collections import defaultdict
from flask import request, g, jsonify


logger = logging.getLogger("vireo.api")


# In-memory rate limit: {ip: [(timestamp, count)]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW_SEC = 60
RATE_LIMIT_MAX_REQUESTS = 300


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SEC

    # Prune old entries
    _rate_limit_store[ip] = [
        ts for ts in _rate_limit_store[ip] if ts > window_start
    ]

    if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return True

    _rate_limit_store[ip].append(now)
    return False


def register_middleware(app):
    """Register all middleware on the Flask app."""

    @app.before_request
    def before():
        g.request_started = time.time()

        # Rate limit (skip health checks)
        if request.path not in ("/api/health", "/"):
            ip = request.remote_addr or "unknown"
            if _is_rate_limited(ip):
                return jsonify({
                    "error": "rate limit exceeded",
                    "retry_after_sec": RATE_LIMIT_WINDOW_SEC,
                }), 429

    @app.after_request
    def after(response):
        duration_ms = (time.time() - getattr(g, "request_started", time.time())) * 1000
        logger.info(
            "%s %s → %s (%.1f ms)",
            request.method, request.path, response.status_code, duration_ms,
        )
        response.headers["X-Vireo-Version"] = "3.1"
        response.headers["X-Vireo-Wire-Version"] = "0x0301"
        return response

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found", "path": request.path}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "error": "method not allowed",
            "method": request.method,
            "path": request.path,
        }), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Internal server error")
        return jsonify({"error": "internal server error"}), 500


__all__ = ["register_middleware"]