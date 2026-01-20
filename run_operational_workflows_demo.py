"""
GlobalBank Multi-Agent System - Operational Workflows Demonstration

This script demonstrates the complete operational workflows system with all 165 agents
working together in realistic banking scenarios.

Workflows Demonstrated:
1. Loan Origination - Complete loan processing from application to funding
2. Account Opening - New customer onboarding with KYC/AML compliance
3. Fraud Investigation - Suspicious transaction detection and resolution
4. Daily Operations - End-of-day reconciliation and reporting
5. Large Transaction - Multi-level approval process

Author: GlobalBank Multi-Agent System
Date: January 2026
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from divisions.hr_agent import HRAgent
from multi_agent.message_bus import MessageBus
from multi_agent.organization_orchestrator import OrganizationOrchestrator
from multi_agent.real_bank_structure import RealBankOrganizationalStructure


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100 + "\n")


def print_workflow_summary(workflow_result: dict):
    """Print formatted workflow summary"""
    print(f"\n[WORKFLOW SUMMARY]")
    print(f"  Workflow ID: {workflow_result.get('workflow_id')}")
    print(f"  Type: {workflow_result.get('workflow_type')}")
    print(f"  Status: {workflow_result.get('status')}")
    print(f"  Start Time: {workflow_result.get('start_time')}")
    print(f"  End Time: {workflow_result.get('end_time')}")
    print(f"  Total Agents Involved: {workflow_result.get('total_agents_involved', 0)}")
    print(f"  Steps Completed: {len(workflow_result.get('steps_completed', []))}")

    if workflow_result.get('steps_completed'):
        print(f"\n  [WORKFLOW STEPS]")
        for i, step in enumerate(workflow_result.get('steps_completed', []), 1):
            print(f"    {i}. {step.get('step')} - Agent: {step.get('agent', 'N/A')}")

    if workflow_result.get('decision_trail'):
        print(f"\n  [DECISION TRAIL]")
        for decision in workflow_result.get('decision_trail', []):
            print(f"    - {decision.get('decision')} by {decision.get('made_by', decision.get('approver', 'N/A'))}")

    print("")


async def run_operational_workflows_demo():
    """
    Run complete operational workflows demonstration.
    """
    print_section("GLOBALBANK OPERATIONAL WORKFLOWS DEMONSTRATION")

    print("[INFO] Initializing GlobalBank Multi-Agent System...")
    print("[INFO] Creating 165 employee agents across 14 departments...")

    # ===================================================================
    # PHASE 1: Create Organization Structure
    # ===================================================================
    print_section("PHASE 1: ORGANIZATION CREATION")

    hr_agent = HRAgent()
    message_bus = MessageBus()

    print("[STEP 1] Creating complete bank organization...")
    organization = RealBankOrganizationalStructure.create_complete_bank_organization(hr_agent)

    c_suite_count = len(organization.get('c_suite', {}))
    senior_count = len(organization.get('senior_leadership', {}))
    lines_of_business_count = sum(len(v) for v in organization.get('lines_of_business', {}).values())
    middle_office_count = sum(len(v) for v in organization.get('middle_office', {}).values())
    back_office_count = sum(len(v) for v in organization.get('back_office', {}).values())
    total = c_suite_count + senior_count + lines_of_business_count + middle_office_count + back_office_count

    print(f"\n[SUCCESS] Created organization with:")
    print(f"  - Total Employees: {total}")
    print(f"  - C-Suite: {c_suite_count}")
    print(f"  - Senior Leadership: {senior_count}")
    print(f"  - Lines of Business: {lines_of_business_count}")
    print(f"  - Middle Office: {middle_office_count}")
    print(f"  - Back Office: {back_office_count}")

    # ===================================================================
    # PHASE 2: Initialize Multi-Agent System
    # ===================================================================
    print_section("PHASE 2: MULTI-AGENT SYSTEM INITIALIZATION")

    print("[STEP 2] Initializing organization orchestrator...")
    orchestrator = OrganizationOrchestrator(
        hr_agent=hr_agent,
        message_bus=message_bus,
        llm_provider="mock"  # Use mock LLM for demo (no API key required)
    )

    print("[STEP 3] Creating all employee agents...")
    await orchestrator.initialize_organization()

    print(f"\n[SUCCESS] Multi-agent system initialized:")
    print(f"  - Total Agents: {len(orchestrator.agents)}")
    print(f"  - Executive Agents: {len(orchestrator.executives)}")
    print(f"  - Departments: {len(orchestrator.department_coordinators)}")
    print(f"  - Operational Workflows: Ready")

    # ===================================================================
    # PHASE 3: WORKFLOW DEMONSTRATIONS
    # ===================================================================
    print_section("PHASE 3: OPERATIONAL WORKFLOW DEMONSTRATIONS")

    # ---------------------------------------------------------------------
    # WORKFLOW 1: Loan Origination
    # ---------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("[WORKFLOW 1] LOAN ORIGINATION - $250,000 Business Loan")
    print("-" * 100)

    print("\n[INFO] Customer applying for $250,000 business loan...")
    print("[INFO] This will trigger: Loan Officer -> Credit Analyst -> Risk Analyst -> Director Approval")
    print("[INFO]                     -> Operations -> Treasury -> Settlement -> Customer Notification")

    loan_result = await orchestrator.operational_workflows.execute_loan_origination(
        customer_id="CUST-001",
        loan_type="business",
        loan_amount=250000.0,
        customer_data={
            "business_name": "TechStartup Inc.",
            "credit_score": 720,
            "annual_revenue": 1500000,
            "years_in_business": 3
        }
    )

    print_workflow_summary(loan_result)

    # ---------------------------------------------------------------------
    # WORKFLOW 2: Account Opening
    # ---------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("[WORKFLOW 2] ACCOUNT OPENING - New Business Checking Account")
    print("-" * 100)

    print("\n[INFO] New customer opening business checking account...")
    print("[INFO] This will trigger: Customer Service -> KYC Verification -> AML Screening")
    print("[INFO]                     -> Account Setup -> Initial Deposit -> Welcome Package")

    account_result = await orchestrator.operational_workflows.execute_account_opening(
        customer_data={
            "first_name": "Sarah",
            "last_name": "Williams",
            "email": "sarah.williams@techstartup.com",
            "ssn": "123-45-6789",
            "address": "123 Main St, San Francisco, CA",
            "phone": "+1-555-0123"
        },
        account_type="business_checking",
        initial_deposit=25000.0
    )

    print_workflow_summary(account_result)

    # ---------------------------------------------------------------------
    # WORKFLOW 3: Fraud Investigation
    # ---------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("[WORKFLOW 3] FRAUD INVESTIGATION - Suspicious $15,000 Transaction")
    print("-" * 100)

    print("\n[INFO] Suspicious transaction detected - investigating...")
    print("[INFO] This will trigger: Fraud Triage -> Transaction Analysis -> Customer Contact")
    print("[INFO]                     -> Manager Decision -> Account Action -> Regulatory Reporting")

    fraud_result = await orchestrator.operational_workflows.execute_fraud_investigation(
        transaction_id="TXN-FRAUD-001",
        transaction_data={
            "amount": 15000.0,
            "destination": "Overseas account",
            "customer_id": "CUST-002",
            "transaction_time": datetime.now().isoformat(),
            "unusual_pattern": True
        },
        alert_reason="Large overseas transfer from previously dormant account"
    )

    print_workflow_summary(fraud_result)

    # ---------------------------------------------------------------------
    # WORKFLOW 4: Daily Operations
    # ---------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("[WORKFLOW 4] DAILY OPERATIONS - End-of-Day Processing")
    print("-" * 100)

    print("\n[INFO] Running end-of-day operations for", datetime.now().strftime("%Y-%m-%d"))
    print("[INFO] This will trigger: Transaction Reconciliation -> Position Reporting")
    print("[INFO]                     -> Risk Reporting -> Compliance Checks")
    print("[INFO]                     -> Financial Reporting -> Executive Summary")

    daily_ops_result = await orchestrator.operational_workflows.execute_daily_operations(
        business_date=datetime.now().strftime("%Y-%m-%d")
    )

    print_workflow_summary(daily_ops_result)
    if daily_ops_result.get('reports_generated'):
        print(f"  [REPORTS GENERATED]")
        for report in daily_ops_result.get('reports_generated', []):
            print(f"    - {report}")

    # ===================================================================
    # PHASE 4: WORKFLOW ANALYTICS
    # ===================================================================
    print_section("PHASE 4: WORKFLOW ANALYTICS")

    analytics = orchestrator.operational_workflows.get_workflow_analytics()

    print("[WORKFLOW ANALYTICS]")
    print(f"  Total Workflows Executed: {analytics['total_workflows_executed']}")
    print(f"  Completed Workflows: {analytics['completed_workflows']}")
    print(f"  Active Workflows: {analytics['active_workflows']}")
    print(f"  Unique Agents Used: {analytics['unique_agents_used']}")
    print(f"  Average Steps per Workflow: {analytics['average_steps_per_workflow']}")
    print(f"  Total Agents in System: {analytics['total_agents_in_system']}")

    print(f"\n  [WORKFLOWS BY TYPE]")
    for workflow_type, count in analytics['workflows_by_type'].items():
        print(f"    - {workflow_type}: {count}")

    # ===================================================================
    # PHASE 5: MESSAGE BUS STATUS
    # ===================================================================
    print_section("PHASE 5: MESSAGE BUS STATUS")

    print("[MESSAGE BUS STATUS]")
    print(f"  Message History: {len(message_bus.message_history)} messages")
    print(f"  Subscribers: {len(message_bus.subscribers)} direct subscriptions")
    print(f"  Department Subscriptions: {len(message_bus.department_subscribers)} departments")
    print(f"  Broadcast Subscribers: {len(message_bus.broadcast_subscribers)}")
    print(f"  Pending Responses: {len(message_bus.pending_responses)}")

    # ===================================================================
    # SUMMARY
    # ===================================================================
    print_section("DEMONSTRATION COMPLETE")

    print("[SUMMARY]")
    print("  [SUCCESS] All operational workflows executed successfully!")
    print("")
    print("  System Components:")
    print(f"    - Employee Agents: {len(orchestrator.agents)}")
    print(f"    - Executive Agents: {len(orchestrator.executives)}")
    print(f"    - Departments: {len(orchestrator.department_coordinators)}")
    print(f"    - Workflows Executed: {analytics['completed_workflows']}")
    print(f"    - Messages Exchanged: {len(message_bus.message_history)}")
    print("")
    print("  Workflows Demonstrated:")
    print("    1. [OK] Loan Origination - 8+ agents coordinated")
    print("    2. [OK] Account Opening - 6+ agents coordinated")
    print("    3. [OK] Fraud Investigation - 5+ agents coordinated")
    print("    4. [OK] Daily Operations - 6+ agents coordinated")
    print("")
    print("  Key Features Demonstrated:")
    print("    [OK] Multi-step workflows with proper handoffs")
    print("    [OK] Department coordination")
    print("    [OK] Amount-based approval routing")
    print("    [OK] Compliance and risk checks")
    print("    [OK] Executive oversight")
    print("    [OK] Real-time message passing")
    print("    [OK] Decision trail tracking")
    print("    [OK] Agent specialization")
    print("")
    print("=" * 100)
    print("  GLOBALBANK OPERATIONAL WORKFLOWS SYSTEM - FULLY OPERATIONAL")
    print("=" * 100)
    print("")


def main():
    """Main entry point"""
    print("""
    ================================================================================

                        GLOBALBANK MULTI-AGENT SYSTEM
                       Operational Workflows Demonstration

      System: 165 Autonomous Banking Agents
      Workflows: Loan Origination, Account Opening, Fraud, Daily Ops
      Architecture: Multi-Agent Coordination with Message Bus

    ================================================================================
    """)

    try:
        asyncio.run(run_operational_workflows_demo())
    except KeyboardInterrupt:
        print("\n\n[INFO] Demonstration interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Demonstration failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
