"""Vireo Identity v3.1."""

from .did import (
    make_did,
    resolve_public_key,
    register_did,
    get_did_document,
    list_dids,
    DID_REGISTRY,
)
from .key_manager import KeyManager
from .trust_bootstrap import TrustBootstrap
from .reputation import Reputation

__all__ = [
    "make_did", "resolve_public_key", "register_did",
    "get_did_document", "list_dids", "DID_REGISTRY",
    "KeyManager", "TrustBootstrap", "Reputation",
]