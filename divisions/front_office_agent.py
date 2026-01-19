"""
Front-Office & Onboarding Agent
Responsible for:
- Creating Agent Cards (Circle Wallets)
- Onboarding new agents
- Initial identity validation
- Integration with Circle's Programmable Wallets
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import sys, os

try:
    from ..core.base_banking_agent import BaseBankingAgent, BankingAgentError
    from ..core.transaction_types import Transaction, AgentState, BankingAnalysis
    from ..core.config import CONFIG, DECISION_TYPES
    from ..blockchain.circle_wallets import CircleWalletsAPI, CircleWallet
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.base_banking_agent import BaseBankingAgent, BankingAgentError
    from core.transaction_types import Transaction, AgentState, BankingAnalysis
    from core.config import CONFIG, DECISION_TYPES
    from blockchain.circle_wallets import CircleWalletsAPI, CircleWallet

class FrontOfficeAgent(BaseBankingAgent):
    """
    Front-Office Agent
    Entry point for new agents in the banking syndicate
    Integrated with Circle Programmable Wallets for USDC
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(role="FRONT_OFFICE", config=config)
        self.onboarded_agents = {}

        # Initialize Circle Wallets API
        self.circle_api = None
        self.use_circle = config.get("use_circle_wallets", False) if config else False

        if self.use_circle:
            try:
                environment = config.get("circle_environment", "sandbox") if config else "sandbox"
                self.circle_api = CircleWalletsAPI(environment=environment)
                self.logger.info("[SUCCESS] Circle Wallets API initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Circle API: {e}")
                self.use_circle = False
    
    def analyze_transaction(
        self,
        transaction: Transaction,
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None
    ) -> BankingAnalysis:
        """
        Front-Office validates if the agent is properly onboarded
        and if the transaction has valid metadata.
        """
        self.logger.info(f"[TICKET] Front-Office analyzing transaction {transaction.tx_id}")
        
        alerts = []
        recommended_actions = []
        risk_score = 0.0

        # Check if agent is onboarded
        if agent_state.agent_id not in self.onboarded_agents:
            alerts.append(f"Agent {agent_state.agent_id} was not formally onboarded")
            risk_score += 0.3

        # Validate transaction metadata
        if not transaction.description:
            alerts.append("Transaction without description")
            risk_score += 0.1

        if not transaction.supplier:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=1.0,
                reasoning="Supplier not specified",
                alerts=["Invalid transaction: supplier missing"]
            )

        # Validate wallet address
        if not agent_state.wallet_address:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=1.0,
                reasoning="Agent does not have wallet configured",
                alerts=["Agent needs Agent Card (ERC-4337 wallet)"],
                recommended_actions=["Execute complete onboarding"]
            )

        # All OK
        decision = DECISION_TYPES["APPROVE"] if risk_score < 0.3 else DECISION_TYPES["ADJUST"]
        
        analysis = self._create_analysis(
            decision=decision,
            risk_score=risk_score,
            reasoning="Front-Office validation passed" if decision == "approve" else "Minor adjustments needed",
            alerts=alerts,
            recommended_actions=recommended_actions
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
        Executes Front-Office actions

        Actions:
        - "onboard": Creates Agent Card for new agent
        - "validate": Validates agent credentials
        """
        if action == "onboard":
            return self._onboard_agent(context or {})
        elif action == "validate":
            return self._validate_agent(transaction.agent_id)
        else:
            raise BankingAgentError(f"Unknown action: {action}")
    
    def _onboard_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates Agent Card (Circle Wallet) for new agent

        Args:
            agent_data: {
                "agent_id": str,
                "initial_deposit": float,
                "metadata": dict,
                "blockchain": str (optional, default: "MATIC")
            }
        """
        agent_id = agent_data.get("agent_id") or str(uuid.uuid4())
        initial_deposit = agent_data.get("initial_deposit", 0.0)
        blockchain = agent_data.get("blockchain", "MATIC")

        self.logger.info(f"[TICKET] Onboarding agent {agent_id}")

        wallet_address = None
        circle_wallet_id = None
        circle_wallet = None

        # Try to create Circle Wallet if API is available
        if self.use_circle and self.circle_api:
            try:
                self.logger.info(f"Creating Circle wallet for {agent_id} on {blockchain}")

                circle_wallet = self.circle_api.create_wallet(
                    agent_id=agent_id,
                    blockchain=blockchain,
                    metadata={
                        "agent_type": "banking_agent",
                        "initial_deposit": str(initial_deposit),
                        **(agent_data.get("metadata", {}))
                    }
                )

                wallet_address = circle_wallet.address
                circle_wallet_id = circle_wallet.wallet_id

                self.logger.info(f"[SUCCESS] Circle wallet created: {wallet_address}")

            except Exception as e:
                self.logger.error(f"Failed to create Circle wallet: {e}")
                self.logger.info("Falling back to simulated wallet")
                wallet_address = None

        # Fallback: Generate simulated wallet if Circle API not available
        if not wallet_address:
            wallet_address = f"0x{uuid.uuid4().hex[:40]}"
            self.logger.info(f"Using simulated wallet: {wallet_address}")

        # Create AgentState
        agent_state = AgentState(
            agent_id=agent_id,
            wallet_address=wallet_address,
            credit_limit=CONFIG.DEFAULT_CREDIT_LIMIT,
            available_balance=initial_deposit,
            invested_balance=0.0
        )

        # Register onboarding
        self.onboarded_agents[agent_id] = {
            "agent_state": agent_state,
            "onboarded_at": datetime.now(),
            "metadata": agent_data.get("metadata", {}),
            "circle_wallet_id": circle_wallet_id,
            "circle_wallet": circle_wallet.to_dict() if circle_wallet else None,
            "blockchain": blockchain
        }

        self.logger.info(f"[SUCCESS] Agent {agent_id} onboarded with wallet {wallet_address}")

        result = {
            "success": True,
            "agent_id": agent_id,
            "wallet_address": wallet_address,
            "credit_limit": agent_state.credit_limit,
            "agent_state": agent_state.to_dict(),
            "blockchain": blockchain
        }

        # Add Circle-specific details if available
        if circle_wallet_id:
            result["circle_wallet_id"] = circle_wallet_id
            result["wallet_type"] = "circle_programmable"
        else:
            result["wallet_type"] = "simulated"

        return result
    
    def _validate_agent(self, agent_id: str) -> Dict[str, Any]:
        """Validates if agent is onboarded"""
        is_valid = agent_id in self.onboarded_agents
        
        return {
            "valid": is_valid,
            "agent_id": agent_id,
            "message": "Agent is onboarded" if is_valid else "Agent not found"
        }
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Returns state of an onboarded agent"""
        agent_data = self.onboarded_agents.get(agent_id)
        return agent_data["agent_state"] if agent_data else None

    def get_circle_wallet_id(self, agent_id: str) -> Optional[str]:
        """
        Returns Circle Wallet ID associated with the agent

        Args:
            agent_id: Agent identifier

        Returns:
            Circle wallet ID or None
        """
        agent_data = self.onboarded_agents.get(agent_id)
        return agent_data.get("circle_wallet_id") if agent_data else None

    def get_wallet_balance(self, agent_id: str) -> Dict[str, Any]:
        """
        Get wallet balance from Circle API

        Args:
            agent_id: Agent identifier

        Returns:
            Balance information
        """
        if not self.use_circle or not self.circle_api:
            return {
                "success": False,
                "error": "Circle API not available"
            }

        circle_wallet_id = self.get_circle_wallet_id(agent_id)
        if not circle_wallet_id:
            return {
                "success": False,
                "error": "No Circle wallet found for agent"
            }

        try:
            balance = self.circle_api.get_wallet_balance(circle_wallet_id)
            return {
                "success": True,
                "agent_id": agent_id,
                **balance
            }
        except Exception as e:
            self.logger.error(f"Failed to get wallet balance: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def transfer_usdc(
        self,
        from_agent_id: str,
        to_address: str,
        amount: str,
        blockchain: str = "MATIC"
    ) -> Dict[str, Any]:
        """
        Transfer USDC from agent wallet to another address

        Args:
            from_agent_id: Source agent ID
            to_address: Destination address
            amount: Amount in USDC
            blockchain: Target blockchain

        Returns:
            Transaction details
        """
        if not self.use_circle or not self.circle_api:
            return {
                "success": False,
                "error": "Circle API not available"
            }

        circle_wallet_id = self.get_circle_wallet_id(from_agent_id)
        if not circle_wallet_id:
            return {
                "success": False,
                "error": "No Circle wallet found for agent"
            }

        try:
            transaction = self.circle_api.transfer_usdc(
                from_wallet_id=circle_wallet_id,
                to_address=to_address,
                amount=amount,
                blockchain=blockchain
            )

            return {
                "success": True,
                "agent_id": from_agent_id,
                "tx_id": transaction.tx_id,
                "tx_hash": transaction.tx_hash,
                "amount": transaction.amount,
                "destination": transaction.destination,
                "state": transaction.state,
                "blockchain": transaction.blockchain
            }
        except Exception as e:
            self.logger.error(f"Transfer failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_transaction_history(self, agent_id: str) -> Dict[str, Any]:
        """
        Get transaction history for agent's wallet

        Args:
            agent_id: Agent identifier

        Returns:
            List of transactions
        """
        if not self.use_circle or not self.circle_api:
            return {
                "success": False,
                "error": "Circle API not available"
            }

        circle_wallet_id = self.get_circle_wallet_id(agent_id)
        if not circle_wallet_id:
            return {
                "success": False,
                "error": "No Circle wallet found for agent"
            }

        try:
            transactions = self.circle_api.get_transaction_history(circle_wallet_id)

            return {
                "success": True,
                "agent_id": agent_id,
                "transactions": [tx.to_dict() for tx in transactions],
                "count": len(transactions)
            }
        except Exception as e:
            self.logger.error(f"Failed to get transaction history: {e}")
            return {
                "success": False,
                "error": str(e)
            }
