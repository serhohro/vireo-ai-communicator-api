# ============================================================
# LAYER 3 — AI PROTOCOL: DIALOGUE STATE MACHINE
# ============================================================

from __future__ import annotations

import time
import threading
import logging
from enum import Enum
from typing import Dict, Optional, Set, Callable, List, Tuple

logger = logging.getLogger("vireo.protocol.state")


class DialogueState(str, Enum):
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    NEGOTIATING = "NEGOTIATING"  # 🆕 Для багатораундових переговорів
    COMMITTED = "COMMITTED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"  # 🆕 Стан верифікації результату
    DONE = "DONE"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"  # 🆕 Для диспутів


# Термінальні стани (з них немає виходу)
_TERMINAL_STATES = {
    DialogueState.DONE,
    DialogueState.FAILED,
    DialogueState.TIMEOUT,
    DialogueState.REJECTED,
    DialogueState.CANCELLED,
    DialogueState.ESCALATED,
}


_TRANSITIONS: Dict[DialogueState, Set[DialogueState]] = {
    DialogueState.NEW: {DialogueState.PROPOSED, DialogueState.CANCELLED},
    
    DialogueState.PROPOSED: {
        DialogueState.NEGOTIATING,
        DialogueState.COMMITTED,
        DialogueState.REJECTED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    
    DialogueState.NEGOTIATING: {
        DialogueState.PROPOSED,  # Повернення до пропозиції
        DialogueState.COMMITTED,
        DialogueState.REJECTED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    
    DialogueState.COMMITTED: {
        DialogueState.RUNNING,
        DialogueState.CANCELLED,
        DialogueState.TIMEOUT,
    },
    
    DialogueState.RUNNING: {
        DialogueState.VERIFYING,  # 🆕 Замість DONE
        DialogueState.FAILED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    
    DialogueState.VERIFYING: {  # 🆕 Новий стан
        DialogueState.DONE,
        DialogueState.ESCALATED,
        DialogueState.FAILED,
        DialogueState.TIMEOUT,
    },
    
    DialogueState.DONE: set(),
    DialogueState.FAILED: set(),
    DialogueState.TIMEOUT: set(),
    DialogueState.REJECTED: set(),
    DialogueState.CANCELLED: set(),
    DialogueState.ESCALATED: set(),  # 🆕 Термінальний
}


class InvalidTransition(Exception):
    pass


class DialogueStateMachine:
    """Стан машина для відстеження діалогів між агентами."""
    
    def __init__(self, timeout_check_interval: float = 1.0):
        self._states: Dict[str, DialogueState] = {}
        self._timeouts: Dict[str, float] = {}  # conversation_id -> deadline (Unix timestamp)
        self._timeout_callbacks: Dict[str, List[Callable[[str], None]]] = {}  # callbacks для таймаутів
        self._history: Dict[str, List[Tuple[float, DialogueState, DialogueState]]] = {}  # 🆕 Історія переходів
        self._lock = threading.Lock()
        self._running = False
        self._check_thread: Optional[threading.Thread] = None
        self._check_interval = timeout_check_interval
    
    def start(self) -> None:
        """Запускає фоновий потік для перевірки таймаутів."""
        if self._running:
            return
        
        self._running = True
        self._check_thread = threading.Thread(target=self._timeout_loop, daemon=True)
        self._check_thread.start()
        logger.info("🔄 State machine timeout checker started")
    
    def stop(self) -> None:
        """Зупиняє фоновий потік перевірки таймаутів."""
        self._running = False
        if self._check_thread:
            self._check_thread.join(timeout=2.0)
            self._check_thread = None
        logger.info("🛑 State machine timeout checker stopped")
    
    def _timeout_loop(self) -> None:
        """Основний цикл перевірки таймаутів."""
        while self._running:
            self._check_timeouts()
            time.sleep(self._check_interval)
    
    def _check_timeouts(self) -> List[str]:
        """
        Перевіряє прострочені таймаути і автоматично переводить їх у TIMEOUT.
        
        Returns:
            List[str]: Список conversation_id, які були переведені у TIMEOUT.
        """
        expired = []
        now = time.time()
        
        with self._lock:
            for conv_id, deadline in list(self._timeouts.items()):
                current_state = self._states.get(conv_id, DialogueState.NEW)
                
                # Перевіряємо тільки якщо стан не термінальний
                if current_state not in _TERMINAL_STATES and now > deadline:
                    # Переходимо в TIMEOUT
                    try:
                        self._states[conv_id] = DialogueState.TIMEOUT
                        self._history.setdefault(conv_id, []).append(
                            (now, current_state, DialogueState.TIMEOUT)
                        )
                        expired.append(conv_id)
                        logger.info(f"⏰ [{conv_id}] Timed out from {current_state.value}")
                        
                        # Викликаємо callbacks для таймауту
                        callbacks = self._timeout_callbacks.get(conv_id, [])
                        for callback in callbacks:
                            try:
                                callback(conv_id)
                            except Exception as e:
                                logger.error(f"Timeout callback error: {e}")
                        
                        # Видаляємо таймаут після обробки
                        del self._timeouts[conv_id]
                    except Exception as e:
                        logger.error(f"Error processing timeout for {conv_id}: {e}")
        
        return expired
    
    def set_timeout(self, conversation_id: str, timeout_sec: float, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Встановлює таймаут для розмови.
        
        Args:
            conversation_id: ID розмови
            timeout_sec: Час у секундах до таймауту
            callback: Функція, яка викликається при таймауті
        """
        deadline = time.time() + timeout_sec
        with self._lock:
            self._timeouts[conversation_id] = deadline
            if callback:
                self._timeout_callbacks.setdefault(conversation_id, []).append(callback)
            logger.debug(f"⏱️ [{conversation_id}] Timeout set to {timeout_sec}s (deadline: {deadline})")
    
    def get_timeout(self, conversation_id: str) -> Optional[float]:
        """Отримує дедлайн таймауту для розмови."""
        return self._timeouts.get(conversation_id)
    
    def clear_timeout(self, conversation_id: str) -> None:
        """Очищує таймаут для розмови."""
        with self._lock:
            if conversation_id in self._timeouts:
                del self._timeouts[conversation_id]
            if conversation_id in self._timeout_callbacks:
                del self._timeout_callbacks[conversation_id]
            logger.debug(f"⏱️ [{conversation_id}] Timeout cleared")
    
    def get(self, conversation_id: str) -> DialogueState:
        """Отримує поточний стан розмови."""
        return self._states.get(conversation_id, DialogueState.NEW)
    
    def transition(self, conversation_id: str, to_state: DialogueState) -> DialogueState:
        """
        Виконує перехід між станами.
        
        Args:
            conversation_id: ID розмови
            to_state: Новий стан
            
        Returns:
            Новий стан
            
        Raises:
            InvalidTransition: Якщо перехід не дозволений
        """
        with self._lock:
            current = self.get(conversation_id)
            
            if current == to_state:
                return current
            
            allowed = _TRANSITIONS.get(current, set())
            if to_state not in allowed:
                raise InvalidTransition(
                    f"[{conversation_id}] cannot go {current.value} -> {to_state.value}"
                )
            
            # Зберігаємо історію
            self._history.setdefault(conversation_id, []).append(
                (time.time(), current, to_state)
            )
            
            self._states[conversation_id] = to_state
            logger.debug(f"[{conversation_id}] {current.value} → {to_state.value}")
            
            # Якщо перейшли в термінальний стан, очищуємо таймаут
            if to_state in _TERMINAL_STATES:
                self.clear_timeout(conversation_id)
            
            return to_state
    
    def is_terminal(self, conversation_id: str) -> bool:
        """Перевіряє, чи є стан термінальним."""
        return self.get(conversation_id) in _TERMINAL_STATES
    
    def is_active(self, conversation_id: str) -> bool:
        """Перевіряє, чи є розмова активною (не термінальною)."""
        return not self.is_terminal(conversation_id)
    
    def get_history(self, conversation_id: str) -> List[Tuple[float, DialogueState, DialogueState]]:
        """Отримує історію переходів для розмови."""
        return self._history.get(conversation_id, [])
    
    def list_conversations(self) -> Dict[str, DialogueState]:
        """Отримує список всіх розмов з їх станами."""
        with self._lock:
            return dict(self._states)
    
    def get_timeouts(self) -> Dict[str, float]:
        """Отримує список всіх активних таймаутів."""
        with self._lock:
            return dict(self._timeouts)
    
    def get_terminals(self) -> List[str]:
        """Отримує список розмов у термінальному стані."""
        with self._lock:
            return [cid for cid, state in self._states.items() if state in _TERMINAL_STATES]
    
    def reset_conversation(self, conversation_id: str) -> None:
        """Скидає стан розмови до NEW."""
        with self._lock:
            self._states[conversation_id] = DialogueState.NEW
            self.clear_timeout(conversation_id)
            logger.debug(f"[{conversation_id}] Reset to NEW")


# ============================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================

def is_valid_transition(from_state: DialogueState, to_state: DialogueState) -> bool:
    """Перевіряє, чи дозволений перехід між станами."""
    return to_state in _TRANSITIONS.get(from_state, set())


def get_allowed_transitions(state: DialogueState) -> Set[DialogueState]:
    """Отримує список дозволених переходів зі стану."""
    return _TRANSITIONS.get(state, set())


def is_terminal_state(state: DialogueState) -> bool:
    """Перевіряє, чи є стан термінальним."""
    return state in _TERMINAL_STATES


def get_state_description(state: DialogueState) -> str:
    """Отримує опис стану."""
    descriptions = {
        DialogueState.NEW: "Новий діалог",
        DialogueState.PROPOSED: "Пропозиція зроблена",
        DialogueState.NEGOTIATING: "Тривають переговори",
        DialogueState.COMMITTED: "Угода досягнута",
        DialogueState.RUNNING: "Виконання триває",
        DialogueState.VERIFYING: "Верифікація результату",
        DialogueState.DONE: "Завершено успішно",
        DialogueState.FAILED: "Помилка виконання",
        DialogueState.TIMEOUT: "Час вичерпано",
        DialogueState.REJECTED: "Відхилено",
        DialogueState.CANCELLED: "Скасовано",
        DialogueState.ESCALATED: "Передано на вирішення",
    }
    return descriptions.get(state, state.value)
