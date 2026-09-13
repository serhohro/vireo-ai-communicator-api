# [file name]: protocol/agents/master_agent.py
# ============================================================
# MASTER AGENT - Координатор всіх агентів
# ============================================================

import json
import logging
from typing import List, Dict, Any, Optional
from collections import deque

from .base_agent import RoleAgent, ROLES, create_role_agent

logger = logging.getLogger("vireo.master_agent")


class MasterAgent(RoleAgent):
    """Головний агент-координатор."""
    
    def __init__(self, agent_id: str = "master", **kwargs):
        super().__init__(agent_id, ROLES["master"], **kwargs)
        self.agents: Dict[str, RoleAgent] = {}
        self.task_history: List[Dict] = []
        self.conversations: Dict[str, List] = {}
        self._round_robin_index: Dict[str, int] = {}  # Для балансування навантаження
    
    def register_agent(self, agent: RoleAgent) -> None:
        """Реєструє агента в системі."""
        self.agents[agent.id] = agent
        # Ініціалізуємо round-robin індекс для ролі
        role = agent.role.name.lower()
        if role not in self._round_robin_index:
            self._round_robin_index[role] = 0
        logger.info(f"📋 Registered agent: {agent}")
    
    def register_agents(self, agents: List[RoleAgent]) -> None:
        """Реєструє кількох агентів."""
        for agent in agents:
            self.register_agent(agent)
    
    def get_agent(self, agent_id: str) -> Optional[RoleAgent]:
        """Отримує агента за ID."""
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role_name: str) -> List[RoleAgent]:
        """Отримує всіх агентів за роллю."""
        role_name = role_name.lower()
        return [agent for agent in self.agents.values() if agent.role.name.lower() == role_name]
    
    def get_agent_by_role(self, role_name: str) -> Optional[RoleAgent]:
        """Знаходить агента за роллю (першого)."""
        agents = self.get_agents_by_role(role_name)
        return agents[0] if agents else None
    
    def select_agent_by_role(self, role_name: str, strategy: str = "round_robin") -> Optional[RoleAgent]:
        """
        Вибирає агента за роллю з різними стратегіями.
        
        Args:
            role_name: Назва ролі
            strategy: "round_robin", "first", "random"
        """
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
        """Знаходить агентів за можливістю."""
        result = []
        for agent in self.agents.values():
            if agent.has_capability(capability):
                result.append(agent)
        return result
    
    def list_agents(self) -> Dict[str, str]:
        """Повертає список всіх агентів з їх ролями."""
        return {agent.id: agent.role.name for agent in self.agents.values()}
    
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """Аналізує задачу і визначає, які агенти потрібні."""
        logger.info(f"🔍 [{self.id}] Analyzing task: {task_description[:100]}...")
        
        available_roles = list(set(agent.role.name for agent in self.agents.values()))
        
        system_prompt = f"""
You are the Master Agent. Analyze this task and determine:
1. What subtasks are needed
2. Which agent roles should handle each subtask
3. The optimal order of execution (dependencies)

Available agent roles:
{', '.join(available_roles)}

Respond with JSON:
{{
    "subtasks": [
        {{
            "description": "subtask description",
            "assigned_role": "role_name",
            "priority": 1-5,
            "depends_on": []  // indices of subtasks this depends on
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
        Виконує підзавдання з повторними спробами.
        
        ✅ Виправлено: правильний recipient для auto_negotiate
        """
        role_name = subtask.get("assigned_role")
        description = subtask.get("description", "")
        priority = subtask.get("priority", 3)
        
        logger.info(f"\n📝 [{self.id}] Subtask {index+1}: {description[:80]}...")
        logger.info(f"   Priority: {priority}")
        
        # Шукаємо агента за роллю (з round-robin)
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
                # ✅ ВИПРАВЛЕНО: правильний recipient — ID агента, а не свій ID
                result = agent.auto_negotiate(
                    recipient=agent.id,  # ← виправлено: agent.id, а не self.id
                    task=description
                )
                
                return {
                    "subtask": index,
                    "description": description,
                    "agent": agent.id,
                    "role": agent.role.name,
                    "result": result,
                    "status": "success",
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
    
    def _execute_subtasks_in_order(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Виконує підзавдання в порядку залежностей (DAG).
        
        ✅ Виправлено: додано вирішення залежностей
        """
        results = [None] * len(subtasks)
        completed = set()
        
        # Будуємо граф залежностей
        dependencies = {}
        for i, subtask in enumerate(subtasks):
            deps = subtask.get("depends_on", [])
            if isinstance(deps, int):
                deps = [deps]
            dependencies[i] = set(deps)
        
        # Топологічне сортування (алгоритм Кана)
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
            # Є цикл залежностей — виконуємо в порядку визначення
            logger.warning("⚠️ Circular dependency detected — falling back to definition order")
            order = list(range(len(subtasks)))
        
        # Виконуємо в топологічному порядку
        for i in order:
            result = self._execute_subtask_with_retry(subtasks[i], i)
            results[i] = result
            
            if result.get("status") == "failed":
                # Якщо завдання провалилося, пропускаємо залежні
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
        """Повна оркестрація: аналіз → розподіл → виконання → збір результатів."""
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
        
        # ✅ Виправлено: виконання з урахуванням залежностей
        results = self._execute_subtasks_in_order(subtasks)
        
        conversation_id = f"conv-{len(self.task_history) + 1}"
        self.conversations[conversation_id] = []
        
        for i, result in enumerate(results):
            if result:
                self.conversations[conversation_id].append({
                    "agent": result.get("agent"),
                    "role": result.get("role"),
                    "task": result.get("description"),
                    "result": result.get("result")
                })
        
        # ✅ Виправлено: task_history тепер заповнюється
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
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ ORCHESTRATION COMPLETE!")
        logger.info(f"   Total subtasks: {len(subtasks)}")
        logger.info(f"   Completed: {completed}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Skipped: {skipped}")
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
                "skipped": skipped
            }
        }
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Отримує історію розмови за ID."""
        return self.conversations.get(conversation_id, [])
    
    def get_all_conversations(self) -> Dict[str, List]:
        """Отримує всі розмови."""
        return self.conversations
    
    def reset(self):
        """Скидає стан майстра."""
        self.agents = {}
        self.task_history = []
        self.conversations = {}
        self._round_robin_index = {}