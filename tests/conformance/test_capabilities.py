#!/usr/bin/env python3
"""
Conformance Tests: Capabilities

Tests for agent capability management.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocol.capabilities import (
    Capability, CapabilityType, CapabilityRegistry, CapabilityManager
)


class TestCapability:
    """Capability conformance tests."""
    
    def test_capability_creation(self):
        """Test capability creation."""
        cap = Capability(
            name="text-generation",
            type="ml",
            description="Generate text using AI",
            version="1.0.0"
        )
        
        assert cap.name == "text-generation"
        assert cap.type == "ml"
        assert cap.description == "Generate text using AI"
        assert cap.version == "1.0.0"
        
    def test_capability_from_type(self):
        """Test capability creation from enum."""
        cap = Capability.create(
            name="code-analysis",
            type=CapabilityType.CODE_ANALYSIS,
            description="Analyze code for issues"
        )
        
        assert cap.name == "code-analysis"
        assert cap.type == CapabilityType.CODE_ANALYSIS.value
        
    def test_capability_serialization(self):
        """Test capability serialization."""
        cap = Capability(
            name="data-analysis",
            type="ml",
            description="Analyze data",
            config={"method": "statistical"}
        )
        
        data = cap.to_dict()
        assert data["name"] == "data-analysis"
        assert data["type"] == "ml"
        assert data["config"]["method"] == "statistical"
        
        restored = Capability.from_dict(data)
        assert restored.name == cap.name
        assert restored.type == cap.type
        assert restored.config == cap.config


class TestCapabilityRegistry:
    """Capability registry conformance tests."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = CapabilityRegistry()
        assert registry is not None
        assert len(registry.list_capabilities()) == 0
        
    def test_register_capability(self):
        """Test registering a capability."""
        registry = CapabilityRegistry()
        
        cap = Capability("test", "test")
        registry.register_capability("agent1", cap)
        
        assert len(registry.list_capabilities()) == 1
        assert "test" in registry.list_capabilities()
        
    def test_get_agent_capabilities(self):
        """Test getting agent capabilities."""
        registry = CapabilityRegistry()
        
        cap1 = Capability("cap1", "test")
        cap2 = Capability("cap2", "test")
        
        registry.register_capability("agent1", cap1)
        registry.register_capability("agent1", cap2)
        registry.register_capability("agent2", cap1)
        
        caps = registry.get_agent_capabilities("agent1")
        assert len(caps) == 2
        assert caps[0].name == "cap1"
        assert caps[1].name == "cap2"
        
    def test_get_agents_with_capability(self):
        """Test getting agents with capability."""
        registry = CapabilityRegistry()
        
        cap = Capability("shared", "test")
        
        registry.register_capability("agent1", cap)
        registry.register_capability("agent2", cap)
        registry.register_capability("agent3", Capability("other", "test"))
        
        agents = registry.get_agents_with_capability("shared")
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents
        
    def test_unregister_capability(self):
        """Test unregistering a capability."""
        registry = CapabilityRegistry()
        
        cap = Capability("test", "test")
        registry.register_capability("agent1", cap)
        
        assert len(registry.list_capabilities()) == 1
        
        registry.unregister_capability("agent1", "test")
        assert len(registry.list_capabilities()) == 0
        
    def test_find_agents_by_capabilities(self):
        """Test finding agents by required capabilities."""
        registry = CapabilityRegistry()
        
        registry.register_capability("agent1", Capability("ml", "test"))
        registry.register_capability("agent1", Capability("data", "test"))
        registry.register_capability("agent2", Capability("ml", "test"))
        registry.register_capability("agent3", Capability("nlp", "test"))
        
        results = registry.find_agents_by_capabilities(
            required_capabilities=["ml"],
            min_match=1
        )
        
        assert len(results) == 2
        assert results[0]["agent_id"] == "agent1" or results[0]["agent_id"] == "agent2"
        
    def test_find_agents_with_optional(self):
        """Test finding agents with optional capabilities."""
        registry = CapabilityRegistry()
        
        registry.register_capability("agent1", Capability("ml", "test"))
        registry.register_capability("agent1", Capability("data", "test"))
        registry.register_capability("agent2", Capability("ml", "test"))
        
        results = registry.find_agents_by_capabilities(
            required_capabilities=["ml"],
            optional_capabilities=["data"]
        )
        
        assert len(results) == 2
        # agent1 should have higher score
        assert results[0]["agent_id"] == "agent1"
        assert results[0]["score"] > results[1]["score"]


class TestCapabilityManager:
    """Capability manager conformance tests."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = CapabilityManager()
        assert manager is not None
        
    def test_manager_register(self):
        """Test registering via manager."""
        manager = CapabilityManager()
        
        manager.register("agent1", Capability("test", "test"))
        caps = manager.get_capabilities("agent1")
        assert len(caps) == 1
        
    def test_manager_find_match(self):
        """Test finding matches via manager."""
        manager = CapabilityManager()
        
        manager.register("agent1", Capability("ml", "test"))
        manager.register("agent2", Capability("ml", "test"))
        manager.register("agent3", Capability("nlp", "test"))
        
        results = manager.find_match(
            agent_id="agent1",
            required_capabilities=["ml"]
        )
        
        # Should not include self
        assert len(results) == 1
        assert results[0]["agent_id"] == "agent2"
        
    def test_manager_negotiate(self):
        """Test negotiation via manager."""
        manager = CapabilityManager()
        
        manager.register("provider", Capability("ml", "test"))
        manager.register("provider", Capability("data", "test"))
        
        result = manager.negotiate_capabilities(
            requester_id="requester",
            provider_id="provider",
            required_capabilities=["ml"]
        )
        
        assert result["status"] == "pending"
        assert "negotiation_id" in result