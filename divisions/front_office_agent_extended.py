"""
Front Office Agent - Extended Banking Functions
Complete retail banking operations for AI agents
"""

import os
import json
import sys
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

# Import existing base
try:
    from .front_office_agent import FrontOfficeAgent
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from front_office_agent import FrontOfficeAgent


class AccountStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    DORMANT = "dormant"
    CLOSED = "closed"


class CardType(Enum):
    VIRTUAL_DEBIT = "virtual_debit"
    PHYSICAL_DEBIT = "physical_debit"
    VIRTUAL_CREDIT = "virtual_credit"
    PHYSICAL_CREDIT = "physical_credit"


class CardStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    FROZEN = "frozen"
    LOST = "lost"
    STOLEN = "stolen"
    EXPIRED = "expired"


class FrontOfficeAgentExtended(FrontOfficeAgent):
    """Extended Front Office Agent with full retail banking suite"""

    def __init__(self, config):
        super().__init__(config)
        self.accounts_db = {}  # All accounts storage
        self.cards_db = {}  # Card storage
        self.external_accounts_db = {}  # Linked external accounts
        self.sub_accounts_db = {}  # Sub-accounts
        self.notifications_db = {}  # Notification preferences
        self.agents_db = {}  # Agent storage (mock)

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent details (mock implementation for testing)"""
        if agent_id not in self.agents_db:
            self.agents_db[agent_id] = {
                "agent_id": agent_id,
                "kyc_verified": True,
                "status": "active"
            }
        return self.agents_db[agent_id]

    # ============================================================================
    # ACCOUNT MANAGEMENT - Advanced
    # ============================================================================

    def create_joint_account(
        self,
        agent_ids: List[str],
        account_type: str = "checking",
        ownership_percentages: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, Any]:
        """
        Create joint account with multiple owners

        Args:
            agent_ids: List of 2-4 agent IDs
            account_type: checking, savings, business
            ownership_percentages: Optional custom ownership split

        Returns:
            Joint account details
        """
        # Validation
        if len(agent_ids) < 2 or len(agent_ids) > 4:
            raise ValueError("Joint accounts require 2-4 owners")

        # Verify all agents exist and are verified
        for agent_id in agent_ids:
            agent = self.get_agent(agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            if not agent.get("kyc_verified"):
                raise ValueError(f"Agent {agent_id} not KYC verified")

        # Default equal ownership
        if not ownership_percentages:
            split = Decimal("1.0") / len(agent_ids)
            ownership_percentages = {
                agent_id: split for agent_id in agent_ids
            }

        # Create account
        account_id = f"JOINT-{uuid.uuid4().hex[:12].upper()}"

        account = {
            "account_id": account_id,
            "account_type": "joint_" + account_type,
            "owners": agent_ids,
            "ownership_percentages": {
                k: str(v) for k, v in ownership_percentages.items()
            },
            "balance": Decimal("0.00"),
            "status": AccountStatus.ACTIVE.value,
            "requires_all_signatures": True,  # All owners must approve withdrawals
            "created_at": datetime.now().isoformat(),
            "tier": "SILVER"  # Joint accounts start at Silver
        }

        # Store account
        self.accounts_db[account_id] = account

        # Link to each owner
        for agent_id in agent_ids:
            agent = self.agents_db[agent_id]
            if "linked_accounts" not in agent:
                agent["linked_accounts"] = []
            agent["linked_accounts"].append(account_id)

        # Add convenience field for API response
        account["signatures_required"] = "all" if account["requires_all_signatures"] else "any"

        return account

    def create_sub_account(
        self,
        parent_account_id: str,
        name: str,
        purpose: str,
        auto_transfer_rule: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create sub-account for budgeting/categorization

        Args:
            parent_account_id: Main account ID
            name: Sub-account name (e.g., "Emergency Fund", "Vacation")
            purpose: Description
            auto_transfer_rule: Optional auto-transfer config
                Example: {"frequency": "monthly", "amount": 100, "percentage": 0.10}

        Returns:
            Sub-account details
        """
        parent = self.accounts_db.get(parent_account_id)
        if not parent:
            raise ValueError("Parent account not found")

        sub_account_id = f"SUB-{parent_account_id}-{uuid.uuid4().hex[:8].upper()}"

        sub_account = {
            "account_id": sub_account_id,
            "parent_account_id": parent_account_id,
            "name": name,
            "purpose": purpose,
            "balance": Decimal("0.00"),
            "status": AccountStatus.ACTIVE.value,
            "auto_transfer_rule": auto_transfer_rule,
            "created_at": datetime.now().isoformat()
        }

        self.sub_accounts_db[sub_account_id] = sub_account

        # Schedule auto-transfer if configured
        if auto_transfer_rule:
            self._schedule_auto_transfer(sub_account_id, auto_transfer_rule)

        return sub_account

    def freeze_account(
        self,
        account_id: str,
        reason: str,
        duration_days: Optional[int] = None,
        freeze_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Temporarily freeze account

        Args:
            account_id: Account to freeze
            reason: "fraud_prevention", "legal_hold", "customer_request", etc.
            duration_days: Auto-unfreeze after N days (None = manual unfreeze)
            freeze_type: "full" (no transactions) or "withdrawal_only" (deposits ok)

        Returns:
            Freeze confirmation
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        # Update status
        account["status"] = AccountStatus.FROZEN.value
        account["frozen_at"] = datetime.now().isoformat()
        account["freeze_reason"] = reason
        account["freeze_type"] = freeze_type

        if duration_days:
            unfreeze_at = datetime.now() + timedelta(days=duration_days)
            account["auto_unfreeze_at"] = unfreeze_at.isoformat()
            # Schedule auto-unfreeze
            self._schedule_auto_unfreeze(account_id, unfreeze_at)

        # Audit log
        self._log_event(
            "account_frozen",
            account_id=account_id,
            reason=reason,
            duration_days=duration_days
        )

        # Notify owner
        self._send_notification(
            account["agent_id"],
            f"Your account {account_id} has been frozen. Reason: {reason}"
        )

        return {
            "account_id": account_id,
            "status": "frozen",
            "reason": reason,
            "frozen_at": account["frozen_at"],
            "auto_unfreeze_at": account.get("auto_unfreeze_at")
        }

    def unfreeze_account(
        self,
        account_id: str,
        verification_code: str,
        unfrozen_by: str
    ) -> Dict[str, Any]:
        """
        Unfreeze previously frozen account

        Args:
            account_id: Account to unfreeze
            verification_code: MFA code or admin authorization
            unfrozen_by: Who is unfreezing (agent_id or "admin")

        Returns:
            Unfreeze confirmation
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        if account["status"] != AccountStatus.FROZEN.value:
            raise ValueError("Account is not frozen")

        # Verify authorization
        if not self._verify_unfreeze_authorization(account_id, verification_code, unfrozen_by):
            raise ValueError("Invalid verification code")

        # Update status
        account["status"] = AccountStatus.ACTIVE.value
        account["unfrozen_at"] = datetime.now().isoformat()
        account["unfrozen_by"] = unfrozen_by

        # Clear freeze data
        account.pop("freeze_reason", None)
        account.pop("auto_unfreeze_at", None)

        # Audit log
        self._log_event(
            "account_unfrozen",
            account_id=account_id,
            unfrozen_by=unfrozen_by
        )

        # Notify owner
        self._send_notification(
            account["agent_id"],
            f"Your account {account_id} has been unfrozen and is now active."
        )

        return {
            "account_id": account_id,
            "status": "active",
            "unfrozen_at": account["unfrozen_at"]
        }

    def close_account(
        self,
        account_id: str,
        destination_account: str,
        closure_reason: str
    ) -> Dict[str, Any]:
        """
        Close account and transfer remaining balance

        Args:
            account_id: Account to close
            destination_account: Where to send remaining balance
            closure_reason: Why closing

        Returns:
            Closure confirmation with certificate
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        # Check no pending transactions
        pending = self._get_pending_transactions(account_id)
        if pending:
            raise ValueError(f"Cannot close account with {len(pending)} pending transactions")

        # Transfer remaining balance
        balance = account["balance"]
        if balance > 0:
            self._transfer_balance(
                from_account=account_id,
                to_account=destination_account,
                amount=balance,
                description=f"Account closure - {closure_reason}"
            )

        # Update status
        account["status"] = AccountStatus.CLOSED.value
        account["closed_at"] = datetime.now().isoformat()
        account["closure_reason"] = closure_reason
        account["final_balance"] = "0.00"

        # Generate closure certificate
        certificate = self._generate_closure_certificate(account)

        # Archive account (7-year retention for banking records)
        self._archive_account(account, retention_years=7)

        # Audit log
        self._log_event(
            "account_closed",
            account_id=account_id,
            reason=closure_reason,
            final_balance=str(balance)
        )

        # Notify owner
        self._send_notification(
            account["agent_id"],
            f"Account {account_id} has been closed. Certificate sent via email."
        )

        return {
            "account_id": account_id,
            "status": "closed",
            "closed_at": account["closed_at"],
            "certificate": certificate,
            "balance_transferred_to": destination_account,
            "amount_transferred": str(balance)
        }

    def upgrade_account_tier(
        self,
        account_id: str,
        new_tier: str,
        override_checks: bool = False
    ) -> Dict[str, Any]:
        """
        Upgrade account tier (Bronze → Silver → Gold → Platinum)

        Args:
            account_id: Account to upgrade
            new_tier: Target tier (SILVER, GOLD, PLATINUM)
            override_checks: Skip eligibility checks (admin only)

        Returns:
            Upgrade confirmation with new benefits
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        current_tier = account.get("tier", "BRONZE")

        # Check eligibility (unless override)
        if not override_checks:
            eligible, reason = self._check_tier_eligibility(account_id, new_tier)
            if not eligible:
                raise ValueError(f"Not eligible for {new_tier}: {reason}")

        # Apply new tier
        old_tier = current_tier
        account["tier"] = new_tier
        account["tier_upgraded_at"] = datetime.now().isoformat()

        # Update limits and fees
        new_benefits = self._apply_tier_benefits(account, new_tier)

        # Audit log
        self._log_event(
            "account_tier_upgraded",
            account_id=account_id,
            old_tier=old_tier,
            new_tier=new_tier
        )

        # Congratulations notification
        self._send_notification(
            account["agent_id"],
            f"Congratulations! Your account has been upgraded to {new_tier} tier. "
            f"New benefits: {new_benefits['summary']}"
        )

        return {
            "account_id": account_id,
            "old_tier": old_tier,
            "new_tier": new_tier,
            "benefits": new_benefits,
            "effective_date": account["tier_upgraded_at"]
        }

    # ============================================================================
    # CARD MANAGEMENT
    # ============================================================================

    def issue_virtual_card(
        self,
        account_id: str,
        card_type: str = "debit",
        daily_limit: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Issue virtual debit/credit card (instant)

        Args:
            account_id: Account to link card to
            card_type: "debit" or "credit"
            daily_limit: Optional spending limit

        Returns:
            Card details (PAN, CVV, expiry)
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        # Generate card details (in production, use Marqeta API)
        card_id = f"CARD-{uuid.uuid4().hex[:16].upper()}"
        pan = self._generate_card_number()  # 16 digits
        cvv = self._generate_cvv()  # 3 digits
        expiry = self._generate_expiry()  # MM/YY (3 years from now)

        # Default limits based on tier
        if not daily_limit:
            tier_limits = {
                "BRONZE": Decimal("1000"),
                "SILVER": Decimal("5000"),
                "GOLD": Decimal("25000"),
                "PLATINUM": Decimal("100000")
            }
            daily_limit = tier_limits.get(account["tier"], Decimal("1000"))

        card = {
            "card_id": card_id,
            "account_id": account_id,
            "agent_id": account["agent_id"],
            "card_type": CardType.VIRTUAL_DEBIT.value if card_type == "debit" else CardType.VIRTUAL_CREDIT.value,
            "pan": pan,
            "cvv": cvv,
            "expiry": expiry,
            "status": CardStatus.ACTIVE.value,
            "daily_limit": str(daily_limit),
            "per_transaction_limit": str(daily_limit / 2),
            "created_at": datetime.now().isoformat(),
            "is_virtual": True
        }

        self.cards_db[card_id] = card

        # Link to account
        if "cards" not in account:
            account["cards"] = []
        account["cards"].append(card_id)

        # Audit log
        self._log_event(
            "virtual_card_issued",
            account_id=account_id,
            card_id=card_id,
            card_type=card_type
        )

        # Notify
        self._send_notification(
            account["agent_id"],
            f"Virtual {card_type} card issued. Use it immediately for online purchases."
        )

        return {
            "card_id": card_id,
            "pan": pan,
            "cvv": cvv,
            "expiry": expiry,
            "status": "active",
            "daily_limit": str(daily_limit),
            "message": "Card active immediately"
        }

    def issue_physical_card(
        self,
        account_id: str,
        shipping_address: Dict[str, str],
        card_type: str = "debit",
        expedited_shipping: bool = False
    ) -> Dict[str, Any]:
        """
        Order physical card (3-5 business days delivery)

        Args:
            account_id: Account to link card to
            shipping_address: {"street", "city", "state", "zip", "country"}
            card_type: "debit" or "credit"
            expedited_shipping: 1-2 days ($25 extra)

        Returns:
            Order confirmation with tracking
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        # Verify shipping address
        self._verify_shipping_address(shipping_address)

        # Generate card (won't be active until activated)
        card_id = f"CARD-{uuid.uuid4().hex[:16].upper()}"
        pan = self._generate_card_number()
        last_4 = pan[-4:]

        # Shipping cost
        shipping_cost = Decimal("25.00") if expedited_shipping else Decimal("5.00")

        # Deduct shipping from account
        if account["balance"] < shipping_cost:
            raise ValueError(f"Insufficient balance for shipping (${shipping_cost})")

        account["balance"] -= shipping_cost

        # Estimated delivery
        delivery_days = 2 if expedited_shipping else 5
        estimated_delivery = datetime.now() + timedelta(days=delivery_days)

        card = {
            "card_id": card_id,
            "account_id": account_id,
            "agent_id": account["agent_id"],
            "card_type": CardType.PHYSICAL_DEBIT.value if card_type == "debit" else CardType.PHYSICAL_CREDIT.value,
            "pan": pan,
            "last_4": last_4,
            "cvv": self._generate_cvv(),
            "expiry": self._generate_expiry(),
            "status": CardStatus.PENDING.value,  # Not active until activated
            "shipping_address": shipping_address,
            "shipped_at": datetime.now().isoformat(),
            "estimated_delivery": estimated_delivery.isoformat(),
            "tracking_number": self._generate_tracking_number(),
            "is_virtual": False,
            "expedited": expedited_shipping
        }

        self.cards_db[card_id] = card

        # Audit log
        self._log_event(
            "physical_card_ordered",
            account_id=account_id,
            card_id=card_id,
            shipping_cost=str(shipping_cost)
        )

        return {
            "card_id": card_id,
            "last_4": last_4,
            "status": "pending_activation",
            "estimated_delivery": card["estimated_delivery"],
            "tracking_number": card["tracking_number"],
            "shipping_cost": str(shipping_cost),
            "message": "Card will be delivered in " + str(delivery_days) + " business days. Activate upon receipt."
        }

    def activate_card(
        self,
        card_id: str,
        last_4_digits: str,
        set_pin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Activate physical card upon receipt

        Args:
            card_id: Card to activate
            last_4_digits: Last 4 digits (verification)
            set_pin: Optional 4-digit PIN

        Returns:
            Activation confirmation
        """
        card = self.cards_db.get(card_id)
        if not card:
            raise ValueError("Card not found")

        if card["status"] != CardStatus.PENDING.value:
            raise ValueError(f"Card status is {card['status']}, cannot activate")

        # Verify last 4 digits
        if card["last_4"] != last_4_digits:
            raise ValueError("Last 4 digits do not match")

        # Activate
        card["status"] = CardStatus.ACTIVE.value
        card["activated_at"] = datetime.now().isoformat()

        # Set PIN if provided
        if set_pin:
            if len(set_pin) != 4 or not set_pin.isdigit():
                raise ValueError("PIN must be 4 digits")
            card["pin_hash"] = self._hash_pin(set_pin)
            card["pin_set_at"] = datetime.now().isoformat()

        # Audit log
        self._log_event(
            "card_activated",
            card_id=card_id,
            account_id=card["account_id"]
        )

        # Notify
        self._send_notification(
            card["agent_id"],
            f"Your card ending in {last_4_digits} is now active and ready to use!"
        )

        return {
            "card_id": card_id,
            "status": "active",
            "activated_at": card["activated_at"],
            "message": "Card is now active. You can use it for purchases and ATM withdrawals."
        }

    def freeze_card(
        self,
        card_id: str,
        reason: str = "customer_request"
    ) -> Dict[str, Any]:
        """
        Temporarily freeze card (lost, suspicious activity, or customer request)
        """
        card = self.cards_db.get(card_id)
        if not card:
            raise ValueError("Card not found")

        card["status"] = CardStatus.FROZEN.value
        card["frozen_at"] = datetime.now().isoformat()
        card["freeze_reason"] = reason

        self._log_event("card_frozen", card_id=card_id, reason=reason)

        return {
            "card_id": card_id,
            "status": "frozen",
            "message": "Card frozen. New authorizations will be declined. Unfreeze anytime."
        }

    def unfreeze_card(self, card_id: str) -> Dict[str, Any]:
        """Unfreeze previously frozen card"""
        card = self.cards_db.get(card_id)
        if not card:
            raise ValueError("Card not found")

        if card["status"] != CardStatus.FROZEN.value:
            raise ValueError("Card is not frozen")

        card["status"] = CardStatus.ACTIVE.value
        card["unfrozen_at"] = datetime.now().isoformat()

        self._log_event("card_unfrozen", card_id=card_id)

        return {"card_id": card_id, "status": "active", "message": "Card unfrozen successfully"}

    # ============================================================================
    # STATEMENTS & REPORTING
    # ============================================================================

    def generate_monthly_statement(
        self,
        account_id: str,
        month: int,
        year: int,
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Generate monthly PDF statement

        Args:
            account_id: Account ID
            month: 1-12
            year: e.g., 2026
            format: "pdf", "json", or "csv"

        Returns:
            Statement data or PDF bytes
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        # Get transactions for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        transactions = self._get_transactions_in_period(
            account_id,
            start_date,
            end_date
        )

        # Calculate summary
        starting_balance = self._get_balance_at_date(account_id, start_date)
        ending_balance = account["balance"]

        deposits = sum(tx["amount"] for tx in transactions if tx["type"] == "credit")
        withdrawals = sum(tx["amount"] for tx in transactions if tx["type"] == "debit")
        fees = sum(tx["amount"] for tx in transactions if tx["type"] == "fee")
        interest = sum(tx["amount"] for tx in transactions if tx["type"] == "interest")

        statement_data = {
            "account_id": account_id,
            "account_holder": account.get("agent_name", "Agent"),
            "statement_period": f"{month:02d}/{year}",
            "statement_date": datetime.now().isoformat(),
            "starting_balance": str(starting_balance),
            "ending_balance": str(ending_balance),
            "total_deposits": str(deposits),
            "total_withdrawals": str(withdrawals),
            "total_fees": str(fees),
            "interest_earned": str(interest),
            "transaction_count": len(transactions),
            "transactions": transactions
        }

        if format == "pdf":
            # Generate PDF (using reportlab or similar)
            pdf_bytes = self._generate_statement_pdf(statement_data)

            # Save to storage
            statement_id = f"STMT-{account_id}-{year}{month:02d}"
            self._save_statement(statement_id, pdf_bytes)

            return {
                "statement_id": statement_id,
                "format": "pdf",
                "size_bytes": len(pdf_bytes),
                "download_url": f"/statements/{statement_id}.pdf",
                "data": statement_data  # Also include raw data
            }
        else:
            return statement_data

    def export_transactions_csv(
        self,
        account_id: str,
        start_date: date,
        end_date: date
    ) -> str:
        """
        Export transactions to CSV

        Returns:
            CSV string
        """
        transactions = self._get_transactions_in_period(
            account_id,
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )

        # Build CSV
        csv_lines = [
            "Date,Description,Amount,Type,Balance,Category,Merchant"
        ]

        for tx in transactions:
            csv_lines.append(
                f"{tx['date']},{tx['description']},{tx['amount']},"
                f"{tx['type']},{tx['balance_after']},{tx.get('category', '')},"
                f"{tx.get('merchant', '')}"
            )

        csv_content = "\n".join(csv_lines)

        # Save for download
        export_id = f"EXPORT-{account_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self._save_export(export_id, csv_content, "text/csv")

        return csv_content

    # ============================================================================
    # ALERTS & NOTIFICATIONS
    # ============================================================================

    def set_balance_alert(
        self,
        account_id: str,
        threshold: Decimal,
        notification_method: str = "email"
    ) -> Dict[str, Any]:
        """
        Alert when balance falls below threshold
        """
        account = self.accounts_db.get(account_id)
        if not account:
            raise ValueError("Account not found")

        alert_config = {
            "type": "balance_threshold",
            "threshold": str(threshold),
            "notification_method": notification_method,
            "created_at": datetime.now().isoformat(),
            "enabled": True
        }

        if "alerts" not in account:
            account["alerts"] = []

        account["alerts"].append(alert_config)

        return {
            "account_id": account_id,
            "alert_type": "balance_threshold",
            "threshold": str(threshold),
            "status": "active"
        }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _check_tier_eligibility(self, account_id: str, target_tier: str) -> tuple:
        """Check if account qualifies for tier upgrade"""
        account = self.accounts_db.get(account_id)

        # Tier requirements
        requirements = {
            "SILVER": {
                "min_balance": Decimal("1000"),
                "min_transactions_30d": 10,
                "min_age_days": 30
            },
            "GOLD": {
                "min_balance": Decimal("10000"),
                "min_transactions_30d": 50,
                "min_age_days": 90
            },
            "PLATINUM": {
                "min_balance": Decimal("100000"),
                "min_transactions_30d": 100,
                "min_age_days": 180
            }
        }

        req = requirements.get(target_tier)
        if not req:
            return False, "Invalid tier"

        # Check balance
        if account["balance"] < req["min_balance"]:
            return False, f"Minimum balance ${req['min_balance']} required"

        # Check transaction volume
        tx_count_30d = self._count_transactions_last_30_days(account_id)
        if tx_count_30d < req["min_transactions_30d"]:
            return False, f"Minimum {req['min_transactions_30d']} transactions in last 30 days required"

        # Check account age
        created = datetime.fromisoformat(account["created_at"])
        age_days = (datetime.now() - created).days
        if age_days < req["min_age_days"]:
            return False, f"Account must be at least {req['min_age_days']} days old"

        return True, "Eligible"

    def _apply_tier_benefits(self, account: dict, tier: str) -> dict:
        """Apply tier-specific benefits"""
        benefits = {
            "BRONZE": {
                "daily_limit": "10000",
                "transaction_fee": "0.50",
                "atm_fee": "2.50",
                "free_transactions_monthly": 10,
                "interest_rate": "0.01"
            },
            "SILVER": {
                "daily_limit": "50000",
                "transaction_fee": "0.30",
                "atm_fee": "0.00",
                "free_transactions_monthly": 50,
                "interest_rate": "0.02"
            },
            "GOLD": {
                "daily_limit": "250000",
                "transaction_fee": "0.15",
                "atm_fee": "0.00",
                "free_transactions_monthly": 200,
                "interest_rate": "0.03"
            },
            "PLATINUM": {
                "daily_limit": "1000000",
                "transaction_fee": "0.05",
                "atm_fee": "0.00",
                "free_transactions_monthly": 999999,
                "interest_rate": "0.04"
            }
        }

        tier_benefits = benefits[tier]

        # Apply to account
        account["daily_limit"] = tier_benefits["daily_limit"]
        account["transaction_fee_percent"] = tier_benefits["transaction_fee"]
        account["atm_fee"] = tier_benefits["atm_fee"]
        account["free_transactions_monthly"] = tier_benefits["free_transactions_monthly"]

        return {
            "tier": tier,
            **tier_benefits,
            "summary": f"Daily limit: ${tier_benefits['daily_limit']}, "
                      f"Fee: {tier_benefits['transaction_fee']}%, "
                      f"Free ATM, {tier_benefits['free_transactions_monthly']} free tx/month"
        }

    def _generate_card_number(self) -> str:
        """Generate valid credit card number (Luhn algorithm)"""
        # In production, use Marqeta/issuer API
        # This is placeholder
        import random
        prefix = "4"  # Visa
        number = prefix + "".join([str(random.randint(0, 9)) for _ in range(14)])
        # Add Luhn check digit
        check_digit = self._calculate_luhn_check_digit(number)
        return number + str(check_digit)

    def _calculate_luhn_check_digit(self, number: str) -> int:
        """Calculate Luhn check digit"""
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return (10 - (checksum % 10)) % 10

    def _generate_cvv(self) -> str:
        """Generate CVV"""
        import random
        return "".join([str(random.randint(0, 9)) for _ in range(3)])

    def _generate_expiry(self) -> str:
        """Generate expiry date (3 years from now)"""
        expiry_date = datetime.now() + timedelta(days=3*365)
        return expiry_date.strftime("%m/%y")

    def _generate_tracking_number(self) -> str:
        """Generate shipping tracking number"""
        import random
        return "".join([str(random.randint(0, 9)) for _ in range(16)])

    def _hash_pin(self, pin: str) -> str:
        """Hash PIN for storage"""
        import hashlib
        return hashlib.sha256(pin.encode()).hexdigest()

    def _send_notification(self, agent_id: str, message: str):
        """Send notification to agent"""
        # In production: email, SMS, push notification
        print(f"[NOTIFICATION to {agent_id}]: {message}")

    def _log_event(self, event_type: str, **kwargs):
        """Log audit event"""
        # In production: write to audit log database
        print(f"[AUDIT] {event_type}: {kwargs}")


# Helper function for external use
def create_extended_front_office_agent(config):
    """Factory function to create extended agent"""
    return FrontOfficeAgentExtended(config)
