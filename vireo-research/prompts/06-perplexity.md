# Vireo Research — Perplexity

## Context

I'm building **Vireo** — an AI-to-AI communication language and wire protocol.

- **GitHub:** https://github.com/serhohro/vireo-ai-communicator-api
- **Release:** https://github.com/serhohro/vireo-ai-communicator-api/releases/tag/3.3.0

### Current state (v3.3.0)

- Byte-identical wire format across **Python, Rust, and TypeScript**
- 96-byte header + RFC 8785 JCS payload
- Ed25519 signatures, BLAKE2b-256 hashing
- DID-based identity (`did:vireo:...`)
- Contract lifecycle: DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE
- 226 B canonical bytes, wire_hash `011c2182...7255db`
- Verified in CI on every push (4/4 jobs green)

### Positioning

> "Standards aren't declared. They're reproduced."

---

## Questions

### Universal

1. **What do you know about Vireo?** Honest assessment — even if you don't know it.

2. **Is there a real need for an AI-to-AI communication standard?** Or is this premature?

3. **What are the biggest obstacles** for AI agents to communicate? (technical, political, economic)

4. **How does Vireo compare to:**
   - A2A (Agent-to-Agent, Google)
   - MCP (Model Context Protocol, Anthropic)
   - ANP (Agent Network Protocol)
   - ACP (Agent Communication Protocol)
   - FIPA-ACL (1990s)

5. **What's needed** for an AI-to-AI protocol to become a **real standard**?

6. **What's the weakest part of Vireo?**

7. **Concrete next steps** — what would you do next if you were me?

8. **Which organizations** should I approach for standardization? (IETF, W3C, IEEE, Linux Foundation, etc.)

### Specific to Perplexity

9. **What recent research exists** on AI-to-AI communication protocols? (2023–2026) **Cite sources.**

10. **Who is already working** on this? (companies, researchers, standards bodies) **Cite sources.**

11. **What patents exist** in this space? **Cite patent numbers if possible.**

12. **What academic papers** are most relevant? **Cite DOIs / arXiv links.**

13. **What real-world deployments exist?** Any production use of AI-to-AI protocols? **Cite cases.**

---

## Instructions

- Be **honest** and **critical**. I don't need validation.
- If you don't know something — say so.
- Focus on **actionable** recommendations.
- **Please cite sources with links.** Prioritize recent (2024–2026) and peer-reviewed.
- Length: 800–1500 words.
