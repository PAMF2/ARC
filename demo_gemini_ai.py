"""
Gemini AI Banking Demo
Live demonstration of AI-powered banking intelligence

For ARC Hackathon - $10k Google GCP Credits Bonus
"""
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Fix Unicode for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add banking to path
sys.path.insert(0, os.path.dirname(__file__))

from intelligence.gemini_agent_advisor import GeminiAgentAdvisor
from divisions.risk_compliance_agent import RiskComplianceAgent
from core.transaction_types import Transaction, AgentState, TransactionType


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title: str):
    """Print formatted section"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def demo_scenario_1_legitimate_payment():
    """
    Scenario 1: Legitimate payment to AWS
    Should be APPROVED by AI
    """
    print_header("SCENARIO 1: Legitimate AWS Payment")

    # Initialize
    api_key = os.getenv('GEMINI_API_KEY')
    advisor = GeminiAgentAdvisor(api_key=api_key)

    # Create legitimate transaction
    transaction = Transaction(
        tx_id="DEMO-001",
        agent_id="agent_alpha",
        tx_type=TransactionType.PURCHASE,
        amount=450.0,
        supplier="AWS",
        description="EC2 compute instances for AI model training - monthly subscription"
    )

    # Agent state
    agent_state = AgentState(
        agent_id="agent_alpha",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        credit_limit=1000.0,
        available_balance=2500.0,
        invested_balance=500.0,
        total_transactions=150,
        successful_transactions=145,
        failed_transactions=5
    )

    print("\n[ANALYTICS] Transaction Details:")
    print(f"   Amount: ${transaction.amount}")
    print(f"   Supplier: {transaction.supplier}")
    print(f"   Description: {transaction.description}")
    print(f"   Type: {transaction.tx_type.value}")

    print("\n[TREASURY] Agent Financial State:")
    print(f"   Available Balance: ${agent_state.available_balance}")
    print(f"   Invested: ${agent_state.invested_balance}")
    print(f"   Credit Limit: ${agent_state.credit_limit}")
    print(f"   Success Rate: {agent_state.successful_transactions}/{agent_state.total_transactions}")
    print(f"   Efficiency: {agent_state.efficiency:.2%}")

    # AI Analysis
    print_section("AI Payment Analysis")
    result = advisor.analyze_payment_decision(
        transaction=transaction.to_dict(),
        agent_state=agent_state.to_dict(),
        market_context={
            "gas_price_gwei": 22,
            "eth_price_usd": 3600,
            "aave_usdc_apy": 4.2
        }
    )

    print(f"\n[SUCCESS] RECOMMENDATION: {result['recommendation'].upper()}")
    print(f"   Confidence: {result['confidence'] * 100:.1f}%")
    print(f"   Reasoning: {result['reasoning']}")

    if result.get('optimization_tips'):
        print("\n[INFO] Optimization Tips:")
        for i, tip in enumerate(result['optimization_tips'][:3], 1):
            print(f"   {i}. {tip}")

    if result.get('risk_factors'):
        print("\n[WARNING]  Risk Factors:")
        for risk in result['risk_factors'][:3]:
            print(f"   • {risk}")

    expected_roi = result.get('expected_roi', 0)
    if expected_roi > 0:
        print(f"\n[GROWTH] Expected ROI: +{expected_roi:.1f}%")

    # Risk Compliance Check
    print_section("Risk Compliance Analysis")
    risk_agent = RiskComplianceAgent(config={'gemini_api_key': api_key})
    risk_analysis = risk_agent.analyze_transaction(transaction, agent_state)

    print(f"\n[SHIELD]  RISK DECISION: {risk_analysis.decision.upper()}")
    print(f"   Risk Score: {risk_analysis.risk_score * 100:.1f}%")
    print(f"   Reasoning: {risk_analysis.reasoning}")

    if risk_analysis.metadata.get('ai_enabled'):
        print("   ✨ AI-Enhanced Analysis: YES")


def demo_scenario_2_suspicious_transaction():
    """
    Scenario 2: Suspicious scam transaction
    Should be REJECTED by AI
    """
    print_header("SCENARIO 2: Suspicious Scam Transaction")

    api_key = os.getenv('GEMINI_API_KEY')
    advisor = GeminiAgentAdvisor(api_key=api_key)

    # Suspicious transaction
    transaction = Transaction(
        tx_id="DEMO-SCAM-001",
        agent_id="agent_beta",
        tx_type=TransactionType.PURCHASE,
        amount=9999.0,
        supplier="0x0000000000000000000000000000000000000000",
        description="URGENT LIMITED TIME OFFER! Act now to claim your prize!"
    )

    agent_state = AgentState(
        agent_id="agent_beta",
        wallet_address="0x8B4C8D3E2F1A7B5C6D9E0F1A2B3C4D5E6F7A8B9C",
        credit_limit=500.0,
        available_balance=15000.0,
        invested_balance=2000.0,
        total_transactions=75,
        successful_transactions=72,
        failed_transactions=3
    )

    print("\n[ALERT] Transaction Details:")
    print(f"   Amount: ${transaction.amount} (suspiciously round)")
    print(f"   Supplier: {transaction.supplier} (null address)")
    print(f"   Description: {transaction.description}")

    print("\n[TREASURY] Agent Financial State:")
    print(f"   Available Balance: ${agent_state.available_balance}")
    print(f"   Credit Limit: ${agent_state.credit_limit}")

    # Fraud Detection
    print_section("AI Fraud Detection")

    agent_history = [
        {
            "tx_id": f"TX-{i}",
            "amount": 50 + (i * 10),
            "supplier": "AWS" if i % 2 == 0 else "OpenAI",
            "description": "Regular cloud service payment",
            "timestamp": datetime.now().isoformat()
        }
        for i in range(10)
    ]

    fraud_result = advisor.detect_fraud_patterns(
        transaction=transaction.to_dict(),
        agent_history=agent_history
    )

    print(f"\n[ALERT] FRAUD SCORE: {fraud_result['fraud_score'] * 100:.1f}%")
    print(f"   Severity: {fraud_result.get('severity', 'unknown').upper()}")
    print(f"   Recommended Action: {fraud_result['recommended_action'].upper()}")
    print(f"   Confidence: {fraud_result.get('confidence', 0) * 100:.1f}%")

    if fraud_result.get('fraud_indicators'):
        print("\n[CRITICAL] Fraud Indicators Detected:")
        for indicator in fraud_result['fraud_indicators']:
            print(f"   • {indicator}")

    print(f"\n[NOTE] Explanation:")
    print(f"   {fraud_result['explanation']}")

    # Risk Compliance Check
    print_section("Risk Compliance Decision")
    risk_agent = RiskComplianceAgent(config={'gemini_api_key': api_key})
    risk_analysis = risk_agent.analyze_transaction(transaction, agent_state)

    print(f"\n[SHIELD]  FINAL DECISION: {risk_analysis.decision.upper()}")
    print(f"   Risk Score: {risk_analysis.risk_score * 100:.1f}%")

    if risk_analysis.alerts:
        print("\n[WARNING]  Alerts:")
        for alert in risk_analysis.alerts[:5]:
            print(f"   • {alert}")


def demo_scenario_3_resource_optimization():
    """
    Scenario 3: Agent with idle funds needs optimization advice
    """
    print_header("SCENARIO 3: Resource Optimization Strategy")

    api_key = os.getenv('GEMINI_API_KEY')
    advisor = GeminiAgentAdvisor(api_key=api_key)

    agent_state = {
        "agent_id": "agent_gamma",
        "available_balance": 8000.0,  # Lots of idle cash
        "invested_balance": 1000.0,
        "credit_limit": 2000.0,
        "total_spent": 25000.0,
        "total_earned": 32000.0,
        "reputation_score": 0.96,
        "total_transactions": 200,
        "successful_transactions": 192
    }

    pending_transactions = [
        {
            "tx_id": "PENDING-1",
            "amount": 300.0,
            "supplier": "AWS",
            "description": "Cloud compute",
            "priority": 2
        },
        {
            "tx_id": "PENDING-2",
            "amount": 800.0,
            "supplier": "OpenAI",
            "description": "GPT-4 API credits",
            "priority": 1
        },
        {
            "tx_id": "PENDING-3",
            "amount": 150.0,
            "supplier": "Vercel",
            "description": "Hosting services",
            "priority": 3
        },
        {
            "tx_id": "PENDING-4",
            "amount": 450.0,
            "supplier": "Google Cloud",
            "description": "BigQuery analytics",
            "priority": 2
        }
    ]

    market_opportunities = {
        "aave_usdc": {"apy": 4.5, "risk": "low", "tvl": 1000000000},
        "compound_dai": {"apy": 3.8, "risk": "low", "tvl": 800000000},
        "curve_3pool": {"apy": 5.2, "risk": "medium", "tvl": 500000000}
    }

    print("\n[TREASURY] Current Financial State:")
    print(f"   Available Balance: ${agent_state['available_balance']:,.2f}")
    print(f"   Invested: ${agent_state['invested_balance']:,.2f}")
    print(f"   Total Assets: ${agent_state['available_balance'] + agent_state['invested_balance']:,.2f}")
    roi = (agent_state['total_earned'] - agent_state['total_spent']) / agent_state['total_spent'] * 100
    print(f"   Historical ROI: {roi:.1f}%")
    print(f"   Success Rate: {agent_state['successful_transactions']}/{agent_state['total_transactions']} ({agent_state['successful_transactions']/agent_state['total_transactions']*100:.1f}%)")

    print(f"\n[STEP] Pending Transactions ({len(pending_transactions)}):")
    total_pending = sum(tx['amount'] for tx in pending_transactions)
    for tx in pending_transactions:
        print(f"   • {tx['supplier']}: ${tx['amount']} (priority: {tx['priority']})")
    print(f"   Total: ${total_pending}")

    print("\n[GROWTH] Available DeFi Opportunities:")
    for protocol, data in market_opportunities.items():
        print(f"   • {protocol.replace('_', ' ').title()}: {data['apy']}% APY (risk: {data['risk']})")

    # Get optimization strategy
    print_section("AI Optimization Strategy")
    optimization = advisor.optimize_resources(
        agent_state=agent_state,
        pending_transactions=pending_transactions,
        market_opportunities=market_opportunities
    )

    print(f"\n[SUCCESS] STRATEGY: {optimization['strategy'].upper()}")
    print(f"   Risk Level: {optimization['risk_level'].upper()}")
    print(f"   Confidence: {optimization.get('confidence', 0) * 100:.1f}%")

    if optimization.get('allocation_advice'):
        print("\n[BUSINESS] Recommended Fund Allocation:")
        alloc = optimization['allocation_advice']
        total_funds = agent_state['available_balance']
        print(f"   • Immediate Transactions: {alloc.get('immediate_transactions', 0)}% (${total_funds * alloc.get('immediate_transactions', 0) / 100:.2f})")
        print(f"   • Yield Investment: {alloc.get('yield_investment', 0)}% (${total_funds * alloc.get('yield_investment', 0) / 100:.2f})")
        print(f"   • Reserve Buffer: {alloc.get('reserve_buffer', 0)}% (${total_funds * alloc.get('reserve_buffer', 0) / 100:.2f})")

    if optimization.get('yield_opportunities'):
        print("\n[ANALYTICS] Recommended Yield Strategies:")
        for opp in optimization['yield_opportunities'][:3]:
            print(f"   • {opp.get('protocol', 'Unknown')}: {opp.get('apy', 0)}% APY")
            print(f"     Risk: {opp.get('risk', 'unknown')} | Amount: ${opp.get('recommended_amount', 0):.2f}")

    if optimization.get('expected_gains'):
        gains = optimization['expected_gains']
        print("\n[DOLLAR] Projected Returns:")
        print(f"   • Daily: ${gains.get('daily', 0):.2f}")
        print(f"   • Weekly: ${gains.get('weekly', 0):.2f}")
        print(f"   • Monthly: ${gains.get('monthly', 0):.2f}")
        print(f"   • Annual: ${gains.get('monthly', 0) * 12:.2f}")


def demo_ai_features_summary():
    """Summary of AI capabilities"""
    print_header("AI CAPABILITIES SUMMARY")

    print("\n[AGENT] Gemini AI Integration Features:")
    print("\n1. Smart Payment Decisions")
    print("   ✓ Analyzes transaction viability and ROI")
    print("   ✓ Considers market conditions and timing")
    print("   ✓ Provides optimization recommendations")
    print("   ✓ Suggests alternative suppliers")

    print("\n2. Advanced Fraud Detection")
    print("   ✓ Deep pattern analysis across history")
    print("   ✓ Behavioral anomaly detection")
    print("   ✓ Real-time risk scoring")
    print("   ✓ Scam language recognition")

    print("\n3. Resource Optimization")
    print("   ✓ Intelligent fund allocation")
    print("   ✓ Yield opportunity identification")
    print("   ✓ Cost savings analysis")
    print("   ✓ Transaction priority optimization")

    print("\n4. Supplier Risk Assessment")
    print("   ✓ AI-powered reputation analysis")
    print("   ✓ Historical pattern recognition")
    print("   ✓ Alternative supplier suggestions")
    print("   ✓ Continuous monitoring recommendations")

    print("\n5. Financial Insights")
    print("   ✓ Performance metrics and trends")
    print("   ✓ Spending pattern analysis")
    print("   ✓ Future projections")
    print("   ✓ Actionable recommendations")

    print("\n[ANALYTICS] Technical Details:")
    print(f"   • Model: Gemini 2.0 Flash")
    print(f"   • Response Time: <2 seconds average")
    print(f"   • Fallback: Rule-based if API unavailable")
    print(f"   • Caching: Intelligent decision caching")
    print(f"   • Integration: Seamless with risk compliance")


def main():
    """Run all demo scenarios"""
    print("\n" + "=" * 80)
    print("  [LAUNCH] GEMINI AI BANKING INTELLIGENCE DEMO")
    print("  ARC Hackathon - $10k Google GCP Credits Bonus")
    print("=" * 80)

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n[WARNING]  WARNING: GEMINI_API_KEY not set!")
        print("Demo will run in fallback mode (rule-based analysis)")
        print("\nTo enable full AI features:")
        print("1. Get API key from: https://makersuite.google.com/app/apikey")
        print("2. Set in .env file: GEMINI_API_KEY=your-key-here")
        print("3. Or export: export GEMINI_API_KEY='your-key-here'")
        print("\nPress Enter to continue with fallback mode...")
        input()
    else:
        print("\n[SUCCESS] GEMINI_API_KEY detected - Full AI features enabled!")
        print("Press Enter to start demo...")
        input()

    try:
        # Run scenarios
        demo_scenario_1_legitimate_payment()
        print("\nPress Enter for next scenario...")
        input()

        demo_scenario_2_suspicious_transaction()
        print("\nPress Enter for next scenario...")
        input()

        demo_scenario_3_resource_optimization()
        print("\nPress Enter to see feature summary...")
        input()

        demo_ai_features_summary()

    except KeyboardInterrupt:
        print("\n\n[WAVE] Demo interrupted by user.")
        return

    print("\n" + "=" * 80)
    print("  [SUCCESS] DEMO COMPLETE!")
    print("=" * 80)

    print("\n[TARGET] Next Steps:")
    print("   1. Set GEMINI_API_KEY in .env file")
    print("   2. Run: python demo_arc_hackathon.py")
    print("   3. Test with banking_ui.py dashboard")
    print("   4. Monitor AI performance metrics")
    print("   5. Deploy to maximize $10k GCP credits!")

    print("\n[EMOJI] Documentation:")
    print("   • README: intelligence/README_GEMINI_INTEGRATION.md")
    print("   • Examples: intelligence/gemini_integration_example.py")
    print("   • Tests: test_gemini_integration.py")

    print("\n[TREASURY] Built for ARC Hackathon - Maximizing AI-powered banking! [LAUNCH]\n")


if __name__ == "__main__":
    main()
