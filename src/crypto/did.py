# [file name]: src/crypto/did.py
# ============================================================
# W3C DECENTRALIZED IDENTIFIERS (DID)
# ============================================================
"""
W3C Decentralized Identifiers for Vireo.

Provides:
- DID generation and management
- DID document creation
- DID verification
"""

import json
import uuid
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("vireo.crypto.did")


class DIDManager:
    """Управління W3C DID."""
    
    def __init__(self, did: Optional[str] = None):
        self.did = did or self._generate_did()
        self.documents: Dict[str, Dict[str, Any]] = {}
        logger.info(f"🔑 DID Manager initialized: {self.did}")
    
    def _generate_did(self) -> str:
        """Генерує новий DID."""
        return f"did:key:{uuid.uuid4().hex}"
    
    def create_did_document(self, public_key: str, service_endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Створює DID документ.
        
        Args:
            public_key: Публічний ключ (multibase encoded)
            service_endpoint: URL сервісу (опціонально)
            
        Returns:
            Dict[str, Any]: DID документ
        """
        doc = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": self.did,
            "verificationMethod": [{
                "id": f"{self.did}#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": self.did,
                "publicKeyMultibase": public_key
            }],
            "authentication": [f"{self.did}#keys-1"],
            "assertionMethod": [f"{self.did}#keys-1"]
        }
        
        if service_endpoint:
            doc["service"] = [{
                "id": f"{self.did}#service-1",
                "type": "VireoAgent",
                "serviceEndpoint": service_endpoint
            }]
        
        self.documents[self.did] = doc
        logger.info(f"📄 DID document created for: {self.did}")
        return doc
    
    def verify_did(self, did: str, document: Dict[str, Any]) -> bool:
        """
        Перевіряє DID документ.
        
        Args:
            did: DID для перевірки
            document: DID документ
            
        Returns:
            bool: True якщо валідний
        """
        if document.get("id") != did:
            logger.warning(f"❌ DID mismatch: {document.get('id')} != {did}")
            return False
        return True
    
    def resolve_did(self, did: str) -> Optional[Dict[str, Any]]:
        """Отримує DID документ за ідентифікатором."""
        return self.documents.get(did)
    
    def to_json(self, document: Dict[str, Any]) -> str:
        """Конвертує документ в JSON."""
        return json.dumps(document, indent=2)
    
    def from_json(self, json_str: str) -> Dict[str, Any]:
        """Парсить JSON в документ."""
        return json.loads(json_str)
    
    def sign_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Додає підпис до документа."""
        # TODO: Реалізація підпису
        document["proof"] = {
            "type": "Ed25519Signature2020",
            "created": "2024-01-01T00:00:00Z",
            "verificationMethod": f"{self.did}#keys-1"
        }
        return document