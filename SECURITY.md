# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 3.1.x   | Yes       |
| 3.0.x   | No        |
| < 3.0   | No        |

## Reporting a Vulnerability

Report security issues to: security@vireo.example

Please include:
- Description of the issue
- Steps to reproduce
- Potential impact

## Cryptography

- Ed25519 signatures (PyNaCl)
- BLAKE2b-256 hashing
- RFC 8785 canonical form
- Nonce replay protection (SQLite)
- Timestamp tolerance +/- 5 minutes

See specification/CRYPTO_v3.1.md.

## Disclaimer

Vireo v3.1 is a proof-of-concept.
Do not use in production without a security audit.