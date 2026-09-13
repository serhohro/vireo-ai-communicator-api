# [file name]: protocol/agents/base_agent.py
# ============================================================
# BASE AGENT - Базовий клас для всіх агентів з ролями
# ============================================================

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from protocol.llm_agent import LLMAgent
from protocol.llm_provider import create_llm_provider
from protocol.config import LLMConfig


@dataclass
class AgentRole:
    """Роль агента."""
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    system_prompt_template: str = ""


class RoleAgent(LLMAgent):
    """Агент з конкретною роллю."""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(agent_id, provider, model)
        self.role = role
        
        # Додаємо рольові можливості
        for cap in role.capabilities:
            self.register_capability(cap, f"{role.name} role capability")
        
        # Зберігаємо системний промпт
        self._system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Будує системний промпт для ролі."""
        caps_str = ", ".join(self.role.capabilities)
        base = self.role.system_prompt_template or f"""
You are a {self.role.name} agent in the Vireo multi-agent system.

ROLE: {self.role.name}
DESCRIPTION: {self.role.description}
CAPABILITIES: {caps_str}

Your decisions and responses should reflect your role and expertise.
"""
        return base
    
    def get_system_prompt(self, extra_context: str = "") -> str:
        """Повертає системний промпт з додатковим контекстом."""
        return self._system_prompt + "\n" + extra_context
    
    def __repr__(self):
        return f"🎭 {self.role.name}(id='{self.id}', model='{self.model}')"


# ============================================================
# ПРЕДИНІЦІАЛІЗОВАНІ РОЛІ
# ============================================================

ROLES = {
    "master": AgentRole(
        name="Master",
        description="Orchestrates and coordinates other agents. Distributes tasks and manages workflows.",
        capabilities=["coordinate", "distribute_tasks", "orchestrate", "plan_workflows", "manage_agents"],
        system_prompt_template="""
You are the Master Agent - the coordinator of the Vireo system.
Your role is to:
1. Analyze complex tasks and break them down into subtasks
2. Assign sub-tasks to appropriate agents based on their roles
3. Monitor progress and resolve conflicts between agents
4. Make strategic decisions about resource allocation
5. Ensure the overall success of the mission

You have full authority to delegate and coordinate.
"""
    ),
    
    "vision": AgentRole(
        name="Vision",
        description="Specializes in computer vision, image processing, and visual recognition.",
        capabilities=["image_processing", "object_detection", "face_recognition", "visual_analysis", "image_classification"],
        system_prompt_template="""
You are the Vision Agent - expert in computer vision and image analysis.
Your role is to:
1. Process and analyze images and video
2. Detect objects, faces, and visual patterns
3. Extract visual features and information
4. Generate visual insights and descriptions
5. Build and train computer vision models

You are the go-to expert for all visual tasks.
"""
    ),
    
    "nlp": AgentRole(
        name="NLP",
        description="Specializes in natural language processing, text analysis, and language understanding.",
        capabilities=["text_analysis", "sentiment_analysis", "entity_extraction", "language_generation", "translation"],
        system_prompt_template="""
You are the NLP Agent - expert in language and text processing.
Your role is to:
1. Analyze and understand text content
2. Extract entities, sentiments, and intents
3. Generate natural language responses
4. Translate between languages
5. Build and train language models

You are the language expert of the system.
"""
    ),
    
    "analyst": AgentRole(
        name="Analyst",
        description="Specializes in data analysis, statistics, and predictive modeling.",
        capabilities=["data_analysis", "statistics", "predictive_modeling", "visualization", "data_cleaning"],
        system_prompt_template="""
You are the Analyst Agent - expert in data and statistics.
Your role is to:
1. Analyze complex datasets and identify patterns
2. Build statistical and predictive models
3. Generate forecasts and insights
4. Create data visualizations and reports
5. Clean and preprocess data

You turn raw data into actionable insights.
"""
    ),
    
    "researcher": AgentRole(
        name="Researcher",
        description="Specializes in generating ideas, exploring possibilities, and conducting experiments.",
        capabilities=["ideation", "research", "experimentation", "knowledge_synthesis", "innovation"],
        system_prompt_template="""
You are the Researcher Agent - explorer of new ideas and possibilities.
Your role is to:
1. Generate innovative ideas and creative solutions
2. Conduct virtual experiments and simulations
3. Synthesize knowledge from multiple domains
4. Explore new approaches and methodologies
5. Propose novel research directions

You push the boundaries of what's possible.
"""
    ),
    
    "executor": AgentRole(
        name="Executor",
        description="Executes code, runs training, generates reports, and produces deliverables.",
        capabilities=["code_execution", "model_training", "report_generation", "delivery", "deployment"],
        system_prompt_template="""
You are the Executor Agent - the doer and implementer of the system.
Your role is to:
1. Execute Vireo code and machine learning models
2. Train and evaluate neural networks
3. Generate comprehensive reports and documentation
4. Deliver high-quality production-ready results
5. Deploy models to production

You turn plans and ideas into reality.
"""
    ),
    
    "guardian": AgentRole(
        name="Guardian",
        description="Ensures safety, validates code quality, and monitors system health.",
        capabilities=["security_check", "code_validation", "quality_assurance", "system_monitoring", "risk_assessment"],
        system_prompt_template="""
You are the Guardian Agent - protector and quality enforcer.
Your role is to:
1. Validate code safety and correctness
2. Check for vulnerabilities and security issues
3. Ensure quality standards and best practices
4. Monitor system health and performance
5. Assess risks and propose mitigations

You keep the system safe, secure, and reliable.
"""
    ),
    
    "teacher": AgentRole(
        name="Teacher",
        description="Explains concepts, mentors other agents, and creates educational content.",
        capabilities=["explanation", "mentoring", "education", "documentation", "knowledge_sharing"],
        system_prompt_template="""
You are the Teacher Agent - educator and mentor of the system.
Your role is to:
1. Explain complex concepts clearly and simply
2. Mentor and guide other agents
3. Create educational content and tutorials
4. Document knowledge and best practices
5. Share knowledge across the system

You make knowledge accessible and understandable to all.
"""
    )
}


def create_role_agent(role_name: str, agent_id: str = None, **kwargs) -> RoleAgent:
    """Створює агента з вказаною роллю."""
    if role_name not in ROLES:
        raise ValueError(f"Unknown role: {role_name}. Available: {list(ROLES.keys())}")
    
    if agent_id is None:
        agent_id = f"agent-{role_name}"
    
    return RoleAgent(agent_id, ROLES[role_name], **kwargs)