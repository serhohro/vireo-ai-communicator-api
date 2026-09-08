"""
Vireo Configuration

Configuration management for Vireo core.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

import os
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from threading import Lock

from .errors import VireoConfigError


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class CryptoConfig:
    """Cryptography configuration."""
    default_algorithm: str = "Ed25519"
    default_hash: str = "BLAKE2b"
    key_rotation_days: int = 90
    min_signature_length: int = 64
    nonce_size: int = 24
    max_signature_age_seconds: int = 300


@dataclass
class ProtocolConfig:
    """Protocol configuration."""
    max_message_size: int = 1024 * 1024  # 1MB
    max_messages_per_session: int = 10000
    session_timeout_seconds: int = 3600
    idle_timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: int = 1
    max_escalation_depth: int = 5
    require_signatures: bool = True
    require_nonce: bool = True


@dataclass
class NetworkConfig:
    """Network configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    use_ssl: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    websocket_path: str = "/ws"
    grpc_port: int = 50051
    http_timeout_seconds: int = 30


@dataclass
class SandboxConfig:
    """Sandbox configuration."""
    max_execution_time_seconds: float = 30.0
    max_memory_mb: int = 512
    max_cpu_percent: int = 80
    max_file_size_mb: int = 10
    allowed_imports: List[str] = field(default_factory=lambda: [
        "math", "json", "random", "datetime", "collections"
    ])
    disallowed_functions: List[str] = field(default_factory=lambda: [
        "exec", "eval", "__import__", "compile", "open", "file", 
        "input", "raw_input", "print"
    ])
    enable_network: bool = False
    enable_filesystem: bool = False
    enable_subprocess: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True
    json_format: bool = False


@dataclass
class VireoConfig:
    """Main Vireo configuration."""
    environment: Environment = Environment.DEVELOPMENT
    version: str = "3.0.0"
    
    crypto: CryptoConfig = field(default_factory=CryptoConfig)
    protocol: ProtocolConfig = field(default_factory=ProtocolConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Additional settings
    debug: bool = False
    test_mode: bool = False
    config_path: Optional[str] = None
    
    # Extensions
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "environment": self.environment.value,
            "version": self.version,
            "debug": self.debug,
            "test_mode": self.test_mode,
            "crypto": {
                "default_algorithm": self.crypto.default_algorithm,
                "default_hash": self.crypto.default_hash,
                "key_rotation_days": self.crypto.key_rotation_days,
                "min_signature_length": self.crypto.min_signature_length,
                "nonce_size": self.crypto.nonce_size,
                "max_signature_age_seconds": self.crypto.max_signature_age_seconds,
            },
            "protocol": {
                "max_message_size": self.protocol.max_message_size,
                "max_messages_per_session": self.protocol.max_messages_per_session,
                "session_timeout_seconds": self.protocol.session_timeout_seconds,
                "idle_timeout_seconds": self.protocol.idle_timeout_seconds,
                "retry_attempts": self.protocol.retry_attempts,
                "retry_delay_seconds": self.protocol.retry_delay_seconds,
                "max_escalation_depth": self.protocol.max_escalation_depth,
                "require_signatures": self.protocol.require_signatures,
                "require_nonce": self.protocol.require_nonce,
            },
            "network": {
                "host": self.network.host,
                "port": self.network.port,
                "use_ssl": self.network.use_ssl,
                "ssl_cert_path": self.network.ssl_cert_path,
                "ssl_key_path": self.network.ssl_key_path,
                "websocket_path": self.network.websocket_path,
                "grpc_port": self.network.grpc_port,
                "http_timeout_seconds": self.network.http_timeout_seconds,
            },
            "sandbox": {
                "max_execution_time_seconds": self.sandbox.max_execution_time_seconds,
                "max_memory_mb": self.sandbox.max_memory_mb,
                "max_cpu_percent": self.sandbox.max_cpu_percent,
                "max_file_size_mb": self.sandbox.max_file_size_mb,
                "allowed_imports": self.sandbox.allowed_imports,
                "disallowed_functions": self.sandbox.disallowed_functions,
                "enable_network": self.sandbox.enable_network,
                "enable_filesystem": self.sandbox.enable_filesystem,
                "enable_subprocess": self.sandbox.enable_subprocess,
            },
            "logging": {
                "level": self.logging.level.value,
                "format": self.logging.format,
                "file": self.logging.file,
                "console": self.logging.console,
                "json_format": self.logging.json_format,
            },
            "extensions": self.extensions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VireoConfig:
        """Create config from dictionary."""
        config = cls()
        
        # Main settings
        if "environment" in data:
            config.environment = Environment(data["environment"])
        if "version" in data:
            config.version = data["version"]
        if "debug" in data:
            config.debug = data["debug"]
        if "test_mode" in data:
            config.test_mode = data["test_mode"]
        
        # Crypto settings
        if "crypto" in data:
            crypto = data["crypto"]
            config.crypto.default_algorithm = crypto.get("default_algorithm", config.crypto.default_algorithm)
            config.crypto.default_hash = crypto.get("default_hash", config.crypto.default_hash)
            config.crypto.key_rotation_days = crypto.get("key_rotation_days", config.crypto.key_rotation_days)
            config.crypto.min_signature_length = crypto.get("min_signature_length", config.crypto.min_signature_length)
            config.crypto.nonce_size = crypto.get("nonce_size", config.crypto.nonce_size)
            config.crypto.max_signature_age_seconds = crypto.get("max_signature_age_seconds", config.crypto.max_signature_age_seconds)
        
        # Protocol settings
        if "protocol" in data:
            proto = data["protocol"]
            config.protocol.max_message_size = proto.get("max_message_size", config.protocol.max_message_size)
            config.protocol.max_messages_per_session = proto.get("max_messages_per_session", config.protocol.max_messages_per_session)
            config.protocol.session_timeout_seconds = proto.get("session_timeout_seconds", config.protocol.session_timeout_seconds)
            config.protocol.idle_timeout_seconds = proto.get("idle_timeout_seconds", config.protocol.idle_timeout_seconds)
            config.protocol.retry_attempts = proto.get("retry_attempts", config.protocol.retry_attempts)
            config.protocol.retry_delay_seconds = proto.get("retry_delay_seconds", config.protocol.retry_delay_seconds)
            config.protocol.max_escalation_depth = proto.get("max_escalation_depth", config.protocol.max_escalation_depth)
            config.protocol.require_signatures = proto.get("require_signatures", config.protocol.require_signatures)
            config.protocol.require_nonce = proto.get("require_nonce", config.protocol.require_nonce)
        
        # Network settings
        if "network" in data:
            net = data["network"]
            config.network.host = net.get("host", config.network.host)
            config.network.port = net.get("port", config.network.port)
            config.network.use_ssl = net.get("use_ssl", config.network.use_ssl)
            config.network.ssl_cert_path = net.get("ssl_cert_path", config.network.ssl_cert_path)
            config.network.ssl_key_path = net.get("ssl_key_path", config.network.ssl_key_path)
            config.network.websocket_path = net.get("websocket_path", config.network.websocket_path)
            config.network.grpc_port = net.get("grpc_port", config.network.grpc_port)
            config.network.http_timeout_seconds = net.get("http_timeout_seconds", config.network.http_timeout_seconds)
        
        # Sandbox settings
        if "sandbox" in data:
            sand = data["sandbox"]
            config.sandbox.max_execution_time_seconds = sand.get("max_execution_time_seconds", config.sandbox.max_execution_time_seconds)
            config.sandbox.max_memory_mb = sand.get("max_memory_mb", config.sandbox.max_memory_mb)
            config.sandbox.max_cpu_percent = sand.get("max_cpu_percent", config.sandbox.max_cpu_percent)
            config.sandbox.max_file_size_mb = sand.get("max_file_size_mb", config.sandbox.max_file_size_mb)
            config.sandbox.allowed_imports = sand.get("allowed_imports", config.sandbox.allowed_imports)
            config.sandbox.disallowed_functions = sand.get("disallowed_functions", config.sandbox.disallowed_functions)
            config.sandbox.enable_network = sand.get("enable_network", config.sandbox.enable_network)
            config.sandbox.enable_filesystem = sand.get("enable_filesystem", config.sandbox.enable_filesystem)
            config.sandbox.enable_subprocess = sand.get("enable_subprocess", config.sandbox.enable_subprocess)
        
        # Logging settings
        if "logging" in data:
            log = data["logging"]
            config.logging.level = LogLevel(log.get("level", config.logging.level.value))
            config.logging.format = log.get("format", config.logging.format)
            config.logging.file = log.get("file", config.logging.file)
            config.logging.console = log.get("console", config.logging.console)
            config.logging.json_format = log.get("json_format", config.logging.json_format)
        
        # Extensions
        if "extensions" in data:
            config.extensions = data["extensions"]
        
        return config
    
    def to_json(self) -> str:
        """Convert config to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> VireoConfig:
        """Create config from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save(self, path: Union[str, Path]) -> None:
        """Save config to file."""
        path = Path(path)
        with open(path, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> VireoConfig:
        """Load config from file."""
        path = Path(path)
        if not path.exists():
            raise VireoConfigError(f"Config file not found: {path}")
        with open(path, 'r') as f:
            return cls.from_json(f.read())
    
    def merge(self, other: VireoConfig) -> VireoConfig:
        """Merge with another config (other takes precedence)."""
        merged = VireoConfig()
        # Copy from self
        merged.__dict__.update(self.__dict__)
        # Override with other
        for key, value in other.__dict__.items():
            if value is not None and value != getattr(self, key):
                merged.__dict__[key] = value
        return merged


# Default configuration
DEFAULT_CONFIG = VireoConfig()

# Global configuration instance
_global_config: Optional[VireoConfig] = None
_config_lock = Lock()


def get_config() -> VireoConfig:
    """Get global configuration."""
    global _global_config
    with _config_lock:
        if _global_config is None:
            # Try to load from environment or default location
            config_path = os.environ.get("VIREO_CONFIG_PATH")
            if config_path and Path(config_path).exists():
                _global_config = VireoConfig.load(config_path)
            else:
                # Try default locations
                default_paths = [
                    Path("vireo.json"),
                    Path("config/vireo.json"),
                    Path(".vireo/config.json"),
                ]
                for path in default_paths:
                    if path.exists():
                        _global_config = VireoConfig.load(path)
                        break
                else:
                    _global_config = DEFAULT_CONFIG
        return _global_config


def set_config(config: VireoConfig) -> None:
    """Set global configuration."""
    global _global_config
    with _config_lock:
        _global_config = config


def load_config(path: Union[str, Path]) -> VireoConfig:
    """Load configuration from file and set as global."""
    config = VireoConfig.load(path)
    set_config(config)
    return config


def reset_config() -> None:
    """Reset global configuration to default."""
    global _global_config
    with _config_lock:
        _global_config = DEFAULT_CONFIG


def config_from_env() -> VireoConfig:
    """Create configuration from environment variables."""
    config = VireoConfig()
    
    # Environment
    env = os.environ.get("VIREO_ENV", "development")
    config.environment = Environment(env)
    
    # Debug
    config.debug = os.environ.get("VIREO_DEBUG", "false").lower() == "true"
    config.test_mode = os.environ.get("VIREO_TEST_MODE", "false").lower() == "true"
    
    # Network
    config.network.host = os.environ.get("VIREO_HOST", config.network.host)
    config.network.port = int(os.environ.get("VIREO_PORT", config.network.port))
    config.network.use_ssl = os.environ.get("VIREO_SSL", "false").lower() == "true"
    config.network.ssl_cert_path = os.environ.get("VIREO_SSL_CERT")
    config.network.ssl_key_path = os.environ.get("VIREO_SSL_KEY")
    
    # Logging
    log_level = os.environ.get("VIREO_LOG_LEVEL", "INFO")
    config.logging.level = LogLevel(log_level)
    
    # Sandbox
    config.sandbox.max_execution_time_seconds = float(os.environ.get("VIREO_SANDBOX_TIMEOUT", config.sandbox.max_execution_time_seconds))
    config.sandbox.max_memory_mb = int(os.environ.get("VIREO_SANDBOX_MEMORY", config.sandbox.max_memory_mb))
    
    return config