# ============================================================
# VIREO API SERVER
# ============================================================
"""
Async API server for Vireo.

Provides:
- Async FastAPI endpoints
- Agent management
- LLM provider integration
- Model serving
- Web interface
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .models import HealthResponse, VersionResponse

logger = logging.getLogger(__name__)


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting Vireo API server...")
    
    # Initialize components
    from protocol.llm_provider import AVAILABLE_PROVIDERS
    logger.info(f"✅ LLM Providers: {AVAILABLE_PROVIDERS}")
    
    yield
    
    logger.info("🛑 Shutting down Vireo API server...")


# ============================================================
# APP CREATION
# ============================================================

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Vireo AI Communicator API",
        description="The World's First AI-to-AI Communication Language",
        version="2.0.2",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include router
    app.include_router(router)
    
    # ============================================================
    # ROOT ENDPOINT
    # ============================================================
    
    @app.get("/", response_model=VersionResponse)
    async def root():
        """Root endpoint with API information."""
        return VersionResponse(
            name="Vireo AI Communicator API",
            version="2.0.2",
            status="running",
            service="The World's First AI-to-AI Communication Language",
            endpoints=[
                "/",
                "/web",
                "/docs",
                "/health",
                "/api/health",
                "/api/providers",
                "/api/agent/register",
                "/api/agent/list",
                "/api/agent/{id}/status",
                "/api/agent/{id}/capability",
                "/api/interpreter",
                "/api/neural",
                "/api/chat",
                "/api/llm/agent/{id}/auto_negotiate",
                "/api/crypto/generate_keys",
                "/api/crypto/sign",
                "/api/crypto/verify",
                "/api/crypto/test_trust",
                "/api/mistral/generate",
                "/api/mistral/chat",
                "/models/list",
                "/models/load/{model_name}",
                "/models/predict/{model_name}",
                "/models/info/{model_name}",
                "/models/cache/clear",
                "/lstm"
            ]
        )
    
    # ============================================================
    # WEB INTERFACE
    # ============================================================
    
    @app.get("/web")
    async def web_interface():
        """Web interface."""
        possible_paths = [
            Path("web_interface.html"),
            Path(__file__).parent.parent / "web_interface.html",
        ]
        
        for path in possible_paths:
            if path.exists():
                return FileResponse(path)
        
        return HTMLResponse("""
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
                <div class="version">v2.0.2</div>
            </div>
        </body>
        </html>
        """, status_code=404)
    
    # ============================================================
    # HEALTH CHECK
    # ============================================================
    
    @app.get("/health")
    @app.get("/api/health")
    async def health():
        """Health check."""
        return HealthResponse(
            status="healthy",
            version="2.0.2",
            name="Vireo AI Communicator API"
        )
    
    return app


# ============================================================
# MAIN
# ============================================================

app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🌿 VIREO API SERVER v2.0.2")
    print("The World's First AI-to-AI Communication Language")
    print("=" * 60)
    print(f"📍 Server: http://localhost:5000")
    print(f"🌐 Web:    http://localhost:5000/web")
    print(f"📡 API:    http://localhost:5000/api/health")
    print("=" * 60)
    print("🧠 LLM Providers: Ollama, Gemini, Claude, OpenAI, Mistral")
    print("🔥 European LLM support: Mistral, BLOOM, OpenChat")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )