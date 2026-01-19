"""
Blockchain Integration Layer
Web3.py wrapper para interações com blockchain
"""
from typing import Dict, Any, Optional
from web3 import Web3
from eth_account import Account
import logging

logger = logging.getLogger(__name__)

class BlockchainConnector:
    """
    Conecta com blockchain via Web3.py
    Suporta: Arc (USDC gas), Ethereum, Polygon, Arbitrum
    """

    def __init__(self, network: str = "arc-sepolia"):
        """
        Inicializa conexão com blockchain

        Args:
            network: Nome da rede (arc-sepolia, arc-mainnet, ethereum-sepolia, etc)
        """
        self.network = network
        self.rpc_urls = {
            "arc-sepolia": "https://sepolia.rpc.arcscan.xyz",
            "arc-mainnet": "https://rpc.arcscan.xyz",
            "polygon-mumbai": "https://rpc-mumbai.maticvigil.com",
            "ethereum-sepolia": "https://rpc.sepolia.org",
            "polygon-mainnet": "https://polygon-rpc.com",
            "localhost": "http://127.0.0.1:8545"
        }

        self.chain_ids = {
            "arc-sepolia": 93027492,  # Arc Sepolia testnet
            "arc-mainnet": 1234567890,  # Arc Mainnet (placeholder - update with actual)
            "polygon-mumbai": 80001,
            "ethereum-sepolia": 11155111,
            "polygon-mainnet": 137,
            "localhost": 31337
        }

        # Arc uses USDC as native gas token
        self.native_tokens = {
            "arc-sepolia": "USDC",
            "arc-mainnet": "USDC",
            "polygon-mumbai": "MATIC",
            "ethereum-sepolia": "ETH",
            "polygon-mainnet": "MATIC",
            "localhost": "ETH"
        }

        self.w3 = self._connect()
        logger.info(f"Connected to {network} (Chain ID: {self.w3.eth.chain_id}, Gas Token: {self.get_native_token()})")
    
    def _connect(self) -> Web3:
        """Estabelece conexão Web3"""
        rpc_url = self.rpc_urls.get(self.network)
        
        if not rpc_url:
            raise ValueError(f"Unknown network: {self.network}")
        
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not w3.is_connected():
            logger.warning(f"Failed to connect to {self.network}, falling back to localhost")
            w3 = Web3(Web3.HTTPProvider(self.rpc_urls["localhost"]))
        
        return w3
    
    def create_wallet(self) -> Dict[str, str]:
        """
        Cria novo wallet
        
        Returns:
            Dict com address e private_key
        """
        account = Account.create()
        
        return {
            "address": account.address,
            "private_key": account.key.hex()
        }
    
    def get_native_token(self) -> str:
        """
        Retorna o token nativo usado para gas

        Returns:
            Nome do token (USDC, ETH, MATIC)
        """
        return self.native_tokens.get(self.network, "ETH")

    def is_usdc_gas_network(self) -> bool:
        """
        Verifica se a rede usa USDC como gas

        Returns:
            True se for Arc blockchain
        """
        return self.get_native_token() == "USDC"

    def get_balance(self, address: str) -> float:
        """
        Retorna balance em token nativo (USDC/ETH/MATIC)

        Args:
            address: Endereço da wallet

        Returns:
            Balance em unidades nativas
        """
        balance_wei = self.w3.eth.get_balance(address)

        # USDC tem 6 decimais, ETH/MATIC tem 18
        if self.is_usdc_gas_network():
            # USDC usa 6 decimais
            balance = balance_wei / (10 ** 6)
        else:
            # ETH/MATIC usa 18 decimais
            balance = self.w3.from_wei(balance_wei, 'ether')

        return float(balance)
    
    def send_transaction(
        self,
        from_address: str,
        private_key: str,
        to_address: str,
        amount: float,
        gas_limit: int = 21000
    ) -> Dict[str, Any]:
        """
        Envia transação

        Args:
            from_address: Endereço de origem
            private_key: Chave privada
            to_address: Endereço de destino
            amount: Valor em token nativo (USDC/ETH/MATIC)
            gas_limit: Limite de gas

        Returns:
            Transaction receipt
        """
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(from_address)

        # Convert amount to smallest unit (wei equivalent)
        if self.is_usdc_gas_network():
            # USDC tem 6 decimais
            value_in_smallest_unit = int(amount * (10 ** 6))
        else:
            # ETH/MATIC tem 18 decimais
            value_in_smallest_unit = self.w3.to_wei(amount, 'ether')

        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': value_in_smallest_unit,
            'gas': gas_limit,
            'gasPrice': self.w3.eth.gas_price,
            'chainId': self.chain_ids[self.network]
        }

        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        gas_token = self.get_native_token()

        return {
            "tx_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber'],
            "gas_used": receipt['gasUsed'],
            "gas_token": gas_token,
            "status": receipt['status']
        }
    
    def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """
        Estima gas necessário
        
        Args:
            transaction: Dict com parâmetros da transação
        
        Returns:
            Gas estimate
        """
        try:
            gas_estimate = self.w3.eth.estimate_gas(transaction)
            return gas_estimate
        except Exception as e:
            logger.warning(f"Gas estimation failed: {e}, using default")
            return 100000
    
    def is_contract(self, address: str) -> bool:
        """
        Verifica se endereço é um contrato
        
        Args:
            address: Endereço para verificar
        
        Returns:
            True se for contrato
        """
        code = self.w3.eth.get_code(address)
        return len(code) > 0
    
    def get_network_info(self) -> Dict[str, Any]:
        """Retorna informações da rede"""
        gas_token = self.get_native_token()

        # Format gas price based on token type
        if self.is_usdc_gas_network():
            # USDC gas price em micro-USDC (6 decimais)
            gas_price_formatted = self.w3.eth.gas_price / (10 ** 6)
            gas_unit = "micro-USDC"
        else:
            # ETH/MATIC gas price em gwei
            gas_price_formatted = self.w3.from_wei(self.w3.eth.gas_price, 'gwei')
            gas_unit = "gwei"

        return {
            "network": self.network,
            "chain_id": self.w3.eth.chain_id,
            "connected": self.w3.is_connected(),
            "latest_block": self.w3.eth.block_number,
            "gas_price": gas_price_formatted,
            "gas_unit": gas_unit,
            "gas_token": gas_token,
            "is_arc": self.is_usdc_gas_network()
        }

    def switch_network(self, network: str) -> None:
        """
        Troca para outra rede

        Args:
            network: Nome da nova rede
        """
        if network not in self.rpc_urls:
            raise ValueError(f"Unknown network: {network}")

        old_network = self.network
        self.network = network
        self.w3 = self._connect()

        logger.info(f"Switched from {old_network} to {network} (Chain ID: {self.w3.eth.chain_id}, Gas Token: {self.get_native_token()})")
