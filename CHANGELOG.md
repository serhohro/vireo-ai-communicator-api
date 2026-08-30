
---

### 2. `CHANGELOG.md` (НОВИЙ)

```markdown
# 🌿 Vireo Changelog

All notable changes to this project will be documented in this file.

---

## [1.4.3] - 2026-08-29

### Added
- **Language Positioning** — Vireo is now positioned as a full programming language
- **Formal Grammar** — `language/grammar.lark` — complete grammar specification
- **Syntax Documentation** — `language/syntax.md` — full language syntax
- **Standard Library** — `language/stdlib/` — math, tensor, agent, contract modules
- **Language Examples** — `language/examples/` — hello_world, neural_network, agent_negotiation, multi_agent
- **CHANGELOG.md** — Version history

### Changed
- **README.md** — Completely rewritten with focus on "Language" positioning
- **ROADMAP.md** — Updated with language development priorities

---

## [1.4.2] - 2026-08-28

### Added
- Real Ed25519 cryptography (keygen, sign, verify)
- Full negotiation protocol (PROPOSE → COMMIT → REJECT → EXECUTE → DONE)
- 7+ agent roles + Master Agent
- Gemini LLM provider
- MCP/LangChain adapters
- Multi-language UI (Ukrainian/English)

### Fixed
- `protocol/agent.py` — full commit cycle
- `_handle_message` — full intent dispatching
- Redis transport integration

---

## [1.4.1] - 2026-08-25

### Added
- Initial release
- Core language features
- Multi-agent system
- Web interface with 8 tabs

---

## [1.4.0] - 2026-08-20

### Added
- Initial prototype
- Basic interpreter
- Tensor operations