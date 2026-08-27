"""
Демо: два агента договариваются о задаче обучения через VIREO-A2A протокол.
"""

import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol import (
    Agent,
    Intent,
    InMemoryEventBus,
    DialogueState,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")


def fake_vireo_executor(code: str) -> dict:
    return {"status": "ok", "epochs_run": 10, "final_accuracy": 0.974}


def main() -> None:
    bus = InMemoryEventBus()

    vision = Agent("agent-vision", bus, model="gpt-5")
    training = Agent("agent-training", bus, executor=fake_vireo_executor)

    training.register_capability(
        "train_model",
        description="Обучает модель по Vireo DSL коду",
        input_schema={"code": "string"},
        output_schema={"status": "string", "final_accuracy": "number"},
    )

    result_holder = {}

    def on_capabilities(agent, msg):
        result_holder["capabilities"] = msg.payload["capabilities"]
        print(f"\n[vision] узнал возможности training: {msg.payload['capabilities']}\n")

    vision.on(Intent.INFORM_CAPABILITIES, on_capabilities)
    vision.query_capabilities("agent-training")

    assert "capabilities" in result_holder, "capability discovery не сработал"

    vireo_code = """
    model MNIST {
        layer Dense(784, 128)
        activation ReLU
        layer Dense(128, 10)
        activation Softmax
        loss CrossEntropy
        optimizer Adam(lr=0.001)
    }
    train MNIST {
        epochs = 10
        batch_size = 64
    }
    """

    proposal = vision.propose(
        "agent-training",
        payload={"dsl": "vireo", "code": vireo_code},
        constraints={"timeout_sec": 120},
    )
    print(f"[vision] state после propose: {vision.state.get(proposal.conversation_id).value}")

    final_result = {}

    def on_inform(agent, msg):
        final_result.update(msg.payload)
        print(f"[vision] получил результат: {msg.payload}")
        if "error" in msg.payload:
            agent.state.transition(msg.conversation_id, DialogueState.FAILED)
        elif "result" in msg.payload:
            agent.state.transition(msg.conversation_id, DialogueState.DONE)

    vision.on(Intent.INFORM, on_inform)

    training.commit(proposal)

    print(f"\n[training] state: {training.state.get(proposal.conversation_id).value}")
    print(f"[vision]   state: {vision.state.get(proposal.conversation_id).value}")

    assert vision.state.get(proposal.conversation_id) == DialogueState.DONE
    assert final_result.get("result", {}).get("final_accuracy") == 0.974

    print("\n✅ Полный цикл переговоров прошёл успешно: "
          "QUERY_CAPABILITIES -> PROPOSE -> COMMIT -> RUNNING -> DONE -> INFORM")

    print("\n--- Журнал всех сообщений на шине (аудит) ---")
    for m in bus.log:
        print(f"{m.timestamp:.3f}  {m.sender.id:15s} -> {m.recipient.id:15s}  {m.intent.value}")


if __name__ == "__main__":
    main()