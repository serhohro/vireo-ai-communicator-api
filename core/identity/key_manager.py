"""
Key Manager — управління ключами та їх ротація
"""

import time
import base64
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.exceptions import InvalidSignature
import logging

logger = logging.getLogger(__name__)


@dataclass
class KeyRecord:
    """Запис про ключ агента."""
    public_key_hex: str
    created_at: float
    active: bool = True
    previous_key: Optional[str] = None
    revoked_at: Optional[float] = None


class KeyManager:
    """
    Управління ключами агентів.
    
    Підтримує:
    - Генерацію ключів
    - Ротацію ключів
    - Відкликання ключів
    - Історію ключів
    """
    
    def __init__(self):
        self._keys: Dict[str, KeyRecord] = {}  # agent_id → KeyRecord
        self._history: Dict[str, List[KeyRecord]] = {}  # agent_id → history
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self._public_key_hex = self._public_key.public_bytes_raw().hex()
    
    def register_key(self, agent_id: str, public_key_hex: str) -> bool:
        """
        Реєструє ключ агента.
        
        Args:
            agent_id: ID агента
            public_key_hex: Публічний ключ у hex (64 символи)
        
        Returns:
            True якщо реєстрація успішна
        """
        # Валідація ключа
        if not self._validate_public_key(public_key_hex):
            logger.error(f"Invalid public key for {agent_id}")
            return False
        
        # Перевіряємо, чи агент вже існує
        if agent_id in self._keys:
            logger.warning(f"Agent {agent_id} already registered")
            return False
        
        # Створюємо запис
        record = KeyRecord(
            public_key_hex=public_key_hex,
            created_at=time.time()
        )
        self._keys[agent_id] = record
        self._history.setdefault(agent_id, []).append(record)
        
        logger.info(f"✅ Key registered for {agent_id}")
        return True
    
    def rotate_key(self, agent_id: str, old_public_key_hex: str,
                   new_public_key_hex: str, signature_hex: str) -> bool:
        """
        Ротація ключа.
        
        Args:
            agent_id: ID агента
            old_public_key_hex: Старий публічний ключ
            new_public_key_hex: Новий публічний ключ
            signature_hex: Підпис старого ключа (hex)
        
        Returns:
            True якщо ротація успішна
        """
        # Перевіряємо, чи існує агент
        if agent_id not in self._keys:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        record = self._keys[agent_id]
        
        # Перевіряємо старий ключ
        if record.public_key_hex != old_public_key_hex:
            logger.error(f"Old key mismatch for {agent_id}")
            return False
        
        if not record.active:
            logger.error(f"Agent {agent_id} key is revoked")
            return False
        
        # Валідація нового ключа
        if not self._validate_public_key(new_public_key_hex):
            logger.error(f"Invalid new public key for {agent_id}")
            return False
        
        # Перевіряємо підпис старого ключа
        if not self._verify_key_rotation_signature(
            agent_id, old_public_key_hex, new_public_key_hex, signature_hex
        ):
            logger.error(f"Invalid signature for key rotation for {agent_id}")
            return False
        
        # Деактивуємо старий ключ
        record.active = False
        
        # Створюємо новий запис
        new_record = KeyRecord(
            public_key_hex=new_public_key_hex,
            created_at=time.time(),
            active=True,
            previous_key=old_public_key_hex
        )
        self._keys[agent_id] = new_record
        self._history.setdefault(agent_id, []).append(new_record)
        
        logger.info(f"🔄 Key rotated for {agent_id}")
        return True
    
    def revoke_key(self, agent_id: str) -> bool:
        """
        Відкликає ключ агента.
        
        Args:
            agent_id: ID агента
        
        Returns:
            True якщо відкликання успішне
        """
        if agent_id not in self._keys:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        record = self._keys[agent_id]
        if not record.active:
            logger.warning(f"Agent {agent_id} key already revoked")
            return False
        
        record.active = False
        record.revoked_at = time.time()
        
        logger.info(f"🗑️ Key revoked for {agent_id}")
        return True
    
    def get_public_key(self, agent_id: str) -> Optional[str]:
        """
        Отримує активний публічний ключ агента.
        
        Returns:
            Публічний ключ у hex або None
        """
        record = self._keys.get(agent_id)
        if record and record.active:
            return record.public_key_hex
        return None
    
    def get_key_history(self, agent_id: str) -> List[Dict]:
        """
        Отримує історію ключів агента.
        
        Returns:
            Список записів про ключі
        """
        records = self._history.get(agent_id, [])
        return [
            {
                "public_key": r.public_key_hex,
                "created_at": r.created_at,
                "active": r.active,
                "previous_key": r.previous_key,
                "revoked_at": r.revoked_at
            }
            for r in records
        ]
    
    def is_active(self, agent_id: str) -> bool:
        """Перевіряє, чи активний ключ агента."""
        record = self._keys.get(agent_id)
        return record is not None and record.active
    
    def is_registered(self, agent_id: str) -> bool:
        """Перевіряє, чи зареєстрований агент."""
        return agent_id in self._keys
    
    def get_own_public_key_hex(self) -> str:
        """Отримує власний публічний ключ."""
        return self._public_key_hex
    
    def get_own_private_key(self) -> Ed25519PrivateKey:
        """Отримує власний приватний ключ."""
        return self._private_key
    
    def sign_with_own_key(self, message: bytes) -> str:
        """Підписує повідомлення власним ключем."""
        signature = self._private_key.sign(message)
        return signature.hex()
    
    def verify_signature(self, agent_id: str, message: bytes, 
                         signature_hex: str) -> bool:
        """
        Перевіряє підпис повідомлення.
        
        Args:
            agent_id: ID агента
            message: Повідомлення (bytes)
            signature_hex: Підпис у hex
        
        Returns:
            True якщо підпис валідний
        """
        public_key_hex = self.get_public_key(agent_id)
        if not public_key_hex:
            return False
        
        try:
            public_key_bytes = bytes.fromhex(public_key_hex)
            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature = bytes.fromhex(signature_hex)
            public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def get_all_active_keys(self) -> Dict[str, str]:
        """Отримує всі активні ключі."""
        return {
            agent_id: record.public_key_hex
            for agent_id, record in self._keys.items()
            if record.active
        }
    
    def get_all_agents(self) -> List[str]:
        """Отримує список всіх зареєстрованих агентів."""
        return list(self._keys.keys())
    
    def get_stats(self) -> Dict[str, int]:
        """Отримує статистику ключів."""
        total = len(self._keys)
        active = sum(1 for r in self._keys.values() if r.active)
        revoked = total - active
        return {
            "total": total,
            "active": active,
            "revoked": revoked
        }
    
    def _validate_public_key(self, public_key_hex: str) -> bool:
        """Валідує публічний ключ."""
        # Перевіряємо довжину (32 байти = 64 hex символи)
        if len(public_key_hex) != 64:
            return False
        
        try:
            public_key_bytes = bytes.fromhex(public_key_hex)
            Ed25519PublicKey.from_public_bytes(public_key_bytes)
            return True
        except Exception:
            return False
    
    def _verify_key_rotation_signature(self, agent_id: str, 
                                        old_key_hex: str, 
                                        new_key_hex: str, 
                                        signature_hex: str) -> bool:
        """Перевіряє підпис для ротації ключа."""
        try:
            public_key_bytes = bytes.fromhex(old_key_hex)
            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            # Повідомлення для підпису
            message = f"key_rotation:{agent_id}:{new_key_hex}".encode('utf-8')
            signature = bytes.fromhex(signature_hex)
            
            public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            logger.error(f"Rotation signature verification error: {e}")
            return False


# ============================================================
# ФАБРИКА
# ============================================================

_default_key_manager: Optional[KeyManager] = None


def get_key_manager() -> KeyManager:
    """Отримує глобальний менеджер ключів."""
    global _default_key_manager
    if _default_key_manager is None:
        _default_key_manager = KeyManager()
    return _default_key_manager


def reset_key_manager():
    """Скидає глобальний менеджер ключів."""
    global _default_key_manager
    _default_key_manager = None