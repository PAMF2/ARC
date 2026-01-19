# Banking Validation Protocol for AI Agents

## Overview

Production-ready 6-layer validation system providing comprehensive security, fraud detection, compliance, and audit trails for AI agent banking transactions.

## Features

### 6-Layer Validation Architecture

```
Layer 1: KYA (Know Your Agent) - Identity verification & compliance
Layer 2: Pre-Flight Checks - Balance, limits, velocity, patterns
Layer 3: Multi-Agent Consensus - 4-division unanimous voting
Layer 4: Gemini AI Fraud Detection - ML-powered risk analysis
Layer 5: Arc Settlement - Blockchain feasibility validation
Layer 6: Compliance & Audit - Complete audit trails & reporting
```

### Agent Tier System

| Tier | Daily Limit | TX Fee | Support | Features |
|------|------------|--------|---------|----------|
| **BRONZE** | $10,000 | 0.50% | Email | Basic access |
| **SILVER** | $50,000 | 0.30% | Priority | Higher limits |
| **GOLD** | $250,000 | 0.15% | 24/7 Chat | Premium features |
| **PLATINUM** | $1,000,000 | 0.05% | Dedicated | VIP treatment |

## Quick Start

### 1. Basic Usage

```python
from validation_protocol import BankingValidationProtocol

# Initialize
protocol = BankingValidationProtocol(use_real_gemini=False)

# Validate transaction
approved, audit_trail = protocol.validate_full_transaction(
    transaction=transaction,
    agent_state=agent_state,
    division_votes=division_votes
)

print(f"Status: {'APPROVED' if approved else 'REJECTED'}")
print(f"Audit: {audit_trail.to_dict()}")
```

### 2. Integration with Banking Syndicate

```python
from banking_syndicate import BankingSyndicate
from validation_protocol import BankingValidationProtocol

syndicate = BankingSyndicate()
protocol = BankingValidationProtocol()

# Process transaction
evaluation = syndicate.process_transaction(transaction, agent_state)

# Validate
approved, audit = protocol.validate_full_transaction(
    transaction, agent_state, evaluation.division_votes
)
```

### 3. Run Examples

```bash
# Basic demonstration
python validation_protocol.py

# Comprehensive tests
python test_validation_protocol.py

# Integration example
python example_validation_integration.py
```

## Implementation Details

### Layer 1: KYA Validation

```python
from validation_protocol import KYAData

kya = KYAData(
    agent_id="agent_001",
    agent_type="api_consumer",
    owner_entity="Company",
    purpose="API payments",
    jurisdiction="US",
    created_timestamp=datetime.now(),
    code_hash="sha256_hash",
    behavior_model="gemini-001",
    security_audit_url="https://audit.com",
    aml_score=90.0,
    sanctions_check="cleared",
    regulatory_approval="approved"
)

result = protocol.kya_validator.validate_agent_identity(kya)
```

**Validation Checks:**
- ✓ Code integrity (SHA-256 hash)
- ✓ Owner reputation
- ✓ AML score ≥70
- ✓ Sanctions screening
- ✓ Regulatory approval

### Layer 2: Pre-Flight Validation

```python
result = protocol.pre_flight_validator.validate_transaction(
    transaction, agent_state
)
```

**Checks:**
- ✓ Agent active status
- ✓ Certificate validity
- ✓ Sufficient balance
- ✓ Transaction limits
- ✓ Blacklist screening
- ✓ Velocity limits
- ✓ Pattern analysis

**Velocity Limits:**
- Bronze: 5/min, 50/hour, 500/day
- Silver: 20/min, 200/hour, 2000/day
- Gold: 100/min, 1000/hour, 10000/day
- Platinum: 500/min, 5000/hour, 50000/day

### Layer 3: Consensus Mechanism

```python
result = protocol.consensus_mechanism.collect_votes(division_votes)
```

**Requirements:**
- Unanimous approval (4/4 divisions)
- Front Office, Risk & Compliance, Treasury, Clearing
- Each division votes: approve/reject
- Average risk score calculated

### Layer 4: Gemini AI Fraud Detection

```python
# With real Gemini API
os.environ["GOOGLE_API_KEY"] = "your-key"
protocol = BankingValidationProtocol(use_real_gemini=True)

result = protocol.gemini_detector.analyze_transaction(
    transaction, agent_state, history
)
```

**AI Analysis:**
- Risk score (0-100)
- Fraud probability (0-100%)
- Anomaly detection
- Pattern recognition
- Recommendation (APPROVE/REVIEW/BLOCK)

**Without API:** Falls back to rule-based simulation

### Layer 5: Arc Settlement Validation

```python
result = protocol.arc_validator.validate_settlement(
    transaction, agent_state
)
```

**Checks:**
- ✓ Wallet address format
- ✓ Gas estimation
- ✓ Network availability
- ✓ Settlement feasibility

### Layer 6: Compliance & Audit

```python
# Create audit trail
audit = protocol.compliance_reporter.create_audit_trail(
    transaction, agent_id, validation_results
)

# Generate report
report = protocol.generate_daily_compliance_report()
```

**Audit Trail Includes:**
- Transaction metadata
- All layer results
- Timestamps
- Risk scores
- Decisions
- Reasoning

## Agent Reputation System

```python
reputation = protocol.get_agent_reputation(
    agent_id, agent_state, transaction_history
)
```

**Reputation Factors:**
- Transaction success rate (30%)
- Fraud score (25%)
- Compliance score (20%)
- Community rating (15%)
- System uptime (10%)

**Tier Assignment:**
- Platinum: ≥90 reputation
- Gold: ≥75 reputation
- Silver: ≥60 reputation
- Bronze: <60 reputation

## Agent Certificates

```python
# Issue certificate
cert = protocol.kya_validator.issue_agent_certificate(
    agent_id, AgentTier.GOLD
)

# Verify certificate
valid, error = protocol.kya_validator.verify_certificate(agent_id)
```

**Certificate Contents:**
- Certificate ID
- Issue/expiry dates (1 year)
- Agent tier
- Permissions list
- Transaction limits
- Cryptographic signature

## Compliance Reporting

```python
# Daily report
report = protocol.generate_daily_compliance_report()
```

**Report Includes:**
- Total transactions
- Completed vs failed
- Fraud detected
- Risk breakdown (low/medium/high)
- Compliance score
- Average processing time
- Regulatory flags

## Testing

```bash
# Run all tests
python test_validation_protocol.py
```

**Test Coverage:**
- ✓ KYA validation (various scenarios)
- ✓ Pre-flight checks (limits, velocity, patterns)
- ✓ Consensus mechanism (unanimous/partial)
- ✓ Gemini AI fraud detection
- ✓ Arc settlement validation
- ✓ Agent reputation system
- ✓ Full 6-layer validation flow
- ✓ Compliance reporting

**Expected Results:**
```
======================================================================
ALL TESTS PASSED!
======================================================================

Key Features Verified:
  [OK] Layer 1: KYA validation
  [OK] Layer 2: Pre-flight checks
  [OK] Layer 3: Multi-agent consensus
  [OK] Layer 4: Gemini AI fraud detection
  [OK] Layer 5: Arc settlement validation
  [OK] Layer 6: Compliance reporting
  [OK] Agent reputation system
  [OK] Audit trail generation
  [OK] Tier benefits system
```

## Performance

**Typical Validation Times:**
- Layer 1 (KYA): <1ms (cached)
- Layer 2 (Pre-Flight): <5ms
- Layer 3 (Consensus): <10ms
- Layer 4 (Gemini AI): 50-200ms (real) / <5ms (simulated)
- Layer 5 (Arc): <5ms
- Layer 6 (Audit): <5ms

**Total: 60-230ms with AI** | **<30ms without AI**

## Configuration

```python
# Customize velocity rules
protocol.pre_flight_validator.velocity_rules[AgentTier.GOLD] = {
    "per_minute": 200,
    "per_hour": 2000,
    "per_day": 20000
}

# Adjust consensus requirements
protocol.consensus_mechanism.required_approvals = 4

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
```

## Error Handling

```python
approved, audit_trail = protocol.validate_full_transaction(...)

if not approved:
    # Check which layer failed
    if audit_trail.kya_validation:
        print(f"KYA: {audit_trail.kya_validation['status']}")

    if audit_trail.gemini_analysis:
        risk = audit_trail.gemini_analysis['risk_score']
        print(f"AI Risk: {risk}%")
```

## Production Deployment

### Environment Variables

```bash
# Optional: Gemini AI API key
export GOOGLE_API_KEY="your-api-key"

# Optional: Logging level
export LOG_LEVEL="INFO"
```

### Best Practices

1. **Always validate** transactions through all 6 layers
2. **Store audit trails** for regulatory compliance
3. **Monitor reputation scores** and adjust tiers
4. **Review compliance reports** daily
5. **Update velocity limits** based on patterns
6. **Enable Gemini AI** for production
7. **Backup audit data** to immutable storage
8. **Monitor false positives** and tune thresholds

## Security Features

- ✓ Code integrity verification (SHA-256)
- ✓ Digital certificates with expiry
- ✓ Velocity limits (tier-based)
- ✓ Pattern detection (suspicious behavior)
- ✓ Blacklist screening (real-time)
- ✓ AI fraud detection (ML-powered)
- ✓ Audit trails (immutable)
- ✓ AML/CTF compliance

## API Reference

### Main Classes

```python
BankingValidationProtocol(use_real_gemini: bool)
KYAValidator()
PreFlightValidator(kya_validator)
ConsensusMechanism()
GeminiFraudDetector(use_real_ai: bool)
ArcSettlementValidator()
ComplianceReporter()
AgentReputationSystem()
```

### Data Classes

```python
KYAData
AgentCertificate
ValidationResult
AuditTrail
AgentTier(Enum)
ValidationStatus(Enum)
```

## Files

```
validation_protocol.py              - Main implementation (1500+ lines)
test_validation_protocol.py         - Comprehensive test suite
example_validation_integration.py   - Integration example
VALIDATION_PROTOCOL.md              - Specification document
VALIDATION_PROTOCOL_IMPLEMENTATION.md - Implementation guide
VALIDATION_README.md                - This file
```

## Integration with Existing System

The validation protocol integrates with:
- ✓ `banking_syndicate.py` - 4-division transaction processing
- ✓ `core/transaction_types.py` - Transaction data structures
- ✓ `core/config.py` - Configuration
- ✓ `intelligence/credit_scoring.py` - Credit scoring
- ✓ `blockchain/arc_integration.py` - Arc blockchain
- ✓ `intelligence/gemini_agent_advisor.py` - Gemini AI

## Support

**Documentation:**
- `VALIDATION_PROTOCOL.md` - Full specification
- `VALIDATION_PROTOCOL_IMPLEMENTATION.md` - Implementation guide
- `VALIDATION_README.md` - Quick reference

**Examples:**
- `validation_protocol.py` - Basic example
- `test_validation_protocol.py` - Test examples
- `example_validation_integration.py` - Integration example

**Testing:**
```bash
python test_validation_protocol.py
```

## Compliance

Supports:
- ✓ AML (Anti-Money Laundering)
- ✓ CTF (Counter-Terrorism Financing)
- ✓ KYC/KYA (Know Your Customer/Agent)
- ✓ Transaction Monitoring
- ✓ Audit Trails
- ✓ Regulatory Reporting

## Changelog

### Version 1.0.0 (2026-01-19)

Initial production release:
- ✓ 6-layer validation protocol
- ✓ KYA verification system
- ✓ Agent tier system (4 tiers)
- ✓ Pre-flight validation
- ✓ Multi-agent consensus
- ✓ Gemini AI fraud detection
- ✓ Arc settlement validation
- ✓ Audit trails & compliance
- ✓ Agent reputation system
- ✓ Full test coverage

## License

Part of Arc BaaS - Banking as a Service for AI Agents

---

**PRODUCTION READY - Version 1.0.0**

For questions or issues, refer to the test suite and documentation.
