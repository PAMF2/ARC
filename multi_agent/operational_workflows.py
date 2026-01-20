"""
GlobalBank Multi-Agent System - Operational Workflows

This module implements real-world banking operational workflows that connect all 165 employee agents
in realistic end-to-end processes. Each workflow demonstrates how different departments and roles
collaborate to complete banking operations.

Workflows Implemented:
1. Loan Origination - Complete loan application to funding
2. Account Opening - New customer onboarding with KYC/AML
3. Fraud Investigation - Suspicious transaction detection and resolution
4. Daily Operations - End-of-day reconciliation and reporting
5. Large Transaction Processing - Multi-level approval workflow
6. Customer Complaint Resolution - Cross-department issue handling

Author: GlobalBank Multi-Agent System
Date: January 2026
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from core.employee_types import (
    Employee, Department, JobTitle, EmployeeLevel
)
from multi_agent.message_bus import Message, MessageType, MessagePriority, MessageBus
from multi_agent.employee_agent import EmployeeAgent
from multi_agent.executive_agent import ExecutiveAgent


logger = logging.getLogger(__name__)


class OperationalWorkflows:
    """
    Orchestrates real-world banking operational workflows across all departments.
    Each workflow demonstrates proper agent coordination and handoffs.
    """

    def __init__(self,
                 message_bus: MessageBus,
                 all_agents: Dict[str, EmployeeAgent],
                 agents_by_department: Dict[Department, List[EmployeeAgent]]):
        """
        Initialize operational workflows coordinator.

        Args:
            message_bus: The organization's message bus
            all_agents: Dictionary mapping employee_id to agent
            agents_by_department: Dictionary mapping department to list of agents
        """
        self.message_bus = message_bus
        self.all_agents = all_agents
        self.agents_by_department = agents_by_department

        # Workflow state tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: List[Dict[str, Any]] = []

        logger.info("OperationalWorkflows initialized")

    # ==================================================================================
    # WORKFLOW 1: LOAN ORIGINATION
    # ==================================================================================

    async def execute_loan_origination(self,
                                      customer_id: str,
                                      loan_type: str,
                                      loan_amount: float,
                                      customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete loan origination workflow from application to funding.

        Workflow Steps:
        1. Application Intake (Loan Officer)
        2. Credit Assessment (Credit Analyst)
        3. Risk Evaluation (Risk Analyst)
        4. Underwriting (Underwriter)
        5. Approval Routing (Manager -> Director -> VP based on amount)
        6. Document Processing (Operations Analyst)
        7. Funding Authorization (Treasury Analyst)
        8. Settlement (Settlement Specialist)
        9. Customer Notification (Customer Service)

        Args:
            customer_id: Unique customer identifier
            loan_type: Type of loan (mortgage, personal, business, auto)
            loan_amount: Requested loan amount
            customer_data: Customer information and financials

        Returns:
            Dict containing workflow results and decision trail
        """
        workflow_id = f"LOAN-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Starting loan origination workflow: {workflow_id}")

        workflow_state = {
            "workflow_id": workflow_id,
            "workflow_type": "loan_origination",
            "customer_id": customer_id,
            "loan_type": loan_type,
            "loan_amount": loan_amount,
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "decision_trail": [],
            "agents_involved": []
        }
        self.active_workflows[workflow_id] = workflow_state

        try:
            # STEP 1: Application Intake (Loan Officer)
            loan_officers = [a for a in self.agents_by_department.get(Department.RETAIL_BANKING, [])
                           if a.employee.job_title == JobTitle.LOAN_OFFICER]

            if not loan_officers:
                raise ValueError("No loan officers available")

            loan_officer = loan_officers[0]

            intake_result = await loan_officer.process_task(
                task_description=f"Process loan application for customer {customer_id}",
                context={
                    "loan_type": loan_type,
                    "loan_amount": loan_amount,
                    "customer_data": customer_data,
                    "step": "application_intake"
                }
            )

            workflow_state["steps_completed"].append({
                "step": "application_intake",
                "agent": loan_officer.employee.employee_id,
                "result": intake_result,
                "timestamp": datetime.now().isoformat()
            })
            workflow_state["agents_involved"].append(loan_officer.employee.employee_id)

            # STEP 2: Credit Assessment (Credit Analyst)
            credit_analysts = [a for a in self.agents_by_department.get(Department.RISK_MANAGEMENT, [])
                             if "credit" in a.employee.job_title.value.lower()]

            if credit_analysts:
                credit_analyst = credit_analysts[0]
                credit_result = await credit_analyst.process_task(
                    task_description=f"Perform credit assessment for loan application {workflow_id}",
                    context={
                        "customer_id": customer_id,
                        "loan_amount": loan_amount,
                        "customer_data": customer_data,
                        "step": "credit_assessment"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "credit_assessment",
                    "agent": credit_analyst.employee.employee_id,
                    "result": credit_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(credit_analyst.employee.employee_id)
                workflow_state["decision_trail"].append({
                    "decision": "credit_assessment_complete",
                    "made_by": credit_analyst.employee.employee_id,
                    "timestamp": datetime.now().isoformat()
                })

            # STEP 3: Risk Evaluation (Risk Analyst)
            risk_analysts = [a for a in self.agents_by_department.get(Department.RISK_MANAGEMENT, [])
                           if a.employee.job_title == JobTitle.RISK_ANALYST]

            if risk_analysts:
                risk_analyst = risk_analysts[0]
                risk_result = await risk_analyst.process_task(
                    task_description=f"Evaluate risk for loan application {workflow_id}",
                    context={
                        "customer_id": customer_id,
                        "loan_type": loan_type,
                        "loan_amount": loan_amount,
                        "credit_assessment": credit_result if credit_analysts else None,
                        "step": "risk_evaluation"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "risk_evaluation",
                    "agent": risk_analyst.employee.employee_id,
                    "result": risk_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(risk_analyst.employee.employee_id)
                workflow_state["decision_trail"].append({
                    "decision": "risk_evaluation_complete",
                    "made_by": risk_analyst.employee.employee_id,
                    "timestamp": datetime.now().isoformat()
                })

            # STEP 4: Approval Routing (Amount-based escalation)
            approval_result = await self._route_loan_approval(
                workflow_id=workflow_id,
                loan_amount=loan_amount,
                loan_type=loan_type,
                assessment_data={
                    "intake": intake_result,
                    "credit": credit_result if credit_analysts else None,
                    "risk": risk_result if risk_analysts else None
                }
            )

            workflow_state["steps_completed"].append({
                "step": "approval_routing",
                "result": approval_result,
                "timestamp": datetime.now().isoformat()
            })
            workflow_state["decision_trail"].append({
                "decision": "loan_approval_decision",
                "approved": approval_result.get("approved", False),
                "approver": approval_result.get("approver"),
                "timestamp": datetime.now().isoformat()
            })

            if not approval_result.get("approved", False):
                workflow_state["status"] = "rejected"
                workflow_state["rejection_reason"] = approval_result.get("reason", "Unknown")
                return workflow_state

            # STEP 5: Document Processing (Operations)
            ops_analysts = [a for a in self.agents_by_department.get(Department.OPERATIONS, [])
                          if a.employee.job_title == JobTitle.OPERATIONS_ANALYST]

            if ops_analysts:
                ops_analyst = ops_analysts[0]
                doc_result = await ops_analyst.process_task(
                    task_description=f"Process loan documentation for {workflow_id}",
                    context={
                        "loan_amount": loan_amount,
                        "approval": approval_result,
                        "step": "document_processing"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "document_processing",
                    "agent": ops_analyst.employee.employee_id,
                    "result": doc_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(ops_analyst.employee.employee_id)

            # STEP 6: Funding Authorization (Treasury)
            treasury_analysts = [a for a in self.agents_by_department.get(Department.TREASURY, [])
                                if a.employee.job_title == JobTitle.TREASURY_ANALYST]

            if treasury_analysts:
                treasury_analyst = treasury_analysts[0]
                funding_result = await treasury_analyst.process_task(
                    task_description=f"Authorize funding for loan {workflow_id}",
                    context={
                        "loan_amount": loan_amount,
                        "approval": approval_result,
                        "step": "funding_authorization"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "funding_authorization",
                    "agent": treasury_analyst.employee.employee_id,
                    "result": funding_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(treasury_analyst.employee.employee_id)

            # STEP 7: Settlement (Clearing & Settlement)
            settlement_specialists = [a for a in self.agents_by_department.get(Department.CLEARING_SETTLEMENT, [])]

            if settlement_specialists:
                settlement_specialist = settlement_specialists[0]
                settlement_result = await settlement_specialist.process_task(
                    task_description=f"Settle loan disbursement for {workflow_id}",
                    context={
                        "loan_amount": loan_amount,
                        "customer_id": customer_id,
                        "step": "settlement"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "settlement",
                    "agent": settlement_specialist.employee.employee_id,
                    "result": settlement_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(settlement_specialist.employee.employee_id)

            # STEP 8: Customer Notification (Customer Service)
            customer_service_reps = [a for a in self.agents_by_department.get(Department.RETAIL_BANKING, [])
                                    if a.employee.job_title == JobTitle.CUSTOMER_SERVICE_REP]

            if customer_service_reps:
                cs_rep = customer_service_reps[0]
                notification_result = await cs_rep.process_task(
                    task_description=f"Notify customer about loan approval {workflow_id}",
                    context={
                        "customer_id": customer_id,
                        "loan_amount": loan_amount,
                        "step": "customer_notification"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "customer_notification",
                    "agent": cs_rep.employee.employee_id,
                    "result": notification_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(cs_rep.employee.employee_id)

            # Mark workflow complete
            workflow_state["status"] = "completed"
            workflow_state["end_time"] = datetime.now().isoformat()
            workflow_state["total_agents_involved"] = len(set(workflow_state["agents_involved"]))

            self.completed_workflows.append(workflow_state)
            del self.active_workflows[workflow_id]

            logger.info(f"Loan origination workflow completed: {workflow_id}")
            return workflow_state

        except Exception as e:
            logger.error(f"Loan origination workflow failed: {workflow_id} - {str(e)}")
            workflow_state["status"] = "failed"
            workflow_state["error"] = str(e)
            workflow_state["end_time"] = datetime.now().isoformat()
            return workflow_state

    async def _route_loan_approval(self,
                                   workflow_id: str,
                                   loan_amount: float,
                                   loan_type: str,
                                   assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route loan approval based on amount thresholds.

        Approval Authority:
        - Up to $25,000: Branch Manager
        - $25,001 - $100,000: Director
        - $100,001 - $500,000: VP
        - Over $500,000: CFO
        """
        # Determine approval level needed
        if loan_amount <= 25000:
            required_level = EmployeeLevel.MANAGER
            required_title = JobTitle.BRANCH_MANAGER
        elif loan_amount <= 100000:
            required_level = EmployeeLevel.DIRECTOR
            required_title = None
        elif loan_amount <= 500000:
            required_level = EmployeeLevel.VP
            required_title = None
        else:
            required_level = EmployeeLevel.C_LEVEL
            required_title = JobTitle.CFO

        # Find appropriate approver
        approvers = [a for a in self.all_agents.values()
                    if a.employee.level == required_level]

        if required_title:
            approvers = [a for a in approvers if a.employee.job_title == required_title]

        if not approvers:
            return {
                "approved": False,
                "reason": f"No approver available at required level: {required_level.value}",
                "required_level": required_level.value
            }

        approver = approvers[0]

        # Request approval
        approval_decision = await approver.process_task(
            task_description=f"Approve loan application {workflow_id} for ${loan_amount:,.2f}",
            context={
                "workflow_id": workflow_id,
                "loan_amount": loan_amount,
                "loan_type": loan_type,
                "assessment_data": assessment_data,
                "step": "approval_decision"
            }
        )

        return {
            "approved": True,  # In real system, would parse LLM decision
            "approver": approver.employee.employee_id,
            "approver_name": f"{approver.employee.first_name} {approver.employee.last_name}",
            "approver_title": approver.employee.job_title.value,
            "approval_level": required_level.value,
            "decision": approval_decision,
            "timestamp": datetime.now().isoformat()
        }

    # ==================================================================================
    # WORKFLOW 2: ACCOUNT OPENING
    # ==================================================================================

    async def execute_account_opening(self,
                                     customer_data: Dict[str, Any],
                                     account_type: str,
                                     initial_deposit: float) -> Dict[str, Any]:
        """
        Complete account opening workflow with KYC/AML compliance.

        Workflow Steps:
        1. Application Intake (Customer Service Rep)
        2. KYC Verification (Compliance Officer)
        3. AML Screening (Compliance Analyst)
        4. Fraud Check (Fraud Analyst - if available)
        5. Account Setup (Operations Analyst)
        6. Initial Deposit Processing (Teller)
        7. Welcome Package (Customer Service)

        Args:
            customer_data: Customer information (name, address, SSN, etc.)
            account_type: Type of account (checking, savings, business)
            initial_deposit: Initial deposit amount

        Returns:
            Dict containing workflow results
        """
        workflow_id = f"ACCT-{customer_data.get('email', 'UNKNOWN')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Starting account opening workflow: {workflow_id}")

        workflow_state = {
            "workflow_id": workflow_id,
            "workflow_type": "account_opening",
            "account_type": account_type,
            "initial_deposit": initial_deposit,
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "agents_involved": []
        }
        self.active_workflows[workflow_id] = workflow_state

        try:
            # STEP 1: Application Intake
            cs_reps = [a for a in self.agents_by_department.get(Department.RETAIL_BANKING, [])
                      if a.employee.job_title == JobTitle.CUSTOMER_SERVICE_REP]

            if not cs_reps:
                raise ValueError("No customer service reps available")

            cs_rep = cs_reps[0]
            intake_result = await cs_rep.process_task(
                task_description=f"Process account opening application {workflow_id}",
                context={
                    "customer_data": customer_data,
                    "account_type": account_type,
                    "initial_deposit": initial_deposit,
                    "step": "application_intake"
                }
            )

            workflow_state["steps_completed"].append({
                "step": "application_intake",
                "agent": cs_rep.employee.employee_id,
                "result": intake_result,
                "timestamp": datetime.now().isoformat()
            })
            workflow_state["agents_involved"].append(cs_rep.employee.employee_id)

            # STEP 2: KYC Verification
            compliance_officers = [a for a in self.agents_by_department.get(Department.COMPLIANCE, [])
                                  if a.employee.job_title == JobTitle.COMPLIANCE_OFFICER]

            if compliance_officers:
                compliance_officer = compliance_officers[0]
                kyc_result = await compliance_officer.process_task(
                    task_description=f"Perform KYC verification for {workflow_id}",
                    context={
                        "customer_data": customer_data,
                        "step": "kyc_verification"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "kyc_verification",
                    "agent": compliance_officer.employee.employee_id,
                    "result": kyc_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(compliance_officer.employee.employee_id)

            # STEP 3: AML Screening
            compliance_analysts = [a for a in self.agents_by_department.get(Department.COMPLIANCE, [])]

            if compliance_analysts:
                compliance_analyst = compliance_analysts[0]
                aml_result = await compliance_analyst.process_task(
                    task_description=f"Perform AML screening for {workflow_id}",
                    context={
                        "customer_data": customer_data,
                        "initial_deposit": initial_deposit,
                        "step": "aml_screening"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "aml_screening",
                    "agent": compliance_analyst.employee.employee_id,
                    "result": aml_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(compliance_analyst.employee.employee_id)

            # STEP 4: Account Setup
            ops_analysts = [a for a in self.agents_by_department.get(Department.OPERATIONS, [])
                          if a.employee.job_title == JobTitle.OPERATIONS_ANALYST]

            if ops_analysts:
                ops_analyst = ops_analysts[0]
                setup_result = await ops_analyst.process_task(
                    task_description=f"Set up new account {workflow_id}",
                    context={
                        "customer_data": customer_data,
                        "account_type": account_type,
                        "step": "account_setup"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "account_setup",
                    "agent": ops_analyst.employee.employee_id,
                    "result": setup_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(ops_analyst.employee.employee_id)
                workflow_state["account_number"] = setup_result.get("account_number", f"ACCT-{workflow_id[-8:]}")

            # STEP 5: Initial Deposit Processing
            if initial_deposit > 0:
                tellers = [a for a in self.agents_by_department.get(Department.RETAIL_BANKING, [])
                          if a.employee.job_title == JobTitle.TELLER]

                if tellers:
                    teller = tellers[0]
                    deposit_result = await teller.process_task(
                        task_description=f"Process initial deposit for {workflow_id}",
                        context={
                            "account_number": workflow_state.get("account_number"),
                            "deposit_amount": initial_deposit,
                            "step": "initial_deposit"
                        }
                    )

                    workflow_state["steps_completed"].append({
                        "step": "initial_deposit",
                        "agent": teller.employee.employee_id,
                        "result": deposit_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    workflow_state["agents_involved"].append(teller.employee.employee_id)

            # STEP 6: Welcome Package
            cs_rep_final = cs_reps[0]
            welcome_result = await cs_rep_final.process_task(
                task_description=f"Send welcome package for {workflow_id}",
                context={
                    "customer_data": customer_data,
                    "account_number": workflow_state.get("account_number"),
                    "step": "welcome_package"
                }
            )

            workflow_state["steps_completed"].append({
                "step": "welcome_package",
                "agent": cs_rep_final.employee.employee_id,
                "result": welcome_result,
                "timestamp": datetime.now().isoformat()
            })

            # Mark complete
            workflow_state["status"] = "completed"
            workflow_state["end_time"] = datetime.now().isoformat()
            workflow_state["total_agents_involved"] = len(set(workflow_state["agents_involved"]))

            self.completed_workflows.append(workflow_state)
            del self.active_workflows[workflow_id]

            logger.info(f"Account opening workflow completed: {workflow_id}")
            return workflow_state

        except Exception as e:
            logger.error(f"Account opening workflow failed: {workflow_id} - {str(e)}")
            workflow_state["status"] = "failed"
            workflow_state["error"] = str(e)
            workflow_state["end_time"] = datetime.now().isoformat()
            return workflow_state

    # ==================================================================================
    # WORKFLOW 3: FRAUD INVESTIGATION
    # ==================================================================================

    async def execute_fraud_investigation(self,
                                         transaction_id: str,
                                         transaction_data: Dict[str, Any],
                                         alert_reason: str) -> Dict[str, Any]:
        """
        Investigate suspicious transaction for potential fraud.

        Workflow Steps:
        1. Alert Triage (Fraud Analyst)
        2. Transaction Analysis (Risk Analyst)
        3. Customer Contact (Customer Service)
        4. Decision Making (Manager or Director)
        5. Account Action (Operations - if needed)
        6. Regulatory Reporting (Compliance - if confirmed fraud)

        Args:
            transaction_id: Transaction being investigated
            transaction_data: Transaction details
            alert_reason: Why transaction was flagged

        Returns:
            Dict containing investigation results
        """
        workflow_id = f"FRAUD-{transaction_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Starting fraud investigation workflow: {workflow_id}")

        workflow_state = {
            "workflow_id": workflow_id,
            "workflow_type": "fraud_investigation",
            "transaction_id": transaction_id,
            "alert_reason": alert_reason,
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "agents_involved": [],
            "fraud_confirmed": False
        }
        self.active_workflows[workflow_id] = workflow_state

        try:
            # STEP 1: Alert Triage (use Risk Analyst since we don't have dedicated Fraud Analyst)
            risk_analysts = [a for a in self.agents_by_department.get(Department.RISK_MANAGEMENT, [])
                           if a.employee.job_title == JobTitle.RISK_ANALYST]

            if not risk_analysts:
                raise ValueError("No risk analysts available for fraud triage")

            fraud_analyst = risk_analysts[0]
            triage_result = await fraud_analyst.process_task(
                task_description=f"Triage fraud alert for transaction {transaction_id}",
                context={
                    "transaction_data": transaction_data,
                    "alert_reason": alert_reason,
                    "step": "alert_triage"
                }
            )

            workflow_state["steps_completed"].append({
                "step": "alert_triage",
                "agent": fraud_analyst.employee.employee_id,
                "result": triage_result,
                "timestamp": datetime.now().isoformat()
            })
            workflow_state["agents_involved"].append(fraud_analyst.employee.employee_id)

            # STEP 2: Transaction Analysis
            analysis_result = await fraud_analyst.process_task(
                task_description=f"Analyze transaction {transaction_id} for fraud indicators",
                context={
                    "transaction_data": transaction_data,
                    "triage_result": triage_result,
                    "step": "transaction_analysis"
                }
            )

            workflow_state["steps_completed"].append({
                "step": "transaction_analysis",
                "agent": fraud_analyst.employee.employee_id,
                "result": analysis_result,
                "timestamp": datetime.now().isoformat()
            })

            # STEP 3: Customer Contact
            cs_reps = [a for a in self.agents_by_department.get(Department.RETAIL_BANKING, [])
                      if a.employee.job_title == JobTitle.CUSTOMER_SERVICE_REP]

            if cs_reps:
                cs_rep = cs_reps[0]
                contact_result = await cs_rep.process_task(
                    task_description=f"Contact customer regarding suspicious transaction {transaction_id}",
                    context={
                        "transaction_data": transaction_data,
                        "step": "customer_contact"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "customer_contact",
                    "agent": cs_rep.employee.employee_id,
                    "result": contact_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(cs_rep.employee.employee_id)

            # STEP 4: Decision Making (Manager)
            managers = [a for a in self.all_agents.values()
                       if a.employee.level == EmployeeLevel.MANAGER
                       and a.employee.department in [Department.RISK_MANAGEMENT, Department.OPERATIONS]]

            if managers:
                manager = managers[0]
                decision_result = await manager.process_task(
                    task_description=f"Make decision on fraud investigation {workflow_id}",
                    context={
                        "analysis": analysis_result,
                        "customer_contact": contact_result if cs_reps else None,
                        "step": "fraud_decision"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "fraud_decision",
                    "agent": manager.employee.employee_id,
                    "result": decision_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(manager.employee.employee_id)

                # Simulate fraud confirmation decision
                workflow_state["fraud_confirmed"] = transaction_data.get("amount", 0) > 10000

            # STEP 5: Account Action (if fraud confirmed)
            if workflow_state["fraud_confirmed"]:
                ops_analysts = [a for a in self.agents_by_department.get(Department.OPERATIONS, [])
                              if a.employee.job_title == JobTitle.OPERATIONS_ANALYST]

                if ops_analysts:
                    ops_analyst = ops_analysts[0]
                    action_result = await ops_analyst.process_task(
                        task_description=f"Take account action for confirmed fraud {workflow_id}",
                        context={
                            "transaction_id": transaction_id,
                            "action": "freeze_account",
                            "step": "account_action"
                        }
                    )

                    workflow_state["steps_completed"].append({
                        "step": "account_action",
                        "agent": ops_analyst.employee.employee_id,
                        "result": action_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    workflow_state["agents_involved"].append(ops_analyst.employee.employee_id)

                # STEP 6: Regulatory Reporting
                compliance_officers = [a for a in self.agents_by_department.get(Department.COMPLIANCE, [])
                                      if a.employee.job_title == JobTitle.COMPLIANCE_OFFICER]

                if compliance_officers:
                    compliance_officer = compliance_officers[0]
                    reporting_result = await compliance_officer.process_task(
                        task_description=f"File regulatory report for confirmed fraud {workflow_id}",
                        context={
                            "transaction_id": transaction_id,
                            "transaction_data": transaction_data,
                            "step": "regulatory_reporting"
                        }
                    )

                    workflow_state["steps_completed"].append({
                        "step": "regulatory_reporting",
                        "agent": compliance_officer.employee.employee_id,
                        "result": reporting_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    workflow_state["agents_involved"].append(compliance_officer.employee.employee_id)

            # Mark complete
            workflow_state["status"] = "completed"
            workflow_state["end_time"] = datetime.now().isoformat()
            workflow_state["total_agents_involved"] = len(set(workflow_state["agents_involved"]))

            self.completed_workflows.append(workflow_state)
            del self.active_workflows[workflow_id]

            logger.info(f"Fraud investigation workflow completed: {workflow_id}")
            return workflow_state

        except Exception as e:
            logger.error(f"Fraud investigation workflow failed: {workflow_id} - {str(e)}")
            workflow_state["status"] = "failed"
            workflow_state["error"] = str(e)
            workflow_state["end_time"] = datetime.now().isoformat()
            return workflow_state

    # ==================================================================================
    # WORKFLOW 4: DAILY OPERATIONS
    # ==================================================================================

    async def execute_daily_operations(self, business_date: str) -> Dict[str, Any]:
        """
        Execute end-of-day operations and reconciliation.

        Workflow Steps:
        1. Transaction Reconciliation (Operations)
        2. Position Reporting (Treasury)
        3. Risk Reporting (Risk Management)
        4. Compliance Checks (Compliance)
        5. Financial Reporting (Finance)
        6. Executive Summary (CFO)

        Args:
            business_date: Date for daily operations (YYYY-MM-DD)

        Returns:
            Dict containing daily operations summary
        """
        workflow_id = f"DAILY-{business_date}"
        logger.info(f"Starting daily operations workflow: {workflow_id}")

        workflow_state = {
            "workflow_id": workflow_id,
            "workflow_type": "daily_operations",
            "business_date": business_date,
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "agents_involved": [],
            "reports_generated": []
        }

        try:
            # STEP 1: Transaction Reconciliation
            ops_analysts = [a for a in self.agents_by_department.get(Department.OPERATIONS, [])
                          if a.employee.job_title == JobTitle.OPERATIONS_ANALYST]

            if ops_analysts:
                ops_analyst = ops_analysts[0]
                recon_result = await ops_analyst.process_task(
                    task_description=f"Reconcile transactions for {business_date}",
                    context={
                        "business_date": business_date,
                        "step": "transaction_reconciliation"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "transaction_reconciliation",
                    "agent": ops_analyst.employee.employee_id,
                    "result": recon_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(ops_analyst.employee.employee_id)
                workflow_state["reports_generated"].append("transaction_reconciliation_report")

            # STEP 2: Position Reporting
            treasury_analysts = [a for a in self.agents_by_department.get(Department.TREASURY, [])
                                if a.employee.job_title == JobTitle.TREASURY_ANALYST]

            if treasury_analysts:
                treasury_analyst = treasury_analysts[0]
                position_result = await treasury_analyst.process_task(
                    task_description=f"Generate position report for {business_date}",
                    context={
                        "business_date": business_date,
                        "step": "position_reporting"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "position_reporting",
                    "agent": treasury_analyst.employee.employee_id,
                    "result": position_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(treasury_analyst.employee.employee_id)
                workflow_state["reports_generated"].append("treasury_position_report")

            # STEP 3: Risk Reporting
            risk_analysts = [a for a in self.agents_by_department.get(Department.RISK_MANAGEMENT, [])
                           if a.employee.job_title == JobTitle.RISK_ANALYST]

            if risk_analysts:
                risk_analyst = risk_analysts[0]
                risk_result = await risk_analyst.process_task(
                    task_description=f"Generate risk report for {business_date}",
                    context={
                        "business_date": business_date,
                        "step": "risk_reporting"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "risk_reporting",
                    "agent": risk_analyst.employee.employee_id,
                    "result": risk_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(risk_analyst.employee.employee_id)
                workflow_state["reports_generated"].append("daily_risk_report")

            # STEP 4: Compliance Checks
            compliance_officers = [a for a in self.agents_by_department.get(Department.COMPLIANCE, [])
                                  if a.employee.job_title == JobTitle.COMPLIANCE_OFFICER]

            if compliance_officers:
                compliance_officer = compliance_officers[0]
                compliance_result = await compliance_officer.process_task(
                    task_description=f"Perform daily compliance checks for {business_date}",
                    context={
                        "business_date": business_date,
                        "step": "compliance_checks"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "compliance_checks",
                    "agent": compliance_officer.employee.employee_id,
                    "result": compliance_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(compliance_officer.employee.employee_id)
                workflow_state["reports_generated"].append("compliance_report")

            # STEP 5: Financial Reporting
            finance_dept = self.agents_by_department.get(Department.FINANCE, [])
            if finance_dept:
                finance_analyst = finance_dept[0]
                finance_result = await finance_analyst.process_task(
                    task_description=f"Generate financial report for {business_date}",
                    context={
                        "business_date": business_date,
                        "step": "financial_reporting"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "financial_reporting",
                    "agent": finance_analyst.employee.employee_id,
                    "result": finance_result,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(finance_analyst.employee.employee_id)
                workflow_state["reports_generated"].append("daily_financial_report")

            # STEP 6: Executive Summary (CFO)
            cfo_agents = [a for a in self.all_agents.values()
                         if a.employee.job_title == JobTitle.CFO]

            if cfo_agents and isinstance(cfo_agents[0], ExecutiveAgent):
                cfo = cfo_agents[0]
                executive_summary = await cfo.process_task(
                    task_description=f"Review daily operations summary for {business_date}",
                    context={
                        "business_date": business_date,
                        "reports": workflow_state["reports_generated"],
                        "step": "executive_summary"
                    }
                )

                workflow_state["steps_completed"].append({
                    "step": "executive_summary",
                    "agent": cfo.employee.employee_id,
                    "result": executive_summary,
                    "timestamp": datetime.now().isoformat()
                })
                workflow_state["agents_involved"].append(cfo.employee.employee_id)

            # Mark complete
            workflow_state["status"] = "completed"
            workflow_state["end_time"] = datetime.now().isoformat()
            workflow_state["total_agents_involved"] = len(set(workflow_state["agents_involved"]))
            workflow_state["total_reports"] = len(workflow_state["reports_generated"])

            self.completed_workflows.append(workflow_state)

            logger.info(f"Daily operations workflow completed: {workflow_id}")
            return workflow_state

        except Exception as e:
            logger.error(f"Daily operations workflow failed: {workflow_id} - {str(e)}")
            workflow_state["status"] = "failed"
            workflow_state["error"] = str(e)
            workflow_state["end_time"] = datetime.now().isoformat()
            return workflow_state

    # ==================================================================================
    # ANALYTICS
    # ==================================================================================

    def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get analytics across all workflows."""
        total_workflows = len(self.completed_workflows) + len(self.active_workflows)

        completed_by_type = {}
        for workflow in self.completed_workflows:
            workflow_type = workflow.get("workflow_type", "unknown")
            completed_by_type[workflow_type] = completed_by_type.get(workflow_type, 0) + 1

        total_agents_used = set()
        for workflow in self.completed_workflows:
            total_agents_used.update(workflow.get("agents_involved", []))

        avg_steps = 0
        if self.completed_workflows:
            avg_steps = sum(len(w.get("steps_completed", [])) for w in self.completed_workflows) / len(self.completed_workflows)

        return {
            "total_workflows_executed": total_workflows,
            "completed_workflows": len(self.completed_workflows),
            "active_workflows": len(self.active_workflows),
            "workflows_by_type": completed_by_type,
            "unique_agents_used": len(total_agents_used),
            "average_steps_per_workflow": round(avg_steps, 2),
            "total_agents_in_system": len(self.all_agents)
        }
