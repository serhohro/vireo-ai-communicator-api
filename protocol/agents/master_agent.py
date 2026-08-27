# [file name]: protocol/agents/master_agent.py
# ============================================================
# MASTER AGENT - Координатор всіх агентів
# ============================================================

import json
import logging
from typing import List, Dict, Any, Optional

from .base_agent import RoleAgent, ROLES, create_role_agent

logger = logging.getLogger("vireo.master_agent")


class MasterAgent(RoleAgent):
    """Головний агент-координатор."""
    
    def __init__(self, agent_id: str = "master", **kwargs):
        super().__init__(agent_id, ROLES["master"], **kwargs)
        self.agents: Dict[str, RoleAgent] = {}
        self.task_history: List[Dict] = []
        self.conversations: Dict[str, List] = {}
    
    def register_agent(self, agent: RoleAgent) -> None:
        """Реєструє агента в системі."""
        self.agents[agent.id] = agent
        logger.info(f"📋 Registered agent: {agent}")
    
    def register_agents(self, agents: List[RoleAgent]) -> None:
        """Реєструє кількох агентів."""
        for agent in agents:
            self.register_agent(agent)
    
    def get_agent(self, agent_id: str) -> Optional[RoleAgent]:
        """Отримує агента за ID."""
        return self.agents.get(agent_id)
    
    def get_agent_by_role(self, role_name: str) -> Optional[RoleAgent]:
        """Знаходить агента за роллю."""
        role_name = role_name.lower()
        for agent in self.agents.values():
            if agent.role.name.lower() == role_name:
                return agent
        return None
    
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
        
        available_roles = [agent.role.name for agent in self.agents.values()]
        
        system_prompt = f"""
You are the Master Agent. Analyze this task and determine:
1. What subtasks are needed
2. Which agent roles should handle each subtask
3. The optimal order of execution

Available agent roles:
{', '.join(available_roles)}

Respond with JSON:
{{
    "subtasks": [
        {{
            "description": "subtask description",
            "assigned_role": "role_name",
            "priority": 1-5,
            "depends_on": []
        }}
    ],
    "reasoning": "why this plan"
}}
"""
        user_prompt = f"Task: {task_description}"
        
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
        
        results = []
        conversation_id = f"conv-{len(self.task_history) + 1}"
        self.conversations[conversation_id] = []
        
        for i, subtask in enumerate(subtasks):
            role_name = subtask.get("assigned_role")
            description = subtask.get("description", "")
            priority = subtask.get("priority", 3)
            
            logger.info(f"\n📝 [{self.id}] Subtask {i+1}: {description[:80]}...")
            logger.info(f"   Priority: {priority}")
            
            agent = self.get_agent_by_role(role_name)
            if agent is None:
                logger.warning(f"   ⚠️ No agent for role: {role_name}")
                results.append({
                    "subtask": i,
                    "description": description,
                    "status": "failed",
                    "error": f"No agent for role: {role_name}"
                })
                continue
            
            logger.info(f"   🤖 Using agent: {agent}")
            
            try:
                result = agent.auto_negotiate(agent.id, description)
                
                self.conversations[conversation_id].append({
                    "agent": agent.id,
                    "role": agent.role.name,
                    "task": description,
                    "result": result
                })
                
                results.append({
                    "subtask": i,
                    "description": description,
                    "agent": agent.id,
                    "role": agent.role.name,
                    "result": result
                })
                
                logger.info(f"   ✅ Subtask {i+1} completed")
                
            except Exception as e:
                logger.error(f"   ❌ Subtask {i+1} failed: {e}")
                results.append({
                    "subtask": i,
                    "description": description,
                    "agent": agent.id,
                    "status": "failed",
                    "error": str(e)
                })
        
        completed = len([r for r in results if r.get('result', {}).get('status') == 'success'])
        failed = len([r for r in results if r.get('status') == 'failed'])
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ ORCHESTRATION COMPLETE!")
        logger.info(f"   Total subtasks: {len(subtasks)}")
        logger.info(f"   Completed: {completed}")
        logger.info(f"   Failed: {failed}")
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
                "failed": failed
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