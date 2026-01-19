# Agentic Commerce Payment Flows

Complete implementation of autonomous payment systems for AI agent hackathon.

## Overview

The Agentic Commerce module extends the Banking Syndicate with specialized payment flows for AI agents:

1. **Usage-based Payments** - AI agents pay for API calls automatically
2. **Autonomous Transaction Approvals** - Multi-agent consensus for approvals
3. **Micropayment Support** - Sub-dollar USDC transactions with batching
4. **Agent-to-Agent Payments** - Direct transfers between agents
5. **API Consumption Tracking** - Automatic billing based on usage

## Architecture

```
agentic_commerce.py
├── AgenticCommerce (Main Class)
│   ├── Usage-Based Payment System
│   │   ├── track_api_call()
│   │   ├── get_api_usage_summary()
│   │   └── API pricing for: GPT-4, Claude, Gemini
│   │
│   ├── Micropayment Management
│   │   ├── Batch aggregation (threshold: $1.00)
│   │   ├── Timeout-based execution (5 minutes)
│   │   └── Fast-track processing
│   │
│   ├── Agent-to-Agent Transfers
│   │   ├── transfer_between_agents()
│   │   ├── Payment validation
│   │   └── Balance verification
│   │
│   ├── Autonomous Consensus
│   │   ├── request_autonomous_approval()
│   │   ├── Multi-agent voting (66% threshold)
│   │   └── Confidence-based decisions
│   │
│   └── Billing & Reporting
│       ├── process_usage_billing()
│       ├── get_commerce_summary()
│       └── get_system_metrics()
│
└── Data Structures
    ├── APIUsageRecord
    ├── MicropaymentBatch
    ├── AgentToAgentPayment
    └── ConsensusVote
```

## New Transaction Types

Added to `core/transaction_types.py`:

```python
class TransactionType(Enum):
    # ... existing types ...

    # Agentic Commerce Types
    API_PAYMENT = "api_payment"        # Pay for API usage
    MICROPAYMENT = "micropayment"      # Sub-dollar automated payments
    AGENT_TO_AGENT = "agent_to_agent"  # Inter-agent transactions
    USAGE_BILLING = "usage_billing"    # Usage-based billing
```

## Key Features

### 1. Usage-Based Payment System

AI agents automatically pay for API calls with per-call pricing:

```python
commerce = AgenticCommerce()

# Track API call (automatically charges agent)
usage = commerce.track_api_call(
    agent_id="ai-agent-001",
    api_endpoint="gpt-4"  # $0.03 per call
)

# Get usage summary
summary = commerce.get_api_usage_summary("ai-agent-001")
# {
#   "total_calls": 10,
#   "total_cost": 0.30,
#   "by_endpoint": {...}
# }
```

**API Pricing:**
- GPT-4: $0.03/call
- GPT-3.5-turbo: $0.002/call
- Claude-3-Opus: $0.015/call
- Claude-3-Sonnet: $0.003/call
- Gemini-Pro: $0.001/call

### 2. Micropayment Support

Automatically batches small transactions to reduce gas costs:

```python
# Small payments aggregate until threshold
for i in range(10):
    commerce.track_api_call("agent", "gemini-pro")  # $0.001 each

# Batch executes when:
# - Total >= $1.00 (threshold)
# - OR timeout reached (5 minutes)
```

**Micropayment Flow:**
1. Payment < $1.00 → Added to batch
2. Batch accumulates payments
3. Auto-executes when threshold/timeout reached
4. Single on-chain transaction for all payments

**Benefits:**
- Reduces gas costs by 10-100x
- Enables sub-cent transactions
- Automatic optimization

### 3. Agent-to-Agent Payments

Direct transfers between AI agents:

```python
payment = commerce.transfer_between_agents(
    from_agent_id="agent-001",
    to_agent_id="agent-002",
    amount=Decimal("50.0"),
    purpose="Payment for service"
)

# Returns AgentToAgentPayment with:
# - payment_id
# - status ("pending", "processing", "completed", "failed")
# - tx_hash (if completed)
# - metadata
```

**Features:**
- Balance validation
- Transfer limits
- Payment history tracking
- Automatic state updates

### 4. Autonomous Consensus

Multi-agent voting for transaction approval:

```python
approved, votes = commerce.request_autonomous_approval(
    transaction=transaction,
    voting_agents=["risk-agent", "compliance-agent", "fraud-detector"],
    timeout_seconds=30
)

# Returns:
# - approved: True/False (based on 66% threshold)
# - votes: List[ConsensusVote] with reasoning
```

**Consensus Mechanism:**
- Configurable threshold (default: 66%)
- Confidence scores per vote
- Reasoning for each decision
- Timeout protection

### 5. API Consumption Billing

Periodic billing based on accumulated usage:

```python
# Process billing for agent (respects billing cycle)
tx = commerce.process_usage_billing("agent-001")

# Force immediate billing
tx = commerce.process_usage_billing("agent-001", force=True)
```

**Billing Features:**
- Daily billing cycle (configurable)
- Aggregates all API usage
- Creates single USAGE_BILLING transaction
- Tracks billing history

## Banking Syndicate Integration

Extended `banking_syndicate.py` with agentic commerce support:

### New Methods

```python
# Process agentic commerce transactions with optimizations
evaluation = syndicate.process_agentic_commerce_transaction(
    transaction=transaction,
    agent_state=agent_state,
    skip_consensus=True  # Enable fast-track for micropayments
)

# Fast-track micropayments (< $1)
evaluation = syndicate._fast_track_micropayment(
    transaction=transaction,
    agent_state=agent_state
)
```

### Enhanced Status

```python
status = syndicate.get_syndicate_status()
# Now includes:
# - transactions_by_type: Count per transaction type
# - Full breakdown of all transaction types
```

## Usage Examples

### Complete Flow

```python
from agentic_commerce import create_agentic_commerce_system
from decimal import Decimal

# Initialize
commerce = create_agentic_commerce_system()

# Onboard agents
commerce.syndicate.onboard_agent("agent-001", initial_deposit=1000.0)
commerce.syndicate.onboard_agent("agent-002", initial_deposit=500.0)

# 1. Track API usage
commerce.track_api_call("agent-001", "gpt-4")
commerce.track_api_call("agent-001", "claude-3-sonnet")

# 2. Create micropayments
for i in range(10):
    commerce.track_api_call("agent-001", "gemini-pro")

# 3. Agent-to-agent transfer
payment = commerce.transfer_between_agents(
    "agent-001", "agent-002",
    Decimal("100"),
    "Service payment"
)

# 4. Autonomous approval
approved, votes = commerce.request_autonomous_approval(
    transaction,
    ["risk-agent", "compliance-agent"]
)

# 5. Process billing
commerce.process_usage_billing("agent-001", force=True)

# 6. Get summaries
agent_summary = commerce.get_commerce_summary("agent-001")
system_metrics = commerce.get_system_metrics()
```

### API Usage Tracking

```python
# Track with metadata
usage = commerce.track_api_call(
    "agent-001",
    "gpt-4",
    metadata={"tokens": 1500, "prompt": "code generation"}
)

# Get summary for date range
from datetime import datetime, timedelta
summary = commerce.get_api_usage_summary(
    "agent-001",
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now()
)

print(f"Weekly usage: {summary['total_calls']} calls, ${summary['total_cost']:.2f}")
```

### Micropayment Batching

```python
# Check pending batch
batch = commerce.get_pending_micropayments("agent-001")
if batch:
    print(f"Batch: {batch.batch_id}")
    print(f"Payments: {len(batch.payments)}")
    print(f"Total: ${float(batch.total_amount):.4f}")
    print(f"Status: {batch.status}")
```

### Agent Payment History

```python
# Get sent payments
sent = commerce.get_agent_payment_history("agent-001", direction="sent")

# Get received payments
received = commerce.get_agent_payment_history("agent-001", direction="received")

# Get all payments
all_payments = commerce.get_agent_payment_history("agent-001", direction="both")

for payment in sent:
    print(f"{payment.payment_id}: ${float(payment.amount):.2f} to {payment.to_agent}")
    print(f"  Status: {payment.status}, Purpose: {payment.purpose}")
```

## Testing

### Quick Test

```bash
cd banking
python quick_test.py
```

Output:
```
============================================================
AGENTIC COMMERCE - QUICK TEST
============================================================

[OK] System initialized
[1] Agent onboarded: agent-001
[2] Tracking API calls...
[3] Creating micropayments...
[4] A2A Transfer: $50.00
[5] Commerce Summary: 4 API calls, $0.0330 total
[6] System Metrics: 1 agents, 1 A2A payments

[OK] ALL TESTS PASSED
============================================================
```

### Comprehensive Test Suite

```bash
python test_agentic_commerce.py
```

Tests all features:
- ✓ Usage-based payments
- ✓ Micropayment batching
- ✓ Agent-to-agent transfers
- ✓ Autonomous consensus
- ✓ API billing
- ✓ Summary reports
- ✓ Syndicate integration

## Performance Metrics

### Micropayment Optimization

**Without batching:**
- 100 micropayments = 100 on-chain transactions
- Gas cost: ~$50-200 (depending on network)
- Processing time: ~5-10 minutes

**With batching:**
- 100 micropayments = 1 on-chain transaction
- Gas cost: ~$0.50-2.00
- Processing time: ~5-15 seconds
- **Savings: 98-99% reduction in gas costs**

### Fast-Track Processing

Micropayments < $1 can use fast-track mode:
- Skips multi-division consensus
- Simple balance validation
- Execution time: <100ms vs ~1-2s
- **10-20x faster for small transactions**

## Configuration

### Micropayment Settings

```python
commerce = AgenticCommerce()
commerce.micropayment_threshold = Decimal("2.0")  # Batch until $2
commerce.batch_timeout = timedelta(minutes=10)    # Or 10 min timeout
```

### API Pricing

```python
# Update pricing
commerce.api_pricing["custom-model"] = Decimal("0.005")

# Get current pricing
pricing = commerce.api_pricing
```

### Consensus Settings

```python
# Adjust consensus threshold
commerce.consensus_threshold = 0.75  # Require 75% approval
```

### Billing Cycle

```python
# Change billing cycle
commerce.billing_cycle = timedelta(hours=12)  # Bill every 12 hours
```

## Data Structures

### APIUsageRecord

```python
@dataclass
class APIUsageRecord:
    agent_id: str
    api_endpoint: str
    calls_count: int
    timestamp: datetime
    cost_per_call: Decimal
    total_cost: Decimal
    metadata: Dict[str, Any]
```

### MicropaymentBatch

```python
@dataclass
class MicropaymentBatch:
    batch_id: str
    agent_id: str
    payments: List[Transaction]
    total_amount: Decimal
    created_at: datetime
    executed_at: Optional[datetime]
    status: str  # pending, executing, completed, failed
```

### AgentToAgentPayment

```python
@dataclass
class AgentToAgentPayment:
    payment_id: str
    from_agent: str
    to_agent: str
    amount: Decimal
    purpose: str
    timestamp: datetime
    status: str
    metadata: Dict[str, Any]
```

### ConsensusVote

```python
@dataclass
class ConsensusVote:
    voter_agent_id: str
    vote: str  # "approve", "reject", "abstain"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    timestamp: datetime
```

## System Metrics

Get comprehensive system statistics:

```python
metrics = commerce.get_system_metrics()

# Returns:
{
    "api_tracking": {
        "total_calls": 1000,
        "total_cost": 15.50,
        "unique_agents": 25,
        "tracked_endpoints": 5
    },
    "micropayments": {
        "active_batches": 5,
        "threshold": 1.0,
        "batch_timeout_minutes": 5
    },
    "agent_to_agent": {
        "total_payments": 150,
        "completed": 145,
        "failed": 5
    },
    "consensus": {
        "threshold": 0.66,
        "total_consensus_requests": 50
    }
}
```

## Error Handling

The system handles common error cases:

```python
# Insufficient balance
payment = commerce.transfer_between_agents(...)
if payment.status == "failed":
    error = payment.metadata.get("error")
    if error == "insufficient_balance":
        print("Agent has insufficient funds")

# Agent not found
usage = commerce.track_api_call("non-existent-agent", "gpt-4")
# System creates pending usage, agent must be onboarded

# Consensus timeout
approved, votes = commerce.request_autonomous_approval(
    transaction, agents, timeout_seconds=5
)
if not approved:
    print("Consensus not reached within timeout")
```

## Integration with Banking Syndicate

The agentic commerce module seamlessly integrates with the existing banking syndicate:

1. **Uses same agent onboarding**
2. **Leverages existing divisions** (Front-Office, Risk, Treasury, Clearing)
3. **Extends transaction types** without breaking existing flows
4. **Adds optimizations** for high-volume, low-value transactions
5. **Maintains full audit trail** through syndicate logging

## Future Enhancements

Potential additions for production:

1. **Dynamic pricing** - Adjust API costs based on market rates
2. **Volume discounts** - Reduce costs for high-usage agents
3. **Credit lines** - Allow agents to exceed balance with credit
4. **Subscription models** - Fixed monthly fees for unlimited usage
5. **Multi-currency support** - Beyond USDC
6. **Advanced consensus** - ML-based voting weights
7. **Fraud detection** - Pattern analysis for suspicious activity
8. **Real-time analytics** - Live dashboards and alerts

## License

Part of the Banking Syndicate Autonomous Banking System.

## Support

For issues or questions, refer to:
- `banking/README.md` - Main banking system documentation
- `banking/quick_test.py` - Working examples
- `banking/test_agentic_commerce.py` - Comprehensive test suite
