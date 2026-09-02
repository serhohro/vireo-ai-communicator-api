# 🗺️ Vireo Development Roadmap

## 🌿 Vision

Vireo's mission is to become the **standard language and protocol** for autonomous AI-to-AI communication, enabling interoperability across different implementations, providers, and platforms.

---

## 📊 Phase Overview

| Phase | Timeline | Status |
|-------|----------|--------|
| **Phase 1: Hardening** | Jan 2026 | ✅ Done |
| **Phase 2: Specification** | Jan–Feb 2026 | 🚧 In Progress |
| **Phase 3: Core Implementation** | Feb–Apr 2026 | 📅 Planned |
| **Phase 4: Interoperability** | Apr–Jul 2026 | 📅 Planned |
| **Phase 5: Production** | Jul–Dec 2026 | 📅 Planned |

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

---

## 🚧 Phase 2: Specification (v2.0.1) — IN PROGRESS

**Goal:** Create formal specifications for all components to enable independent implementations.

### Tasks

| # | Task | Status | Priority |
|---|------|--------|----------|
| 1 | LANGUAGE.md — Vireo language specification | 🚧 In Progress | 🔴 P0 |
| 2 | PROTOCOL.md — Protocol specification | 🚧 In Progress | 🔴 P0 |
| 3 | AST.md — Abstract Syntax Tree specification | 📅 Planned | 🔴 P0 |
| 4 | WIRE_FORMAT.md — Wire format specification | 📅 Planned | 🔴 P0 |
| 5 | CONTRACTS.md — Contract specification | 📅 Planned | 🔴 P0 |
| 6 | TRUST_BOOTSTRAP.md — Trust bootstrap protocol | 📅 Planned | 🟠 P1 |
| 7 | INTEROPERABILITY.md — Interoperability guidelines | 📅 Planned | 🟠 P1 |

### Deliverables

- Complete specification suite in `specification/`
- AI_EVALUATIONS.md with 7 model reviews
- GOVERNANCE.md with RFC process

---

## 📅 Phase 3: Core Implementation (v2.1)

**Goal:** Implement core components based on formal specifications.

### Tasks

| # | Task | Priority |
|---|------|----------|
| 8 | Trust Bootstrap Protocol implementation | 🔴 P0 |
| 9 | Core Agent with roles and capabilities | 🔴 P0 |
| 10 | Core Protocol with full state machine | 🔴 P0 |
| 11 | Core Contract validation engine | 🔴 P0 |
| 12 | Core Verification with cryptographic proof | 🔴 P0 |
| 13 | Capability Discovery registry | 🟠 P1 |
| 14 | Execution runner with sandboxing | 🟠 P1 |
| 15 | Key rotation support | 🟠 P1 |
| 16 | MCP Server adapter | 🟡 P2 |

### Deliverables

- Fully functional core in `core/`
- All P0 tasks completed
- Initial test suite

---

## 📅 Phase 4: Interoperability (v2.2)

**Goal:** Enable cross-language and cross-platform interoperability.

### Tasks

| # | Task | Priority |
|---|------|----------|
| 17 | Python SDK (stable) | 🔴 P0 |
| 18 | TypeScript SDK | 🟠 P1 |
| 19 | Rust Implementation | 🟡 P2 |
| 20 | A2A Adapter | 🟠 P1 |
| 21 | MCP Adapter (complete) | 🟡 P2 |
| 22 | Conformance Test Suite | 🔴 P0 |
| 23 | Open Wire Specification implementation | 🟡 P2 |

### Deliverables

- Working Python ↔ Rust interoperability
- TypeScript SDK for web agents
- Conformance Test Suite

---

## 📅 Phase 5: Production (v3.0)

**Goal:** Production-ready system with performance and security.

### Tasks

| # | Task | Priority |
|---|------|----------|
| 24 | WASM Runtime (for sandboxing) | 🟡 P2 |
| 25 | GPU Support (via ONNX) | 🟡 P2 |
| 26 | JIT Compilation (LLVM) | 🟢 P3 |
| 27 | Performance optimization | 🟠 P1 |
| 28 | Formal verification of contracts | 🟡 P2 |
| 29 | Integration with European LLMs | 🟠 P1 |
| 30 | Host Interoperability Hackathon | 🟡 P2 |

### Deliverables

- Production-ready v3.0 release
- Performance benchmarks
- Hackathon results

---

## 🎯 Key Milestones

| Milestone | Target Date | Success Criteria |
|-----------|-------------|------------------|
| **v2.0.1 Release** | Feb 2026 | Complete specification suite |
| **v2.1 Release** | Apr 2026 | Core implementation complete |
| **Interop Demo** | Jun 2026 | Python ↔ Rust agents negotiate |
| **v2.2 Release** | Jul 2026 | TypeScript SDK + full A2A/MCP |
| **v3.0 Release** | Dec 2026 | WASM runtime + GPU support |

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

*Last updated: 2026-01-15*