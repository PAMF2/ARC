"""
Treasury & Wealth Management Division
Responsible for:
- Auto-investment of idle capital in Aave/Morpho (80% allocation)
- Automatic liquidity withdrawal on-demand
- Yield maximization
- Portfolio management
"""
from typing import Dict, Any, Optional
from datetime import datetime
import sys, os

try:
    from ..core.base_banking_agent import BaseBankingAgent, InsufficientBalanceError
    from ..core.transaction_types import Transaction, AgentState, BankingAnalysis
    from ..core.config import CONFIG, DECISION_TYPES
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.base_banking_agent import BaseBankingAgent, InsufficientBalanceError
    from core.transaction_types import Transaction, AgentState, BankingAnalysis
    from core.config import CONFIG, DECISION_TYPES

class TreasuryAgent(BaseBankingAgent):
    """
    Treasury & Wealth Management Agent
    Maximizes idle capital by generating yield
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(role="TREASURY", config=config)
        self.aave_positions = {}  # {agent_id: {deposited, yield_earned}}
        self.allocation_percent = CONFIG.TREASURY_ALLOCATION_PERCENT
    
    def analyze_transaction(
        self, 
        transaction: Transaction, 
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None
    ) -> BankingAnalysis:
        """
        Treasury verifica:
        1. Se há liquidez suficiente disponível
        2. Se precisa retirar de yield
        3. Qual a melhor estratégia de liquidação
        """
        self.logger.info(f"[TREASURY] Treasury analyzing liquidity for transaction {transaction.tx_id}")
        
        alerts = []
        recommended_actions = []
        risk_score = 0.0

        # Check available liquidity
        available = agent_state.available_balance
        needed = transaction.amount
        
        if available >= needed:
            # Sufficient liquidity available
            return self._create_analysis(
                decision=DECISION_TYPES["APPROVE"],
                risk_score=0.0,
                reasoning=f"Sufficient liquidity: ${available:.2f} >= ${needed:.2f}",
                metadata={
                    "liquidity_status": "sufficient",
                    "withdrawal_needed": False,
                    "available": available
                }
            )

        # Need to withdraw from yield
        invested = agent_state.invested_balance
        total_available = available + invested
        
        if total_available < needed:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=1.0,
                reasoning=f"Insufficient total balance: ${total_available:.2f} < ${needed:.2f}",
                alerts=["BLOCKED: Total balance insufficient even with yield"],
                recommended_actions=["Wait for more yield or add funds"]
            )
        
        # Can withdraw from yield
        withdrawal_amount = needed - available

        alerts.append(f"Need to withdraw ${withdrawal_amount:.2f} from yield")
        recommended_actions.append("Execute Aave withdrawal before transaction")

        # Check if sufficient capital will remain invested
        remaining_invested = invested - withdrawal_amount
        if remaining_invested < (agent_state.available_balance * 0.5):
            risk_score += 0.2
            alerts.append("Withdrawal will significantly reduce future yield")
        
        analysis = self._create_analysis(
            decision=DECISION_TYPES["APPROVE"],
            risk_score=risk_score,
            reasoning=f"Withdrawal needed: ${withdrawal_amount:.2f} from Aave",
            alerts=alerts,
            recommended_actions=recommended_actions,
            metadata={
                "liquidity_status": "withdrawal_needed",
                "withdrawal_needed": True,
                "withdrawal_amount": withdrawal_amount,
                "remaining_invested": remaining_invested
            }
        )
        
        self._record_call("analyze_transaction", analysis)
        return analysis
    
    def execute_action(
        self, 
        transaction: Transaction, 
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa ações de treasury management
        
        Actions:
        - "deposit": Deposita capital em Aave
        - "withdraw": Retira capital de Aave
        - "rebalance": Rebalanceia portfolio (80% yield, 20% liquid)
        - "calculate_yield": Calcula yield acumulado
        """
        if action == "deposit":
            return self._deposit_to_yield(context or {})
        elif action == "withdraw":
            return self._withdraw_from_yield(context or {})
        elif action == "rebalance":
            return self._rebalance_portfolio(context or {})
        elif action == "calculate_yield":
            return self._calculate_yield(context.get("agent_id"))
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _deposit_to_yield(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deposits capital in Aave to generate yield

        Strategy: 80% of available balance goes to yield
        """
        agent_id = data.get("agent_id")
        agent_state: AgentState = data.get("agent_state")
        
        if not agent_id or not agent_state:
            return {"error": "Missing agent_id or agent_state"}
        
        # Calculate deposit amount
        available = agent_state.available_balance
        deposit_amount = available * self.allocation_percent

        if deposit_amount < 1.0:  # Minimum deposit
            return {
                "success": False,
                "message": "Deposit amount too small",
                "deposit_amount": deposit_amount
            }

        self.logger.info(f"[TREASURY] Depositing ${deposit_amount:.2f} to Aave for agent {agent_id}")

        # Simulate Aave deposit (will be replaced by real integration)
        if agent_id not in self.aave_positions:
            self.aave_positions[agent_id] = {
                "deposited": 0.0,
                "yield_earned": 0.0,
                "deposit_timestamp": datetime.now(),
                "apy": 0.05  # 5% APY (simulated)
            }

        position = self.aave_positions[agent_id]
        position["deposited"] += deposit_amount
        position["deposit_timestamp"] = datetime.now()

        # Update agent state
        agent_state.available_balance -= deposit_amount
        agent_state.invested_balance += deposit_amount
        
        return {
            "success": True,
            "action": "deposit",
            "amount": deposit_amount,
            "total_invested": position["deposited"],
            "apy": position["apy"],
            "agent_state": agent_state.to_dict()
        }
    
    def _withdraw_from_yield(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Withdraws capital from Aave
        """
        agent_id = data.get("agent_id")
        agent_state: AgentState = data.get("agent_state")
        amount = data.get("amount")
        
        if not agent_id or not agent_state or not amount:
            return {"error": "Missing required parameters"}
        
        if agent_id not in self.aave_positions:
            return {"error": "No Aave position found for agent"}
        
        position = self.aave_positions[agent_id]
        
        if amount > position["deposited"]:
            return {
                "error": "Insufficient Aave balance",
                "requested": amount,
                "available": position["deposited"]
            }
        
        self.logger.info(f"[MONEY] Withdrawing ${amount:.2f} from Aave for agent {agent_id}")

        # Calculate yield before withdrawal
        yield_earned = self._calculate_yield(agent_id)["yield_earned"]

        # Withdraw capital + yield
        total_withdrawal = amount + yield_earned
        position["deposited"] -= amount
        position["yield_earned"] = 0.0  # Reset yield

        # Update agent state
        agent_state.invested_balance -= amount
        agent_state.available_balance += total_withdrawal
        agent_state.total_earned += yield_earned
        
        return {
            "success": True,
            "action": "withdraw",
            "principal": amount,
            "yield_earned": yield_earned,
            "total_withdrawn": total_withdrawal,
            "remaining_invested": position["deposited"],
            "agent_state": agent_state.to_dict()
        }
    
    def _rebalance_portfolio(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rebalances portfolio to 80% yield, 20% liquid
        """
        agent_id = data.get("agent_id")
        agent_state: AgentState = data.get("agent_state")
        
        if not agent_id or not agent_state:
            return {"error": "Missing agent_id or agent_state"}
        
        total_balance = agent_state.total_balance
        target_invested = total_balance * self.allocation_percent
        current_invested = agent_state.invested_balance
        
        difference = target_invested - current_invested

        if abs(difference) < 1.0:  # Already balanced
            return {
                "success": True,
                "action": "rebalance",
                "message": "Portfolio already balanced",
                "difference": difference
            }

        # Deposit or withdraw to rebalance
        if difference > 0:
            result = self._deposit_to_yield({
                "agent_id": agent_id,
                "agent_state": agent_state
            })
        else:
            result = self._withdraw_from_yield({
                "agent_id": agent_id,
                "agent_state": agent_state,
                "amount": abs(difference)
            })
        
        return result
    
    def _calculate_yield(self, agent_id: str) -> Dict[str, Any]:
        """
        Calculates accumulated yield

        Simplified formula: yield = principal × APY × (days / 365)
        """
        if agent_id not in self.aave_positions:
            return {"yield_earned": 0.0}
        
        position = self.aave_positions[agent_id]

        # Calculate days since deposit
        days_invested = (datetime.now() - position["deposit_timestamp"]).days

        # Yield = principal × APY × (days / 365)
        yield_earned = position["deposited"] * position["apy"] * (days_invested / 365)
        
        return {
            "yield_earned": yield_earned,
            "days_invested": days_invested,
            "apy": position["apy"],
            "principal": position["deposited"]
        }
