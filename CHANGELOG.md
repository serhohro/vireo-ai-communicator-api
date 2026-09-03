# 🌿 Vireo Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.1] - 2026-09-03

### 🎯 Major Changes

- **New Architecture**: `core/` directory with modular components
- **Formal Specifications**: Complete specification suite in `specification/`
- **Trust Bootstrap Protocol**: Ed25519-based identity and whitelist
- **VERIFY & ESCALATE States**: Added to protocol lifecycle
- **Core + Extensions Architecture**: ML is now optional
- **Grammar Split**: `grammar_core.lark` + `grammar_ml.lark` + `grammar_tensor.lark`

### 🆕 New Features

- **VERIFY state** — explicit result verification before completion
- **ESCALATE state** — dispute resolution path for autonomous agents
- **Trust Bootstrap Protocol** — Ed25519-based identity and whitelist
- **Key Rotation** — secure key rotation mechanism
- **LLMAgent now inherits Agent** — real protocol integration
- **Guardian Agent** — `resolve_escalation()` method
- **max_rounds enforcement** — prevents infinite negotiation loops
- **verify_timeout_sec** — separate timeout for verification phase
- **Conformance test suite** — initial structure for compatibility testing
- **JIT compilation** — LLVM-based JIT for performance (experimental)

### 📚 Documentation

- Added `specification/` with 7 formal specs
- Added `QUICKSTART.md` and `TUTORIAL.md`
- Added `EU_LLM_GUIDE.md` for European AI providers
- Added `GOVERNANCE.md` for RFC process
- Added `AI_EVALUATIONS.md` with 7 AI model reviews
- Added `evaluations/` folder with detailed model evaluations

### 🔧 Changed

- `PROTOCOL.md` — added VERIFY/ESCALATE documentation
- `SECURITY.md` — updated with Threat Model
- `GOVERNANCE.md` — RFC process formalized
- `protocol/agent.py` — removed auto-transition to RUNNING
- `protocol/llm_agent.py` — now inherits Agent, uses real protocol
- `protocol/trust.py` — replaced HMAC with Ed25519
- `requirements.txt` — added llvmlite, transformers

### 🐛 Fixed

- `contract.py` — truthiness bug with `max_tokens=0` (is not None)
- `agent.py` — `_pending_proposals` memory leak cleanup
- `master_agent.py` — `auto_negotiate(agent.id, ...)` recipient fix
- `state.py` — timeout checking implemented
- `grammar.lark` — `on offer(NAME:type)` fix
- `redis.py` — Message.from_dict fix

### ⚠️ Breaking Changes

- Protocol state machine now includes VERIFY and ESCALATE
- Contract validation is now mandatory before execution
- `protocol/trust.py` now uses Ed25519 (HMAC deprecated)

---

## [1.4.5] - 2026-08-31

### 🆕 New Features

- **EfficientNet (B0–B5)** — lightweight image classification (5–30M params)
- **UNet3+** — image segmentation (3.5M params)
- **Zipformer (Wav2Vec2)** — speech recognition / ASR (291M params)
- **LSTM with Activations** — ReLU, Sigmoid, Swish, GELU, LeakyReLU
- **Mistral AI support** — 6th LLM provider
- **New "Models" Tab** — web interface for managing pretrained models
- **New API Endpoints** — `/models/list`, `/models/load`, `/models/predict`, `/models/info`, `/models/cache/clear`
- **European LLM support** — Ollama, Mistral, BLOOM, OpenChat

### 🔧 Changed

- `README.md` — new positioning
- `web_interface.html` — 9 tabs (added Models tab)
- `api_server.py` — extended with LSTM and Pretrained Models endpoints
- `language/grammar.lark` — added LSTM layer syntax

### 🐛 Fixed

- `.env.example` — `GEMINI_MODEL gemini-1.5-pro` → `GEMINI_MODEL=gemini-1.5-pro`
- `api_server.py` — removed extra closing parenthesis
- `pretrained.py` — `GPT2Model` → `GPT2LMHeadModel` (adds `generate` method)

---

## [1.4.3] - 2026-08-29

### 🆕 New Features

- **Language Positioning** — Vireo is now positioned as a full programming language
- **Formal Grammar** — `language/grammar.lark` — complete grammar specification
- **Syntax Documentation** — `language/syntax.md` — full language syntax
- **Standard Library** — `language/stdlib/` — math, tensor, agent, contract, crypto modules
- **Language Examples** — `language/examples/` — hello_world, neural_network, agent_negotiation, multi_agent
- **CHANGELOG.md** — Version history

### 🔧 Changed

- `README.md` — Completely rewritten with focus on "Language" positioning
- `ROADMAP.md` — Updated with language development priorities

---

## [1.4.2] - 2026-08-28

### 🆕 New Features

- Real Ed25519 cryptography (keygen, sign, verify)
- Full negotiation protocol (PROPOSE → COMMIT → REJECT → EXECUTE → DONE)
- 7+ agent roles + Master Agent
- Gemini LLM provider
- MCP/LangChain adapters
- Multi-language UI (Ukrainian/English)

### 🔧 Changed

- Protocol state machine improvements

### 🐛 Fixed

- `protocol/agent.py` — full commit cycle
- `_handle_message` — full intent dispatching
- Redis transport integration

---

## [1.4.1] - 2026-08-25

### 🆕 New Features

- Initial release
- Core language features
- Multi-agent system
- Web interface with 8 tabs
- Basic interpreter
- Tensor operations
- REST API

---

## [1.4.0] - 2026-08-20

### 🆕 New Features

- Initial prototype
- Basic interpreter
- Tensor operations
- Simple agent communication

---

## [1.3.0] - 2026-08-15

### 🆕 New Features

- Vireo language core
- Formal grammar (grammar.lark) initial version

---

## [1.0.0] - 2026-08-10

### 🎉 Initial Release

- Basic language syntax
- Single-agent execution
- REST API

---

## 📋 Legend

| Prefix | Meaning |
|--------|---------|
| 🎯 Major Changes | Breaking or significant changes |
| 🆕 New Features | New functionality added |
| 🔧 Changed | Existing functionality modified |
| 🐛 Fixed | Bug fixes |
| 📚 Documentation | Documentation updates |
| ⚠️ Breaking Changes | Breaking changes to API or protocol |
| 🎉 Initial Release | First public release |

---

🌿 **Vireo — The World's First AI-to-AI Communication Language.** 🚀