"""
Clearing & Settlement Agent Extended - Complete Payment Processing + Cross-Chain
=================================================================================

22 functions for enterprise payment processing:
- ACH, Wire, SWIFT, RTP/FedNow
- Batch processing with 90% gas savings
- Transaction netting (offset to reduce fees)
- Cross-chain bridges (Arc ↔ Ethereum)
- Payment reconciliation
- Settlement proof generation
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import sys
import os

try:
    from .clearing_settlement_agent import ClearingSettlementAgent
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from clearing_settlement_agent import ClearingSettlementAgent


class PaymentMethod(str, Enum):
    """Payment rail types"""
    ACH = "ach"
    WIRE = "wire"
    SWIFT = "swift"
    RTP = "rtp"  # Real-Time Payments
    FEDNOW = "fednow"
    SEPA = "sepa"  # European payments
    CHECK = "check"
    CRYPTO = "crypto"


class SettlementStatus(str, Enum):
    """Settlement lifecycle"""
    PENDING = "pending"
    BATCHED = "batched"
    PROCESSING = "processing"
    SETTLED = "settled"
    FAILED = "failed"
    REVERSED = "reversed"


class ChainType(str, Enum):
    """Blockchain networks"""
    ARC = "arc"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"


class ClearingSettlementAgentExtended(ClearingSettlementAgent):
    """
    Extended Clearing & Settlement with:
    - Multi-rail payment processing (ACH, Wire, SWIFT, RTP)
    - Batch processing (90% gas savings)
    - Transaction netting (reduce fees)
    - Cross-chain bridges
    - Real-time gross settlement
    - Proof of settlement generation
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.payment_queues: Dict[str, List[Dict]] = {
            "ach": [],
            "wire": [],
            "swift": [],
            "rtp": []
        }
        self.settlements: Dict[str, Dict] = {}
        self.bridge_transactions: Dict[str, Dict] = {}
        self.reconciliation_reports: List[Dict] = []

    # ==================== ACH PROCESSING ====================

    def process_ach_transfer(
        self,
        from_account: str,
        to_account: str,
        amount: Decimal,
        routing_number: str,
        account_number: str,
        description: str,
        same_day: bool = False
    ) -> Dict[str, Any]:
        """
        Process ACH transfer (domestic US)

        Standard ACH: 1-3 business days, $0.25 fee
        Same-Day ACH: Same day by 5pm ET, $1.00 fee
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if len(routing_number) != 9:
            raise ValueError("Invalid routing number (must be 9 digits)")

        # ACH limits
        if same_day and amount > Decimal("1000000"):
            raise ValueError("Same-Day ACH limited to $1,000,000")

        fee = Decimal("1.00") if same_day else Decimal("0.25")

        ach_id = f"ACH{int(datetime.now().timestamp())}"

        ach_transfer = {
            "ach_id": ach_id,
            "from_account": from_account,
            "to_account": to_account,
            "routing_number": routing_number,
            "account_number": account_number[-4:],  # Last 4 digits only
            "amount": amount,
            "fee": fee,
            "description": description,
            "type": "same_day" if same_day else "standard",
            "status": SettlementStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "settlement_date": self._calculate_ach_settlement_date(same_day)
        }

        # Queue for batch processing
        self.payment_queues["ach"].append(ach_transfer)
        self.settlements[ach_id] = ach_transfer

        return {
            "ach_id": ach_id,
            "status": "pending",
            "settlement_date": ach_transfer["settlement_date"],
            "fee": str(fee),
            "processing_time": "Same business day by 5pm ET" if same_day else "1-3 business days"
        }

    def _calculate_ach_settlement_date(self, same_day: bool) -> str:
        """Calculate ACH settlement date"""
        now = datetime.now()

        if same_day:
            # Same day by 5pm ET if submitted before 2:45pm ET
            settlement = now
        else:
            # 1-3 business days (skip weekends)
            days_to_add = 1
            settlement = now + timedelta(days=days_to_add)

            while settlement.weekday() >= 5:  # Saturday or Sunday
                settlement += timedelta(days=1)

        return settlement.isoformat()

    # ==================== WIRE TRANSFERS ====================

    def process_wire_transfer(
        self,
        from_account: str,
        to_account: str,
        amount: Decimal,
        beneficiary_bank: str,
        beneficiary_account: str,
        routing_number: str,
        international: bool = False,
        swift_code: Optional[str] = None,
        intermediary_bank: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process wire transfer (domestic or international)

        Domestic: Same day, $25 fee
        International: 1-5 days, $45 fee, requires SWIFT code
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if international and not swift_code:
            raise ValueError("SWIFT code required for international wires")

        fee = Decimal("45") if international else Decimal("25")

        wire_id = f"WIRE{int(datetime.now().timestamp())}"

        wire_transfer = {
            "wire_id": wire_id,
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "fee": fee,
            "beneficiary_bank": beneficiary_bank,
            "beneficiary_account": beneficiary_account[-4:],
            "routing_number": routing_number,
            "swift_code": swift_code,
            "intermediary_bank": intermediary_bank,
            "type": "international" if international else "domestic",
            "status": SettlementStatus.PROCESSING,
            "created_at": datetime.now().isoformat(),
            "settlement_date": self._calculate_wire_settlement_date(international)
        }

        self.payment_queues["wire"].append(wire_transfer)
        self.settlements[wire_id] = wire_transfer

        return {
            "wire_id": wire_id,
            "status": "processing",
            "settlement_date": wire_transfer["settlement_date"],
            "fee": str(fee),
            "processing_time": "1-5 business days" if international else "Same business day"
        }

    def _calculate_wire_settlement_date(self, international: bool) -> str:
        """Calculate wire settlement date"""
        now = datetime.now()

        if international:
            # 1-5 business days for international
            settlement = now + timedelta(days=3)
        else:
            # Same business day for domestic
            settlement = now

        return settlement.isoformat()

    # ==================== SWIFT PAYMENTS ====================

    def process_swift_payment(
        self,
        from_account: str,
        swift_code: str,
        beneficiary_name: str,
        beneficiary_account: str,
        amount: Decimal,
        currency: str,
        beneficiary_address: str,
        purpose_code: str
    ) -> Dict[str, Any]:
        """
        Process SWIFT international payment

        SWIFT MT103: Standard customer credit transfer
        Fee: $45 + correspondent bank fees (~$15-30)
        Time: 1-5 business days
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if len(swift_code) not in [8, 11]:
            raise ValueError("Invalid SWIFT code (must be 8 or 11 characters)")

        # SWIFT fee + estimated correspondent fees
        base_fee = Decimal("45")
        correspondent_fee = Decimal("20")  # Estimated
        total_fee = base_fee + correspondent_fee

        swift_id = f"SWIFT{int(datetime.now().timestamp())}"

        swift_payment = {
            "swift_id": swift_id,
            "from_account": from_account,
            "swift_code": swift_code,
            "beneficiary_name": beneficiary_name,
            "beneficiary_account": beneficiary_account[-4:],
            "amount": amount,
            "currency": currency,
            "beneficiary_address": beneficiary_address,
            "purpose_code": purpose_code,
            "base_fee": base_fee,
            "correspondent_fee": correspondent_fee,
            "total_fee": total_fee,
            "status": SettlementStatus.PROCESSING,
            "message_type": "MT103",
            "created_at": datetime.now().isoformat(),
            "estimated_settlement": (datetime.now() + timedelta(days=3)).isoformat()
        }

        self.payment_queues["swift"].append(swift_payment)
        self.settlements[swift_id] = swift_payment

        return {
            "swift_id": swift_id,
            "status": "processing",
            "message_type": "MT103",
            "estimated_settlement": swift_payment["estimated_settlement"],
            "total_fee": str(total_fee),
            "processing_time": "1-5 business days",
            "note": "Correspondent bank fees may apply"
        }

    # ==================== REAL-TIME PAYMENTS ====================

    def process_real_time_payment(
        self,
        from_account: str,
        to_account: str,
        amount: Decimal,
        routing_number: str,
        account_number: str,
        payment_info: str,
        network: str = "rtp"  # "rtp" or "fednow"
    ) -> Dict[str, Any]:
        """
        Process real-time payment (RTP or FedNow)

        RTP (The Clearing House): 24/7/365, sub-second settlement
        FedNow (Federal Reserve): 24/7/365, immediate settlement

        Fee: $0.045 per transaction
        Limit: $1,000,000 per transaction
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if amount > Decimal("1000000"):
            raise ValueError("RTP/FedNow limited to $1,000,000 per transaction")

        if network not in ["rtp", "fednow"]:
            raise ValueError("Network must be 'rtp' or 'fednow'")

        fee = Decimal("0.045")

        rtp_id = f"{network.upper()}{int(datetime.now().timestamp())}"

        rtp_payment = {
            "rtp_id": rtp_id,
            "from_account": from_account,
            "to_account": to_account,
            "routing_number": routing_number,
            "account_number": account_number[-4:],
            "amount": amount,
            "fee": fee,
            "payment_info": payment_info,
            "network": network.upper(),
            "status": SettlementStatus.SETTLED,  # Immediate settlement
            "created_at": datetime.now().isoformat(),
            "settled_at": datetime.now().isoformat()
        }

        self.payment_queues["rtp"].append(rtp_payment)
        self.settlements[rtp_id] = rtp_payment

        return {
            "rtp_id": rtp_id,
            "status": "settled",
            "network": network.upper(),
            "settled_at": rtp_payment["settled_at"],
            "fee": str(fee),
            "processing_time": "Immediate (sub-second)"
        }

    # ==================== BATCH PROCESSING ====================

    def batch_process_transactions(
        self,
        payment_method: PaymentMethod,
        max_batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Batch process queued transactions (90% gas savings)

        Instead of processing 1000 transactions individually:
        - Individual: 1000 tx * 21000 gas = 21M gas
        - Batched: 1 batch tx = ~2.1M gas (90% savings!)
        """
        queue = self.payment_queues.get(payment_method.value, [])

        if not queue:
            return {
                "batch_id": None,
                "message": f"No pending {payment_method.value} transactions"
            }

        # Take up to max_batch_size transactions
        batch = queue[:max_batch_size]
        self.payment_queues[payment_method.value] = queue[max_batch_size:]

        batch_id = f"BATCH{payment_method.value.upper()}{int(datetime.now().timestamp())}"

        total_amount = sum(tx["amount"] for tx in batch)
        total_fees = sum(tx["fee"] for tx in batch)

        # Calculate gas savings
        individual_gas = len(batch) * 21000
        batch_gas = 210000 + (len(batch) * 5000)  # Base + per-tx overhead
        gas_savings = ((individual_gas - batch_gas) / individual_gas) * 100

        batch_record = {
            "batch_id": batch_id,
            "payment_method": payment_method.value,
            "transaction_count": len(batch),
            "total_amount": total_amount,
            "total_fees": total_fees,
            "status": SettlementStatus.PROCESSING,
            "gas_estimate": batch_gas,
            "gas_savings_percent": round(gas_savings, 1),
            "created_at": datetime.now().isoformat(),
            "transactions": [tx.get("ach_id") or tx.get("wire_id") or tx.get("swift_id") for tx in batch]
        }

        # Update all transactions in batch to "batched" status
        for tx in batch:
            tx_id = tx.get("ach_id") or tx.get("wire_id") or tx.get("swift_id")
            if tx_id in self.settlements:
                self.settlements[tx_id]["status"] = SettlementStatus.BATCHED
                self.settlements[tx_id]["batch_id"] = batch_id

        self.settlements[batch_id] = batch_record

        return {
            "batch_id": batch_id,
            "transactions_batched": len(batch),
            "total_amount": str(total_amount),
            "gas_savings": f"{gas_savings:.1f}%",
            "estimated_gas": batch_gas,
            "status": "processing"
        }

    # ==================== TRANSACTION NETTING ====================

    def netting_settlement(
        self,
        agent_pairs: List[tuple[str, str]],
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Net offsetting transactions to reduce settlement volume

        Example:
        - Agent A owes B $1000
        - Agent B owes A $700
        - Net result: A pays B $300 (70% reduction!)

        Benefits:
        - Reduce transaction fees
        - Reduce settlement volume
        - Faster reconciliation
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        # Calculate bilateral net positions
        net_positions = {}

        for agent_a, agent_b in agent_pairs:
            pair_key = tuple(sorted([agent_a, agent_b]))

            if pair_key not in net_positions:
                net_positions[pair_key] = {
                    "agent_a": pair_key[0],
                    "agent_b": pair_key[1],
                    "a_to_b": Decimal("0"),
                    "b_to_a": Decimal("0"),
                    "transactions": []
                }

            # Find all transactions between these agents
            for settlement in self.settlements.values():
                if isinstance(settlement, dict) and "created_at" in settlement:
                    created = datetime.fromisoformat(settlement["created_at"])

                    if created >= cutoff_time:
                        from_acc = settlement.get("from_account")
                        to_acc = settlement.get("to_account")
                        amount = settlement.get("amount", Decimal("0"))

                        if from_acc == agent_a and to_acc == agent_b:
                            net_positions[pair_key]["a_to_b"] += amount
                            net_positions[pair_key]["transactions"].append(settlement)
                        elif from_acc == agent_b and to_acc == agent_a:
                            net_positions[pair_key]["b_to_a"] += amount
                            net_positions[pair_key]["transactions"].append(settlement)

        # Calculate net settlements
        net_settlements = []
        total_original = Decimal("0")
        total_netted = Decimal("0")

        for pair_key, position in net_positions.items():
            a_to_b = position["a_to_b"]
            b_to_a = position["b_to_a"]

            total_original += a_to_b + b_to_a

            net_amount = abs(a_to_b - b_to_a)

            if net_amount > 0:
                from_agent = position["agent_a"] if a_to_b > b_to_a else position["agent_b"]
                to_agent = position["agent_b"] if a_to_b > b_to_a else position["agent_a"]

                total_netted += net_amount

                net_settlements.append({
                    "from": from_agent,
                    "to": to_agent,
                    "gross_a_to_b": str(a_to_b),
                    "gross_b_to_a": str(b_to_a),
                    "net_amount": str(net_amount),
                    "reduction": str(a_to_b + b_to_a - net_amount),
                    "transactions_netted": len(position["transactions"])
                })

        reduction_percent = ((total_original - total_netted) / total_original * 100) if total_original > 0 else 0

        netting_id = f"NET{int(datetime.now().timestamp())}"

        return {
            "netting_id": netting_id,
            "time_window_hours": time_window_hours,
            "pairs_processed": len(net_positions),
            "total_original_volume": str(total_original),
            "total_netted_volume": str(total_netted),
            "volume_reduction": f"{reduction_percent:.1f}%",
            "net_settlements": net_settlements,
            "created_at": datetime.now().isoformat()
        }

    # ==================== CROSS-CHAIN BRIDGES ====================

    def bridge_to_ethereum(
        self,
        agent_id: str,
        amount_usdc: Decimal,
        eth_address: str,
        gas_tier: str = "standard"  # "slow", "standard", "fast"
    ) -> Dict[str, Any]:
        """
        Bridge USDC from Arc to Ethereum

        Uses Circle's Cross-Chain Transfer Protocol (CCTP)
        - Burn USDC on Arc
        - Mint USDC on Ethereum
        - Atomic, no wrapped tokens

        Gas tiers:
        - Slow: ~10 min, $5 fee
        - Standard: ~5 min, $10 fee
        - Fast: ~2 min, $20 fee
        """
        if amount_usdc < Decimal("10"):
            raise ValueError("Minimum bridge amount: $10 USDC")

        if not eth_address.startswith("0x") or len(eth_address) != 42:
            raise ValueError("Invalid Ethereum address")

        gas_fees = {
            "slow": Decimal("5"),
            "standard": Decimal("10"),
            "fast": Decimal("20")
        }

        gas_times = {
            "slow": "~10 minutes",
            "standard": "~5 minutes",
            "fast": "~2 minutes"
        }

        fee = gas_fees.get(gas_tier, Decimal("10"))

        bridge_id = f"BRIDGE{int(datetime.now().timestamp())}"

        bridge_tx = {
            "bridge_id": bridge_id,
            "agent_id": agent_id,
            "from_chain": ChainType.ARC,
            "to_chain": ChainType.ETHEREUM,
            "amount": amount_usdc,
            "token": "USDC",
            "destination_address": eth_address,
            "gas_tier": gas_tier,
            "bridge_fee": fee,
            "protocol": "CCTP",  # Circle Cross-Chain Transfer Protocol
            "status": SettlementStatus.PROCESSING,
            "created_at": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat()
        }

        self.bridge_transactions[bridge_id] = bridge_tx

        return {
            "bridge_id": bridge_id,
            "from_chain": "Arc",
            "to_chain": "Ethereum",
            "amount": str(amount_usdc),
            "destination": eth_address,
            "fee": str(fee),
            "estimated_time": gas_times[gas_tier],
            "protocol": "Circle CCTP (burn & mint)",
            "status": "processing"
        }

    def bridge_from_ethereum(
        self,
        agent_id: str,
        amount_usdc: Decimal,
        eth_tx_hash: str,
        arc_address: str
    ) -> Dict[str, Any]:
        """
        Bridge USDC from Ethereum to Arc

        Verify Ethereum burn transaction, then mint on Arc
        """
        if amount_usdc < Decimal("10"):
            raise ValueError("Minimum bridge amount: $10 USDC")

        if not eth_tx_hash.startswith("0x") or len(eth_tx_hash) != 66:
            raise ValueError("Invalid Ethereum transaction hash")

        bridge_id = f"BRIDGE{int(datetime.now().timestamp())}"

        bridge_tx = {
            "bridge_id": bridge_id,
            "agent_id": agent_id,
            "from_chain": ChainType.ETHEREUM,
            "to_chain": ChainType.ARC,
            "amount": amount_usdc,
            "token": "USDC",
            "source_tx": eth_tx_hash,
            "destination_address": arc_address,
            "bridge_fee": Decimal("10"),
            "protocol": "CCTP",
            "status": SettlementStatus.PROCESSING,
            "created_at": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat()
        }

        self.bridge_transactions[bridge_id] = bridge_tx

        return {
            "bridge_id": bridge_id,
            "from_chain": "Ethereum",
            "to_chain": "Arc",
            "amount": str(amount_usdc),
            "source_tx": eth_tx_hash,
            "destination": arc_address,
            "status": "processing"
        }

    def bridge_to_polygon(
        self,
        agent_id: str,
        amount_usdc: Decimal,
        polygon_address: str
    ) -> Dict[str, Any]:
        """Bridge USDC to Polygon (low fees, fast)"""
        if amount_usdc < Decimal("5"):
            raise ValueError("Minimum bridge amount: $5 USDC")

        bridge_id = f"BRIDGE{int(datetime.now().timestamp())}"

        bridge_tx = {
            "bridge_id": bridge_id,
            "agent_id": agent_id,
            "from_chain": ChainType.ARC,
            "to_chain": ChainType.POLYGON,
            "amount": amount_usdc,
            "destination_address": polygon_address,
            "bridge_fee": Decimal("2"),  # Polygon is cheap!
            "protocol": "CCTP",
            "status": SettlementStatus.PROCESSING,
            "created_at": datetime.now().isoformat()
        }

        self.bridge_transactions[bridge_id] = bridge_tx

        return {
            "bridge_id": bridge_id,
            "to_chain": "Polygon",
            "amount": str(amount_usdc),
            "fee": "$2",
            "estimated_time": "~3 minutes"
        }

    # ==================== RECONCILIATION ====================

    def reconcile_daily_settlements(
        self,
        date: str
    ) -> Dict[str, Any]:
        """
        End-of-day reconciliation report

        Ensures all payments match:
        - Internal ledger
        - External bank confirmations
        - Blockchain settlements
        """
        target_date = datetime.fromisoformat(date).date()

        # Categorize settlements by type
        by_method = {
            "ach": [],
            "wire": [],
            "swift": [],
            "rtp": [],
            "bridge": []
        }

        total_volume = Decimal("0")
        total_fees = Decimal("0")

        for settlement_id, settlement in self.settlements.items():
            if isinstance(settlement, dict) and "created_at" in settlement:
                created = datetime.fromisoformat(settlement["created_at"]).date()

                if created == target_date:
                    amount = settlement.get("amount", Decimal("0"))
                    fee = settlement.get("fee", Decimal("0"))

                    total_volume += amount
                    total_fees += fee

                    # Categorize
                    if "ach_id" in settlement:
                        by_method["ach"].append(settlement)
                    elif "wire_id" in settlement:
                        by_method["wire"].append(settlement)
                    elif "swift_id" in settlement:
                        by_method["swift"].append(settlement)
                    elif "rtp_id" in settlement:
                        by_method["rtp"].append(settlement)

        # Bridge transactions
        for bridge_id, bridge in self.bridge_transactions.items():
            created = datetime.fromisoformat(bridge["created_at"]).date()
            if created == target_date:
                by_method["bridge"].append(bridge)
                total_volume += bridge["amount"]
                total_fees += bridge["bridge_fee"]

        reconciliation_id = f"RECON{date}"

        report = {
            "reconciliation_id": reconciliation_id,
            "date": date,
            "total_volume": str(total_volume),
            "total_fees": str(total_fees),
            "by_method": {
                "ach": {
                    "count": len(by_method["ach"]),
                    "volume": str(sum(s["amount"] for s in by_method["ach"]))
                },
                "wire": {
                    "count": len(by_method["wire"]),
                    "volume": str(sum(s["amount"] for s in by_method["wire"]))
                },
                "swift": {
                    "count": len(by_method["swift"]),
                    "volume": str(sum(s["amount"] for s in by_method["swift"]))
                },
                "rtp": {
                    "count": len(by_method["rtp"]),
                    "volume": str(sum(s["amount"] for s in by_method["rtp"]))
                },
                "bridge": {
                    "count": len(by_method["bridge"]),
                    "volume": str(sum(b["amount"] for b in by_method["bridge"]))
                }
            },
            "status_breakdown": self._count_by_status(by_method),
            "created_at": datetime.now().isoformat()
        }

        self.reconciliation_reports.append(report)

        return report

    def _count_by_status(self, by_method: Dict) -> Dict[str, int]:
        """Count settlements by status"""
        status_counts = {
            "pending": 0,
            "processing": 0,
            "settled": 0,
            "failed": 0
        }

        for method_list in by_method.values():
            for settlement in method_list:
                status = settlement.get("status", "unknown")
                if status in status_counts:
                    status_counts[status] += 1

        return status_counts

    # ==================== SETTLEMENT PROOFS ====================

    def generate_settlement_proof(
        self,
        settlement_id: str
    ) -> Dict[str, Any]:
        """
        Generate cryptographic proof of settlement

        Includes:
        - Settlement details hash
        - Blockchain transaction hash
        - Timestamp proof
        - Digital signature
        """
        settlement = self.settlements.get(settlement_id)

        if not settlement:
            settlement = self.bridge_transactions.get(settlement_id)

        if not settlement:
            raise ValueError(f"Settlement {settlement_id} not found")

        # Create merkle root of settlement data
        settlement_json = json.dumps(settlement, sort_keys=True, default=str)
        settlement_hash = hashlib.sha256(settlement_json.encode()).hexdigest()

        # Generate proof
        proof = {
            "settlement_id": settlement_id,
            "settlement_hash": settlement_hash,
            "settlement_type": settlement.get("type", "unknown"),
            "amount": str(settlement.get("amount", "0")),
            "status": settlement.get("status"),
            "timestamp": settlement.get("created_at"),
            "proof_generated_at": datetime.now().isoformat(),
            "blockchain_tx": f"0x{settlement_hash[:64]}",  # Mock tx hash
            "merkle_root": self._generate_merkle_root(settlement_hash),
            "digital_signature": self._sign_settlement(settlement_hash)
        }

        return proof

    def _generate_merkle_root(self, settlement_hash: str) -> str:
        """Generate Merkle root for settlement proof"""
        # In production, this would be a real Merkle tree
        combined = settlement_hash + datetime.now().isoformat()
        return hashlib.sha256(combined.encode()).hexdigest()

    def _sign_settlement(self, settlement_hash: str) -> str:
        """Digital signature for settlement (mock)"""
        # In production, use actual private key signing
        signature_data = f"{settlement_hash}:BAAS_ARC_BANK"
        return hashlib.sha256(signature_data.encode()).hexdigest()

    # ==================== PAYMENT ANALYTICS ====================

    def get_payment_analytics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Payment processing analytics

        Metrics:
        - Volume by method
        - Average processing time
        - Fee efficiency
        - Settlement success rate
        """
        cutoff = datetime.now() - timedelta(days=days)

        analytics = {
            "period_days": days,
            "by_method": {},
            "total_volume": Decimal("0"),
            "total_fees": Decimal("0"),
            "total_transactions": 0
        }

        for settlement in self.settlements.values():
            if isinstance(settlement, dict) and "created_at" in settlement:
                created = datetime.fromisoformat(settlement["created_at"])

                if created >= cutoff:
                    amount = settlement.get("amount", Decimal("0"))
                    fee = settlement.get("fee", Decimal("0"))

                    analytics["total_volume"] += amount
                    analytics["total_fees"] += fee
                    analytics["total_transactions"] += 1

                    # Categorize by method
                    if "ach_id" in settlement:
                        method = "ach"
                    elif "wire_id" in settlement:
                        method = "wire"
                    elif "swift_id" in settlement:
                        method = "swift"
                    elif "rtp_id" in settlement:
                        method = "rtp"
                    else:
                        method = "other"

                    if method not in analytics["by_method"]:
                        analytics["by_method"][method] = {
                            "count": 0,
                            "volume": Decimal("0"),
                            "fees": Decimal("0")
                        }

                    analytics["by_method"][method]["count"] += 1
                    analytics["by_method"][method]["volume"] += amount
                    analytics["by_method"][method]["fees"] += fee

        # Convert Decimals to strings for JSON
        analytics["total_volume"] = str(analytics["total_volume"])
        analytics["total_fees"] = str(analytics["total_fees"])

        for method in analytics["by_method"]:
            analytics["by_method"][method]["volume"] = str(analytics["by_method"][method]["volume"])
            analytics["by_method"][method]["fees"] = str(analytics["by_method"][method]["fees"])

        # Calculate fee efficiency
        if analytics["total_transactions"] > 0:
            avg_fee = Decimal(analytics["total_fees"]) / analytics["total_transactions"]
            analytics["average_fee_per_tx"] = str(avg_fee)

        return analytics

    # ==================== BILL PAY ====================

    def process_bill_payment(
        self,
        agent_id: str,
        payee_name: str,
        payee_account: str,
        amount: Decimal,
        due_date: str,
        recurring: bool = False,
        frequency: Optional[str] = None  # "monthly", "weekly"
    ) -> Dict[str, Any]:
        """
        Bill pay service

        Schedule one-time or recurring bill payments
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        bill_id = f"BILL{int(datetime.now().timestamp())}"

        bill_payment = {
            "bill_id": bill_id,
            "agent_id": agent_id,
            "payee_name": payee_name,
            "payee_account": payee_account[-4:],
            "amount": amount,
            "due_date": due_date,
            "recurring": recurring,
            "frequency": frequency,
            "status": SettlementStatus.PENDING,
            "payment_method": PaymentMethod.ACH,  # Default to ACH for bills
            "created_at": datetime.now().isoformat()
        }

        self.settlements[bill_id] = bill_payment

        # If due date is today, queue for processing
        if due_date == datetime.now().date().isoformat():
            self.payment_queues["ach"].append(bill_payment)

        return {
            "bill_id": bill_id,
            "payee": payee_name,
            "amount": str(amount),
            "due_date": due_date,
            "recurring": recurring,
            "status": "scheduled"
        }

    # ==================== CHECK PROCESSING ====================

    def process_check_deposit(
        self,
        agent_id: str,
        check_image_front: str,  # Base64 encoded
        check_image_back: str,
        amount: Decimal,
        check_number: str
    ) -> Dict[str, Any]:
        """
        Mobile check deposit (Remote Deposit Capture)

        Uses OCR + fraud detection
        Hold period: 2 business days for checks <$5000
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        check_id = f"CHK{int(datetime.now().timestamp())}"

        # Determine hold period based on amount
        hold_days = 2 if amount < Decimal("5000") else 5

        check_deposit = {
            "check_id": check_id,
            "agent_id": agent_id,
            "amount": amount,
            "check_number": check_number,
            "status": SettlementStatus.PENDING,
            "hold_until": (datetime.now() + timedelta(days=hold_days)).isoformat(),
            "fraud_score": self._check_fraud_score(),  # Mock
            "created_at": datetime.now().isoformat()
        }

        self.settlements[check_id] = check_deposit

        return {
            "check_id": check_id,
            "amount": str(amount),
            "status": "pending",
            "hold_until": check_deposit["hold_until"],
            "hold_days": hold_days,
            "fraud_score": check_deposit["fraud_score"]
        }

    def _check_fraud_score(self) -> int:
        """Mock fraud detection for checks (0-100, higher = riskier)"""
        # In production: OCR, signature verification, duplicate detection
        return 15  # Low risk

    # ==================== MULTI-CHAIN ATOMIC SWAPS ====================

    def atomic_swap_cross_chain(
        self,
        agent_a_id: str,
        agent_b_id: str,
        agent_a_asset: str,
        agent_b_asset: str,
        agent_a_amount: Decimal,
        agent_b_amount: Decimal,
        agent_a_chain: ChainType,
        agent_b_chain: ChainType,
        timeout_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Cross-chain atomic swap using Hash Time-Locked Contracts (HTLCs)

        Example:
        - Agent A: 1000 USDC on Arc
        - Agent B: 0.5 ETH on Ethereum
        - Atomic swap: both succeed or both fail

        How it works:
        1. Agent A locks USDC with hash H
        2. Agent B locks ETH with same hash H
        3. Agent A reveals secret, claims ETH
        4. Agent B uses revealed secret, claims USDC
        5. If timeout: both refunded
        """
        swap_id = f"SWAP{int(datetime.now().timestamp())}"
        secret = hashlib.sha256(swap_id.encode()).hexdigest()
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()

        swap = {
            "swap_id": swap_id,
            "agent_a": {
                "id": agent_a_id,
                "asset": agent_a_asset,
                "amount": str(agent_a_amount),
                "chain": agent_a_chain.value
            },
            "agent_b": {
                "id": agent_b_id,
                "asset": agent_b_asset,
                "amount": str(agent_b_amount),
                "chain": agent_b_chain.value
            },
            "secret_hash": secret_hash,
            "timeout": (datetime.now() + timedelta(hours=timeout_hours)).isoformat(),
            "status": "locked",
            "created_at": datetime.now().isoformat()
        }

        self.bridge_transactions[swap_id] = swap

        return {
            "swap_id": swap_id,
            "secret_hash": secret_hash,
            "timeout": swap["timeout"],
            "status": "locked",
            "note": "Both parties must complete within timeout or swap is refunded"
        }
