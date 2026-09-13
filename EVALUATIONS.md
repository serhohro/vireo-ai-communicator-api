# Evaluations

AI model reviews of Vireo.

## v3.0.0 Reviews

| Model | Focus | File |
|-------|-------|------|
| ChatGPT | Control plane architecture | [ChatGPT.md](evaluations/ChatGPT.md) |
| Gemini | Wire format, WASM | [Gemini.md](evaluations/Gemini.md) |
| Kimi | Critical fixes (10 found) | [Kimi.md](evaluations/Kimi.md) |
| Mistral | EU independence | [Mistral.md](evaluations/Mistral.md) |
| Perplexity | Standardization | [Perplexity.md](evaluations/Perplexity.md) |
| Qwen | Trust layer | [Qwen.md](evaluations/Qwen.md) |

## v3.1 Reviews (compliance audit + spec)

| Model | Focus |
|-------|-------|
| ChatGPT | Compliance audit (gaps in v3.0.0) |
| Qwen | Envelope vs payload boundary |
| Gemini | Wire format spec (RFC 8785 + 96B header) |
| Mistral | Crypto + EU compliance |

## Key Insights

- **Qwen:** "Let PyTorch handle the tensors; let Vireo handle the trust."
- **ChatGPT:** "LLMs provide intelligence. Vireo provides structure, execution, verification and interoperability."
- **Kimi:** "The real challenge isn't signing - it's key discovery and trust bootstrapping."
- **Perplexity:** "Standards are born from open specifications, not single repositories."
- **Claude:** "Change the code, then tell me, in that order."
- **Gemini:** "WASM compilation and Open Wire Specification are the two most impactful investments."
- **Mistral:** "Vireo is the only solution that combines language, runtime, protocol and ecosystem in a single system."

## Assessment Summary

| Area | ChatGPT | Kimi |
|------|---------|------|
| Idea | 9.5/10 | 9.5/10 |
| Architecture | 8.5/10 | 9/10 |
| Uniqueness | - | 8.5/10 |
| Production readiness | 5.5/10 | ~6/10 |
| Standardization potential | 6-9/10 | 7/10 |

## v3.1 Fixes (from audit)

- Real Ed25519 verification (was mock `valid: True`)
- Real state machine enforcement (was documented only)
- Real contract verification with evidence (was `verified: True`)
- Real nonce replay protection (was absent)
- Honest LLM provider status (was fake responses)
- Removed "10x faster" overclaim (measured: 0.42x-0.90x)

See [CHANGELOG.md](CHANGELOG.md) for full list.