# 🌿 Vireo Changelog

All notable changes to this project will be documented in this file.

---

## [1.4.5] - 2026-08-30

### Added
- **EfficientNet (B0–B5)** — lightweight image classification models (5–30M parameters)
- **UNet3+** — lightweight image segmentation model (3.5M parameters)
- **Zipformer (Wav2Vec2)** — speech recognition / ASR model (291M parameters)
- **LSTM with Activations** — support for ReLU, Sigmoid, Swish, GELU, LeakyReLU
- **New "Models" Tab** — web interface for managing pretrained models
- **New API Endpoints** — `/models/list`, `/models/load`, `/models/predict`, `/models/info`, `/models/cache/clear`
- **requirements.txt** — added `efficientnet-pytorch`, `torchaudio`, `soundfile`, `librosa`

### Fixed
- Fixed syntax error in `.env.example` — `GEMINI_MODEL gemini-1.5-pro` → `GEMINI_MODEL=gemini-1.5-pro`
- Fixed syntax error in `api_server.py` — removed extra closing parenthesis
- Fixed `pretrained.py` — `GPT2Model` → `GPT2LMHeadModel` (adds `generate` method support)

### Changed
- **README.md** — updated with new model support
- **language/grammar.lark** — added LSTM layer syntax
- **web_interface.html** — now includes 9 tabs (added Models tab)
- **api_server.py** — extended with LSTM and Pretrained Models endpoints

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
