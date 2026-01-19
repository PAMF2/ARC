"""
Banking Syndicate Configuration
Central configurations for the Autonomous Banking Syndicate
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BankingConfig:
    """Banking system configuration"""

    # Blockchain Configuration - Arc Sepolia
    NETWORK: str = "arc-sepolia"  # Arc testnet with USDC gas
    RPC_URL: str = "https://sepolia.rpc.arcscan.xyz"
    CHAIN_ID: int = 93027492

    # Arc Network Configuration
    ARC_MAINNET_RPC: str = "https://rpc.arcscan.xyz"
    ARC_MAINNET_CHAIN_ID: int = 1234567890  # Placeholder - update with actual

    # Native Gas Token (USDC on Arc)
    GAS_TOKEN: str = "USDC"
    GAS_TOKEN_DECIMALS: int = 6

    # Circle USDC Integration
    CIRCLE_API_URL: str = "https://api.circle.com/v1"
    USDC_TOKEN_ADDRESS: str = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # USDC on Arc Sepolia
    USDC_MAINNET_ADDRESS: str = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"  # Update with Arc mainnet USDC

    # Aave Protocol (Arc - if available)
    # Note: These need to be updated with actual Arc deployment addresses
    AAVE_POOL_ADDRESS: str = "0x6C9fB0D5bD9429eb9Cd96B85B81d872281771E6B"  # Update for Arc
    AAVE_USDC_ADDRESS: str = "0x52D800ca262522580CeBAD275395ca6e7598C014"  # Update for Arc
    TREASURY_ALLOCATION_PERCENT: float = 0.80  # 80% in yield
    
    # ERC-4337 Account Abstraction
    ENTRY_POINT_ADDRESS: str = "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"
    ACCOUNT_FACTORY_ADDRESS: str = "0x9406Cc6185a346906296840746125a0E44976454"
    
    # Risk Management
    DEFAULT_CREDIT_LIMIT: float = 100.0  # USD
    MAX_CREDIT_LIMIT: float = 10000.0  # USD
    MIN_CREDIT_LIMIT: float = 10.0  # USD
    ALPHA: float = 0.05  # Dynamic credit score multiplier
    
    # Transaction Timeouts
    RISK_ANALYSIS_TIMEOUT: int = 2  # seconds (T+2s)
    TREASURY_WITHDRAWAL_TIMEOUT: int = 5  # seconds (T+5s)
    CLEARING_EXECUTION_TIMEOUT: int = 10  # seconds (T+10s)
    POST_AUDIT_TIMEOUT: int = 15  # seconds (T+15s)
    
    # Scam Detection
    SCAM_BLACKLIST: list = None
    MAX_GAS_LIMIT: int = 500000
    SUSPICIOUS_VALUE_THRESHOLD: float = 1000.0  # USD
    
    # Gemini AI Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_RETRIES: int = 3
    
    def __post_init__(self):
        if self.SCAM_BLACKLIST is None:
            self.SCAM_BLACKLIST = [
                "0x0000000000000000000000000000000000000000",
                # Add known scam addresses
            ]

    def is_arc_network(self) -> bool:
        """Checks if using Arc blockchain"""
        return self.NETWORK.startswith("arc-")

    def get_usdc_address(self) -> str:
        """Returns USDC address based on network"""
        if self.NETWORK == "arc-mainnet":
            return self.USDC_MAINNET_ADDRESS
        return self.USDC_TOKEN_ADDRESS

# Global configuration
CONFIG = BankingConfig()

# Network Configurations
NETWORK_CONFIGS = {
    "arc-sepolia": {
        "name": "Arc Sepolia Testnet",
        "rpc_url": "https://sepolia.rpc.arcscan.xyz",
        "chain_id": 93027492,
        "explorer": "https://sepolia.arcscan.xyz",
        "gas_token": "USDC",
        "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        "is_testnet": True
    },
    "arc-mainnet": {
        "name": "Arc Mainnet",
        "rpc_url": "https://rpc.arcscan.xyz",
        "chain_id": 1234567890,  # Update with actual
        "explorer": "https://arcscan.xyz",
        "gas_token": "USDC",
        "usdc_address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",  # Update with actual
        "is_testnet": False
    },
    "polygon-mumbai": {
        "name": "Polygon Mumbai",
        "rpc_url": "https://rpc-mumbai.maticvigil.com",
        "chain_id": 80001,
        "explorer": "https://mumbai.polygonscan.com",
        "gas_token": "MATIC",
        "usdc_address": "0x52D800ca262522580CeBAD275395ca6e7598C014",
        "is_testnet": True
    }
}

# Agent Roles
AGENT_ROLES = {
    "FRONT_OFFICE": "Front-Office & Onboarding",
    "RISK_COMPLIANCE": "Risk & Compliance Division",
    "TREASURY": "Treasury & Wealth Management",
    "CLEARING": "Clearing & Settlement"
}

# Transaction States
TRANSACTION_STATES = {
    "PENDING": "pending",
    "ANALYZING": "analyzing",
    "APPROVED": "approved",
    "REJECTED": "rejected",
    "EXECUTING": "executing",
    "COMPLETED": "completed",
    "FAILED": "failed"
}

# Decision Types
DECISION_TYPES = {
    "APPROVE": "approve",
    "REJECT": "reject",
    "ADJUST": "adjust"
}
