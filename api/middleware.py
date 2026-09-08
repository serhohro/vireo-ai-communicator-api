"""
Vireo API Middleware

Custom middleware for request processing, logging, rate limiting,
and security headers.
"""

import asyncio
import logging
import time
from collections import defaultdict
from typing import Dict, Optional, Callable, Awaitable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request logging middleware.
    Logs request details and response times.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging."""
        start_time = time.time()
        
        # Log request
        self.logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host}"
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            duration = (time.time() - start_time) * 1000
            self.logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status={response.status_code} duration={duration:.2f}ms"
            )
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(
                f"Error: {request.method} {request.url.path} "
                f"error={str(e)} duration={duration:.2f}ms"
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    Limits requests per client IP per time window.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        self.minute_counts: Dict[str, list] = defaultdict(list)
        self.hour_counts: Dict[str, list] = defaultdict(list)
        
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        client_ip = request.client.host
        
        # Check minute limit
        if self._is_rate_limited(client_ip, self.minute_counts, 60):
            self.logger.warning(f"Minute rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": "Too many requests per minute",
                    "retry_after": 60,
                },
            )
        
        # Check hour limit
        if self._is_rate_limited(client_ip, self.hour_counts, 3600):
            self.logger.warning(f"Hour rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": "Too many requests per hour",
                    "retry_after": 3600,
                },
            )
        
        # Record request
        current_time = time.time()
        self.minute_counts[client_ip].append(current_time)
        self.hour_counts[client_ip].append(current_time)
        
        # Clean old records
        self._clean_counts(client_ip, self.minute_counts, 60)
        self._clean_counts(client_ip, self.hour_counts, 3600)
        
        return await call_next(request)
    
    def _is_rate_limited(
        self,
        client_ip: str,
        counts: Dict[str, list],
        window_seconds: int,
    ) -> bool:
        """Check if client is rate limited."""
        if client_ip not in counts:
            return False
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Count requests in window
        valid_requests = [t for t in counts[client_ip] if t >= window_start]
        limit = self.requests_per_minute if window_seconds == 60 else self.requests_per_hour
        
        return len(valid_requests) >= limit
    
    def _clean_counts(self, client_ip: str, counts: Dict[str, list], window_seconds: int):
        """Remove old request records."""
        if client_ip in counts:
            current_time = time.time()
            window_start = current_time - window_seconds
            counts[client_ip] = [t for t in counts[client_ip] if t >= window_start]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware.
    Adds security headers to all responses.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.headers = {
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with security headers."""
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.headers.items():
            response.headers[header] = value
        
        return response


class CORSMiddlewareOverride(BaseHTTPMiddleware):
    """
    CORS middleware with configurable origins.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allowed_origins: Optional[list] = None,
        allowed_methods: Optional[list] = None,
        allowed_headers: Optional[list] = None,
    ):
        super().__init__(app)
        
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["*"]
        self.allowed_headers = allowed_headers or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with CORS headers."""
        response = await call_next(request)
        
        origin = request.headers.get("origin")
        if origin and (self.allowed_origins == ["*"] or origin in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Adds unique request ID to each request.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with request ID."""
        import uuid
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        self.logger.info(f"Request ID: {request_id}")
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Response compression middleware.
    Compresses responses for clients that support it.
    """
    
    def __init__(self, app: ASGIApp, min_size: int = 1024):
        super().__init__(app)
        self.min_size = min_size
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with compression."""
        response = await call_next(request)
        
        # Check if client supports compression
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return response
        
        # Check if response body is large enough
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.min_size:
            return response
        
        # Don't compress already compressed content
        content_type = response.headers.get("content-type", "")
        if "image/" in content_type or "video/" in content_type:
            return response
        
        try:
            # Get response body
            body = response.body
            if len(body) < self.min_size:
                return response
            
            # Compress
            import gzip
            compressed = gzip.compress(body)
            
            # Update headers
            response.body = compressed
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed))
            response.headers.pop("content-length", None)
            
        except Exception as e:
            self.logger.warning(f"Compression failed: {e}")
        
        return response


def setup_middleware(app: ASGIApp) -> ASGIApp:
    """
    Setup all middleware for the application.
    Order matters - first added is outermost.
    """
    # Add middleware in order (reverse of execution order)
    app = RequestIDMiddleware(app)
    app = SecurityHeadersMiddleware(app)
    app = CompressionMiddleware(app)
    app = RateLimitMiddleware(app)
    app = LoggingMiddleware(app)
    
    return app