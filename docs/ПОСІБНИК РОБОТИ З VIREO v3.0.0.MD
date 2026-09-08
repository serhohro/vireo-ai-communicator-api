🚀 ПОСІБНИК РОБОТИ З VIREO v3.0.0
Ось повний посібник, як запускати, створювати агентів, контракти та використовувати всі можливості Vireo.

📋 ЗМІСТ
Запуск Vireo

Створення агентів

Додавання можливостей

Створення контрактів

Автономна комунікація

DIDs та довіра

Open Wire Protocol

Security (криптографія)

Робота з LLM провайдерами

Команди PowerShell

1. ЗАПУСК VIREO
Швидкий запуск
powershell
# Перейдіть в папку з проєктом
cd C:\Users\Startklar\Desktop\vireo-ai-communicator-3

# Запустіть сервер
.\start_vireo.bat
Альтернативний запуск
powershell
python api/server.py
Після запуску
Відкрийте браузер:

text
http://localhost:5000/web
2. СТВОРЕННЯ АГЕНТІВ
Через веб-інтерфейс
Відкрийте http://localhost:5000/web

Перейдіть на вкладку 🧠 Agents

Введіть ID агента (наприклад, my-agent)

Натисніть 📝 Register v3

Через API (PowerShell)
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" `
  -ContentType "application/json" `
  -Body '{"id": "my-agent"}'
Через API (curl)
bash
curl -X POST http://localhost:5000/api/v3/agent/register \
  -H "Content-Type: application/json" \
  -d '{"id": "my-agent"}'
Створити кількох агентів
powershell
# Агент 1
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" -ContentType "application/json" -Body '{"id": "agent-1"}'

# Агент 2
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" -ContentType "application/json" -Body '{"id": "agent-2"}'
3. ДОДАВАННЯ МОЖЛИВОСТЕЙ (CAPABILITIES)
Через веб-інтерфейс
На вкладці 🧠 Agents

Введіть назву можливості (наприклад, analyze_data)

Натисніть 📌 Add Capability

Через API
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/agent-1/capability" `
  -ContentType "application/json" `
  -Body '{"name": "analyze_data"}'
Перевірити статус агента
powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/agent/agent-1/status"
Список всіх агентів
powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/agents"
4. СТВОРЕННЯ КОНТРАКТІВ
Через веб-інтерфейс
Перейдіть на вкладку 📜 Contracts

Заповніть:

Parties: agent-1, agent-2

Max Tokens: 1000

Timeout: 60

Натисніть 📝 Create v3

Через API
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/propose" `
  -ContentType "application/json" `
  -Body '{
    "contract_id": "contract-1",
    "parties": ["agent-1", "agent-2"],
    "terms": {"max_tokens": 1000, "timeout_sec": 60}
  }'
Виконати контракт
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/execute" `
  -ContentType "application/json" `
  -Body '{"contract_id": "contract-1"}'
Верифікувати контракт
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/verify" `
  -ContentType "application/json" `
  -Body '{"contract_id": "contract-1"}'
Список контрактів
powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/contracts"
5. АВТОНОМНА КОМУНІКАЦІЯ
Через веб-інтерфейс
Відкрийте http://localhost:5000/web

Перейдіть на вкладку 🤖 Autonomous

Заповніть:

Agent (Proposer): agent-1

Agent (Executor): agent-2

LLM Provider: виберіть провайдера

Task Description: опишіть завдання

Натисніть 🚀 Start Negotiation

Через API
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/llm/agent/agent-1/auto_negotiate" `
  -ContentType "application/json" `
  -Body '{
    "recipient": "agent-2",
    "task": "Create a neural network for MNIST classification",
    "provider": "ollama"
  }'
Доступні провайдери
Провайдер	ID	Тип
Ollama (локальний)	ollama	🦙 Local
Mistral AI (Франція)	mistral	🇪🇺 EU
Aleph Alpha (Німеччина)	aleph_alpha	🇪🇺 EU
Cohere (Швейцарія)	cohere	🇪🇺 EU
Qwen AI (Китай)	qwen	🌍 Global
OpenAI GPT	openai	🌍 Global
Claude	claude	🌍 Global
Gemini	gemini	🌍 Global
6. DIDs ТА ДОВІРА
Створити DID
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/did/create" `
  -ContentType "application/json" `
  -Body '{"name": "agent-1"}'
Верифікувати DID
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/did/verify" `
  -ContentType "application/json" `
  -Body '{"did": "did:vireo:agent-1-1"}'
Встановити довіру
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/trust/establish" `
  -ContentType "application/json" `
  -Body '{"agent_a": "did:vireo:agent-1-1", "agent_b": "did:vireo:agent-2-1"}'
7. OPEN WIRE PROTOCOL
Отримати версію протоколу
powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/protocol/version"
Відправити повідомлення
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/message" `
  -ContentType "application/json" `
  -Body '{
    "type": "PROPOSE",
    "sender": "agent-1",
    "recipient": "agent-2",
    "payload": {"text": "Hello!"}
  }'
8. SECURITY (КРИПТОГРАФІЯ)
Генерація ключів
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/crypto/generate_keys"
Підпис повідомлення
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/crypto/sign" `
  -ContentType "application/json" `
  -Body '{"message": "Hello Vireo!"}'
Перевірка підпису
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/crypto/verify" `
  -ContentType "application/json" `
  -Body '{"signature": "...", "message": "Hello Vireo!"}'
Тест довіри
powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/crypto/test_trust"
9. РОБОТА З LLM ПРОВАЙДЕРАМИ
Список провайдерів
powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/providers"
Налаштування Ollama (локальний)
powershell
# Запустити Ollama
ollama serve

# Перевірити моделі
ollama list

# Завантажити модель
ollama pull qwen2.5-coder:latest
Налаштування Mistral AI (європейський)
У .env додайте:

text
MISTRAL_API_KEY=your-api-key-here
Налаштування Aleph Alpha (європейський)
У .env додайте:

text
ALEPH_ALPHA_API_KEY=your-api-key-here
10. КОМАНДИ POWERSHELL
Швидка довідка
Команда	Опис
.\start_vireo.bat	Запустити сервер
Invoke-RestMethod -Uri "http://localhost:5000/api/health"	Перевірити сервер
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/agents"	Список агентів
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/metrics"	Метрики
Invoke-RestMethod -Uri "http://localhost:5000/api/providers"	LLM провайдери
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/protocol/version"	Версія протоколу
Повний сценарій
powershell
# 1. Запустити сервер
.\start_vireo.bat

# 2. Створити агентів
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" -ContentType "application/json" -Body '{"id": "alice"}'
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/register" -ContentType "application/json" -Body '{"id": "bob"}'

# 3. Додати можливості
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/alice/capability" -ContentType "application/json" -Body '{"name": "analyze"}'
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/agent/bob/capability" -ContentType "application/json" -Body '{"name": "process"}'

# 4. Створити контракт
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/propose" -ContentType "application/json" -Body '{"contract_id": "c1", "parties": ["alice", "bob"], "terms": {"max_tokens": 1000}}'

# 5. Виконати контракт
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/execute" -ContentType "application/json" -Body '{"contract_id": "c1"}'

# 6. Верифікувати
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/v3/verify" -ContentType "application/json" -Body '{"contract_id": "c1"}'

# 7. Автономна комунікація
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/llm/agent/alice/auto_negotiate" -ContentType "application/json" -Body '{"recipient": "bob", "task": "Analyze data", "provider": "ollama"}'

# 8. Перевірити метрики
Invoke-RestMethod -Uri "http://localhost:5000/api/v3/metrics"
📋 ДОСТУПНІ URL
URL	Опис
http://localhost:5000/	Головна API
http://localhost:5000/web	Веб-інтерфейс
http://localhost:5000/docs	Документація
http://localhost:5000/api/health	Health check
http://localhost:5000/api/docs	API документація
http://localhost:5000/api/v3/metrics	Метрики
🌿 Vireo v3.0.0 — The World's First AI-to-AI Communication Language 🚀