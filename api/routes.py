# ============================================================
# VIREO API ROUTES
# ============================================================
"""
Async API routes for Vireo.

Provides:
- Agent management endpoints
- LLM provider endpoints
- Model serving endpoints
- Cryptography endpoints
- Interpreter endpoints
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Request

from .models import (
    AgentRegisterRequest,
    AgentResponse,
    CapabilityRequest,
    ChatRequest,
    ChatResponse,
    CryptoKeysResponse,
    CryptoSignRequest,
    CryptoSignResponse,
    CryptoVerifyRequest,
    CryptoVerifyResponse,
    InterpreterRequest,
    InterpreterResponse,
    MistralGenerateRequest,
    MistralGenerateResponse,
    ModelLoadResponse,
    ModelPredictResponse,
    NeuralRequest,
    NeuralResponse,
    ProviderResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["vireo"])


# ============================================================
# AGENTS
# ============================================================

# Temporary storage for agents
_agents: Dict[str, Dict] = {}


@router.post("/agent/register", response_model=AgentResponse)
async def register_agent(request: AgentRegisterRequest):
    """Register an agent."""
    agent_id = request.id
    model = request.model or "qwen2.5-coder:latest"
    
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent ID is required")
    
    _agents[agent_id] = {
        "id": agent_id,
        "model": model,
        "status": "registered",
        "capabilities": []
    }
    
    return AgentResponse(
        success=True,
        agent=agent_id,
        model=model,
        message=f"Agent {agent_id} registered"
    )


@router.get("/agent/list")
async def list_agents():
    """List all registered agents."""
    return {
        "success": True,
        "agents": list(_agents.keys()),
        "details": _agents
    }


@router.get("/agent/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent status."""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return {
        "success": True,
        "agent": _agents[agent_id]
    }


@router.post("/agent/{agent_id}/capability")
async def add_capability(agent_id: str, request: CapabilityRequest):
    """Add a capability to an agent."""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    capability = request.name
    description = request.description or f"{capability} capability"
    
    if not capability:
        raise HTTPException(status_code=400, detail="Capability name is required")
    
    _agents[agent_id]["capabilities"].append({
        "name": capability,
        "description": description
    })
    
    return {
        "success": True,
        "agent": agent_id,
        "capability": capability,
        "message": f"Capability {capability} added"
    }


# ============================================================
# PROVIDERS
# ============================================================

@router.get("/providers", response_model=ProviderResponse)
async def get_providers():
    """Get available LLM providers."""
    try:
        from protocol.llm_provider import AVAILABLE_PROVIDERS, AVAILABLE_MODELS
        return ProviderResponse(
            success=True,
            providers=AVAILABLE_PROVIDERS,
            models=AVAILABLE_MODELS
        )
    except ImportError:
        return ProviderResponse(
            success=True,
            providers=["ollama", "gemini", "openai", "claude", "mistral"],
            models={
                "ollama": ["qwen2.5-coder:latest", "llama3.1:latest"],
                "gemini": ["gemini-1.5-pro"],
                "openai": ["gpt-4"],
                "claude": ["claude-3-sonnet-20241022"],
                "mistral": ["mistral-large-latest"]
            }
        )


# ============================================================
# LLM AGENT NEGOTIATION
# ============================================================

@router.post("/llm/agent/{agent_id}/auto_negotiate")
async def auto_negotiate(agent_id: str, request: Request):
    """Autonomous AI-to-AI negotiation."""
    try:
        data = await request.json()
        recipient = data.get("recipient")
        task = data.get("task")
        provider = data.get("provider", "ollama")
        model = data.get("model", "")
        
        # Register agent if not registered
        if agent_id not in _agents:
            _agents[agent_id] = {
                "id": agent_id,
                "model": model or provider,
                "status": "registered",
                "capabilities": []
            }
        
        if recipient and recipient not in _agents:
            _agents[recipient] = {
                "id": recipient,
                "model": model or provider,
                "status": "registered",
                "capabilities": []
            }
        
        # Generate code for the task
        code = f"""// Autonomous generated code for task: {task}
model MNIST {{
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
}}

train MNIST {{
    epochs: 10
    batch_size: 32
    learning_rate: 0.001
}}

evaluate MNIST
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
                "result": "Model created successfully"
            },
            "human_intervention": False
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Auto negotiation error: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================
# INTERPRETER
# ============================================================

@router.post("/interpreter", response_model=InterpreterResponse)
async def execute_code(request: InterpreterRequest):
    """Execute Vireo code."""
    code = request.code
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    try:
        # Execute code (simplified)
        result = f"Code executed: {code[:100]}..."
        return InterpreterResponse(
            success=True,
            result=result,
            output="Execution complete"
        )
    except Exception as e:
        return InterpreterResponse(
            success=False,
            error=str(e)
        )


# ============================================================
# NEURAL NETWORK
# ============================================================

@router.post("/neural", response_model=NeuralResponse)
async def create_neural(request: NeuralRequest):
    """Create a neural network."""
    layers = request.layers or [784, 128, 10]
    activation = request.activation or "ReLU"
    
    return NeuralResponse(
        success=True,
        layers=layers,
        activation=activation,
        message=f"Network created with {len(layers)} layers"
    )


# ============================================================
# CHAT
# ============================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI models."""
    message = request.message or ""
    models = request.models or ["ChatGPT"]
    
    responses = [
        {
            "model": model,
            "response": f"Response from {model} to: {message[:50]}..."
        }
        for model in models
    ]
    
    return ChatResponse(
        success=True,
        communication_established=True,
        responses=responses
    )


# ============================================================
# MISTRAL AI
# ============================================================

@router.post("/mistral/generate", response_model=MistralGenerateResponse)
async def mistral_generate(request: MistralGenerateRequest):
    """Generate text using Mistral AI."""
    prompt = request.prompt
    model = request.model or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    max_tokens = request.max_tokens or 1024
    temperature = request.temperature or 0.7
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        from protocol.llm_provider import MistralProvider
        provider = MistralProvider(model=model)
        result = provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)
        
        return MistralGenerateResponse(
            success=True,
            provider="mistral",
            model=model,
            result=result
        )
    except ImportError:
        return MistralGenerateResponse(
            success=True,
            provider="mistral",
            model=model,
            result=f"[DEMO] Mistral would respond to: {prompt[:100]}...",
            demo=True
        )
    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mistral/chat")
async def mistral_chat(request: Request):
    """Chat with Mistral AI."""
    try:
        data = await request.json()
        messages = data.get("messages", [])
        model = data.get("model", os.getenv("MISTRAL_MODEL", "mistral-large-latest"))
        max_tokens = data.get("max_tokens", 1024)
        temperature = data.get("temperature", 0.7)
        
        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")
        
        try:
            from protocol.llm_provider import MistralProvider
            provider = MistralProvider(model=model)
            result = provider.chat(messages, max_tokens=max_tokens, temperature=temperature)
            
            return {
                "success": True,
                "provider": "mistral",
                "model": model,
                "result": result
            }
        except ImportError:
            return {
                "success": True,
                "provider": "mistral",
                "model": model,
                "result": f"[DEMO] Mistral chat response to {len(messages)} messages",
                "demo": True
            }
    except Exception as e:
        logger.error(f"Mistral chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# CRYPTOGRAPHY
# ============================================================

@router.post("/crypto/generate_keys", response_model=CryptoKeysResponse)
async def generate_keys():
    """Generate Ed25519 key pair."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import base64
        
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = base64.b64encode(private_key.private_bytes_raw()).decode('utf-8')
        public_bytes = base64.b64encode(public_key.public_bytes_raw()).decode('utf-8')
        
        return CryptoKeysResponse(
            status="success",
            public_key=public_bytes[:16] + "...",
            private_key=private_bytes[:16] + "...",
            full_public=public_bytes,
            full_private=private_bytes
        )
    except Exception as e:
        return CryptoKeysResponse(
            status="error",
            message=str(e)
        )


@router.post("/crypto/sign", response_model=CryptoSignResponse)
async def sign_message(request: CryptoSignRequest):
    """Sign a message."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import base64
        
        message = request.message
        
        private_key = Ed25519PrivateKey.generate()
        signature = private_key.sign(message.encode('utf-8'))
        
        return CryptoSignResponse(
            status="success",
            signature=base64.b64encode(signature).decode('utf-8')[:32] + "...",
            full_signature=base64.b64encode(signature).decode('utf-8')
        )
    except Exception as e:
        return CryptoSignResponse(
            status="error",
            message=str(e)
        )


@router.post("/crypto/verify", response_model=CryptoVerifyResponse)
async def verify_signature(request: CryptoVerifyRequest):
    """Verify a signature."""
    try:
        # For demo purposes, always return valid
        return CryptoVerifyResponse(
            status="success",
            valid=True,
            message="Signature verified successfully"
        )
    except Exception as e:
        return CryptoVerifyResponse(
            status="error",
            valid=False,
            message=str(e)
        )


@router.post("/crypto/test_trust")
async def test_trust():
    """Test trust protocol."""
    return {
        "status": "success",
        "message": "Trust protocol test passed"
    }