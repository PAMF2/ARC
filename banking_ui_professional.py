"""
Arc BaaS - Banking as a Service
Professional Enterprise Banking Platform
"""

import requests
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Backend API base URL
BACKEND_URL = "http://localhost:5001"

# Professional logging format
def log(level, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arc BaaS - Banking as a Service</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --navy-primary: #003366;
            --navy-dark: #001f3f;
            --navy-light: #004080;
            --white: #FFFFFF;
            --off-white: #F8F9FA;
            --gray-100: #F1F3F5;
            --gray-200: #E9ECEF;
            --gray-300: #DEE2E6;
            --gray-400: #CED4DA;
            --gray-600: #6C757D;
            --gray-800: #343A40;
            --gray-900: #212529;
            --green-positive: #10B981;
            --green-light: #D1FAE5;
            --red-negative: #EF4444;
            --red-light: #FEE2E2;
            --blue-accent: #3B82F6;
            --gold-accent: #D4AF37;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: var(--gray-100);
            color: var(--gray-900);
            line-height: 1.6;
            min-height: 100vh;
        }

        /* Header Navigation */
        .header {
            background: linear-gradient(135deg, var(--navy-dark) 0%, var(--navy-primary) 100%);
            color: var(--white);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .header-top {
            padding: 1.5rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: var(--white);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: var(--navy-primary);
            font-size: 1.2rem;
        }

        .logo-text h1 {
            font-size: 1.5rem;
            font-weight: 600;
            letter-spacing: -0.5px;
        }

        .logo-text p {
            font-size: 0.75rem;
            opacity: 0.9;
            font-weight: 300;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .header-status {
            display: flex;
            align-items: center;
            gap: 2rem;
            font-size: 0.875rem;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green-positive);
            box-shadow: 0 0 8px var(--green-positive);
        }

        .status-indicator.offline {
            background: var(--red-negative);
            box-shadow: 0 0 8px var(--red-negative);
        }

        /* Navigation */
        .nav-tabs {
            background: var(--navy-primary);
            padding: 0 2rem;
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            gap: 0.5rem;
            overflow-x: auto;
        }

        .nav-tab {
            padding: 1rem 1.5rem;
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .nav-tab:hover {
            color: var(--white);
            background: rgba(255, 255, 255, 0.05);
        }

        .nav-tab.active {
            color: var(--white);
            border-bottom-color: var(--white);
            background: rgba(255, 255, 255, 0.1);
        }

        /* Main Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Tab Content */
        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Statistics Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--white);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--navy-primary);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .stat-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--navy-primary);
            margin-bottom: 0.5rem;
        }

        .stat-subtext {
            font-size: 0.875rem;
            color: var(--gray-600);
        }

        /* Section Headers */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--gray-900);
        }

        /* Cards */
        .card {
            background: var(--white);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gray-200);
        }

        .card-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--gray-900);
        }

        /* Account Cards */
        .account-card {
            background: var(--white);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .account-card:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .account-info h4 {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 0.25rem;
        }

        .account-meta {
            font-size: 0.875rem;
            color: var(--gray-600);
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .account-id {
            font-family: 'Courier New', monospace;
            background: var(--gray-100);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }

        .account-balance {
            text-align: right;
        }

        .balance-amount {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--navy-primary);
        }

        .balance-label {
            font-size: 0.75rem;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Transaction Cards */
        .transaction-card {
            background: var(--white);
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 3px solid var(--gray-300);
            transition: all 0.2s ease;
        }

        .transaction-card:hover {
            background: var(--gray-100);
            border-left-color: var(--navy-primary);
        }

        .transaction-info h4 {
            font-size: 1rem;
            font-weight: 500;
            color: var(--gray-900);
            margin-bottom: 0.25rem;
        }

        .transaction-meta {
            font-size: 0.875rem;
            color: var(--gray-600);
            display: flex;
            gap: 1rem;
        }

        .transaction-details {
            text-align: right;
        }

        .transaction-amount {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .amount-positive {
            color: var(--green-positive);
        }

        .amount-negative {
            color: var(--red-negative);
        }

        /* Status Badges */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-approved {
            background: var(--green-light);
            color: var(--green-positive);
        }

        .status-pending {
            background: #FEF3C7;
            color: #D97706;
        }

        .status-blocked {
            background: var(--red-light);
            color: var(--red-negative);
        }

        /* Forms */
        .form-section {
            background: var(--white);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            max-width: 600px;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--gray-800);
        }

        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--gray-300);
            border-radius: 6px;
            font-size: 1rem;
            font-family: inherit;
            color: var(--gray-900);
            background: var(--white);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: var(--navy-primary);
            box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1);
        }

        .form-textarea {
            min-height: 100px;
            resize: vertical;
        }

        /* Buttons */
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--navy-primary);
            color: var(--white);
        }

        .btn-primary:hover {
            background: var(--navy-dark);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 51, 102, 0.3);
        }

        .btn-secondary {
            background: var(--gray-200);
            color: var(--gray-800);
        }

        .btn-secondary:hover {
            background: var(--gray-300);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }

        /* Alerts */
        .alert {
            padding: 1rem 1.5rem;
            border-radius: 6px;
            margin-bottom: 1.5rem;
            display: none;
            font-size: 0.875rem;
            font-weight: 500;
        }

        .alert.show {
            display: block;
        }

        .alert-success {
            background: var(--green-light);
            color: var(--green-positive);
            border-left: 4px solid var(--green-positive);
        }

        .alert-error {
            background: var(--red-light);
            color: var(--red-negative);
            border-left: 4px solid var(--red-negative);
        }

        .alert-info {
            background: #DBEAFE;
            color: var(--blue-accent);
            border-left: 4px solid var(--blue-accent);
        }

        /* Chart Container */
        .chart-container {
            background: var(--white);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* AI Analysis Panel */
        .ai-panel {
            background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
            border-radius: 12px;
            padding: 1.5rem;
            border-left: 4px solid var(--blue-accent);
            margin-top: 1rem;
        }

        .ai-panel-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--blue-accent);
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .ai-panel-content {
            color: var(--gray-800);
            line-height: 1.6;
        }

        /* Grid Layouts */
        .grid-2col {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 1.5rem;
        }

        /* Footer */
        .footer {
            background: var(--gray-900);
            color: var(--gray-400);
            padding: 2rem;
            margin-top: 4rem;
        }

        .footer-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.875rem;
        }

        .footer-links {
            display: flex;
            gap: 2rem;
        }

        .footer-link {
            color: var(--gray-400);
            text-decoration: none;
            transition: color 0.2s ease;
        }

        .footer-link:hover {
            color: var(--white);
        }

        /* Loading State */
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid var(--gray-300);
            border-radius: 50%;
            border-top-color: var(--navy-primary);
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: var(--gray-600);
        }

        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.3;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .grid-2col {
                grid-template-columns: 1fr;
            }

            .account-card {
                flex-direction: column;
                gap: 1rem;
                align-items: flex-start;
            }

            .account-balance {
                text-align: left;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="header-top">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon">AB</div>
                    <div class="logo-text">
                        <h1>Arc BaaS</h1>
                        <p>Banking as a Service</p>
                    </div>
                </div>
                <div class="header-status">
                    <div class="status-item">
                        <span class="status-indicator" id="status-indicator"></span>
                        <span id="status-text">System Online</span>
                    </div>
                    <div class="status-item">
                        <span id="status-time"></span>
                    </div>
                </div>
            </div>
        </div>
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab('dashboard')">Dashboard</button>
            <button class="nav-tab" onclick="switchTab('accounts')">Accounts</button>
            <button class="nav-tab" onclick="switchTab('transactions')">Transactions</button>
            <button class="nav-tab" onclick="switchTab('agents')">AI Agents</button>
            <button class="nav-tab" onclick="switchTab('analytics')">Analytics</button>
        </div>
    </div>

    <!-- Main Container -->
    <div class="container">
        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="section-header">
                <h2 class="section-title">Account Overview</h2>
            </div>
            <div class="stats-grid" id="dashboard-stats"></div>

            <div class="section-header">
                <h2 class="section-title">Active Accounts</h2>
            </div>
            <div id="dashboard-accounts"></div>

            <div class="section-header">
                <h2 class="section-title">Recent Transactions</h2>
            </div>
            <div id="dashboard-transactions"></div>
        </div>

        <!-- Accounts Tab -->
        <div id="accounts" class="tab-content">
            <div class="section-header">
                <h2 class="section-title">Account Management</h2>
            </div>
            <div id="accounts-list"></div>

            <div class="section-header" style="margin-top: 3rem;">
                <h2 class="section-title">Create New Account</h2>
            </div>
            <div class="form-section">
                <div id="account-alert" class="alert"></div>
                <div class="form-group">
                    <label class="form-label">Account Owner</label>
                    <input type="text" class="form-input" id="owner-name" placeholder="Enter full name">
                </div>
                <div class="form-group">
                    <label class="form-label">Account Type</label>
                    <select class="form-select" id="account-type">
                        <option>Checking</option>
                        <option>Savings</option>
                        <option>Investment</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Initial Balance (USD)</label>
                    <input type="number" class="form-input" id="initial-balance" placeholder="0.00" value="0" step="0.01">
                </div>
                <button class="btn btn-primary" onclick="createAccount()">Create Account</button>
            </div>
        </div>

        <!-- Transactions Tab -->
        <div id="transactions" class="tab-content">
            <div class="section-header">
                <h2 class="section-title">Transaction History</h2>
            </div>
            <div id="transactions-list"></div>

            <div class="section-header" style="margin-top: 3rem;">
                <h2 class="section-title">Process New Transaction</h2>
            </div>
            <div class="form-section">
                <div id="transaction-alert" class="alert"></div>
                <div class="form-group">
                    <label class="form-label">Source Account</label>
                    <select class="form-select" id="from-account"></select>
                </div>
                <div class="form-group">
                    <label class="form-label">Transaction Type</label>
                    <select class="form-select" id="transaction-type">
                        <option>Debit</option>
                        <option>Credit</option>
                        <option>Transfer</option>
                        <option>Withdrawal</option>
                        <option>Deposit</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Amount (USD)</label>
                    <input type="number" class="form-input" id="amount" placeholder="0.00" step="0.01">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" id="description" placeholder="Transaction description">
                </div>
                <button class="btn btn-primary" onclick="processTransaction()">Process Transaction</button>
            </div>
        </div>

        <!-- AI Agents Tab -->
        <div id="agents" class="tab-content">
            <div class="section-header">
                <h2 class="section-title">AI Agent Services</h2>
            </div>

            <div class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Transaction Validation</h3>
                    </div>
                    <p style="color: var(--gray-600); margin-bottom: 1.5rem; font-size: 0.875rem;">
                        Analyze transactions for fraud risk and security threats using AI-powered validation
                    </p>
                    <div id="validation-alert" class="alert"></div>
                    <div class="form-group">
                        <label class="form-label">Account ID</label>
                        <input type="text" class="form-input" id="val-account" placeholder="ACC001">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Amount (USD)</label>
                        <input type="number" class="form-input" id="val-amount" placeholder="1000">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Transaction Type</label>
                        <select class="form-select" id="val-type">
                            <option>Debit</option>
                            <option>Credit</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" onclick="validateWithAI()" style="width: 100%;">Analyze Transaction</button>
                    <div id="validation-result"></div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Financial Advisory</h3>
                    </div>
                    <p style="color: var(--gray-600); margin-bottom: 1.5rem; font-size: 0.875rem;">
                        Get AI-powered financial recommendations based on account activity and patterns
                    </p>
                    <div id="advice-alert" class="alert"></div>
                    <div class="form-group">
                        <label class="form-label">Select Account</label>
                        <select class="form-select" id="advice-account"></select>
                    </div>
                    <button class="btn btn-primary" onclick="getFinancialAdvice()" style="width: 100%;">Get Recommendations</button>
                    <div id="advice-result"></div>
                </div>
            </div>

            <div class="section-header" style="margin-top: 3rem;">
                <h2 class="section-title">Arc Network Status</h2>
            </div>
            <div class="card">
                <div class="stats-grid">
                    <div>
                        <div class="stat-label">Network Status</div>
                        <div style="color: var(--green-positive); font-weight: 600; margin-top: 0.5rem;">Active</div>
                    </div>
                    <div>
                        <div class="stat-label">Connected Agents</div>
                        <div style="font-size: 1.5rem; font-weight: 600; margin-top: 0.5rem;">2</div>
                    </div>
                    <div>
                        <div class="stat-label">Processing Capacity</div>
                        <div style="font-size: 1.5rem; font-weight: 600; margin-top: 0.5rem;">98%</div>
                    </div>
                    <div>
                        <div class="stat-label">Response Time</div>
                        <div style="font-size: 1.5rem; font-weight: 600; margin-top: 0.5rem;">245ms</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analytics Tab -->
        <div id="analytics" class="tab-content">
            <div class="section-header">
                <h2 class="section-title">Banking Analytics</h2>
            </div>
            <div class="chart-container">
                <div id="chart-by-type"></div>
            </div>
            <div class="chart-container">
                <div id="chart-status-distribution"></div>
            </div>
            <div class="chart-container">
                <div id="chart-account-balances"></div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <div class="footer">
        <div class="footer-content">
            <div>
                <div style="margin-bottom: 0.5rem;">Arc BaaS Platform v2.0.1</div>
                <div style="font-size: 0.75rem; color: var(--gray-600);">© 2024 Arc Banking Services. All rights reserved.</div>
            </div>
            <div class="footer-links">
                <a href="#" class="footer-link">Privacy Policy</a>
                <a href="#" class="footer-link">Terms of Service</a>
                <a href="#" class="footer-link">Support</a>
            </div>
        </div>
    </div>

    <script>
        const API_URL = '/api';

        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');

            if (tabName === 'dashboard') loadDashboard();
            if (tabName === 'accounts') loadAccounts();
            if (tabName === 'transactions') loadTransactions();
            if (tabName === 'agents') loadAgentsData();
            if (tabName === 'analytics') loadAnalytics();
        }

        // Update status
        function updateStatus() {
            fetch(API_URL + '/health')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status-indicator').classList.remove('offline');
                    document.getElementById('status-text').textContent = 'System Online';
                })
                .catch(() => {
                    document.getElementById('status-indicator').classList.add('offline');
                    document.getElementById('status-text').textContent = 'System Offline';
                });

            const now = new Date();
            document.getElementById('status-time').textContent = now.toLocaleString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });
        }

        // Load dashboard
        function loadDashboard() {
            fetch(API_URL + '/analytics')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const a = data.analytics;
                        const statsHtml = `
                            <div class="stat-card">
                                <div class="stat-label">Total Assets</div>
                                <div class="stat-value">$${a.total_balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                                <div class="stat-subtext">${a.total_accounts} Active Accounts</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Total Transactions</div>
                                <div class="stat-value">${a.total_transactions}</div>
                                <div class="stat-subtext">${a.approved_transactions} Approved</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Pending Review</div>
                                <div class="stat-value">${a.pending_transactions}</div>
                                <div class="stat-subtext">Awaiting Approval</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Active Accounts</div>
                                <div class="stat-value">${a.total_accounts}</div>
                                <div class="stat-subtext">All Account Types</div>
                            </div>
                        `;
                        document.getElementById('dashboard-stats').innerHTML = statsHtml;

                        const accountsHtml = a.accounts.slice(0, 5).map(acc => `
                            <div class="account-card">
                                <div class="account-info">
                                    <h4>${acc.owner}</h4>
                                    <div class="account-meta">
                                        <span class="account-id">${acc.account_id}</span>
                                        <span>${acc.account_type}</span>
                                    </div>
                                </div>
                                <div class="account-balance">
                                    <div class="balance-label">Balance</div>
                                    <div class="balance-amount">$${acc.balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('dashboard-accounts').innerHTML = accountsHtml || '<div class="empty-state"><div class="empty-state-icon">—</div><p>No accounts found</p></div>';

                        // Load recent transactions for dashboard
                        fetch(API_URL + '/transactions')
                            .then(r => r.json())
                            .then(txData => {
                                if (txData.success) {
                                    const txHtml = txData.transactions.slice(0, 5).map(tx => `
                                        <div class="transaction-card">
                                            <div class="transaction-info">
                                                <h4>${tx.description}</h4>
                                                <div class="transaction-meta">
                                                    <span>${tx.date}</span>
                                                    <span>${tx.transaction_type}</span>
                                                </div>
                                            </div>
                                            <div class="transaction-details">
                                                <div class="transaction-amount ${tx.transaction_type === 'Credit' || tx.transaction_type === 'Deposit' ? 'amount-positive' : 'amount-negative'}">
                                                    ${tx.transaction_type === 'Credit' || tx.transaction_type === 'Deposit' ? '+' : '-'}$${tx.amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                                </div>
                                                <span class="status-badge status-${tx.status.toLowerCase()}">${tx.status}</span>
                                            </div>
                                        </div>
                                    `).join('');
                                    document.getElementById('dashboard-transactions').innerHTML = txHtml || '<div class="empty-state"><div class="empty-state-icon">—</div><p>No transactions found</p></div>';
                                }
                            });
                    }
                });
        }

        // Load accounts
        function loadAccounts() {
            fetch(API_URL + '/accounts')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const accountsHtml = data.accounts.map(acc => `
                            <div class="account-card">
                                <div class="account-info">
                                    <h4>${acc.owner}</h4>
                                    <div class="account-meta">
                                        <span class="account-id">${acc.account_id}</span>
                                        <span>${acc.account_type}</span>
                                    </div>
                                </div>
                                <div class="account-balance">
                                    <div class="balance-label">Balance</div>
                                    <div class="balance-amount">$${acc.balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('accounts-list').innerHTML = accountsHtml || '<div class="empty-state"><div class="empty-state-icon">—</div><p>No accounts found</p></div>';

                        // Populate selectors
                        const options = data.accounts.map(acc =>
                            `<option value="${acc.account_id}">${acc.owner} (${acc.account_id}) - $${acc.balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</option>`
                        ).join('');
                        document.getElementById('from-account').innerHTML = options;
                        document.getElementById('advice-account').innerHTML = options;
                        if (data.accounts.length > 0) {
                            document.getElementById('val-account').value = data.accounts[0].account_id;
                        }
                    }
                });
        }

        // Load transactions
        function loadTransactions() {
            fetch(API_URL + '/transactions')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const txHtml = data.transactions.map(tx => `
                            <div class="transaction-card">
                                <div class="transaction-info">
                                    <h4>${tx.description}</h4>
                                    <div class="transaction-meta">
                                        <span>${tx.date}</span>
                                        <span>${tx.transaction_type}</span>
                                    </div>
                                </div>
                                <div class="transaction-details">
                                    <div class="transaction-amount ${tx.transaction_type === 'Credit' || tx.transaction_type === 'Deposit' ? 'amount-positive' : 'amount-negative'}">
                                        ${tx.transaction_type === 'Credit' || tx.transaction_type === 'Deposit' ? '+' : '-'}$${tx.amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                    </div>
                                    <span class="status-badge status-${tx.status.toLowerCase()}">${tx.status}</span>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('transactions-list').innerHTML = txHtml || '<div class="empty-state"><div class="empty-state-icon">—</div><p>No transactions found</p></div>';
                    }
                });
        }

        // Create account
        function createAccount() {
            const owner = document.getElementById('owner-name').value;
            const type = document.getElementById('account-type').value;
            const balance = parseFloat(document.getElementById('initial-balance').value);

            if (!owner) {
                showAlert('account-alert', 'Please enter account owner name', 'error');
                return;
            }

            fetch(API_URL + '/accounts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({owner, account_type: type, initial_balance: balance})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showAlert('account-alert', 'Account created successfully', 'success');
                    document.getElementById('owner-name').value = '';
                    document.getElementById('initial-balance').value = '0';
                    loadAccounts();
                    loadDashboard();
                } else {
                    showAlert('account-alert', data.error, 'error');
                }
            });
        }

        // Process transaction
        function processTransaction() {
            const accountId = document.getElementById('from-account').value;
            const type = document.getElementById('transaction-type').value;
            const amount = parseFloat(document.getElementById('amount').value);
            const description = document.getElementById('description').value;

            if (!amount || amount <= 0 || !description) {
                showAlert('transaction-alert', 'Please fill all fields with valid values', 'error');
                return;
            }

            fetch(API_URL + '/transactions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    account_id: accountId,
                    transaction_type: type,
                    amount,
                    description
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showAlert('transaction-alert', `Transaction ${data.transaction.transaction_id} processed successfully`, 'success');
                    document.getElementById('amount').value = '';
                    document.getElementById('description').value = '';
                    loadTransactions();
                    loadDashboard();
                } else {
                    showAlert('transaction-alert', data.error, 'error');
                }
            });
        }

        // AI Validation
        function validateWithAI() {
            const accountId = document.getElementById('val-account').value;
            const amount = parseFloat(document.getElementById('val-amount').value);
            const type = document.getElementById('val-type').value;

            if (!amount || !accountId) {
                showAlert('validation-alert', 'Please fill all required fields', 'error');
                return;
            }

            document.getElementById('validation-result').innerHTML = '<p style="color: var(--gray-600); margin-top: 1rem;">Processing analysis...</p>';

            fetch(API_URL + '/banking-ai/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({account_id: accountId, amount, transaction_type: type, description: 'AI Validation'})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('validation-result').innerHTML = `
                        <div class="ai-panel">
                            <div class="ai-panel-title">Risk Analysis Results</div>
                            <div class="ai-panel-content">${data.validation}</div>
                        </div>
                    `;
                } else {
                    showAlert('validation-alert', data.error, 'error');
                }
            });
        }

        // Financial Advice
        function getFinancialAdvice() {
            const accountId = document.getElementById('advice-account').value;

            if (!accountId) {
                showAlert('advice-alert', 'Please select an account', 'error');
                return;
            }

            document.getElementById('advice-result').innerHTML = '<p style="color: var(--gray-600); margin-top: 1rem;">Generating recommendations...</p>';

            fetch(API_URL + '/banking-ai/advice', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({account_id: accountId})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('advice-result').innerHTML = `
                        <div class="ai-panel">
                            <div class="ai-panel-title">Financial Recommendations</div>
                            <div class="ai-panel-content">${data.advice}</div>
                        </div>
                    `;
                } else {
                    showAlert('advice-alert', data.error, 'error');
                }
            });
        }

        // Load agents data
        function loadAgentsData() {
            loadAccounts();
        }

        // Load analytics
        function loadAnalytics() {
            fetch(API_URL + '/analytics')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const a = data.analytics;

                        // Transaction by type chart
                        const typeData = a.transactions_by_type || {};
                        Plotly.newPlot('chart-by-type', [{
                            x: Object.keys(typeData),
                            y: Object.values(typeData),
                            type: 'bar',
                            marker: {color: '#003366'}
                        }], {
                            title: 'Transaction Volume by Type',
                            font: {family: 'Inter, sans-serif', size: 14},
                            paper_bgcolor: '#FFFFFF',
                            plot_bgcolor: '#F8F9FA',
                            margin: {t: 60, b: 60, l: 60, r: 40}
                        });

                        // Status distribution chart
                        Plotly.newPlot('chart-status-distribution', [{
                            labels: ['Approved', 'Pending'],
                            values: [a.approved_transactions, a.pending_transactions],
                            type: 'pie',
                            marker: {colors: ['#10B981', '#D97706']},
                            textfont: {family: 'Inter, sans-serif', size: 14}
                        }], {
                            title: 'Transaction Status Distribution',
                            font: {family: 'Inter, sans-serif', size: 14},
                            paper_bgcolor: '#FFFFFF',
                            margin: {t: 60, b: 40, l: 40, r: 40}
                        });

                        // Account balances chart
                        const accounts = a.accounts || [];
                        Plotly.newPlot('chart-account-balances', [{
                            x: accounts.map(acc => acc.owner),
                            y: accounts.map(acc => acc.balance),
                            type: 'bar',
                            marker: {color: '#3B82F6'}
                        }], {
                            title: 'Account Balances Overview',
                            font: {family: 'Inter, sans-serif', size: 14},
                            paper_bgcolor: '#FFFFFF',
                            plot_bgcolor: '#F8F9FA',
                            yaxis: {title: 'Balance (USD)'},
                            margin: {t: 60, b: 80, l: 60, r: 40}
                        });
                    }
                });
        }

        // Show alert
        function showAlert(elementId, message, type) {
            const alert = document.getElementById(elementId);
            if (alert) {
                alert.textContent = message;
                alert.className = `alert alert-${type} show`;
                setTimeout(() => {
                    alert.classList.remove('show');
                }, 5000);
            }
        }

        // Initialize
        updateStatus();
        loadDashboard();
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
"""

# ============================================================================
# API PROXY ROUTES
# ============================================================================

def make_request(method, endpoint, data=None):
    """Make request to backend API"""
    try:
        url = f"{BACKEND_URL}/api{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10, headers={'Content-Type': 'application/json'})

        return response.json() if response.ok else {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        log("ERROR", f"API request failed: {str(e)}")
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    log("INFO", "Dashboard accessed")
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/<path:endpoint>', methods=['GET', 'POST'])
def proxy_api(endpoint):
    method = request.method
    data = request.get_json() if method == 'POST' else None
    log("INFO", f"{method} request to /{endpoint}")
    result = make_request(method, f"/{endpoint}", data)
    return jsonify(result)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    log("INFO", "=" * 80)
    log("INFO", "ARC BAAS - BANKING AS A SERVICE PLATFORM")
    log("INFO", "=" * 80)
    log("INFO", "Frontend Dashboard: http://localhost:5000")
    log("INFO", "Backend API: http://localhost:5001")
    log("INFO", "=" * 80)
    log("SUCCESS", "System initialization complete")

    app.run(debug=False, port=5000, host='0.0.0.0')
