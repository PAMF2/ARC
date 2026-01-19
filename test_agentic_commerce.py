"""
Test Agentic Commerce Implementation
Comprehensive test suite for hackathon demo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from decimal import Decimal
from agentic_commerce import AgenticCommerce, create_agentic_commerce_system
from banking_syndicate import BankingSyndicate
from core.transaction_types import Transaction, TransactionType
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_usage_based_payments():
    """Test 1: Usage-based payment system"""
    print_section("TEST 1: Usage-Based Payment System (API Tracking)")

    commerce = create_agentic_commerce_system()

    # Onboard test agent
    result = commerce.syndicate.onboard_agent("test-agent-001", initial_deposit=1000.0)
    print(f"[OK] Agent onboarded: {result['agent_id']}")
    print(f"   Wallet: {result['wallet_address']}")
    print(f"   Credit limit: ${result['credit_limit']:.2f}\n")

    # Track multiple API calls
    print("[ANALYTICS] Tracking API calls...")
    endpoints = ["gpt-4", "claude-3-opus", "gpt-3.5-turbo", "gemini-pro"]

    for endpoint in endpoints:
        usage = commerce.track_api_call("test-agent-001", endpoint)
        print(f"   • {endpoint}: ${float(usage.total_cost):.4f}")

    # Get usage summary
    print("\n[GROWTH] Usage Summary:")
    summary = commerce.get_api_usage_summary("test-agent-001")
    print(f"   Total calls: {summary['total_calls']}")
    print(f"   Total cost: ${summary['total_cost']:.4f}")
    print("\n   By endpoint:")
    for endpoint, data in summary['by_endpoint'].items():
        print(f"     • {endpoint}: {data['calls']} calls, ${data['cost']:.4f}")

    return commerce


def test_micropayments(commerce):
    """Test 2: Micropayment batching"""
    print_section("TEST 2: Micropayment Support (Sub-Dollar Transactions)")

    # Onboard second agent
    commerce.syndicate.onboard_agent("test-agent-002", initial_deposit=500.0)
    print("[OK] Agent 2 onboarded\n")

    # Create multiple micropayments
    print("[MONEY] Creating micropayments (< $1)...")
    for i in range(10):
        usage = commerce.track_api_call("test-agent-002", "gemini-pro")
        print(f"   • Call {i+1}: ${float(usage.total_cost):.4f}")

    # Check pending batch
    print("\n[BATCH] Checking pending batch...")
    pending = commerce.get_pending_micropayments("test-agent-002")
    if pending:
        print(f"   Batch ID: {pending.batch_id}")
        print(f"   Payments in batch: {len(pending.payments)}")
        print(f"   Total amount: ${float(pending.total_amount):.4f}")
        print(f"   Status: {pending.status}")
    else:
        print("   No pending batch (already executed)")


def test_agent_to_agent_payments(commerce):
    """Test 3: Agent-to-agent transfers"""
    print_section("TEST 3: Agent-to-Agent Payments")

    # Onboard third agent
    commerce.syndicate.onboard_agent("test-agent-003", initial_deposit=300.0)
    print("[OK] Agent 3 onboarded\n")

    # Transfer from agent 1 to agent 3
    print("[SYNC] Transferring funds between agents...")
    payment = commerce.transfer_between_agents(
        from_agent_id="test-agent-001",
        to_agent_id="test-agent-003",
        amount=Decimal("75.50"),
        purpose="Payment for AI model training service"
    )

    print(f"   Payment ID: {payment.payment_id}")
    print(f"   Status: {payment.status}")
    print(f"   Amount: ${float(payment.amount):.2f}")
    print(f"   Purpose: {payment.purpose}")

    if payment.status == "completed":
        print(f"   [OK] Transaction hash: {payment.metadata.get('tx_hash', 'N/A')}")

    # Get payment history
    print("\n[EMOJI] Payment history for agent-001:")
    history = commerce.get_agent_payment_history("test-agent-001", direction="sent")
    print(f"   Sent payments: {len(history)}")
    for p in history[:3]:  # Show first 3
        print(f"     • {p.payment_id}: ${float(p.amount):.2f} to {p.to_agent} ({p.status})")


def test_autonomous_consensus(commerce):
    """Test 4: Autonomous transaction approvals"""
    print_section("TEST 4: Autonomous Transaction Approvals (Multi-Agent Consensus)")

    # Create test transaction
    agent_state = commerce.syndicate.get_agent_state("test-agent-001")

    transaction = Transaction(
        tx_id="consensus-test-001",
        agent_id="test-agent-001",
        tx_type=TransactionType.PURCHASE,
        amount=250.0,
        supplier="0xTestSupplier",
        description="High-value purchase requiring consensus"
    )

    print("[VOTE]  Requesting consensus approval...")
    print(f"   Transaction: {transaction.tx_id}")
    print(f"   Amount: ${transaction.amount:.2f}\n")

    # Request approval from multiple voting agents
    voting_agents = [
        "risk-agent-001",
        "compliance-agent-001",
        "treasury-agent-001",
        "fraud-detector-001"
    ]

    approved, votes = commerce.request_autonomous_approval(
        transaction=transaction,
        voting_agents=voting_agents
    )

    print(f"\n{'='*60}")
    print(f"   Result: {'[OK] APPROVED' if approved else '[ERROR] REJECTED'}")
    print(f"   Votes: {sum(1 for v in votes if v.vote == 'approve')}/{len(votes)}")
    print(f"{'='*60}")


def test_api_billing(commerce):
    """Test 5: API consumption billing"""
    print_section("TEST 5: API Consumption Tracking & Billing")

    print("[CARD] Processing usage billing...")

    # Add more API usage
    for i in range(5):
        commerce.track_api_call("test-agent-001", "gpt-4")

    # Force billing cycle
    tx = commerce.process_usage_billing("test-agent-001", force=True)

    if tx:
        print(f"   Billing transaction: {tx.tx_id}")
        print(f"   Amount: ${tx.amount:.4f}")
        print(f"   Description: {tx.description}")
        print(f"   Status: {tx.state}")
    else:
        print("   No billing needed (no usage or cycle not reached)")


def test_commerce_summary(commerce):
    """Test 6: Comprehensive summary"""
    print_section("TEST 6: Commerce Summary & Metrics")

    # Agent-specific summary
    print("[ANALYTICS] Agent Commerce Summary (test-agent-001):")
    summary = commerce.get_commerce_summary("test-agent-001")

    print(f"\n   API Usage:")
    print(f"     • Total calls: {summary['api_usage']['total_calls']}")
    print(f"     • Total cost: ${summary['api_usage']['total_cost']:.4f}")

    print(f"\n   Agent-to-Agent Payments:")
    print(f"     • Sent: {summary['agent_to_agent_payments']['sent']['count']} "
          f"(${summary['agent_to_agent_payments']['sent']['total']:.2f})")
    print(f"     • Received: {summary['agent_to_agent_payments']['received']['count']} "
          f"(${summary['agent_to_agent_payments']['received']['total']:.2f})")
    print(f"     • Net: ${summary['agent_to_agent_payments']['net']:.2f}")

    # System metrics
    print("\n" + "-"*60)
    print("[GROWTH] System-Wide Metrics:")
    metrics = commerce.get_system_metrics()

    print(f"\n   API Tracking:")
    print(f"     • Total calls: {metrics['api_tracking']['total_calls']}")
    print(f"     • Total cost: ${metrics['api_tracking']['total_cost']:.4f}")
    print(f"     • Unique agents: {metrics['api_tracking']['unique_agents']}")
    print(f"     • Tracked endpoints: {metrics['api_tracking']['tracked_endpoints']}")

    print(f"\n   Micropayments:")
    print(f"     • Active batches: {metrics['micropayments']['active_batches']}")
    print(f"     • Threshold: ${metrics['micropayments']['threshold']}")

    print(f"\n   Agent-to-Agent:")
    print(f"     • Total payments: {metrics['agent_to_agent']['total_payments']}")
    print(f"     • Completed: {metrics['agent_to_agent']['completed']}")
    print(f"     • Failed: {metrics['agent_to_agent']['failed']}")

    print(f"\n   Consensus:")
    print(f"     • Threshold: {metrics['consensus']['threshold'] * 100}%")
    print(f"     • Total requests: {metrics['consensus']['total_consensus_requests']}")


def test_syndicate_integration(commerce):
    """Test 7: Banking syndicate integration"""
    print_section("TEST 7: Banking Syndicate Integration")

    print("[BANK] Syndicate Status:")
    status = commerce.syndicate.get_syndicate_status()

    print(f"   Total transactions: {status['total_transactions']}")
    print(f"   Total evaluations: {status['total_evaluations']}")
    print(f"   Agents onboarded: {status['agents_onboarded']}")

    print(f"\n   Transactions by type:")
    for tx_type, count in status.get('transactions_by_type', {}).items():
        print(f"     • {tx_type}: {count}")

    print(f"\n   Division Health:")
    for division, health in status['divisions'].items():
        print(f"     • {division}: {health['status']}")


def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("+" + "="*78 + "+")
    print("|" + " "*20 + "AGENTIC COMMERCE TEST SUITE" + " "*31 + "|")
    print("|" + " "*26 + "Hackathon Demo" + " "*38 + "|")
    print("+" + "="*78 + "+")

    try:
        # Run all tests
        commerce = test_usage_based_payments()
        test_micropayments(commerce)
        test_agent_to_agent_payments(commerce)
        test_autonomous_consensus(commerce)
        test_api_billing(commerce)
        test_commerce_summary(commerce)
        test_syndicate_integration(commerce)

        # Final summary
        print_section("ALL TESTS COMPLETED SUCCESSFULLY")
        print("Agentic Commerce System is fully operational!")
        print("\nFeatures Demonstrated:")
        print("  [X] Usage-based payment (API call tracking)")
        print("  [X] Autonomous transaction approvals (multi-agent consensus)")
        print("  [X] Micropayment support (sub-dollar USDC transactions)")
        print("  [X] Agent-to-agent payments")
        print("  [X] API consumption tracking and billing")
        print("  [X] Banking syndicate integration")
        print("\n")

    except Exception as e:
        print(f"\n[!] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
