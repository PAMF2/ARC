"""
Integration Tests para Blockchain Layer
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

from blockchain.web3_connector import BlockchainConnector
from blockchain.erc4337_wallet import ERC4337Wallet
from blockchain.aave_integration import AaveIntegration

class TestBlockchainConnector:
    """Testes para BlockchainConnector"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.connector = BlockchainConnector(network="localhost")
    
    def test_create_wallet(self):
        """Testa criação de wallet"""
        wallet = self.connector.create_wallet()
        
        assert "address" in wallet
        assert "private_key" in wallet
        assert wallet["address"].startswith("0x")
    
    def test_network_info(self):
        """Testa obtenção de info da rede"""
        info = self.connector.get_network_info()
        
        assert "network" in info
        assert "chain_id" in info
        assert "connected" in info

class TestERC4337Wallet:
    """Testes para ERC-4337 Wallet"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.connector = BlockchainConnector(network="localhost")
        self.wallet = ERC4337Wallet(
            self.connector,
            entry_point_address="0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789",
            factory_address="0x9406Cc6185a346906296840746125a0E44976454"
        )
    
    def test_create_account(self):
        """Testa criação de Smart Account"""
        owner = "0x" + "1" * 40
        
        result = self.wallet.create_account(owner)
        
        assert "account_address" in result
        assert result["owner"] == owner
    
    def test_get_account_address(self):
        """Testa cálculo de endereço"""
        owner = "0x" + "1" * 40
        
        address1 = self.wallet.get_account_address(owner, salt=0)
        address2 = self.wallet.get_account_address(owner, salt=0)
        
        # Mesmo salt = mesmo endereço (determinístico)
        assert address1 == address2
        
        # Salt diferente = endereço diferente
        address3 = self.wallet.get_account_address(owner, salt=1)
        assert address1 != address3

class TestAaveIntegration:
    """Testes para Aave Integration"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.connector = BlockchainConnector(network="localhost")
        self.aave = AaveIntegration(self.connector)
    
    def test_deposit(self):
        """Testa depósito em Aave"""
        wallet_address = "0x" + "1" * 40
        private_key = "0x" + "2" * 64
        
        result = self.aave.deposit(
            wallet_address,
            private_key,
            "USDC",
            100.0
        )
        
        assert result["success"] == True
        assert result["amount"] == 100.0
        assert "apy" in result
    
    def test_withdraw(self):
        """Testa retirada de Aave"""
        wallet_address = "0x" + "1" * 40
        private_key = "0x" + "2" * 64
        
        result = self.aave.withdraw(
            wallet_address,
            private_key,
            "USDC",
            100.0
        )
        
        assert result["success"] == True
        assert result["principal"] == 100.0
        assert "yield_earned" in result
        assert result["total_withdrawn"] > result["principal"]
    
    def test_calculate_yield(self):
        """Testa cálculo de yield"""
        yield_amount = self.aave.calculate_yield(
            amount=1000.0,
            token="USDC",
            days=365
        )
        
        # 1000 * 0.05 * (365/365) = 50
        assert yield_amount > 0
        assert yield_amount <= 1000.0 * 0.1  # Max 10% APY

if __name__ == "__main__":
    print("Running Blockchain Integration Tests...")
    pytest.main([__file__, "-v"])
