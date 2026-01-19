-- ============================================================================
-- Arc BaaS - PostgreSQL Initialization Script
-- ============================================================================
-- Creates database schema for production deployment
-- Runs automatically on first container startup
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- Accounts Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    balance DECIMAL(20, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    transactions_count INTEGER NOT NULL DEFAULT 0,
    wallet_address VARCHAR(42),
    circle_wallet_id VARCHAR(255),
    CONSTRAINT chk_balance_positive CHECK (balance >= 0),
    CONSTRAINT chk_account_type CHECK (account_type IN ('Checking', 'Savings', 'Business', 'Investment')),
    CONSTRAINT chk_status CHECK (status IN ('Active', 'Suspended', 'Closed'))
);

CREATE INDEX idx_accounts_owner ON accounts(owner);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_wallet ON accounts(wallet_address);

-- ----------------------------------------------------------------------------
-- Transactions Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    related_account UUID REFERENCES accounts(account_id),
    tx_hash VARCHAR(66),
    blockchain_network VARCHAR(50),
    gas_fee DECIMAL(20, 8),
    CONSTRAINT chk_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_transaction_type CHECK (transaction_type IN ('Debit', 'Credit', 'Transfer', 'Withdrawal', 'Deposit')),
    CONSTRAINT chk_status CHECK (status IN ('Approved', 'Pending', 'Blocked', 'Failed'))
);

CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(date DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_hash ON transactions(tx_hash);

-- ----------------------------------------------------------------------------
-- Risk Events Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS risk_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID REFERENCES transactions(transaction_id) ON DELETE SET NULL,
    account_id UUID REFERENCES accounts(account_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    risk_score DECIMAL(5, 2) NOT NULL,
    detected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'Open',
    details JSONB,
    CONSTRAINT chk_risk_score CHECK (risk_score >= 0 AND risk_score <= 100),
    CONSTRAINT chk_event_status CHECK (status IN ('Open', 'Investigating', 'Resolved', 'False_Positive'))
);

CREATE INDEX idx_risk_events_account ON risk_events(account_id);
CREATE INDEX idx_risk_events_transaction ON risk_events(transaction_id);
CREATE INDEX idx_risk_events_status ON risk_events(status);
CREATE INDEX idx_risk_events_score ON risk_events(risk_score DESC);

-- ----------------------------------------------------------------------------
-- AI Insights Table (Gemini AI)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_insights (
    insight_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(account_id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,
    confidence DECIMAL(5, 2) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB,
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 100)
);

CREATE INDEX idx_ai_insights_account ON ai_insights(account_id);
CREATE INDEX idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX idx_ai_insights_created ON ai_insights(created_at DESC);

-- ----------------------------------------------------------------------------
-- Audit Log Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB
);

CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);

-- ----------------------------------------------------------------------------
-- Update Triggers
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- Grant Permissions
-- ----------------------------------------------------------------------------
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO baas_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO baas_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO baas_admin;

-- ============================================================================
-- Initialization Complete
-- ============================================================================
