"""
Banking Syndicate Coordinator
Coordinates the 4 banking divisions and executes transaction lifecycle

Transaction Lifecycle (T+0 to T+15s):
- T+0s: Agent requests transaction
- T+2s: Risk & Compliance validates
- T+5s: Treasury checks/withdraws liquidity
- T+10s: Clearing executes on-chain
- T+15s: Post-trade audit and credit score update
"""
from typing import Dict, Any, Optional, List
import time
from datetime import datetime
import logging
import sys
import os
import uuid

# Support both module and script execution
try:
    from .core.transaction_types import (
        Transaction, AgentState, BankingAnalysis, 
        TransactionEvaluation, TransactionType
    )
    from .core.config import CONFIG, AGENT_ROLES, TRANSACTION_STATES, DECISION_TYPES
    from .divisions.front_office_agent import FrontOfficeAgent
    from .divisions.risk_compliance_agent import RiskComplianceAgent
    from .divisions.treasury_agent import TreasuryAgent
    from .divisions.clearing_settlement_agent import ClearingSettlementAgent
    from .intelligence.credit_scoring import CreditScoringSystem
except ImportError:
    # Direct imports when run as script
    sys.path.insert(0, os.path.dirname(__file__))
    from core.transaction_types import (
        Transaction, AgentState, BankingAnalysis, 
        TransactionEvaluation, TransactionType
    )
    from core.config import CONFIG, AGENT_ROLES, TRANSACTION_STATES, DECISION_TYPES
    from divisions.front_office_agent import FrontOfficeAgent
    from divisions.risk_compliance_agent import RiskComplianceAgent
    from divisions.treasury_agent import TreasuryAgent
    from divisions.clearing_settlement_agent import ClearingSettlementAgent
    from intelligence.credit_scoring import CreditScoringSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankingSyndicate:
    """
    Autonomous Banking Syndicate

    Coordinates 4 divisions:
    - Front-Office: Onboarding and Agent Cards
    - Risk & Compliance: Security validation
    - Treasury: Liquidity and yield management
    - Clearing: On-chain execution
    """

    def __init__(self):
        """Initializes the syndicate with all divisions"""
        logger.info("[BANK] Initializing Autonomous Banking Syndicate...")
        
        # Initialize divisions
        self.front_office = FrontOfficeAgent()
        self.risk = RiskComplianceAgent()
        self.treasury = TreasuryAgent()
        self.clearing = ClearingSettlementAgent()

        # Credit scoring system
        self.credit_system = CreditScoringSystem()

        # State
        self.transaction_log = []
        self.evaluations = []
        
        logger.info("[SUCCESS] Banking Syndicate initialized with 4 divisions")
    
    def process_transaction(
        self,
        transaction: Transaction,
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None
    ) -> TransactionEvaluation:
        """
        Processes transaction through complete lifecycle (T+0 to T+15s)

        Args:
            transaction: Transaction to process
            agent_state: Requesting agent's state
            context: Additional context

        Returns:
            TransactionEvaluation with complete result
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[LAUNCH] Processing transaction {transaction.tx_id}")
        logger.info(f"Agent: {agent_state.agent_id} | Amount: ${transaction.amount:.2f}")
        logger.info(f"{'='*60}\n")

        start_time = time.time()

        # Create evaluation
        evaluation = TransactionEvaluation(
            transaction=transaction,
            timestamp=datetime.now()
        )
        
        try:
            # T+0s: Front-Office validation
            logger.info("[TIMER]  T+0s: Front-Office analyzing...")
            front_vote = self.front_office.analyze_transaction(transaction, agent_state, context)
            evaluation.division_votes["FRONT_OFFICE"] = front_vote
            
            if front_vote.decision == DECISION_TYPES["REJECT"]:
                evaluation.blockers.append(front_vote)
                evaluation.consensus = "BLOCKED"
                logger.error(f"[ERROR] BLOCKED by Front-Office: {front_vote.reasoning}")
                return evaluation
            
            # T+2s: Risk & Compliance validation
            logger.info("[TIMER]  T+2s: Risk & Compliance analyzing...")
            time.sleep(0.1)  # Simulate latency
            risk_vote = self.risk.analyze_transaction(transaction, agent_state, context)
            evaluation.division_votes["RISK_COMPLIANCE"] = risk_vote
            
            if risk_vote.decision == DECISION_TYPES["REJECT"]:
                evaluation.blockers.append(risk_vote)
                evaluation.consensus = "BLOCKED"
                logger.error(f"[ERROR] BLOCKED by Risk: {risk_vote.reasoning}")
                return evaluation
            
            # T+5s: Treasury liquidity check
            logger.info("[TIMER]  T+5s: Treasury checking liquidity...")
            time.sleep(0.1)
            treasury_vote = self.treasury.analyze_transaction(transaction, agent_state, context)
            evaluation.division_votes["TREASURY"] = treasury_vote
            
            if treasury_vote.decision == DECISION_TYPES["REJECT"]:
                evaluation.blockers.append(treasury_vote)
                evaluation.consensus = "BLOCKED"
                logger.error(f"[ERROR] BLOCKED by Treasury: {treasury_vote.reasoning}")
                return evaluation
            
            # If Treasury needs withdrawal, execute it
            if treasury_vote.metadata.get("withdrawal_needed"):
                withdrawal_amount = treasury_vote.metadata["withdrawal_amount"]
                logger.info(f"[MONEY] Treasury withdrawing ${withdrawal_amount:.2f} from Aave...")

                withdrawal_result = self.treasury.execute_action(
                    transaction,
                    "withdraw",
                    {
                        "agent_id": agent_state.agent_id,
                        "agent_state": agent_state,
                        "amount": withdrawal_amount
                    }
                )

                if withdrawal_result.get("success"):
                    logger.info(f"[SUCCESS] Withdrawal successful. Yield earned: ${withdrawal_result['yield_earned']:.2f}")
                    # Update agent_state with new balance
                    state_dict = withdrawal_result["agent_state"]
                    state_dict.pop("efficiency", None)
                    state_dict.pop("total_balance", None)
                    agent_state = AgentState(**state_dict)
            
            # T+10s: Clearing execution
            logger.info("[TIMER]  T+10s: Clearing executing settlement...")
            time.sleep(0.2)
            clearing_vote = self.clearing.analyze_transaction(transaction, agent_state, context)
            evaluation.division_votes["CLEARING"] = clearing_vote
            
            if clearing_vote.decision == DECISION_TYPES["REJECT"]:
                evaluation.blockers.append(clearing_vote)
                evaluation.consensus = "BLOCKED"
                logger.error(f"[ERROR] BLOCKED by Clearing: {clearing_vote.reasoning}")
                return evaluation
            
            # Execute settlement on-chain
            settlement_result = self.clearing.execute_action(
                transaction,
                "execute",
                {"agent_state": agent_state}
            )

            if not settlement_result.get("success"):
                evaluation.consensus = "FAILED"
                logger.error(f"[ERROR] Settlement execution failed")
                return evaluation

            logger.info(f"[SUCCESS] Settlement executed: {settlement_result['tx_hash']}")
            logger.info(f"[SECURE] ZKP generated: {settlement_result['zkp']['commitment'][:16]}...")

            # Update transaction with on-chain data
            transaction.tx_hash = settlement_result["tx_hash"]
            transaction.block_number = settlement_result["block_number"]
            transaction.gas_used = settlement_result["gas_used"]
            transaction.state = "completed"
            
            # T+15s: Post-trade audit and credit score update
            logger.info("[TIMER]  T+15s: Post-trade audit...")
            time.sleep(0.1)

            # Update agent state
            agent_state.total_transactions += 1
            agent_state.successful_transactions += 1
            agent_state.total_spent += transaction.amount
            agent_state.available_balance -= transaction.amount
            agent_state.last_transaction = datetime.now()

            # Update credit score
            old_limit = agent_state.credit_limit
            new_limit = self.credit_system.update_credit_limit(agent_state, transaction)
            agent_state.credit_limit = new_limit

            credit_change = ((new_limit - old_limit) / old_limit) * 100
            logger.info(f"[ANALYTICS] Credit limit updated: ${old_limit:.2f} → ${new_limit:.2f} ({credit_change:+.1f}%)")

            # Update reputation
            agent_state.reputation_score = self.credit_system.calculate_reputation_score(agent_state)
            logger.info(f"[RATING] Reputation score: {agent_state.reputation_score:.2f}")
            
            # Consensus APPROVED
            evaluation.consensus = "APPROVED"
            evaluation.final_risk_score = sum(
                vote.risk_score for vote in evaluation.division_votes.values()
            ) / len(evaluation.division_votes)
            
            execution_time = time.time() - start_time
            evaluation.execution_time = execution_time
            
            logger.info(f"\n{'='*60}")
            logger.info(f"[SUCCESS] Transaction {transaction.tx_id} COMPLETED")
            logger.info(f"[TIMER]  Total time: {execution_time:.2f}s")
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"[ERROR] Error processing transaction: {e}")
            evaluation.consensus = "FAILED"
            evaluation.blockers.append(
                BankingAnalysis(
                    agent_role="SYSTEM",
                    decision="reject",
                    risk_score=1.0,
                    reasoning=f"System error: {str(e)}"
                )
            )
        
        finally:
            # Record evaluation
            self.evaluations.append(evaluation)
            self.transaction_log.append(transaction)
            self.credit_system.record_transaction(agent_state.agent_id, transaction)

        return evaluation
    
    def onboard_agent(
        self,
        agent_id: str,
        initial_deposit: float = 100.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Onboard new agent into the syndicate

        Args:
            agent_id: Agent ID
            initial_deposit: Initial deposit
            metadata: Additional metadata

        Returns:
            Onboarding result with Agent Card
        """
        logger.info(f"[TICKET] Onboarding agent {agent_id}...")
        
        result = self.front_office.execute_action(
            None,
            "onboard",
            {
                "agent_id": agent_id,
                "initial_deposit": initial_deposit,
                "metadata": metadata or {}
            }
        )
        
        if result.get("success"):
            # Reconstruct AgentState excluding computed properties
            state_dict = result["agent_state"]
            state_dict.pop("efficiency", None)  # Remove computed property
            state_dict.pop("total_balance", None)  # Remove computed property
            agent_state = AgentState(**state_dict)

            # Auto-invest 80% in yield
            if initial_deposit > 0:
                deposit_result = self.treasury.execute_action(
                    None,
                    "deposit",
                    {
                        "agent_id": agent_id,
                        "agent_state": agent_state
                    }
                )
                
                if deposit_result.get("success"):
                    logger.info(f"[TREASURY] Auto-invested ${deposit_result['amount']:.2f} in Aave")
                    result["treasury"] = deposit_result
        
        return result
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Returns current state of an agent"""
        return self.front_office.get_agent_state(agent_id)

    def get_performance_report(self, agent_id: str) -> Dict[str, Any]:
        """Generates performance report for an agent"""
        agent_state = self.get_agent_state(agent_id)
        
        if not agent_state:
            return {"error": "Agent not found"}
        
        return self.credit_system.get_performance_report(agent_state)
    
    def get_syndicate_status(self) -> Dict[str, Any]:
        """Returns general syndicate status"""
        # Aggregate transaction types
        tx_by_type = {}
        for tx in self.transaction_log:
            tx_type = tx.tx_type.value if hasattr(tx.tx_type, 'value') else str(tx.tx_type)
            tx_by_type[tx_type] = tx_by_type.get(tx_type, 0) + 1

        return {
            "total_transactions": len(self.transaction_log),
            "total_evaluations": len(self.evaluations),
            "agents_onboarded": len(self.front_office.onboarded_agents),
            "transactions_by_type": tx_by_type,
            "divisions": {
                "front_office": self.front_office.get_health_status(),
                "risk": self.risk.get_health_status(),
                "treasury": self.treasury.get_health_status(),
                "clearing": self.clearing.get_health_status()
            }
        }

    def process_agentic_commerce_transaction(
        self,
        transaction: Transaction,
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None,
        skip_consensus: bool = False
    ) -> TransactionEvaluation:
        """
        Processes agentic commerce transaction (micropayments, API payments, etc.)
        with specific optimizations for high volume and low value

        Args:
            transaction: Agentic commerce transaction
            agent_state: Agent state
            context: Additional context
            skip_consensus: If True, skips multi-agent consensus for micropayments

        Returns:
            TransactionEvaluation
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[AGENT] Processing Agentic Commerce Transaction")
        logger.info(f"Type: {transaction.tx_type.value}")
        logger.info(f"Agent: {agent_state.agent_id} | Amount: ${transaction.amount:.4f}")
        logger.info(f"{'='*60}\n")

        # For micropayments below threshold, use fast-track
        if (transaction.tx_type == TransactionType.MICROPAYMENT and
            transaction.amount < 1.0 and skip_consensus):
            return self._fast_track_micropayment(transaction, agent_state, context)

        # For API payments and others, use normal flow
        return self.process_transaction(transaction, agent_state, context)

    def _fast_track_micropayment(
        self,
        transaction: Transaction,
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None
    ) -> TransactionEvaluation:
        """
        Fast-track for micropayments (< $1) with simplified validations
        """
        logger.info("[FAST] Fast-track micropayment processing...")

        start_time = time.time()
        evaluation = TransactionEvaluation(
            transaction=transaction,
            timestamp=datetime.now()
        )

        try:
            # Simplified validation
            if agent_state.available_balance < transaction.amount:
                evaluation.consensus = "BLOCKED"
                evaluation.blockers.append(
                    BankingAnalysis(
                        agent_role="SYSTEM",
                        decision="reject",
                        risk_score=1.0,
                        reasoning="Insufficient balance for micropayment"
                    )
                )
                return evaluation

            # Auto-approve micropayments
            evaluation.consensus = "APPROVED"
            evaluation.final_risk_score = 0.1  # Low risk

            # Update agent state
            agent_state.total_transactions += 1
            agent_state.successful_transactions += 1
            agent_state.total_spent += transaction.amount
            agent_state.available_balance -= transaction.amount
            agent_state.last_transaction = datetime.now()

            # Simulate on-chain data (no real execution for micropayments)
            transaction.tx_hash = f"0x{uuid.uuid4().hex}"
            transaction.block_number = 12345678
            transaction.gas_used = 21000
            transaction.state = "completed"

            execution_time = time.time() - start_time
            evaluation.execution_time = execution_time

            logger.info(f"[SUCCESS] Micropayment fast-tracked in {execution_time:.3f}s")

        except Exception as e:
            logger.error(f"[ERROR] Fast-track failed: {e}")
            evaluation.consensus = "FAILED"
            evaluation.blockers.append(
                BankingAnalysis(
                    agent_role="SYSTEM",
                    decision="reject",
                    risk_score=1.0,
                    reasoning=f"Fast-track error: {str(e)}"
                )
            )

        finally:
            self.evaluations.append(evaluation)
            self.transaction_log.append(transaction)

        return evaluation
