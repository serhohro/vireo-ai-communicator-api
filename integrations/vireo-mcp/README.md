# Vireo MCP Bridge

**Status:** Draft
**Version:** 0.1

## What This Is

An MCP server that exposes Vireo agents as tools for MCP-compatible hosts (Claude, ChatGPT, Cursor, Azure AI Agent Service).

## Why

MCP connects agents to tools. Vireo adds **signed contracts** and **deterministic wire format** to MCP tool calls.

- MCP handles discovery.
- Vireo handles cryptographic proof.

## Architecture
MCP Host (Claude/ChatGPT/Cursor)
│
▼
MCP Client
│
▼
Vireo MCP Server
│
▼
Vireo Agent Endpoint

text

## Tools Exposed

| Tool | Description |
|------|-------------|
| `vireo.discover` | Resolve DID, fetch agent capabilities |
| `vireo.propose` | Send PROPOSE intent, get signed contract |
| `vireo.execute` | Execute signed contract |
| `vireo.verify` | Verify receipt |

## Usage

### Server
```bash
cd integrations/vireo-mcp
npm install
npm run start
Client Registration
python
from mcp import ClientSession

async with ClientSession() as session:
    await session.initialize()
    tools = await session.list_tools()
    # Tools: vireo.discover, vireo.propose, vireo.execute, vireo.verify
Example: Signed Contract
json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "vireo.propose",
    "arguments": {
      "sender_did": "did:vireo:a1b2c3...",
      "recipient_did": "did:vireo:d4e5f6...",
      "contract": {
        "action": "generate_report",
        "spec": "PDF, 10 pages, financial summary"
      }
    }
  }
}
Response includes Vireo-signed wire message with Ed25519 signature.

References
MCP Specification (Anthropic)

Vireo Wire Format Specification

text

---

## 📁 Файл 5: `integrations/vireo-a2a/README.md`

```markdown
# Vireo A2A Bridge

**Status:** Draft
**Version:** 0.1

## What This Is

"A2A over Vireo" — A2A semantics, Vireo transport.

A2A handles agent-to-agent task delegation. Vireo adds **signed contracts** and **deterministic wire format** for bandwidth-constrained or privacy-sensitive deployments.

## Architecture
A2A Client Agent
│ (A2A semantics)
▼
Vireo A2A Transport
│ (Vireo wire format, Ed25519 signatures)
▼
A2A Server Agent

text

## Components

### Agent Card (Vireo-signed)
```json
{
  "name": "Vireo-Signed Agent",
  "description": "A2A agent with Vireo transport",
  "url": "https://agent.example.com/a2a",
  "capabilities": {
    "streaming": false,
    "pushNotifications": true
  },
  "vireo_did": "did:vireo:a1b2c3...",
  "vireo_signature": "base64..."
}
Delegation with Proof
Every A2A SendMessage is wrapped in Vireo wire format:

96-byte header

RFC 8785 JCS payload

Ed25519 signature

Why
Bandwidth-constrained: Vireo wire format is 2.58x smaller than JSON.

Privacy-sensitive: Deterministic bytes enable selective disclosure.

Auditable: Every delegation step is signed and verifiable.

Usage
Send Delegation
typescript
import { VireoA2ATransport } from './transport';

const transport = new VireoA2ATransport({
  privateKey: myEd25519Key,
  did: 'did:vireo:a1b2c3...'
});

const signedMessage = await transport.wrapA2AMessage({
  to: 'did:vireo:d4e5f6...',
  task: 'analyze_dataset',
  payload: { dataset: 'sales_2026.csv' }
});
Verify Incoming
typescript
const verified = await transport.verifyIncoming(signedMessage);
if (verified.valid) {
  // Process A2A task
}
References
A2A v1.0 Specification (Agentic AI Foundation)

Vireo Wire Format Specification

AGTP Composition (IETF draft)