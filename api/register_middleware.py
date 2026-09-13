"""
Vireo API Middleware v3.1.
"""

import time
import logging
from flask import request, g


logger = logging.getLogger("vireo.api")


def register_middleware(app):
    @app.before_request
    def before():
        g.request_started = time.time()

    @app.after_request
    def after(response):
        duration_ms = (time.time() - getattr(g, "request_started", time.time())) * 1000
        logger.info(
            "%s %s → %s (%.1f ms)",
            request.method, request.path, response.status_code, duration_ms,
        )
        response.headers["X-Vireo-Version"] = "3.1"
        return response


__all__ = ["register_middleware"]