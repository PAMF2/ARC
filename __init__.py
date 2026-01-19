"""
Package initialization for Banking Syndicate
"""
from .banking_syndicate import BankingSyndicate
from .core.transaction_types import Transaction, TransactionType, AgentState
from .core.config import CONFIG

__version__ = "0.1.0"
__all__ = ["BankingSyndicate", "Transaction", "TransactionType", "AgentState", "CONFIG"]
