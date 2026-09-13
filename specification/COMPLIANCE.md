# Vireo Compliance

## Status

Vireo v3.1 is a proof-of-concept. Do not use in production
without a security audit.

## GDPR

### Data processed

Vireo processes message payloads. Payloads may contain:

- Agent identifiers (DIDs - pseudonymous)
- Contract terms (may include business data)
- Task descriptions
- LLM prompts and responses

### Data retention

- Nonces: 24 hours, then deleted automatically.
- Messages: no persistent storage by default.
- Keys: stored locally; never transmitted.
- DID registry: persistent; user-controlled.

### User rights (Art. 15-22)

- Access: GET /api/v3/did/<did> returns the DID document.
- Erasure: delete nonce database (nonces.db) and DID registry entry.
- Portability: DID registry exportable as JSON.

### Legal basis

Processing is based on:

- Contract performance (Art. 6(1)(b)) for agent negotiation.
- Legitimate interest (Art. 6(1)(f)) for security (nonce replay protection).

## AI Act

Vireo is infrastructure, not an AI system itself. However, when used
in high-risk AI applications:

1. Document training data - Vireo does not train models.
2. Human oversight - ESCALATED state allows human intervention.
3. Technical robustness - see specification/CRYPTO_v3.1.md and
   benches/wire_perf/RESULTS.md.
4. Reproducibility - deterministic builds via Docker with pinned deps.

## Honest Claims Policy

Vireo README and documentation MUST NOT claim:

- "World's first" - unprovable.
- "10x faster" - measured benchmark shows 0.42x-0.90x (slower).
- "Production ready" - it is a proof-of-concept.
- "Fully implemented X" - unless X has a passing conformance test.

## Disclaimer

This software is provided "as is", without warranty of any kind.
Use at your own risk. See LICENSE (Apache 2.0).