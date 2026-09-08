# api/routes.py
"""Vireo API routes."""

import json
from flask import Blueprint, request, jsonify
from .auth import AuthManager, require_auth, require_api_key, get_auth_manager

# Create blueprint
router = Blueprint('api', __name__, url_prefix='/api')

# Auth manager
_auth_manager = None

def get_auth_manager():
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# ============================================================
# AUTH ENDPOINTS
# ============================================================

@router.route('/auth/api-key', methods=['POST'])
def create_api_key():
    """Create a new API key."""
    data = request.get_json() or {}
    agent_id = data.get('agent_id')
    did = data.get('did', '')
    
    if not agent_id:
        return jsonify({'error': 'agent_id required'}), 400
    
    manager = get_auth_manager()
    result = manager.create_api_key(agent_id, did)
    return jsonify(result)


@router.route('/auth/api-key/verify', methods=['POST'])
def verify_api_key():
    """Verify an API key."""
    data = request.get_json() or {}
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'api_key required'}), 400
    
    manager = get_auth_manager()
    result = manager.verify_api_key(api_key)
    
    if result:
        return jsonify({'valid': True, 'agent_id': result['agent_id']})
    return jsonify({'valid': False}), 401


@router.route('/auth/api-key/<agent_id>', methods=['GET'])
@require_api_key
def list_api_keys(agent_id):
    """List API keys for an agent."""
    manager = get_auth_manager()
    keys = manager.list_api_keys(agent_id)
    return jsonify({'keys': keys})


@router.route('/auth/api-key', methods=['DELETE'])
def revoke_api_key():
    """Revoke an API key."""
    data = request.get_json() or {}
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'api_key required'}), 400
    
    manager = get_auth_manager()
    success = manager.revoke_api_key(api_key)
    return jsonify({'success': success})


# ============================================================
# V3.0.0 ENDPOINTS (MOCK)
# ============================================================

@router.route('/v3/protocol/version', methods=['GET'])
def protocol_version():
    """Get protocol version."""
    return jsonify({
        'version': '3.0.0',
        'protocol': 'Open Wire v3.0.0',
        'wire_format': 'Protobuf + FlatBuffers',
        'features': [
            'binary_serialization',
            'canonical_hashing',
            'ed25519_signatures'
        ]
    })


@router.route('/v3/agent/register', methods=['POST'])
def register_agent():
    """Register an agent."""
    data = request.get_json() or {}
    agent_id = data.get('id')
    
    if not agent_id:
        return jsonify({'error': 'id required'}), 400
    
    return jsonify({
        'success': True,
        'agent': {
            'id': agent_id,
            'name': data.get('name', agent_id),
            'status': 'registered',
            'registered_at': '2026-09-06T10:30:00Z'
        }
    })


@router.route('/v3/agents', methods=['GET'])
def list_agents():
    """List all agents."""
    return jsonify({
        'success': True,
        'agents': {},
        'total': 0
    })


@router.route('/v3/agent/<agent_id>/status', methods=['GET'])
def agent_status(agent_id):
    """Get agent status."""
    return jsonify({
        'success': True,
        'agent': {
            'id': agent_id,
            'status': 'registered'
        }
    })


@router.route('/v3/propose', methods=['POST'])
def propose_contract():
    """Create a contract proposal."""
    data = request.get_json() or {}
    contract_id = data.get('contract_id', 'contract-1')
    
    return jsonify({
        'success': True,
        'contract': {
            'id': contract_id,
            'parties': data.get('parties', []),
            'terms': data.get('terms', {}),
            'status': 'proposed',
            'created_at': '2026-09-06T10:30:00Z'
        }
    })


@router.route('/v3/execute', methods=['POST'])
def execute_contract():
    """Execute a contract."""
    data = request.get_json() or {}
    contract_id = data.get('contract_id')
    
    return jsonify({
        'success': True,
        'execution_id': f'exec-{contract_id}',
        'result': {
            'status': 'executed',
            'output': 'Contract executed successfully'
        }
    })


@router.route('/v3/verify', methods=['POST'])
def verify_contract():
    """Verify a contract."""
    data = request.get_json() or {}
    contract_id = data.get('contract_id')
    
    return jsonify({
        'success': True,
        'verification_id': f'ver-{contract_id}',
        'verified': True
    })


@router.route('/v3/did/create', methods=['POST'])
def create_did():
    """Create a DID."""
    data = request.get_json() or {}
    name = data.get('name', 'agent')
    
    return jsonify({
        'success': True,
        'did': f'did:vireo:{name}-123',
        'public_key': 'mock_public_key_12345',
        'created_at': '2026-09-06T10:30:00Z'
    })


@router.route('/v3/did/verify', methods=['POST'])
def verify_did():
    """Verify a DID."""
    data = request.get_json() or {}
    did = data.get('did')
    
    return jsonify({
        'success': True,
        'did': did,
        'verified': True
    })


@router.route('/v3/metrics', methods=['GET'])
def get_metrics():
    """Get metrics."""
    return jsonify({
        'success': True,
        'agents': 0,
        'contracts': 0,
        'version': '3.0.0',
        'uptime': '0h 0m 0s'
    })


@router.route('/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({
        'status': 'healthy',
        'version': '3.0.0',
        'protocol': 'Open Wire v3.0.0'
    })