# 📘 Vireo — Як працювати з Vireo

## Порівняння середовищ та рекомендації

---

## 1. ПОРІВНЯННЯ СЕРЕДОВИЩ

| Характеристика | **Чистий Python** | **Vireo** | **Термінал + Vireo** | **Jupyter + Vireo** | **Colab + Vireo** |
|----------------|-------------------|-----------|----------------------|---------------------|-------------------|
| **Складність** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| **Візуалізація** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Інтерактивність** | ❌ | ✅ | ⭐ | ✅ | ✅ |
| **AI-агенти** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Контракти** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Криптографія** | ⭐ | ✅ | ✅ | ✅ | ✅ |
| **Документація** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Швидкість** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| **Хмарний доступ** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 2. ЩО КРАЩЕ?

### 🏆 **Для розробників: Vireo + Jupyter Lab**
- Візуалізація результатів
- Інтерактивна робота з агентами
- Можливість документувати експерименти

### 🏆 **Для швидких тестів: Термінал + Vireo**
- Швидкий запуск
- Мінімум залежностей
- Ідеально для CI/CD

### 🏆 **Для досліджень: Google Colab + Vireo**
- Безкоштовний GPU
- Хмарний доступ
- Швидке поширення

### 🏆 **Для продакшену: Чистий Python + Vireo API**
- Максимальна продуктивність
- Повний контроль
- Оптимізація

---

## 3. ЯК ПРАЦЮВАТИ

### 🖥️ **Чистий Python + Vireo (Рекомендовано)**

**Створіть `vireo_client.py`:**

```python
# ============================================================
# VIREO CLIENT — Робота з Vireo з чистого Python
# ============================================================

import requests
import json
from typing import Optional, Dict, Any

class VireoClient:
    """Клієнт для роботи з Vireo API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.agents = {}
    
    def register_agent(self, agent_id: str, model: str = "qwen2.5-coder:latest") -> Dict:
        """Зареєструвати агента."""
        response = requests.post(
            f"{self.base_url}/api/agent/register",
            json={"id": agent_id, "model": model}
        )
        return response.json()
    
    def auto_negotiate(self, sender: str, recipient: str, task: str, provider: str = "mistral") -> Dict:
        """Автономна комунікація."""
        response = requests.post(
            f"{self.base_url}/api/llm/agent/{sender}/auto_negotiate",
            json={"recipient": recipient, "task": task, "provider": provider}
        )
        return response.json()
    
    def execute_code(self, code: str) -> Dict:
        """Виконати Vireo код."""
        response = requests.post(
            f"{self.base_url}/api/interpreter",
            json={"code": code}
        )
        return response.json()
    
    def create_contract(self, parties: list, terms: dict, obligations: dict) -> Dict:
        """Створити контракт."""
        response = requests.post(
            f"{self.base_url}/api/v2/contracts",
            json={"parties": parties, "terms": terms, "obligations": obligations}
        )
        return response.json()
    
    def execute_contract(self, contract_id: str) -> Dict:
        """Виконати контракт."""
        response = requests.post(f"{self.base_url}/api/v2/contracts/{contract_id}/execute")
        return response.json()
    
    def verify_contract(self, contract_id: str) -> Dict:
        """Верифікувати контракт."""
        response = requests.post(f"{self.base_url}/api/v2/contracts/{contract_id}/verify")
        return response.json()

# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    client = VireoClient()
    
    # 1. Реєстрація агентів
    client.register_agent("agent-1")
    client.register_agent("agent-2")
    
    # 2. Автономна комунікація
    result = client.auto_negotiate(
        sender="agent-1",
        recipient="agent-2",
        task="Create a Python function for quicksort"
    )
    print("✅ Negotiation:", result.get("decision", {}).get("decision"))
    
    # 3. Створення контракту
    contract = client.create_contract(
        parties=["agent-1", "agent-2"],
        terms={"max_tokens": 1000, "timeout_sec": 60},
        obligations={
            "agent-1": {"action": "analyze", "input": {"data": "test"}},
            "agent-2": {"action": "report", "input": {"analysis": "$ref.agent-1.result"}}
        }
    )
    print("✅ Contract:", contract.get("contract_id"))
    
    # 4. Виконання контракту
    if contract.get("contract_id"):
        result = client.execute_contract(contract["contract_id"])
        print("✅ Execution:", result.get("execution", {}).get("status"))
        
        verification = client.verify_contract(contract["contract_id"])
        print("✅ Verification:", verification.get("verification", {}).get("verified"))
💻 Термінал + Vireo
bash
# Запуск сервера
python api_server.py

# Перевірка статусу
curl http://localhost:5000/health

# Список провайдерів
curl http://localhost:5000/api/providers

# Реєстрація агента
curl -X POST http://localhost:5000/api/agent/register \
  -H "Content-Type: application/json" \
  -d '{"id": "my-agent", "model": "qwen2.5-coder:latest"}'

# Автономна комунікація
curl -X POST http://localhost:5000/api/llm/agent/agent-vision/auto_negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "agent-training",
    "task": "Create a neural network",
    "provider": "mistral"
  }'

# Виконання коду
curl -X POST http://localhost:5000/api/interpreter \
  -H "Content-Type: application/json" \
  -d '{"code": "let x = 5; print(x)"}'

# Створення контракту
curl -X POST http://localhost:5000/api/v2/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "parties": ["agent-1", "agent-2"],
    "terms": {"max_tokens": 1000, "timeout_sec": 60}
  }'
📓 Jupyter Lab + Vireo
Створіть ноутбук vireo_notebook.ipynb:

python
# ============================================================
# Vireo v2.0.2 — Jupyter Lab Client
# ============================================================

import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:5000"

# ============================================================
# 1. ПЕРЕВІРКА СТАТУСУ
# ============================================================

response = requests.get(f"{BASE_URL}/health")
data = response.json()
print(f"✅ Server: {data['status']}")
print(f"📌 Version: {data['version']}")

# ============================================================
# 2. ПРОВАЙДЕРИ
# ============================================================

response = requests.get(f"{BASE_URL}/api/providers")
data = response.json()

providers_df = pd.DataFrame([
    {"Provider": p, "Models": ", ".join(data.get("models", {}).get(p, []))}
    for p in data.get("providers", [])
])
print(providers_df)

# ============================================================
# 3. АВТОНОМНА КОМУНІКАЦІЯ
# ============================================================

def negotiate(task, provider="mistral"):
    """Запустити автономну комунікацію."""
    # Реєстрація агентів
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-1"})
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-2"})
    
    response = requests.post(
        f"{BASE_URL}/api/llm/agent/agent-1/auto_negotiate",
        json={"recipient": "agent-2", "task": task, "provider": provider}
    )
    return response.json()

# Тест задач
tasks = [
    "Create a neural network for MNIST classification",
    "Write a Python function for quicksort",
    "Generate a report about climate change"
]

results = []
for task in tasks:
    result = negotiate(task)
    results.append({
        "task": task,
        "decision": result.get("decision", {}).get("decision"),
        "status": result.get("status")
    })

df = pd.DataFrame(results)
print(df)

# ============================================================
# 4. ВІЗУАЛІЗАЦІЯ
# ============================================================

# Графік результатів
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Статуси
status_counts = df['status'].value_counts()
ax1.bar(status_counts.index, status_counts.values)
ax1.set_title('Task Status Distribution')
ax1.set_xlabel('Status')
ax1.set_ylabel('Count')

# Рішення
decision_counts = df['decision'].value_counts()
ax2.bar(decision_counts.index, decision_counts.values)
ax2.set_title('Decision Distribution')
ax2.set_xlabel('Decision')
ax2.set_ylabel('Count')

plt.tight_layout()
plt.show()

# ============================================================
# 5. КРИПТОГРАФІЯ
# ============================================================

# Генерація ключів
response = requests.post(f"{BASE_URL}/api/crypto/generate_keys")
keys = response.json()
print(f"🔑 Public Key: {keys.get('public_key', 'N/A')[:20]}...")

# Підпис
response = requests.post(
    f"{BASE_URL}/api/crypto/sign",
    json={"message": "Hello, Jupyter!"}
)
signature = response.json()
print(f"✍️ Signature: {signature.get('signature', 'N/A')[:20]}...")

# ============================================================
# 6. КОНТРАКТИ
# ============================================================

contract_data = {
    "parties": ["agent-1", "agent-2"],
    "terms": {
        "max_tokens": 1000,
        "timeout_sec": 60
    },
    "obligations": {
        "agent-1": {
            "action": "analyze",
            "input": {"task": "Analyze data"}
        },
        "agent-2": {
            "action": "report",
            "input": {"analysis": "$ref.agent-1.result"}
        }
    }
}

response = requests.post(f"{BASE_URL}/api/v2/contracts", json=contract_data)
contract = response.json()
print(f"✅ Contract: {contract.get('contract_id', 'N/A')}")

if contract.get("contract_id"):
    contract_id = contract["contract_id"]
    
    # Виконання
    response = requests.post(f"{BASE_URL}/api/v2/contracts/{contract_id}/execute")
    execution = response.json()
    print(f"✅ Execution: {execution.get('execution', {}).get('status')}")
    
    # Верифікація
    response = requests.post(f"{BASE_URL}/api/v2/contracts/{contract_id}/verify")
    verification = response.json()
    print(f"✅ Verification: {verification.get('verification', {}).get('verified')}")
🚀 Google Colab + Vireo
Створіть ноутбук у Colab:

python
# ============================================================
# Vireo v2.0.2 — Google Colab Client
# ============================================================

# Встановлення залежностей (якщо потрібно)
!pip install requests

import requests
import pandas as pd
import matplotlib.pyplot as plt

# Налаштування (локальний сервер або ngrok)
BASE_URL = "http://localhost:5000"  # або ваш ngrok URL

# ============================================================
# 1. ПЕРЕВІРКА СТАТУСУ
# ============================================================

response = requests.get(f"{BASE_URL}/health")
print(f"✅ Server: {response.json()}")

# ============================================================
# 2. АВТОНОМНА КОМУНІКАЦІЯ
# ============================================================

def negotiate(task):
    """Запустити автономну комунікацію."""
    # Реєстрація агентів
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-1"})
    requests.post(f"{BASE_URL}/api/agent/register", json={"id": "agent-2"})
    
    response = requests.post(
        f"{BASE_URL}/api/llm/agent/agent-1/auto_negotiate",
        json={"recipient": "agent-2", "task": task, "provider": "mistral"}
    )
    return response.json()

# Тест задач
tasks = [
    "Create a neural network for MNIST classification",
    "Write a Python function for quicksort"
]

for task in tasks:
    result = negotiate(task)
    print(f"📝 Task: {task}")
    print(f"✅ Decision: {result.get('decision', {}).get('decision')}")
    print("-" * 50)

# ============================================================
# 3. ВІЗУАЛІЗАЦІЯ
# ============================================================

plt.figure(figsize=(8, 4))
plt.bar(["Task 1", "Task 2"], [1, 1])
plt.title("Task Completion")
plt.ylabel("Status")
plt.show()

# ============================================================
# 4. КРИПТОГРАФІЯ
# ============================================================

# Генерація ключів
response = requests.post(f"{BASE_URL}/api/crypto/generate_keys")
keys = response.json()
print(f"🔑 Keys generated: {keys.get('status')}")

# Підпис
response = requests.post(
    f"{BASE_URL}/api/crypto/sign",
    json={"message": "Hello, Colab!"}
)
signature = response.json()
print(f"✍️ Signature: {signature.get('status')}")
4. ПОРІВНЯЛЬНА ТАБЛИЦЯ
Критерій	Чистий Python	Vireo	Термінал + Vireo	Jupyter + Vireo	Colab + Vireo
AI-агенти	❌	✅	✅	✅	✅
Контракти	❌	✅	✅	✅	✅
Криптографія	⭐	✅	✅	✅	✅
Автономність	❌	✅	✅	✅	✅
Візуалізація	❌	❌	❌	✅	✅
Інтерактивність	❌	❌	⭐	✅	✅
Хмарний доступ	❌	❌	❌	❌	✅
Швидкість	⭐⭐⭐	⭐⭐	⭐⭐	⭐⭐	⭐
5. ВИСНОВОК
Для чого	Кращий варіант
Продакшен	Чистий Python + Vireo API
Дослідження	Jupyter Lab + Vireo
Тестування	Термінал + Vireo
Навчання	Google Colab + Vireo
Швидкі прототипи	Vireo Web Interface
З Vireo ви отримуєте AI-агентів, контракти та криптографію — у будь-якому середовищі! 🚀

🌿 Vireo — The World's First AI-to-AI Communication Language. 🚀