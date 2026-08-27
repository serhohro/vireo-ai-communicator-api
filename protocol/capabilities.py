"""
Layer 3 — AI Protocol: Capability discovery
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Capability:
    name: str
    description: str = ""
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}

    def register(self, name: str, description: str = "", input_schema: dict = None, output_schema: dict = None):
        capability = Capability(
            name=name,
            description=description,
            input_schema=input_schema or {},
            output_schema=output_schema or {}
        )
        self._capabilities[name] = capability

    def has(self, name: str) -> bool:
        return name in self._capabilities

    def get(self, name: str) -> Optional[Capability]:
        return self._capabilities.get(name)

    def list(self) -> List[dict]:
        return [c.to_dict() for c in self._capabilities.values()]