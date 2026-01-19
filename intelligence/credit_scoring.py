"""
Credit Scoring System
Implementa Dynamic Credit Limit (DCL)

Fórmula: L_{t+1} = L_t × (1 + α × efficiency_t)

Onde:
- L_t = Credit limit atual
- α = Multiplicador (default 0.05)
- efficiency_t = Performance do agente na tarefa anterior
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys, os

try:
    from ..core.transaction_types import Transaction, AgentState
    from ..core.config import CONFIG
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.transaction_types import Transaction, AgentState
    from core.config import CONFIG

class CreditScoringSystem:
    """
    Sistema de Dynamic Credit Limit
    
    O limite de crédito do agente evolui baseado em:
    - Taxa de sucesso de transações
    - Economia de gas
    - ROI (Return on Investment)
    - Pontualidade de pagamentos
    """
    
    def __init__(self, alpha: float = CONFIG.ALPHA):
        """
        Args:
            alpha: Multiplicador para ajuste de crédito (default 0.05 = 5%)
        """
        self.alpha = alpha
        self.transaction_history: Dict[str, List[Transaction]] = {}
    
    def calculate_efficiency(
        self, 
        agent_state: AgentState,
        recent_transaction: Optional[Transaction] = None
    ) -> float:
        """
        Calcula eficiência do agente
        
        Componentes:
        1. Success Rate (40%)
        2. Gas Efficiency (30%)
        3. ROI (30%)
        
        Returns:
            float: -1.0 a 1.0 (negativo = penalidade, positivo = bonus)
        """
        if agent_state.total_transactions == 0:
            return 0.0
        
        # 1. Success Rate
        success_rate = agent_state.successful_transactions / agent_state.total_transactions
        success_score = (success_rate - 0.5) * 2  # Normaliza para -1 a 1
        
        # 2. Gas Efficiency (compara gas_used vs gas_estimate)
        gas_efficiency = 0.0
        if recent_transaction and recent_transaction.gas_used and recent_transaction.gas_estimate:
            gas_ratio = recent_transaction.gas_used / recent_transaction.gas_estimate
            # Bonus se usou menos gas que estimado
            gas_efficiency = (1.0 - gas_ratio) * 2  # -1 a 1
        
        # 3. ROI
        roi = 0.0
        if agent_state.total_spent > 0:
            roi_ratio = (agent_state.total_earned - agent_state.total_spent) / agent_state.total_spent
            roi = max(min(roi_ratio, 1.0), -1.0)  # Clamp entre -1 e 1
        
        # Weighted average
        efficiency = (
            0.4 * success_score +
            0.3 * gas_efficiency +
            0.3 * roi
        )
        
        return efficiency
    
    def update_credit_limit(
        self,
        agent_state: AgentState,
        recent_transaction: Optional[Transaction] = None
    ) -> float:
        """
        Atualiza credit limit baseado em performance
        
        Fórmula: L_{t+1} = L_t × (1 + α × efficiency_t)
        
        Args:
            agent_state: Estado atual do agente
            recent_transaction: Última transação (opcional)
        
        Returns:
            novo_credit_limit: Limite atualizado
        """
        current_limit = agent_state.credit_limit
        efficiency = self.calculate_efficiency(agent_state, recent_transaction)
        
        # Aplica fórmula DCL
        new_limit = current_limit * (1 + self.alpha * efficiency)
        
        # Clamp entre min e max
        new_limit = max(
            CONFIG.MIN_CREDIT_LIMIT,
            min(new_limit, CONFIG.MAX_CREDIT_LIMIT)
        )
        
        return new_limit
    
    def calculate_reputation_score(self, agent_state: AgentState) -> float:
        """
        Calcula reputation score (0.0 a 1.0)
        
        Fatores:
        - Número de transações (volume)
        - Taxa de sucesso
        - Longevidade (tempo desde criação)
        - Consistência (desvio padrão de performance)
        """
        if agent_state.total_transactions == 0:
            return 0.5  # Neutro para novos agentes
        
        # 1. Volume score (logarítmico)
        volume_score = min(1.0, agent_state.total_transactions / 100)
        
        # 2. Success rate
        success_rate = agent_state.successful_transactions / agent_state.total_transactions
        
        # 3. Longevity score
        days_active = (datetime.now() - agent_state.created_at).days
        longevity_score = min(1.0, days_active / 365)  # Max score após 1 ano
        
        # 4. Efficiency
        efficiency = self.calculate_efficiency(agent_state)
        efficiency_normalized = (efficiency + 1) / 2  # 0 a 1
        
        # Weighted average
        reputation = (
            0.25 * volume_score +
            0.35 * success_rate +
            0.15 * longevity_score +
            0.25 * efficiency_normalized
        )
        
        return reputation
    
    def record_transaction(self, agent_id: str, transaction: Transaction):
        """Registra transação para histórico"""
        if agent_id not in self.transaction_history:
            self.transaction_history[agent_id] = []
        
        self.transaction_history[agent_id].append(transaction)
    
    def get_performance_report(self, agent_state: AgentState) -> Dict[str, Any]:
        """
        Gera relatório de performance do agente
        """
        efficiency = self.calculate_efficiency(agent_state)
        reputation = self.calculate_reputation_score(agent_state)
        
        return {
            "agent_id": agent_state.agent_id,
            "current_credit_limit": agent_state.credit_limit,
            "efficiency": efficiency,
            "reputation_score": reputation,
            "success_rate": (
                agent_state.successful_transactions / agent_state.total_transactions
                if agent_state.total_transactions > 0 else 0.0
            ),
            "total_transactions": agent_state.total_transactions,
            "total_spent": agent_state.total_spent,
            "total_earned": agent_state.total_earned,
            "roi": (
                (agent_state.total_earned - agent_state.total_spent) / agent_state.total_spent
                if agent_state.total_spent > 0 else 0.0
            ),
            "projected_next_limit": self.update_credit_limit(agent_state)
        }
