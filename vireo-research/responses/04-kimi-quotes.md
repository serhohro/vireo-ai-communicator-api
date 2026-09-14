# Kimi (Moonshot AI) — Key Quotes

**Model:** Kimi (Moonshot AI)
**Date:** 2026-09-14
**Full response length:** ~250 lines (not published — see methodology)

**Note:** Kimi gave the sharpest technical critique. These quotes are the most important.

---

## On Vireo

> "Vireo is a signed, deterministic agent-messaging format: 96-byte header + RFC 8785 JCS, Ed25519, BLAKE2b-256, self-certifying did:vireo: identities, and an enforced contract state machine."

> "The engineering discipline is real — JCS canonicalization, cross-language test vectors, honest benchmarks (you disclose being slower than JSON)."

## On timing

> "You're simultaneously late and early. Late, because the transport/tool layers are consolidating fast. Early, because almost no agent-to-agent economic activity exists yet to standardize around."

> "FIPA-ACL had IBM, HP, BT, Fujitsu and Motorola in its consortium and still died."

> "By your own tagline, Vireo today is reproduced by one person in three languages. That's a format, not yet a standard."

## On oracle problem (deepest critique)

> "Your hardest state is VERIFY, and nothing in the repo addresses it. Signatures prove what bytes were exchanged, not whether the real-world commitment was fulfilled."

> "'Both parties signed a receipt' is not verification of execution. There's no escrow, attestation, or dispute mechanism."

> "This is the deepest unsolved problem in your design and it's currently invisible in your docs."

## On key lifecycle

> "Your crypto story is sign + hash, with no key rotation, revocation, or expiry listed anywhere."

> "For a protocol whose identity layer is entirely self-certifying, a leaked key is permanent identity theft with no recovery path."

> "This is fatal for contracts and easy to fix — fix it before anything else."

## On semantics

> "The DSL and 'Semantic AST Pass' are still targets, so today Vireo is a wire format plus state machine, not yet a language."

> "Interop breaks at meaning ('what exactly does deliver commit to?'), not at bytes."

> "Your comparison table claiming four layers overstates current reality."

## On incentives

> "'Illegal transitions are physically forbidden' protects against buggy honest agents. Against a malicious agent, a forbidden transition is just a rejected message — there's no equivocation detection, no penalty, no stake."

> "A state machine enforces the syntax of behavior, not incentives."

## On trust at scale

> "Challenge-response bootstrap with SQLite nonces is pairwise introduction. How does agent #10,000 decide whether to contract with a stranger?"

> "No reputation, registry, or delegation story (agents acting for humans or organizations — the 'on whose authority?' question)."

## On A2A comparison (key insight)

> "Don't compete with A2A; become the signed contract layer that rides it."

## On W3C DID registration

> "did:vireo is almost certainly not registered in the W3C DID Spec Registries — you claim DID-based identity without a registered method spec, which anyone in the W3C orbit will notice immediately."

## On next steps (priority order)

> "1. Key rotation + revocation spec. Non-negotiable for contracts."

> "2. Register did:vireo in the W3C DID Spec Registries. Cheap, fast, immediate credibility."

> "3. Ship bridges, not replacements: vireo-a2a and vireo-mcp."

> "4. One vertical with real money. Your COMMIT→EXECUTE→VERIFY lifecycle is 80% of an agent-payment authorization protocol."

> "5. Solve VERIFY minimally: define what evidence satisfies it."

> "6. Get one independent implementer. A Go or Kotlin SDK written by someone not you is worth more than ten more conformance vectors."

> "7. Submit an IETF Internet-Draft (ART area) for visibility and citability. Don't chase an RFC yet."

> "8. Apply to the LF Agentic AI Foundation as a sandbox project."

> "9. Track 'contracts executed' instead of 'tests passed.'"

## On European wedge

> "An EU-sovereign agent contracting layer (eIDAS 2.0, Gaia-X, data sovereignty) is a niche where 'small and not-US-controlled' is a feature."

> "NGI/Horizon Europe funding exists for exactly this. It's probably your best beachhead."

## On China (caveat: Kimi is built by Moonshot)

> "Developer gravity beats standardization pitches. Your path is bottom-up: Chinese-language docs, and adapters for tools Chinese developers actually use — Dify, FastGPT, Coze, Qwen-Agent."

> "China regulates commercial cryptography (密码法); Ed25519 isn't a state-approved algorithm (SM2 is the domestic ECC standard)."

> "Expect a bridged, multi-protocol world rather than one global winner — design for that."

## Single sentence version

> "Vireo's cryptography is done, its transport strategy is correctly humble, and its future is decided entirely by the semantic layer, the oracle problem, and whether anyone other than you ever runs it in production."

> "I'd spend the next 90 days on key rotation, DID registration, the A2A bridge, and one paying counterparty — in that order."

---

**Full response:** available upon request via GitHub Issues.
**Reason for not publishing full text:** AI chat outputs are subject to provider ToS. Only key quotes are published.