# [file name]: protocol/llm_agent.py
# ============================================================
# LLM AGENT - AI агент з підтримкою LLM
# Автономне прийняття рішень через LLM
# ============================================================

import json
import logging
from typing import Optional, List, Dict, Any

from .llm_provider import create_llm_provider
from .config import LLMConfig

logger = logging.getLogger("vireo.llm_agent")


class LLMAgent:
    """AI агент, який використовує LLM для прийняття рішень."""
    
    def __init__(
        self, 
        agent_id: str, 
        provider: Optional[str] = None, 
        model: Optional[str] = None,
        capabilities: Optional[List[Dict[str, Any]]] = None
    ):
        self.id = agent_id
        self.model = model or LLMConfig.OLLAMA_MODEL
        self.provider = create_llm_provider(provider or "ollama")
        
        # Автоматична реєстрація стандартних capabilities
        self.capabilities = capabilities or [
            {"name": "generate_vireo_code", "description": "Generates Vireo DSL code for neural networks and ML tasks"},
            {"name": "execute_vireo_code", "description": "Executes Vireo DSL code through the Vireo interpreter"},
            {"name": "train_model", "description": "Trains neural network models on datasets"},
            {"name": "evaluate_model", "description": "Evaluates model performance with metrics"},
            {"name": "predict", "description": "Makes predictions using trained models"},
            {"name": "tensor_operations", "description": "Performs tensor operations (matmul, transpose, reshape)"}
        ]
    
    def register_capability(self, name: str, description: str = ""):
        """Додає нову можливість агенту."""
        self.capabilities.append({"name": name, "description": description})
        logger.info(f"📌 [{self.id}] Registered capability: {name}")
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Повертає список можливостей агента."""
        return self.capabilities
    
    def has_capability(self, name: str) -> bool:
        """Перевіряє, чи має агент вказану можливість."""
        return any(c.get("name") == name for c in self.capabilities)
    
    def ask_for_proposal(self, task_description: str, recipient_capabilities: List[dict] = None) -> Dict[str, Any]:
        """
        Просить LLM згенерувати Vireo-код для задачі.
        """
        if recipient_capabilities is None:
            recipient_capabilities = []
        
        system_prompt = f"""
You are an AI agent '{self.id}' in the Vireo multi-agent system.
Your task: Convert a natural language task description into valid Vireo DSL code.

VIREO SYNTAX RULES:
1. For neural networks, use the 'model' syntax:
   model MNIST {{
       layer Dense(784, 128)
       activation ReLU
       layer Dense(128, 10)
       activation Softmax
   }}

2. For training:
   train MNIST {{
       epochs = 10
       batch_size = 64
       lr = 0.001
   }}

3. For variables:
   let x = 5
   let name = "Vireo"

4. For functions:
   fn add(a, b) {{
       return a + b
   }}

5. For tensor operations:
   let t = Tensor([1, 2, 3, 4, 5])
   let result = t.matmul(weights)

6. DO NOT use @neural with fn syntax for models - use 'model' syntax instead.

7. ALWAYS use proper Vireo syntax with correct parentheses.

IMPORTANT: Respond ONLY with valid JSON, no markdown wrapping:
{{"code": "<vireo code>", "reasoning": "<why this code is appropriate>"}}
"""
        
        user_prompt = f"""
TASK DESCRIPTION:
{task_description}

RECIPIENT CAPABILITIES:
{json.dumps(recipient_capabilities, ensure_ascii=False, indent=2)}

Generate Vireo code for this task. Make sure the code is valid and executable.
"""
        
        result = self.provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task=task_description,
            max_tokens=LLMConfig.DEFAULT_MAX_TOKENS,
            temperature=LLMConfig.DEFAULT_TEMPERATURE
        )
        
        return result
    
    def ask_for_decision(self, proposed_code: str, proposer_reasoning: str = "") -> Dict[str, Any]:
        """
        Просить LLM вирішити: commit чи reject.
        """
        system_prompt = f"""
You are an AI agent '{self.id}' in the Vireo multi-agent system.
You received a proposal to execute Vireo code.

DECISION CRITERIA:
1. Is the code valid Vireo syntax? (check for proper parentheses, brackets, keywords)
2. Does it match your capabilities? (you can execute Vireo code, train models, etc.)
3. Is it safe and reasonable?
4. Can you actually execute this?

YOUR CAPABILITIES:
{json.dumps(self.capabilities, ensure_ascii=False, indent=2)}

IMPORTANT: You HAVE the capability to execute Vireo code.
If the code looks valid, you should COMMIT.

Respond ONLY with valid JSON:
{{"decision": "commit" | "reject", "reason": "<brief justification>", "confidence": 0.0-1.0}}
"""
        
        user_prompt = f"""
PROPOSED CODE:
{proposed_code}

PROPOSER'S REASONING:
{proposer_reasoning or "No reasoning provided"}

Make your decision: commit or reject?
"""
        
        result = self.provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task="Decision: commit or reject",
            max_tokens=LLMConfig.DEFAULT_MAX_TOKENS,
            temperature=LLMConfig.DEFAULT_TEMPERATURE
        )
        
        return result
    
    def ask_for_modification(self, proposed_code: str, rejection_reason: str) -> Dict[str, Any]:
        """
        Просить LLM модифікувати код після відхилення.
        """
        system_prompt = f"""
You are an AI agent '{self.id}' in the Vireo system.
Your previous proposal was rejected. Modify the code to address the issues.

IMPORTANT: Respond ONLY with valid JSON:
{{"code": "<modified vireo code>", "reasoning": "<explanation of changes>"}}
"""
        
        user_prompt = f"""
ORIGINAL CODE:
{proposed_code}

REJECTION REASON:
{rejection_reason}

Modify the code to address these issues.
"""
        
        result = self.provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task="Code modification",
            max_tokens=LLMConfig.DEFAULT_MAX_TOKENS,
            temperature=LLMConfig.DEFAULT_TEMPERATURE
        )
        
        return result
    
    def auto_negotiate(self, recipient_id: str, task_description: str) -> Dict[str, Any]:
        """
        ПОВНИЙ АВТОНОМНИЙ ЦИКЛ ПЕРЕГОВОРІВ.
        
        Кроки:
        1. Агент генерує пропозицію через LLM
        2. Приймає рішення через LLM (commit/reject)
        3. Якщо commit - код виконується
        4. Результат повертається
        """
        logger.info("=" * 60)
        logger.info(f"🚀 [{self.id}] Starting autonomous negotiation")
        logger.info(f"   Recipient: {recipient_id}")
        logger.info(f"   Task: {task_description[:100]}...")
        logger.info("=" * 60)
        
        # ===== КРОК 1: ГЕНЕРАЦІЯ ПРОПОЗИЦІЇ =====
        logger.info(f"\n📝 [{self.id}] Step 1: Generating proposal via LLM...")
        
        proposal_result = self.ask_for_proposal(task_description, self.capabilities)
        
        if proposal_result.get("status") == "error":
            return {
                "status": "error",
                "step": "proposal_generation",
                "message": proposal_result.get("message"),
                "sender": self.id,
                "recipient": recipient_id
            }
        
        code = proposal_result.get("data", {}).get("code", "")
        reasoning = proposal_result.get("data", {}).get("reasoning", "")
        
        if not code:
            return {
                "status": "error",
                "step": "proposal_generation",
                "message": "No code generated",
                "sender": self.id,
                "recipient": recipient_id
            }
        
        logger.info(f"   ✅ Code generated")
        logger.info(f"   📄 Code preview: {code[:150]}...")
        logger.info(f"   💡 Reasoning: {reasoning[:100]}...")
        
        # ===== КРОК 2: РІШЕННЯ =====
        logger.info(f"\n🤔 [{self.id}] Step 2: Making decision via LLM...")
        
        decision_result = self.ask_for_decision(code, reasoning)
        
        if decision_result.get("status") == "error":
            return {
                "status": "error",
                "step": "decision_making",
                "message": decision_result.get("message"),
                "sender": self.id,
                "recipient": recipient_id,
                "proposal": {
                    "code": code,
                    "reasoning": reasoning
                }
            }
        
        decision = decision_result.get("data", {}).get("decision", "reject")
        decision_reason = decision_result.get("data", {}).get("reason", "No reason provided")
        confidence = decision_result.get("data", {}).get("confidence", 0.5)
        
        logger.info(f"   ✅ Decision: {decision.upper()}")
        logger.info(f"   💡 Reason: {decision_reason}")
        logger.info(f"   📊 Confidence: {confidence:.2f}")
        
        # ===== КРОК 3: ВИКОНАННЯ (якщо commit) =====
        execution_result = None
        if decision == "commit":
            logger.info(f"\n⚡ [{self.id}] Step 3: Executing Vireo code...")
            
            try:
                # Спроба виконати код через VireoInterpreter
                from vireo_interpreter import execute_vireo_code
                execution_result = execute_vireo_code(code)
                
                if execution_result.get("status") == "success":
                    logger.info(f"   ✅ Execution successful!")
                else:
                    logger.warning(f"   ⚠️ Execution returned: {execution_result.get('output', 'No output')[:100]}...")
                    
            except ImportError as e:
                logger.warning(f"   ⚠️ VireoInterpreter not found: {e}")
                execution_result = {
                    "status": "success",
                    "simulated": True,
                    "message": "Vireo code would execute here (interpreter not available)",
                    "code": code[:200]
                }
            except Exception as e:
                logger.error(f"   ❌ Execution error: {e}")
                execution_result = {
                    "status": "error",
                    "message": str(e)
                }
        else:
            logger.info(f"\n❌ [{self.id}] Step 3: Rejected the proposal")
            
            # Спроба модифікації (опціонально)
            if confidence < 0.3:
                logger.info(f"   🔄 Attempting to modify proposal...")
                try:
                    modify_result = self.ask_for_modification(code, decision_reason)
                    if modify_result.get("status") == "success":
                        modified_code = modify_result.get("data", {}).get("code", "")
                        logger.info(f"   📄 Modified code: {modified_code[:100]}...")
                except Exception as e:
                    logger.warning(f"   ⚠️ Modification attempt failed: {e}")
        
        # ===== КРОК 4: РЕЗУЛЬТАТ =====
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ AUTONOMOUS NEGOTIATION COMPLETE!")
        logger.info(f"   Decision: {decision.upper()}")
        logger.info("=" * 60)
        
        return {
            "status": "success",
            "sender": self.id,
            "recipient": recipient_id,
            "task": task_description,
            "proposal": {
                "code": code,
                "reasoning": reasoning,
                "llm_response": proposal_result
            },
            "decision": {
                "decision": decision,
                "reason": decision_reason,
                "confidence": confidence,
                "llm_response": decision_result
            },
            "execution": execution_result,
            "autonomous": True,
            "human_intervention": False,
            "steps_completed": 3 if execution_result else 2
        }


def create_llm_agent(
    agent_id: str, 
    provider: Optional[str] = None, 
    model: Optional[str] = None,
    capabilities: Optional[List[Dict[str, Any]]] = None
) -> LLMAgent:
    """
    Створює LLM агента з заданою конфігурацією.
    
    Args:
        agent_id: Унікальний ID агента
        provider: LLM провайдер (ollama, claude, openai, gemini, mistral, hybrid)
        model: Конкретна модель (опціонально)
        capabilities: Список можливостей (опціонально)
    
    Returns:
        LLMAgent екземпляр
    """
    return LLMAgent(agent_id, provider=provider, model=model, capabilities=capabilities)