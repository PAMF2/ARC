"""Quick test of agentic commerce - no unicode"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_commerce import create_agentic_commerce_system
from decimal import Decimal

def main():
    print('='*60)
    print('AGENTIC COMMERCE - QUICK TEST')
    print('='*60 + '\n')

    commerce = create_agentic_commerce_system()
    print('[OK] System initialized\n')

    # Test 1: Onboarding
    result = commerce.syndicate.onboard_agent('agent-001', initial_deposit=1000.0)
    print(f'[1] Agent onboarded: {result["agent_id"]}')
    print(f'    Wallet: {result["wallet_address"]}\n')

    # Test 2: API Tracking
    print('[2] Tracking API calls...')
    usage = commerce.track_api_call('agent-001', 'gpt-4')
    print(f'    gpt-4 call cost: ${float(usage.total_cost):.4f}\n')

    # Test 3: Micropayments
    print('[3] Creating micropayments...')
    for i in range(3):
        commerce.track_api_call('agent-001', 'gemini-pro')
    print('    3 micropayments created\n')

    # Test 4: Agent-to-Agent Transfer
    commerce.syndicate.onboard_agent('agent-002', initial_deposit=500.0)
    payment = commerce.transfer_between_agents('agent-001', 'agent-002', Decimal('50'), 'test payment')
    print(f'[4] A2A Transfer: ${float(payment.amount):.2f}')
    print(f'    Status: {payment.status}\n')

    # Test 5: Summary
    summary = commerce.get_commerce_summary('agent-001')
    print('[5] Commerce Summary:')
    print(f'    API calls: {summary["api_usage"]["total_calls"]}')
    print(f'    API cost: ${summary["api_usage"]["total_cost"]:.4f}')
    print(f'    A2A payments sent: {summary["agent_to_agent_payments"]["sent"]["count"]}\n')

    # System metrics
    metrics = commerce.get_system_metrics()
    print('[6] System Metrics:')
    print(f'    Total API calls: {metrics["api_tracking"]["total_calls"]}')
    print(f'    Total agents: {metrics["api_tracking"]["unique_agents"]}')
    print(f'    A2A payments: {metrics["agent_to_agent"]["total_payments"]}\n')

    print('='*60)
    print('[OK] ALL TESTS PASSED')
    print('='*60)

if __name__ == '__main__':
    main()
