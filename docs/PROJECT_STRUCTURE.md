# Banking Project Structure

> Comprehensive documentation of the BaaS Arc project organization

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Core Modules](#core-modules)
- [Configuration Files](#configuration-files)
- [Documentation](#documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [File Organization Guidelines](#file-organization-guidelines)

---

## Overview

BaaS Arc is organized as a modular Python project with clear separation between:

- **Core business logic** - Banking agents and transaction processing
- **Blockchain integration** - Arc, Circle, Aave interactions
- **Intelligence layer** - Gemini AI fraud detection and credit scoring
- **Division agents** - Specialized banking operations (front office, risk, treasury, clearing)
- **API layer** - REST endpoints and Swagger documentation
- **Testing** - Unit, integration, and demo tests
- **Deployment** - Docker containers and scripts

---

## Directory Structure

```
banking/
├── core/                           # Core banking logic
│   ├── __init__.py
│   ├── base_banking_agent.py      # Base agent class
│   ├── config.py                  # Configuration management
│   └── transaction_types.py       # Transaction data structures
│
├── divisions/                      # Banking division agents
│   ├── __init__.py
│   ├── front_office_agent.py      # Customer onboarding & agent cards
│   ├── risk_compliance_agent.py   # Risk assessment & fraud detection
│   ├── treasury_agent.py          # Liquidity & yield management
│   └── clearing_settlement_agent.py # Transaction settlement
│
├── blockchain/                     # Blockchain integrations
│   ├── __init__.py
│   ├── web3_connector.py          # Web3 utilities
│   ├── arc_usdc_utils.py          # Arc Network USDC operations
│   ├── circle_wallets.py          # Circle Wallets API integration
│   ├── aave_integration.py        # Aave Protocol integration
│   ├── erc4337_wallet.py          # Account abstraction wallets
│   └── CIRCLE_INTEGRATION.md      # Circle integration guide
│
├── intelligence/                   # AI/ML components
│   ├── __init__.py
│   ├── gemini_agent_advisor.py    # Gemini agent advisory
│   ├── gemini_scam_detector.py    # Real-time fraud detection
│   ├── credit_scoring.py          # Dynamic credit scoring
│   ├── gemini_integration_example.py # Usage examples
│   └── README_GEMINI_INTEGRATION.md # Gemini setup guide
│
├── scripts/                        # Utility scripts
│   ├── __init__.py
│   ├── setup.py                   # Initial setup script
│   ├── deploy.py                  # Deployment automation
│   └── monitor.py                 # System monitoring
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_blockchain.py         # Blockchain integration tests
│   └── test_syndicate.py          # Syndicate unit tests
│
├── examples/                       # Example code & demos
│   └── circle_wallet_example.py   # Circle Wallets usage example
│
├── docker/                         # Docker configuration
│   ├── README.md                  # Docker documentation
│   ├── prometheus/                # Prometheus monitoring
│   │   └── prometheus.yml
│   └── grafana/                   # Grafana dashboards
│       └── provisioning/
│           ├── dashboards/
│           └── datasources/
│
├── docs/                           # Documentation (proposed)
│   ├── api/                       # API documentation
│   ├── architecture/              # Architecture diagrams
│   ├── guides/                    # How-to guides
│   └── integration/               # Integration guides
│
├── banking_data/                   # Runtime data storage
│   ├── agents/                    # Agent state
│   ├── transactions/              # Transaction logs
│   └── analytics/                 # Analytics data
│
├── logs/                           # Application logs
├── memory/                         # Agent memory/context
└── outputs/                        # Generated outputs

# Root Level Files
├── banking_syndicate.py           # Main syndicate orchestrator
├── baas_backend.py                # FastAPI backend server
├── baas_backend_with_docs.py      # Backend with OpenAPI docs
├── banking_ui_professional.py     # Streamlit UI
├── agentic_commerce.py            # Commerce agent demo
├── validation_protocol.py         # Transaction validation
│
├── demo_arc_hackathon.py          # Arc hackathon demo
├── demo_gemini_ai.py              # Gemini AI demo
├── quick_test.py                  # Quick validation test
├── validate_demo.py               # Demo validator
│
├── swagger_ui.py                  # Swagger UI server
├── openapi.yaml                   # OpenAPI specification
│
├── docker-compose.yml             # Main compose file
├── docker-compose.monitoring.yml  # Monitoring stack
├── Dockerfile                     # Backend container
├── Dockerfile.frontend            # Frontend container
├── docker-entrypoint.sh           # Container entrypoint
├── .dockerignore                  # Docker ignore rules
│
├── requirements.txt               # Python dependencies
├── requirements_docs.txt          # Documentation dependencies
├── .env.example                   # Environment template
├── .env.docker                    # Docker environment template
├── .gitignore                     # Git ignore rules
├── .coveragerc                    # Coverage configuration
├── pytest.ini                     # Pytest configuration
│
├── Makefile                       # Build automation
├── LICENSE                        # MIT License
├── README.md                      # Project overview
└── PROJECT_STRUCTURE.md           # This file

# GitHub Workflows
.github/
└── workflows/
    └── ci.yml                     # CI/CD pipeline
```

---

## Core Modules

### 1. Banking Syndicate (`banking_syndicate.py`)

Main orchestrator that coordinates all four banking divisions.

**Key Components:**
- `BankingSyndicate` class
- Transaction processing pipeline
- Agent onboarding
- State management

**Usage:**
```python
from banking_syndicate import BankingSyndicate

syndicate = BankingSyndicate()
result = syndicate.onboard_agent(agent_id="bot_001", initial_deposit=100.0)
```

### 2. Core Module (`core/`)

Foundational classes and utilities.

#### `base_banking_agent.py`
- Base class for all banking agents
- Common methods: evaluate, communicate, log
- Agent state management

#### `config.py`
- Environment variable loading
- API key management
- Network configuration
- Default constants

#### `transaction_types.py`
- `Transaction` dataclass
- `AgentState` dataclass
- `EvaluationResult` dataclass
- Type definitions

### 3. Division Agents (`divisions/`)

Specialized banking operations.

#### Front Office (`front_office_agent.py`)
- Agent onboarding
- KYC/AML checks
- Agent card issuance
- Identity verification

#### Risk & Compliance (`risk_compliance_agent.py`)
- Gemini AI fraud detection
- Blacklist checking
- Transaction risk scoring
- Compliance validation

#### Treasury (`treasury_agent.py`)
- Liquidity management
- Aave yield optimization
- Balance monitoring
- Fund allocation (80/20 rule)

#### Clearing & Settlement (`clearing_settlement_agent.py`)
- Transaction execution
- Arc Network settlement
- ZK-proof generation
- Final confirmation

### 4. Blockchain Integration (`blockchain/`)

Smart contract and blockchain interactions.

#### `web3_connector.py`
- Web3 connection management
- Gas optimization
- Transaction signing
- Network utilities

#### `arc_usdc_utils.py`
- Arc Network RPC
- USDC contract interface
- Balance queries
- Transfer execution

#### `circle_wallets.py`
- Circle Wallets API client
- Wallet creation
- Transaction signing
- Webhook handling

#### `aave_integration.py`
- Aave Pool contract interface
- Deposit/withdrawal
- Interest rate queries
- Position management

### 5. Intelligence Layer (`intelligence/`)

AI-powered decision making.

#### `gemini_scam_detector.py`
- Real-time fraud detection
- Pattern analysis
- Risk scoring
- Recommendation generation

#### `credit_scoring.py`
- Dynamic credit scoring
- Reputation calculation
- Credit limit adjustment
- Historical analysis

### 6. API Layer

#### `baas_backend.py` / `baas_backend_with_docs.py`
- FastAPI REST endpoints
- WebSocket support
- Authentication
- Request validation

#### `swagger_ui.py` + `openapi.yaml`
- Interactive API documentation
- Endpoint testing
- Schema validation
- Example requests/responses

---

## Configuration Files

### Environment Files

#### `.env.example`
Template for local development configuration.

```bash
# Arc Network
ARC_RPC_ENDPOINT=https://rpc.arc.network
ARC_CHAIN_ID=999999

# Circle
CIRCLE_API_KEY=your_key_here
CIRCLE_ENVIRONMENT=sandbox

# Gemini AI
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Wallets
TREASURY_WALLET_ADDRESS=0x...
TREASURY_WALLET_PRIVATE_KEY=0x...
```

#### `.env.docker`
Docker-specific environment configuration with container hostnames.

### Docker Files

#### `Dockerfile`
Multi-stage Python backend container:
- Base: Python 3.11-slim
- Dependencies installation
- Application code
- Health checks

#### `Dockerfile.frontend`
Streamlit frontend container:
- Python runtime
- UI dependencies
- Port 5002 exposure

#### `docker-compose.yml`
Main services orchestration:
- Backend (FastAPI)
- Frontend (Streamlit)
- PostgreSQL database
- Redis cache
- Networking

#### `docker-compose.monitoring.yml`
Monitoring stack:
- Prometheus metrics
- Grafana dashboards
- Node exporter

### Testing Configuration

#### `pytest.ini`
Pytest configuration:
- Test discovery patterns
- Markers (unit, integration, e2e)
- Coverage settings
- Output formatting

#### `.coveragerc`
Code coverage configuration:
- Include/exclude patterns
- Branch coverage
- Report formatting

### CI/CD

#### `.github/workflows/ci.yml`
GitHub Actions pipeline:
- Linting (flake8, black)
- Testing (pytest)
- Coverage reporting
- Docker build validation

---

## Documentation

### Core Documentation (Root)

| File | Description |
|------|-------------|
| `README.md` | Main project overview with quick start |
| `ARCHITECTURE.md` | Technical architecture and design decisions |
| `CONTRIBUTING.md` | Contribution guidelines and code standards |
| `CHANGELOG.md` | Version history and release notes |
| `SECURITY.md` | Security policies and reporting |
| `LICENSE` | MIT License text |

### Feature Documentation

| File | Description |
|------|-------------|
| `ARC_IMPLEMENTATION_SUMMARY.md` | Arc Network integration details |
| `ARC_MIGRATION_GUIDE.md` | Migration from testnet to mainnet |
| `ARC_QUICK_REFERENCE.md` | Arc API quick reference |
| `CIRCLE_INTEGRATION_SUMMARY.md` | Circle integration overview |
| `GEMINI_AI_INTEGRATION_COMPLETE.md` | Gemini AI setup and usage |
| `VALIDATION_PROTOCOL.md` | Transaction validation system |

### Deployment Documentation

| File | Description |
|------|-------------|
| `DEPLOYMENT.md` | Deployment guide for all environments |
| `DOCKER_QUICKSTART.md` | Quick Docker setup guide |
| `DOCKER_DEPLOYMENT_SUMMARY.md` | Docker deployment overview |
| `DOCKER_INDEX.md` | Docker documentation index |
| `TROUBLESHOOTING.md` | Common issues and solutions |

### API Documentation

| File | Description |
|------|-------------|
| `API_DOCUMENTATION.md` | REST API reference |
| `README_SWAGGER.md` | Swagger UI usage guide |
| `SWAGGER_SUMMARY.md` | OpenAPI specification overview |
| `openapi.yaml` | OpenAPI 3.0 specification |

### Demo Documentation

| File | Description |
|------|-------------|
| `HACKATHON_ARC.md` | Complete hackathon submission |
| `HACKATHON_DEMO.md` | Demo script and scenarios |
| `HACKATHON_SUBMISSION.md` | Submission checklist |
| `DEMO_QUICKSTART.md` | Quick demo setup |
| `DEMO_CHECKLIST.md` | Pre-demo checklist |
| `QUICKSTART_JUDGES.md` | Judge evaluation guide |

### Implementation Guides

| File | Description |
|------|-------------|
| `AGENTIC_COMMERCE_README.md` | Commerce agent implementation |
| `VALIDATION_PROTOCOL_IMPLEMENTATION.md` | Validation system details |
| `VALIDATION_QUICK_START.md` | Validation quick start |
| `GEMINI_QUICK_START.md` | Gemini integration quick start |

---

## Testing

### Test Organization

```
tests/
├── __init__.py
├── test_blockchain.py          # Blockchain integration tests
├── test_syndicate.py           # Syndicate unit tests
└── fixtures/                   # Test fixtures (proposed)
    ├── agents.py               # Mock agents
    ├── transactions.py         # Sample transactions
    └── wallets.py              # Test wallets

# Root-level test files
test_agentic_commerce.py        # Commerce agent tests
test_arc_integration.py         # Arc Network integration
test_baas_integration.py        # Full system integration
test_circle_integration.py      # Circle Wallets tests
test_gemini_integration.py      # Gemini AI tests
test_swagger.py                 # API documentation tests
test_validation_protocol.py     # Validation tests
test_demo.py                    # Demo scenario tests
```

### Test Categories

#### Unit Tests
Focus: Individual components in isolation

```bash
pytest tests/test_syndicate.py -v
```

#### Integration Tests
Focus: Component interactions

```bash
pytest test_baas_integration.py -v
```

#### End-to-End Tests
Focus: Complete user flows

```bash
pytest test_demo.py -v
```

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest test_arc_integration.py -v

# With coverage
pytest --cov=. --cov-report=html

# Integration tests only
pytest -m integration

# Fast tests only
pytest -m "not slow"
```

---

## Deployment

### Local Development

```bash
# Setup
make install
python scripts/setup.py

# Run
make dev

# Test
make test
```

### Docker Deployment

```bash
# Build
make docker-build

# Start
make docker-up

# Monitor
make logs

# Stop
make docker-down
```

### Production Deployment

```bash
# Environment check
make verify

# Deploy
make prod-deploy

# Monitor
make health
```

---

## File Organization Guidelines

### Proposed Reorganization

Move files to appropriate directories for better organization:

#### Move to `tests/`
- `test_*.py` files currently in root
- Create `tests/integration/` and `tests/unit/` subdirectories

#### Move to `docs/`
- All `*.md` files except README, LICENSE, CONTRIBUTING
- Organize by category: `docs/api/`, `docs/guides/`, `docs/architecture/`

#### Keep in Root
- `README.md` - Main entry point
- `LICENSE` - License file
- `CONTRIBUTING.md` - Contribution guide
- `CHANGELOG.md` - Version history
- `Makefile` - Build automation
- `requirements.txt` - Dependencies
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Container definition
- `.env.example` - Configuration template
- `.gitignore` - Git ignore rules
- `pytest.ini` - Test configuration

#### Move to `examples/`
- `demo_*.py` files
- `quick_test.py`
- `validate_demo.py`
- `example_validation_integration.py`

#### Keep in `scripts/`
- `setup.py`
- `deploy.py`
- `monitor.py`
- Shell scripts: `run_demo.sh`, `start_baas.sh`, `verify_docker_setup.sh`
- Batch scripts: `run_demo.bat`, `start_baas.ps1`, `verify_docker_setup.bat`

### Module Guidelines

#### Creating New Modules

1. **Place in appropriate directory**
   - Core logic → `core/`
   - Banking operations → `divisions/`
   - Blockchain code → `blockchain/`
   - AI/ML → `intelligence/`

2. **Include docstrings**
   ```python
   """
   Module: description

   Purpose: what it does

   Usage:
       from module import Class
       instance = Class()
   """
   ```

3. **Add tests**
   - Create corresponding `test_*.py` in `tests/`
   - Maintain >80% coverage

4. **Update documentation**
   - Add module to this file
   - Update relevant guides
   - Add examples if applicable

#### Import Conventions

```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party
import web3
from fastapi import FastAPI

# Local
from core.config import Config
from divisions.front_office_agent import FrontOfficeAgent
```

#### File Naming

- Python modules: `lowercase_with_underscores.py`
- Classes: `PascalCase`
- Functions/methods: `lowercase_with_underscores()`
- Constants: `UPPERCASE_WITH_UNDERSCORES`
- Test files: `test_module_name.py`

---

## Best Practices

### Code Organization

1. **Single Responsibility**: Each module has one clear purpose
2. **Separation of Concerns**: UI ≠ Business Logic ≠ Data Access
3. **Dependency Injection**: Pass dependencies, don't create them
4. **Configuration Management**: Use environment variables
5. **Error Handling**: Explicit error types and messages

### Documentation

1. **README First**: Start with clear README
2. **Code Comments**: Explain why, not what
3. **API Documentation**: Keep OpenAPI spec updated
4. **Examples**: Provide working code samples
5. **Troubleshooting**: Document common issues

### Testing

1. **Test Pyramid**: Many unit tests, fewer integration tests
2. **Mock External Services**: Don't hit real APIs in tests
3. **Fixtures**: Reuse test data
4. **Coverage**: Aim for >80%
5. **CI/CD**: Automate testing

### Version Control

1. **Meaningful Commits**: Describe what and why
2. **Branch Strategy**: feature/*, bugfix/*, hotfix/*
3. **Pull Requests**: Required for main branch
4. **Code Review**: At least one approval
5. **Changelog**: Update with each release

---

## Maintenance

### Regular Tasks

- **Weekly**: Review logs, update dependencies
- **Monthly**: Security audit, performance review
- **Quarterly**: Architecture review, refactoring
- **Annually**: Major version release

### Monitoring

- **Metrics**: Track via Prometheus
- **Logs**: Centralized logging
- **Alerts**: Critical errors → immediate notification
- **Health Checks**: Automated endpoint monitoring

---

## Additional Resources

### Internal Documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API reference
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues

### External Resources
- [Arc Network Docs](https://docs.arc.network)
- [Circle Developer Docs](https://developers.circle.com)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Aave Docs](https://docs.aave.com)

---

**Last Updated**: 2026-01-19
**Version**: 1.0.0
**Maintainer**: BaaS Arc Team
