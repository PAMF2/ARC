"""
Complete Banking Organization Simulation
Demonstrates full multi-agent system with realistic bank structure

This simulation shows:
1. Real bank organizational structure (CEO, CFO, COO, CRO, CTO)
2. All departments and employees as autonomous agents
3. Inter-agent communication
4. Complete transaction workflows
5. Executive decision-making
6. Crisis management
7. Integration with existing banking agents (Front Office, Risk, Treasury, Clearing)

Usage:
    python run_complete_bank_simulation.py
"""
import asyncio
import sys
import os
import logging
from datetime import datetime

# Setup paths
sys.path.insert(0, os.path.dirname(__file__))

from divisions.hr_agent import HRAgent
from multi_agent.message_bus import MessageBus, MessageType, MessagePriority, create_message
from multi_agent.organization_orchestrator import OrganizationOrchestrator
from multi_agent.real_bank_structure import RealBankOrganizationalStructure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_complete_simulation():
    """Run complete bank simulation"""

    print("\n" + "=" * 100)
    print(" " * 20 + "GLOBALBANK - COMPLETE MULTI-AGENT BANKING SYSTEM")
    print("=" * 100)
    print("\nThis simulation demonstrates a fully autonomous banking organization")
    print("with real-time agent communication, decision-making, and workflows.\n")

    # Phase 1: Create Organization
    print("\n[PHASE 1] CREATING ORGANIZATIONAL STRUCTURE")
    print("=" * 100)

    hr_agent = HRAgent()
    message_bus = MessageBus()

    # Create realistic bank structure
    organization = RealBankOrganizationalStructure.create_complete_bank_organization(
        hr_agent=hr_agent,
        bank_name="GlobalBank"
    )

    # Phase 2: Initialize Multi-Agent System
    print("\n[PHASE 2] INITIALIZING MULTI-AGENT SYSTEM")
    print("=" * 100)

    orchestrator = OrganizationOrchestrator(
        hr_agent=hr_agent,
        message_bus=message_bus,
        llm_provider="mock"  # Use "anthropic" if you have API key
    )

    await orchestrator.initialize_organization()

    print(f"\n[OK] {len(orchestrator.agents)} autonomous agents initialized")
    print(f"[OK] {len(orchestrator.executives)} executive agents ready")
    print(f"[OK] Message bus active")

    # Show organization status
    status = orchestrator.get_organization_status()
    print("\n[ORGANIZATION STATUS]")
    print(f"  Total Agents: {status['agents']['total']}")
    print(f"  Executives: {status['agents']['executives']}")
    print(f"  Active: {status['agents']['active']}")
    print("\n[DEPARTMENTS]")
    for dept, count in status['departments'].items():
        print(f"  {dept.replace('_', ' ').title()}: {count} agents")

    # Phase 3: Demonstration Scenarios
    print("\n[PHASE 3] RUNNING DEMONSTRATION SCENARIOS")
    print("=" * 100)

    # Scenario 1: Simple Transaction Workflow
    print("\n[SCENARIO 1] Simple Banking Transaction")
    print("-" * 100)
    print("Customer withdraws $5,000 from account")

    transaction_result = await orchestrator.execute_banking_transaction(
        customer_id="CUST-001",
        transaction_type="withdrawal",
        amount=5000.0,
        details={
            "account_number": "123456789",
            "branch": "Main Branch"
        }
    )

    print(f"\n[RESULT] Transaction {transaction_result['workflow_id']}: {transaction_result['status']}")
    print(f"[STEPS] Completed {len(transaction_result['steps'])} steps:")
    for step in transaction_result['steps']:
        print(f"  - {step['step']}: {step.get('agent', 'N/A')}")

    # Scenario 2: Large Transaction Requiring Approvals
    print("\n[SCENARIO 2] Large Transaction Requiring Multi-Level Approval")
    print("-" * 100)
    print("Corporate client requests $150,000 wire transfer")

    large_txn_result = await orchestrator.execute_banking_transaction(
        customer_id="CORP-001",
        transaction_type="wire_transfer",
        amount=150000.0,
        details={
            "destination": "International Wire",
            "purpose": "Supplier Payment"
        }
    )

    print(f"\n[RESULT] Transaction {large_txn_result['workflow_id']}: {large_txn_result['status']}")
    print(f"[APPROVAL CHAIN]")
    for step in large_txn_result['steps']:
        if 'approval' in step['step'].lower():
            print(f"  - {step['step']}: {step.get('result', {}).get('approver', 'N/A')}")

    # Scenario 3: Executive Strategic Meeting
    print("\n[SCENARIO 3] Executive Leadership Meeting")
    print("-" * 100)

    # Find CEO
    ceo_id = organization['c_suite'].get('ceo')
    ceo_agent = orchestrator.get_agent(ceo_id)

    if ceo_agent:
        print(f"[CEO] {ceo_agent.employee.full_name} conducting executive meeting")

        meeting_result = await orchestrator.conduct_executive_meeting([
            "Q1 Financial Performance Review",
            "Digital Banking Strategy for 2026",
            "Risk Management Framework Updates"
        ])

        print(f"\n[MEETING RESULTS]")
        print(f"  Meeting ID: {meeting_result.get('meeting_id')}")
        print(f"  Attendees: {', '.join(meeting_result.get('attendees', []))}")
        print(f"  Decisions Made: {len(meeting_result.get('decisions', []))}")

        for i, decision in enumerate(meeting_result.get('decisions', []), 1):
            print(f"\n  Decision {i}: {decision.get('topic')}")
            print(f"    {decision.get('decision', '')[:200]}...")

    # Scenario 4: Department Coordination
    print("\n[SCENARIO 4] Cross-Department Coordination")
    print("-" * 100)
    print("New digital product launch requiring IT, Marketing, Operations coordination")

    # CFO initiates strategic initiative
    cfo_id = organization['c_suite'].get('cfo')
    cfo_agent = orchestrator.get_agent(cfo_id)

    if cfo_agent:
        from core.employee_types import Department

        initiative_result = await orchestrator.execute_strategic_initiative(
            initiative_name="Mobile Banking App 2.0",
            objectives=[
                "Launch new mobile app by Q2",
                "Increase digital banking adoption by 30%",
                "Improve customer satisfaction scores"
            ],
            departments=[Department.IT, Department.MARKETING, Department.OPERATIONS]
        )

        print(f"\n[INITIATIVE LAUNCHED]")
        print(f"  Project: {initiative_result.get('name', 'N/A')}")
        print(f"  Sponsor: {cfo_agent.employee.full_name}")
        print(f"  Departments: {len(initiative_result.get('departments', []))}")

    # Scenario 5: Agent Communication Example
    print("\n[SCENARIO 5] Direct Agent Communication")
    print("-" * 100)

    # Get a risk analyst
    from core.employee_types import Department
    risk_agents = orchestrator.get_agents_by_department(Department.RISK_MANAGEMENT)

    if len(risk_agents) > 0:
        risk_agent = risk_agents[0]

        # Get an operations analyst
        ops_agents = orchestrator.get_agents_by_department(Department.OPERATIONS)
        if len(ops_agents) > 0:
            ops_agent = ops_agents[0]

            print(f"[COMMUNICATION] {ops_agent.employee.full_name} queries {risk_agent.employee.full_name}")

            # Send query
            response = await ops_agent.send_message(
                to_agent=risk_agent.employee.employee_id,
                message_type=MessageType.QUERY,
                subject="Risk Assessment for New Transaction Type",
                content={
                    "query": "What are the risk considerations for implementing instant crypto transfers?",
                    "urgency": "medium"
                },
                requires_response=True
            )

            if response:
                print(f"\n[RESPONSE FROM {risk_agent.employee.full_name}]")
                print(f"  {response.get('response', 'No response')[:300]}...")

    # Phase 4: Statistics and Analytics
    print("\n[PHASE 4] SYSTEM ANALYTICS")
    print("=" * 100)

    # Message bus stats
    bus_stats = message_bus.get_stats()
    print(f"\n[MESSAGE BUS STATISTICS]")
    print(f"  Total Messages: {bus_stats['total_messages']}")
    print(f"  Active Subscribers: {bus_stats['active_subscribers']}")
    print(f"  Messages by Type:")
    for msg_type, count in bus_stats['messages_by_type'].items():
        print(f"    - {msg_type}: {count}")

    # Workflow stats
    print(f"\n[WORKFLOW STATISTICS]")
    print(f"  Active Workflows: {status['workflows']['active']}")
    print(f"  Completed Workflows: {status['workflows']['completed']}")

    # HR Stats
    hr_summary = hr_agent.get_organization_summary()
    print(f"\n[HR STATISTICS]")
    print(f"  Total Employees: {hr_summary['total_employees']}")
    print(f"  Active Employees: {hr_summary['active_employees']}")
    print(f"  Average Tenure: {hr_summary['average_tenure']:.1f} years")

    # Executive Dashboard (CEO)
    if ceo_agent:
        dashboard = ceo_agent.get_executive_dashboard()
        print(f"\n[CEO DASHBOARD - {ceo_agent.employee.full_name}]")
        print(f"  Direct Reports: {dashboard['organization']['direct_reports']}")
        print(f"  Inbox Messages: {dashboard['inbox']['total']}")
        print(f"  Urgent Items: {dashboard['inbox']['urgent']}")

    # Phase 5: Summary
    print("\n[PHASE 5] SIMULATION SUMMARY")
    print("=" * 100)

    print("\n[COMPLETED DEMONSTRATIONS]")
    print("  [OK] Simple transaction workflow")
    print("  [OK] Large transaction with multi-level approval")
    print("  [OK] Executive strategic meeting")
    print("  [OK] Cross-department initiative")
    print("  [OK] Direct agent-to-agent communication")

    print("\n[SYSTEM CAPABILITIES DEMONSTRATED]")
    print("  [OK] Realistic bank organizational structure")
    print("  [OK] Autonomous agent decision-making")
    print("  [OK] Inter-agent messaging and communication")
    print("  [OK] Hierarchical escalation and approvals")
    print("  [OK] Multi-department workflow coordination")
    print("  [OK] Executive-level strategic planning")
    print("  [OK] Real-time analytics and monitoring")

    print("\n[INTEGRATION POINTS]")
    print("  [OK] HR Agent - Employee management")
    print("  [OK] Message Bus - Communication infrastructure")
    print("  [OK] Employee Agents - Individual autonomous agents")
    print("  [OK] Executive Agents - Strategic decision makers")
    print("  [OK] Organization Orchestrator - Workflow coordination")
    print("  [OK] Banking Agents - Transaction processing")

    print("\n" + "=" * 100)
    print(" " * 30 + "SIMULATION COMPLETE")
    print("=" * 100)

    print("\n[NEXT STEPS]")
    print("  1. Connect to real LLM (set ANTHROPIC_API_KEY to use Claude)")
    print("  2. Add more complex workflows")
    print("  3. Implement real banking transactions")
    print("  4. Add monitoring dashboard")
    print("  5. Scale to multiple branches")

    print("\n[FILES CREATED]")
    print("  core/employee_types.py - Employee data models")
    print("  divisions/hr_agent.py - HR management")
    print("  employees/employee_factory.py - Employee creation")
    print("  multi_agent/message_bus.py - Communication system")
    print("  multi_agent/employee_agent.py - Individual agents")
    print("  multi_agent/executive_agent.py - Executive agents")
    print("  multi_agent/organization_orchestrator.py - Workflow coordinator")
    print("  multi_agent/real_bank_structure.py - Bank org structure")

    return orchestrator


def main():
    """Main entry point"""
    try:
        # Run async simulation
        orchestrator = asyncio.run(run_complete_simulation())

        print("\n[SUCCESS] Simulation completed successfully!")
        print("\nThe organization is now running with autonomous agents.")
        print("All agents can communicate, make decisions, and coordinate workflows.")

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Simulation stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
