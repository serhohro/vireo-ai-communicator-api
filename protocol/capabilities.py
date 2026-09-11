"""Vireo Capabilities v3.1."""

from dataclasses import dataclass


@dataclass
class Capability:
    name: str
    version: str = "1.0"
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
        }