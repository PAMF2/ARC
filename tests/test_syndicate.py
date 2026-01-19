"""
Unit Tests para Banking Syndicate
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import datetime
import uuid

from core.transaction_types import Transaction, TransactionType, AgentState
from core.config import CONFIG
from intelligence.credit_scoring import CreditScoringSystem
from banking_syndicate import BankingSyndicate

class TestCreditScoring:
    """Testes para sistema de credit scoring"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.credit_system = CreditScoringSystem()
        self.agent_state = AgentState(
            agent_id="test_agent",
            wallet_address="0x123",
            credit_limit=100.0,
            available_balance=200.0,
            invested_balance=100.0
        )
    
    def test_efficiency_calculation(self):
        """Testa cálculo de eficiência"""
        # Agent com 100% success rate
        self.agent_state.total_transactions = 10
        self.agent_state.successful_transactions = 10
        
        efficiency = self.credit_system.calculate_efficiency(self.agent_state)
        
        assert 0.0 <= efficiency <= 1.0
        assert efficiency > 0.5  # Success rate alto = eficiência alta
    
    def test_credit_limit_increase(self):
        """Testa aumento de limite de crédito"""
        self.agent_state.total_transactions = 5
        self.agent_state.successful_transactions = 5
        
        old_limit = self.agent_state.credit_limit
        new_limit = self.credit_system.update_credit_limit(self.agent_state)
        
        assert new_limit >= old_limit  # Limite nunca diminui com sucesso
        assert new_limit <= CONFIG.MAX_CREDIT_LIMIT
    
    def test_reputation_score(self):
        """Testa cálculo de reputation score"""
        self.agent_state.total_transactions = 20
        self.agent_state.successful_transactions = 18
        
        reputation = self.credit_system.calculate_reputation_score(self.agent_state)
        
        assert 0.0 <= reputation <= 1.0
        assert reputation > 0.7  # Alta taxa de sucesso

class TestBankingSyndicate:
    """Testes para Banking Syndicate"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.syndicate = BankingSyndicate()
    
    def test_onboard_agent(self):
        """Testa onboarding de agente"""
        result = self.syndicate.onboard_agent(
            agent_id="test_agent_001",
            initial_deposit=100.0
        )
        
        assert result["success"] == True
        assert "wallet_address" in result
        assert result["credit_limit"] == CONFIG.DEFAULT_CREDIT_LIMIT
    
    def test_successful_transaction(self):
        """Testa transação bem-sucedida"""
        # Onboard agent
        agent_id = "test_agent_002"
        self.syndicate.onboard_agent(agent_id, initial_deposit=200.0)
        agent_state = self.syndicate.get_agent_state(agent_id)
        
        # Create transaction
        tx = Transaction(
            tx_id=str(uuid.uuid4()),
            agent_id=agent_id,
            tx_type=TransactionType.PURCHASE,
            amount=50.0,
            supplier="AWS",
            description="Test purchase"
        )
        
        # Process
        evaluation = self.syndicate.process_transaction(tx, agent_state)
        
        assert evaluation.consensus == "APPROVED"
        assert tx.tx_hash is not None
    
    def test_blocked_transaction_credit_limit(self):
        """Testa transação bloqueada por limite de crédito"""
        # Onboard agent
        agent_id = "test_agent_003"
        self.syndicate.onboard_agent(agent_id, initial_deposit=50.0)
        agent_state = self.syndicate.get_agent_state(agent_id)
        
        # Transaction exceeds limit
        tx = Transaction(
            tx_id=str(uuid.uuid4()),
            agent_id=agent_id,
            tx_type=TransactionType.PURCHASE,
            amount=150.0,  # More than credit limit
            supplier="AWS",
            description="Large purchase"
        )
        
        # Process
        evaluation = self.syndicate.process_transaction(tx, agent_state)
        
        assert evaluation.consensus == "BLOCKED"
        assert len(evaluation.blockers) > 0
    
    def test_blocked_transaction_blacklist(self):
        """Testa transação bloqueada por blacklist"""
        # Onboard agent
        agent_id = "test_agent_004"
        self.syndicate.onboard_agent(agent_id, initial_deposit=100.0)
        agent_state = self.syndicate.get_agent_state(agent_id)
        
        # Blacklisted supplier
        tx = Transaction(
            tx_id=str(uuid.uuid4()),
            agent_id=agent_id,
            tx_type=TransactionType.PURCHASE,
            amount=10.0,
            supplier="0x0000000000000000000000000000000000000000",
            description="Test"
        )
        
        # Process
        evaluation = self.syndicate.process_transaction(tx, agent_state)
        
        assert evaluation.consensus == "BLOCKED"
    
    def test_performance_report(self):
        """Testa geração de relatório de performance"""
        # Onboard agent
        agent_id = "test_agent_005"
        self.syndicate.onboard_agent(agent_id, initial_deposit=100.0)
        
        # Get report
        report = self.syndicate.get_performance_report(agent_id)
        
        assert "success_rate" in report
        assert "efficiency" in report
        assert "reputation_score" in report

class TestAgentState:
    """Testes para AgentState"""
    
    def test_efficiency_property(self):
        """Testa property efficiency"""
        agent = AgentState(
            agent_id="test",
            wallet_address="0x123",
            credit_limit=100.0,
            available_balance=100.0,
            invested_balance=0.0,
            total_transactions=10,
            successful_transactions=8,
            total_spent=100.0,
            total_earned=110.0
        )
        
        efficiency = agent.efficiency
        
        assert 0.0 <= efficiency <= 1.0
    
    def test_total_balance_property(self):
        """Testa property total_balance"""
        agent = AgentState(
            agent_id="test",
            wallet_address="0x123",
            credit_limit=100.0,
            available_balance=150.0,
            invested_balance=50.0
        )
        
        assert agent.total_balance == 200.0

if __name__ == "__main__":
    # Run tests
    print("Running Banking Syndicate Tests...")
    pytest.main([__file__, "-v"])
