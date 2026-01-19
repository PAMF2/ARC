"""
Example: Integrating Validation Protocol with Banking Syndicate

This example demonstrates how to use the 6-layer validation protocol
with the existing banking syndicate for complete transaction processing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from banking_syndicate import BankingSyndicate
from validation_protocol import BankingValidationProtocol, AgentTier
from core.transaction_types import Transaction, TransactionType
from datetime import datetime
import uuid


def main():
    print("="*70)
    print("BANKING SYNDICATE + VALIDATION PROTOCOL INTEGRATION")
    print("="*70)

    # Initialize both systems
    print("\n[1] Initializing systems...")
    syndicate = BankingSyndicate()
    validation_protocol = BankingValidationProtocol(use_real_gemini=False)

    # Onboard agent
    print("\n[2] Onboarding new agent...")
    agent_id = "agent_demo_integrated"
    onboard_result = syndicate.onboard_agent(
        agent_id=agent_id,
        initial_deposit=1000.0,
        metadata={"purpose": "API payments", "owner": "DemoCompany"}
    )

    if not onboard_result.get("success"):
        print(f"[ERROR] Onboarding failed: {onboard_result}")
        return

    print(f"[SUCCESS] Agent onboarded: {agent_id}")
    agent_state = syndicate.get_agent_state(agent_id)
    print(f"  - Wallet: {agent_state.wallet_address}")
    print(f"  - Balance: ${agent_state.available_balance:.2f}")
    print(f"  - Credit Limit: ${agent_state.credit_limit:.2f}")

    # Create transaction (within credit limit)
    print("\n[3] Creating transaction...")
    transaction = Transaction(
        tx_id=f"TX-{uuid.uuid4().hex[:8].upper()}",
        agent_id=agent_id,
        tx_type=TransactionType.PURCHASE,
        amount=50.0,  # Within initial credit limit
        supplier="OpenAI",
        description="API usage payment - GPT-4",
        timestamp=datetime.now()
    )
    print(f"  - TX ID: {transaction.tx_id}")
    print(f"  - Amount: ${transaction.amount:.2f}")
    print(f"  - Supplier: {transaction.supplier}")

    # Process through banking syndicate
    print("\n[4] Processing through Banking Syndicate...")
    print("    (4 divisions analyzing: Front Office, Risk, Treasury, Clearing)")

    evaluation = syndicate.process_transaction(
        transaction=transaction,
        agent_state=agent_state,
        context={"integration": "validation_protocol"}
    )

    if evaluation.consensus != "APPROVED":
        print(f"[BLOCKED] Syndicate rejected transaction: {evaluation.consensus}")
        print(f"Blockers: {[b.reasoning for b in evaluation.blockers]}")
        return

    print(f"[OK] Syndicate approved transaction")
    print(f"  - Consensus: {evaluation.consensus}")
    print(f"  - Risk Score: {evaluation.final_risk_score:.1f}")
    print(f"  - Execution Time: {evaluation.execution_time:.2f}s")

    # Run validation protocol
    print("\n[5] Running 6-Layer Validation Protocol...")
    print("    Layer 1: KYA (Know Your Agent)")
    print("    Layer 2: Pre-Flight Checks")
    print("    Layer 3: Multi-Agent Consensus")
    print("    Layer 4: Gemini AI Fraud Detection")
    print("    Layer 5: Arc Settlement Validation")
    print("    Layer 6: Compliance & Audit")

    approved, audit_trail = validation_protocol.validate_full_transaction(
        transaction=transaction,
        agent_state=agent_state,
        division_votes=evaluation.division_votes,
        agent_history=[]
    )

    print(f"\n[{'APPROVED' if approved else 'REJECTED'}] Validation Result: {audit_trail.final_status}")
    print(f"  - Total Time: {audit_trail.total_time_ms:.2f}ms")

    # Show validation details
    print("\n[6] Validation Details:")

    if audit_trail.kya_validation:
        print(f"  [OK] KYA: {audit_trail.kya_validation['status']}")
        print(f"       Risk: {audit_trail.kya_validation['risk_score']:.1f}")

    if audit_trail.pre_flight_checks:
        print(f"  [OK] Pre-Flight: {audit_trail.pre_flight_checks['status']}")
        checks = audit_trail.pre_flight_checks.get('checks', {})
        print(f"       Checks passed: {sum(1 for v in checks.values() if v)}/{len(checks)}")

    if audit_trail.consensus_voting:
        print(f"  [OK] Consensus: {audit_trail.consensus_voting['status']}")
        print(f"       Votes: {audit_trail.consensus_voting['approved_count']}/4")

    if audit_trail.gemini_analysis:
        print(f"  [OK] Gemini AI: {audit_trail.gemini_analysis['risk_score']:.1f}% risk")
        print(f"       Fraud Probability: {audit_trail.gemini_analysis['fraud_probability']:.1f}%")

    if audit_trail.blockchain_settlement:
        print(f"  [OK] Arc Settlement: {audit_trail.blockchain_settlement['status']}")
        print(f"       Gas Estimate: {audit_trail.blockchain_settlement['gas_estimate']}")

    if audit_trail.compliance_checks:
        print(f"  [OK] Compliance: Score {audit_trail.compliance_checks['audit_score']}")

    # Agent reputation
    print("\n[7] Agent Reputation:")
    reputation = validation_protocol.get_agent_reputation(
        agent_id=agent_id,
        agent_state=agent_state,
        transaction_history=[]
    )

    print(f"  - Reputation Score: {reputation['reputation_score']:.1f}/100")
    print(f"  - Tier: {reputation['tier'].upper()}")
    print(f"  - Success Rate: {reputation['metrics']['success_rate']:.1f}%")

    tier_benefits = reputation['tier_benefits']
    print(f"  - Daily Limit: ${tier_benefits['daily_limit']:,.0f}")
    print(f"  - Transaction Fee: {tier_benefits['tx_fee']*100:.2f}%")
    print(f"  - Support: {tier_benefits['support']}")

    # Get certificate
    cert = validation_protocol.get_agent_certificate(agent_id)
    if cert:
        print("\n[8] Agent Certificate:")
        print(f"  - Certificate ID: {cert.certificate_id}")
        print(f"  - Issued: {cert.issued_date.strftime('%Y-%m-%d')}")
        print(f"  - Expires: {cert.expiry_date.strftime('%Y-%m-%d')}")
        print(f"  - Valid: {'YES' if cert.is_valid() else 'NO'}")
        print(f"  - Permissions: {', '.join(cert.permissions)}")

    # Generate compliance report
    print("\n[9] Compliance Report:")
    report = validation_protocol.generate_daily_compliance_report()

    print(f"  - Date: {report['report_date']}")
    print(f"  - Total Transactions: {report['total_transactions']}")
    print(f"  - Completed: {report['completed_count']}")
    print(f"  - Compliance Score: {report['compliance_score']:.1f}%")
    print(f"  - Avg Processing Time: {report['avg_processing_time_ms']:.2f}ms")

    # Export audit trail
    print("\n[10] Audit Trail Export:")
    audit_data = audit_trail.to_dict()
    print(f"  - Transaction ID: {audit_data['transaction_id']}")
    print(f"  - Timestamp: {audit_data['timestamp_initiated']}")
    print(f"  - Final Status: {audit_data['final_status']}")
    print(f"  - JSON Export: Available")

    # Summary
    print("\n" + "="*70)
    print("INTEGRATION SUMMARY")
    print("="*70)
    print(f"[OK] Agent Onboarded: {agent_id}")
    print(f"[OK] Transaction Processed: {transaction.tx_id}")
    print(f"[OK] Syndicate Evaluation: {evaluation.consensus}")
    print(f"[OK] Validation Protocol: {'APPROVED' if approved else 'REJECTED'}")
    print(f"[OK] Audit Trail: {audit_trail.final_status}")
    print(f"[OK] Reputation: {reputation['reputation_score']:.1f}/100 ({reputation['tier'].upper()})")
    print(f"[OK] Certificate: {cert.certificate_id if cert else 'Not issued'}")
    print(f"[OK] Compliance: {report['compliance_score']:.1f}%")
    print("="*70)

    print("\n[SUCCESS] Integration demonstration complete!")
    print("\nThe banking system now has:")
    print("  1. Banking Syndicate: 4-division transaction processing")
    print("  2. Validation Protocol: 6-layer security validation")
    print("  3. Agent Reputation: Tier-based benefits system")
    print("  4. Compliance Reporting: Audit trails and reports")
    print("  5. Fraud Detection: AI-powered risk analysis")
    print("\nReady for production deployment.")


if __name__ == "__main__":
    main()
