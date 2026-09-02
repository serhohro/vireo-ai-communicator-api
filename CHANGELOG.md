```markdown
# 📋 Changelog

All notable changes to Vireo will be documented in this file.

---

## [2.0.1] - 2026-01-15

### 🎯 Major Changes

- **New Architecture**: `core/` directory with modular components
- **Formal Specifications**: Complete specification suite in `specification/`
- **Trust Bootstrap Protocol**: Initial implementation for secure agent identity
- **VERIFY & ESCALATE States**: Added to protocol lifecycle
- **European LLM Support**: Dedicated `llm_provider_eu.py` for EU models

### 🆕 New Features

- Core agent base with role-based capabilities
- Contract validation pipeline
- Capability discovery registry
- Identity management with Ed25519
- Execution runner with timeout support
- Verification engine for contract validation

### 📚 Documentation

- Added `specification/` with 7 formal specs
- Added `QUICKSTART.md` and `TUTORIAL.md`
- Added `EU_LLM_GUIDE.md` for European AI providers
- Added `GOVERNANCE.md` for RFC process
- Added `AI_EVALUATIONS.md` with 7 AI model reviews

### 🐛 Fixed (from v1.4.5)

- Fixed `contract.py`: `is not None` checks for all fields
- Fixed `agent.py`: Added contract validation in `commit()`
- Fixed `master_agent.py`: Correct recipient in `auto_negotiate()`
- Fixed `state.py`: Added timeout checking with background thread
- Fixed `agent.py`: Added `_cleanup_pending()` for proposal cleanup
- Fixed `grammar.lark`: Fixed `on offer(NAME:NAME)` → `NAME:type`
- Fixed `redis.py`: Now uses `Message.from_dict()` correctly

### ⚠️ Breaking Changes

- Protocol state machine now includes VERIFY and ESCALATE
- Contract validation is now mandatory before execution

---

## [1.4.5] - 2026-01-10

### 🐛 Critical Fixes

- 7 critical fixes across core components
- Grammar fixes for `grammar.lark`
- Redis transport now properly handles Message objects

### 📚 Documentation

- Added QUICKSTART.md
- Added TUTORIAL.md

---

## [1.4.0] - 2025-12-20

### 🎯 Major Features

- Multi-Agent System with negotiation
- 6+ LLM providers integrated
- Ed25519 cryptography support
- Contract validation

---

## [1.3.0] - 2025-12-01

### 🎯 Features

- Vireo language core
- Interpreter implementation
- Formal grammar (grammar.lark)

---

## [1.0.0] - 2025-10-01

### 🎉 Initial Release

- Basic language syntax
- Single-agent execution
- REST API