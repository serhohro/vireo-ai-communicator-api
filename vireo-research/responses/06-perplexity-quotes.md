# Perplexity — Key Quotes

**Model:** Perplexity (with web access)
**Date:** 2026-09-14
**Full response length:** ~400 lines (not published — see methodology)

**Note:** Perplexity provided research with citations. Drafts (arXiv, LF proposal, technical spec) are in `../drafts/`.

---

## On need for AI-to-AI standard

> "Yes — but timing is critical. The field is fragmenting rapidly."

> "Academic consensus: 'Interoperability, achieved by the adoption of minimal standards, is essential to ensure open, secure, web-scale, and widely-adopted agentic ecosystems'."

> "However: The window is narrowing. A2A already has production deployments at Microsoft, Amazon, and Salesforce."

## On Vireo vs competitors

| Dimension | Vireo | A2A | MCP |
|---|---|---|---|
| Wire format | 96-byte header + JCS | JSON-RPC 2.0 over HTTPS | JSON-RPC 2.0 |
| Message size | 226 B canonical | ~500-800 B | ~400-600 B |
| Cross-language determinism | ✅ Yes | ❌ No | ❌ No |
| Governance | Proposed: LF AI & Data | Linux Foundation | AAIF |
| Adoption | Unknown | 150+ orgs | Claude Desktop |

## On differentiators

> "✅ Byte-identical across languages (Python, Rust, TypeScript) — A2A/MCP don't guarantee this."

> "✅ Compact 226-byte canonical form — more efficient than JSON-RPC verbosity."

> "✅ Built-in contract lifecycle — more explicit than A2A's task states."

## On gaps

> "❌ No production deployments (vs A2A at MS/Amazon/Salesforce)."

> "❌ No standards body backing (vs A2A: Linux Foundation, MCP: AAIF)."

> "❌ No SDK ecosystem (A2A has 5 language SDKs)."

## On weakest parts

> "No production use cases — standards are 'reproduced, not declared', but Vireo has no real-world deployments."

> "No standards body affiliation — A2A (Linux Foundation) and MCP (AAIF) have institutional backing."

> "Unclear value prop vs A2A — A2A already does DIDs, JCS, and task lifecycles."

## On recent research (2024–2026) — citations

> "'Position: Collaborative Agentic AI Needs Interoperability Across Ecosystems' — ICML 2026, arXiv:2505.21550v2"

> "'A survey of agent interoperability protocols' — arXiv:2505.02279"

> "'BlockA2A: Towards Secure and Verifiable Agent-to-AI Interoperability' — arXiv:2508.01332"

> "'Beyond Context Sharing: A Unified Agent Communication Protocol (ACP)' — arXiv:2602.15055"

> "'Governance Gaps in Agent Interoperability Protocols' — arXiv:2606.31498"

**Key researchers:** Rishi Sharma, Martijn de Vos, Anne-Marie Kermarrec, Abul Ehtesham, Naveen Krishnan.

## On patents

> "Google likely holds patents on A2A (filed 2024-2025). Anthropic may have MCP-related patents (filed 2024). IBM has historical FIPA-ACL patents (expired)."

## On real-world deployments

> "A2A: Microsoft, Amazon, Salesforce (150+ orgs total). MCP: Claude Desktop, major AI platforms. Vireo: None documented."

## Final verdict

> "Vireo is technically impressive (byte-identical, compact, cryptographically sound) but strategically vulnerable."

> "If I were you: I'd pivot Vireo to complement A2A (not compete) — position it as 'A2A over Vireo wire format' for bandwidth-constrained or privacy-sensitive deployments. Then approach Linux Foundation to propose it as an A2A extension."

## On best standardization target

> "Best bet: Linux Foundation AI & Data — they already govern A2A and OVON, and Vireo's European focus aligns with their neutrality goals."

---

**Full response:** available upon request via GitHub Issues.
**Drafts (arXiv paper, LF proposal, technical spec):** see `../drafts/`.

**Reason for not publishing full text:** AI chat outputs are subject to provider ToS. Only key quotes are published.