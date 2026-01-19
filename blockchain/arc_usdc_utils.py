"""
Arc Blockchain USDC Utilities
Helper functions for Arc's native USDC gas token
"""
from typing import Dict, Any, Optional
from web3 import Web3
import logging

logger = logging.getLogger(__name__)

class ArcUSDCUtils:
    """
    Utilitários para trabalhar com USDC nativo no Arc
    Arc usa USDC como token de gas nativo, não ETH
    """

    USDC_DECIMALS = 6  # USDC usa 6 decimais

    @staticmethod
    def to_usdc_units(amount: float) -> int:
        """
        Converte valor em USDC para unidades base (6 decimais)

        Args:
            amount: Valor em USDC (ex: 10.5)

        Returns:
            Valor em unidades base (ex: 10500000)
        """
        return int(amount * (10 ** ArcUSDCUtils.USDC_DECIMALS))

    @staticmethod
    def from_usdc_units(units: int) -> float:
        """
        Converte unidades base para USDC (6 decimais)

        Args:
            units: Valor em unidades base (ex: 10500000)

        Returns:
            Valor em USDC (ex: 10.5)
        """
        return units / (10 ** ArcUSDCUtils.USDC_DECIMALS)

    @staticmethod
    def format_usdc_amount(amount: float) -> str:
        """
        Formata valor USDC para exibição

        Args:
            amount: Valor em USDC

        Returns:
            String formatada (ex: "10.50 USDC")
        """
        return f"{amount:.2f} USDC"

    @staticmethod
    def format_gas_price(gas_price_units: int) -> str:
        """
        Formata gas price para exibição

        Args:
            gas_price_units: Gas price em unidades base

        Returns:
            String formatada (ex: "0.000001 USDC/gas")
        """
        gas_price = ArcUSDCUtils.from_usdc_units(gas_price_units)
        return f"{gas_price:.6f} USDC/gas"

    @staticmethod
    def estimate_transaction_cost(gas_limit: int, gas_price_units: int) -> Dict[str, Any]:
        """
        Estima custo total de transação em USDC

        Args:
            gas_limit: Limite de gas
            gas_price_units: Preço do gas em unidades base

        Returns:
            Dict com custo estimado
        """
        total_cost_units = gas_limit * gas_price_units
        total_cost_usdc = ArcUSDCUtils.from_usdc_units(total_cost_units)

        return {
            "gas_limit": gas_limit,
            "gas_price_usdc": ArcUSDCUtils.from_usdc_units(gas_price_units),
            "total_cost_usdc": total_cost_usdc,
            "formatted": ArcUSDCUtils.format_usdc_amount(total_cost_usdc)
        }

    @staticmethod
    def validate_usdc_balance(balance: float, amount: float, gas_estimate: float = 0.01) -> Dict[str, Any]:
        """
        Valida se há saldo USDC suficiente para transação + gas

        Args:
            balance: Saldo atual em USDC
            amount: Valor da transação em USDC
            gas_estimate: Estimativa de gas em USDC (default 0.01)

        Returns:
            Dict com resultado da validação
        """
        total_needed = amount + gas_estimate
        has_sufficient = balance >= total_needed

        return {
            "valid": has_sufficient,
            "balance": balance,
            "amount_requested": amount,
            "gas_estimate": gas_estimate,
            "total_needed": total_needed,
            "remaining": balance - total_needed if has_sufficient else 0,
            "message": "Sufficient USDC balance" if has_sufficient else f"Insufficient USDC: need {total_needed:.2f}, have {balance:.2f}"
        }

    @staticmethod
    def get_circle_api_headers(api_key: str) -> Dict[str, str]:
        """
        Retorna headers para Circle API

        Args:
            api_key: Circle API key

        Returns:
            Headers dict
        """
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def build_usdc_transfer_data(to_address: str, amount: float) -> Dict[str, Any]:
        """
        Constrói dados para transferência USDC via Circle

        Args:
            to_address: Endereço de destino
            amount: Valor em USDC

        Returns:
            Dict com dados da transferência
        """
        return {
            "destination": {
                "type": "blockchain",
                "address": to_address,
                "chain": "ARC"
            },
            "amount": {
                "amount": str(amount),
                "currency": "USD"
            }
        }

class ArcNetworkValidator:
    """
    Validador para operações específicas da rede Arc
    """

    @staticmethod
    def validate_arc_address(address: str) -> bool:
        """
        Valida endereço Arc (compatível com EVM)

        Args:
            address: Endereço para validar

        Returns:
            True se válido
        """
        try:
            return Web3.is_address(address)
        except Exception as e:
            logger.error(f"Invalid Arc address {address}: {e}")
            return False

    @staticmethod
    def validate_usdc_amount(amount: float) -> Dict[str, Any]:
        """
        Valida valor USDC

        Args:
            amount: Valor em USDC

        Returns:
            Dict com resultado da validação
        """
        min_amount = 0.01  # Mínimo 1 cent
        max_amount = 1000000.0  # Máximo 1M USDC

        valid = min_amount <= amount <= max_amount

        return {
            "valid": valid,
            "amount": amount,
            "min": min_amount,
            "max": max_amount,
            "message": "Valid USDC amount" if valid else f"Amount must be between {min_amount} and {max_amount}"
        }

    @staticmethod
    def validate_network_params(chain_id: int, rpc_url: str) -> Dict[str, Any]:
        """
        Valida parâmetros da rede Arc

        Args:
            chain_id: Chain ID
            rpc_url: RPC URL

        Returns:
            Dict com resultado da validação
        """
        valid_chain_ids = [93027492, 1234567890]  # Sepolia e Mainnet
        valid_rpc_prefixes = ["https://sepolia.rpc.arcscan.xyz", "https://rpc.arcscan.xyz"]

        chain_id_valid = chain_id in valid_chain_ids
        rpc_valid = any(rpc_url.startswith(prefix) for prefix in valid_rpc_prefixes)

        return {
            "valid": chain_id_valid and rpc_valid,
            "chain_id_valid": chain_id_valid,
            "rpc_valid": rpc_valid,
            "chain_id": chain_id,
            "rpc_url": rpc_url
        }
