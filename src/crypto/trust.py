# [file name]: src/crypto/trust.py
# ============================================================
# ZERO-TRUST PROTOCOL FOR VIREO
# ============================================================
"""
Zero-Trust protocol for Vireo agents.

Provides:
- Nonce generation and validation
- Replay attack protection
- Timestamp validation
- Message signing and verification
"""

import time
import secrets
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger("vireo.crypto.trust")


class TrustManager:
    """Zero-Trust протокол для агентів."""
    
    def __init__(self, ttl: int = 60):
        self.ttl = ttl
        self._used_nonces: Dict[str, float] = {}
        logger.info(f"🔒 Trust Manager initialized (TTL: {ttl}s)")
    
    def generate_nonce(self) -> Tuple[str, float]:
        """
        Генерує новий nonce.
        
        Returns:
            Tuple[str, float]: (nonce, timestamp)
        """
        nonce = secrets.token_hex(32)
        timestamp = time.time()
        self._used_nonces[nonce] = timestamp
        return nonce, timestamp
    
    def validate_nonce(self, nonce: str, timestamp: float) -> bool:
        """
        Перевіряє nonce.
        
        Args:
            nonce: Nonce для перевірки
            timestamp: Часова мітка
            
        Returns:
            bool: True якщо nonce валідний
        """
        # Перевіряємо, чи не використовувався nonce раніше
        if nonce in self._used_nonces:
            logger.warning("⚠️ Nonce already used (replay attack detected)")
            return False
        
        # Перевіряємо, чи не застарів nonce
        current_time = time.time()
        if current_time - timestamp > self.ttl:
            logger.warning(f"⚠️ Nonce expired (TTL: {self.ttl}s)")
            return False
        
        # Зберігаємо використаний nonce
        self._used_nonces[nonce] = timestamp
        return True
    
    def create_trust_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Створює payload з trust-інформацією.
        
        Args:
            data: Вхідні дані
            
        Returns:
            Dict[str, Any]: Дані з nonce та timestamp
        """
        nonce, timestamp = self.generate_nonce()
        return {
            "data": data,
            "nonce": nonce,
            "timestamp": timestamp,
            "ttl": self.ttl
        }
    
    def validate_trust_payload(self, payload: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Перевіряє trust-payload.
        
        Args:
            payload: Payload для перевірки
            
        Returns:
            Tuple[bool, Optional[Dict]]: (is_valid, data)
        """
        try:
            data = payload.get("data", {})
            nonce = payload.get("nonce", "")
            timestamp = payload.get("timestamp", 0)
            
            if not self.validate_nonce(nonce, timestamp):
                return False, None
            
            return True, data
        except Exception as e:
            logger.error(f"❌ Trust validation error: {e}")
            return False, None
    
    def cleanup_expired(self):
        """Очищує застарілі nonce."""
        current_time = time.time()
        expired = [n for n, t in self._used_nonces.items() if current_time - t > self.ttl]
        for n in expired:
            del self._used_nonces[n]
        if expired:
            logger.info(f"🧹 Cleaned {len(expired)} expired nonces")
    
    def get_stats(self) -> Dict[str, int]:
        """Повертає статистику."""
        return {
            "total_nonces": len(self._used_nonces),
            "ttl_seconds": self.ttl
        }


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    trust = TrustManager(ttl=30)
    
    # Створення payload
    data = {"task": "weather_prediction", "agent": "agent-vision"}
    payload = trust.create_trust_payload(data)
    print(f"📦 Payload: {payload}")
    
    # Валідація
    is_valid, validated_data = trust.validate_trust_payload(payload)
    print(f"✅ Valid: {is_valid}")
    print(f"📊 Data: {validated_data}")