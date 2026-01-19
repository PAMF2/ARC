# Gemini AI Integration for Banking Syndicate

**For ARC Hackathon - Google $10k GCP Credits Bonus**

This integration leverages Google's Gemini AI to provide advanced financial intelligence for autonomous banking agents, enabling smart payment decisions, fraud detection, and optimal resource usage.

---

## 🎯 Features

### 1. **Smart Payment Decisions**
- AI analyzes transaction viability, ROI potential, and timing
- Provides optimization tips and alternative recommendations
- Considers market context (gas prices, yields, etc.)
- Returns confidence scores and detailed reasoning

### 2. **Advanced Fraud Detection**
- Deep pattern analysis across transaction history
- Detects behavioral anomalies and suspicious patterns
- Compares against known fraud indicators
- Real-time risk scoring with severity levels

### 3. **Resource Optimization**
- Intelligent fund allocation strategies
- Yield opportunity identification
- Transaction priority optimization
- Cost savings analysis and projections

### 4. **Supplier Risk Assessment**
- AI-powered supplier reputation analysis
- Historical pattern recognition
- Market reputation integration
- Alternative supplier suggestions

### 5. **Financial Insights**
- Performance metrics and trend analysis
- Spending pattern identification
- Future projections with confidence scores
- Actionable recommendations and warnings

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install google-generativeai
```

Already included in `requirements.txt`:
```
google-generativeai==0.4.0
```

### 2. Set API Key

Add to your `.env` file:
```env
GEMINI_API_KEY=your_google_ai_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

### 3. Basic Usage

```python
from intelligence.gemini_agent_advisor import GeminiAgentAdvisor

# Initialize advisor
advisor = GeminiAgentAdvisor(
    api_key="your-api-key",
    model="gemini-2.0-flash-exp"
)

# Analyze a payment decision
result = advisor.analyze_payment_decision(
    transaction=transaction_dict,
    agent_state=agent_state_dict,
    market_context=market_data
)

print(f"Recommendation: {result['recommendation']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
```

---

## 📚 API Reference

### `GeminiAgentAdvisor` Class

#### Initialization

```python
advisor = GeminiAgentAdvisor(
    api_key: Optional[str] = None,
    model: str = "gemini-2.0-flash-exp",
    enable_thinking: bool = False
)
```

**Parameters:**
- `api_key`: Google AI API key (reads from env if not provided)
- `model`: Gemini model to use
  - `"gemini-2.0-flash-exp"` - Fast, balanced (recommended)
  - `"gemini-2.0-flash-thinking-exp"` - Extended thinking for complex analysis
  - `"gemini-1.5-pro"` - Longer context window
- `enable_thinking`: Enable extended reasoning mode

---

### Methods

#### 1. `analyze_payment_decision()`

Smart payment decision analysis.

```python
result = advisor.analyze_payment_decision(
    transaction: Dict[str, Any],
    agent_state: Dict[str, Any],
    market_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "recommendation": "approve|reject|defer|optimize",
    "confidence": 0.95,  # 0.0-1.0
    "reasoning": "Detailed explanation...",
    "optimization_tips": ["tip1", "tip2"],
    "risk_factors": ["risk1", "risk2"],
    "expected_roi": 15.5,  # percentage
    "optimal_timing": "now|wait_X_hours",
    "alternative_suppliers": ["supplier1", "supplier2"],
    "cost_savings_potential": 50.0  # USD
}
```

**Example:**
```python
transaction = {
    "tx_id": "TX-001",
    "amount": 500.0,
    "supplier": "AWS",
    "description": "Cloud compute",
    "tx_type": "purchase"
}

agent_state = {
    "available_balance": 1000.0,
    "credit_limit": 500.0,
    "reputation_score": 0.95
}

result = advisor.analyze_payment_decision(transaction, agent_state)
# => {"recommendation": "approve", "confidence": 0.92, ...}
```

---

#### 2. `detect_fraud_patterns()`

AI-powered fraud detection.

```python
result = advisor.detect_fraud_patterns(
    transaction: Dict[str, Any],
    agent_history: List[Dict[str, Any]],
    global_patterns: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "fraud_score": 0.85,  # 0.0-1.0
    "fraud_indicators": ["indicator1", "indicator2"],
    "behavioral_anomalies": ["anomaly1"],
    "similar_cases": ["case1", "case2"],
    "recommended_action": "block|review|approve",
    "explanation": "Human-readable explanation",
    "severity": "low|medium|high|critical",
    "confidence": 0.88
}
```

**Example:**
```python
suspicious_tx = {
    "amount": 9999.0,  # Round number
    "supplier": "0x0000000000000000000000000000000000000000",
    "description": "URGENT! Act now!"  # Scam language
}

result = advisor.detect_fraud_patterns(suspicious_tx, agent_history)
# => {"fraud_score": 0.95, "recommended_action": "block", ...}
```

---

#### 3. `optimize_resources()`

Financial resource optimization.

```python
result = advisor.optimize_resources(
    agent_state: Dict[str, Any],
    pending_transactions: List[Dict[str, Any]],
    market_opportunities: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "strategy": "conservative|balanced|aggressive",
    "allocation_advice": {
        "immediate_transactions": 60,  # percentage
        "yield_investment": 30,
        "reserve_buffer": 10
    },
    "priority_queue": ["tx_id1", "tx_id2"],
    "yield_opportunities": [
        {
            "protocol": "Aave",
            "apy": 4.5,
            "risk": "low",
            "recommended_amount": 1000.0
        }
    ],
    "cost_savings": [
        {
            "area": "gas_optimization",
            "potential_savings": 50.0,
            "action": "Batch transactions"
        }
    ],
    "expected_gains": {
        "daily": 5.0,
        "weekly": 35.0,
        "monthly": 150.0
    },
    "risk_level": "medium",
    "confidence": 0.85
}
```

---

#### 4. `assess_supplier_risk()`

Supplier risk assessment.

```python
result = advisor.assess_supplier_risk(
    supplier: str,
    transaction_history: Optional[List[Dict[str, Any]]] = None,
    market_reputation: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "risk_level": "low|medium|high|critical",
    "risk_score": 0.3,  # 0.0-1.0
    "risk_factors": ["factor1", "factor2"],
    "trust_indicators": ["indicator1"],
    "recommendation": "approve|review|reject|monitor",
    "monitoring_suggested": False,
    "confidence": 0.78,
    "explanation": "Clear reasoning",
    "alternative_suppliers": ["alt1", "alt2"]
}
```

---

#### 5. `generate_financial_insights()`

Comprehensive financial analysis.

```python
result = advisor.generate_financial_insights(
    agent_state: Dict[str, Any],
    transaction_history: List[Dict[str, Any]],
    time_period: str = "week"  # "day", "week", "month"
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "performance_summary": {
        "success_rate": 92.0,  # percentage
        "roi": 15.5,
        "efficiency_score": 0.88,
        "trend": "improving|stable|declining"
    },
    "spending_patterns": [
        {
            "category": "cloud_services",
            "amount": 1500.0,
            "percentage": 45.0,
            "trend": "up|down|stable"
        }
    ],
    "efficiency_score": 0.88,
    "recommendations": ["rec1", "rec2"],
    "warnings": ["warning1"],
    "opportunities": ["opp1", "opp2"],
    "projections": {
        "next_period_revenue": 5000.0,
        "next_period_expenses": 3500.0,
        "confidence": 0.75
    }
}
```

---

## 🔧 Integration with Risk Compliance Agent

The `RiskComplianceAgent` now uses Gemini AI automatically:

```python
from divisions.risk_compliance_agent import RiskComplianceAgent

# Initialize with Gemini API key
risk_agent = RiskComplianceAgent(
    config={
        'gemini_api_key': 'your-api-key'
    }
)

# Analyze transaction with AI
analysis = risk_agent.analyze_transaction(
    transaction=tx,
    agent_state=state,
    context={}
)

# AI insights in metadata
print(analysis.metadata['fraud_detection'])
print(analysis.metadata['supplier_assessment'])
```

---

## 📊 Example Output

### Payment Decision Analysis
```
🤖 Analyzing payment with Gemini AI...
✅ Gemini recommendation: approve (confidence: 0.92)

RECOMMENDATION: APPROVE
Confidence: 92%
Reasoning: Transaction shows strong ROI potential with manageable risk.
          AWS is a trusted supplier with consistent track record.

Optimization Tips:
  • Consider annual commitment for 15% cost savings
  • Idle funds ($300) could earn 4.5% APY in Aave
  • Schedule during off-peak hours for lower gas fees

Risk Factors:
  • High monthly recurring cost
  • Limited diversification in cloud providers

Expected ROI: 12.5%
Optimal Timing: Now
```

### Fraud Detection
```
🕵️ Running AI fraud detection...
🛡️ Fraud score: 0.85

FRAUD ANALYSIS:
  Fraud Score: 85%
  Severity: HIGH
  Recommended Action: BLOCK
  Confidence: 95%

Fraud Indicators:
  • Suspiciously round amount ($9,999.00)
  • Null address supplier
  • Urgent/pressure language detected
  • Deviates significantly from normal transaction patterns

Explanation: Transaction exhibits multiple red flags consistent with
             known scam patterns. Recommend immediate blocking.
```

---

## 🎨 Advanced Features

### 1. **Decision Caching**

The advisor caches similar decisions to reduce API calls:

```python
# First call - makes API request
result1 = advisor.analyze_payment_decision(tx1, state)

# Similar call - uses cache (instant)
result2 = advisor.analyze_payment_decision(tx1, state)

# Clear cache when needed
advisor.clear_cache()
```

### 2. **Fallback Mode**

If Gemini API is unavailable, the system automatically falls back to rule-based analysis:

```python
advisor = GeminiAgentAdvisor(api_key=None)  # No API key

# Still works, but uses heuristics
result = advisor.analyze_payment_decision(tx, state)
# => {"method": "rule_based_fallback", ...}
```

### 3. **Extended Thinking Mode**

For complex decisions, enable thinking mode:

```python
advisor = GeminiAgentAdvisor(
    api_key="your-key",
    model="gemini-2.0-flash-thinking-exp",
    enable_thinking=True
)

# More detailed analysis with reasoning chains
result = advisor.analyze_payment_decision(complex_tx, state)
```

### 4. **Statistics & Monitoring**

```python
stats = advisor.get_stats()
print(stats)
# => {
#     "enabled": True,
#     "model": "gemini-2.0-flash-exp",
#     "cache_size": 42,
#     "gemini_available": True
# }
```

---

## 🧪 Testing

Run the comprehensive examples:

```bash
cd banking/intelligence
python gemini_integration_example.py
```

This will demonstrate:
1. Smart payment decisions
2. Fraud detection
3. Resource optimization
4. Supplier risk assessment
5. Financial insights generation

---

## 🏗️ Architecture

```
banking/
├── intelligence/
│   ├── gemini_agent_advisor.py       # Main AI advisor
│   ├── gemini_scam_detector.py       # Legacy scam detector
│   ├── gemini_integration_example.py # Usage examples
│   └── README_GEMINI_INTEGRATION.md  # This file
├── divisions/
│   └── risk_compliance_agent.py      # Uses Gemini for risk
└── core/
    └── transaction_types.py          # Data models
```

---

## 💡 Best Practices

### 1. **API Key Security**
```python
# ✅ Good - Use environment variables
api_key = os.getenv('GEMINI_API_KEY')
advisor = GeminiAgentAdvisor(api_key=api_key)

# ❌ Bad - Hardcode API key
advisor = GeminiAgentAdvisor(api_key="AIzaSy...")
```

### 2. **Error Handling**
```python
try:
    result = advisor.analyze_payment_decision(tx, state)
except Exception as e:
    logger.error(f"AI analysis failed: {e}")
    # Fallback to rule-based analysis
    result = fallback_analysis(tx, state)
```

### 3. **Context Management**
```python
# Provide rich context for better AI decisions
result = advisor.analyze_payment_decision(
    transaction=tx,
    agent_state=state,
    market_context={
        "gas_price_gwei": current_gas_price,
        "eth_price_usd": current_eth_price,
        "aave_apy": current_yield_rate,
        "network_congestion": "low|medium|high"
    }
)
```

### 4. **Response Validation**
```python
result = advisor.analyze_payment_decision(tx, state)

# Always check confidence before acting
if result['confidence'] > 0.8:
    # High confidence - act on recommendation
    execute_decision(result['recommendation'])
else:
    # Low confidence - escalate to human review
    request_human_review(tx, result)
```

---

## 🔍 Troubleshooting

### Issue: "Gemini Agent Advisor disabled"

**Solution:**
```bash
# Check if API key is set
echo $GEMINI_API_KEY

# Set API key if missing
export GEMINI_API_KEY="your-key-here"

# Or add to .env file
echo "GEMINI_API_KEY=your-key-here" >> .env
```

### Issue: "google-generativeai not installed"

**Solution:**
```bash
pip install google-generativeai
```

### Issue: API rate limits

**Solution:**
- Use caching to reduce API calls
- Implement exponential backoff
- Consider upgrading to paid tier for higher limits

```python
import time

def analyze_with_retry(advisor, tx, state, max_retries=3):
    for attempt in range(max_retries):
        try:
            return advisor.analyze_payment_decision(tx, state)
        except Exception as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

---

## 📈 Performance Tips

### 1. **Batch Processing**
```python
# Process multiple transactions efficiently
transactions = [tx1, tx2, tx3]
results = []

for tx in transactions:
    result = advisor.analyze_payment_decision(tx, state)
    results.append(result)
```

### 2. **Async Operations** (Future Enhancement)
```python
# Parallel processing for multiple agents
import asyncio

async def analyze_multiple_agents(agents, transactions):
    tasks = [
        advisor.analyze_payment_decision_async(tx, agent.state)
        for agent, tx in zip(agents, transactions)
    ]
    return await asyncio.gather(*tasks)
```

### 3. **Selective AI Usage**
```python
# Use AI only for high-value or suspicious transactions
if tx.amount > 1000 or supplier_risk > 0.5:
    # Use AI for critical decisions
    result = advisor.analyze_payment_decision(tx, state)
else:
    # Use rule-based for simple cases
    result = simple_rule_analysis(tx, state)
```

---

## 🎯 Use Cases

### 1. **Autonomous Trading Agents**
```python
# AI decides optimal trade timing and amounts
trade_decision = advisor.analyze_payment_decision(
    transaction=trade_tx,
    agent_state=trader_state,
    market_context={
        "volatility": market.volatility,
        "liquidity": market.liquidity,
        "trend": market.trend
    }
)

if trade_decision['recommendation'] == 'approve':
    execute_trade(trade_tx)
```

### 2. **Treasury Management**
```python
# Optimize yield farming strategies
optimization = advisor.optimize_resources(
    agent_state=treasury_state,
    pending_transactions=pending_expenses,
    market_opportunities=defi_protocols
)

# Allocate funds based on AI recommendation
allocate_to_yield(optimization['yield_opportunities'])
```

### 3. **Fraud Prevention**
```python
# Real-time fraud detection
for tx in incoming_transactions:
    fraud_check = advisor.detect_fraud_patterns(
        transaction=tx,
        agent_history=recent_history
    )

    if fraud_check['fraud_score'] > 0.7:
        block_transaction(tx)
        alert_admin(fraud_check)
```

---

## 🚀 Future Enhancements

- [ ] Multi-agent consensus (multiple AI models vote)
- [ ] Historical pattern learning (improve over time)
- [ ] Integration with on-chain oracles
- [ ] Real-time market data feeds
- [ ] Advanced portfolio optimization
- [ ] Predictive maintenance for agents
- [ ] Natural language transaction queries
- [ ] Voice-activated AI assistant

---

## 📞 Support

For issues or questions:
- Check existing examples: `gemini_integration_example.py`
- Review API reference above
- Check Gemini AI docs: https://ai.google.dev/docs
- Open GitHub issue with detailed logs

---

## 🏆 ARC Hackathon

**This integration maximizes the $10k Google GCP credits bonus by:**
1. Advanced AI for autonomous agent decisions
2. Real-time fraud detection and prevention
3. Optimal resource allocation and yield farming
4. Scalable to hundreds of agents
5. Production-ready with fallback mechanisms

**Built with ❤️ for the ARC Hackathon**

---

## 📄 License

MIT License - See LICENSE file for details

---

**Happy AI Banking! 🤖💰🚀**
