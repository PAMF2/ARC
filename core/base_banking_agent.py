"""
Base Banking Agent
Classe base para todos os agentes do sindicato bancário
Adaptado de taver/business/base_agent.py
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import sys, os

try:
    from .transaction_types import Transaction, AgentState, BankingAnalysis
    from .config import CONFIG, DECISION_TYPES
except ImportError:
    # Support for direct imports
    from transaction_types import Transaction, AgentState, BankingAnalysis
    from config import CONFIG, DECISION_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseBankingAgent(ABC):
    """
    Classe base abstrata para agentes do sindicato bancário.
    Cada divisão (Front-Office, Risk, Treasury, Clearing) herda desta classe.
    """
    
    def __init__(self, role: str, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o agente bancário
        
        Args:
            role: Papel do agente (ex: "RISK_COMPLIANCE")
            config: Configurações específicas do agente
        """
        self.role = role
        self.config = config or {}
        self.call_history = []
        self.logger = logging.getLogger(f"BankingAgent.{role}")
        
        self.logger.info(f"[BANK] {role} Agent initialized")
    
    @abstractmethod
    def analyze_transaction(
        self, 
        transaction: Transaction, 
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None
    ) -> BankingAnalysis:
        """
        Analisa uma transação do ponto de vista desta divisão.
        
        Args:
            transaction: Transação a ser analisada
            agent_state: Estado atual do agente solicitante
            context: Contexto adicional (histórico, mercado, etc)
        
        Returns:
            BankingAnalysis com decisão e raciocínio
        """
        pass
    
    @abstractmethod
    def execute_action(
        self, 
        transaction: Transaction, 
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa uma ação específica desta divisão.
        
        Args:
            transaction: Transação sendo processada
            action: Ação a executar (ex: "deposit", "withdraw", "validate")
            context: Contexto adicional
        
        Returns:
            Resultado da execução
        """
        pass
    
    def _record_call(self, method: str, result: Any):
        """Registra chamada para auditoria"""
        self.call_history.append({
            "method": method,
            "timestamp": datetime.now(),
            "result": str(result)[:200]  # Limita tamanho
        })
    
    def _create_analysis(
        self,
        decision: str,
        risk_score: float,
        reasoning: str,
        **kwargs
    ) -> BankingAnalysis:
        """
        Helper para criar BankingAnalysis padronizado
        
        Args:
            decision: "approve", "reject", ou "adjust"
            risk_score: Score de risco (0.0 a 1.0)
            reasoning: Explicação da decisão
            **kwargs: Campos adicionais (alerts, actions, metadata)
        """
        return BankingAnalysis(
            agent_role=self.role,
            decision=decision,
            risk_score=risk_score,
            reasoning=reasoning,
            recommended_actions=kwargs.get("recommended_actions", []),
            alerts=kwargs.get("alerts", []),
            metadata=kwargs.get("metadata", {})
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do agente"""
        return {
            "role": self.role,
            "status": "healthy",
            "total_calls": len(self.call_history),
            "last_call": self.call_history[-1] if self.call_history else None
        }
    
    def __repr__(self) -> str:
        return f"<BaseBankingAgent role={self.role}>"


class BankingAgentError(Exception):
    """Exceção base para erros de agentes bancários"""
    pass

class TransactionRejectedError(BankingAgentError):
    """Transação rejeitada por um agente"""
    def __init__(self, agent_role: str, reason: str):
        self.agent_role = agent_role
        self.reason = reason
        super().__init__(f"{agent_role} rejected transaction: {reason}")

class InsufficientBalanceError(BankingAgentError):
    """Saldo insuficiente"""
    pass

class ExceededCreditLimitError(BankingAgentError):
    """Limite de crédito excedido"""
    pass
