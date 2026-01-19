"""
Circle Programmable Wallets Integration
Provides USDC wallet creation and management for AI agents
Uses Circle's Web3 Services API
"""
from typing import Dict, Any, Optional, List
import os
import logging
import uuid
import hashlib
import hmac
from datetime import datetime
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CircleWallet:
    """Represents a Circle Programmable Wallet"""
    wallet_id: str
    address: str
    blockchain: str
    account_type: str
    state: str
    create_date: datetime
    update_date: datetime
    custody_type: str = "DEVELOPER"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "wallet_id": self.wallet_id,
            "address": self.address,
            "blockchain": self.blockchain,
            "account_type": self.account_type,
            "state": self.state,
            "create_date": self.create_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "custody_type": self.custody_type
        }

@dataclass
class CircleTransaction:
    """Represents a Circle USDC transaction"""
    tx_id: str
    wallet_id: str
    token_id: str
    destination: str
    amount: str
    state: str
    create_date: datetime
    blockchain: str
    tx_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tx_id": self.tx_id,
            "wallet_id": self.wallet_id,
            "token_id": self.token_id,
            "destination": self.destination,
            "amount": self.amount,
            "state": self.state,
            "create_date": self.create_date.isoformat(),
            "blockchain": self.blockchain,
            "tx_hash": self.tx_hash
        }

class CircleWalletsAPI:
    """
    Circle Programmable Wallets API Integration
    Supports USDC transactions and wallet management for AI agents
    """

    # API Endpoints
    BASE_URL = "https://api.circle.com/v1"
    SANDBOX_URL = "https://api-sandbox.circle.com/v1"

    # Supported Blockchains
    BLOCKCHAINS = {
        "ETH": "ETH",
        "MATIC": "MATIC-AMOY",  # Polygon Amoy testnet
        "AVAX": "AVAX-FUJI",
        "SOL": "SOL-DEVNET",
        "ARC": "ARC-SEPOLIA",  # Arc Sepolia testnet
        "ARC-MAINNET": "ARC"  # Arc Mainnet
    }

    # USDC Token IDs
    USDC_TOKENS = {
        "ETH": "36b1737e-7d26-5345-86d7-8b99c6e8a2a5",  # USDC on Ethereum
        "MATIC": "f2a2c41a-1e2e-59fc-a0c0-a4b4a6ba2e5f",  # USDC on Polygon
        "AVAX": "c6d3b5f0-2a1a-5f3e-9d4a-1b2c3d4e5f6a",  # USDC on Avalanche
        "ARC": "arc-usdc-sepolia-token-id",  # USDC on Arc Sepolia (update with actual)
        "ARC-MAINNET": "arc-usdc-mainnet-token-id"  # USDC on Arc Mainnet (update with actual)
    }

    # Arc-specific configuration
    ARC_CONFIG = {
        "sepolia": {
            "chain_id": 93027492,
            "rpc_url": "https://sepolia.rpc.arcscan.xyz",
            "explorer": "https://sepolia.arcscan.xyz",
            "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
        },
        "mainnet": {
            "chain_id": 1234567890,  # Update with actual
            "rpc_url": "https://rpc.arcscan.xyz",
            "explorer": "https://arcscan.xyz",
            "usdc_address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"  # Update with actual
        }
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        entity_secret: Optional[str] = None,
        environment: str = "sandbox"
    ):
        """
        Initialize Circle Wallets API client

        Args:
            api_key: Circle API key
            entity_secret: Circle entity secret for encryption
            environment: "sandbox" or "production"
        """
        self.api_key = api_key or os.getenv("CIRCLE_API_KEY")
        self.entity_secret = entity_secret or os.getenv("CIRCLE_ENTITY_SECRET")
        self.environment = environment

        if not self.api_key:
            raise ValueError("Circle API key is required. Set CIRCLE_API_KEY environment variable.")

        if not self.entity_secret:
            logger.warning("Circle entity secret not set. Some features may be limited.")

        self.base_url = self.SANDBOX_URL if environment == "sandbox" else self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

        logger.info(f"Circle Wallets API initialized ({environment} environment)")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Circle API

        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: API endpoint
            data: Request body
            params: Query parameters

        Returns:
            API response as dict
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Circle API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    def is_arc_blockchain(self, blockchain: str) -> bool:
        """
        Check if blockchain is Arc

        Args:
            blockchain: Blockchain identifier

        Returns:
            True if Arc blockchain
        """
        return blockchain in ["ARC", "ARC-MAINNET"]

    def get_arc_config(self, is_mainnet: bool = False) -> Dict[str, Any]:
        """
        Get Arc blockchain configuration

        Args:
            is_mainnet: True for mainnet, False for sepolia

        Returns:
            Arc configuration dict
        """
        return self.ARC_CONFIG["mainnet"] if is_mainnet else self.ARC_CONFIG["sepolia"]

    def create_wallet(
        self,
        agent_id: str,
        blockchain: str = "ARC",  # Default to Arc
        wallet_set_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CircleWallet:
        """
        Create a new programmable wallet for an AI agent

        Args:
            agent_id: Unique identifier for the AI agent
            blockchain: Target blockchain (ETH, MATIC, AVAX, SOL)
            wallet_set_id: Optional wallet set ID for grouping
            metadata: Additional metadata to store

        Returns:
            CircleWallet object with wallet details
        """
        logger.info(f"Creating Circle wallet for agent {agent_id} on {blockchain}")

        blockchain_code = self.BLOCKCHAINS.get(blockchain, "MATIC-AMOY")

        # Generate idempotency key
        idempotency_key = str(uuid.uuid4())

        payload = {
            "idempotencyKey": idempotency_key,
            "accountType": "SCA",  # Smart Contract Account
            "blockchains": [blockchain_code],
            "metadata": [
                {
                    "name": "agent_id",
                    "value": agent_id
                },
                {
                    "name": "created_at",
                    "value": datetime.now().isoformat()
                }
            ]
        }

        # Add wallet set if provided
        if wallet_set_id:
            payload["walletSetId"] = wallet_set_id

        # Add custom metadata
        if metadata:
            for key, value in metadata.items():
                payload["metadata"].append({
                    "name": key,
                    "value": str(value)
                })

        try:
            response = self._make_request("POST", "/w3s/wallets", data=payload)

            wallet_data = response["data"]["wallets"][0]

            wallet = CircleWallet(
                wallet_id=wallet_data["id"],
                address=wallet_data["address"],
                blockchain=wallet_data["blockchain"],
                account_type=wallet_data["accountType"],
                state=wallet_data["state"],
                create_date=datetime.fromisoformat(wallet_data["createDate"].replace("Z", "+00:00")),
                update_date=datetime.fromisoformat(wallet_data["updateDate"].replace("Z", "+00:00")),
                custody_type=wallet_data.get("custodyType", "DEVELOPER")
            )

            logger.info(f"[SUCCESS] Created wallet {wallet.wallet_id} at address {wallet.address}")

            return wallet

        except Exception as e:
            logger.error(f"Failed to create wallet for agent {agent_id}: {e}")
            raise

    def get_wallet(self, wallet_id: str) -> CircleWallet:
        """
        Retrieve wallet details

        Args:
            wallet_id: Circle wallet ID

        Returns:
            CircleWallet object
        """
        response = self._make_request("GET", f"/w3s/wallets/{wallet_id}")
        wallet_data = response["data"]["wallet"]

        return CircleWallet(
            wallet_id=wallet_data["id"],
            address=wallet_data["address"],
            blockchain=wallet_data["blockchain"],
            account_type=wallet_data["accountType"],
            state=wallet_data["state"],
            create_date=datetime.fromisoformat(wallet_data["createDate"].replace("Z", "+00:00")),
            update_date=datetime.fromisoformat(wallet_data["updateDate"].replace("Z", "+00:00")),
            custody_type=wallet_data.get("custodyType", "DEVELOPER")
        )

    def get_wallet_balance(
        self,
        wallet_id: str,
        token_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get wallet token balances

        Args:
            wallet_id: Circle wallet ID
            token_id: Optional specific token ID

        Returns:
            Balance information
        """
        endpoint = f"/w3s/wallets/{wallet_id}/balances"

        response = self._make_request("GET", endpoint)

        balances = response["data"]["tokenBalances"]

        # If specific token requested, filter
        if token_id:
            balances = [b for b in balances if b["token"]["id"] == token_id]

        # Format balances
        formatted_balances = []
        for balance in balances:
            formatted_balances.append({
                "token_id": balance["token"]["id"],
                "token_symbol": balance["token"]["symbol"],
                "amount": balance["amount"],
                "update_date": balance["updateDate"]
            })

        return {
            "wallet_id": wallet_id,
            "balances": formatted_balances,
            "total_tokens": len(formatted_balances)
        }

    def transfer_usdc(
        self,
        from_wallet_id: str,
        to_address: str,
        amount: str,
        blockchain: str = "MATIC",
        fee_level: str = "MEDIUM"
    ) -> CircleTransaction:
        """
        Transfer USDC from wallet to another address

        Args:
            from_wallet_id: Source wallet ID
            to_address: Destination address (0x...)
            amount: Amount in USDC (string for precision)
            blockchain: Target blockchain
            fee_level: Transaction fee level (LOW, MEDIUM, HIGH)

        Returns:
            CircleTransaction object
        """
        logger.info(f"Transferring {amount} USDC from {from_wallet_id} to {to_address}")

        # Get token ID for blockchain
        token_id = self.USDC_TOKENS.get(blockchain)
        if not token_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}")

        # Generate idempotency key
        idempotency_key = str(uuid.uuid4())

        payload = {
            "idempotencyKey": idempotency_key,
            "amounts": [amount],
            "destinationAddress": to_address,
            "tokenId": token_id,
            "walletId": from_wallet_id,
            "fee": {
                "type": "level",
                "config": {
                    "feeLevel": fee_level
                }
            }
        }

        try:
            response = self._make_request("POST", "/w3s/developer/transactions/transfer", data=payload)

            tx_data = response["data"]

            transaction = CircleTransaction(
                tx_id=tx_data["id"],
                wallet_id=from_wallet_id,
                token_id=token_id,
                destination=to_address,
                amount=amount,
                state=tx_data["state"],
                create_date=datetime.fromisoformat(tx_data["createDate"].replace("Z", "+00:00")),
                blockchain=blockchain,
                tx_hash=tx_data.get("txHash")
            )

            logger.info(f"[SUCCESS] Transfer initiated: {transaction.tx_id}")

            return transaction

        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            raise

    def get_transaction(self, tx_id: str) -> CircleTransaction:
        """
        Get transaction details

        Args:
            tx_id: Circle transaction ID

        Returns:
            CircleTransaction object
        """
        response = self._make_request("GET", f"/w3s/transactions/{tx_id}")
        tx_data = response["data"]["transaction"]

        return CircleTransaction(
            tx_id=tx_data["id"],
            wallet_id=tx_data["walletId"],
            token_id=tx_data["tokenId"],
            destination=tx_data["destinationAddress"],
            amount=tx_data["amounts"][0],
            state=tx_data["state"],
            create_date=datetime.fromisoformat(tx_data["createDate"].replace("Z", "+00:00")),
            blockchain=tx_data["blockchain"],
            tx_hash=tx_data.get("txHash")
        )

    def list_wallets(
        self,
        wallet_set_id: Optional[str] = None,
        blockchain: Optional[str] = None,
        page_size: int = 10
    ) -> List[CircleWallet]:
        """
        List all wallets

        Args:
            wallet_set_id: Filter by wallet set
            blockchain: Filter by blockchain
            page_size: Number of results per page

        Returns:
            List of CircleWallet objects
        """
        params = {
            "pageSize": page_size
        }

        if wallet_set_id:
            params["walletSetId"] = wallet_set_id
        if blockchain:
            params["blockchain"] = self.BLOCKCHAINS.get(blockchain, blockchain)

        response = self._make_request("GET", "/w3s/wallets", params=params)

        wallets = []
        for wallet_data in response["data"]["wallets"]:
            wallets.append(CircleWallet(
                wallet_id=wallet_data["id"],
                address=wallet_data["address"],
                blockchain=wallet_data["blockchain"],
                account_type=wallet_data["accountType"],
                state=wallet_data["state"],
                create_date=datetime.fromisoformat(wallet_data["createDate"].replace("Z", "+00:00")),
                update_date=datetime.fromisoformat(wallet_data["updateDate"].replace("Z", "+00:00")),
                custody_type=wallet_data.get("custodyType", "DEVELOPER")
            ))

        return wallets

    def get_wallet_by_agent_id(self, agent_id: str) -> Optional[CircleWallet]:
        """
        Find wallet associated with an agent ID

        Args:
            agent_id: Agent identifier

        Returns:
            CircleWallet if found, None otherwise
        """
        # List all wallets and filter by metadata
        wallets = self.list_wallets(page_size=50)

        # Note: This is a simplified implementation
        # In production, you'd use a database to map agent_id -> wallet_id
        for wallet in wallets:
            # Would need to fetch wallet details with metadata
            # For now, return first wallet as placeholder
            pass

        return None

    def get_transaction_history(
        self,
        wallet_id: str,
        page_size: int = 20
    ) -> List[CircleTransaction]:
        """
        Get transaction history for a wallet

        Args:
            wallet_id: Circle wallet ID
            page_size: Number of results

        Returns:
            List of CircleTransaction objects
        """
        params = {
            "walletIds": wallet_id,
            "pageSize": page_size
        }

        response = self._make_request("GET", "/w3s/transactions", params=params)

        transactions = []
        for tx_data in response["data"]["transactions"]:
            transactions.append(CircleTransaction(
                tx_id=tx_data["id"],
                wallet_id=tx_data["walletId"],
                token_id=tx_data["tokenId"],
                destination=tx_data.get("destinationAddress", ""),
                amount=tx_data["amounts"][0] if tx_data.get("amounts") else "0",
                state=tx_data["state"],
                create_date=datetime.fromisoformat(tx_data["createDate"].replace("Z", "+00:00")),
                blockchain=tx_data["blockchain"],
                tx_hash=tx_data.get("txHash")
            ))

        return transactions

    def check_health(self) -> bool:
        """
        Check API connectivity

        Returns:
            True if API is accessible
        """
        try:
            response = self._make_request("GET", "/w3s/config/entity")
            return response.get("data") is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Convenience functions for common operations

def create_agent_wallet(
    agent_id: str,
    blockchain: str = "ARC",  # Default to Arc
    api_key: Optional[str] = None,
    environment: str = "sandbox"
) -> Dict[str, Any]:
    """
    Quick function to create a wallet for an agent

    Args:
        agent_id: Agent identifier
        blockchain: Target blockchain (ARC, MATIC, ETH, etc)
        api_key: Circle API key
        environment: sandbox or production

    Returns:
        Dict with wallet details
    """
    client = CircleWalletsAPI(api_key=api_key, environment=environment)
    wallet = client.create_wallet(
        agent_id=agent_id,
        blockchain=blockchain,
        metadata={"agent_type": "banking_agent"}
    )

    return {
        "success": True,
        "wallet_id": wallet.wallet_id,
        "address": wallet.address,
        "blockchain": wallet.blockchain,
        "agent_id": agent_id,
        "gas_token": "USDC" if blockchain.startswith("ARC") else wallet.blockchain
    }

def transfer_between_agents(
    from_agent_id: str,
    to_address: str,
    amount: str,
    blockchain: str = "ARC",  # Default to Arc
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transfer USDC between agents

    Args:
        from_agent_id: Source agent ID
        to_address: Destination wallet address
        amount: Amount in USDC
        blockchain: Target blockchain
        api_key: Circle API key

    Returns:
        Dict with transaction details
    """
    client = CircleWalletsAPI(api_key=api_key)

    # Get wallet for agent
    wallet = client.get_wallet_by_agent_id(from_agent_id)

    if not wallet:
        raise ValueError(f"No wallet found for agent {from_agent_id}")

    # Execute transfer
    transaction = client.transfer_usdc(
        from_wallet_id=wallet.wallet_id,
        to_address=to_address,
        amount=amount,
        blockchain=blockchain
    )

    return {
        "success": True,
        "tx_id": transaction.tx_id,
        "tx_hash": transaction.tx_hash,
        "amount": transaction.amount,
        "state": transaction.state
    }
