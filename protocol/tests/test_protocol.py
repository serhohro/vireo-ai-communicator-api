import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    import pytest
except ImportError:
    pytest = None

from protocol import (
    Message,
    make_message,
    Intent,
    DialogueState,
    DialogueStateMachine,
    InvalidTransition,
    ContextStore,
    ConflictError,
    ConflictStrategy,
)
from protocol import trust


def test_message_roundtrip_json():
    msg = make_message("a", "b", Intent.REQUEST, payload={"x": 1})
    restored = Message.from_json(msg.to_json())
    assert restored.sender.id == "a"
    assert restored.recipient.id == "b"
    assert restored.intent == Intent.REQUEST
    assert restored.payload == {"x": 1}
    assert restored.message_id == msg.message_id


def test_state_machine_valid_path():
    sm = DialogueStateMachine()
    conv = "conv-1"
    assert sm.get(conv) == DialogueState.NEW
    sm.transition(conv, DialogueState.PROPOSED)
    sm.transition(conv, DialogueState.COMMITTED)
    sm.transition(conv, DialogueState.RUNNING)
    sm.transition(conv, DialogueState.DONE)
    assert sm.get(conv) == DialogueState.DONE
    assert sm.is_terminal(conv)


def test_state_machine_rejects_invalid_transition():
    sm = DialogueStateMachine()
    conv = "conv-2"
    try:
        sm.transition(conv, DialogueState.RUNNING)
        assert False, "expected InvalidTransition"
    except InvalidTransition:
        pass


def test_context_store_detects_conflict():
    store = ContextStore(strategy=ConflictStrategy.REJECT_ON_CONFLICT)
    _, v0 = store.read("job:1:epochs")
    v1 = store.write("job:1:epochs", 10, expected_version=v0)
    store.write("job:1:epochs", 20, expected_version=v1)
    try:
        store.write("job:1:epochs", 30, expected_version=v1)
        assert False, "expected ConflictError"
    except ConflictError:
        pass


def test_context_store_last_write_wins():
    store = ContextStore(strategy=ConflictStrategy.LAST_WRITE_WINS)
    store.write("k", 1, expected_version=0)
    store.write("k", 2, expected_version=0)
    value, version = store.read("k")
    assert value == 2


def test_message_signature_valid_and_tampered():
    secret = "shared-secret"
    msg = make_message("a", "b", Intent.PROPOSE, payload={"epochs": 10})
    trust.attach_signature(msg, secret)
    assert trust.verify(msg, secret) is True
    msg.payload["epochs"] = 999
    assert trust.verify(msg, secret) is False


def test_wrong_secret_fails_verification():
    msg = make_message("a", "b", Intent.PROPOSE, payload={})
    trust.attach_signature(msg, "secret-a")
    assert trust.verify(msg, "secret-b") is False


def run_all():
    tests = [name for name in globals() if name.startswith("test_")]
    failed = 0
    for name in tests:
        fn = globals()[name]
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed == 0


if __name__ == "__main__":
    if pytest is not None:
        raise SystemExit(pytest.main([__file__, "-v"]))
    else:
        raise SystemExit(0 if run_all() else 1)