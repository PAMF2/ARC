# Arc Blockchain Quick Reference

## Quick Start

```python
from banking.blockchain import BlockchainConnector

# Connect to Arc (default)
arc = BlockchainConnector("arc-sepolia")

# Create wallet
wallet = arc.create_wallet()
print(f"Address: {wallet['address']}")

# Check USDC balance
balance = arc.get_balance(wallet['address'])
print(f"Balance: {balance} USDC")

# Send USDC
receipt = arc.send_transaction(
    from_address=wallet['address'],
    private_key=wallet['private_key'],
    to_address="0x...",
    amount=10.5  # 10.5 USDC
)
```

## Network Info

### Arc Sepolia (Testnet)
```
RPC:      https://sepolia.rpc.arcscan.xyz
Chain ID: 93027492
Explorer: https://sepolia.arcscan.xyz
Gas:      USDC (6 decimals)
```

### Arc Mainnet
```
RPC:      https://rpc.arcscan.xyz
Chain ID: TBD
Explorer: https://arcscan.xyz
Gas:      USDC (6 decimals)
```

## Key Differences from ETH/Polygon

| Feature | ETH/Polygon | Arc |
|---------|-------------|-----|
| Gas Token | ETH/MATIC | USDC |
| Decimals | 18 | 6 |
| Gas Price Unit | gwei | micro-USDC |
| Balance Unit | ETH/MATIC | USDC |

## Common Operations

### Get Network Info
```python
info = arc.get_network_info()
print(info)
# {
#   'network': 'arc-sepolia',
#   'chain_id': 93027492,
#   'gas_token': 'USDC',
#   'is_arc': True,
#   ...
# }
```

### Check Gas Token
```python
token = arc.get_native_token()  # "USDC"
is_usdc = arc.is_usdc_gas_network()  # True
```

### Switch Networks
```python
arc.switch_network("arc-mainnet")
arc.switch_network("polygon-mumbai")  # Backward compatible
```

## USDC Utilities

```python
from banking.blockchain import ArcUSDCUtils

# Convert amounts
units = ArcUSDCUtils.to_usdc_units(10.5)  # 10500000
usdc = ArcUSDCUtils.from_usdc_units(10500000)  # 10.5

# Format
formatted = ArcUSDCUtils.format_usdc_amount(10.5)  # "10.50 USDC"

# Validate balance
check = ArcUSDCUtils.validate_usdc_balance(
    balance=100.0,
    amount=50.0,
    gas_estimate=0.01
)
print(check['valid'])  # True/False
print(check['message'])  # Human-readable result

# Estimate gas cost
cost = ArcUSDCUtils.estimate_transaction_cost(
    gas_limit=21000,
    gas_price_units=100000
)
print(cost['total_cost_usdc'])  # Total in USDC
```

## Network Validation

```python
from banking.blockchain import ArcNetworkValidator

# Validate address
valid = ArcNetworkValidator.validate_arc_address("0x...")

# Validate amount
check = ArcNetworkValidator.validate_usdc_amount(100.0)

# Validate network params
check = ArcNetworkValidator.validate_network_params(
    chain_id=93027492,
    rpc_url="https://sepolia.rpc.arcscan.xyz"
)
```

## Configuration

```python
from banking.core.config import CONFIG, NETWORK_CONFIGS

# Default settings
print(CONFIG.NETWORK)  # "arc-sepolia"
print(CONFIG.GAS_TOKEN)  # "USDC"
print(CONFIG.CHAIN_ID)  # 93027492

# Check if Arc
if CONFIG.is_arc_network():
    usdc_addr = CONFIG.get_usdc_address()

# Get network config
arc_config = NETWORK_CONFIGS["arc-sepolia"]
```

## Error Handling

```python
try:
    receipt = arc.send_transaction(...)
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Transaction failed: {e}")
```

## Testing

```bash
# Run Arc integration tests
cd banking
python test_arc_integration.py
```

## Important Notes

1. **USDC has 6 decimals** (not 18 like ETH)
2. **Gas is paid in USDC** (not separate token)
3. **Need USDC for both** value + gas
4. **Addresses are EVM-compatible** (same format as Ethereum)
5. **Web3.py works normally** (EVM-compatible)

## Common Issues

### "Cannot connect"
→ Check RPC URL is correct
→ Verify internet connection
→ Try mainnet if testnet down

### "Insufficient funds"
→ Need USDC for amount + gas
→ Use faucet to get testnet USDC
→ Check balance with `get_balance()`

### "Invalid chain ID"
→ Arc Sepolia = 93027492
→ Verify in wallet settings
→ Check with `get_network_info()`

## Resources

- Arc Docs: https://docs.arcscan.xyz
- Arc Explorer: https://sepolia.arcscan.xyz
- Circle USDC: https://developers.circle.com
- Web3.py: https://web3py.readthedocs.io

## Migration Checklist

- [ ] Update network to `arc-sepolia`
- [ ] Handle USDC decimals (6 not 18)
- [ ] Update gas calculations
- [ ] Test balance checking
- [ ] Test transactions
- [ ] Verify gas payment in USDC
- [ ] Update docs/UI to show USDC
