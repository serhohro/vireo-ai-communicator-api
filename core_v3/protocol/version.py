"""
Version Management

Protocol version management and compatibility.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set, Tuple

from ..errors import VireoVersionError


@dataclass
class VersionInfo:
    """Version information."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise VireoVersionError("Version components must be non-negative")
    
    @classmethod
    def parse(cls, version_str: str) -> VersionInfo:
        """Parse version string to VersionInfo."""
        # Semver pattern
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
        match = re.match(pattern, version_str)
        if not match:
            raise VireoVersionError(f"Invalid version string: {version_str}")
        
        major, minor, patch, prerelease, build = match.groups()
        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build=build,
        )
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VersionInfo):
            return False
        return (self.major == other.major and
                self.minor == other.minor and
                self.patch == other.patch and
                self.prerelease == other.prerelease and
                self.build == other.build)
    
    def __lt__(self, other: VersionInfo) -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        
        # Handle prerelease
        if self.prerelease and not other.prerelease:
            return True
        if not self.prerelease and other.prerelease:
            return False
        if self.prerelease and other.prerelease:
            return self.prerelease < other.prerelease
        
        return False
    
    def __le__(self, other: VersionInfo) -> bool:
        return self == other or self < other
    
    def __gt__(self, other: VersionInfo) -> bool:
        return other < self
    
    def __ge__(self, other: VersionInfo) -> bool:
        return self == other or self > other
    
    def is_compatible_with(self, other: VersionInfo) -> bool:
        """Check if versions are compatible (same major)."""
        return self.major == other.major
    
    def is_fully_compatible(self, other: VersionInfo) -> bool:
        """Check if versions are fully compatible (same major and minor)."""
        return self.major == other.major and self.minor == other.minor


@dataclass
class VersionConstraint:
    """Version constraint for compatibility."""
    min_version: VersionInfo
    max_version: Optional[VersionInfo] = None
    exact_version: Optional[VersionInfo] = None
    allowed_prerelease: bool = False
    
    def satisfies(self, version: VersionInfo) -> bool:
        """Check if version satisfies the constraint."""
        if self.exact_version:
            return version == self.exact_version
        
        if version < self.min_version:
            return False
        
        if self.max_version and version > self.max_version:
            return False
        
        if not self.allowed_prerelease and version.prerelease:
            return False
        
        return True
    
    @classmethod
    def from_string(cls, constraint_str: str) -> VersionConstraint:
        """Parse constraint string."""
        constraint_str = constraint_str.strip()
        
        # Exact version
        if constraint_str.startswith('== '):
            version_str = constraint_str[3:].strip()
            return cls(
                min_version=VersionInfo.parse(version_str),
                exact_version=VersionInfo.parse(version_str),
            )
        
        # Range: >=1.0.0 <2.0.0
        if '>=' in constraint_str or '>' in constraint_str or '<=' in constraint_str or '<' in constraint_str:
            # Simple range parsing
            parts = constraint_str.split(' ')
            min_v = None
            max_v = None
            
            for part in parts:
                if part.startswith('>='):
                    min_v = VersionInfo.parse(part[2:])
                elif part.startswith('>'):
                    min_v = VersionInfo.parse(part[1:])
                elif part.startswith('<='):
                    max_v = VersionInfo.parse(part[2:])
                elif part.startswith('<'):
                    max_v = VersionInfo.parse(part[1:])
            
            if min_v is None:
                min_v = VersionInfo(0, 0, 0)
            
            return cls(min_version=min_v, max_version=max_v)
        
        # Simple: >=1.0.0
        if constraint_str.startswith('>= '):
            version_str = constraint_str[3:].strip()
            return cls(min_version=VersionInfo.parse(version_str))
        
        # Default: parse as version requirement
        try:
            return cls(min_version=VersionInfo.parse(constraint_str))
        except:
            raise VireoVersionError(f"Invalid constraint: {constraint_str}")


class VersionManager:
    """
    Version manager for protocol compatibility.
    """
    
    # Protocol versions supported by this implementation
    SUPPORTED_VERSIONS = [
        VersionInfo(3, 0, 0),
        VersionInfo(3, 0, 1),
        VersionInfo(3, 0, 2),
    ]
    
    DEFAULT_VERSION = VersionInfo(3, 0, 0)
    
    def __init__(self):
        self._supported = set(self.SUPPORTED_VERSIONS)
        self._deprecated: Dict[VersionInfo, str] = {}
        self._current_version = self.DEFAULT_VERSION
    
    def is_supported(self, version: VersionInfo) -> bool:
        """Check if version is supported."""
        return version in self._supported or any(
            v.is_fully_compatible(version) and v.major == version.major
            for v in self._supported
        )
    
    def is_deprecated(self, version: VersionInfo) -> bool:
        """Check if version is deprecated."""
        return version in self._deprecated
    
    def get_deprecation_message(self, version: VersionInfo) -> Optional[str]:
        """Get deprecation message for a version."""
        return self._deprecated.get(version)
    
    def deprecate(self, version: VersionInfo, message: str) -> None:
        """Mark a version as deprecated."""
        self._deprecated[version] = message
    
    def get_supported_versions(self) -> List[VersionInfo]:
        """Get all supported versions."""
        return sorted(self._supported)
    
    def get_latest_supported(self) -> VersionInfo:
        """Get the latest supported version."""
        return max(self._supported)
    
    def get_current_version(self) -> VersionInfo:
        """Get the current protocol version."""
        return self._current_version
    
    def set_current_version(self, version: VersionInfo) -> None:
        """Set the current protocol version."""
        if not self.is_supported(version):
            raise VireoVersionError(f"Version {version} is not supported")
        self._current_version = version
    
    def negotiate_version(self, proposed: VersionInfo) -> VersionInfo:
        """
        Negotiate protocol version.
        
        Returns the highest compatible version.
        """
        if proposed in self._supported:
            return proposed
        
        # Find the highest supported version that is compatible
        for version in sorted(self._supported, reverse=True):
            if version.is_compatible_with(proposed):
                return version
        
        # No compatible version found
        raise VireoVersionError(
            f"No compatible version found for {proposed}",
            str(self.get_latest_supported()),
            str(proposed)
        )
    
    def get_version_info(self, version_str: str) -> VersionInfo:
        """Parse version string to VersionInfo."""
        return VersionInfo.parse(version_str)
    
    def add_supported_version(self, version: VersionInfo) -> None:
        """Add a supported version."""
        self._supported.add(version)
    
    def remove_supported_version(self, version: VersionInfo) -> None:
        """Remove a supported version."""
        if version in self._supported:
            self._supported.remove(version)
    
    def is_compatible(self, v1: VersionInfo, v2: VersionInfo) -> bool:
        """Check if two versions are compatible."""
        return v1.is_compatible_with(v2)
    
    def get_minimum_supported(self) -> VersionInfo:
        """Get the minimum supported version."""
        return min(self._supported) if self._supported else VersionInfo(0, 0, 0)


class VersionCompatibility:
    """Version compatibility utilities."""
    
    @staticmethod
    def check_compatibility(
        client_version: VersionInfo,
        server_version: VersionInfo,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check compatibility between client and server versions.
        
        Returns (is_compatible, message).
        """
        # Same version
        if client_version == server_version:
            return True, "Versions match exactly"
        
        # Same major version (minor differences are okay)
        if client_version.major == server_version.major:
            # Check if client version is older
            if client_version < server_version:
                # Older client, newer server
                if client_version.minor == server_version.minor:
                    return True, "Patch version difference only"
                else:
                    return True, "Minor version difference (backward compatible)"
            else:
                # Newer client, older server
                if server_version.minor == client_version.minor:
                    return True, "Patch version difference only"
                else:
                    return True, "Minor version difference (forward compatible)"
        
        # Different major versions
        return False, f"Incompatible major versions: {client_version.major} != {server_version.major}"
    
    @staticmethod
    def get_compatible_versions(
        version: VersionInfo,
        supported: List[VersionInfo],
    ) -> List[VersionInfo]:
        """Get all supported versions compatible with a given version."""
        return [v for v in supported if v.is_compatible_with(version)]
    
    @staticmethod
    def get_best_match(
        version: VersionInfo,
        supported: List[VersionInfo],
    ) -> Optional[VersionInfo]:
        """Get the best matching supported version."""
        compatible = VersionCompatibility.get_compatible_versions(version, supported)
        if not compatible:
            return None
        
        # Prefer the closest match
        if version in compatible:
            return version
        
        # Prefer the version with the same minor
        same_minor = [v for v in compatible if v.minor == version.minor]
        if same_minor:
            return max(same_minor)
        
        # Otherwise, return the latest compatible
        return max(compatible)