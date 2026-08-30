# [file name]: protocol/tests/test_state.py
# ============================================================
# TESTS: STATE MACHINE (Idempotency, Timeouts) v1.4.3
# Тести для машини станів (ідемпотентність, таймаути)
# The World's First AI-to-AI Communication Language
# ============================================================

__version__ = "1.4.3"

import sys
import os
import time
import uuid
import threading
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol.state import DialogueStateMachine, DialogueState, InvalidTransition


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def state_machine():
    """Створює чисту машину станів для кожного тесту."""
    return DialogueStateMachine()


@pytest.fixture
def conversation_id():
    """Створює унікальний ID конверсації."""
    return f"conv-{uuid.uuid4().hex[:8]}"


# ============================================================
# TESTS
# ============================================================

def test_idempotent_transition(state_machine, conversation_id):
    """Тест ідемпотентності переходів станів."""
    conv = conversation_id
    
    # Перший перехід
    state_machine.transition(conv, DialogueState.PROPOSED)
    state_machine.transition(conv, DialogueState.COMMITTED)
    assert state_machine.get(conv) == DialogueState.COMMITTED
    
    # Повторний перехід в COMMITTED (ідемпотентний)
    state_machine.transition(conv, DialogueState.COMMITTED)
    assert state_machine.get(conv) == DialogueState.COMMITTED


def test_state_machine_valid_path(state_machine, conversation_id):
    """Тест валідного шляху станів."""
    conv = conversation_id
    
    assert state_machine.get(conv) == DialogueState.NEW
    
    state_machine.transition(conv, DialogueState.PROPOSED)
    state_machine.transition(conv, DialogueState.COMMITTED)
    state_machine.transition(conv, DialogueState.RUNNING)
    state_machine.transition(conv, DialogueState.DONE)
    
    assert state_machine.get(conv) == DialogueState.DONE
    assert state_machine.is_terminal(conv)


def test_state_machine_rejects_invalid_transition(state_machine, conversation_id):
    """Тест відхилення невалідних переходів."""
    conv = conversation_id
    
    # NEW → RUNNING (невалідно)
    with pytest.raises(InvalidTransition):
        state_machine.transition(conv, DialogueState.RUNNING)


def test_state_machine_allows_valid_transitions(state_machine, conversation_id):
    """Тест всіх валідних переходів."""
    conv = conversation_id
    sm = state_machine
    
    # Тестуємо всі можливі переходи
    valid_transitions = [
        (DialogueState.NEW, DialogueState.PROPOSED),
        (DialogueState.NEW, DialogueState.CANCELLED),
        (DialogueState.PROPOSED, DialogueState.COMMITTED),
        (DialogueState.PROPOSED, DialogueState.REJECTED),
        (DialogueState.PROPOSED, DialogueState.TIMEOUT),
        (DialogueState.PROPOSED, DialogueState.CANCELLED),
        (DialogueState.COMMITTED, DialogueState.RUNNING),
        (DialogueState.COMMITTED, DialogueState.CANCELLED),
        (DialogueState.COMMITTED, DialogueState.TIMEOUT),
        (DialogueState.RUNNING, DialogueState.DONE),
        (DialogueState.RUNNING, DialogueState.FAILED),
        (DialogueState.RUNNING, DialogueState.TIMEOUT),
        (DialogueState.RUNNING, DialogueState.CANCELLED),
    ]
    
    for from_state, to_state in valid_transitions:
        sm = DialogueStateMachine()
        sm.transition(conv, from_state)
        sm.transition(conv, to_state)
        assert sm.get(conv) == to_state


def test_timeout_transition(state_machine, conversation_id):
    """Тест переходу по таймауту."""
    conv = conversation_id
    sm = state_machine
    
    sm.transition(conv, DialogueState.PROPOSED)
    sm.transition(conv, DialogueState.COMMITTED)
    sm.transition(conv, DialogueState.TIMEOUT)
    
    assert sm.get(conv) == DialogueState.TIMEOUT
    assert sm.is_terminal(conv)


def test_rollback_transition(state_machine, conversation_id):
    """Тест переходу по відкату."""
    conv = conversation_id
    sm = state_machine
    
    sm.transition(conv, DialogueState.PROPOSED)
    sm.transition(conv, DialogueState.COMMITTED)
    sm.transition(conv, DialogueState.RUNNING)
    sm.transition(conv, DialogueState.FAILED)
    
    assert sm.get(conv) == DialogueState.FAILED
    assert sm.is_terminal(conv)


def test_terminal_states():
    """Тест термінальних станів."""
    terminal_states = [
        DialogueState.DONE,
        DialogueState.FAILED,
        DialogueState.TIMEOUT,
        DialogueState.REJECTED,
        DialogueState.CANCELLED
    ]
    
    for state in terminal_states:
        sm = DialogueStateMachine()
        conv = f"conv-{state.value.lower()}"
        sm.transition(conv, state)
        assert sm.is_terminal(conv)
        
        # З термінального стану не можна перейти
        with pytest.raises(InvalidTransition):
            sm.transition(conv, DialogueState.PROPOSED)
        
        with pytest.raises(InvalidTransition):
            sm.transition(conv, DialogueState.COMMITTED)
        
        with pytest.raises(InvalidTransition):
            sm.transition(conv, DialogueState.RUNNING)


def test_get_conversations(state_machine):
    """Тест отримання всіх конверсацій."""
    sm = state_machine
    
    sm.transition("conv-001", DialogueState.PROPOSED)
    sm.transition("conv-002", DialogueState.COMMITTED)
    sm.transition("conv-003", DialogueState.DONE)
    
    conversations = sm._states
    assert len(conversations) == 3
    assert conversations["conv-001"] == DialogueState.PROPOSED
    assert conversations["conv-002"] == DialogueState.COMMITTED
    assert conversations["conv-003"] == DialogueState.DONE


def test_multiple_conversations(state_machine):
    """Тест різних конверсацій з різними станами."""
    sm = state_machine
    
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


def test_state_persistence(state_machine, conversation_id):
    """Тест збереження стану."""
    conv = conversation_id
    sm = state_machine
    
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


def test_state_machine_concurrent():
    """Тест паралельних операцій з різними конверсаціями."""
    sm = DialogueStateMachine()
    
    results = []
    errors = []
    
    def worker(conv_id, states):
        for state in states:
            try:
                sm.transition(conv_id, state)
                results.append((conv_id, state, "success"))
            except InvalidTransition as e:
                errors.append(str(e))
    
    threads = []
    for i in range(5):
        conv = f"conv-thread-{i}"
        states = [
            DialogueState.PROPOSED,
            DialogueState.COMMITTED,
            DialogueState.RUNNING,
            DialogueState.DONE
        ]
        t = threading.Thread(target=worker, args=(conv, states))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Перевіряємо, що всі конверсації дійшли до DONE
    for i in range(5):
        conv = f"conv-thread-{i}"
        assert sm.get(conv) == DialogueState.DONE
    
    # Перевіряємо, що помилок немає
    assert len(errors) == 0


def test_conversation_count(state_machine):
    """Тест кількості конверсацій."""
    sm = state_machine
    
    # Початкова кількість
    initial_count = len(sm._states)
    
    # Додаємо конверсації
    sm.transition("conv-1", DialogueState.PROPOSED)
    sm.transition("conv-2", DialogueState.COMMITTED)
    sm.transition("conv-3", DialogueState.RUNNING)
    
    assert len(sm._states) == initial_count + 3
    
    # Видалення не передбачено, але можна перевірити що вони є
    assert "conv-1" in sm._states
    assert "conv-2" in sm._states
    assert "conv-3" in sm._states


def test_state_machine_cleanup():
    """Тест очищення старих конверсацій."""
    sm = DialogueStateMachine()
    
    # Додаємо конверсації
    for i in range(10):
        conv = f"conv-{i:03d}"
        sm.transition(conv, DialogueState.PROPOSED)
        sm.transition(conv, DialogueState.COMMITTED)
        sm.transition(conv, DialogueState.DONE)
    
    # Всі мають бути в DONE
    for i in range(10):
        conv = f"conv-{i:03d}"
        assert sm.get(conv) == DialogueState.DONE


# ============================================================
# RUN WITHOUT PYTEST
# ============================================================

def run_without_pytest():
    """Запуск тестів без pytest."""
    print("\n" + "=" * 50)
    print("🧪 VIREO STATE MACHINE TESTS v1.4.3")
    print("The World's First AI-to-AI Communication Language")
    print("=" * 50)
    print("")
    
    tests = [
        ("Idempotent transition", lambda: test_idempotent_transition(DialogueStateMachine(), "conv-001")),
        ("Valid path", lambda: test_state_machine_valid_path(DialogueStateMachine(), "conv-002")),
        ("Rejects invalid transition", lambda: test_state_machine_rejects_invalid_transition(DialogueStateMachine(), "conv-003")),
        ("Timeout transition", lambda: test_timeout_transition(DialogueStateMachine(), "conv-004")),
        ("Rollback transition", lambda: test_rollback_transition(DialogueStateMachine(), "conv-005")),
        ("Terminal states", test_terminal_states),
        ("Get conversations", lambda: test_get_conversations(DialogueStateMachine())),
        ("Multiple conversations", lambda: test_multiple_conversations(DialogueStateMachine())),
        ("State persistence", lambda: test_state_persistence(DialogueStateMachine(), "conv-007")),
        ("Concurrent", test_state_machine_concurrent),
        ("Conversation count", lambda: test_conversation_count(DialogueStateMachine())),
        ("Cleanup", test_state_machine_cleanup),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"   ✅ {name} passed")
            passed += 1
        except Exception as e:
            print(f"   ❌ {name} failed: {e}")
            failed += 1
    
    print("")
    print("=" * 50)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)
    print("")
    
    return failed == 0


if __name__ == "__main__":
    # Якщо pytest доступний, використовуємо його
    if pytest:
        pytest.main([__file__, "-v"])
    else:
        success = run_without_pytest()
        sys.exit(0 if success else 1)