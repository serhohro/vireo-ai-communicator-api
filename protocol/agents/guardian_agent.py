# [file name]: protocol/agents/guardian_agent.py
# ============================================================
# GUARDIAN AGENT — Безпека, верифікація та контроль якості
# ============================================================
"""
Guardian Agent — захисник системи Vireo.

Відповідає за:
- Валідацію безпеки коду перед виконанням
- Перевірку ресурсів (пам'ять, час, токени)
- Аналіз ризиків пропозицій агентів
- Моніторинг виконання задач
- Захист від шкідливого коду
- Аудит дій агентів
"""

from __future__ import annotations

import re
import ast
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

from .base_agent import RoleAgent, ROLES, create_role_agent
from protocol.contract import Contract, Proposal

logger = logging.getLogger("vireo.agents.guardian")


# ============================================================
# КОНФІГУРАЦІЯ БЕЗПЕКИ
# ============================================================

@dataclass
class SecurityPolicy:
    """Політика безпеки для Guardian агента."""
    
    # Обмеження ресурсів
    max_memory_mb: int = 1024
    max_execution_time_sec: int = 60
    max_tokens: int = 10000
    max_cost_usd: float = 0.1
    
    # Дозволені операції
    allowed_imports: List[str] = field(default_factory=lambda: [
        "math", "random", "json", "typing", "collections"
    ])
    forbidden_keywords: List[str] = field(default_factory=lambda: [
        "exec", "eval", "compile", "globals", "locals",
        "open", "file", "input", "raw_input",
        "os", "sys", "subprocess", "socket", "pickle"
    ])
    
    # Дозволені дії агентів
    allowed_actions: List[str] = field(default_factory=lambda: [
        "train_model", "predict", "evaluate", "generate_code",
        "analyze_data", "process_image", "analyze_text"
    ])
    
    # Рівень довіри для різних джерел
    trust_levels: Dict[str, float] = field(default_factory=lambda: {
        "local": 1.0,
        "verified": 0.9,
        "unknown": 0.5,
        "external": 0.3
    })
    
    # Мінімальний рівень довіри для виконання
    min_trust_threshold: float = 0.5


# ============================================================
# АНАЛІЗАТОР БЕЗПЕКИ
# ============================================================

class SecurityAnalyzer:
    """Аналізатор безпеки Vireo коду."""
    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
        self.issues: List[Dict[str, Any]] = []
    
    def analyze(self, code: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Аналізує код на безпеку.
        
        Args:
            code: Vireo код для аналізу
            
        Returns:
            Tuple[bool, List[Dict]]: (is_safe, issues)
        """
        self.issues = []
        
        # Перевірка на шкідливі ключові слова
        self._check_forbidden_keywords(code)
        
        # Перевірка імпортів
        self._check_imports(code)
        
        # Перевірка потенційно небезпечних конструкцій
        self._check_dangerous_patterns(code)
        
        # Перевірка обмежень ресурсів
        self._check_resources(code)
        
        return len(self.issues) == 0, self.issues
    
    def _check_forbidden_keywords(self, code: str):
        """Перевіряє наявність заборонених ключових слів."""
        for keyword in self.policy.forbidden_keywords:
            if re.search(rf'\b{keyword}\b', code):
                self.issues.append({
                    "level": "error",
                    "type": "forbidden_keyword",
                    "keyword": keyword,
                    "message": f"Виявлено заборонене ключове слово: {keyword}"
                })
    
    def _check_imports(self, code: str):
        """Перевіряє імпорти на дозволені."""
        import_pattern = r'import\s+(\w+)'
        imports = re.findall(import_pattern, code)
        
        for imp in imports:
            if imp not in self.policy.allowed_imports:
                self.issues.append({
                    "level": "warning",
                    "type": "unverified_import",
                    "import": imp,
                    "message": f"Не перевірений імпорт: {imp}"
                })
    
    def _check_dangerous_patterns(self, code: str):
        """Перевіряє небезпечні патерни."""
        # Перевірка на нескінченні цикли
        if re.search(r'while\s+True\s*{', code):
            self.issues.append({
                "level": "warning",
                "type": "infinite_loop",
                "message": "Потенційно нескінченний цикл"
            })
        
        # Перевірка на рекурсію
        if re.search(r'fn\s+(\w+)\s*\([^)]*\)\s*{[^}]*\1\s*\(', code):
            self.issues.append({
                "level": "warning",
                "type": "recursion",
                "message": "Виявлено потенційну рекурсію"
            })
    
    def _check_resources(self, code: str):
        """Перевіряє використання ресурсів."""
        # Підрахунок операцій
        operations = {
            'dense': len(re.findall(r'Dense\(', code)),
            'conv2d': len(re.findall(r'Conv2D\(', code)),
            'for': len(re.findall(r'for\s+', code)),
        }
        
        total_ops = sum(operations.values())
        
        if total_ops > 100:
            self.issues.append({
                "level": "warning",
                "type": "resource_intensive",
                "operations": operations,
                "message": f"Велика кількість операцій: {total_ops}"
            })


# ============================================================
# GUARDIAN AGENT
# ============================================================

class GuardianAgent(RoleAgent):
    """
    Guardian Agent — захисник системи Vireo.
    
    Відповідає за:
    - Валідацію безпеки коду
    - Формальну верифікацію пропозицій
    - Моніторинг виконання
    - Аудит дій агентів
    - Захист від шкідливого коду
    """
    
    def __init__(self, agent_id: str = "agent-guardian", **kwargs):
        super().__init__(agent_id, ROLES["guardian"], **kwargs)
        
        self.policy = SecurityPolicy()
        self.analyzer = SecurityAnalyzer(self.policy)
        self.audit_log: List[Dict[str, Any]] = []
        self._current_proposals: Dict[str, Proposal] = {}
        
        # Реєстрація додаткових можливостей
        self.register_capability("validate_security", "Валідація безпеки коду")
        self.register_capability("check_resources", "Перевірка ресурсів")
        self.register_capability("audit_trail", "Ведення журналу аудиту")
        self.register_capability("risk_assessment", "Оцінка ризиків")
    
    def validate_proposal(self, proposal: Proposal) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Валідує пропозицію агента.
        
        Args:
            proposal: Пропозиція для перевірки
            
        Returns:
            Tuple[bool, List[Dict]]: (is_valid, issues)
        """
        logger.info(f"🛡️ [{self.id}] Validating proposal: {proposal.id}")
        
        issues = []
        is_valid = True
        
        # 1. Перевірка контракту
        contract_valid, contract_issues = self._validate_contract(proposal.contract)
        if not contract_valid:
            is_valid = False
            issues.extend(contract_issues)
        
        # 2. Перевірка безпеки коду
        code = proposal.code
        safe, security_issues = self.analyzer.analyze(code)
        if not safe:
            is_valid = False
            issues.extend(security_issues)
        
        # 3. Перевірка на шкідливий код
        malicious, malicious_issues = self._check_malicious(code)
        if malicious:
            is_valid = False
            issues.extend(malicious_issues)
        
        # 4. Оцінка ризику
        risk_level = self._assess_risk(proposal)
        if risk_level > 0.7:
            issues.append({
                "level": "warning",
                "type": "high_risk",
                "risk_level": risk_level,
                "message": f"Високий рівень ризику: {risk_level:.2f}"
            })
        
        # Логування
        self._log_validation(proposal, is_valid, issues)
        
        return is_valid, issues
    
    def _validate_contract(self, contract: Contract) -> Tuple[bool, List[Dict[str, Any]]]:
        """Перевіряє контракт."""
        issues = []
        is_valid = True
        
        if contract.max_tokens and contract.max_tokens > self.policy.max_tokens:
            is_valid = False
            issues.append({
                "level": "error",
                "type": "contract_violation",
                "message": f"Перевищення ліміту токенів: {contract.max_tokens} > {self.policy.max_tokens}"
            })
        
        if contract.timeout_sec and contract.timeout_sec > self.policy.max_execution_time_sec:
            is_valid = False
            issues.append({
                "level": "error",
                "type": "contract_violation",
                "message": f"Перевищення таймауту: {contract.timeout_sec}s > {self.policy.max_execution_time_sec}s"
            })
        
        return is_valid, issues
    
    def _check_malicious(self, code: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Перевіряє код на наявність шкідливих конструкцій."""
        issues = []
        is_malicious = False
        
        # Перевірка на системні виклики
        if re.search(r'os\.', code) or re.search(r'subprocess\.', code):
            is_malicious = True
            issues.append({
                "level": "error",
                "type": "malicious_code",
                "message": "Виявлено системні виклики"
            })
        
        # Перевірка на доступ до файлів
        if re.search(r'open\s*\(', code):
            is_malicious = True
            issues.append({
                "level": "error",
                "type": "malicious_code",
                "message": "Виявлено доступ до файлів"
            })
        
        return is_malicious, issues
    
    def _assess_risk(self, proposal: Proposal) -> float:
        """
        Оцінює ризик пропозиції.
        
        Returns:
            float: Рівень ризику (0-1)
        """
        risk_score = 0.0
        
        # Ризик на основі коду
        code = proposal.code
        if 'while' in code or 'for' in code:
            risk_score += 0.1
        
        if len(code) > 1000:
            risk_score += 0.1
        
        # Ризик на основі контракту
        if proposal.contract.max_tokens and proposal.contract.max_tokens > 5000:
            risk_score += 0.1
        
        # Ризик на основі джерела
        if proposal.sender not in self.policy.trust_levels:
            risk_score += 0.3
        else:
            trust = self.policy.trust_levels.get(proposal.sender, 0.5)
            risk_score += (1 - trust) * 0.3
        
        return min(risk_score, 1.0)
    
    def _log_validation(self, proposal: Proposal, is_valid: bool, issues: List[Dict[str, Any]]):
        """Логує результат валідації."""
        log_entry = {
            "timestamp": time.time(),
            "proposal_id": proposal.id,
            "sender": proposal.sender,
            "is_valid": is_valid,
            "issues": issues,
            "risk_level": self._assess_risk(proposal)
        }
        self.audit_log.append(log_entry)
        
        logger.info(f"📋 [{self.id}] Validation logged: {proposal.id} -> {is_valid}")
    
    def monitor_execution(self, conversation_id: str, task: str) -> Dict[str, Any]:
        """
        Моніторить виконання задачі.
        
        Args:
            conversation_id: ID розмови
            task: Задача для моніторингу
            
        Returns:
            Dict: Статус моніторингу
        """
        logger.info(f"📊 [{self.id}] Monitoring execution: {conversation_id}")
        
        return {
            "conversation_id": conversation_id,
            "status": "monitoring",
            "start_time": time.time(),
            "task": task[:100] + "...",
            "agent": self.id
        }
    
    def approve_execution(self, proposal: Proposal) -> Dict[str, Any]:
        """
        Дає дозвіл на виконання.
        
        Args:
            proposal: Пропозиція для затвердження
            
        Returns:
            Dict: Результат затвердження
        """
        is_valid, issues = self.validate_proposal(proposal)
        
        if is_valid:
            return {
                "status": "approved",
                "proposal_id": proposal.id,
                "message": "Пропозиція схвалена",
                "issues": issues
            }
        else:
            return {
                "status": "rejected",
                "proposal_id": proposal.id,
                "message": "Пропозиція відхилена з причин безпеки",
                "issues": issues
            }
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Повертає журнал аудиту."""
        return self.audit_log[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Повертає статистику роботи."""
        total_validations = len(self.audit_log)
        approved = sum(1 for entry in self.audit_log if entry.get("is_valid", False))
        
        return {
            "total_validations": total_validations,
            "approved": approved,
            "rejected": total_validations - approved,
            "avg_risk": sum(e.get("risk_level", 0) for e in self.audit_log) / max(total_validations, 1),
            "last_check": self.audit_log[-1] if self.audit_log else None
        }


# ============================================================
# ФАБРИКА
# ============================================================

def create_guardian_agent(agent_id: str = "agent-guardian", **kwargs) -> GuardianAgent:
    """Створює Guardian агента."""
    return GuardianAgent(agent_id, **kwargs)


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    from protocol.contract import Contract, create_default_contract
    from protocol.llm_provider import create_llm_provider
    
    # Створення Guardian агента
    guardian = create_guardian_agent()
    
    print(f"🛡️ Guardian Agent: {guardian.id}")
    print(f"📋 Capabilities: {[c['name'] for c in guardian.capabilities]}")
    
    # Створення пропозиції
    proposal = Proposal(
        id="prop-001",
        sender="agent-vision",
        recipient="agent-training",
        task="Train MNIST model",
        code="""
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
}
        """,
        reasoning="Simple MNIST classifier",
        contract=create_default_contract()
    )
    
    # Валідація
    is_valid, issues = guardian.validate_proposal(proposal)
    
    print(f"\n📊 Validation result: {is_valid}")
    for issue in issues:
        print(f"   {issue.get('level', 'info')}: {issue.get('message', '')}")
    
    # Статистика
    print(f"\n📈 Stats: {guardian.get_stats()}")