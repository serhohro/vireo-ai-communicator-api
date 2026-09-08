# Contributing to Vireo

Thank you for your interest in contributing to Vireo! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Release Process](#release-process)

---

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.9+ | Core development |
| Rust | 1.70+ | Rust SDK |
| Node.js | 18+ | TypeScript SDK |
| Go | 1.20+ | Go SDK |
| Java | 17+ | Java SDK |
| Docker | 20+ | Containerization |

### First Time Setup

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR_USERNAME/vireo-ai-communicator-3
cd vireo-ai-communicator-3

# Add upstream remote
git remote add upstream https://github.com/vireo-ai/vireo-ai-communicator-3

# Install development dependencies
make install
Development Setup
Python
bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
Rust
bash
# Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build
cd sdk/rust
cargo build

# Run tests
cargo test
TypeScript
bash
cd sdk/typescript
npm install
npm run build
npm test
Go
bash
cd sdk/go
go mod download
go test ./...
Java
bash
cd sdk/java
mvn clean install
mvn test
Coding Standards
Python
Follow PEP 8

Use type hints for all function signatures

Maximum line length: 100 characters

Use docstrings for all public functions and classes

python
def process_message(message: Message) -> Optional[Message]:
    """
    Process an incoming message.

    Args:
        message: The message to process

    Returns:
        Response message or None
    """
    pass
Rust
Follow Rust style guidelines

Use rustfmt for formatting

Use clippy for linting

rust
/// Process an incoming message
///
/// # Arguments
/// * `message` - The message to process
///
/// # Returns
/// Response message or None
fn process_message(message: &Message) -> Option<Message> {
    // Implementation
}
TypeScript
Follow TypeScript style guidelines

Use ESLint and Prettier

Use strict mode (strict: true)

typescript
/**
 * Process an incoming message
 * @param message The message to process
 * @returns Response message or null
 */
function processMessage(message: Message): Message | null {
    // Implementation
}
Commit Messages
Follow Conventional Commits:

text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
Types:

feat: New feature

fix: Bug fix

docs: Documentation changes

style: Code style changes

refactor: Code refactoring

perf: Performance improvements

test: Adding/updating tests

chore: Maintenance tasks

Example:

text
feat(protocol): add nonce validation for replay protection

Adds nonce validation to prevent replay attacks.
Implements NonceManager class with TTL support.

Closes #123
Testing
Running Tests
bash
# Run all tests
make test

# Python tests
pytest tests/ -v

# Rust tests
cd sdk/rust && cargo test

# TypeScript tests
cd sdk/typescript && npm test

# Go tests
cd sdk/go && go test ./...

# Java tests
cd sdk/java && mvn test
Test Coverage
bash
# Python coverage
pytest --cov=. --cov-report=html tests/

# Rust coverage (requires cargo-tarpaulin)
cargo tarpaulin --out Html

# TypeScript coverage
npm run test:coverage
Writing Tests
Unit Tests
python
# tests/unit/test_agent.py
import pytest
from vireo import Agent

def test_agent_creation():
    agent = Agent(name="TestAgent")
    assert agent.name == "TestAgent"
    assert agent.status == "idle"
Integration Tests
python
# tests/integration/test_communication.py
import pytest
from vireo import Agent, Message

@pytest.mark.asyncio
async def test_agent_communication():
    agent1 = Agent("Agent1")
    agent2 = Agent("Agent2")
    
    agent1.start()
    agent2.start()
    
    msg = Message(type="test", payload={"data": "hello"})
    response = await agent1.send_to(agent2, msg)
    
    assert response is not None
Conformance Tests
python
# tests/conformance/test_protocol.py
import pytest
from core.protocol import Protocol, State

def test_protocol_transitions():
    protocol = Protocol()
    protocol.transition(State.PROPOSE)
    assert protocol.get_state() == State.PROPOSE
Documentation
Building Documentation
bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build documentation
cd docs
make html
Documentation Standards
Use Markdown for all documentation

Include code examples where applicable

Keep API documentation up to date

Document all public APIs

Examples
All examples should be placed in docs/examples/ and should be runnable.

vireo
// docs/examples/hello_agent.vireo
agent HelloAgent {
    name: "HelloAgent"
    capabilities: ["greeting"]
    
    on message "hello" {
        respond("Hello, world!")
    }
}
Pull Request Process
Checklist
Before submitting a PR:

□ Code follows style guidelines
□ Tests are added/updated
□ Documentation is updated
□ All tests pass
□ No merge conflicts
□ Commit messages follow conventions
PR Template
markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] All tests pass

## Documentation
- [ ] Documentation updated
- [ ] Examples updated

## Related Issues
Closes #[issue_number]
Review Process
All PRs require at least one review

Address review comments promptly

Keep PRs focused and manageable

Squash commits before merging

Release Process
Versioning
Vireo follows Semantic Versioning:

Major: Incompatible API changes

Minor: Backward-compatible features

Patch: Backward-compatible bug fixes

Release Checklist
Update CHANGELOG.md

Update version numbers

Run full test suite

Build distribution packages

Create GitHub release

Publish to PyPI, crates.io, npm, etc.

Publishing
bash
# Python
python scripts/publish_pypi.sh

# Rust
cd sdk/rust && cargo publish

# TypeScript
cd sdk/typescript && npm publish

# Go
git tag -a v3.0.0 -m "Release v3.0.0"
git push origin v3.0.0
💬 Getting Help
Discord: discord.gg/vireo-ai

GitHub Issues: github.com/vireo-ai/vireo-ai-communicator-3/issues

Documentation: docs.vireo.ai