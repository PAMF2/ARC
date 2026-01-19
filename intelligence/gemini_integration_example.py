"""
Gemini AI Integration Examples
Demonstrates how to use Gemini AI for banking intelligence

Author: Banking Syndicate Team
For: ARC Hackathon - Google $10k GCP Credits Bonus
"""
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from intelligence.gemini_agent_advisor import GeminiAgentAdvisor
from core.transaction_types import Transaction, AgentState, TransactionType


def example_1_payment_decision():
    """
    Example 1: AI-powered payment decision analysis

    Use Case: Agent needs to decide whether to pay $500 to AWS
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Smart Payment Decision with Gemini AI")
    print("=" * 80)

    # Initialize Gemini Advisor
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("[WARNING] Warning: GEMINI_API_KEY not set. Using fallback mode.")

    advisor = GeminiAgentAdvisor(api_key=api_key)

    # Create transaction
    transaction = Transaction(
        tx_id="TX-001",
        agent_id="agent_alpha",
        tx_type=TransactionType.PURCHASE,
        amount=500.0,
        supplier="AWS",
        description="Cloud compute for AI workloads - monthly subscription"
    )

    # Agent state
    agent_state = AgentState(
        agent_id="agent_alpha",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        credit_limit=1000.0,
        available_balance=800.0,
        invested_balance=200.0,
        total_transactions=50,
        successful_transactions=45,
        failed_transactions=5
    )

    # Get AI recommendation
    print("\n[ANALYTICS] Transaction Details:")
    print(f"  Amount: ${transaction.amount}")
    print(f"  Supplier: {transaction.supplier}")
    print(f"  Description: {transaction.description}")

    print("\n[TREASURY] Agent Financial State:")
    print(f"  Available: ${agent_state.available_balance}")
    print(f"  Credit Limit: ${agent_state.credit_limit}")
    print(f"  Success Rate: {agent_state.successful_transactions}/{agent_state.total_transactions}")

    print("\n[AGENT] Analyzing with Gemini AI...")
    result = advisor.analyze_payment_decision(
        transaction=transaction.to_dict(),
        agent_state=agent_state.to_dict(),
        market_context={
            "gas_price_gwei": 25,
            "eth_price_usd": 3500,
            "aave_apy": 4.5
        }
    )

    print("\n[SUCCESS] AI RECOMMENDATION:")
    print(f"  Decision: {result['recommendation'].upper()}")
    print(f"  Confidence: {result['confidence'] * 100:.1f}%")
    print(f"  Reasoning: {result['reasoning']}")

    if result.get('optimization_tips'):
        print("\n[INFO] Optimization Tips:")
        for tip in result['optimization_tips']:
            print(f"  • {tip}")

    if result.get('risk_factors'):
        print("\n[WARNING] Risk Factors:")
        for risk in result['risk_factors']:
            print(f"  • {risk}")

    print(f"\n[GROWTH] Expected ROI: {result.get('expected_roi', 0):.1f}%")


def example_2_fraud_detection():
    """
    Example 2: AI-powered fraud detection

    Use Case: Detect suspicious transaction patterns
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Fraud Detection with Gemini AI")
    print("=" * 80)

    api_key = os.getenv('GEMINI_API_KEY')
    advisor = GeminiAgentAdvisor(api_key=api_key)

    # Suspicious transaction
    suspicious_tx = {
        "tx_id": "TX-SUSPICIOUS-001",
        "agent_id": "agent_beta",
        "tx_type": "purchase",
        "amount": 9999.0,  # Suspiciously round number
        "supplier": "0x0000000000000000000000000000000000000000",  # Null address
        "description": "URGENT! Limited time offer - act now!",  # Scam language
        "timestamp": datetime.now().isoformat()
    }

    # Agent history (normal transactions)
    agent_history = [
        {
            "tx_id": f"TX-{i}",
            "amount": 50 + (i * 10),
            "supplier": "AWS",
            "description": "Regular cloud service",
            "timestamp": datetime.now().isoformat()
        }
        for i in range(5)
    ]

    print("\n[SEARCH] Analyzing Suspicious Transaction...")
    print(f"  Amount: ${suspicious_tx['amount']}")
    print(f"  Supplier: {suspicious_tx['supplier']}")
    print(f"  Description: {suspicious_tx['description']}")

    print("\n[AGENT] Running AI Fraud Detection...")
    fraud_result = advisor.detect_fraud_patterns(
        transaction=suspicious_tx,
        agent_history=agent_history,
        global_patterns=[
            {"pattern": "round_amounts", "severity": "medium"},
            {"pattern": "null_address", "severity": "critical"},
            {"pattern": "urgent_language", "severity": "high"}
        ]
    )

    print("\n[ALERT] FRAUD ANALYSIS:")
    print(f"  Fraud Score: {fraud_result['fraud_score'] * 100:.1f}%")
    print(f"  Severity: {fraud_result.get('severity', 'unknown').upper()}")
    print(f"  Recommended Action: {fraud_result['recommended_action'].upper()}")
    print(f"  Confidence: {fraud_result.get('confidence', 0) * 100:.1f}%")

    if fraud_result.get('fraud_indicators'):
        print("\n[CRITICAL] Fraud Indicators:")
        for indicator in fraud_result['fraud_indicators']:
            print(f"  • {indicator}")

    print(f"\n[NOTE] Explanation: {fraud_result['explanation']}")


def example_3_resource_optimization():
    """
    Example 3: Resource optimization advice

    Use Case: Optimize agent's financial resources
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Resource Optimization with Gemini AI")
    print("=" * 80)

    api_key = os.getenv('GEMINI_API_KEY')
    advisor = GeminiAgentAdvisor(api_key=api_key)

    # Agent with idle funds
    agent_state = {
        "agent_id": "agent_gamma",
        "available_balance": 5000.0,  # Lots of idle cash
        "invested_balance": 500.0,
        "credit_limit": 2000.0,
        "total_spent": 10000.0,
        "total_earned": 12000.0,
        "reputation_score": 0.95
    }

    # Pending transactions
    pending_txs = [
        {
            "tx_id": "PENDING-1",
            "amount": 200.0,
            "supplier": "AWS",
            "description": "Cloud compute",
            "priority": 2
        },
        {
            "tx_id": "PENDING-2",
            "amount": 500.0,
            "supplier": "OpenAI",
            "description": "API credits",
            "priority": 1
        },
        {
            "tx_id": "PENDING-3",
            "amount": 100.0,
            "supplier": "Vercel",
            "description": "Hosting",
            "priority": 3
        }
    ]

    # Market opportunities
    market_opps = {
        "aave_usdc": {"apy": 4.5, "risk": "low"},
        "compound_dai": {"apy": 3.8, "risk": "low"},
        "curve_3pool": {"apy": 5.2, "risk": "medium"}
    }

    print("\n[TREASURY] Current Financial State:")
    print(f"  Available Balance: ${agent_state['available_balance']}")
    print(f"  Invested: ${agent_state['invested_balance']}")
    print(f"  ROI: {((agent_state['total_earned'] - agent_state['total_spent']) / agent_state['total_spent'] * 100):.1f}%")

    print(f"\n[STEP] Pending Transactions: {len(pending_txs)}")
    for tx in pending_txs:
        print(f"  • {tx['supplier']}: ${tx['amount']} (priority: {tx['priority']})")

    print("\n[AGENT] Generating Optimization Strategy...")
    optimization = advisor.optimize_resources(
        agent_state=agent_state,
        pending_transactions=pending_txs,
        market_opportunities=market_opps
    )

    print("\n[SUCCESS] OPTIMIZATION STRATEGY:")
    print(f"  Strategy: {optimization['strategy'].upper()}")
    print(f"  Risk Level: {optimization['risk_level'].upper()}")
    print(f"  Confidence: {optimization.get('confidence', 0) * 100:.1f}%")

    if optimization.get('allocation_advice'):
        print("\n[BUSINESS] Recommended Allocation:")
        alloc = optimization['allocation_advice']
        print(f"  • Immediate Transactions: {alloc.get('immediate_transactions', 0)}%")
        print(f"  • Yield Investment: {alloc.get('yield_investment', 0)}%")
        print(f"  • Reserve Buffer: {alloc.get('reserve_buffer', 0)}%")

    if optimization.get('yield_opportunities'):
        print("\n[GROWTH] Yield Opportunities:")
        for opp in optimization['yield_opportunities']:
            print(f"  • {opp.get('protocol')}: {opp.get('apy')}% APY (risk: {opp.get('risk')})")
            print(f"    Recommended: ${opp.get('recommended_amount', 0)}")

    if optimization.get('expected_gains'):
        gains = optimization['expected_gains']
        print("\n[DOLLAR] Expected Gains:")
        print(f"  • Daily: ${gains.get('daily', 0):.2f}")
        print(f"  • Weekly: ${gains.get('weekly', 0):.2f}")
        print(f"  • Monthly: ${gains.get('monthly', 0):.2f}")


def example_4_supplier_risk():
    """
    Example 4: Supplier risk assessment

    Use Case: Evaluate supplier trustworthiness
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Supplier Risk Assessment with Gemini AI")
    print("=" * 80)

    api_key = os.getenv('GEMINI_API_KEY')
    advisor = GeminiAgentAdvisor(api_key=api_key)

    # Test different suppliers
    suppliers = [
        {
            "name": "AWS",
            "address": "aws.amazon.com",
            "history": [
                {"amount": 500, "status": "success"},
                {"amount": 450, "status": "success"},
                {"amount": 520, "status": "success"}
            ]
        },
        {
            "name": "Unknown Supplier",
            "address": "0x1234567890abcdef1234567890abcdef12345678",
            "history": []
        },
        {
            "name": "Scam Corp",
            "address": "0x0000000000000000000000000000000000000000",
            "history": [
                {"amount": 10000, "status": "failed"}
            ]
        }
    ]

    for supplier in suppliers:
        print(f"\n[SEARCH] Assessing: {supplier['name']}")
        print(f"  Address: {supplier['address']}")
        print(f"  Transaction History: {len(supplier['history'])} transactions")

        assessment = advisor.assess_supplier_risk(
            supplier=supplier['address'],
            transaction_history=supplier['history'],
            market_reputation={"verified": supplier['name'] == "AWS"}
        )

        print(f"\n  [ANALYTICS] Risk Level: {assessment['risk_level'].upper()}")
        print(f"  [GROWTH] Risk Score: {assessment['risk_score'] * 100:.1f}%")
        print(f"  [TARGET] Recommendation: {assessment['recommendation'].upper()}")
        print(f"  [EMOJI] Monitor: {'Yes' if assessment.get('monitoring_suggested') else 'No'}")

        if assessment.get('risk_factors'):
            print("  [WARNING] Risk Factors:")
            for factor in assessment['risk_factors'][:3]:
                print(f"    • {factor}")


def example_5_financial_insights():
    """
    Example 5: Generate financial insights

    Use Case: Weekly performance report
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Financial Insights with Gemini AI")
    print("=" * 80)

    api_key = os.getenv('GEMINI_API_KEY')
    advisor = GeminiAgentAdvisor(api_key=api_key)

    # Agent with transaction history
    agent_state = {
        "agent_id": "agent_delta",
        "available_balance": 1500.0,
        "invested_balance": 800.0,
        "credit_limit": 1000.0,
        "total_transactions": 100,
        "successful_transactions": 92,
        "failed_transactions": 8,
        "total_spent": 15000.0,
        "total_earned": 18500.0
    }

    # Weekly transactions
    transaction_history = [
        {
            "tx_id": f"TX-{i}",
            "amount": 100 + (i * 20),
            "supplier": "AWS" if i % 2 == 0 else "OpenAI",
            "tx_type": "purchase",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        for i in range(25)
    ]

    print("\n[ANALYTICS] Generating Weekly Financial Insights...")
    print(f"  Period: Last 7 days")
    print(f"  Transactions: {len(transaction_history)}")
    print(f"  Success Rate: {agent_state['successful_transactions']}/{agent_state['total_transactions']}")

    insights = advisor.generate_financial_insights(
        agent_state=agent_state,
        transaction_history=transaction_history,
        time_period="week"
    )

    print("\n[GROWTH] PERFORMANCE SUMMARY:")
    summary = insights.get('performance_summary', {})
    print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"  ROI: {summary.get('roi', 0):.1f}%")
    print(f"  Efficiency Score: {summary.get('efficiency_score', 0) * 100:.1f}%")
    print(f"  Trend: {summary.get('trend', 'unknown').upper()}")

    if insights.get('recommendations'):
        print("\n[INFO] RECOMMENDATIONS:")
        for rec in insights['recommendations'][:5]:
            print(f"  • {rec}")

    if insights.get('warnings'):
        print("\n[WARNING] WARNINGS:")
        for warning in insights['warnings'][:3]:
            print(f"  • {warning}")

    if insights.get('opportunities'):
        print("\n[TARGET] OPPORTUNITIES:")
        for opp in insights['opportunities'][:3]:
            print(f"  • {opp}")

    if insights.get('projections'):
        proj = insights['projections']
        print("\n[CRYSTAL] PROJECTIONS (Next Period):")
        print(f"  Revenue: ${proj.get('next_period_revenue', 0):.2f}")
        print(f"  Expenses: ${proj.get('next_period_expenses', 0):.2f}")
        print(f"  Net: ${proj.get('next_period_revenue', 0) - proj.get('next_period_expenses', 0):.2f}")
        print(f"  Confidence: {proj.get('confidence', 0) * 100:.1f}%")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("[LAUNCH] GEMINI AI INTEGRATION FOR BANKING SYNDICATE")
    print("ARC Hackathon - Google $10k GCP Credits Bonus")
    print("=" * 80)

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n[WARNING] WARNING: GEMINI_API_KEY environment variable not set!")
        print("Set it with: export GEMINI_API_KEY='your-api-key'")
        print("Examples will run in fallback mode (rule-based).\n")
        input("Press Enter to continue...")

    # Run examples
    try:
        example_1_payment_decision()
        input("\nPress Enter for next example...")

        example_2_fraud_detection()
        input("\nPress Enter for next example...")

        example_3_resource_optimization()
        input("\nPress Enter for next example...")

        example_4_supplier_risk()
        input("\nPress Enter for next example...")

        example_5_financial_insights()

    except KeyboardInterrupt:
        print("\n\n[WAVE] Examples interrupted by user.")
        return

    print("\n" + "=" * 80)
    print("[SUCCESS] All examples completed!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Set GEMINI_API_KEY in your .env file")
    print("2. Integrate with banking_syndicate.py")
    print("3. Test with demo_arc_hackathon.py")
    print("4. Monitor AI performance in production")
    print("\n[TREASURY] Maximizing that $10k GCP credit bonus! [LAUNCH]")


if __name__ == "__main__":
    main()
