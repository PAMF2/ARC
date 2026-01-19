"""
Bank As A Service (BaaS) - Professional Dashboard
English version with backend integration and AI features
"""

import requests
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Backend API base URL
BACKEND_URL = "http://localhost:5001"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bank As A Service - Professional Banking Platform</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0F0F0F 0%, #1A1A1A 100%);
            color: #E0E0E0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #00D4FF 0%, #0099CC 100%);
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
        }
        
        .header h1 {
            font-size: 36px;
            color: white;
            margin-bottom: 5px;
        }
        
        .header p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1A1A1A;
            padding: 15px 20px;
            border-radius: 6px;
            margin-top: 20px;
            font-size: 12px;
            color: #999;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #333;
            overflow-x: auto;
        }
        
        .tab-btn {
            padding: 12px 24px;
            background: transparent;
            border: none;
            color: #999;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .tab-btn:hover {
            color: #00D4FF;
        }
        
        .tab-btn.active {
            color: #00D4FF;
            border-bottom-color: #00D4FF;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #00D4FF;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .stat-card h3 {
            font-size: 12px;
            color: #999;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-card .value {
            font-size: 28px;
            color: #00D4FF;
            font-weight: 600;
        }
        
        .stat-card .subtext {
            font-size: 12px;
            color: #666;
            margin-top: 8px;
        }
        
        .account-card, .transaction-card {
            background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #00D4FF;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .account-info, .transaction-info {
            flex: 1;
        }
        
        .account-info h4, .transaction-info h4 {
            color: #E0E0E0;
            margin-bottom: 5px;
        }
        
        .account-info p, .transaction-info p {
            font-size: 12px;
            color: #999;
        }
        
        .account-balance, .transaction-details {
            text-align: right;
        }
        
        .account-balance .amount, .transaction-details .amount {
            font-size: 24px;
            color: #00D4FF;
            font-weight: 600;
        }
        
        .transaction-status {
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
            font-weight: 500;
            margin-top: 5px;
        }
        
        .status-approved {
            background: rgba(81, 207, 102, 0.2);
            color: #51CF66;
        }
        
        .status-pending {
            background: rgba(255, 159, 64, 0.2);
            color: #FF9F40;
        }
        
        .status-blocked {
            background: rgba(255, 107, 107, 0.2);
            color: #FF6B6B;
        }
        
        .form-section {
            background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #00D4FF;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            background: #252525;
            border: 1px solid #333;
            border-radius: 6px;
            color: #E0E0E0;
            font-size: 14px;
            font-family: inherit;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #00D4FF;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
        }
        
        .button {
            background: linear-gradient(135deg, #00D4FF 0%, #0099CC 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 212, 255, 0.3);
        }
        
        .button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .chart-container {
            background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #00D4FF;
            margin-bottom: 20px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            display: none;
        }
        
        .alert.success {
            background: rgba(81, 207, 102, 0.1);
            color: #51CF66;
            border-left: 4px solid #51CF66;
            display: block;
        }
        
        .alert.error {
            background: rgba(255, 107, 107, 0.1);
            color: #FF6B6B;
            border-left: 4px solid #FF6B6B;
            display: block;
        }
        
        .ai-panel {
            background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #FFD700;
            margin-bottom: 20px;
        }
        
        .ai-panel h3 {
            color: #FFD700;
            margin-bottom: 10px;
        }
        
        .ai-content {
            color: #E0E0E0;
            line-height: 1.6;
            font-size: 13px;
        }
        
        .grid-2col {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            background: #333;
            color: #999;
            border-radius: 20px;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bank As A Service</h1>
            <p>Professional Banking Platform with AI-Powered Intelligence</p>
            <div class="status-bar">
                <span id="status-health">Status: Initializing...</span>
                <span id="status-time"></span>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('dashboard')">Dashboard</button>
            <button class="tab-btn" onclick="showTab('accounts')">Accounts</button>
            <button class="tab-btn" onclick="showTab('transactions')">Transactions</button>
            <button class="tab-btn" onclick="showTab('ai-services')">AI Services</button>
            <button class="tab-btn" onclick="showTab('analytics')">Analytics</button>
            <button class="tab-btn" onclick="showTab('settings')">Settings</button>
        </div>
        
        <!-- Dashboard -->
        <div id="dashboard" class="tab-content active">
            <div class="stats-grid" id="dashboard-stats"></div>
            <h2 style="margin: 30px 0 20px; color: #E0E0E0;">Recent Accounts</h2>
            <div id="dashboard-accounts"></div>
        </div>
        
        <!-- Accounts Tab -->
        <div id="accounts" class="tab-content">
            <h2 style="margin-bottom: 20px; color: #E0E0E0;">Account Management</h2>
            <div id="accounts-list"></div>
            
            <h2 style="margin-top: 40px; margin-bottom: 20px; color: #E0E0E0;">Create New Account</h2>
            <div class="form-section" style="max-width: 500px;">
                <div id="create-alert"></div>
                <div class="form-group">
                    <label>Account Owner Name</label>
                    <input type="text" placeholder="Full name" id="owner-name">
                </div>
                <div class="form-group">
                    <label>Account Type</label>
                    <select id="account-type">
                        <option>Checking</option>
                        <option>Savings</option>
                        <option>Investment</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Initial Balance</label>
                    <input type="number" placeholder="0.00" id="initial-balance" value="0" step="0.01">
                </div>
                <button class="button" onclick="createAccount()">Create Account</button>
            </div>
        </div>
        
        <!-- Transactions Tab -->
        <div id="transactions" class="tab-content">
            <h2 style="margin-bottom: 20px; color: #E0E0E0;">Transaction History</h2>
            <div id="transactions-list"></div>
            
            <h2 style="margin-top: 40px; margin-bottom: 20px; color: #E0E0E0;">Process New Transaction</h2>
            <div class="form-section" style="max-width: 500px;">
                <div id="txn-alert"></div>
                <div class="form-group">
                    <label>Source Account</label>
                    <select id="from-account"></select>
                </div>
                <div class="form-group">
                    <label>Transaction Type</label>
                    <select id="transaction-type">
                        <option>Debit</option>
                        <option>Credit</option>
                        <option>Transfer</option>
                        <option>Withdrawal</option>
                        <option>Deposit</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Amount (USD)</label>
                    <input type="number" placeholder="0.00" id="amount" step="0.01">
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <input type="text" placeholder="Transaction description" id="description">
                </div>
                <button class="button" onclick="processTransaction()">Process Transaction</button>
            </div>
        </div>
        
        <!-- AI Services -->
        <div id="ai-services" class="tab-content">
            <h2 style="margin-bottom: 20px; color: #E0E0E0;">AI-Powered Banking Services</h2>
            
            <div class="grid-2col">
                <div class="form-section">
                    <h3 style="color: #00D4FF; margin-bottom: 15px;">Transaction Validation</h3>
                    <p style="color: #999; margin-bottom: 20px; font-size: 12px;">Analyze transactions for fraud risk and security threats</p>
                    <div id="validation-alert"></div>
                    <div class="form-group">
                        <label>Account ID</label>
                        <input type="text" placeholder="ACC001" id="val-account">
                    </div>
                    <div class="form-group">
                        <label>Amount</label>
                        <input type="number" placeholder="1000" id="val-amount">
                    </div>
                    <div class="form-group">
                        <label>Type</label>
                        <select id="val-type">
                            <option>Debit</option>
                            <option>Credit</option>
                        </select>
                    </div>
                    <button class="button" onclick="validateWithAI()" style="width: 100%;">Analyze Risk</button>
                    <div id="validation-result" style="margin-top: 15px;"></div>
                </div>
                
                <div class="form-section">
                    <h3 style="color: #FFD700; margin-bottom: 15px;">Financial Advice</h3>
                    <p style="color: #999; margin-bottom: 20px; font-size: 12px;">Get AI-powered recommendations based on your account activity</p>
                    <div id="advice-alert"></div>
                    <div class="form-group">
                        <label>Select Account</label>
                        <select id="advice-account"></select>
                    </div>
                    <button class="button" onclick="getFinancialAdvice()" style="width: 100%;">Get Advice</button>
                    <div id="advice-result" style="margin-top: 15px;"></div>
                </div>
            </div>
        </div>
        
        <!-- Analytics -->
        <div id="analytics" class="tab-content">
            <h2 style="margin-bottom: 20px; color: #E0E0E0;">Banking Analytics</h2>
            <div class="chart-container">
                <div id="chart-by-type"></div>
            </div>
            <div class="chart-container">
                <div id="chart-summary"></div>
            </div>
        </div>
        
        <!-- Settings -->
        <div id="settings" class="tab-content">
            <h2 style="margin-bottom: 20px; color: #E0E0E0;">Configuration</h2>
            <div class="form-section" style="max-width: 500px;">
                <div class="form-group">
                    <label>Transfer Limit (USD)</label>
                    <input type="number" value="10000" placeholder="10000">
                </div>
                <div class="form-group">
                    <label>Daily Withdrawal Limit (USD)</label>
                    <input type="number" value="5000" placeholder="5000">
                </div>
                <div class="form-group">
                    <label>Enable AI Fraud Detection</label>
                    <select>
                        <option>Enabled</option>
                        <option>Disabled</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Backup Frequency</label>
                    <select>
                        <option>Daily</option>
                        <option>Weekly</option>
                        <option>Monthly</option>
                    </select>
                </div>
                <button class="button">Save Settings</button>
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = '/api';
        
        // Tab switching
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'analytics') loadAnalytics();
            if (tabName === 'dashboard') loadDashboard();
            if (tabName === 'ai-services') loadAIServicesData();
        }
        
        // Update status bar
        function updateStatus() {
            fetch(API_URL + '/health')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status-health').innerHTML = `Status: <span style="color: #51CF66;">Healthy</span>`;
                })
                .catch(() => {
                    document.getElementById('status-health').innerHTML = `Status: <span style="color: #FF6B6B;">Offline</span>`;
                });
            
            document.getElementById('status-time').textContent = new Date().toLocaleTimeString();
        }
        
        // Load dashboard
        function loadDashboard() {
            fetch(API_URL + '/analytics')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const a = data.analytics;
                        const stats = `
                            <div class="stat-card">
                                <h3>Total Balance</h3>
                                <div class="value">$${a.total_balance.toFixed(2)}</div>
                                <div class="subtext">${a.total_accounts} active accounts</div>
                            </div>
                            <div class="stat-card">
                                <h3>Transactions</h3>
                                <div class="value">${a.total_transactions}</div>
                                <div class="subtext">${a.approved_transactions} approved</div>
                            </div>
                            <div class="stat-card">
                                <h3>Pending</h3>
                                <div class="value">${a.pending_transactions}</div>
                                <div class="subtext">awaiting review</div>
                            </div>
                            <div class="stat-card">
                                <h3>Total Accounts</h3>
                                <div class="value">${a.total_accounts}</div>
                                <div class="subtext">active</div>
                            </div>
                        `;
                        document.getElementById('dashboard-stats').innerHTML = stats;
                        
                        const accounts = a.accounts.map(acc => `
                            <div class="account-card">
                                <div class="account-info">
                                    <h4>${acc.owner}</h4>
                                    <p>${acc.account_id} • ${acc.account_type}</p>
                                </div>
                                <div class="account-balance">
                                    <div class="amount">$${acc.balance.toFixed(2)}</div>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('dashboard-accounts').innerHTML = accounts;
                    }
                });
        }
        
        // Load accounts
        function loadAccounts() {
            fetch(API_URL + '/accounts')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const accounts = data.accounts.map(acc => `
                            <div class="account-card">
                                <div class="account-info">
                                    <h4>${acc.owner}</h4>
                                    <p>${acc.account_id} • ${acc.account_type}</p>
                                </div>
                                <div class="account-balance">
                                    <div class="amount">$${acc.balance.toFixed(2)}</div>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('accounts-list').innerHTML = accounts;
                        
                        // Populate account selectors
                        const options = data.accounts.map(acc => 
                            `<option value="${acc.account_id}">${acc.owner} (${acc.account_id}) - $${acc.balance.toFixed(2)}</option>`
                        ).join('');
                        document.getElementById('from-account').innerHTML = options;
                        document.getElementById('advice-account').innerHTML = options;
                        document.getElementById('val-account').value = data.accounts[0]?.account_id || '';
                    }
                });
        }
        
        // Load transactions
        function loadTransactions() {
            fetch(API_URL + '/transactions')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const txns = data.transactions.map(tx => `
                            <div class="transaction-card">
                                <div class="transaction-info">
                                    <h4>${tx.description}</h4>
                                    <p>${tx.date} • ${tx.transaction_type}</p>
                                </div>
                                <div class="transaction-details">
                                    <div class="amount">$${tx.amount.toFixed(2)}</div>
                                    <div class="transaction-status status-${tx.status.toLowerCase()}">${tx.status}</div>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('transactions-list').innerHTML = txns || '<p style="color: #666;">No transactions yet</p>';
                    }
                });
        }
        
        // Create account
        function createAccount() {
            const owner = document.getElementById('owner-name').value;
            const type = document.getElementById('account-type').value;
            const balance = parseFloat(document.getElementById('initial-balance').value);
            
            if (!owner) {
                showAlert('create-alert', 'Please enter owner name', 'error');
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
                    showAlert('create-alert', 'Account created successfully!', 'success');
                    document.getElementById('owner-name').value = '';
                    document.getElementById('initial-balance').value = '0';
                    loadAccounts();
                } else {
                    showAlert('create-alert', data.error, 'error');
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
                showAlert('txn-alert', 'Please fill all fields with valid values', 'error');
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
                    showAlert('txn-alert', `Transaction ${data.transaction.transaction_id} processed!`, 'success');
                    document.getElementById('amount').value = '';
                    document.getElementById('description').value = '';
                    loadTransactions();
                    loadDashboard();
                } else {
                    showAlert('txn-alert', data.error, 'error');
                }
            });
        }
        
        // AI Validation
        function validateWithAI() {
            const accountId = document.getElementById('val-account').value;
            const amount = parseFloat(document.getElementById('val-amount').value);
            const type = document.getElementById('val-type').value;
            
            if (!amount || !accountId) {
                showAlert('validation-alert', 'Please fill all fields', 'error');
                return;
            }
            
            document.getElementById('validation-result').innerHTML = '<p style="color: #999;">Analyzing...</p>';
            
            fetch(API_URL + '/banking-ai/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({account_id: accountId, amount, transaction_type: type, description: 'AI Analysis'})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('validation-result').innerHTML = `
                        <div class="ai-panel">
                            <h4 style="color: #00D4FF;">AI Risk Analysis</h4>
                            <p style="color: #E0E0E0; margin-top: 10px;">${data.validation}</p>
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
            
            document.getElementById('advice-result').innerHTML = '<p style="color: #999;">Generating recommendations...</p>';
            
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
                            <h4 style="color: #FFD700;">Financial Recommendations</h4>
                            <p style="color: #E0E0E0; margin-top: 10px;">${data.advice}</p>
                        </div>
                    `;
                } else {
                    showAlert('advice-alert', data.error, 'error');
                }
            });
        }
        
        // Load AI Services data
        function loadAIServicesData() {
            loadAccounts();
        }
        
        // Load analytics
        function loadAnalytics() {
            fetch(API_URL + '/analytics')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const a = data.analytics;
                        
                        // Chart by type
                        const typeData = a.transactions_by_type || {};
                        Plotly.newPlot('chart-by-type', [{
                            x: Object.keys(typeData),
                            y: Object.values(typeData),
                            type: 'bar',
                            marker: {color: '#00D4FF'}
                        }], {
                            title: 'Transaction Volume by Type',
                            paper_bgcolor: '#252525',
                            plot_bgcolor: '#1A1A1A',
                            font: {color: '#E0E0E0'},
                            margin: {t: 40, b: 40, l: 60, r: 40}
                        });
                        
                        // Summary chart
                        Plotly.newPlot('chart-summary', [{
                            labels: ['Approved', 'Pending'],
                            values: [a.approved_transactions, a.pending_transactions],
                            type: 'pie',
                            marker: {colors: ['#51CF66', '#FF9F40']}
                        }], {
                            title: 'Transaction Status Distribution',
                            paper_bgcolor: '#252525',
                            plot_bgcolor: '#1A1A1A',
                            font: {color: '#E0E0E0'},
                            margin: {t: 40, b: 40, l: 60, r: 40}
                        });
                    }
                });
        }
        
        // Show alert
        function showAlert(elementId, message, type) {
            const alert = document.getElementById(elementId);
            if (alert) {
                alert.textContent = message;
                alert.className = 'alert ' + type;
                setTimeout(() => {
                    alert.className = 'alert';
                    alert.style.display = 'none';
                }, 4000);
            }
        }
        
        // Initial load
        updateStatus();
        loadDashboard();
        loadAccounts();
        loadTransactions();
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
"""

# ============================================================================
# FRONTEND API PROXY ROUTES
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
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Proxy routes to backend
@app.route('/api/<path:endpoint>', methods=['GET', 'POST'])
def proxy_api(endpoint):
    method = request.method
    data = request.get_json() if method == 'POST' else None
    result = make_request(method, f"/{endpoint}", data)
    return jsonify(result)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("BANK AS A SERVICE (BaaS) - FRONTEND DASHBOARD")
    print("="*70)
    print("\nFrontend Dashboard running on: http://localhost:5000")
    print("Backend API running on:       http://localhost:5001")
    print("="*70 + "\n")
    
    app.run(debug=False, port=5000, host='0.0.0.0')
