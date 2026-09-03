# 🗺️ Vireo Development Roadmap

## 🌿 Vision

Vireo's mission is to become the **standard language and protocol** for autonomous AI-to-AI communication, enabling interoperability across different implementations, providers, and platforms.

---

## 📊 Phase Overview

| Phase | Version | Timeline | Status |
|-------|---------|----------|--------|
| **Phase 1: Hardening** | v1.4.5 | Aug 2026 | ✅ Done |
| **Phase 2: Specification** | v2.0.1 | Sep 2026 | 🚧 In Progress |
| **Phase 3: Core Implementation** | v2.1.0 | Q4 2026 | 📅 Planned |
| **Phase 4: Interoperability** | v2.2.0 | Q1 2027 | 📅 Planned |
| **Phase 5: Production** | v3.0.0 | Q3 2027 | 📅 Planned |

---

## ✅ Phase 1: Hardening (v1.4.5) — COMPLETED

**Goal:** Stabilize existing codebase and fix critical issues.

### Completed Tasks

- [x] 7 critical fixes (contract.py, agent.py, master_agent.py, state.py, grammar.lark, redis.py)
- [x] Added VERIFY and ESCALATE states
- [x] Timeout checking with background thread
- [x] Contract validation before execution
- [x] Pending proposal cleanup
- [x] QUICKSTART.md and TUTORIAL.md
- [x] Mistral AI support
- [x] European LLM support (Ollama, Mistral, BLOOM, OpenChat)
- [x] Core + Extensions architecture

---

## 🚧 Phase 2: Specification (v2.0.1) — IN PROGRESS

**Goal:** Create formal specifications for all components to enable independent implementations.

### Tasks

| # | Task | Status | Priority |
|---|------|--------|----------|
| 1 | LANGUAGE.md — Core language specification | ✅ Done | 🔴 P0 |
| 2 | PROTOCOL.md — Protocol specification | ✅ Done | 🔴 P0 |
| 3 | AST.md — Abstract Syntax Tree specification | ✅ Done | 🔴 P0 |
| 4 | WIRE_FORMAT.md — Wire format specification | ✅ Done | 🔴 P0 |
| 5 | CONTRACTS.md — Contract specification | ✅ Done | 🔴 P0 |
| 6 | TRUST_BOOTSTRAP.md — Trust bootstrap protocol | ✅ Done | 🟠 P1 |
| 7 | INTEROPERABILITY.md — Interoperability guidelines | ✅ Done | 🟠 P1 |
| 8 | schema.json — JSON Schema for messages | 🚧 In Progress | 🔴 P0 |
| 9 | security.md — Security & Auth Specification | 🚧 In Progress | 🔴 P0 |
| 10 | Semantic Specification — Formal semantics | 📅 Planned | 🔴 P0 |

### Deliverables

- Complete specification suite in `specification/`
- AI_EVALUATIONS.md with 7 model reviews
- GOVERNANCE.md with RFC process
- EVALUATIONS.md and evaluations/ folder

---

## 📅 Phase 3: Core Implementation (v2.1.0) — PLANNED

**Goal:** Implement core components based on formal specifications.

### Tasks

| # | Task | Priority | Status |
|---|------|----------|--------|
| 8 | Trust Bootstrap Protocol implementation | 🔴 P0 | 🚧 In Progress |
| 9 | Core Agent with roles and capabilities | 🔴 P0 | 🚧 In Progress |
| 10 | Core Protocol with full state machine | 🔴 P0 | 🚧 In Progress |
| 11 | Core Contract validation engine | 🔴 P0 | 🚧 In Progress |
| 12 | Core Verification with cryptographic proof | 🔴 P0 | 🚧 In Progress |
| 13 | **Async/await protocol** | 🔴 P0 | 📅 Planned |
| 14 | **LLMAgent inherits Agent** | 🔴 P0 | 🚧 In Progress |
| 15 | Capability Discovery registry | 🟠 P1 | 📅 Planned |
| 16 | Execution runner with sandboxing | 🟠 P1 | 📅 Planned |
| 17 | Key rotation support | 🟠 P1 | 🚧 In Progress |
| 18 | max_rounds enforcement | 🟠 P1 | ✅ Done |
| 19 | resolve_escalation() in Guardian | 🟠 P1 | 🚧 In Progress |
| 20 | MCP Server adapter | 🟡 P2 | 📅 Planned |

### Deliverables

- Fully functional core in `core/`
- All P0 tasks completed
- Initial test suite
- Async protocol ready

---

## 📅 Phase 4: Interoperability (v2.2.0) — PLANNED

**Goal:** Enable cross-language and cross-platform interoperability.

### Tasks

| # | Task | Priority | Status |
|---|------|----------|--------|
| 21 | Python SDK (stable) | 🔴 P0 | 📅 Planned |
| 22 | Conformance Test Suite | 🔴 P0 | 🚧 In Progress |
| 23 | WASM Runtime (Rust → wasm32) | 🟠 P1 | 📅 Planned |
| 24 | TypeScript SDK | 🟠 P1 | 📅 Planned |
| 25 | Rust Implementation | 🟠 P1 | 📅 Planned |
| 26 | A2A Adapter | 🟠 P1 | 📅 Planned |
| 27 | MCP Adapter (complete) | 🟠 P1 | 📅 Planned |
| 28 | Open Wire Specification implementation | 🟡 P2 | 📅 Planned |
| 29 | JIT Compilation (LLVM) | 🟡 P2 | 📅 Planned |
| 30 | GPU Support (CUDA → Metal → ROCm) | 🟡 P2 | 📅 Planned |

### Deliverables

- Working Python ↔ Rust interoperability
- TypeScript SDK for web agents
- Conformance Test Suite
- WASM Runtime for sandboxing

---

## 📅 Phase 5: Production (v3.0.0) — PLANNED

**Goal:** Production-ready system with performance and security.

### Tasks

| # | Task | Priority | Status |
|---|------|----------|--------|
| 31 | Formal verification of contracts | 🟡 P2 | 📅 Planned |
| 32 | Integration with European LLMs | 🟠 P1 | ✅ Done |
| 33 | Performance optimization | 🟠 P1 | 📅 Planned |
| 34 | Host Interoperability Hackathon | 🟡 P2 | 📅 Planned |
| 35 | IETF-style RFC draft | 🟡 P2 | 📅 Planned |
| 36 | IEEE/ISO standardization proposal | 🟢 P3 | 📅 Planned |
| 37 | Vireo Foundation establishment | 🟢 P3 | 📅 Planned |

### Deliverables

- Production-ready v3.0 release
- Performance benchmarks
- Hackathon results
- Standardization proposal

---

## 🎯 Key Milestones

| Milestone | Version | Target Date | Success Criteria |
|-----------|---------|-------------|------------------|
| **Hardening** | v1.4.5 | Aug 2026 | 7 critical fixes + docs | ✅ Done |
| **Specification** | v2.0.1 | Sep 2026 | Complete specification suite | 🚧 In Progress |
| **Core Implementation** | v2.1.0 | Q4 2026 | Core implementation complete | 📅 Planned |
| **Interop Demo** | v2.1.0 | Q4 2026 | Python ↔ Rust agents negotiate | 📅 Planned |
| **SDK Release** | v2.2.0 | Q1 2027 | TypeScript SDK + full A2A/MCP | 📅 Planned |
| **Production** | v3.0.0 | Q3 2027 | WASM runtime + GPU support | 📅 Planned |
| **Standardization** | v3.0.0 | Q3 2027 | IEEE/ISO proposal | 📅 Planned |

---

## 🔄 North Star

> **"Can two independently implemented agents (Python ↔ Rust) negotiate, execute, and cryptographically verify a contract through Vireo?"**

This is the ultimate test of Vireo as a **standard** rather than just a framework.

---

## 📋 Governance

All significant changes follow the RFC process defined in [GOVERNANCE.md](GOVERNANCE.md).

- **RFC**: Proposals for new features or changes
- **Review**: At least 2 maintainers approve
- **Implementation**: Code review + tests required

---

## 🤝 How to Contribute

1. Review [CONTRIBUTING.md](CONTRIBUTING.md)
2. Check open issues and RFCs
3. Submit PR with clear description and tests
4. Pass CI/CD checks

---

## 📊 Key Metrics

| Metric | v1.4.3 | v2.0.1 | Target v3.0 |
|--------|--------|--------|-------------|
| Agent Roles | 8 | 8 | 15+ |
| LLM Providers | 5+ | 6+ | 10+ |
| Tests Coverage | 0% | 20% | 80% |
| Documentation | Good | Comprehensive | Complete |
| Implementations | Python | Python | Python, Rust, TypeScript |
| Specifications | 0 | 7 | 12+ |
| Conformance Tests | 0 | 10+ | 50+ |

---

## 🔗 Related Documents

- [PROTOCOL.md](PROTOCOL.md) — Protocol specification
- [GOVERNANCE.md](GOVERNANCE.md) — RFC process
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
- [CHANGELOG.md](CHANGELOG.md) — Version history

---

*Last updated: 2026-09-03*

🌿 **Vireo — The World's First AI-to-AI Communication Language.** 🚀