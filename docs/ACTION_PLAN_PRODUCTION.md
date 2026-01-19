# ACTION PLAN: MVP to Production Bank
## Practical Steps to Transform BaaS Arc into a Real Bank

**Date**: January 19, 2026
**Timeline**: 12 months to production
**Budget Required**: $1.5M - $4M

---

## EXECUTIVE DECISION: Choose Your Path

### Path A: Full Banking License
- **Timeline**: 18-24 months
- **Capital Required**: $50M minimum
- **Best For**: Long-term vision, full control
- **Risk**: Long approval process, uncertain outcome

### Path B: Bank Partnership (RECOMMENDED)
- **Timeline**: 6-9 months
- **Capital Required**: $5M-$10M
- **Best For**: Faster time to market
- **Partners**: Cross River Bank, Blue Ridge Bank, Evolve Bank

### Path C: Money Transmitter Only
- **Timeline**: 6-12 months
- **Capital Required**: $1M-$5M
- **Best For**: Start small, limited services
- **Limitation**: Cannot take deposits, limited banking features

**RECOMMENDATION**: Start with Path B (Partnership), build towards Path A

---

## MONTH 1: CRITICAL FIXES

### Week 1-2: Database Migration (HIGHEST PRIORITY)
**Current Issue**: Using JSON files for storage - UNACCEPTABLE for banking

**Action Items:**
```bash
# 1. Set up PostgreSQL production instance
docker run -d \
  --name baas-postgres \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=baas_production \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# 2. Create database schema
psql -h localhost -U postgres -d baas_production -f banking/core/schema.sql

# 3. Implement SQLAlchemy models (replace JSON storage)
```

**Files to Create:**
```
banking/
├── core/
│   ├── models.py              # SQLAlchemy models
│   ├── database.py            # Connection pool
│   └── migrations/            # Alembic migrations
│       └── 001_initial_schema.sql
```

**Code Template:**
```python
# banking/core/models.py
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/baas_production")

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False, index=True)
    balance = Column(Numeric(20, 6), nullable=False, default=0)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, nullable=False)
    # ... more fields

# Create all tables
Base.metadata.create_all(bind=engine)
```

**Migration Script:**
```python
# banking/scripts/migrate_json_to_postgres.py
import json
from core.models import SessionLocal, Account, Transaction

def migrate_data():
    """Migrate from JSON files to PostgreSQL"""
    # Read JSON data
    with open("banking_data/accounts.json", "r") as f:
        accounts = json.load(f)

    # Insert into PostgreSQL
    session = SessionLocal()
    for acc_data in accounts:
        account = Account(
            id=acc_data["id"],
            agent_id=acc_data["agent_id"],
            balance=acc_data["balance"],
            # ... map all fields
        )
        session.add(account)

    session.commit()
    print(f"Migrated {len(accounts)} accounts")

if __name__ == "__main__":
    migrate_data()
```

**Testing:**
```bash
# Test database connection
python -c "from core.models import engine; print(engine.connect())"

# Run migration
python banking/scripts/migrate_json_to_postgres.py

# Verify data
psql -h localhost -U postgres -d baas_production -c "SELECT COUNT(*) FROM accounts;"
```

**Success Criteria:**
- [ ] PostgreSQL running with replication
- [ ] All accounts migrated
- [ ] All transactions migrated
- [ ] Zero data loss
- [ ] JSON files backed up and archived

---

### Week 2-3: Multi-Factor Authentication
**Current Issue**: No MFA - required for banking

**Action Items:**
1. Install dependencies:
```bash
pip install pyotp qrcode twilio
```

2. Implement TOTP-based MFA:
```python
# banking/security/mfa.py
import pyotp
import qrcode

class MFAService:
    def setup_mfa(self, agent_id: str):
        """Generate TOTP secret and QR code"""
        secret = pyotp.random_base32()

        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=agent_id,
            issuer_name="BaaS Arc"
        )

        qr = qrcode.make(totp_uri)
        qr.save(f"/tmp/{agent_id}_mfa_qr.png")

        # Save secret to database
        self.save_mfa_secret(agent_id, secret)

        return {
            "secret": secret,
            "qr_code_path": f"/tmp/{agent_id}_mfa_qr.png"
        }

    def verify_mfa(self, agent_id: str, code: str) -> bool:
        """Verify TOTP code"""
        secret = self.get_mfa_secret(agent_id)
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
```

3. Add MFA to login flow:
```python
# banking/baas_backend.py - Update login endpoint
@app.route('/api/auth/login', methods=['POST'])
def login():
    # Step 1: Validate username/password
    # ... existing code ...

    # Step 2: Check if MFA enabled
    if user.mfa_enabled:
        return jsonify({
            "status": "mfa_required",
            "session_token": create_temp_session(user.id)
        }), 200

    # ... existing code ...

@app.route('/api/auth/verify-mfa', methods=['POST'])
def verify_mfa():
    data = request.json
    session_token = data.get('session_token')
    mfa_code = data.get('code')

    user_id = validate_temp_session(session_token)

    if mfa_service.verify_mfa(user_id, mfa_code):
        # Create full session
        access_token = create_access_token(user_id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid MFA code"}), 401
```

**Success Criteria:**
- [ ] TOTP MFA working
- [ ] QR codes generated
- [ ] MFA enforced for all logins
- [ ] Backup codes generated

---

### Week 3-4: KYC Integration
**Current Issue**: Only basic KYA, no real identity verification

**Action Items:**

1. Sign up for Onfido (https://onfido.com):
   - Free trial available
   - Production pricing: $1-$3 per verification

2. Implement KYC flow:
```python
# banking/compliance/kyc_service.py
from onfido import Api, Configuration

class KYCService:
    def __init__(self):
        config = Configuration(api_key=os.getenv("ONFIDO_API_KEY"))
        self.onfido = Api(config)

    async def verify_agent(self, agent_data: dict):
        """Complete KYC verification"""
        # Step 1: Create applicant
        applicant = self.onfido.create_applicant(
            first_name=agent_data["first_name"],
            last_name=agent_data["last_name"],
            email=agent_data["email"]
        )

        # Step 2: Document verification
        document = self.onfido.upload_document(
            applicant_id=applicant.id,
            file=agent_data["document_image"],
            type="passport"
        )

        # Step 3: Run check
        check = self.onfido.create_check(
            applicant_id=applicant.id,
            reports=["identity", "document"]
        )

        # Step 4: Wait for results
        result = await self.wait_for_check_completion(check.id)

        if result.status == "complete" and result.result == "clear":
            return {
                "status": "approved",
                "applicant_id": applicant.id,
                "verification_date": datetime.now()
            }
        else:
            return {
                "status": "rejected",
                "reason": result.reason
            }
```

3. Update onboarding to require KYC:
```python
# banking/divisions/front_office_agent.py - Update onboard_agent
async def onboard_agent(self, agent_data: dict):
    # Step 1: Basic validation
    # ... existing code ...

    # Step 2: KYC verification (NEW)
    kyc_result = await kyc_service.verify_agent(agent_data)

    if kyc_result["status"] != "approved":
        raise KYCRejectedError(kyc_result["reason"])

    # Step 3: Create agent account
    # ... rest of existing code ...

    # Save KYC data
    agent.kyc_verified = True
    agent.kyc_date = kyc_result["verification_date"]
    agent.onfido_applicant_id = kyc_result["applicant_id"]
```

**Success Criteria:**
- [ ] Onfido integration working
- [ ] Document upload functional
- [ ] Identity verification automated
- [ ] KYC status tracked in database

---

## MONTH 2: INFRASTRUCTURE & SECURITY

### Week 5-6: High Availability Setup

**Action Items:**

1. Set up multi-region deployment:
```yaml
# banking/infrastructure/terraform/main.tf
provider "aws" {
  region = "us-east-1"
}

# Application Load Balancer
resource "aws_lb" "baas_alb" {
  name               = "baas-arc-alb"
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  enable_deletion_protection = true
  enable_http2              = true
}

# Auto Scaling Group
resource "aws_autoscaling_group" "baas_asg" {
  name                = "baas-arc-asg"
  vpc_zone_identifier = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  target_group_arns   = [aws_lb_target_group.baas.arn]

  min_size         = 3
  max_size         = 20
  desired_capacity = 3

  health_check_type         = "ELB"
  health_check_grace_period = 300
}

# RDS PostgreSQL with Multi-AZ
resource "aws_db_instance" "baas_db" {
  identifier           = "baas-arc-db"
  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = "db.r6g.xlarge"
  allocated_storage    = 100

  multi_az             = true  # CRITICAL for HA
  backup_retention_period = 30
  backup_window        = "03:00-04:00"
  maintenance_window   = "sun:04:00-sun:05:00"
}
```

2. Deploy using Terraform:
```bash
cd banking/infrastructure/terraform
terraform init
terraform plan
terraform apply
```

**Success Criteria:**
- [ ] Multi-AZ deployment
- [ ] Auto-scaling configured
- [ ] Load balancer healthy
- [ ] Database replication working
- [ ] 99.9% uptime achieved

---

### Week 7-8: Monitoring & Alerting

**Action Items:**

1. Set up comprehensive monitoring:
```yaml
# banking/docker/monitoring/docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards

  # NEW: Error tracking
  sentry:
    image: sentry:latest
    environment:
      SENTRY_SECRET_KEY: ${SENTRY_SECRET_KEY}
    ports:
      - "9000:9000"

  # NEW: Distributed tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI

  # NEW: Log aggregation
  elasticsearch:
    image: elasticsearch:8.11.0

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

2. Instrument code with tracing:
```python
# Add to all critical functions
import sentry_sdk
from opentelemetry import trace

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment="production",
    traces_sample_rate=0.1
)

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_transaction")
async def process_transaction(tx: dict):
    try:
        # Your existing code
        pass
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
```

3. Set up PagerDuty alerts:
```python
# banking/monitoring/alerts.py
from pypagerduty import PagerDuty

class AlertManager:
    def __init__(self):
        self.pd = PagerDuty(api_key=os.getenv("PAGERDUTY_API_KEY"))

    async def trigger_alert(self, severity: str, message: str):
        """Trigger PagerDuty alert"""
        if severity == "critical":
            self.pd.create_incident(
                title=f"CRITICAL: {message}",
                service_id=os.getenv("PAGERDUTY_SERVICE_ID"),
                urgency="high"
            )
```

**Success Criteria:**
- [ ] Grafana dashboards created
- [ ] Sentry capturing errors
- [ ] PagerDuty integration working
- [ ] 24/7 on-call rotation established

---

## MONTH 3: BANKING LICENSE PREPARATION

### Week 9-10: Legal & Compliance Setup

**Action Items:**

1. **Hire Banking Attorney**:
   - Specialty: Fintech/banking regulation
   - Cost: $50K-$150K for initial work
   - Firms: Mayer Brown, Covington & Burling, K&L Gates

2. **Choose Regulatory Path**:
   - [ ] Research bank partner options (Cross River, Blue Ridge, Evolve)
   - [ ] Schedule calls with potential partners
   - [ ] Compare partnership terms:
     - Revenue share (typically 20-40% to bank)
     - Setup fees ($50K-$200K)
     - Monthly platform fees ($5K-$20K)
     - Compliance requirements

3. **Prepare Documentation**:
   - [ ] Business plan (100+ pages)
   - [ ] Financial projections (5 years)
   - [ ] Risk management framework
   - [ ] AML/BSA policies and procedures
   - [ ] Information security program
   - [ ] Disaster recovery plan
   - [ ] Business continuity plan

**Template Structure:**
```
legal/
├── business_plan.md
├── financial_projections.xlsx
├── risk_management_framework.md
├── aml_bsa_program.md
├── information_security_program.md
├── disaster_recovery_plan.md
└── business_continuity_plan.md
```

---

### Week 11-12: Reconciliation System

**Action Items:**

1. Implement daily reconciliation:
```python
# banking/accounting/reconciliation.py
class ReconciliationEngine:
    async def run_daily_reconciliation(self, date: datetime.date):
        """Reconcile internal ledger vs blockchain"""

        # Step 1: Internal ledger
        internal = await self.get_internal_ledger_balance(date)

        # Step 2: Blockchain
        blockchain = await self.get_blockchain_balance(date)

        # Step 3: Circle Wallets
        circle = await self.get_circle_balance(date)

        # Step 4: Compare
        differences = {
            "internal_vs_blockchain": internal - blockchain,
            "internal_vs_circle": internal - circle
        }

        # Step 5: Check tolerance (1 cent)
        for key, diff in differences.items():
            if abs(diff) > Decimal("0.01"):
                # BREAK DETECTED
                await self.handle_reconciliation_break(
                    date=date,
                    difference=diff,
                    type=key
                )

        return ReconciliationReport(
            date=date,
            status="balanced" if all(abs(d) <= 0.01 for d in differences.values()) else "break",
            differences=differences
        )

    async def handle_reconciliation_break(self, date, difference, type):
        """Handle reconciliation break - CRITICAL"""
        # 1. Freeze all operations
        await self.freeze_operations()

        # 2. Alert finance team
        await self.alert_finance_team(
            severity="critical",
            message=f"Reconciliation break: {type} = ${difference}"
        )

        # 3. Create investigation ticket
        await self.create_investigation_ticket(date, difference, type)

        # 4. Notify regulators if required (> $10K)
        if abs(difference) > 10000:
            await self.notify_regulators(date, difference)
```

2. Set up automated daily reconciliation:
```python
# banking/jobs/daily_reconciliation.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)  # 2 AM daily
async def daily_reconciliation_job():
    """Run daily reconciliation automatically"""
    yesterday = datetime.now().date() - timedelta(days=1)

    recon_engine = ReconciliationEngine()
    report = await recon_engine.run_daily_reconciliation(yesterday)

    # Email report to finance team
    await send_reconciliation_report(report)

scheduler.start()
```

**Success Criteria:**
- [ ] Automated daily reconciliation
- [ ] Break detection working
- [ ] Alerts configured
- [ ] Finance team trained

---

## MONTHS 4-6: FEATURE COMPLETION

### Card Program Integration

**Action Items:**

1. Sign partnership with Marqeta:
   - Setup fee: $50K-$100K
   - Per-card fee: $1-$3
   - Transaction fee: $0.01-$0.05

2. Implement virtual cards:
```python
# banking/cards/marqeta_service.py
from marqeta import Client

class CardIssuingService:
    def __init__(self):
        self.marqeta = Client(
            app_token=os.getenv("MARQETA_APP_TOKEN"),
            admin_token=os.getenv("MARQETA_ADMIN_TOKEN")
        )

    async def issue_virtual_card(self, account_id: str):
        """Issue virtual debit card"""
        # Create user in Marqeta
        user = self.marqeta.users.create({
            "token": account_id,
            "first_name": "Agent",
            "last_name": account_id
        })

        # Create card
        card = self.marqeta.cards.create({
            "user_token": account_id,
            "card_product_token": "virtual_debit_card"
        })

        return {
            "card_token": card.token,
            "pan": card.pan,
            "cvv": card.cvv,
            "expiry": card.expiration
        }
```

---

### ACH/Wire Integration

**Action Items:**

1. Integrate Modern Treasury:
   - Platform fee: $5K-$20K/month
   - Per-transaction: $0.25-$1.00

2. Implement ACH transfers:
```python
# banking/payments/modern_treasury.py
from modern_treasury import ModernTreasury

class PaymentRailsService:
    def __init__(self):
        self.mt = ModernTreasury(
            api_key=os.getenv("MODERN_TREASURY_API_KEY")
        )

    async def send_ach_transfer(
        self,
        from_account: str,
        to_routing: str,
        to_account: str,
        amount: Decimal,
        description: str
    ):
        """Send ACH transfer"""
        payment = self.mt.payment_orders.create({
            "type": "ach",
            "amount": int(amount * 100),  # Cents
            "direction": "debit",
            "originating_account_id": from_account,
            "receiving_account": {
                "routing_number": to_routing,
                "account_number": to_account
            },
            "description": description
        })

        return payment
```

---

## MONTHS 6-12: LICENSING & SCALE

### Banking License Application

**If pursuing full license:**

1. Submit application to OCC (for national bank) or state regulator
2. Prepare for examiners' visit
3. Demonstrate compliance with all regulations
4. Await approval (6-12 months)

**If pursuing partnership:**

1. Finalize partnership agreement
2. Integrate with partner bank's systems
3. Complete compliance review
4. Launch to market

---

### Scale Infrastructure

**Action Items:**

1. Migrate to Kubernetes:
```yaml
# banking/kubernetes/production.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: baas-backend
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
  template:
    spec:
      containers:
      - name: backend
        image: baas-arc:v2.0.0
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

2. Implement auto-scaling:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: baas-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: baas-backend
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## BUDGET BREAKDOWN

### Months 1-3 (Foundation)
| Item | Cost |
|------|------|
| PostgreSQL infrastructure | $5K |
| KYC integration (Onfido) | $10K setup + $3/verification |
| MFA implementation | $2K |
| Monitoring tools (DataDog, Sentry) | $5K |
| Legal consultation | $20K |
| Development team (3 engineers) | $75K |
| **TOTAL** | **$117K + $75K = $192K** |

### Months 4-6 (Features)
| Item | Cost |
|------|------|
| Card program (Marqeta) | $75K setup |
| ACH integration (Modern Treasury) | $30K setup + $5K/month |
| Customer support (Zendesk) | $10K |
| Development team | $150K |
| **TOTAL** | **$265K** |

### Months 6-12 (License & Scale)
| Item | Cost |
|------|------|
| Bank partnership fees | $100K-$200K |
| Infrastructure scaling | $50K |
| SOC 2 audit | $50K |
| Development team | $300K |
| **TOTAL** | **$500K-$600K** |

### GRAND TOTAL (12 months)
**$957K - $1.057M**

---

## SUCCESS METRICS

### Month 3
- [ ] PostgreSQL production ready
- [ ] KYC integrated and functional
- [ ] MFA enforced
- [ ] 99.9% uptime achieved

### Month 6
- [ ] Card program launched
- [ ] ACH transfers working
- [ ] 1,000+ verified customers
- [ ] SOC 2 Type I complete

### Month 12
- [ ] Banking license obtained or partnership finalized
- [ ] 10,000+ active customers
- [ ] $10M+ in deposits
- [ ] Profitable unit economics

---

## GETTING STARTED TODAY

### Step 1: Database Migration (This Week)
```bash
# 1. Set up PostgreSQL
docker-compose up -d postgres

# 2. Run migration script
python banking/scripts/migrate_json_to_postgres.py

# 3. Update all code to use PostgreSQL
# Replace all references to JSONStorage with PostgresStorage

# 4. Test thoroughly
pytest banking/tests/test_postgres_storage.py
```

### Step 2: Sign Up for Services (This Week)
- [ ] Onfido account (KYC)
- [ ] Sentry account (error tracking)
- [ ] PagerDuty account (alerts)
- [ ] AWS/GCP account (infrastructure)

### Step 3: Legal Consultation (Next Week)
- [ ] Research banking attorneys
- [ ] Schedule initial consultations (3-5 firms)
- [ ] Choose legal counsel
- [ ] Begin regulatory strategy discussion

---

## CONCLUSION

**This is doable in 12 months with $1M-$1.5M budget.**

**Critical success factors:**
1. Strong legal counsel
2. Experienced compliance team
3. Robust technical infrastructure
4. Clear regulatory strategy
5. Adequate capitalization

**Biggest risks:**
1. Regulatory delays
2. Technical issues in production
3. Insufficient funding
4. Competitive pressure

**Next Steps:**
1. Get database migration done this week
2. Hire legal counsel
3. Decide on regulatory path (partnership vs full license)
4. Secure funding ($1.5M minimum)

---

**Ready to start? Begin with Month 1, Week 1 tasks above.**

**Questions? Review PRODUCTION_BANKING_GAPS.md for detailed gap analysis.**
