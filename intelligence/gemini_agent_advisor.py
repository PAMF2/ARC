"""
Gemini AI Agent Advisor
Advanced AI-powered financial intelligence for autonomous banking agents

Uses Google Gemini to provide:
- Smart payment decisions
- Fraud detection with deep pattern analysis
- Financial advice for optimal resource usage
- Transaction optimization recommendations
- Market intelligence and trend analysis
"""
from typing import Dict, Any, Optional, List, Tuple
import logging
import json
from datetime import datetime
import hashlib

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Using fallback mode.")

logger = logging.getLogger(__name__)


class GeminiAgentAdvisor:
    """
    AI-Powered Financial Advisor for Banking Agents

    Leverages Gemini 2.0 Flash for real-time financial intelligence
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp",
        enable_thinking: bool = False
    ):
        """
        Initialize Gemini Agent Advisor

        Args:
            api_key: Google AI API key
            model: Gemini model to use
            enable_thinking: Enable extended thinking mode for complex decisions
        """
        self.model_name = model
        self.api_key = api_key
        self.enable_thinking = enable_thinking
        self.cache = {}  # Decision cache

        if GEMINI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)

            # Configure generation settings
            self.generation_config = {
                "temperature": 0.4,  # Balanced creativity/consistency
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            # Use thinking mode for complex analysis if enabled
            if enable_thinking and "thinking" in model:
                self.model = genai.GenerativeModel(
                    model,
                    generation_config=self.generation_config
                )
            else:
                self.model = genai.GenerativeModel(
                    model,
                    generation_config=self.generation_config
                )

            self.enabled = True
            logger.info(f"✨ Gemini Agent Advisor initialized with {model}")
        else:
            self.model = None
            self.enabled = False
            logger.warning("[WARNING] Gemini Agent Advisor disabled (no API key or library)")

    def analyze_payment_decision(
        self,
        transaction: Dict[str, Any],
        agent_state: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a payment decision with AI intelligence

        Args:
            transaction: Transaction details
            agent_state: Current agent financial state
            market_context: Optional market data (gas prices, yields, etc)

        Returns:
            Dict with:
                - recommendation: "approve", "reject", "defer", "optimize"
                - confidence: 0.0-1.0
                - reasoning: Detailed explanation
                - optimization_tips: List of suggestions
                - risk_factors: Identified risks
                - expected_roi: Predicted return on investment
        """
        if not self.enabled:
            return self._fallback_payment_analysis(transaction, agent_state)

        try:
            # Check cache first
            cache_key = self._generate_cache_key(transaction, agent_state)
            if cache_key in self.cache:
                logger.info("[BATCH] Using cached decision")
                return self.cache[cache_key]

            # Build prompt
            prompt = self._build_payment_prompt(transaction, agent_state, market_context)

            # Call Gemini
            logger.info("[AGENT] Analyzing payment with Gemini AI...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    **self.generation_config,
                    "response_mime_type": "application/json"
                }
            )

            # Parse response
            result = json.loads(response.text)

            # Add metadata
            result["analysis_timestamp"] = datetime.now().isoformat()
            result["model"] = self.model_name
            result["cache_hit"] = False

            # Cache result
            self.cache[cache_key] = result

            logger.info(
                f"[SUCCESS] Gemini recommendation: {result.get('recommendation')} "
                f"(confidence: {result.get('confidence', 0):.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"[ERROR] Gemini analysis failed: {e}")
            return self._fallback_payment_analysis(transaction, agent_state)

    def detect_fraud_patterns(
        self,
        transaction: Dict[str, Any],
        agent_history: List[Dict[str, Any]],
        global_patterns: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Advanced fraud detection using AI pattern recognition

        Args:
            transaction: Current transaction to analyze
            agent_history: Agent's transaction history
            global_patterns: Known fraud patterns from other agents

        Returns:
            Dict with:
                - fraud_score: 0.0-1.0
                - fraud_indicators: List of suspicious patterns
                - similar_cases: References to similar fraud cases
                - recommended_action: "block", "review", "approve"
                - explanation: Human-readable explanation
        """
        if not self.enabled:
            return self._fallback_fraud_detection(transaction, agent_history)

        try:
            prompt = self._build_fraud_detection_prompt(
                transaction,
                agent_history,
                global_patterns
            )

            logger.info("[EMOJI]️ Running AI fraud detection...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    **self.generation_config,
                    "temperature": 0.2,  # Lower temp for fraud detection
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(response.text)
            result["detection_timestamp"] = datetime.now().isoformat()
            result["model"] = self.model_name

            fraud_score = result.get("fraud_score", 0.0)
            logger.info(f"[SHIELD] Fraud score: {fraud_score:.2f}")

            return result

        except Exception as e:
            logger.error(f"[ERROR] Fraud detection failed: {e}")
            return self._fallback_fraud_detection(transaction, agent_history)

    def optimize_resources(
        self,
        agent_state: Dict[str, Any],
        pending_transactions: List[Dict[str, Any]],
        market_opportunities: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide financial advice for optimal resource usage

        Args:
            agent_state: Current financial state
            pending_transactions: Queue of pending transactions
            market_opportunities: Available DeFi opportunities

        Returns:
            Dict with:
                - strategy: "conservative", "balanced", "aggressive"
                - allocation_advice: How to allocate funds
                - priority_queue: Reordered transaction priorities
                - yield_opportunities: Suggested yield strategies
                - cost_savings: Identified cost reduction opportunities
                - expected_gains: Projected financial improvement
        """
        if not self.enabled:
            return self._fallback_optimization(agent_state, pending_transactions)

        try:
            prompt = self._build_optimization_prompt(
                agent_state,
                pending_transactions,
                market_opportunities
            )

            logger.info("[INFO] Generating optimization strategy...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    **self.generation_config,
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(response.text)
            result["optimization_timestamp"] = datetime.now().isoformat()
            result["model"] = self.model_name

            logger.info(f"[ANALYTICS] Strategy: {result.get('strategy')}")

            return result

        except Exception as e:
            logger.error(f"[ERROR] Optimization failed: {e}")
            return self._fallback_optimization(agent_state, pending_transactions)

    def assess_supplier_risk(
        self,
        supplier: str,
        transaction_history: Optional[List[Dict[str, Any]]] = None,
        market_reputation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deep supplier risk assessment using AI

        Args:
            supplier: Supplier address or name
            transaction_history: Past transactions with this supplier
            market_reputation: External reputation data

        Returns:
            Dict with:
                - risk_level: "low", "medium", "high", "critical"
                - risk_score: 0.0-1.0
                - risk_factors: Identified risk factors
                - trust_indicators: Positive trust signals
                - recommendation: Action recommendation
                - monitoring_suggested: Whether to monitor closely
        """
        if not self.enabled:
            return self._fallback_supplier_risk(supplier)

        try:
            prompt = self._build_supplier_risk_prompt(
                supplier,
                transaction_history,
                market_reputation
            )

            logger.info(f"[SEARCH] Assessing supplier risk: {supplier[:20]}...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    **self.generation_config,
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(response.text)
            result["assessment_timestamp"] = datetime.now().isoformat()
            result["supplier"] = supplier

            logger.info(f"[STEP] Risk level: {result.get('risk_level')}")

            return result

        except Exception as e:
            logger.error(f"[ERROR] Supplier risk assessment failed: {e}")
            return self._fallback_supplier_risk(supplier)

    def generate_financial_insights(
        self,
        agent_state: Dict[str, Any],
        transaction_history: List[Dict[str, Any]],
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive financial insights and recommendations

        Args:
            agent_state: Current financial state
            transaction_history: Historical transactions
            time_period: Analysis period ("day", "week", "month")

        Returns:
            Dict with:
                - performance_summary: Overall performance metrics
                - spending_patterns: Identified spending patterns
                - efficiency_score: Resource usage efficiency
                - recommendations: Action items for improvement
                - warnings: Potential issues to address
                - opportunities: Identified opportunities
        """
        if not self.enabled:
            return self._fallback_insights(agent_state, transaction_history)

        try:
            prompt = self._build_insights_prompt(
                agent_state,
                transaction_history,
                time_period
            )

            logger.info(f"[GROWTH] Generating {time_period}ly insights...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    **self.generation_config,
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(response.text)
            result["insights_timestamp"] = datetime.now().isoformat()
            result["period"] = time_period

            logger.info("[SUCCESS] Insights generated successfully")

            return result

        except Exception as e:
            logger.error(f"[ERROR] Insights generation failed: {e}")
            return self._fallback_insights(agent_state, transaction_history)

    # ============================================================================
    # PROMPT BUILDERS
    # ============================================================================

    def _build_payment_prompt(
        self,
        transaction: Dict[str, Any],
        agent_state: Dict[str, Any],
        market_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for payment decision analysis"""

        prompt = f"""You are a financial AI advisor for an autonomous banking agent.

TRANSACTION DETAILS:
- Amount: ${transaction.get('amount', 0):.2f}
- Supplier: {transaction.get('supplier', 'Unknown')}
- Description: {transaction.get('description', 'No description')}
- Type: {transaction.get('tx_type', 'Unknown')}

AGENT FINANCIAL STATE:
- Available Balance: ${agent_state.get('available_balance', 0):.2f}
- Invested Balance: ${agent_state.get('invested_balance', 0):.2f}
- Credit Limit: ${agent_state.get('credit_limit', 0):.2f}
- Success Rate: {agent_state.get('successful_transactions', 0)}/{agent_state.get('total_transactions', 0)}
- Reputation Score: {agent_state.get('reputation_score', 1.0):.2f}
- Total Spent: ${agent_state.get('total_spent', 0):.2f}
- Total Earned: ${agent_state.get('total_earned', 0):.2f}
"""

        if market_context:
            prompt += f"\nMARKET CONTEXT:\n{json.dumps(market_context, indent=2)}\n"

        prompt += """
ANALYZE this payment decision considering:
1. Financial viability (can agent afford this?)
2. ROI potential (will this generate returns?)
3. Risk factors (what could go wrong?)
4. Timing (is now the right time?)
5. Alternative options (are there better choices?)
6. Resource optimization (best use of funds?)

Return JSON with:
{
  "recommendation": "approve|reject|defer|optimize",
  "confidence": 0.0-1.0,
  "reasoning": "detailed explanation of your decision",
  "optimization_tips": ["list", "of", "improvement", "suggestions"],
  "risk_factors": ["identified", "risks"],
  "expected_roi": estimated_return_percentage,
  "optimal_timing": "now|wait_X_hours|wait_for_better_conditions",
  "alternative_suppliers": ["optional", "better", "suppliers"],
  "cost_savings_potential": estimated_savings_amount
}
"""
        return prompt

    def _build_fraud_detection_prompt(
        self,
        transaction: Dict[str, Any],
        agent_history: List[Dict[str, Any]],
        global_patterns: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build prompt for fraud detection"""

        prompt = f"""You are an expert fraud detection AI for a banking system.

CURRENT TRANSACTION:
{json.dumps(transaction, indent=2, default=str)}

AGENT TRANSACTION HISTORY (last 10):
{json.dumps(agent_history[-10:] if agent_history else [], indent=2, default=str)}

"""

        if global_patterns:
            prompt += f"KNOWN FRAUD PATTERNS:\n{json.dumps(global_patterns[:5], indent=2, default=str)}\n\n"

        prompt += """
DETECT fraud indicators by analyzing:
1. Transaction patterns (unusual amounts, frequency, timing)
2. Supplier reputation (known scammers, suspicious addresses)
3. Description anomalies (vague, urgent language)
4. Behavioral changes (sudden pattern shifts)
5. Common fraud tactics (phishing, social engineering, fake invoices)
6. Historical patterns (does this match agent's normal behavior?)

Return JSON with:
{
  "fraud_score": 0.0-1.0,
  "fraud_indicators": ["specific", "suspicious", "patterns"],
  "behavioral_anomalies": ["deviations", "from", "normal"],
  "similar_cases": ["references", "to", "known", "fraud"],
  "recommended_action": "block|review|approve",
  "explanation": "clear explanation for non-technical users",
  "severity": "low|medium|high|critical",
  "confidence": 0.0-1.0
}
"""
        return prompt

    def _build_optimization_prompt(
        self,
        agent_state: Dict[str, Any],
        pending_transactions: List[Dict[str, Any]],
        market_opportunities: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for resource optimization"""

        prompt = f"""You are a financial optimization AI for an autonomous agent.

CURRENT FINANCIAL STATE:
{json.dumps(agent_state, indent=2, default=str)}

PENDING TRANSACTIONS ({len(pending_transactions)}):
{json.dumps(pending_transactions[:10], indent=2, default=str)}

"""

        if market_opportunities:
            prompt += f"MARKET OPPORTUNITIES:\n{json.dumps(market_opportunities, indent=2, default=str)}\n\n"

        prompt += """
OPTIMIZE resource allocation by:
1. Prioritizing high-ROI transactions
2. Identifying cost savings opportunities
3. Suggesting yield strategies for idle funds
4. Reordering transaction queue for efficiency
5. Balancing risk vs reward
6. Maximizing credit limit utilization

Return JSON with:
{
  "strategy": "conservative|balanced|aggressive",
  "allocation_advice": {
    "immediate_transactions": percentage,
    "yield_investment": percentage,
    "reserve_buffer": percentage
  },
  "priority_queue": ["ordered", "transaction", "ids"],
  "yield_opportunities": [
    {"protocol": "name", "apy": percentage, "risk": "low|med|high", "recommended_amount": value}
  ],
  "cost_savings": [
    {"area": "description", "potential_savings": amount, "action": "what to do"}
  ],
  "expected_gains": {
    "daily": amount,
    "weekly": amount,
    "monthly": amount
  },
  "risk_level": "low|medium|high",
  "confidence": 0.0-1.0
}
"""
        return prompt

    def _build_supplier_risk_prompt(
        self,
        supplier: str,
        transaction_history: Optional[List[Dict[str, Any]]],
        market_reputation: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for supplier risk assessment"""

        prompt = f"""You are a supplier risk assessment AI.

SUPPLIER: {supplier}

"""

        if transaction_history:
            prompt += f"TRANSACTION HISTORY:\n{json.dumps(transaction_history, indent=2, default=str)}\n\n"

        if market_reputation:
            prompt += f"MARKET REPUTATION:\n{json.dumps(market_reputation, indent=2, default=str)}\n\n"

        prompt += """
ASSESS supplier risk by analyzing:
1. Address patterns (common scam patterns, known addresses)
2. Transaction history (consistency, reliability)
3. Market reputation (reviews, ratings, fraud reports)
4. Business legitimacy (verifiable business info)
5. Red flags (suspicious patterns, warning signs)
6. Trust indicators (positive signals, verified credentials)

Return JSON with:
{
  "risk_level": "low|medium|high|critical",
  "risk_score": 0.0-1.0,
  "risk_factors": ["identified", "risks"],
  "trust_indicators": ["positive", "signals"],
  "recommendation": "approve|review|reject|monitor",
  "monitoring_suggested": boolean,
  "confidence": 0.0-1.0,
  "explanation": "clear reasoning",
  "alternative_suppliers": ["optional", "safer", "alternatives"]
}
"""
        return prompt

    def _build_insights_prompt(
        self,
        agent_state: Dict[str, Any],
        transaction_history: List[Dict[str, Any]],
        time_period: str
    ) -> str:
        """Build prompt for financial insights generation"""

        prompt = f"""You are a financial insights AI analyzing {time_period}ly performance.

AGENT STATE:
{json.dumps(agent_state, indent=2, default=str)}

TRANSACTION HISTORY:
{json.dumps(transaction_history[-50:], indent=2, default=str)}

GENERATE comprehensive insights including:
1. Performance metrics (success rate, ROI, efficiency)
2. Spending patterns (categories, trends, anomalies)
3. Revenue analysis (sources, growth, opportunities)
4. Risk assessment (exposure, vulnerabilities)
5. Optimization opportunities (cost savings, yield improvements)
6. Future projections (trends, predictions)

Return JSON with:
{
  "performance_summary": {
    "success_rate": percentage,
    "roi": percentage,
    "efficiency_score": 0.0-1.0,
    "trend": "improving|stable|declining"
  },
  "spending_patterns": [
    {"category": "name", "amount": value, "percentage": value, "trend": "up|down|stable"}
  ],
  "efficiency_score": 0.0-1.0,
  "recommendations": ["actionable", "improvement", "items"],
  "warnings": ["potential", "issues", "to", "address"],
  "opportunities": ["identified", "growth", "opportunities"],
  "projections": {
    "next_period_revenue": amount,
    "next_period_expenses": amount,
    "confidence": 0.0-1.0
  }
}
"""
        return prompt

    # ============================================================================
    # FALLBACK METHODS (when Gemini is unavailable)
    # ============================================================================

    def _fallback_payment_analysis(
        self,
        transaction: Dict[str, Any],
        agent_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simple rule-based payment analysis"""

        amount = transaction.get('amount', 0)
        available = agent_state.get('available_balance', 0)
        credit_limit = agent_state.get('credit_limit', 0)

        if amount > available + credit_limit:
            recommendation = "reject"
            confidence = 0.95
            reasoning = "Insufficient funds"
        elif amount > available * 0.8:
            recommendation = "defer"
            confidence = 0.7
            reasoning = "Would use most of available balance"
        else:
            recommendation = "approve"
            confidence = 0.6
            reasoning = "Sufficient funds available"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": reasoning,
            "optimization_tips": ["Consider yield opportunities for idle funds"],
            "risk_factors": ["No AI analysis available"],
            "expected_roi": 0.0,
            "method": "rule_based_fallback"
        }

    def _fallback_fraud_detection(
        self,
        transaction: Dict[str, Any],
        agent_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simple rule-based fraud detection"""

        fraud_score = 0.0
        indicators = []

        amount = transaction.get('amount', 0)
        description = transaction.get('description', '').lower()

        # Check for suspicious patterns
        if amount > 1000:
            fraud_score += 0.2
            indicators.append("high_amount")

        if "urgent" in description or "limited" in description:
            fraud_score += 0.3
            indicators.append("urgent_language")

        if len(description) < 10:
            fraud_score += 0.1
            indicators.append("vague_description")

        return {
            "fraud_score": min(fraud_score, 1.0),
            "fraud_indicators": indicators,
            "behavioral_anomalies": [],
            "similar_cases": [],
            "recommended_action": "review" if fraud_score > 0.3 else "approve",
            "explanation": "Rule-based analysis (AI unavailable)",
            "severity": "medium" if fraud_score > 0.3 else "low",
            "confidence": 0.5,
            "method": "rule_based_fallback"
        }

    def _fallback_optimization(
        self,
        agent_state: Dict[str, Any],
        pending_transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simple rule-based optimization"""

        return {
            "strategy": "balanced",
            "allocation_advice": {
                "immediate_transactions": 60,
                "yield_investment": 30,
                "reserve_buffer": 10
            },
            "priority_queue": [tx.get('tx_id') for tx in pending_transactions],
            "yield_opportunities": [],
            "cost_savings": [],
            "expected_gains": {"daily": 0, "weekly": 0, "monthly": 0},
            "risk_level": "medium",
            "confidence": 0.5,
            "method": "rule_based_fallback"
        }

    def _fallback_supplier_risk(self, supplier: str) -> Dict[str, Any]:
        """Simple rule-based supplier risk"""

        # Check for Ethereum address patterns
        if supplier.startswith("0x"):
            if supplier.endswith("0000"):
                risk_level = "high"
                risk_score = 0.8
            else:
                risk_level = "medium"
                risk_score = 0.4
        else:
            risk_level = "low"
            risk_score = 0.2

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": ["No AI analysis available"],
            "trust_indicators": [],
            "recommendation": "review" if risk_score > 0.5 else "approve",
            "monitoring_suggested": risk_score > 0.5,
            "confidence": 0.5,
            "explanation": "Rule-based analysis (AI unavailable)",
            "method": "rule_based_fallback"
        }

    def _fallback_insights(
        self,
        agent_state: Dict[str, Any],
        transaction_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simple rule-based insights"""

        total = agent_state.get('total_transactions', 0)
        successful = agent_state.get('successful_transactions', 0)

        success_rate = (successful / total * 100) if total > 0 else 0

        return {
            "performance_summary": {
                "success_rate": success_rate,
                "roi": 0,
                "efficiency_score": 0.5,
                "trend": "stable"
            },
            "spending_patterns": [],
            "efficiency_score": 0.5,
            "recommendations": ["Enable Gemini AI for detailed insights"],
            "warnings": ["Limited analysis without AI"],
            "opportunities": [],
            "projections": {
                "next_period_revenue": 0,
                "next_period_expenses": 0,
                "confidence": 0.3
            },
            "method": "rule_based_fallback"
        }

    # ============================================================================
    # UTILITIES
    # ============================================================================

    def _generate_cache_key(
        self,
        transaction: Dict[str, Any],
        agent_state: Dict[str, Any]
    ) -> str:
        """Generate cache key for decision caching"""

        key_data = {
            "amount": transaction.get('amount'),
            "supplier": transaction.get('supplier'),
            "balance": agent_state.get('available_balance'),
            "credit": agent_state.get('credit_limit')
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    def clear_cache(self):
        """Clear decision cache"""
        self.cache.clear()
        logger.info("[EMOJI]️ Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get advisor statistics"""
        return {
            "enabled": self.enabled,
            "model": self.model_name,
            "cache_size": len(self.cache),
            "gemini_available": GEMINI_AVAILABLE
        }
