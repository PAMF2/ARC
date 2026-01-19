# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with BaaS Arc.

---

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Common Issues](#common-issues)
  - [Installation Problems](#installation-problems)
  - [Configuration Issues](#configuration-issues)
  - [API Errors](#api-errors)
  - [Transaction Failures](#transaction-failures)
  - [Integration Issues](#integration-issues)
- [Error Messages](#error-messages)
- [Performance Issues](#performance-issues)
- [Network Issues](#network-issues)
- [Debug Mode](#debug-mode)
- [Getting Help](#getting-help)

---

## Quick Diagnostics

### Run System Check

```bash
# Quick health check
python -c "
from banking_syndicate import BankingSyndicate
try:
    syndicate = BankingSyndicate()
    print('✅ System initialized successfully')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Check Dependencies

```bash
# Verify all dependencies are installed
pip list | grep -E "flask|web3|google-generativeai|pydantic"

# Or run:
python -c "
import flask
import web3
import google.generativeai as genai
import pydantic
print('✅ All core dependencies installed')
"
```

### Verify Environment Variables

```bash
# Check critical environment variables
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

required = [
    'ARC_RPC_ENDPOINT',
    'CIRCLE_API_KEY',
    'GEMINI_API_KEY',
    'TREASURY_WALLET_ADDRESS',
    'TREASURY_WALLET_PRIVATE_KEY'
]

missing = [var for var in required if not os.getenv(var)]

if missing:
    print(f'❌ Missing variables: {missing}')
else:
    print('✅ All required environment variables set')
"
```

---

## Common Issues

### Installation Problems

#### Issue: `pip install -r requirements.txt` fails

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Causes & Solutions:**

1. **Python version too old**
   ```bash
   # Check Python version
   python --version

   # Should be 3.10 or higher
   # If not, install Python 3.10+:
   # Windows: Download from python.org
   # Mac: brew install python@3.10
   # Linux: sudo apt install python3.10
   ```

2. **Pip outdated**
   ```bash
   # Update pip
   python -m pip install --upgrade pip

   # Try installation again
   pip install -r requirements.txt
   ```

3. **Network issues**
   ```bash
   # Try with different mirror
   pip install -r requirements.txt --index-url https://pypi.org/simple
   ```

4. **Conflicting packages**
   ```bash
   # Use fresh virtual environment
   python -m venv venv_new
   source venv_new/bin/activate  # Linux/Mac
   # or
   venv_new\Scripts\activate  # Windows

   pip install -r requirements.txt
   ```

#### Issue: ImportError after installation

**Symptom:**
```python
ImportError: cannot import name 'BankingSyndicate'
```

**Solutions:**

1. **Check virtual environment**
   ```bash
   # Ensure venv is activated
   which python  # Linux/Mac - should point to venv
   where python  # Windows - should point to venv
   ```

2. **Reinstall package**
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

3. **Check PYTHONPATH**
   ```bash
   # Add banking directory to path
   export PYTHONPATH="${PYTHONPATH}:/path/to/cyber/banking"
   ```

---

### Configuration Issues

#### Issue: `.env` file not loading

**Symptom:**
```
KeyError: 'ARC_RPC_ENDPOINT'
```

**Solutions:**

1. **Check file location**
   ```bash
   # .env should be in banking/ directory
   ls -la banking/.env

   # If missing, copy from example
   cp banking/.env.example banking/.env
   ```

2. **Check file contents**
   ```bash
   # Verify no comments on same line as values
   # Bad:
   ARC_RPC_ENDPOINT=https://rpc.arc.network  # Arc RPC

   # Good:
   # Arc RPC endpoint
   ARC_RPC_ENDPOINT=https://rpc.arc.network
   ```

3. **Load manually in code**
   ```python
   from dotenv import load_dotenv
   import os

   # Explicit path
   load_dotenv('/absolute/path/to/.env')

   # Verify
   print(os.getenv('ARC_RPC_ENDPOINT'))
   ```

#### Issue: Invalid API keys

**Symptom:**
```
401 Unauthorized: Invalid API key
```

**Solutions:**

1. **Gemini API Key**
   ```bash
   # Get new key from: https://ai.google.dev
   # Add to .env:
   GEMINI_API_KEY=AIzaSy...your_key_here

   # Test key:
   python -c "
   import google.generativeai as genai
   import os
   from dotenv import load_dotenv

   load_dotenv()
   genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

   model = genai.GenerativeModel('gemini-2.0-flash-exp')
   response = model.generate_content('Hello')
   print('✅ Gemini API working')
   "
   ```

2. **Circle API Key**
   ```bash
   # Get key from: https://console.circle.com
   # Ensure using sandbox environment for testing
   CIRCLE_API_KEY=your_key_here
   CIRCLE_ENVIRONMENT=sandbox
   ```

3. **Check key format**
   ```bash
   # No extra spaces or quotes
   # Bad:
   GEMINI_API_KEY = "AIzaSy..."

   # Good:
   GEMINI_API_KEY=AIzaSy...
   ```

---

### API Errors

#### Issue: Connection refused on localhost:5001

**Symptom:**
```
ConnectionError: Connection refused
```

**Solutions:**

1. **Start backend server**
   ```bash
   # Terminal 1
   python baas_backend.py

   # Should see:
   # * Running on http://127.0.0.1:5001
   ```

2. **Check port availability**
   ```bash
   # Check if port is in use
   # Linux/Mac:
   lsof -i :5001

   # Windows:
   netstat -ano | findstr :5001

   # If occupied, kill process or use different port
   ```

3. **Check firewall**
   ```bash
   # Ensure localhost connections allowed
   # Windows: Allow Python in Windows Firewall
   # Linux: sudo ufw allow 5001
   ```

#### Issue: 429 Too Many Requests

**Symptom:**
```
429 Too Many Requests: Rate limit exceeded
```

**Solutions:**

1. **Wait and retry**
   ```python
   import time

   # Exponential backoff
   for attempt in range(3):
       try:
           result = process_transaction(tx)
           break
       except RateLimitError:
           wait_time = 2 ** attempt
           time.sleep(wait_time)
   ```

2. **Adjust rate limits**
   ```python
   # In .env
   RATE_LIMIT_PER_MINUTE=100  # Increase if needed
   ```

3. **Use batch operations**
   ```python
   # Instead of many single requests
   results = syndicate.process_transactions_batch(transactions)
   ```

#### Issue: 500 Internal Server Error

**Symptom:**
```
500 Internal Server Error
```

**Solutions:**

1. **Check backend logs**
   ```bash
   # View recent logs
   tail -f logs/backend.log

   # Or check console output where backend is running
   ```

2. **Enable debug mode**
   ```python
   # In baas_backend.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

3. **Verify all services running**
   ```bash
   # Check dependencies
   python -c "
   from banking_syndicate import BankingSyndicate
   syndicate = BankingSyndicate()
   print('✅ Syndicate initialized')
   "
   ```

---

### Transaction Failures

#### Issue: Transaction rejected with "INSUFFICIENT_FUNDS"

**Symptom:**
```json
{
  "consensus": "REJECTED",
  "reason": "insufficient_funds"
}
```

**Solutions:**

1. **Check agent balance**
   ```python
   agent_state = syndicate.get_agent_state("your_agent_id")
   print(f"Balance: ${agent_state.balance}")
   print(f"Credit: ${agent_state.available_credit}")
   ```

2. **Increase deposit**
   ```python
   # Add more funds
   syndicate.deposit_funds(
       agent_id="your_agent_id",
       amount=100.0
   )
   ```

3. **Check credit limit**
   ```python
   # View credit details
   agent_state = syndicate.get_agent_state("your_agent_id")
   print(f"Credit limit: ${agent_state.credit_limit}")
   print(f"Available: ${agent_state.available_credit}")
   ```

#### Issue: Transaction rejected with "FRAUD_DETECTED"

**Symptom:**
```json
{
  "consensus": "REJECTED",
  "reason": "fraud_detected",
  "risk_score": 0.85
}
```

**Solutions:**

1. **Review transaction details**
   ```python
   # Check what triggered fraud detection
   # Common triggers:
   # - Suspicious language ("URGENT", "ACT NOW")
   # - Unknown suppliers
   # - Unusual amounts
   # - Rapid transactions
   ```

2. **Improve transaction description**
   ```python
   # Bad
   Transaction(
       description="URGENT payment needed NOW!!!"
   )

   # Good
   Transaction(
       description="Monthly subscription payment for API service"
   )
   ```

3. **Whitelist trusted suppliers**
   ```python
   # Add supplier to whitelist
   syndicate.add_trusted_supplier(
       agent_id="your_agent_id",
       supplier_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
       supplier_name="Trusted Corp"
   )
   ```

#### Issue: Transaction timeout

**Symptom:**
```
TimeoutError: Transaction processing timeout after 30s
```

**Solutions:**

1. **Check RPC endpoint**
   ```bash
   # Test Arc RPC
   curl -X POST \
     -H "Content-Type: application/json" \
     --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
     https://rpc.arc.network

   # Should return current block number
   ```

2. **Increase timeout**
   ```python
   # In .env
   TRANSACTION_TIMEOUT=60  # Increase to 60 seconds
   ```

3. **Check network status**
   ```bash
   # Check Arc Network status
   # Visit: https://status.arc.network
   ```

---

### Integration Issues

#### Issue: Gemini AI not responding

**Symptom:**
```
GeminiError: Model request failed
```

**Solutions:**

1. **Check API quota**
   ```bash
   # Visit: https://ai.google.dev/console
   # Check: API quotas and limits
   ```

2. **Verify model name**
   ```python
   # In .env
   GEMINI_MODEL=gemini-2.0-flash-exp  # Correct

   # Not:
   GEMINI_MODEL=gemini-pro  # Old model
   ```

3. **Test Gemini directly**
   ```python
   import google.generativeai as genai

   genai.configure(api_key="your_key")
   model = genai.GenerativeModel("gemini-2.0-flash-exp")

   try:
       response = model.generate_content("Test")
       print("✅ Gemini working")
       print(response.text)
   except Exception as e:
       print(f"❌ Gemini error: {e}")
   ```

#### Issue: Circle API errors

**Symptom:**
```
CircleAPIError: Failed to create wallet
```

**Solutions:**

1. **Check API environment**
   ```bash
   # For testing, use sandbox
   CIRCLE_ENVIRONMENT=sandbox
   CIRCLE_API_KEY=your_sandbox_key

   # For production
   CIRCLE_ENVIRONMENT=production
   CIRCLE_API_KEY=your_production_key
   ```

2. **Verify entity ID**
   ```bash
   # Get from Circle console
   CIRCLE_ENTITY_ID=your_entity_id
   ```

3. **Check Circle API status**
   ```bash
   # Visit: https://status.circle.com
   ```

#### Issue: Aave transaction fails

**Symptom:**
```
AaveError: Deposit transaction failed
```

**Solutions:**

1. **Check USDC approval**
   ```python
   # Ensure USDC is approved for Aave
   await aave.approve_usdc(amount)
   await aave.deposit(amount)
   ```

2. **Verify pool address**
   ```bash
   # In .env
   AAVE_POOL_ADDRESS=0x...correct_address

   # Get from: https://docs.aave.com/developers/deployed-contracts
   ```

3. **Check gas settings**
   ```python
   # Increase gas limit
   tx = {
       'gas': 500000,  # Higher limit
       'gasPrice': w3.eth.gas_price * 1.2  # 20% higher
   }
   ```

---

## Error Messages

### Complete Error Reference

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| `AGT001` | Agent not found | Agent ID doesn't exist | Onboard agent first |
| `AGT002` | Agent already exists | Duplicate agent ID | Use different ID |
| `AGT003` | Agent suspended | Account suspended | Contact support |
| `TRX001` | Invalid transaction format | Missing required fields | Check transaction schema |
| `TRX002` | Amount exceeds limit | Transaction too large | Split into smaller amounts |
| `TRX003` | Insufficient funds | Balance too low | Add funds or reduce amount |
| `TRX004` | Transaction timeout | Processing took too long | Retry or check network |
| `FRD001` | Fraud detected | AI flagged as suspicious | Review and modify transaction |
| `FRD002` | Blacklisted address | Supplier on blacklist | Use different supplier |
| `NET001` | RPC connection failed | Can't reach blockchain | Check RPC endpoint |
| `NET002` | API rate limit | Too many requests | Wait and retry |
| `NET003` | Network timeout | Request took too long | Check internet connection |
| `CFG001` | Missing config | Environment variable not set | Add to .env file |
| `CFG002` | Invalid config value | Value format incorrect | Check .env.example |

### Debugging Error Messages

```python
# Enable detailed error logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run transaction
try:
    result = syndicate.process_transaction(tx, agent_state)
except Exception as e:
    logging.error(f"Transaction failed: {e}", exc_info=True)
```

---

## Performance Issues

### Issue: Slow transaction processing

**Symptom:**
Transactions taking > 20 seconds

**Diagnosis:**

```python
# Enable timing metrics
from time import time

start = time()
result = syndicate.process_transaction(tx, agent_state)
elapsed = time() - start

print(f"Total time: {elapsed:.2f}s")
print(f"Breakdown: {result.timing_breakdown}")
```

**Solutions:**

1. **Check RPC latency**
   ```bash
   # Test RPC response time
   time curl -X POST \
     -H "Content-Type: application/json" \
     --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
     https://rpc.arc.network

   # Should be < 1 second
   ```

2. **Optimize Gemini calls**
   ```python
   # Cache Gemini responses
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def cached_gemini_analysis(tx_hash):
       return gemini_detector.analyze(tx)
   ```

3. **Use async operations**
   ```python
   # Process divisions in parallel
   import asyncio

   async def process_parallel():
       results = await asyncio.gather(
           front_office.evaluate(tx),
           risk_compliance.evaluate(tx),
           treasury.evaluate(tx)
       )
       return results
   ```

### Issue: High memory usage

**Symptom:**
Python process using excessive RAM

**Solutions:**

1. **Clear transaction history**
   ```python
   # Limit stored transactions
   MAX_HISTORY = 1000

   if len(agent_state.transaction_history) > MAX_HISTORY:
       agent_state.transaction_history = agent_state.transaction_history[-MAX_HISTORY:]
   ```

2. **Implement pagination**
   ```python
   # Don't load all transactions at once
   def get_transactions(agent_id, page=1, per_page=50):
       start = (page - 1) * per_page
       end = start + per_page
       return transactions[start:end]
   ```

3. **Use generators**
   ```python
   # Instead of loading all at once
   def process_all_agents():
       for agent in get_agents_generator():
           yield process_agent(agent)
   ```

---

## Network Issues

### Issue: Can't connect to Arc Network

**Symptom:**
```
Web3Exception: Could not connect to RPC endpoint
```

**Solutions:**

1. **Test RPC endpoint**
   ```bash
   # Test connection
   curl -X POST \
     -H "Content-Type: application/json" \
     --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}' \
     https://rpc.arc.network
   ```

2. **Try alternative endpoints**
   ```bash
   # In .env, try:
   ARC_RPC_ENDPOINT=https://rpc.arc.network
   # Or:
   ARC_RPC_ENDPOINT=https://rpc-backup.arc.network
   ```

3. **Check firewall/proxy**
   ```bash
   # Ensure outbound HTTPS allowed
   # Test with:
   curl -I https://rpc.arc.network
   ```

### Issue: Transactions not confirming

**Symptom:**
Transaction stuck in pending state

**Solutions:**

1. **Check transaction status**
   ```python
   receipt = w3.eth.get_transaction_receipt(tx_hash)
   print(f"Status: {receipt['status']}")  # 1 = success, 0 = failed
   ```

2. **Increase gas price**
   ```python
   # Use higher gas price
   gas_price = w3.eth.gas_price * 1.5  # 50% higher

   tx = {
       'gasPrice': gas_price,
       # ... other fields
   }
   ```

3. **Check nonce**
   ```python
   # Ensure correct nonce
   nonce = w3.eth.get_transaction_count(address, 'pending')
   ```

---

## Debug Mode

### Enable Debug Logging

```python
# In baas_backend.py or your script

import logging
import structlog

# Configure structlog for debugging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Set log level
logging.basicConfig(level=logging.DEBUG)

# Now all operations will be logged in detail
```

### Debug Transaction Processing

```python
# Add detailed logging to transaction processing

def process_transaction_debug(tx, agent_state):
    logger = structlog.get_logger()

    logger.info("transaction_started", tx_id=tx.tx_id)

    # Front Office
    logger.info("front_office_evaluating")
    fo_result = front_office.evaluate(tx, agent_state)
    logger.info("front_office_result", evaluation=fo_result.evaluation)

    # Risk & Compliance
    logger.info("risk_compliance_evaluating")
    rc_result = risk_compliance.evaluate(tx, agent_state)
    logger.info("risk_compliance_result",
                evaluation=rc_result.evaluation,
                risk_score=rc_result.risk_score)

    # Treasury
    logger.info("treasury_evaluating")
    tr_result = treasury.evaluate(tx, agent_state)
    logger.info("treasury_result", evaluation=tr_result.evaluation)

    # Clearing
    logger.info("clearing_evaluating")
    cl_result = clearing.evaluate(tx, agent_state)
    logger.info("clearing_result", evaluation=cl_result.evaluation)

    logger.info("transaction_completed", consensus=result.consensus)

    return result
```

### Interactive Debugging

```python
# Use Python debugger
import pdb

def process_transaction(tx, agent_state):
    # Set breakpoint
    pdb.set_trace()

    # Process transaction
    result = syndicate.process_transaction(tx, agent_state)

    return result

# When breakpoint hits, you can:
# - Inspect variables: print(tx)
# - Step through code: n (next), s (step into)
# - Continue: c
# - Quit: q
```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Search existing issues**: [GitHub Issues](https://github.com/baas-arc/issues)
3. **Review documentation**: [docs.baas-arc.dev](https://docs.baas-arc.dev)
4. **Try debug mode** to get more information

### Reporting Issues

When reporting an issue, include:

```markdown
**Issue Description:**
[Clear description of the problem]

**Environment:**
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- BaaS Arc version: [e.g., 0.3.0]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [...]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Messages:**
```
[Paste full error message with stack trace]
```

**Logs:**
```
[Paste relevant log entries]
```

**Configuration:**
[Share .env settings - REDACT sensitive keys!]

**Additional Context:**
[Any other relevant information]
```

### Contact Support

- **GitHub Issues**: [github.com/baas-arc/issues](https://github.com/baas-arc/issues)
- **Discord**: [discord.gg/baas-arc](https://discord.gg/baas-arc)
- **Email**: support@baas-arc.dev
- **Emergency**: security@baas-arc.dev (security issues only)

### Community Resources

- **Documentation**: [docs.baas-arc.dev](https://docs.baas-arc.dev)
- **Discord Community**: Real-time help from community
- **Stack Overflow**: Tag questions with `baas-arc`
- **GitHub Discussions**: For general questions

---

## Common Solutions Summary

### Quick Fixes

```bash
# Reset everything
rm -rf venv banking_data logs
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
python baas_backend.py

# Clear cache
rm -rf __pycache__ */__pycache__

# Reset agent data
rm -rf banking_data/*.json

# Fresh start
git pull
pip install -r requirements.txt --upgrade
python baas_setup.py
```

### Verification Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] .env file configured with valid keys
- [ ] Backend server running on port 5001
- [ ] RPC endpoint accessible
- [ ] API keys valid and not rate-limited
- [ ] Firewall allows localhost connections
- [ ] Sufficient disk space for logs

---

**Still having issues?** Join our Discord for real-time help: [discord.gg/baas-arc](https://discord.gg/baas-arc)

**Found a bug?** Report it: [github.com/baas-arc/issues](https://github.com/baas-arc/issues)

---

**BaaS Arc - We're here to help!**

*Autonomous Banking for AI Agents*
