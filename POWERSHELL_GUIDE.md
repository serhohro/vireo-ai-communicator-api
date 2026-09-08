# 🚀 Vireo v3.0.0 — PowerShell Guide

**Робота з Vireo через PowerShell (без веб-інтерфейсу)**

---

## 📋 Перед початком

Переконайтеся, що сервер запущено:

```powershell
.\start_vireo.bat
Або:

powershell
python api/server.py
🤖 1. РОБОТА З АГЕНТАМИ
Створити агента
powershell
curl -X POST http://localhost:5000/api/v3/agent/register `
  -H "Content-Type: application/json" `
  -d '{"id": "agent-1", "name": "My First Agent", "model": "qwen2.5-coder:latest"}'
Відповідь:

json
{
  "success": true,
  "agent": {
    "id": "agent-1",
    "name": "My First Agent",
    "status": "registered"
  }
}
Створити другого агента
powershell
curl -X POST http://localhost:5000/api/v3/agent/register `
  -H "Content-Type: application/json" `
  -d '{"id": "agent-2", "name": "Second Agent", "model": "qwen2.5-coder:latest"}'
Отримати список агентів
powershell
curl http://localhost:5000/api/v3/agents
Відповідь:

json
{
  "success": true,
  "agents": {
    "agent-1": {
      "id": "agent-1",
      "name": "My First Agent",
      "status": "registered"
    },
    "agent-2": {
      "id": "agent-2",
      "name": "Second Agent",
      "status": "registered"
    }
  },
  "total": 2
}
Перевірити статус агента
powershell
curl http://localhost:5000/api/v3/agent/agent-1/status
Додати можливість агенту
powershell
curl -X POST http://localhost:5000/api/v3/agent/agent-1/capability `
  -H "Content-Type: application/json" `
  -d '{"name": "analyze_data", "description": "Analyze data"}'
📜 2. РОБОТА З КОНТРАКТАМИ
Створити контракт
powershell
curl -X POST http://localhost:5000/api/v3/propose `
  -H "Content-Type: application/json" `
  -d '{
    "contract_id": "contract-1",
    "parties": ["agent-1", "agent-2"],
    "terms": {"max_tokens": 1000, "timeout_sec": 60},
    "obligations": {
      "agent-1": {"action": "analyze_data", "input": {"data": "test"}},
      "agent-2": {"action": "process", "input": {"data": "$ref.agent-1.result"}}
    }
  }'
Відповідь:

json
{
  "success": true,
  "contract": {
    "id": "contract-1",
    "parties": ["agent-1", "agent-2"],
    "status": "proposed"
  }
}
Отримати список контрактів
powershell
curl http://localhost:5000/api/v3/contracts
Отримати контракт за ID
powershell
curl http://localhost:5000/api/v3/contracts/contract-1
Виконати контракт
powershell
curl -X POST http://localhost:5000/api/v3/execute `
  -H "Content-Type: application/json" `
  -d '{"contract_id": "contract-1"}'
Відповідь:

json
{
  "success": true,
  "execution_id": "exec-contract-1",
  "result": {
    "status": "executed",
    "output": "Contract contract-1 executed successfully"
  }
}
Верифікувати контракт
powershell
curl -X POST http://localhost:5000/api/v3/verify `
  -H "Content-Type: application/json" `
  -d '{"contract_id": "contract-1"}'
Відповідь:

json
{
  "success": true,
  "verification_id": "ver-contract-1",
  "verified": true
}
🔐 3. DIDs ТА ДОВІРА
Створити DID (Decentralized Identifier)
powershell
curl -X POST http://localhost:5000/api/v3/did/create `
  -H "Content-Type: application/json" `
  -d '{"name": "agent-1"}'
Відповідь:

json
{
  "success": true,
  "did": "did:vireo:agent-1-1",
  "public_key": "pk_agent-1_1",
  "created_at": "2026-09-06T10:30:00Z"
}
Верифікувати DID
powershell
curl -X POST http://localhost:5000/api/v3/did/verify `
  -H "Content-Type: application/json" `
  -d '{"did": "did:vireo:agent-1-1"}'
Встановити довіру між агентами
powershell
curl -X POST http://localhost:5000/api/v3/trust/establish `
  -H "Content-Type: application/json" `
  -d '{"agent_a": "did:vireo:agent-1-1", "agent_b": "did:vireo:agent-2-1"}'
Відповідь:

json
{
  "success": true,
  "trust": {
    "agent_a": "did:vireo:agent-1-1",
    "agent_b": "did:vireo:agent-2-1",
    "trust_level": "full"
  }
}
📊 4. МОНІТОРИНГ
Перевірити стан сервера (Health Check)
powershell
curl http://localhost:5000/api/health
Відповідь:

json
{
  "status": "healthy",
  "version": "3.0.0"
}
Отримати метрики
powershell
curl http://localhost:5000/api/v3/metrics
Відповідь:

json
{
  "success": true,
  "agents": 2,
  "contracts": 1,
  "trust_relationships": 1,
  "identities": 2,
  "version": "3.0.0"
}
Отримати версію протоколу
powershell
curl http://localhost:5000/api/v3/protocol/version
Відповідь:

json
{
  "version": "3.0.0",
  "protocol": "Open Wire v3.0.0",
  "wire_format": "Protobuf + FlatBuffers"
}
Відправити повідомлення
powershell
curl -X POST http://localhost:5000/api/v3/message `
  -H "Content-Type: application/json" `
  -d '{
    "type": "PROPOSE",
    "sender": "agent-1",
    "recipient": "agent-2",
    "payload": {"text": "Hello, agent-2!"}
  }'
🚀 5. АВТОНОМНА КОМУНІКАЦІЯ
Запустити автономну комунікацію між агентами
powershell
curl -X POST http://localhost:5000/api/llm/agent/agent-1/auto_negotiate `
  -H "Content-Type: application/json" `
  -d '{
    "recipient": "agent-2",
    "task": "Create a neural network for MNIST classification",
    "provider": "mistral"
  }'
📦 6. ПОВНИЙ ПРИКЛАД СЦЕНАРІЮ
powershell
# ============================================================
# ПОВНИЙ СЦЕНАРІЙ РОБОТИ З VIREO
# ============================================================

# 1. Створити агентів
curl -X POST http://localhost:5000/api/v3/agent/register -H "Content-Type: application/json" -d '{"id": "alice"}'
curl -X POST http://localhost:5000/api/v3/agent/register -H "Content-Type: application/json" -d '{"id": "bob"}'

# 2. Додати можливості
curl -X POST http://localhost:5000/api/v3/agent/alice/capability -H "Content-Type: application/json" -d '{"name": "analyze"}'
curl -X POST http://localhost:5000/api/v3/agent/bob/capability -H "Content-Type: application/json" -d '{"name": "process"}'

# 3. Створити контракт
curl -X POST http://localhost:5000/api/v3/propose -H "Content-Type: application/json" -d '{"contract_id": "c1", "parties": ["alice", "bob"], "terms": {"max_tokens": 1000}}'

# 4. Виконати контракт
curl -X POST http://localhost:5000/api/v3/execute -H "Content-Type: application/json" -d '{"contract_id": "c1"}'

# 5. Верифікувати
curl -X POST http://localhost:5000/api/v3/verify -H "Content-Type: application/json" -d '{"contract_id": "c1"}'

# 6. Створити DID
curl -X POST http://localhost:5000/api/v3/did/create -H "Content-Type: application/json" -d '{"name": "alice"}'

# 7. Перевірити метрики
curl http://localhost:5000/api/v3/metrics

# 8. Перевірити стан сервера
curl http://localhost:5000/api/health
📋 ШВИДКА ДОВІДКА
Команда	Опис
curl http://localhost:5000/api/health	Перевірити сервер
curl http://localhost:5000/api/v3/metrics	Статистика
curl http://localhost:5000/api/v3/agents	Список агентів
curl http://localhost:5000/api/v3/contracts	Список контрактів
curl http://localhost:5000/api/v3/protocol/version	Версія протоколу
🛑 ЯК ЗУПИНИТИ СЕРВЕР
powershell
# У вікні з сервером натисніть Ctrl+C
# Або:
taskkill /F /IM python.exe 2>nul
📚 Додаткові ресурси
Ресурс	URL
Веб-інтерфейс	http://localhost:5000/web
Документація	http://localhost:5000/docs
API документація	http://localhost:5000/api/docs
Health Check	http://localhost:5000/api/health
🌿 Vireo v3.0.0 — The World's First AI-to-AI Communication Language