"""
Arc Hackathon Demo: Agentic Commerce on Arc Blockchain
=======================================================

Demonstrates:
- AI agents with Circle Wallets
- Autonomous USDC payments for API calls
- Multi-agent consensus on transactions
- Usage-based payment flows
- Transactions settling on Arc blockchain
- Gemini AI analyzing and optimizing payments

Requirements:
- Circle API credentials
- Arc blockchain RPC endpoint
- Gemini API key
"""

# Fix Windows console encoding for Unicode characters
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

# Mock imports for demo (replace with actual SDKs in production)
try:
    import google.generativeai as genai
except ImportError:
    print("[WARNING]  Gemini AI not available. Install with: pip install google-generativeai")
    genai = None

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Demo configuration"""
    # Circle API (sandbox for demo)
    CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY", "TEST_API_KEY")
    CIRCLE_ENTITY_SECRET = os.getenv("CIRCLE_ENTITY_SECRET", "TEST_SECRET")

    # Arc Blockchain
    ARC_RPC_URL = os.getenv("ARC_RPC_URL", "https://rpc.arc.testnet.io")
    ARC_EXPLORER_URL = "https://explorer.arc.testnet.io"
    ARC_CHAIN_ID = 42069  # Arc testnet chain ID

    # Gemini AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Demo settings
    USDC_DECIMALS = 6
    API_CALL_COST = 0.01  # $0.01 per API call
    CONSENSUS_THRESHOLD = 0.66  # 66% agreement required

# ============================================================================
# DATA MODELS
# ============================================================================

class AgentRole(Enum):
    """Agent roles in the system"""
    API_PROVIDER = "API Provider"
    API_CONSUMER = "API Consumer"
    PAYMENT_VALIDATOR = "Payment Validator"
    ANALYTICS_ENGINE = "Analytics Engine"

class TransactionStatus(Enum):
    """Transaction lifecycle states"""
    PENDING = "pending"
    CONSENSUS_VOTING = "consensus_voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"
    FAILED = "failed"

@dataclass
class Wallet:
    """Circle Wallet representation"""
    wallet_id: str
    address: str
    agent_name: str
    balance_usdc: float
    created_at: str

@dataclass
class Transaction:
    """Transaction record"""
    tx_id: str
    from_wallet: str
    to_wallet: str
    amount_usdc: float
    purpose: str
    status: TransactionStatus
    arc_tx_hash: Optional[str] = None
    timestamp: str = None
    consensus_votes: Dict[str, bool] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.consensus_votes is None:
            self.consensus_votes = {}

@dataclass
class APICall:
    """API call record"""
    call_id: str
    provider_agent: str
    consumer_agent: str
    endpoint: str
    cost_usdc: float
    timestamp: str
    payment_tx_id: Optional[str] = None

# ============================================================================
# CIRCLE WALLET MANAGER (Simulated)
# ============================================================================

class CircleWalletManager:
    """
    Manages Circle Wallets for AI agents
    In production, this would use the actual Circle API
    """

    def __init__(self):
        self.wallets: Dict[str, Wallet] = {}
        self.transactions: List[Transaction] = []

    async def create_wallet(self, agent_name: str, initial_balance: float = 100.0) -> Wallet:
        """Create a new Circle Wallet for an agent"""
        wallet_id = f"wallet_{uuid.uuid4().hex[:8]}"
        # In production, this would be the actual blockchain address
        address = f"0x{uuid.uuid4().hex[:40]}"

        wallet = Wallet(
            wallet_id=wallet_id,
            address=address,
            agent_name=agent_name,
            balance_usdc=initial_balance,
            created_at=datetime.now().isoformat()
        )

        self.wallets[wallet_id] = wallet

        print(f"  ✓ Created wallet for {agent_name}")
        print(f"    Wallet ID: {wallet_id}")
        print(f"    Address: {address}")
        print(f"    Initial Balance: ${initial_balance:.2f} USDC")

        await asyncio.sleep(0.5)  # Simulate API call
        return wallet

    async def transfer_usdc(
        self,
        from_wallet_id: str,
        to_wallet_id: str,
        amount: float,
        purpose: str
    ) -> Transaction:
        """Transfer USDC between wallets"""
        tx_id = f"tx_{uuid.uuid4().hex[:8]}"

        transaction = Transaction(
            tx_id=tx_id,
            from_wallet=from_wallet_id,
            to_wallet=to_wallet_id,
            amount_usdc=amount,
            purpose=purpose,
            status=TransactionStatus.PENDING
        )

        self.transactions.append(transaction)
        return transaction

    async def settle_on_arc(self, transaction: Transaction) -> str:
        """
        Settle transaction on Arc blockchain
        In production, this would interact with Arc blockchain
        """
        # Simulate Arc blockchain transaction
        arc_tx_hash = f"0xarc{uuid.uuid4().hex[:60]}"
        transaction.arc_tx_hash = arc_tx_hash
        transaction.status = TransactionStatus.SETTLED

        # Update balances
        from_wallet = self.wallets[transaction.from_wallet]
        to_wallet = self.wallets[transaction.to_wallet]

        from_wallet.balance_usdc -= transaction.amount_usdc
        to_wallet.balance_usdc += transaction.amount_usdc

        await asyncio.sleep(1.0)  # Simulate block confirmation
        return arc_tx_hash

    def get_wallet(self, wallet_id: str) -> Wallet:
        """Get wallet by ID"""
        return self.wallets.get(wallet_id)

    def get_balance(self, wallet_id: str) -> float:
        """Get wallet balance"""
        wallet = self.wallets.get(wallet_id)
        return wallet.balance_usdc if wallet else 0.0

# ============================================================================
# AI AGENT
# ============================================================================

class AIAgent:
    """
    Autonomous AI Agent with Circle Wallet
    Can make payments, call APIs, and participate in consensus
    """

    def __init__(
        self,
        name: str,
        role: AgentRole,
        wallet_manager: CircleWalletManager,
        wallet_id: str
    ):
        self.name = name
        self.role = role
        self.wallet_manager = wallet_manager
        self.wallet_id = wallet_id
        self.api_calls_made: List[APICall] = []

    async def call_api(
        self,
        provider_agent: 'AIAgent',
        endpoint: str,
        auto_pay: bool = True
    ) -> APICall:
        """Call an API and automatically pay for it"""
        call_id = f"api_{uuid.uuid4().hex[:8]}"
        cost = Config.API_CALL_COST

        api_call = APICall(
            call_id=call_id,
            provider_agent=provider_agent.name,
            consumer_agent=self.name,
            endpoint=endpoint,
            cost_usdc=cost,
            timestamp=datetime.now().isoformat()
        )

        print(f"\n  [CALLS] {self.name} calling API: {endpoint}")
        print(f"     Provider: {provider_agent.name}")
        print(f"     Cost: ${cost:.4f} USDC")

        if auto_pay:
            # Automatically pay for the API call
            payment_tx = await self.wallet_manager.transfer_usdc(
                from_wallet_id=self.wallet_id,
                to_wallet_id=provider_agent.wallet_id,
                amount=cost,
                purpose=f"Payment for API call: {endpoint}"
            )
            api_call.payment_tx_id = payment_tx.tx_id
            print(f"     [CARD] Payment initiated: {payment_tx.tx_id}")

        self.api_calls_made.append(api_call)
        await asyncio.sleep(0.3)

        return api_call

    async def vote_on_transaction(self, transaction: Transaction) -> bool:
        """
        Vote on whether to approve a transaction
        Uses simple heuristics (in production, would use AI)
        """
        # Simple validation rules
        wallet = self.wallet_manager.get_wallet(transaction.from_wallet)

        # Check if sender has sufficient balance
        if wallet.balance_usdc < transaction.amount_usdc:
            print(f"  [ERROR] {self.name} REJECTS: Insufficient balance")
            return False

        # Check if amount is reasonable
        if transaction.amount_usdc > 10.0:
            print(f"  [WARNING]  {self.name} REJECTS: Amount too high (${transaction.amount_usdc:.2f})")
            return False

        # Approve
        print(f"  [OK] {self.name} APPROVES transaction")
        return True

    def get_spending_stats(self) -> Dict:
        """Get spending statistics"""
        total_spent = sum(
            call.cost_usdc for call in self.api_calls_made
        )
        return {
            "agent": self.name,
            "total_api_calls": len(self.api_calls_made),
            "total_spent_usdc": total_spent,
            "average_cost": total_spent / len(self.api_calls_made) if self.api_calls_made else 0
        }

# ============================================================================
# MULTI-AGENT CONSENSUS SYSTEM
# ============================================================================

class ConsensusEngine:
    """
    Multi-agent consensus system for transaction approval
    Uses voting mechanism to approve/reject transactions
    """

    def __init__(self, validator_agents: List[AIAgent]):
        self.validator_agents = validator_agents

    async def reach_consensus(self, transaction: Transaction) -> bool:
        """
        Get consensus from validator agents
        Returns True if consensus threshold is met
        """
        print(f"\n[VOTE]  CONSENSUS VOTING for transaction {transaction.tx_id}")
        print(f"   Amount: ${transaction.amount_usdc:.4f} USDC")
        print(f"   Purpose: {transaction.purpose}")
        print(f"   Validators: {len(self.validator_agents)}")

        transaction.status = TransactionStatus.CONSENSUS_VOTING

        # Collect votes from all validators
        votes = []
        for agent in self.validator_agents:
            vote = await agent.vote_on_transaction(transaction)
            votes.append(vote)
            transaction.consensus_votes[agent.name] = vote
            await asyncio.sleep(0.2)

        # Calculate consensus
        approval_rate = sum(votes) / len(votes)
        consensus_reached = approval_rate >= Config.CONSENSUS_THRESHOLD

        print(f"\n   [ANALYTICS] Voting Results:")
        print(f"      Approvals: {sum(votes)}/{len(votes)}")
        print(f"      Approval Rate: {approval_rate*100:.1f}%")
        print(f"      Threshold: {Config.CONSENSUS_THRESHOLD*100:.1f}%")

        if consensus_reached:
            transaction.status = TransactionStatus.APPROVED
            print(f"   [SUCCESS] CONSENSUS REACHED - Transaction approved")
        else:
            transaction.status = TransactionStatus.REJECTED
            print(f"   [ERROR] CONSENSUS FAILED - Transaction rejected")

        return consensus_reached

# ============================================================================
# GEMINI AI ANALYTICS
# ============================================================================

class GeminiAnalytics:
    """
    Uses Gemini AI to analyze payment patterns and optimize costs
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.enabled = bool(self.api_key and genai)

        if self.enabled:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    async def analyze_spending_patterns(
        self,
        agents: List[AIAgent],
        transactions: List[Transaction]
    ) -> str:
        """
        Analyze spending patterns and provide optimization recommendations
        """
        if not self.enabled:
            return self._mock_analysis(agents, transactions)

        # Prepare data for analysis
        agent_stats = [agent.get_spending_stats() for agent in agents]

        prompt = f"""
        Analyze the following AI agent spending patterns on API calls:

        Agents: {json.dumps(agent_stats, indent=2)}

        Total Transactions: {len(transactions)}

        Provide:
        1. Key spending insights
        2. Cost optimization opportunities
        3. Risk assessment
        4. Recommendations for better payment flows

        Keep response concise (max 200 words).
        """

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text
        except Exception as e:
            return f"Analysis error: {str(e)}\n\n" + self._mock_analysis(agents, transactions)

    def _mock_analysis(self, agents: List[AIAgent], transactions: List[Transaction]) -> str:
        """Mock analysis when Gemini is not available"""
        total_spent = sum(
            sum(call.cost_usdc for call in agent.api_calls_made)
            for agent in agents
        )

        return f"""
[AGENT] AI Analysis (Mock Mode - Enable Gemini for real analysis):

[ANALYTICS] Key Insights:
• Total agents: {len(agents)}
• Total API calls: {sum(len(a.api_calls_made) for a in agents)}
• Total spent: ${total_spent:.4f} USDC
• Average cost per call: ${Config.API_CALL_COST:.4f} USDC

[INFO] Optimization Opportunities:
• Implement batch API calls to reduce transaction fees
• Use caching to minimize redundant calls
• Consider volume discounts for high-frequency agents

[WARNING] Risk Assessment: LOW
• All transactions within normal parameters
• No suspicious spending patterns detected

[SUCCESS] Recommendations:
• Continue current payment flow
• Monitor for cost anomalies
• Consider implementing spending limits per agent
"""

# ============================================================================
# DEMO ORCHESTRATOR
# ============================================================================

class DemoOrchestrator:
    """Main demo orchestration"""

    def __init__(self):
        self.wallet_manager = CircleWalletManager()
        self.agents: List[AIAgent] = []
        self.consensus_engine: Optional[ConsensusEngine] = None
        self.analytics = GeminiAnalytics()

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)

    def print_section(self, title: str):
        """Print formatted section"""
        print(f"\n{'─'*80}")
        print(f"  {title}")
        print(f"{'─'*80}")

    async def setup_agents(self):
        """Create AI agents with Circle Wallets"""
        self.print_section("[AGENT] Setting Up AI Agents with Circle Wallets")

        agent_configs = [
            ("DataAPI-Agent", AgentRole.API_PROVIDER, 500.0),
            ("ResearchBot-Alpha", AgentRole.API_CONSUMER, 100.0),
            ("AnalyticsBot-Beta", AgentRole.API_CONSUMER, 100.0),
            ("Validator-Node-1", AgentRole.PAYMENT_VALIDATOR, 50.0),
            ("Validator-Node-2", AgentRole.PAYMENT_VALIDATOR, 50.0),
            ("Validator-Node-3", AgentRole.PAYMENT_VALIDATOR, 50.0),
        ]

        for name, role, initial_balance in agent_configs:
            wallet = await self.wallet_manager.create_wallet(name, initial_balance)
            agent = AIAgent(name, role, self.wallet_manager, wallet.wallet_id)
            self.agents.append(agent)
            await asyncio.sleep(0.3)

        # Set up consensus engine with validator agents
        validators = [a for a in self.agents if a.role == AgentRole.PAYMENT_VALIDATOR]
        self.consensus_engine = ConsensusEngine(validators)

        print(f"\n[SUCCESS] Created {len(self.agents)} agents")
        print(f"   • API Providers: {len([a for a in self.agents if a.role == AgentRole.API_PROVIDER])}")
        print(f"   • API Consumers: {len([a for a in self.agents if a.role == AgentRole.API_CONSUMER])}")
        print(f"   • Validators: {len(validators)}")

    async def demo_api_payments(self):
        """Demonstrate autonomous API payments"""
        self.print_section("[CARD] Autonomous API Payments")

        # Get agents
        provider = next(a for a in self.agents if a.role == AgentRole.API_PROVIDER)
        consumer1 = self.agents[1]
        consumer2 = self.agents[2]

        print(f"\n[TARGET] Scenario: Agents automatically pay for API calls")

        # Consumer 1 makes API calls
        await consumer1.call_api(provider, "/api/v1/market-data", auto_pay=True)
        await consumer1.call_api(provider, "/api/v1/sentiment-analysis", auto_pay=True)

        # Consumer 2 makes API calls
        await consumer2.call_api(provider, "/api/v1/predictive-analytics", auto_pay=True)

        print(f"\n[SUCCESS] All payments processed automatically")

    async def demo_multi_agent_consensus(self):
        """Demonstrate multi-agent consensus on large transaction"""
        self.print_section("[VOTE]  Multi-Agent Consensus System")

        consumer = self.agents[1]
        provider = self.agents[0]

        print(f"\n[TARGET] Scenario: Large transaction requires consensus approval")

        # Create a larger transaction that needs consensus
        large_payment = await self.wallet_manager.transfer_usdc(
            from_wallet_id=consumer.wallet_id,
            to_wallet_id=provider.wallet_id,
            amount=5.0,
            purpose="Bulk API access subscription"
        )

        # Get consensus
        approved = await self.consensus_engine.reach_consensus(large_payment)

        if approved:
            # Settle on Arc blockchain
            print(f"\n[BLOCKCHAIN] Settling transaction on Arc blockchain...")
            arc_tx_hash = await self.wallet_manager.settle_on_arc(large_payment)

            explorer_url = f"{Config.ARC_EXPLORER_URL}/tx/{arc_tx_hash}"
            print(f"\n[SUCCESS] Transaction settled on Arc!")
            print(f"   Tx Hash: {arc_tx_hash}")
            print(f"   Explorer: {explorer_url}")

    async def settle_all_transactions(self):
        """Settle all pending transactions on Arc blockchain"""
        self.print_section("[BLOCKCHAIN] Settling Transactions on Arc Blockchain")

        pending = [
            tx for tx in self.wallet_manager.transactions
            if tx.status == TransactionStatus.PENDING
        ]

        print(f"\n[BATCH] Settling {len(pending)} pending transactions...")

        for i, tx in enumerate(pending, 1):
            print(f"\n  [{i}/{len(pending)}] Settling {tx.tx_id}...")

            # Auto-approve small transactions
            tx.status = TransactionStatus.APPROVED

            # Settle on Arc
            arc_tx_hash = await self.wallet_manager.settle_on_arc(tx)
            explorer_url = f"{Config.ARC_EXPLORER_URL}/tx/{arc_tx_hash}"

            print(f"      [OK] Settled: {arc_tx_hash[:20]}...")
            print(f"      [LINK] {explorer_url}")

            await asyncio.sleep(0.5)

        print(f"\n[SUCCESS] All transactions settled on Arc blockchain")

    async def demo_gemini_analytics(self):
        """Demonstrate Gemini AI analytics"""
        self.print_section("[AI] Gemini AI Payment Analytics")

        print(f"\n[TARGET] Analyzing spending patterns with Gemini AI...\n")

        analysis = await self.analytics.analyze_spending_patterns(
            self.agents,
            self.wallet_manager.transactions
        )

        print(analysis)

    def print_final_summary(self):
        """Print final demo summary"""
        self.print_section("[ANALYTICS] Final Summary")

        # Agent balances
        print(f"\n[TREASURY] Agent Wallet Balances:")
        for agent in self.agents:
            wallet = self.wallet_manager.get_wallet(agent.wallet_id)
            stats = agent.get_spending_stats()
            print(f"   • {agent.name:25} ${wallet.balance_usdc:8.2f} USDC")
            if stats['total_api_calls'] > 0:
                print(f"     └─ API calls: {stats['total_api_calls']}, Spent: ${stats['total_spent_usdc']:.4f}")

        # Transaction summary
        total_transactions = len(self.wallet_manager.transactions)
        settled = len([t for t in self.wallet_manager.transactions if t.status == TransactionStatus.SETTLED])
        total_volume = sum(t.amount_usdc for t in self.wallet_manager.transactions)

        print(f"\n[GROWTH] Transaction Statistics:")
        print(f"   • Total Transactions: {total_transactions}")
        print(f"   • Settled on Arc: {settled}")
        print(f"   • Total Volume: ${total_volume:.4f} USDC")

        # Arc Explorer links
        print(f"\n[LINK] Arc Blockchain Explorer:")
        for tx in self.wallet_manager.transactions[:5]:  # Show first 5
            if tx.arc_tx_hash:
                url = f"{Config.ARC_EXPLORER_URL}/tx/{tx.arc_tx_hash}"
                print(f"   • {tx.tx_id}: {url}")

    async def run_demo(self):
        """Run complete demo"""
        self.print_header("[LAUNCH] Arc Hackathon Demo: Agentic Commerce")

        print(f"""
[STEP] Demo Overview:
   • Create AI agents with Circle Wallets
   • Agents autonomously pay for API calls in USDC
   • Multi-agent consensus approves transactions
   • All transactions settle on Arc blockchain
   • Gemini AI analyzes and optimizes payments

[TOOL] Configuration:
   • Arc RPC: {Config.ARC_RPC_URL}
   • Arc Explorer: {Config.ARC_EXPLORER_URL}
   • Chain ID: {Config.ARC_CHAIN_ID}
   • Consensus Threshold: {Config.CONSENSUS_THRESHOLD*100:.0f}%
        """)

        input("\nPress Enter to start demo...")

        try:
            # Step 1: Setup agents with wallets
            await self.setup_agents()
            await asyncio.sleep(1)

            # Step 2: Demonstrate autonomous payments
            await self.demo_api_payments()
            await asyncio.sleep(1)

            # Step 3: Demonstrate consensus system
            await self.demo_multi_agent_consensus()
            await asyncio.sleep(1)

            # Step 4: Settle remaining transactions
            await self.settle_all_transactions()
            await asyncio.sleep(1)

            # Step 5: AI Analytics
            await self.demo_gemini_analytics()
            await asyncio.sleep(1)

            # Final summary
            self.print_final_summary()

            self.print_header("[SUCCESS] Demo Complete!")
            print("""
[SUCCESS] Successfully demonstrated:
   [OK] AI agents with Circle Wallets
   [OK] Autonomous USDC payments for API calls
   [OK] Multi-agent consensus on transactions
   [OK] Transaction settlement on Arc blockchain
   [OK] Gemini AI payment analytics

[INFO] Next Steps:
   • Integrate real Circle API credentials
   • Connect to Arc blockchain mainnet
   • Deploy agents to production
   • Scale to thousands of autonomous agents

[LINK] Resources:
   • Circle Wallet API: https://developers.circle.com
   • Arc Blockchain: https://arc.io
   • Gemini AI: https://ai.google.dev
            """)

        except KeyboardInterrupt:
            print("\n\n[WARNING]  Demo interrupted by user")
        except Exception as e:
            print(f"\n\n[ERROR] Demo error: {str(e)}")
            import traceback
            traceback.print_exc()

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Main entry point"""
    demo = DemoOrchestrator()
    await demo.run_demo()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ARC HACKATHON DEMO - AGENTIC COMMERCE")
    print("  Powered by Circle Wallets + Arc Blockchain + Gemini AI")
    print("="*80)

    # Check dependencies
    missing_deps = []

    try:
        import google.generativeai
    except ImportError:
        missing_deps.append("google-generativeai")

    if missing_deps:
        print(f"\n[WARNING]  Optional dependencies missing: {', '.join(missing_deps)}")
        print("   Install with: pip install " + " ".join(missing_deps))
        print("   (Demo will run in mock mode)\n")

    # Run demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[WAVE] Demo terminated")
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
