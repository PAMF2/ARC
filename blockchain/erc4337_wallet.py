"""
ERC-4337 Account Abstraction Implementation
Smart Account para agentes IA
"""
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

# ERC-4337 EntryPoint contract ABI (simplified)
ENTRY_POINT_ABI = [
    {
        "inputs": [
            {"name": "userOp", "type": "tuple"},
            {"name": "beneficiary", "type": "address"}
        ],
        "name": "handleOps",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# SimpleAccount Factory ABI (simplified)
ACCOUNT_FACTORY_ABI = [
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "salt", "type": "uint256"}
        ],
        "name": "createAccount",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "salt", "type": "uint256"}
        ],
        "name": "getAddress",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class ERC4337Wallet:
    """
    ERC-4337 Account Abstraction Wallet
    Permite que agentes IA tenham wallets sem gerenciar private keys diretamente
    """
    
    def __init__(self, web3_connector, entry_point_address: str, factory_address: str):
        """
        Inicializa ERC-4337 wallet
        
        Args:
            web3_connector: Instância de BlockchainConnector
            entry_point_address: Endereço do EntryPoint contract
            factory_address: Endereço do Account Factory
        """
        self.w3 = web3_connector.w3
        self.connector = web3_connector
        self.entry_point_address = entry_point_address
        self.factory_address = factory_address
        
        # Initialize contracts (simulado - em produção usar ABIs reais)
        # self.entry_point = self.w3.eth.contract(address=entry_point_address, abi=ENTRY_POINT_ABI)
        # self.factory = self.w3.eth.contract(address=factory_address, abi=ACCOUNT_FACTORY_ABI)
        
        logger.info(f"ERC-4337 Wallet initialized")
    
    def create_account(self, owner_address: str, salt: int = 0) -> Dict[str, Any]:
        """
        Cria novo Smart Account
        
        Args:
            owner_address: Endereço do owner
            salt: Salt para deterministic address
        
        Returns:
            Dict com account_address e deployment info
        """
        # Em produção: chamar factory.createAccount(owner_address, salt)
        # Por enquanto, simulamos a criação
        
        # Gera endereço determinístico (simulado)
        import hashlib
        deterministic_data = f"{owner_address}{salt}{self.factory_address}"
        account_hash = hashlib.sha256(deterministic_data.encode()).hexdigest()
        account_address = f"0x{account_hash[:40]}"
        
        logger.info(f"Smart Account created: {account_address}")
        
        return {
            "account_address": account_address,
            "owner": owner_address,
            "salt": salt,
            "deployed": False,  # Seria True após deploy real
            "entry_point": self.entry_point_address
        }
    
    def get_account_address(self, owner_address: str, salt: int = 0) -> str:
        """
        Calcula endereço do Smart Account sem deploy
        
        Args:
            owner_address: Endereço do owner
            salt: Salt usado
        
        Returns:
            Account address
        """
        # Em produção: factory.getAddress(owner_address, salt)
        import hashlib
        deterministic_data = f"{owner_address}{salt}{self.factory_address}"
        account_hash = hashlib.sha256(deterministic_data.encode()).hexdigest()
        return f"0x{account_hash[:40]}"
    
    def create_user_operation(
        self,
        sender: str,
        target: str,
        value: int,
        data: bytes = b'',
        gas_limit: int = 100000
    ) -> Dict[str, Any]:
        """
        Cria UserOperation para ERC-4337
        
        Args:
            sender: Smart Account address
            target: Target contract/address
            value: Value to send
            data: Calldata
            gas_limit: Gas limit
        
        Returns:
            UserOperation dict
        """
        user_op = {
            "sender": sender,
            "nonce": 0,  # Em produção: pegar do contract
            "initCode": "0x",  # Se account não existe ainda
            "callData": self._encode_call(target, value, data),
            "callGasLimit": gas_limit,
            "verificationGasLimit": 100000,
            "preVerificationGas": 21000,
            "maxFeePerGas": self.w3.eth.gas_price,
            "maxPriorityFeePerGas": self.w3.to_wei(2, 'gwei'),
            "paymasterAndData": "0x",  # Sem paymaster
            "signature": "0x"  # Será assinado depois
        }
        
        return user_op
    
    def _encode_call(self, target: str, value: int, data: bytes) -> str:
        """
        Encoda chamada para execute()
        
        Args:
            target: Target address
            value: Value to send
            data: Calldata
        
        Returns:
            Encoded calldata
        """
        # Simulação - em produção usar web3.py para encodar
        # execute(address target, uint256 value, bytes data)
        return f"0x{'0'*8}{target[2:]}{hex(value)[2:].zfill(64)}"
    
    def send_user_operation(
        self,
        user_op: Dict[str, Any],
        private_key: str
    ) -> Dict[str, Any]:
        """
        Envia UserOperation via EntryPoint
        
        Args:
            user_op: UserOperation
            private_key: Private key para assinar
        
        Returns:
            Transaction receipt
        """
        # Em produção:
        # 1. Assinar user_op
        # 2. Enviar para bundler ou diretamente ao EntryPoint
        # 3. Aguardar confirmação
        
        # Simulação
        import hashlib
        import time
        
        op_hash = hashlib.sha256(json.dumps(user_op).encode()).hexdigest()
        
        logger.info(f"UserOp sent: {op_hash[:16]}...")
        
        return {
            "user_op_hash": f"0x{op_hash}",
            "tx_hash": f"0x{hashlib.sha256(f'{op_hash}{time.time()}'.encode()).hexdigest()}",
            "status": "success",
            "gas_used": user_op["callGasLimit"]
        }
    
    def is_deployed(self, account_address: str) -> bool:
        """
        Verifica se Smart Account foi deployed
        
        Args:
            account_address: Account address
        
        Returns:
            True se deployed
        """
        return self.connector.is_contract(account_address)
