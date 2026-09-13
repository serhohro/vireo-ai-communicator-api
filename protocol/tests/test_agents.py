# [file name]: protocol/tests/test_agents.py
# ============================================================
# ТЕСТИ ДЛЯ АГЕНТІВ З РОЛЯМИ
# ============================================================

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol.agents import ROLES, create_role_agent, MasterAgent


def test_role_creation():
    print("\n🧪 Testing role creation...")
    for role_name in ROLES:
        agent = create_role_agent(role_name, f"test-{role_name}")
        print(f"   ✅ {agent}")
        assert agent.role.name.lower() == role_name.lower()
    print("✅ All roles created successfully")


def test_master_agent():
    print("\n🧪 Testing Master Agent...")
    master = MasterAgent("test-master")
    vision = create_role_agent("vision", "test-vision")
    nlp = create_role_agent("nlp", "test-nlp")
    master.register_agents([vision, nlp])
    assert len(master.agents) == 2
    assert master.get_agent_by_role("vision") is not None
    print("✅ Master Agent tests passed")


def run_all_tests():
    print("=" * 60)
    print("🧪 VIREO AGENT TESTS")
    print("=" * 60)
    test_role_creation()
    test_master_agent()
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()