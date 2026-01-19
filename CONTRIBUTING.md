# Contributing to BaaS Arc

Thank you for your interest in contributing to BaaS Arc! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Format](#commit-message-format)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and considerate in all interactions
- Accept constructive criticism gracefully
- Focus on what's best for the project and community
- Show empathy towards other community members
- Use welcoming and inclusive language

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting/derogatory comments, or personal attacks
- Publishing others' private information without permission
- Any conduct that could be considered unprofessional

### Enforcement

Violations may result in temporary or permanent bans from the project. Report incidents to: conduct@baas-arc.dev

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher
- Git for version control
- Basic understanding of blockchain and Web3 concepts
- Familiarity with async Python programming

### Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/baas-arc.git
cd baas-arc/banking

# Add upstream remote
git remote add upstream https://github.com/original-repo/baas-arc.git
```

---

## Development Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

**Development dependencies include:**
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `isort` - Import organizer

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your test credentials
# NOTE: Use testnet/sandbox credentials only!
```

### 4. Verify Setup

```bash
# Run setup verification
python scripts/setup.py

# Run basic tests
pytest tests/test_basic.py -v
```

---

## How to Contribute

### Areas for Contribution

We welcome contributions in these areas:

#### 1. Core Features
- Improve transaction processing speed
- Enhance fraud detection algorithms
- Add new banking division capabilities
- Optimize yield strategies

#### 2. Integrations
- New blockchain networks
- Additional DeFi protocols
- Alternative AI providers
- Payment gateways

#### 3. Documentation
- Improve existing docs
- Add tutorials and guides
- Create video walkthroughs
- Translate documentation

#### 4. Testing
- Add unit tests
- Create integration tests
- Write end-to-end tests
- Performance benchmarks

#### 5. Bug Fixes
- Fix reported issues
- Improve error handling
- Enhance stability
- Security patches

### Finding Issues to Work On

Look for issues labeled:
- `good first issue` - Perfect for newcomers
- `help wanted` - Need community assistance
- `bug` - Bug fixes needed
- `enhancement` - New features
- `documentation` - Doc improvements

---

## Code Style Guidelines

### Python Style Guide

We follow **PEP 8** with some modifications:

#### General Rules

```python
# Line length: Max 100 characters (not 79)
# Use 4 spaces for indentation (no tabs)
# Use double quotes for strings (not single)

# Good
def process_transaction(transaction: Transaction, agent: AgentState) -> Result:
    """Process a transaction through the banking syndicate."""
    pass

# Bad
def process_transaction(transaction,agent):
    pass
```

#### Naming Conventions

```python
# Classes: PascalCase
class BankingSyndicate:
    pass

# Functions/methods: snake_case
def calculate_credit_score(agent_id: str) -> float:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_CREDIT_LIMIT = 10000.0
DEFAULT_TIMEOUT = 30

# Private methods: Leading underscore
def _internal_calculation(self) -> int:
    pass
```

#### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional, Tuple

def get_agent_transactions(
    agent_id: str,
    limit: int = 10,
    offset: int = 0
) -> List[Transaction]:
    """Get agent transaction history."""
    pass

def parse_response(data: Dict[str, any]) -> Optional[Result]:
    """Parse API response."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def process_transaction(
    transaction: Transaction,
    agent_state: AgentState,
    validate: bool = True
) -> EvaluationResult:
    """Process a transaction through all banking divisions.

    Args:
        transaction: The transaction to process
        agent_state: Current state of the agent
        validate: Whether to run validation checks

    Returns:
        EvaluationResult containing consensus and execution details

    Raises:
        ValidationError: If transaction fails validation
        InsufficientFundsError: If agent lacks funds

    Example:
        >>> transaction = Transaction(tx_id="TRX001", amount=50.0)
        >>> result = process_transaction(transaction, agent_state)
        >>> print(result.consensus)
        APPROVED
    """
    pass
```

#### Error Handling

Use specific exceptions:

```python
# Good
try:
    result = await process_payment(transaction)
except InsufficientFundsError as e:
    logger.error(f"Insufficient funds: {e}")
    return EvaluationResult(consensus="REJECTED", reason="insufficient_funds")
except NetworkError as e:
    logger.error(f"Network error: {e}")
    return EvaluationResult(consensus="FAILED", reason="network_error")

# Bad
try:
    result = await process_payment(transaction)
except Exception as e:
    print("Error:", e)
```

#### Logging

Use structured logging:

```python
import structlog

logger = structlog.get_logger(__name__)

# Good
logger.info(
    "transaction_processed",
    tx_id=transaction.tx_id,
    agent_id=transaction.agent_id,
    amount=transaction.amount,
    consensus=result.consensus,
    execution_time=result.execution_time
)

# Bad
print(f"Transaction {transaction.tx_id} processed")
```

### Formatting Tools

Before committing, run:

```bash
# Format code with black
black banking/

# Sort imports
isort banking/

# Check linting
flake8 banking/

# Type checking
mypy banking/
```

---

## Testing Requirements

### Test Coverage Requirements

- **New features**: Minimum 80% coverage
- **Bug fixes**: Must include regression test
- **Critical paths**: 100% coverage required

### Writing Tests

#### Unit Tests

```python
# tests/test_credit_scoring.py
import pytest
from core.credit_scoring import calculate_credit_score

class TestCreditScoring:
    """Test suite for credit scoring system."""

    def test_new_agent_has_base_score(self):
        """New agents should receive base credit score."""
        agent_state = AgentState(
            agent_id="test_001",
            transactions_count=0,
            success_rate=0.0
        )

        score = calculate_credit_score(agent_state)

        assert score == 50.0  # Base score

    def test_high_success_rate_increases_score(self):
        """Agents with high success rate get higher scores."""
        agent_state = AgentState(
            agent_id="test_002",
            transactions_count=100,
            success_rate=0.95,
            account_age_days=365
        )

        score = calculate_credit_score(agent_state)

        assert score > 80.0

    @pytest.mark.parametrize("success_rate,expected_min", [
        (0.5, 40.0),
        (0.7, 60.0),
        (0.9, 80.0),
    ])
    def test_score_correlates_with_success(self, success_rate, expected_min):
        """Credit score should correlate with success rate."""
        agent_state = AgentState(
            agent_id="test_003",
            transactions_count=50,
            success_rate=success_rate
        )

        score = calculate_credit_score(agent_state)

        assert score >= expected_min
```

#### Integration Tests

```python
# tests/test_syndicate_integration.py
import pytest
from banking_syndicate import BankingSyndicate

@pytest.mark.integration
class TestSyndicateIntegration:
    """Integration tests for banking syndicate."""

    @pytest.fixture
    async def syndicate(self):
        """Create syndicate instance for testing."""
        return BankingSyndicate(test_mode=True)

    @pytest.fixture
    async def test_agent(self, syndicate):
        """Create test agent."""
        result = await syndicate.onboard_agent(
            agent_id="integration_test_001",
            initial_deposit=100.0
        )
        return result.agent_id

    async def test_full_transaction_flow(self, syndicate, test_agent):
        """Test complete transaction from start to finish."""
        # Create transaction
        transaction = Transaction(
            tx_id="INT_TEST_001",
            agent_id=test_agent,
            amount=25.0,
            supplier="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        )

        # Process transaction
        agent_state = await syndicate.get_agent_state(test_agent)
        result = await syndicate.process_transaction(transaction, agent_state)

        # Verify results
        assert result.consensus == "APPROVED"
        assert result.execution_time < 20.0  # Within SLA
        assert result.tx_hash is not None

        # Verify state updated
        updated_state = await syndicate.get_agent_state(test_agent)
        assert updated_state.balance < agent_state.balance
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=banking --cov-report=html

# Run specific test file
pytest tests/test_credit_scoring.py -v

# Run specific test
pytest tests/test_syndicate_integration.py::TestSyndicateIntegration::test_full_transaction_flow -v

# Run only unit tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration
```

### Test Categories

Mark tests appropriately:

```python
# Unit test (no external dependencies)
def test_calculation():
    pass

# Integration test (uses external services)
@pytest.mark.integration
def test_api_integration():
    pass

# Slow test (takes > 1 second)
@pytest.mark.slow
def test_performance():
    pass

# Requires specific environment
@pytest.mark.skipif(not has_testnet_access(), reason="No testnet access")
def test_blockchain_integration():
    pass
```

---

## Pull Request Process

### Before Submitting

1. **Update from upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests locally**
   ```bash
   pytest
   ```

3. **Check code quality**
   ```bash
   black banking/
   flake8 banking/
   mypy banking/
   ```

4. **Update documentation** if needed

### Creating Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub** with:
   - Clear, descriptive title
   - Detailed description of changes
   - Reference related issues
   - Screenshots/demos if applicable

3. **Fill out PR template**

### PR Template

```markdown
## Description
[Describe your changes in detail]

## Motivation and Context
[Why is this change needed? What problem does it solve?]

## Related Issues
Fixes #123
Related to #456

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing locally
- [ ] Test coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Dependent changes merged

## Screenshots (if applicable)
[Add screenshots here]

## Additional Notes
[Any additional information]
```

### Review Process

1. **Automated checks** must pass:
   - All tests passing
   - Coverage requirements met
   - Linting checks passed
   - Type checking passed

2. **Code review** by maintainers:
   - At least 1 approval required
   - Address all review comments
   - Make requested changes

3. **Final checks**:
   - Rebase if needed
   - Squash commits if requested
   - Update documentation

4. **Merge**:
   - Maintainer will merge when ready
   - Delete branch after merge

---

## Commit Message Format

### Format

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature
feat(syndicate): add multi-signature support for high-value transactions

Implement multi-signature requirement for transactions above $10,000.
Requires 2 out of 3 division approvals.

Closes #234

# Bug fix
fix(fraud-detection): correct regex pattern for supplier validation

The previous pattern was incorrectly flagging legitimate suppliers.
Updated regex and added comprehensive test cases.

Fixes #456

# Documentation
docs(api): add examples for transaction processing endpoint

Added curl examples and Python SDK examples for the
/api/transactions/process endpoint.

# Refactor
refactor(treasury): simplify yield calculation logic

Extracted yield calculation into separate function for better
testability and maintainability. No functional changes.

# Performance
perf(database): add index on agent_id for faster queries

Added database index on frequently-queried agent_id column,
improving query performance by ~40%.
```

### Commit Best Practices

- **Keep commits atomic**: One logical change per commit
- **Write clear messages**: Explain why, not just what
- **Reference issues**: Use "Fixes #123" or "Closes #456"
- **Sign commits**: Use `git commit -s` for sign-off

---

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** for known issues
3. **Try latest version** to see if already fixed

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Initialize syndicate with '...'
2. Create transaction with '...'
3. Process transaction
4. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Error messages**
```
[Paste error messages here]
```

**Environment:**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.10.5]
- BaaS Arc version: [e.g., 0.1.0]
- Network: [e.g., Arc testnet]

**Additional context**
Any other relevant information.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Mockups, examples, or other details.

**Willing to contribute?**
- [ ] Yes, I can implement this
- [ ] Yes, with guidance
- [ ] No, but happy to test
```

---

## Community

### Communication Channels

- **GitHub Discussions**: General discussions and Q&A
- **Discord**: Real-time chat and support
- **Twitter**: Announcements and updates
- **Email**: For security issues only

### Getting Help

1. **Documentation**: Check docs first
2. **GitHub Discussions**: Ask questions
3. **Discord**: Real-time help
4. **Stack Overflow**: Tag with `baas-arc`

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website
- Social media shoutouts

### Becoming a Maintainer

Active contributors may be invited to become maintainers. Maintainers:
- Review and merge PRs
- Triage issues
- Guide project direction
- Mentor new contributors

---

## Development Tips

### Useful Commands

```bash
# Run specific test with verbose output
pytest tests/test_file.py::test_function -vv

# Watch mode for tests
pytest-watch

# Generate coverage report
pytest --cov=banking --cov-report=html
open htmlcov/index.html

# Profile performance
python -m cProfile -o profile.stats script.py
python -m pstats profile.stats

# Check type hints
mypy banking/ --strict

# Generate documentation
pdoc --html --output-dir docs banking/
```

### Debugging

```python
# Use breakpoint() for debugging
def process_transaction(transaction):
    breakpoint()  # Drops into debugger
    result = do_processing(transaction)
    return result

# Or use logging
logger.debug("Processing transaction", transaction=transaction)
```

### Testing with Real Networks

For testnet testing:

```bash
# Use testnet environment
export ARC_NETWORK=testnet
export CIRCLE_ENVIRONMENT=sandbox

# Run integration tests
pytest -m integration --testnet
```

---

## License

By contributing to BaaS Arc, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

If you have questions about contributing, reach out:
- **GitHub Discussions**: [github.com/baas-arc/discussions](https://github.com/baas-arc/discussions)
- **Discord**: [discord.gg/baas-arc](https://discord.gg/baas-arc)
- **Email**: contribute@baas-arc.dev

---

**Thank you for contributing to BaaS Arc!**

We appreciate your help in building the future of autonomous banking for AI agents.
