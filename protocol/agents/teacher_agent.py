# [file name]: protocol/agents/master_agent.py
# ============================================================
# MASTER AGENT - Координатор всіх агентів
# ============================================================

import json
import logging
import time
from typing import List, Dict, Any, Optional
from collections import deque

from .base_agent import RoleAgent, ROLES, create_role_agent

logger = logging.getLogger("vireo.master_agent")


class MasterAgent(RoleAgent):
    """Головний агент-координатор з підтримкою VERIFYING та ESCALATED."""
    
    def __init__(self, agent_id: str = "master", **kwargs):
        super().__init__(agent_id, ROLES["master"], **kwargs)
        self.agents: Dict[str, RoleAgent] = {}
        self.task_history: List[Dict] = []
        self.conversations: Dict[str, List] = {}
        self._round_robin_index: Dict[str, int] = {}
        self._escalated_tasks: List[Dict] = []  # 🆕 Завдання, що потребують ескалації
    
    def register_agent(self, agent: RoleAgent) -> None:
        """Реєструє агента в системі."""
        self.agents[agent.id] = agent
        role = agent.role.name.lower()
        if role not in self._round_robin_index:
            self._round_robin_index[role] = 0
        logger.info(f"📋 Registered agent: {agent}")
    
    def register_agents(self, agents: List[RoleAgent]) -> None:
        for agent in agents:
            self.register_agent(agent)
    
    def get_agent(self, agent_id: str) -> Optional[RoleAgent]:
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role_name: str) -> List[RoleAgent]:
        role_name = role_name.lower()
        return [agent for agent in self.agents.values() if agent.role.name.lower() == role_name]
    
    def get_agent_by_role(self, role_name: str) -> Optional[RoleAgent]:
        agents = self.get_agents_by_role(role_name)
        return agents[0] if agents else None
    
    def select_agent_by_role(self, role_name: str, strategy: str = "round_robin") -> Optional[RoleAgent]:
        """Вибирає агента за роллю з різними стратегіями."""
        agents = self.get_agents_by_role(role_name)
        if not agents:
            return None
        
        if strategy == "first":
            return agents[0]
        
        if strategy == "round_robin":
            role_key = role_name.lower()
            if role_key not in self._round_robin_index:
                self._round_robin_index[role_key] = 0
            
            idx = self._round_robin_index[role_key] % len(agents)
            self._round_robin_index[role_key] += 1
            return agents[idx]
        
        return agents[0]
    
    def get_agents_by_capability(self, capability: str) -> List[RoleAgent]:
        result = []
        for agent in self.agents.values():
            if agent.has_capability(capability):
                result.append(agent)
        return result
    
    def list_agents(self) -> Dict[str, str]:
        return {agent.id: agent.role.name for agent in self.agents.values()}
    
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """Аналізує задачу і визначає план виконання."""
        logger.info(f"🔍 [{self.id}] Analyzing task: {task_description[:100]}...")
        
        available_roles = list(set(agent.role.name for agent in self.agents.values()))
        
        system_prompt = f"""
You are the Master Agent. Analyze this task and determine:
1. What subtasks are needed
2. Which agent roles should handle each subtask
3. The optimal order of execution (dependencies)
4. Verification requirements for each subtask

Available agent roles:
{', '.join(available_roles)}

Respond with JSON:
{{
    "subtasks": [
        {{
            "description": "subtask description",
            "assigned_role": "role_name",
            "priority": 1-5,
            "depends_on": [],
            "verify_condition": "accuracy > 0.9"  // 🆕 Умова верифікації
        }}
    ],
    "reasoning": "why this plan"
}}
"""
        user_prompt = f"Task: {task_description}"
        
        try:
            result = self.provider.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task=task_description
            )
            
            return {
                "task": task_description,
                "plan": result.get("data", {}),
                "available_roles": available_roles
            }
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze task: {e}"
            }
    
    def _execute_subtask_with_retry(
        self, 
        subtask: Dict[str, Any], 
        index: int, 
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Виконує підзавдання з повторними спробами та верифікацією.
        🆕 Додано VERIFYING та ESCALATED стани.
        """
        role_name = subtask.get("assigned_role")
        description = subtask.get("description", "")
        priority = subtask.get("priority", 3)
        verify_condition = subtask.get("verify_condition", "")
        
        logger.info(f"\n📝 [{self.id}] Subtask {index+1}: {description[:80]}...")
        logger.info(f"   Priority: {priority}")
        if verify_condition:
            logger.info(f"   🔍 Verify: {verify_condition}")
        
        agent = self.select_agent_by_role(role_name, strategy="round_robin")
        if agent is None:
            logger.warning(f"   ⚠️ No agent for role: {role_name}")
            return {
                "subtask": index,
                "description": description,
                "status": "failed",
                "error": f"No agent for role: {role_name}"
            }
        
        logger.info(f"   🤖 Using agent: {agent.id} ({agent.role.name})")
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                # Виконання підзавдання
                result = agent.auto_negotiate(
                    recipient=agent.id,
                    task=description
                )
                
                # 🆕 Перевірка на ESCALATED
                if result.get("status") == "escalated":
                    self._handle_escalated_task(
                        index=index,
                        description=description,
                        agent_id=agent.id,
                        reason=result.get("reason", "Verification failed"),
                        result=result
                    )
                    return {
                        "subtask": index,
                        "description": description,
                        "agent": agent.id,
                        "role": agent.role.name,
                        "status": "escalated",
                        "reason": result.get("reason", "Verification failed"),
                        "retries": attempt
                    }
                
                # 🆕 VERIFYING стан
                if verify_condition and result.get("status") == "success":
                    logger.info(f"   🔍 Verifying result for subtask {index+1}")
                    
                    # Запит на верифікацію
                    verify_result = self._verify_subtask_result(
                        agent=agent,
                        result=result,
                        condition=verify_condition
                    )
                    
                    if verify_result.get("verified"):
                        logger.info(f"   ✅ Verification passed for subtask {index+1}")
                        return {
                            "subtask": index,
                            "description": description,
                            "agent": agent.id,
                            "role": agent.role.name,
                            "result": result,
                            "verified": True,
                            "status": "success",
                            "retries": attempt
                        }
                    else:
                        # Верифікація не пройшла → ESCALATED
                        error_msg = verify_result.get("error", "Verification failed")
                        self._handle_escalated_task(
                            index=index,
                            description=description,
                            agent_id=agent.id,
                            reason=error_msg,
                            result=result
                        )
                        return {
                            "subtask": index,
                            "description": description,
                            "agent": agent.id,
                            "role": agent.role.name,
                            "status": "escalated",
                            "reason": error_msg,
                            "retries": attempt
                        }
                
                return {
                    "subtask": index,
                    "description": description,
                    "agent": agent.id,
                    "role": agent.role.name,
                    "result": result,
                    "verified": False,
                    "status": "success" if result.get("status") == "success" else "failed",
                    "retries": attempt
                }
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"   ⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries:
                    logger.info(f"   🔄 Retrying... ({attempt + 1}/{max_retries})")
                    continue
                else:
                    logger.error(f"   ❌ Subtask {index+1} failed after {max_retries} retries")
                    return {
                        "subtask": index,
                        "description": description,
                        "agent": agent.id,
                        "status": "failed",
                        "error": last_error,
                        "retries": attempt
                    }
        
        return {
            "subtask": index,
            "description": description,
            "status": "failed",
            "error": "Max retries exceeded"
        }
    
    def _verify_subtask_result(self, agent: RoleAgent, result: Dict, condition: str) -> Dict[str, Any]:
        """
        🆕 Запит на верифікацію результату підзавдання.
        """
        try:
            # Створюємо запит на верифікацію через LLM або Guardian
            verification_prompt = f"""
Verify if the following result meets the condition: {condition}

Result: {json.dumps(result, indent=2)}

Respond with JSON:
{{
    "verified": true/false,
    "reason": "why verification passed or failed",
    "confidence": 0.0-1.0
}}
"""
            # Використовуємо Master Agent як веріфікатор
            verify_response = self.provider.generate_json(
                system_prompt="You are a verification agent. Verify if results meet conditions.",
                user_prompt=verification_prompt,
                task="Verification"
            )
            
            data = verify_response.get("data", {})
            return {
                "verified": data.get("verified", False),
                "error": data.get("reason", "Verification condition not met"),
                "confidence": data.get("confidence", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {
                "verified": False,
                "error": f"Verification error: {e}"
            }
    
    def _handle_escalated_task(self, index: int, description: str, agent_id: str, reason: str, result: Any) -> None:
        """
        🆕 Обробка ескалованих завдань.
        """
        escalated_item = {
            "subtask": index,
            "description": description,
            "agent": agent_id,
            "reason": reason,
            "result": result,
            "timestamp": time.time()
        }
        self._escalated_tasks.append(escalated_item)
        
        # Відправляємо повідомлення Guardian
        try:
            if "guardian" in self.agents:
                guardian = self.agents["guardian"]
                guardian.handle_escalation(escalated_item)
                logger.info(f"   🛡️ Escalated subtask {index+1} to Guardian")
            else:
                logger.warning(f"   ⚠️ No Guardian agent registered for escalation")
        except Exception as e:
            logger.error(f"Failed to escalate: {e}")
    
    def _execute_subtasks_in_order(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Виконує підзавдання в порядку залежностей (DAG) з підтримкою VERIFYING.
        """
        results = [None] * len(subtasks)
        completed = set()
        
        dependencies = {}
        for i, subtask in enumerate(subtasks):
            deps = subtask.get("depends_on", [])
            if isinstance(deps, int):
                deps = [deps]
            dependencies[i] = set(deps)
        
        in_degree = {i: len(deps) for i, deps in dependencies.items()}
        queue = deque([i for i, deg in in_degree.items() if deg == 0])
        order = []
        
        while queue:
            i = queue.popleft()
            order.append(i)
            for j, deps in dependencies.items():
                if i in deps:
                    deps.remove(i)
                    if not deps:
                        queue.append(j)
        
        if len(order) != len(subtasks):
            logger.warning("⚠️ Circular dependency detected — falling back to definition order")
            order = list(range(len(subtasks)))
        
        for i in order:
            result = self._execute_subtask_with_retry(subtasks[i], i)
            results[i] = result
            
            if result.get("status") == "escalated":
                # 🆕 Якщо завдання ескаловане — пропускаємо залежні
                for j in range(i + 1, len(subtasks)):
                    if i in dependencies.get(j, set()):
                        logger.warning(f"   ⏭️ Skipping subtask {j+1} due to escalation")
                        results[j] = {
                            "subtask": j,
                            "description": subtasks[j].get("description", ""),
                            "status": "skipped",
                            "reason": f"Escalated from subtask {i+1}"
                        }
                break
            
            if result.get("status") == "failed":
                for j in range(i + 1, len(subtasks)):
                    if i in dependencies.get(j, set()):
                        logger.warning(f"   ⏭️ Skipping subtask {j+1} due to dependency failure")
                        results[j] = {
                            "subtask": j,
                            "description": subtasks[j].get("description", ""),
                            "status": "skipped",
                            "reason": f"Dependency {i+1} failed"
                        }
        
        return results
    
    def orchestrate(self, task_description: str) -> Dict[str, Any]:
        """Повна оркестрація з VERIFYING та ESCALATED."""
        logger.info("=" * 60)
        logger.info(f"🎯 [{self.id}] Starting orchestration")
        logger.info(f"   Task: {task_description[:100]}...")
        logger.info("=" * 60)
        
        if not self.agents:
            return {
                "status": "error",
                "message": "No agents registered. Please register agents first."
            }
        
        analysis = self.analyze_task(task_description)
        
        if analysis.get("status") == "error":
            return analysis
        
        plan = analysis.get("plan", {})
        subtasks = plan.get("subtasks", [])
        reasoning = plan.get("reasoning", "")
        
        logger.info(f"\n📋 Plan created: {reasoning[:100]}...")
        logger.info(f"   Subtasks: {len(subtasks)}")
        
        results = self._execute_subtasks_in_order(subtasks)
        
        conversation_id = f"conv-{len(self.task_history) + 1}"
        self.conversations[conversation_id] = []
        
        for i, result in enumerate(results):
            if result:
                self.conversations[conversation_id].append({
                    "agent": result.get("agent"),
                    "role": result.get("role"),
                    "task": result.get("description"),
                    "result": result.get("result"),
                    "verified": result.get("verified", False),
                    "status": result.get("status")
                })
        
        self.task_history.append({
            "conversation_id": conversation_id,
            "task": task_description,
            "plan": plan,
            "results": results,
            "timestamp": time.time()
        })
        
        completed = len([r for r in results if r and r.get('status') == 'success'])
        failed = len([r for r in results if r and r.get('status') == 'failed'])
        skipped = len([r for r in results if r and r.get('status') == 'skipped'])
        escalated = len([r for r in results if r and r.get('status') == 'escalated'])
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ ORCHESTRATION COMPLETE!")
        logger.info(f"   Total subtasks: {len(subtasks)}")
        logger.info(f"   Completed: {completed}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Skipped: {skipped}")
        if escalated > 0:
            logger.info(f"   🚨 Escalated: {escalated}")
        logger.info("=" * 60)
        
        return {
            "status": "success" if completed > 0 else "partial",
            "task": task_description,
            "plan": plan,
            "results": results,
            "conversation_id": conversation_id,
            "summary": {
                "total_subtasks": len(subtasks),
                "completed": completed,
                "failed": failed,
                "skipped": skipped,
                "escalated": escalated
            }
        }
    
    def get_escalated_tasks(self) -> List[Dict]:
        """Отримує список ескалованих завдань."""
        return self._escalated_tasks.copy()
    
    def resolve_escalation(self, task_index: int, resolution: str, replacement_agent: Optional[str] = None) -> None:
        """
        🆕 Вирішує ескаловане завдання.
        
        Args:
            task_index: Індекс завдання
            resolution: "retry", "skip", "replace_agent"
            replacement_agent: ID агента для заміни (якщо resolution="replace_agent")
        """
        for item in self._escalated_tasks:
            if item.get("subtask") == task_index:
                item["resolved"] = True
                item["resolution"] = resolution
                item["resolved_at"] = time.time()
                logger.info(f"✅ Resolved escalated task {task_index+1}: {resolution}")
                break
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        return self.conversations.get(conversation_id, [])
    
    def get_all_conversations(self) -> Dict[str, List]:
        return self.conversations
    
    def reset(self):
        self.agents = {}
        self.task_history = []
        self.conversations = {}
        self._round_robin_index = {}
        self._escalated_tasks = []