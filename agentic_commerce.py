"""
Agentic Commerce Payment Flows
Sistema de pagamentos autônomos para hackathon com:
- Usage-based payment (AI agents pagando por API calls)
- Autonomous transaction approvals com multi-agent consensus
- Micropayment support (sub-dollar USDC transactions)
- Agent-to-agent payments
- API consumption tracking e billing
"""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import logging
from collections import defaultdict
import time

try:
    from .core.transaction_types import (
        Transaction, AgentState, BankingAnalysis,
        TransactionEvaluation, TransactionType
    )
    from .core.config import CONFIG, DECISION_TYPES
    from .banking_syndicate import BankingSyndicate
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from core.transaction_types import (
        Transaction, AgentState, BankingAnalysis,
        TransactionEvaluation, TransactionType
    )
    from core.config import CONFIG, DECISION_TYPES
    from banking_syndicate import BankingSyndicate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIUsageRecord:
    """Registro de uso de API"""
    agent_id: str
    api_endpoint: str
    calls_count: int
    timestamp: datetime
    cost_per_call: Decimal
    total_cost: Decimal
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MicropaymentBatch:
    """Batch de micropagamentos agregados"""
    batch_id: str
    agent_id: str
    payments: List[Transaction] = field(default_factory=list)
    total_amount: Decimal = Decimal("0.0")
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    status: str = "pending"  # pending, executing, completed, failed


@dataclass
class AgentToAgentPayment:
    """Pagamento entre agentes"""
    payment_id: str
    from_agent: str
    to_agent: str
    amount: Decimal
    purpose: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusVote:
    """Voto de consenso para aprovação autônoma"""
    voter_agent_id: str
    vote: str  # "approve", "reject", "abstain"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


class AgenticCommerce:
    """
    Sistema de Pagamentos Autônomos para Agentic Commerce

    Features:
    1. Usage-based payment: AI agents pagando por API calls
    2. Autonomous approvals: Consenso multi-agent
    3. Micropayments: Transações sub-dollar otimizadas
    4. Agent-to-agent: Pagamentos diretos entre agentes
    5. API tracking: Monitoramento e billing de consumo
    """

    def __init__(self, syndicate: Optional[BankingSyndicate] = None):
        """
        Inicializa sistema de agentic commerce

        Args:
            syndicate: Instância do BankingSyndicate (opcional)
        """
        logger.info("[AGENT] Initializing Agentic Commerce System...")

        self.syndicate = syndicate or BankingSyndicate()

        # API Usage Tracking
        self.api_usage_log: Dict[str, List[APIUsageRecord]] = defaultdict(list)
        self.api_pricing: Dict[str, Decimal] = {
            "gpt-4": Decimal("0.03"),  # $0.03 per call
            "gpt-3.5-turbo": Decimal("0.002"),  # $0.002 per call
            "claude-3-opus": Decimal("0.015"),  # $0.015 per call
            "claude-3-sonnet": Decimal("0.003"),  # $0.003 per call
            "gemini-pro": Decimal("0.001"),  # $0.001 per call
        }

        # Micropayment Management
        self.micropayment_threshold = Decimal("1.0")  # Aggregate até $1
        self.micropayment_batches: Dict[str, MicropaymentBatch] = {}
        self.batch_timeout = timedelta(minutes=5)  # Executa batch a cada 5 min

        # Agent-to-Agent Payments
        self.agent_payments: List[AgentToAgentPayment] = []
        self.agent_payment_limits: Dict[str, Decimal] = {}  # Limites por agente

        # Autonomous Consensus
        self.consensus_threshold = 0.66  # 66% approval needed
        self.consensus_votes: Dict[str, List[ConsensusVote]] = defaultdict(list)

        # Billing Cycle
        self.billing_cycle = timedelta(hours=24)  # Daily billing
        self.last_billing: Dict[str, datetime] = {}

        logger.info("[SUCCESS] Agentic Commerce System initialized")
        logger.info(f"   - API pricing configured for {len(self.api_pricing)} models")
        logger.info(f"   - Micropayment threshold: ${self.micropayment_threshold}")
        logger.info(f"   - Consensus threshold: {self.consensus_threshold * 100}%")

    # ====================
    # 1. USAGE-BASED PAYMENT
    # ====================

    def track_api_call(
        self,
        agent_id: str,
        api_endpoint: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> APIUsageRecord:
        """
        Registra uma chamada de API e calcula custo

        Args:
            agent_id: ID do agente fazendo a chamada
            api_endpoint: Endpoint da API (ex: "gpt-4", "claude-3-opus")
            metadata: Metadados adicionais

        Returns:
            APIUsageRecord com custo calculado
        """
        logger.info(f"[ANALYTICS] Tracking API call: {agent_id} -> {api_endpoint}")

        # Calcula custo
        cost_per_call = self.api_pricing.get(api_endpoint, Decimal("0.001"))

        # Cria registro
        usage_record = APIUsageRecord(
            agent_id=agent_id,
            api_endpoint=api_endpoint,
            calls_count=1,
            timestamp=datetime.now(),
            cost_per_call=cost_per_call,
            total_cost=cost_per_call,
            metadata=metadata or {}
        )

        # Adiciona ao log
        self.api_usage_log[agent_id].append(usage_record)

        # Se custo >= threshold, cria micropagamento
        if usage_record.total_cost >= self.micropayment_threshold:
            self._create_api_payment(agent_id, usage_record)
        else:
            self._add_to_micropayment_batch(agent_id, usage_record)

        logger.info(f"   [COST] Cost: ${float(usage_record.total_cost):.4f}")

        return usage_record

    def get_api_usage_summary(
        self,
        agent_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retorna sumário de uso de API de um agente

        Args:
            agent_id: ID do agente
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)

        Returns:
            Sumário com total de calls, custos, etc.
        """
        usage_records = self.api_usage_log.get(agent_id, [])

        # Filtra por data se especificado
        if start_date or end_date:
            filtered_records = []
            for record in usage_records:
                if start_date and record.timestamp < start_date:
                    continue
                if end_date and record.timestamp > end_date:
                    continue
                filtered_records.append(record)
            usage_records = filtered_records

        # Agrega por endpoint
        by_endpoint = defaultdict(lambda: {"calls": 0, "cost": Decimal("0.0")})
        total_calls = 0
        total_cost = Decimal("0.0")

        for record in usage_records:
            by_endpoint[record.api_endpoint]["calls"] += record.calls_count
            by_endpoint[record.api_endpoint]["cost"] += record.total_cost
            total_calls += record.calls_count
            total_cost += record.total_cost

        return {
            "agent_id": agent_id,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "total_calls": total_calls,
            "total_cost": float(total_cost),
            "by_endpoint": {
                endpoint: {
                    "calls": data["calls"],
                    "cost": float(data["cost"]),
                    "avg_cost_per_call": float(data["cost"] / data["calls"])
                }
                for endpoint, data in by_endpoint.items()
            }
        }

    def _create_api_payment(self, agent_id: str, usage_record: APIUsageRecord):
        """Cria pagamento imediato para API call"""
        agent_state = self.syndicate.get_agent_state(agent_id)

        if not agent_state:
            logger.error(f"[ERROR] Agent {agent_id} não encontrado")
            return

        # Cria transação
        transaction = Transaction(
            tx_id=f"api-{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            tx_type=TransactionType.API_PAYMENT,
            amount=float(usage_record.total_cost),
            supplier=usage_record.api_endpoint,
            description=f"API call to {usage_record.api_endpoint}",
            metadata={
                "api_endpoint": usage_record.api_endpoint,
                "calls_count": usage_record.calls_count,
                "usage_record": usage_record.__dict__
            }
        )

        # Processa através do syndicate
        logger.info(f"[PAYMENT] Processing API payment: ${float(usage_record.total_cost):.4f}")
        evaluation = self.syndicate.process_transaction(transaction, agent_state)

        return evaluation

    # ====================
    # 2. MICROPAYMENTS
    # ====================

    def _add_to_micropayment_batch(self, agent_id: str, usage_record: APIUsageRecord):
        """Adiciona micropagamento a um batch para agregação"""

        # Encontra ou cria batch ativo
        batch_key = f"{agent_id}-active"

        if batch_key not in self.micropayment_batches:
            self.micropayment_batches[batch_key] = MicropaymentBatch(
                batch_id=f"batch-{uuid.uuid4().hex[:8]}",
                agent_id=agent_id
            )

        batch = self.micropayment_batches[batch_key]

        # Cria mini-transaction
        mini_tx = Transaction(
            tx_id=f"micro-{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            tx_type=TransactionType.MICROPAYMENT,
            amount=float(usage_record.total_cost),
            supplier=usage_record.api_endpoint,
            description=f"Micropayment for {usage_record.api_endpoint}",
            metadata={"usage_record_id": id(usage_record)}
        )

        batch.payments.append(mini_tx)
        batch.total_amount += usage_record.total_cost

        logger.info(f"[BATCH] Added to batch {batch.batch_id}: ${float(usage_record.total_cost):.4f}")
        logger.info(f"   Batch total: ${float(batch.total_amount):.4f}")

        # Se batch atingiu threshold ou timeout, executa
        if (batch.total_amount >= self.micropayment_threshold or
            datetime.now() - batch.created_at >= self.batch_timeout):
            self._execute_micropayment_batch(batch_key)

    def _execute_micropayment_batch(self, batch_key: str) -> Optional[TransactionEvaluation]:
        """Executa batch de micropagamentos agregados"""

        batch = self.micropayment_batches.get(batch_key)
        if not batch or batch.status != "pending":
            return None

        logger.info(f"\n{'='*60}")
        logger.info(f"[MICROPAYMENT] Executing micropayment batch: {batch.batch_id}")
        logger.info(f"   Agent: {batch.agent_id}")
        logger.info(f"   Payments: {len(batch.payments)}")
        logger.info(f"   Total: ${float(batch.total_amount):.4f}")
        logger.info(f"{'='*60}\n")

        agent_state = self.syndicate.get_agent_state(batch.agent_id)
        if not agent_state:
            logger.error(f"[ERROR] Agent {batch.agent_id} não encontrado")
            batch.status = "failed"
            return None

        # Cria transação agregada
        aggregated_tx = Transaction(
            tx_id=f"batch-{batch.batch_id}",
            agent_id=batch.agent_id,
            tx_type=TransactionType.MICROPAYMENT,
            amount=float(batch.total_amount),
            supplier="aggregated-micropayments",
            description=f"Batch of {len(batch.payments)} micropayments",
            metadata={
                "batch_id": batch.batch_id,
                "payment_count": len(batch.payments),
                "payments": [tx.to_dict() for tx in batch.payments]
            }
        )

        # Processa
        batch.status = "executing"
        evaluation = self.syndicate.process_transaction(aggregated_tx, agent_state)

        if evaluation.consensus == "APPROVED":
            batch.status = "completed"
            batch.executed_at = datetime.now()
            logger.info(f"[SUCCESS] Batch {batch.batch_id} executed successfully")
        else:
            batch.status = "failed"
            logger.error(f"[ERROR] Batch {batch.batch_id} failed")

        # Remove batch ativo
        del self.micropayment_batches[batch_key]

        return evaluation

    def get_pending_micropayments(self, agent_id: str) -> Optional[MicropaymentBatch]:
        """Retorna batch de micropagamentos pendentes de um agente"""
        batch_key = f"{agent_id}-active"
        return self.micropayment_batches.get(batch_key)

    # ====================
    # 3. AGENT-TO-AGENT PAYMENTS
    # ====================

    def transfer_between_agents(
        self,
        from_agent_id: str,
        to_agent_id: str,
        amount: Decimal,
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentToAgentPayment:
        """
        Transferência direta entre agentes

        Args:
            from_agent_id: Agente remetente
            to_agent_id: Agente destinatário
            amount: Valor a transferir
            purpose: Propósito da transferência
            metadata: Metadados adicionais

        Returns:
            AgentToAgentPayment com resultado
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[TRANSFER] Agent-to-Agent Transfer")
        logger.info(f"   From: {from_agent_id}")
        logger.info(f"   To: {to_agent_id}")
        logger.info(f"   Amount: ${float(amount):.2f}")
        logger.info(f"   Purpose: {purpose}")
        logger.info(f"{'='*60}\n")

        # Cria registro de pagamento
        payment = AgentToAgentPayment(
            payment_id=f"a2a-{uuid.uuid4().hex[:8]}",
            from_agent=from_agent_id,
            to_agent=to_agent_id,
            amount=amount,
            purpose=purpose,
            metadata=metadata or {}
        )

        # Valida agentes
        from_state = self.syndicate.get_agent_state(from_agent_id)
        to_state = self.syndicate.get_agent_state(to_agent_id)

        if not from_state:
            logger.error(f"[ERROR] From agent {from_agent_id} não encontrado")
            payment.status = "failed"
            payment.metadata["error"] = "from_agent_not_found"
            return payment

        if not to_state:
            logger.error(f"[ERROR] To agent {to_agent_id} não encontrado")
            payment.status = "failed"
            payment.metadata["error"] = "to_agent_not_found"
            return payment

        # Verifica saldo
        if from_state.available_balance < float(amount):
            logger.error(f"[ERROR] Insufficient balance: ${from_state.available_balance:.2f} < ${float(amount):.2f}")
            payment.status = "failed"
            payment.metadata["error"] = "insufficient_balance"
            return payment

        # Cria transação
        transaction = Transaction(
            tx_id=payment.payment_id,
            agent_id=from_agent_id,
            tx_type=TransactionType.AGENT_TO_AGENT,
            amount=float(amount),
            supplier=to_agent_id,
            description=f"Transfer to {to_agent_id}: {purpose}",
            metadata={
                "to_agent": to_agent_id,
                "purpose": purpose,
                "payment_metadata": payment.metadata
            }
        )

        # Processa transação
        payment.status = "processing"
        evaluation = self.syndicate.process_transaction(transaction, from_state)

        if evaluation.consensus == "APPROVED":
            # Atualiza saldo do destinatário
            to_state.available_balance += float(amount)
            to_state.total_earned += float(amount)

            payment.status = "completed"
            payment.metadata["tx_hash"] = transaction.tx_hash
            payment.metadata["evaluation"] = evaluation.to_dict()

            logger.info(f"[SUCCESS] Transfer completed: {payment.payment_id}")
            logger.info(f"   TX Hash: {transaction.tx_hash}")
        else:
            payment.status = "failed"
            payment.metadata["error"] = "transaction_rejected"
            payment.metadata["blockers"] = [b.to_dict() for b in evaluation.blockers]
            logger.error(f"[ERROR] Transfer failed: {payment.payment_id}")

        self.agent_payments.append(payment)
        return payment

    def get_agent_payment_history(
        self,
        agent_id: str,
        direction: str = "both"  # "sent", "received", "both"
    ) -> List[AgentToAgentPayment]:
        """
        Retorna histórico de pagamentos agent-to-agent

        Args:
            agent_id: ID do agente
            direction: "sent", "received" ou "both"

        Returns:
            Lista de AgentToAgentPayment
        """
        payments = []

        for payment in self.agent_payments:
            if direction == "sent" and payment.from_agent == agent_id:
                payments.append(payment)
            elif direction == "received" and payment.to_agent == agent_id:
                payments.append(payment)
            elif direction == "both" and (payment.from_agent == agent_id or payment.to_agent == agent_id):
                payments.append(payment)

        return sorted(payments, key=lambda p: p.timestamp, reverse=True)

    # ====================
    # 4. AUTONOMOUS CONSENSUS
    # ====================

    def request_autonomous_approval(
        self,
        transaction: Transaction,
        voting_agents: List[str],
        timeout_seconds: int = 30
    ) -> Tuple[bool, List[ConsensusVote]]:
        """
        Solicita aprovação autônoma via consenso multi-agent

        Args:
            transaction: Transação a ser aprovada
            voting_agents: Lista de agent_ids que devem votar
            timeout_seconds: Timeout para votação

        Returns:
            (approved: bool, votes: List[ConsensusVote])
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[VOTE]  Requesting Autonomous Approval")
        logger.info(f"   Transaction: {transaction.tx_id}")
        logger.info(f"   Amount: ${transaction.amount:.2f}")
        logger.info(f"   Voting agents: {len(voting_agents)}")
        logger.info(f"   Consensus threshold: {self.consensus_threshold * 100}%")
        logger.info(f"{'='*60}\n")

        consensus_id = f"consensus-{transaction.tx_id}"
        start_time = time.time()

        # Coleta votos (simulado - em produção seria async)
        votes = []
        for voter_id in voting_agents:
            # Simula análise do agente
            vote = self._simulate_agent_vote(voter_id, transaction)
            votes.append(vote)
            self.consensus_votes[consensus_id].append(vote)

            logger.info(f"   [VOTE]  {voter_id}: {vote.vote.upper()} (confidence: {vote.confidence:.2f})")
            logger.info(f"      Reasoning: {vote.reasoning}")

            # Check timeout
            if time.time() - start_time > timeout_seconds:
                logger.warning(f"[WARNING]  Consensus timeout reached")
                break

        # Calcula consenso
        total_votes = len(votes)
        approve_votes = sum(1 for v in votes if v.vote == "approve")
        approval_rate = approve_votes / total_votes if total_votes > 0 else 0.0

        approved = approval_rate >= self.consensus_threshold

        logger.info(f"\n{'='*60}")
        logger.info(f"[ANALYTICS] Consensus Result")
        logger.info(f"   Approve: {approve_votes}/{total_votes} ({approval_rate * 100:.1f}%)")
        logger.info(f"   Decision: {'[SUCCESS] APPROVED' if approved else '[ERROR] REJECTED'}")
        logger.info(f"{'='*60}\n")

        return approved, votes

    def _simulate_agent_vote(self, voter_id: str, transaction: Transaction) -> ConsensusVote:
        """
        Simula voto de um agente (em produção chamaria o agente real)

        Args:
            voter_id: ID do agente votante
            transaction: Transação a avaliar

        Returns:
            ConsensusVote
        """
        # Simula análise baseada em heurísticas simples
        confidence = 0.8
        vote = "approve"
        reasoning = "Transaction appears legitimate"

        # Heurísticas simples
        if transaction.amount > 1000:
            confidence -= 0.2
            reasoning = "High amount requires caution"

        if transaction.amount < 0.01:
            vote = "reject"
            confidence = 0.9
            reasoning = "Amount too low, possible spam"

        # Varia baseado no voter_id (simulando diferentes "personalidades")
        if "conservative" in voter_id.lower():
            confidence -= 0.1
            if transaction.amount > 500:
                vote = "reject"
                reasoning = "Conservative policy: amount too high"

        return ConsensusVote(
            voter_agent_id=voter_id,
            vote=vote,
            confidence=confidence,
            reasoning=reasoning
        )

    # ====================
    # 5. BILLING & REPORTING
    # ====================

    def process_usage_billing(
        self,
        agent_id: str,
        force: bool = False
    ) -> Optional[Transaction]:
        """
        Processa billing de uso acumulado para um agente

        Args:
            agent_id: ID do agente
            force: Força billing mesmo fora do ciclo

        Returns:
            Transaction de billing ou None se não houver cobrança
        """
        logger.info(f"[PAYMENT] Processing usage billing for {agent_id}")

        # Verifica último billing
        last_billing = self.last_billing.get(agent_id)
        if not force and last_billing:
            time_since_last = datetime.now() - last_billing
            if time_since_last < self.billing_cycle:
                logger.info(f"   [SKIP]  Skipping: billing cycle not reached")
                logger.info(f"      Time since last: {time_since_last}")
                logger.info(f"      Cycle: {self.billing_cycle}")
                return None

        # Calcula uso total desde último billing
        usage_summary = self.get_api_usage_summary(
            agent_id,
            start_date=last_billing
        )

        total_cost = Decimal(str(usage_summary["total_cost"]))

        if total_cost == 0:
            logger.info(f"   [SUCCESS] No usage to bill")
            return None

        logger.info(f"   [ANALYTICS] Total usage: ${float(total_cost):.4f}")
        logger.info(f"   [CALLS] API calls: {usage_summary['total_calls']}")

        agent_state = self.syndicate.get_agent_state(agent_id)
        if not agent_state:
            logger.error(f"[ERROR] Agent {agent_id} não encontrado")
            return None

        # Cria transação de billing
        transaction = Transaction(
            tx_id=f"billing-{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            tx_type=TransactionType.USAGE_BILLING,
            amount=float(total_cost),
            supplier="agentic-commerce-billing",
            description=f"API usage billing: {usage_summary['total_calls']} calls",
            metadata={
                "usage_summary": usage_summary,
                "billing_period_start": last_billing.isoformat() if last_billing else None,
                "billing_period_end": datetime.now().isoformat()
            }
        )

        # Processa
        evaluation = self.syndicate.process_transaction(transaction, agent_state)

        if evaluation.consensus == "APPROVED":
            self.last_billing[agent_id] = datetime.now()
            logger.info(f"[SUCCESS] Billing processed successfully")
        else:
            logger.error(f"[ERROR] Billing failed")

        return transaction

    def get_commerce_summary(self, agent_id: str) -> Dict[str, Any]:
        """
        Retorna sumário completo de agentic commerce para um agente

        Args:
            agent_id: ID do agente

        Returns:
            Sumário com todas as métricas
        """
        api_usage = self.get_api_usage_summary(agent_id)
        pending_batch = self.get_pending_micropayments(agent_id)
        payment_history = self.get_agent_payment_history(agent_id)

        sent_payments = [p for p in payment_history if p.from_agent == agent_id]
        received_payments = [p for p in payment_history if p.to_agent == agent_id]

        sent_total = sum(float(p.amount) for p in sent_payments if p.status == "completed")
        received_total = sum(float(p.amount) for p in received_payments if p.status == "completed")

        return {
            "agent_id": agent_id,
            "api_usage": api_usage,
            "micropayments": {
                "pending_batch": {
                    "batch_id": pending_batch.batch_id if pending_batch else None,
                    "payment_count": len(pending_batch.payments) if pending_batch else 0,
                    "total_amount": float(pending_batch.total_amount) if pending_batch else 0.0
                } if pending_batch else None
            },
            "agent_to_agent_payments": {
                "sent": {
                    "count": len(sent_payments),
                    "total": sent_total
                },
                "received": {
                    "count": len(received_payments),
                    "total": received_total
                },
                "net": received_total - sent_total
            },
            "last_billing": self.last_billing.get(agent_id, datetime.min).isoformat()
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Retorna métricas gerais do sistema de agentic commerce"""
        total_api_calls = sum(
            len(records) for records in self.api_usage_log.values()
        )

        total_api_cost = sum(
            sum(float(record.total_cost) for record in records)
            for records in self.api_usage_log.values()
        )

        active_batches = sum(
            1 for batch in self.micropayment_batches.values()
            if batch.status == "pending"
        )

        total_a2a_payments = len(self.agent_payments)
        completed_a2a = sum(1 for p in self.agent_payments if p.status == "completed")

        return {
            "api_tracking": {
                "total_calls": total_api_calls,
                "total_cost": total_api_cost,
                "unique_agents": len(self.api_usage_log),
                "tracked_endpoints": len(self.api_pricing)
            },
            "micropayments": {
                "active_batches": active_batches,
                "threshold": float(self.micropayment_threshold),
                "batch_timeout_minutes": self.batch_timeout.total_seconds() / 60
            },
            "agent_to_agent": {
                "total_payments": total_a2a_payments,
                "completed": completed_a2a,
                "failed": total_a2a_payments - completed_a2a
            },
            "consensus": {
                "threshold": self.consensus_threshold,
                "total_consensus_requests": len(self.consensus_votes)
            }
        }


# ====================
# CONVENIENCE FUNCTIONS
# ====================

def create_agentic_commerce_system(
    syndicate: Optional[BankingSyndicate] = None
) -> AgenticCommerce:
    """Factory function para criar sistema de agentic commerce"""
    return AgenticCommerce(syndicate=syndicate)


def demo_agentic_commerce():
    """Demonstração do sistema de agentic commerce"""
    logger.info("\n" + "="*80)
    logger.info("[AGENT] AGENTIC COMMERCE DEMO")
    logger.info("="*80 + "\n")

    # Inicializa sistema
    commerce = create_agentic_commerce_system()

    # Onboard agentes
    logger.info("[STEP] Step 1: Onboarding agents...")
    agent1_result = commerce.syndicate.onboard_agent("ai-agent-001", initial_deposit=500.0)
    agent2_result = commerce.syndicate.onboard_agent("ai-agent-002", initial_deposit=300.0)
    logger.info(f"   [SUCCESS] Agent 1: {agent1_result['agent_id']}")
    logger.info(f"   [SUCCESS] Agent 2: {agent2_result['agent_id']}")

    # Test API tracking
    logger.info("\n[STEP] Step 2: Tracking API usage...")
    commerce.track_api_call("ai-agent-001", "gpt-4")
    commerce.track_api_call("ai-agent-001", "claude-3-sonnet")
    commerce.track_api_call("ai-agent-001", "gemini-pro")

    # Test micropayments
    logger.info("\n[STEP] Step 3: Accumulating micropayments...")
    for i in range(5):
        commerce.track_api_call("ai-agent-002", "gemini-pro")

    # Test agent-to-agent payment
    logger.info("\n[STEP] Step 4: Agent-to-agent transfer...")
    commerce.transfer_between_agents(
        from_agent_id="ai-agent-001",
        to_agent_id="ai-agent-002",
        amount=Decimal("50.0"),
        purpose="Payment for service"
    )

    # Test usage billing
    logger.info("\n[STEP] Step 5: Processing usage billing...")
    commerce.process_usage_billing("ai-agent-001", force=True)

    # System metrics
    logger.info("\n[STEP] Step 6: System metrics...")
    metrics = commerce.get_system_metrics()
    logger.info(f"   [ANALYTICS] Total API calls: {metrics['api_tracking']['total_calls']}")
    logger.info(f"   [COST] Total API cost: ${metrics['api_tracking']['total_cost']:.4f}")
    logger.info(f"   [TRANSFER] A2A payments: {metrics['agent_to_agent']['total_payments']}")

    logger.info("\n" + "="*80)
    logger.info("[SUCCESS] DEMO COMPLETED")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    demo_agentic_commerce()
