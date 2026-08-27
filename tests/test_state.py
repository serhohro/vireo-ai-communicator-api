# [file name]: protocol/tests/test_state.py
# ============================================================
# TESTS: STATE MACHINE (Idempotency, Timeouts)
# Тести для машини станів (ідемпотентність, таймаути)
# ============================================================

import sys
import os
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol.state import DialogueStateMachine, DialogueState, InvalidTransition


def test_idempotent_transition():
    """Тест ідемпотентності переходів станів."""
    sm = DialogueStateMachine()
    conv = "conv-001"
    
    # Перший перехід
    sm.transition(conv, DialogueState.PROPOSED)
    sm.transition(conv, DialogueState.COMMITTED)
    assert sm.get(conv) == DialogueState.COMMITTED
    
    # Повторний перехід в COMMITTED (ідемпотентний)
    sm.transition(conv, DialogueState.COMMITTED)
    assert sm.get(conv) == DialogueState.COMMITTED


def test_state_machine_valid_path():
    """Тест валідного шляху станів."""
    sm = DialogueStateMachine()
    conv = "conv-002"
    
    assert sm.get(conv) == DialogueState.NEW
    
    sm.transition(conv, DialogueState.PROPOSED)
    sm.transition(conv, DialogueState.COMMITTED)
    sm.transition(conv, DialogueState.RUNNING)
    sm.transition(conv, DialogueState.DONE)
    
    assert sm.get(conv) == DialogueState.DONE
    assert sm.is_terminal(conv)


def test_state_machine_rejects_invalid_transition():
    """Тест відхилення невалідних переходів."""
    sm = DialogueStateMachine()
    conv = "conv-003"
    
    # NEW → RUNNING (невалідно)
    try:
        sm.transition(conv, DialogueState.RUNNING)
        assert False, "Expected InvalidTransition"
    except InvalidTransition:
        pass


def test_timeout_transition():
    """Тест переходу по таймауту."""
    sm = DialogueStateMachine()
    conv = "conv-004"
    
    sm.transition(conv, DialogueState.PROPOSED)
    sm.transition(conv, DialogueState.COMMITTED)
    
    # Симуляція таймауту
    sm.transition(conv, DialogueState.TIMEOUT)
    assert sm.get(conv) == DialogueState.TIMEOUT
    assert sm.is_terminal(conv)


def test_rollback_transition():
    """Тест переходу по відкату."""
    sm = DialogueStateMachine()
    conv = "conv-005"
    
    sm.transition(conv, DialogueState.PROPOSED)
    sm.transition(conv, DialogueState.COMMITTED)
    sm.transition(conv, DialogueState.RUNNING)
    
    # Відкат
    sm.transition(conv, DialogueState.FAILED)
    assert sm.get(conv) == DialogueState.FAILED


def test_terminal_states():
    """Тест термінальних станів."""
    sm = DialogueStateMachine()
    conv = "conv-006"
    
    terminal_states = [
        DialogueState.DONE,
        DialogueState.FAILED,
        DialogueState.TIMEOUT,
        DialogueState.REJECTED,
        DialogueState.CANCELLED
    ]
    
    for state in terminal_states:
        sm.transition(conv, state)
        assert sm.is_terminal(conv)
        
        # З термінального стану не можна перейти
        try:
            sm.transition(conv, DialogueState.PROPOSED)
            assert False, f"Expected InvalidTransition from {state.value}"
        except InvalidTransition:
            pass
        sm = DialogueStateMachine()  # Reset


def test_get_conversations():
    """Тест отримання всіх конверсацій."""
    sm = DialogueStateMachine()
    
    sm.transition("conv-001", DialogueState.PROPOSED)
    sm.transition("conv-002", DialogueState.COMMITTED)
    sm.transition("conv-003", DialogueState.DONE)
    
    conversations = sm._states
    assert len(conversations) == 3
    assert conversations["conv-001"] == DialogueState.PROPOSED
    assert conversations["conv-002"] == DialogueState.COMMITTED
    assert conversations["conv-003"] == DialogueState.DONE


def test_multiple_conversations():
    """Тест різних конверсацій з різними станами."""
    sm = DialogueStateMachine()
    
    # Різні конверсації в різних станах
    sm.transition("conv-a", DialogueState.PROPOSED)
    sm.transition("conv-b", DialogueState.COMMITTED)
    sm.transition("conv-c", DialogueState.RUNNING)
    sm.transition("conv-d", DialogueState.DONE)
    
    assert sm.get("conv-a") == DialogueState.PROPOSED
    assert sm.get("conv-b") == DialogueState.COMMITTED
    assert sm.get("conv-c") == DialogueState.RUNNING
    assert sm.get("conv-d") == DialogueState.DONE
    
    # Перевірка, що вони незалежні
    sm.transition("conv-a", DialogueState.COMMITTED)
    assert sm.get("conv-a") == DialogueState.COMMITTED
    assert sm.get("conv-b") == DialogueState.COMMITTED
    assert sm.get("conv-c") == DialogueState.RUNNING
    assert sm.get("conv-d") == DialogueState.DONE


def test_state_persistence():
    """Тест збереження стану."""
    sm = DialogueStateMachine()
    conv = "conv-007"
    
    assert sm.get(conv) == DialogueState.NEW
    
    states = [
        DialogueState.PROPOSED,
        DialogueState.COMMITTED,
        DialogueState.RUNNING,
        DialogueState.DONE
    ]
    
    for state in states:
        sm.transition(conv, state)
        assert sm.get(conv) == state


if __name__ == "__main__":
    test_idempotent_transition()
    test_state_machine_valid_path()
    test_state_machine_rejects_invalid_transition()
    test_timeout_transition()
    test_rollback_transition()
    test_terminal_states()
    test_get_conversations()
    test_multiple_conversations()
    test_state_persistence()
    print("\n✅ All state machine tests passed!")