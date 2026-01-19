"""
Risk & Compliance Division
Responsible for:
- Budget validation and credit limits
- Scam detection with Gemini AI
- Supplier risk analysis
- Negative scores
- AI-powered fraud detection
"""
from typing import Dict, Any, Optional
import hashlib
import sys, os
import logging

try:
    from ..core.base_banking_agent import BaseBankingAgent, ExceededCreditLimitError
    from ..core.transaction_types import Transaction, AgentState, BankingAnalysis
    from ..core.config import CONFIG, DECISION_TYPES
    from ..intelligence.gemini_agent_advisor import GeminiAgentAdvisor
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.base_banking_agent import BaseBankingAgent, ExceededCreditLimitError
    from core.transaction_types import Transaction, AgentState, BankingAnalysis
    from core.config import CONFIG, DECISION_TYPES
    from intelligence.gemini_agent_advisor import GeminiAgentAdvisor

logger = logging.getLogger(__name__)

class RiskComplianceAgent(BaseBankingAgent):
    """
    Risk & Compliance Agent
    "The Brain" - Ethics/security validator with Gemini AI
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(role="RISK_COMPLIANCE", config=config)
        self.supplier_reputation = {}  # Reputation cache
        self.scam_blacklist = set(CONFIG.SCAM_BLACKLIST)

        # Initialize Gemini AI Advisor
        gemini_api_key = config.get('gemini_api_key') if config else None
        self.ai_advisor = GeminiAgentAdvisor(
            api_key=gemini_api_key,
            enable_thinking=False  # Use fast model for real-time analysis
        )

        if self.ai_advisor.enabled:
            self.logger.info("✨ Gemini AI integration enabled for risk assessment")
        else:
            self.logger.warning("[WARNING] Gemini AI not available, using rule-based analysis")

        # Transaction history for AI context
        self.transaction_history = []
    
    def analyze_transaction(
        self,
        transaction: Transaction,
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None
    ) -> BankingAnalysis:
        """
        Risk valida com AI:
        1. Budget disponível vs valor da transação
        2. Limite de crédito do agente
        3. Reputação do supplier (com Gemini)
        4. Padrões suspeitos (com Gemini fraud detection)
        5. AI-powered recommendations
        """
        self.logger.info(f"[SHIELD] Risk analyzing transaction {transaction.tx_id} for ${transaction.amount}")

        alerts = []
        recommended_actions = []
        risk_score = 0.0
        ai_metadata = {}

        # 1. Verifica budget disponível
        total_available = agent_state.available_balance + agent_state.invested_balance
        if transaction.amount > total_available:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=1.0,
                reasoning=f"Insufficient balance: ${total_available:.2f} < ${transaction.amount:.2f}",
                alerts=["BLOCKED: Insufficient balance"],
                recommended_actions=["Wait for yield or add funds"]
            )

        # 2. Verifica limite de crédito diário
        if transaction.amount > agent_state.credit_limit:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=1.0,
                reasoning=f"Credit limit exceeded: ${transaction.amount:.2f} > ${agent_state.credit_limit:.2f}",
                alerts=["BLOCKED: Credit limit exceeded"],
                recommended_actions=["Increase reputation for higher limit"]
            )

        # 3. Verifica blacklist de scam
        supplier_hash = hashlib.sha256(transaction.supplier.encode()).hexdigest()
        if transaction.supplier in self.scam_blacklist or supplier_hash in self.scam_blacklist:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=1.0,
                reasoning=f"Supplier {transaction.supplier} is blacklisted",
                alerts=["CRITICAL: Supplier in scam blacklist"],
                recommended_actions=["Choose trusted supplier"]
            )

        # 4. AI-POWERED FRAUD DETECTION [AGENT]
        if self.ai_advisor.enabled:
            try:
                fraud_analysis = self.ai_advisor.detect_fraud_patterns(
                    transaction=transaction.to_dict(),
                    agent_history=self.transaction_history[-20:],  # Last 20 transactions
                    global_patterns=None  # Could add known fraud patterns here
                )

                ai_fraud_score = fraud_analysis.get('fraud_score', 0.0)
                risk_score += ai_fraud_score * 0.5  # Weight AI score at 50%

                ai_metadata['fraud_detection'] = fraud_analysis

                # Add AI-detected indicators
                for indicator in fraud_analysis.get('fraud_indicators', []):
                    alerts.append(f"[AGENT] AI detected: {indicator}")

                # Add AI recommendations
                if fraud_analysis.get('recommended_action') == 'block':
                    alerts.append("[ALERT] AI RECOMMENDS BLOCKING this transaction")
                    risk_score += 0.3

                self.logger.info(f"✨ AI fraud score: {ai_fraud_score:.2f}")

            except Exception as e:
                self.logger.error(f"AI fraud detection failed: {e}")

        # 5. AI-POWERED SUPPLIER RISK ASSESSMENT [AGENT]
        if self.ai_advisor.enabled:
            try:
                supplier_analysis = self.ai_advisor.assess_supplier_risk(
                    supplier=transaction.supplier,
                    transaction_history=[
                        tx for tx in self.transaction_history
                        if tx.get('supplier') == transaction.supplier
                    ],
                    market_reputation=None  # Could add oracle data here
                )

                supplier_risk = supplier_analysis.get('risk_score', 0.5)
                risk_score += supplier_risk * 0.3  # Weight supplier risk at 30%

                ai_metadata['supplier_assessment'] = supplier_analysis

                # Add AI-identified risks
                for risk_factor in supplier_analysis.get('risk_factors', []):
                    alerts.append(f"[WARNING] Supplier risk: {risk_factor}")

                if supplier_analysis.get('risk_level') in ['high', 'critical']:
                    recommended_actions.append(
                        f"Consider alternative suppliers: {', '.join(supplier_analysis.get('alternative_suppliers', []))}"
                    )

                self.logger.info(f"✨ AI supplier risk: {supplier_risk:.2f}")

            except Exception as e:
                self.logger.error(f"AI supplier assessment failed: {e}")
        else:
            # Fallback to rule-based analysis
            supplier_risk = self._analyze_supplier_risk(transaction.supplier)
            risk_score += supplier_risk

            if supplier_risk > 0.6:
                alerts.append(f"Supplier {transaction.supplier} has high risk score ({supplier_risk:.2f})")
                recommended_actions.append("Consider alternative supplier")

        # 6. Check suspicious value
        if transaction.amount > CONFIG.SUSPICIOUS_VALUE_THRESHOLD:
            risk_score += 0.2
            alerts.append(f"High value: ${transaction.amount:.2f}")
            recommended_actions.append("Consider splitting into multiple transactions")

        # 7. Analyze agent history
        if agent_state.failed_transactions > agent_state.successful_transactions:
            risk_score += 0.3
            alerts.append("Agent has more failures than successes")

        # Normalize risk score
        risk_score = min(risk_score, 1.0)

        # Final decision
        if risk_score >= 0.7:
            decision = DECISION_TYPES["REJECT"]
            reasoning = f"Risk score too high for approval ({risk_score:.2f})"
        elif risk_score >= 0.4:
            decision = DECISION_TYPES["ADJUST"]
            reasoning = f"Moderate risk ({risk_score:.2f}) - adjustments recommended"
        else:
            decision = DECISION_TYPES["APPROVE"]
            reasoning = f"Acceptable risk score ({risk_score:.2f})"

        # Add AI insights to reasoning if available
        if ai_metadata:
            reasoning += " | AI-enhanced analysis"

        analysis = self._create_analysis(
            decision=decision,
            risk_score=risk_score,
            reasoning=reasoning,
            alerts=alerts,
            recommended_actions=recommended_actions,
            metadata={
                "supplier_risk": supplier_risk if not self.ai_advisor.enabled else ai_metadata.get('supplier_assessment', {}).get('risk_score'),
                "balance_check": "passed",
                "credit_check": "passed",
                "ai_enabled": self.ai_advisor.enabled,
                **ai_metadata
            }
        )

        # Store transaction for future AI context
        self.transaction_history.append({
            **transaction.to_dict(),
            'risk_score': risk_score,
            'decision': decision
        })

        # Keep history manageable (last 100 transactions)
        if len(self.transaction_history) > 100:
            self.transaction_history = self.transaction_history[-100:]

        self._record_call("analyze_transaction", analysis)
        return analysis
    
    def execute_action(
        self, 
        transaction: Transaction, 
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa ações de risk management
        
        Actions:
        - "blacklist": Adiciona supplier à blacklist
        - "whitelist": Remove supplier da blacklist
        - "analyze_supplier": Analisa reputação de supplier
        """
        if action == "blacklist":
            return self._blacklist_supplier(transaction.supplier)
        elif action == "whitelist":
            return self._whitelist_supplier(transaction.supplier)
        elif action == "analyze_supplier":
            risk = self._analyze_supplier_risk(transaction.supplier)
            return {"supplier": transaction.supplier, "risk_score": risk}
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _analyze_supplier_risk(self, supplier: str) -> float:
        """
        Analisa risco de um supplier
        
        Em produção, isso consultaria:
        - Oráculos de reputação on-chain
        - APIs de KYC/AML
        - Histórico de transações
        """
        # Cache hit
        if supplier in self.supplier_reputation:
            return self.supplier_reputation[supplier]
        
        # Heurística simples (substituir por ML em produção)
        risk_score = 0.0
        
        # Suppliers conhecidos (whitelist manual)
        trusted_suppliers = ["AWS", "Google Cloud", "Microsoft Azure", "OpenAI"]
        if any(trusted in supplier for trusted in trusted_suppliers):
            risk_score = 0.1
        elif supplier.startswith("0x"):  # Endereço Ethereum
            # Analisa padrões suspeitos
            if supplier.endswith("0000"):
                risk_score = 0.8  # Padrão comum de scam
            else:
                risk_score = 0.3  # Risco moderado para endereços desconhecidos
        else:
            risk_score = 0.5  # Risco médio para suppliers não verificados
        
        # Cacheia resultado
        self.supplier_reputation[supplier] = risk_score
        
        return risk_score
    
    def _blacklist_supplier(self, supplier: str) -> Dict[str, Any]:
        """Adiciona supplier à blacklist"""
        self.scam_blacklist.add(supplier)
        self.logger.warning(f"[EMOJI] Supplier {supplier} added to blacklist")
        return {"success": True, "supplier": supplier, "action": "blacklisted"}
    
    def _whitelist_supplier(self, supplier: str) -> Dict[str, Any]:
        """Remove supplier da blacklist"""
        if supplier in self.scam_blacklist:
            self.scam_blacklist.remove(supplier)
            self.logger.info(f"[SUCCESS] Supplier {supplier} removed from blacklist")
            return {"success": True, "supplier": supplier, "action": "whitelisted"}
        return {"success": False, "message": "Supplier not in blacklist"}
