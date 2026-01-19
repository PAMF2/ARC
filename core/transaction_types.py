"""
Transaction Types and Schemas
Type definitions for banking transactions
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    """Supported transaction types"""
    PURCHASE = "purchase"  # Service/product purchase
    TRANSFER = "transfer"  # Transfer between agents
    INVESTMENT = "investment"  # Investment in DeFi protocol
    WITHDRAWAL = "withdrawal"  # Yield withdrawal
    DEPOSIT = "deposit"  # Initial deposit

    # Agentic Commerce Transaction Types
    API_PAYMENT = "api_payment"  # Payment for API usage
    MICROPAYMENT = "micropayment"  # Automated micropayment (< $1)
    AGENT_TO_AGENT = "agent_to_agent"  # Transaction between agents
    USAGE_BILLING = "usage_billing"  # Usage-based billing

@dataclass
class Transaction:
    """Transaction schema"""
    tx_id: str
    agent_id: str
    tx_type: TransactionType
    amount: float  # USD
    supplier: str  # Supplier address or name
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Transaction state
    state: str = "pending"
    risk_score: float = 0.0
    gas_estimate: int = 0
    
    # Blockchain data
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes to dict"""
        return {
            "tx_id": self.tx_id,
            "agent_id": self.agent_id,
            "tx_type": self.tx_type.value,
            "amount": self.amount,
            "supplier": self.supplier,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "state": self.state,
            "risk_score": self.risk_score,
            "gas_estimate": self.gas_estimate,
            "tx_hash": self.tx_hash,
            "block_number": self.block_number,
            "gas_used": self.gas_used
        }

@dataclass
class AgentState:
    """Agent financial state"""
    agent_id: str
    wallet_address: str
    credit_limit: float
    available_balance: float
    invested_balance: float  # Capital in yield
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    total_spent: float = 0.0
    total_earned: float = 0.0
    reputation_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_transaction: Optional[datetime] = None
    
    @property
    def efficiency(self) -> float:
        """Calculates agent efficiency for credit scoring"""
        if self.total_transactions == 0:
            return 0.0

        success_rate = self.successful_transactions / self.total_transactions
        roi = (self.total_earned - self.total_spent) / max(self.total_spent, 1.0)

        # Efficiency = 70% success rate + 30% ROI
        return (0.7 * success_rate) + (0.3 * max(min(roi, 1.0), -1.0))

    @property
    def total_balance(self) -> float:
        """Total balance (available + invested)"""
        return self.available_balance + self.invested_balance

    def to_dict(self) -> Dict[str, Any]:
        """Serializes to dict"""
        created_at = self.created_at
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        last_tx = self.last_transaction
        if isinstance(last_tx, str):
            last_tx = datetime.fromisoformat(last_tx) if last_tx else None
        
        return {
            "agent_id": self.agent_id,
            "wallet_address": self.wallet_address,
            "credit_limit": self.credit_limit,
            "available_balance": self.available_balance,
            "invested_balance": self.invested_balance,
            "total_transactions": self.total_transactions,
            "successful_transactions": self.successful_transactions,
            "failed_transactions": self.failed_transactions,
            "total_spent": self.total_spent,
            "total_earned": self.total_earned,
            "reputation_score": self.reputation_score,
            "efficiency": self.efficiency,
            "total_balance": self.total_balance,
            "created_at": created_at.isoformat() if isinstance(created_at, datetime) else created_at,
            "last_transaction": last_tx.isoformat() if last_tx and isinstance(last_tx, datetime) else last_tx
        }

@dataclass
class BankingAnalysis:
    """Banking agent analysis"""
    agent_role: str
    decision: str  # "approve", "reject", "adjust"
    risk_score: float
    reasoning: str
    recommended_actions: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes to dict"""
        return {
            "agent_role": self.agent_role,
            "decision": self.decision,
            "risk_score": self.risk_score,
            "reasoning": self.reasoning,
            "recommended_actions": self.recommended_actions,
            "alerts": self.alerts,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class TransactionEvaluation:
    """Complete transaction evaluation by all divisions"""
    transaction: Transaction
    timestamp: datetime = field(default_factory=datetime.now)
    division_votes: Dict[str, BankingAnalysis] = field(default_factory=dict)
    consensus: str = ""  # "APPROVED", "BLOCKED", "ADJUSTED"
    blockers: List[BankingAnalysis] = field(default_factory=list)
    final_risk_score: float = 0.0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes to dict"""
        return {
            "transaction": self.transaction.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "division_votes": {role: vote.to_dict() for role, vote in self.division_votes.items()},
            "consensus": self.consensus,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
            "final_risk_score": self.final_risk_score,
            "execution_time": self.execution_time
        }
