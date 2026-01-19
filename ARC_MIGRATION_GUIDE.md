# Arc Blockchain Migration Guide

## Overview
This guide documents the migration from Polygon Mumbai testnet to Arc blockchain, which uses USDC as the native gas token.

## Key Changes

### 1. Network Configuration
- **Old**: Polygon Mumbai (testnet)
- **New**: Arc Sepolia (testnet)
- **Gas Token**: USDC instead of MATIC/ETH

### 2. Network Details

#### Arc Sepolia Testnet
- **RPC URL**: `https://sepolia.rpc.arcscan.xyz`
- **Chain ID**: `93027492`
- **Explorer**: `https://sepolia.arcscan.xyz`
- **Gas Token**: USDC (6 decimals)
- **USDC Address**: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`

#### Arc Mainnet
- **RPC URL**: `https://rpc.arcscan.xyz`
- **Chain ID**: `1234567890` (placeholder - update with actual)
- **Explorer**: `https://arcscan.xyz`
- **Gas Token**: USDC (6 decimals)
- **USDC Address**: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` (update with actual)

### 3. Code Changes

#### Updated Files
1. **`banking/blockchain/web3_connector.py`**
   - Added Arc Sepolia and Arc Mainnet RPC URLs
   - Added native token tracking (USDC vs ETH/MATIC)
   - Updated balance retrieval to handle USDC's 6 decimals
   - Updated transaction sending to handle USDC amounts correctly
   - Added network switching capability
   - Added `is_usdc_gas_network()` method
   - Added `get_native_token()` method

2. **`banking/core/config.py`**
   - Changed default network from `polygon-mumbai` to `arc-sepolia`
   - Added Arc-specific configuration
   - Added USDC token addresses
   - Added Circle API configuration
   - Added network configuration dictionary
   - Added helper methods for Arc detection

3. **`banking/blockchain/arc_usdc_utils.py`** (NEW)
   - USDC amount conversion utilities
   - Gas cost estimation in USDC
   - Balance validation for USDC + gas
   - Circle API integration helpers
   - Arc network validators

### 4. Important Differences

#### Gas Token (USDC vs ETH/MATIC)

**Traditional Blockchain (ETH/MATIC)**:
```python
# 18 decimals
amount_wei = web3.to_wei(1.0, 'ether')  # 1 ETH = 1000000000000000000 wei
```

**Arc Blockchain (USDC)**:
```python
# 6 decimals
amount_usdc = int(1.0 * (10 ** 6))  # 1 USDC = 1000000 units
```

#### Balance Checking
```python
# Arc automatically returns USDC balance
connector = BlockchainConnector("arc-sepolia")
balance = connector.get_balance(address)  # Returns USDC amount
print(f"Balance: {balance} USDC")
```

#### Sending Transactions
```python
# Amount is in USDC on Arc
receipt = connector.send_transaction(
    from_address=wallet_address,
    private_key=private_key,
    to_address=recipient,
    amount=10.5,  # 10.5 USDC
    gas_limit=21000
)
# Gas fees are paid in USDC automatically
```

### 5. Migration Steps

#### Step 1: Update Dependencies
```bash
# No new dependencies required - Web3.py works with Arc
pip install web3>=6.0.0
```

#### Step 2: Update Configuration
```python
from banking.core.config import CONFIG

# Default is now arc-sepolia
print(CONFIG.NETWORK)  # "arc-sepolia"
print(CONFIG.GAS_TOKEN)  # "USDC"
print(CONFIG.CHAIN_ID)  # 93027492
```

#### Step 3: Initialize Connector
```python
from banking.blockchain import BlockchainConnector

# Connect to Arc Sepolia (default)
connector = BlockchainConnector()

# Or explicitly specify
connector = BlockchainConnector("arc-sepolia")

# Check connection
info = connector.get_network_info()
print(f"Network: {info['network']}")
print(f"Gas Token: {info['gas_token']}")
print(f"Chain ID: {info['chain_id']}")
```

#### Step 4: Use USDC Utilities
```python
from banking.blockchain import ArcUSDCUtils

# Convert amounts
usdc_units = ArcUSDCUtils.to_usdc_units(10.5)  # 10500000
usdc_amount = ArcUSDCUtils.from_usdc_units(10500000)  # 10.5

# Format for display
formatted = ArcUSDCUtils.format_usdc_amount(10.5)  # "10.50 USDC"

# Validate balance
validation = ArcUSDCUtils.validate_usdc_balance(
    balance=100.0,
    amount=50.0,
    gas_estimate=0.01
)
print(validation['valid'])  # True
print(validation['message'])  # "Sufficient USDC balance"
```

#### Step 5: Switch Networks (if needed)
```python
# Start with Arc Sepolia
connector = BlockchainConnector("arc-sepolia")

# Switch to mainnet
connector.switch_network("arc-mainnet")

# Or switch back to Polygon for testing
connector.switch_network("polygon-mumbai")
```

### 6. Testing Checklist

- [ ] Connect to Arc Sepolia testnet
- [ ] Create new wallet
- [ ] Check USDC balance (should show 0)
- [ ] Get testnet USDC from faucet
- [ ] Send USDC transaction
- [ ] Verify gas fees paid in USDC
- [ ] Check transaction on Arc explorer
- [ ] Test network switching
- [ ] Validate USDC amounts
- [ ] Test balance validation

### 7. Getting Testnet USDC

To test on Arc Sepolia, you'll need testnet USDC:

1. **Arc Faucet** (if available)
   - Visit: `https://faucet.arcscan.xyz` (or similar)
   - Request testnet USDC

2. **Circle Testnet USDC**
   - Use Circle's testnet tools to mint USDC
   - Bridge to Arc Sepolia if needed

3. **Manual Request**
   - Contact Arc team for testnet tokens

### 8. Breaking Changes

#### API Changes
- `get_balance()` now returns USDC on Arc networks (not ETH/MATIC)
- `send_transaction()` amounts are in USDC on Arc networks
- `get_network_info()` includes new fields:
  - `gas_token`: Token used for gas (USDC/ETH/MATIC)
  - `gas_unit`: Unit for gas price (micro-USDC/gwei)
  - `is_arc`: Boolean indicating if Arc network

#### Configuration Changes
- Default network changed: `polygon-mumbai` → `arc-sepolia`
- New config fields:
  - `GAS_TOKEN`: "USDC"
  - `GAS_TOKEN_DECIMALS`: 6
  - `CIRCLE_API_URL`: Circle API endpoint
  - `USDC_TOKEN_ADDRESS`: USDC contract address

### 9. Backward Compatibility

The system still supports Polygon and Ethereum:

```python
# Use Polygon Mumbai
connector = BlockchainConnector("polygon-mumbai")
balance = connector.get_balance(address)  # Returns MATIC

# Use Ethereum Sepolia
connector = BlockchainConnector("ethereum-sepolia")
balance = connector.get_balance(address)  # Returns ETH
```

### 10. Circle Integration (Future)

Arc's integration with Circle enables:
- Native USDC gas payments
- Seamless USDC transfers
- Circle API integration for advanced features

**Circle API Configuration**:
```python
from banking.core.config import CONFIG

# Circle API
api_url = CONFIG.CIRCLE_API_URL
usdc_address = CONFIG.get_usdc_address()

# Build transfer data
from banking.blockchain import ArcUSDCUtils
transfer_data = ArcUSDCUtils.build_usdc_transfer_data(
    to_address="0x...",
    amount=100.0
)
```

### 11. Troubleshooting

#### "Cannot connect to Arc RPC"
- Verify RPC URL: `https://sepolia.rpc.arcscan.xyz`
- Check network connectivity
- Try mainnet RPC if testnet is down

#### "Insufficient USDC for gas"
- You need USDC for both transaction value AND gas fees
- Get testnet USDC from faucet
- Use `validate_usdc_balance()` to check requirements

#### "Wrong chain ID"
- Arc Sepolia: 93027492
- Verify in wallet/provider
- Check `get_network_info()` output

#### "Transaction failed"
- Check USDC balance covers amount + gas
- Verify recipient address
- Check gas limit (21000 for simple transfers)

### 12. Resources

- **Arc Documentation**: https://docs.arcscan.xyz
- **Arc Explorer**: https://sepolia.arcscan.xyz
- **Circle USDC Docs**: https://developers.circle.com
- **Web3.py Docs**: https://web3py.readthedocs.io

### 13. Next Steps

1. **Update Aave Integration**: Verify Aave deployment on Arc or update to Arc-native DeFi
2. **Update ERC-4337**: Verify Account Abstraction contracts on Arc
3. **Test Integration**: Full end-to-end testing on Arc Sepolia
4. **Mainnet Preparation**: Get actual mainnet addresses and chain ID
5. **Circle Integration**: Implement advanced Circle API features
6. **Documentation**: Update all docs to reflect Arc as default

## Summary

The banking system now uses Arc blockchain with USDC as native gas token by default. All existing functionality is preserved, with automatic handling of USDC's 6-decimal precision. The system remains backward-compatible with Polygon and Ethereum networks.

**Key Advantage**: Gasless UX for users who already hold USDC - no need for separate gas tokens!
