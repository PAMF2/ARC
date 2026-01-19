"""
Treasury Agent - Extended Functions
Complete treasury operations + Crypto trading + DeFi yield farming
"""

import os
import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum

# Import existing base
try:
    from .treasury_agent import TreasuryAgent
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from treasury_agent import TreasuryAgent


class AssetType(Enum):
    USDC = "usdc"
    BTC = "btc"
    ETH = "eth"
    MATIC = "matic"
    SOL = "sol"
    AVAX = "avax"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TreasuryAgentExtended(TreasuryAgent):
    """Extended Treasury with DeFi yield farming + crypto trading"""

    def __init__(self, config):
        super().__init__(config)
        self.crypto_portfolios = {}
        self.trading_orders = {}
        self.staking_positions = {}
        self.liquidity_pools = {}
        self.price_cache = {}

    # ============================================================================
    # CRYPTO TRADING (Corretora)
    # ============================================================================

    def buy_crypto(
        self,
        agent_id: str,
        crypto_asset: str,
        amount_usdc: Decimal,
        order_type: str = "market",
        limit_price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Buy cryptocurrency

        Args:
            agent_id: Agent buying
            crypto_asset: BTC, ETH, SOL, etc.
            amount_usdc: USDC amount to spend
            order_type: "market" or "limit"
            limit_price: Price limit for limit orders

        Returns:
            Order details
        """
        # Get current price
        current_price = self._get_crypto_price(crypto_asset)

        if order_type == "market":
            # Execute immediately at market price
            crypto_amount = amount_usdc / current_price

            # Calculate fees (0.1% trading fee)
            fee = amount_usdc * Decimal("0.001")
            total_cost = amount_usdc + fee

            # Check balance
            account = self._get_account(agent_id)
            if account["balance"] < total_cost:
                raise ValueError(f"Insufficient USDC balance. Need ${total_cost}, have ${account['balance']}")

            # Deduct USDC
            account["balance"] -= total_cost

            # Add crypto to portfolio
            portfolio = self.crypto_portfolios.get(agent_id, {})
            if crypto_asset not in portfolio:
                portfolio[crypto_asset] = Decimal("0")

            portfolio[crypto_asset] += crypto_amount
            self.crypto_portfolios[agent_id] = portfolio

            order = {
                "order_id": f"BUY-{crypto_asset}-{datetime.now().timestamp()}",
                "agent_id": agent_id,
                "type": "buy",
                "crypto_asset": crypto_asset,
                "order_type": OrderType.MARKET.value,
                "amount_usdc": str(amount_usdc),
                "crypto_amount": str(crypto_amount),
                "price": str(current_price),
                "fee": str(fee),
                "total_cost": str(total_cost),
                "status": OrderStatus.FILLED.value,
                "executed_at": datetime.now().isoformat()
            }

            self.trading_orders[order["order_id"]] = order

            # Log transaction
            self._log_transaction(
                agent_id,
                "crypto_buy",
                f"Bought {crypto_amount} {crypto_asset} at ${current_price}"
            )

            return order

        elif order_type == "limit":
            # Create limit order
            if not limit_price:
                raise ValueError("Limit price required for limit orders")

            order = {
                "order_id": f"BUY-LIMIT-{crypto_asset}-{datetime.now().timestamp()}",
                "agent_id": agent_id,
                "type": "buy",
                "crypto_asset": crypto_asset,
                "order_type": OrderType.LIMIT.value,
                "amount_usdc": str(amount_usdc),
                "limit_price": str(limit_price),
                "status": OrderStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
            }

            self.trading_orders[order["order_id"]] = order

            # Schedule price monitoring
            self._monitor_limit_order(order["order_id"])

            return order

    def sell_crypto(
        self,
        agent_id: str,
        crypto_asset: str,
        crypto_amount: Decimal,
        order_type: str = "market",
        limit_price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Sell cryptocurrency

        Args:
            agent_id: Agent selling
            crypto_asset: BTC, ETH, SOL, etc.
            crypto_amount: Amount of crypto to sell
            order_type: "market" or "limit"
            limit_price: Price limit for limit orders

        Returns:
            Order details
        """
        # Check crypto balance
        portfolio = self.crypto_portfolios.get(agent_id, {})
        if crypto_asset not in portfolio or portfolio[crypto_asset] < crypto_amount:
            raise ValueError(f"Insufficient {crypto_asset} balance")

        # Get current price
        current_price = self._get_crypto_price(crypto_asset)

        if order_type == "market":
            # Execute immediately
            usdc_proceeds = crypto_amount * current_price

            # Calculate fees (0.1%)
            fee = usdc_proceeds * Decimal("0.001")
            net_proceeds = usdc_proceeds - fee

            # Deduct crypto
            portfolio[crypto_asset] -= crypto_amount
            self.crypto_portfolios[agent_id] = portfolio

            # Add USDC to account
            account = self._get_account(agent_id)
            account["balance"] += net_proceeds

            order = {
                "order_id": f"SELL-{crypto_asset}-{datetime.now().timestamp()}",
                "agent_id": agent_id,
                "type": "sell",
                "crypto_asset": crypto_asset,
                "order_type": OrderStatus.MARKET.value,
                "crypto_amount": str(crypto_amount),
                "price": str(current_price),
                "usdc_proceeds": str(usdc_proceeds),
                "fee": str(fee),
                "net_proceeds": str(net_proceeds),
                "status": OrderStatus.FILLED.value,
                "executed_at": datetime.now().isoformat()
            }

            self.trading_orders[order["order_id"]] = order

            return order

        elif order_type == "limit":
            # Create limit order
            if not limit_price:
                raise ValueError("Limit price required")

            order = {
                "order_id": f"SELL-LIMIT-{crypto_asset}-{datetime.now().timestamp()}",
                "agent_id": agent_id,
                "type": "sell",
                "crypto_asset": crypto_asset,
                "order_type": OrderType.LIMIT.value,
                "crypto_amount": str(crypto_amount),
                "limit_price": str(limit_price),
                "status": OrderStatus.PENDING.value,
                "created_at": datetime.now().isoformat()
            }

            self.trading_orders[order["order_id"]] = order

            return order

    def swap_crypto(
        self,
        agent_id: str,
        from_asset: str,
        to_asset: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Swap one cryptocurrency for another (DEX-style)

        Args:
            agent_id: Agent swapping
            from_asset: Source crypto (e.g., ETH)
            to_asset: Destination crypto (e.g., BTC)
            amount: Amount of source crypto

        Returns:
            Swap details
        """
        # Check balance
        portfolio = self.crypto_portfolios.get(agent_id, {})
        if from_asset not in portfolio or portfolio[from_asset] < amount:
            raise ValueError(f"Insufficient {from_asset} balance")

        # Get prices
        from_price = self._get_crypto_price(from_asset)
        to_price = self._get_crypto_price(to_asset)

        # Calculate swap
        usdc_value = amount * from_price
        to_amount = usdc_value / to_price

        # Swap fee (0.3% like Uniswap)
        swap_fee_percent = Decimal("0.003")
        to_amount_after_fee = to_amount * (Decimal("1") - swap_fee_percent)

        # Execute swap
        portfolio[from_asset] -= amount
        if to_asset not in portfolio:
            portfolio[to_asset] = Decimal("0")
        portfolio[to_asset] += to_amount_after_fee

        self.crypto_portfolios[agent_id] = portfolio

        swap = {
            "swap_id": f"SWAP-{datetime.now().timestamp()}",
            "agent_id": agent_id,
            "from_asset": from_asset,
            "to_asset": to_asset,
            "from_amount": str(amount),
            "to_amount": str(to_amount_after_fee),
            "exchange_rate": str(from_price / to_price),
            "fee_percent": str(swap_fee_percent * 100),
            "executed_at": datetime.now().isoformat()
        }

        self._log_transaction(
            agent_id,
            "crypto_swap",
            f"Swapped {amount} {from_asset} for {to_amount_after_fee} {to_asset}"
        )

        return swap

    def stake_crypto(
        self,
        agent_id: str,
        crypto_asset: str,
        amount: Decimal,
        duration_days: int
    ) -> Dict[str, Any]:
        """
        Stake cryptocurrency for rewards

        Args:
            agent_id: Agent staking
            crypto_asset: Crypto to stake (ETH, SOL, MATIC, etc.)
            amount: Amount to stake
            duration_days: Lock period (30, 60, 90, 180, 365)

        Returns:
            Staking position details
        """
        # Validate stakeable assets
        stakeable_assets = {
            "eth": {"min_duration": 30, "apr": Decimal("0.05")},  # 5% APR
            "sol": {"min_duration": 7, "apr": Decimal("0.07")},   # 7% APR
            "matic": {"min_duration": 7, "apr": Decimal("0.06")},  # 6% APR
            "avax": {"min_duration": 14, "apr": Decimal("0.08")}  # 8% APR
        }

        if crypto_asset.lower() not in stakeable_assets:
            raise ValueError(f"{crypto_asset} is not stakeable")

        # Check balance
        portfolio = self.crypto_portfolios.get(agent_id, {})
        if crypto_asset not in portfolio or portfolio[crypto_asset] < amount:
            raise ValueError(f"Insufficient {crypto_asset} balance")

        # Check minimum duration
        min_duration = stakeable_assets[crypto_asset.lower()]["min_duration"]
        if duration_days < min_duration:
            raise ValueError(f"Minimum staking duration is {min_duration} days")

        # Calculate rewards
        apr = stakeable_assets[crypto_asset.lower()]["apr"]
        rewards = amount * apr * (Decimal(duration_days) / Decimal("365"))

        # Lock crypto
        portfolio[crypto_asset] -= amount

        # Create staking position
        position_id = f"STAKE-{crypto_asset}-{datetime.now().timestamp()}"
        unlock_date = datetime.now() + timedelta(days=duration_days)

        position = {
            "position_id": position_id,
            "agent_id": agent_id,
            "crypto_asset": crypto_asset,
            "amount_staked": str(amount),
            "apr": str(apr * 100),  # Convert to percentage
            "duration_days": duration_days,
            "estimated_rewards": str(rewards),
            "staked_at": datetime.now().isoformat(),
            "unlock_at": unlock_date.isoformat(),
            "status": "active"
        }

        self.staking_positions[position_id] = position

        return position

    def unstake_crypto(
        self,
        agent_id: str,
        position_id: str,
        early_withdrawal: bool = False
    ) -> Dict[str, Any]:
        """
        Unstake cryptocurrency

        Args:
            agent_id: Agent unstaking
            position_id: Staking position ID
            early_withdrawal: If true, unstake before unlock (penalty applies)

        Returns:
            Unstaking details
        """
        position = self.staking_positions.get(position_id)
        if not position:
            raise ValueError("Staking position not found")

        if position["agent_id"] != agent_id:
            raise ValueError("Not your staking position")

        unlock_date = datetime.fromisoformat(position["unlock_at"])
        is_locked = datetime.now() < unlock_date

        if is_locked and not early_withdrawal:
            raise ValueError(f"Position locked until {unlock_date.strftime('%Y-%m-%d')}")

        amount_staked = Decimal(position["amount_staked"])
        estimated_rewards = Decimal(position["estimated_rewards"])

        if early_withdrawal:
            # Apply penalty (10% of rewards)
            penalty = estimated_rewards * Decimal("0.10")
            actual_rewards = estimated_rewards - penalty
        else:
            actual_rewards = estimated_rewards
            penalty = Decimal("0")

        total_return = amount_staked + actual_rewards

        # Return crypto to portfolio
        portfolio = self.crypto_portfolios.get(agent_id, {})
        crypto_asset = position["crypto_asset"]

        if crypto_asset not in portfolio:
            portfolio[crypto_asset] = Decimal("0")

        portfolio[crypto_asset] += total_return
        self.crypto_portfolios[agent_id] = portfolio

        # Update position status
        position["status"] = "unstaked"
        position["unstaked_at"] = datetime.now().isoformat()
        position["actual_rewards"] = str(actual_rewards)
        position["penalty"] = str(penalty)

        return {
            "position_id": position_id,
            "amount_staked": str(amount_staked),
            "rewards_earned": str(actual_rewards),
            "penalty": str(penalty),
            "total_returned": str(total_return),
            "crypto_asset": crypto_asset
        }

    # ============================================================================
    # YIELD FARMING (DeFi)
    # ============================================================================

    def multi_protocol_yield_farming(
        self,
        allocation: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """
        Distribute treasury funds across multiple DeFi protocols

        Args:
            allocation: {
                "aave": Decimal("0.40"),     # 40%
                "compound": Decimal("0.30"),  # 30%
                "yearn": Decimal("0.20"),    # 20%
                "curve": Decimal("0.10")     # 10%
            }

        Returns:
            Allocation summary
        """
        # Validate allocation sums to 1.0
        total = sum(allocation.values())
        if abs(total - Decimal("1.0")) > Decimal("0.01"):
            raise ValueError("Allocation must sum to 100%")

        # Get total treasury balance
        treasury_balance = self._get_treasury_balance()

        # Distribute across protocols
        distributions = {}

        for protocol, percent in allocation.items():
            amount = treasury_balance * percent

            # Deposit to protocol
            result = self._deposit_to_protocol(protocol, amount)

            distributions[protocol] = {
                "amount": str(amount),
                "percent": str(percent * 100),
                "current_apy": result["apy"],
                "shares_received": result.get("shares", "N/A")
            }

        return {
            "total_allocated": str(treasury_balance),
            "distributions": distributions,
            "allocated_at": datetime.now().isoformat(),
            "rebalance_due": (datetime.now() + timedelta(days=7)).isoformat()
        }

    def auto_compound_interest(
        self,
        frequency: str = "daily"
    ) -> Dict[str, Any]:
        """
        Automatically reinvest earned interest

        Args:
            frequency: "daily", "weekly", "monthly"

        Returns:
            Compounding schedule
        """
        # Get current yield balance from all protocols
        aave_balance = self._get_aave_balance()
        compound_balance = self._get_compound_balance()
        yearn_balance = self._get_yearn_balance()

        total_interest = (
            aave_balance["interest_earned"] +
            compound_balance.get("interest_earned", Decimal("0")) +
            yearn_balance.get("interest_earned", Decimal("0"))
        )

        if total_interest > Decimal("10"):  # Min $10 to compound
            # Withdraw interest
            self._withdraw_interest_from_protocols()

            # Reinvest
            self._reinvest_to_highest_yield(total_interest)

            return {
                "action": "compounded",
                "interest_amount": str(total_interest),
                "compounded_at": datetime.now().isoformat(),
                "next_compound": self._get_next_compound_date(frequency)
            }
        else:
            return {
                "action": "skipped",
                "reason": "Insufficient interest to compound",
                "current_interest": str(total_interest),
                "minimum_required": "10.00"
            }

    def forecast_liquidity(
        self,
        horizon_days: int
    ) -> Dict[str, Any]:
        """
        Forecast cash needs for next N days

        Analyzes:
        - Historical transaction patterns
        - Pending transactions
        - Scheduled payments
        - Seasonal trends

        Returns:
            Daily liquidity projection
        """
        # Get historical data
        historical_txs = self._get_historical_transactions(days=90)

        # Calculate daily averages
        daily_inflows = self._calculate_daily_average(historical_txs, "credit")
        daily_outflows = self._calculate_daily_average(historical_txs, "debit")

        # Get pending transactions
        pending = self._get_pending_transactions()
        pending_outflows = sum(tx["amount"] for tx in pending)

        # Forecast each day
        forecast = []
        current_balance = self._get_treasury_balance()

        for day in range(horizon_days):
            date = datetime.now() + timedelta(days=day)

            # Project balance
            projected_balance = current_balance + daily_inflows - daily_outflows

            # Add pending if due on this day
            if day == 0:
                projected_balance -= pending_outflows

            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "projected_balance": str(projected_balance),
                "projected_inflows": str(daily_inflows),
                "projected_outflows": str(daily_outflows),
                "below_minimum": projected_balance < Decimal("10000"),  # $10K reserve
                "recommended_action": "withdraw_from_yield" if projected_balance < Decimal("10000") else "maintain"
            })

            current_balance = projected_balance

        return {
            "horizon_days": horizon_days,
            "current_balance": str(self._get_treasury_balance()),
            "daily_forecast": forecast,
            "recommendations": self._generate_liquidity_recommendations(forecast)
        }

    # ============================================================================
    # PORTFOLIO MANAGEMENT
    # ============================================================================

    def create_investment_portfolio(
        self,
        name: str,
        strategy: str,
        allocation: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """
        Create diversified investment portfolio

        Args:
            name: Portfolio name
            strategy: "conservative", "balanced", "aggressive"
            allocation: Asset allocation (must sum to 1.0)

        Returns:
            Portfolio details
        """
        # Validate strategy
        if strategy not in ["conservative", "balanced", "aggressive"]:
            raise ValueError("Invalid strategy")

        # Validate allocation
        if abs(sum(allocation.values()) - Decimal("1.0")) > Decimal("0.01"):
            raise ValueError("Allocation must sum to 100%")

        portfolio_id = f"PORT-{datetime.now().timestamp()}"

        portfolio = {
            "portfolio_id": portfolio_id,
            "name": name,
            "strategy": strategy,
            "allocation": {k: str(v) for k, v in allocation.items()},
            "created_at": datetime.now().isoformat(),
            "last_rebalanced": datetime.now().isoformat(),
            "performance": {
                "total_return": "0.00",
                "ytd_return": "0.00",
                "sharpe_ratio": "0.00"
            }
        }

        return portfolio

    def rebalance_portfolio(
        self,
        portfolio_id: str,
        threshold: Decimal = Decimal("0.05")
    ) -> Dict[str, Any]:
        """
        Rebalance portfolio to target allocation

        Args:
            portfolio_id: Portfolio to rebalance
            threshold: Rebalance if drift > 5%

        Returns:
            Rebalancing actions
        """
        portfolio = self._get_portfolio(portfolio_id)

        # Calculate current allocation
        current_values = self._get_portfolio_current_values(portfolio_id)
        total_value = sum(current_values.values())

        current_allocation = {
            asset: value / total_value
            for asset, value in current_values.items()
        }

        # Calculate drift from target
        target_allocation = {
            k: Decimal(v)
            for k, v in portfolio["allocation"].items()
        }

        drifts = {
            asset: current_allocation.get(asset, Decimal("0")) - target
            for asset, target in target_allocation.items()
        }

        # Check if rebalancing needed
        max_drift = max(abs(drift) for drift in drifts.values())

        if max_drift < threshold:
            return {
                "action": "no_rebalancing_needed",
                "max_drift": str(max_drift * 100),
                "threshold": str(threshold * 100)
            }

        # Execute rebalancing trades
        trades = []

        for asset, drift in drifts.items():
            if abs(drift) > threshold:
                # Calculate trade amount
                trade_value = total_value * drift

                if drift > 0:
                    # Overweight - sell
                    trades.append({
                        "action": "sell",
                        "asset": asset,
                        "amount": str(abs(trade_value))
                    })
                else:
                    # Underweight - buy
                    trades.append({
                        "action": "buy",
                        "asset": asset,
                        "amount": str(abs(trade_value))
                    })

        # Execute trades
        for trade in trades:
            if trade["action"] == "sell":
                # Sell logic
                pass
            else:
                # Buy logic
                pass

        portfolio["last_rebalanced"] = datetime.now().isoformat()

        return {
            "portfolio_id": portfolio_id,
            "trades_executed": len(trades),
            "trades": trades,
            "rebalanced_at": datetime.now().isoformat()
        }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _get_crypto_price(self, crypto_asset: str) -> Decimal:
        """Get current crypto price in USDC (mock - use real API in production)"""
        # Mock prices - in production use CoinGecko, Binance API, etc.
        prices = {
            "btc": Decimal("45000.00"),
            "eth": Decimal("2500.00"),
            "sol": Decimal("100.00"),
            "matic": Decimal("0.80"),
            "avax": Decimal("35.00")
        }
        return prices.get(crypto_asset.lower(), Decimal("1.00"))

    def _log_transaction(self, agent_id: str, tx_type: str, description: str):
        """Log transaction"""
        print(f"[TRANSACTION] {agent_id}: {tx_type} - {description}")

    def _get_account(self, agent_id: str) -> dict:
        """Get agent account (mock)"""
        return {"balance": Decimal("100000.00")}

    def _deposit_to_protocol(self, protocol: str, amount: Decimal) -> dict:
        """Deposit to DeFi protocol (mock)"""
        apys = {
            "aave": "4.5",
            "compound": "3.8",
            "yearn": "6.2",
            "curve": "5.1"
        }
        return {
            "apy": apys.get(protocol, "4.0"),
            "shares": str(amount)
        }


# Export
def create_extended_treasury_agent(config):
    """Factory function"""
    return TreasuryAgentExtended(config)
