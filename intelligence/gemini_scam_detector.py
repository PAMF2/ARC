"""
Gemini AI-Powered Scam Detector
Usa Google Gemini para detectar padrões suspeitos em transações
"""
from typing import Dict, Any, Optional, List
import logging
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Using fallback scam detection.")

logger = logging.getLogger(__name__)

class GeminiScamDetector:
    """
    AI-powered scam detection usando Gemini
    Analisa transações para detectar padrões suspeitos
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        Inicializa Gemini scam detector
        
        Args:
            api_key: Google AI API key
            model: Modelo Gemini a usar
        """
        self.model_name = model
        self.api_key = api_key
        
        if GEMINI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
            self.enabled = True
            logger.info(f"Gemini scam detector initialized with {model}")
        else:
            self.model = None
            self.enabled = False
            logger.warning("Gemini scam detector disabled (no API key or library)")
    
    def analyze_transaction(
        self,
        transaction: Dict[str, Any],
        agent_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analisa transação para detectar scam
        
        Args:
            transaction: Dados da transação
            agent_history: Histórico de transações do agente
        
        Returns:
            Dict com risk_score, reasoning, e flags
        """
        if not self.enabled:
            return self._fallback_analysis(transaction)
        
        try:
            # Prepara prompt para Gemini
            prompt = self._build_prompt(transaction, agent_history)
            
            # Chama Gemini
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )
            
            # Parse response
            result = json.loads(response.text)
            
            logger.info(f"Gemini analysis: risk={result.get('risk_score', 0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._fallback_analysis(transaction)
    
    def _build_prompt(
        self,
        transaction: Dict[str, Any],
        agent_history: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Constrói prompt para Gemini"""
        
        prompt = f"""You are a fraud detection AI for an autonomous banking system.

Analyze this transaction for scam/fraud indicators:

Transaction Details:
- Amount: ${transaction.get('amount', 0)}
- Supplier: {transaction.get('supplier', 'Unknown')}
- Description: {transaction.get('description', 'No description')}
- Type: {transaction.get('tx_type', 'Unknown')}
- Metadata: {json.dumps(transaction.get('metadata', {}), indent=2)}

Agent History:
"""
        
        if agent_history:
            prompt += f"- Total transactions: {len(agent_history)}\n"
            prompt += f"- Recent patterns: {json.dumps(agent_history[-3:], indent=2)}\n"
        else:
            prompt += "- First transaction (no history)\n"
        
        prompt += """
Analyze for:
1. Unusual amounts (too high or round numbers)
2. Suspicious supplier names
3. Vague descriptions
4. Pattern anomalies compared to history
5. Known scam indicators

Return JSON with:
{{
  "risk_score": 0.0-1.0,
  "reasoning": "brief explanation",
  "flags": ["list", "of", "suspicious", "indicators"],
  "recommendation": "approve|review|reject"
}}
"""
        
        return prompt
    
    def _fallback_analysis(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback analysis sem Gemini (rule-based)
        """
        risk_score = 0.0
        flags = []
        
        amount = transaction.get('amount', 0)
        supplier = transaction.get('supplier', '')
        description = transaction.get('description', '')
        
        # Heurísticas simples
        if amount > 1000:
            risk_score += 0.2
            flags.append("high_amount")
        
        if amount % 100 == 0:  # Round number
            risk_score += 0.1
            flags.append("round_amount")
        
        if len(description) < 10:
            risk_score += 0.15
            flags.append("vague_description")
        
        if not supplier or supplier.lower() == "unknown":
            risk_score += 0.3
            flags.append("unknown_supplier")
        
        # Palavras suspeitas
        suspicious_words = ["urgent", "limited time", "act now", "guaranteed", "free money"]
        if any(word in description.lower() for word in suspicious_words):
            risk_score += 0.4
            flags.append("suspicious_language")
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score > 0.7:
            recommendation = "reject"
        elif risk_score > 0.4:
            recommendation = "review"
        else:
            recommendation = "approve"
        
        return {
            "risk_score": risk_score,
            "reasoning": f"Fallback analysis detected {len(flags)} risk factors",
            "flags": flags,
            "recommendation": recommendation,
            "method": "rule_based"
        }
    
    def batch_analyze(
        self,
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analisa múltiplas transações em batch
        
        Args:
            transactions: Lista de transações
        
        Returns:
            Lista de análises
        """
        results = []
        
        for tx in transactions:
            analysis = self.analyze_transaction(tx)
            results.append({
                "transaction_id": tx.get('tx_id'),
                "analysis": analysis
            })
        
        return results
