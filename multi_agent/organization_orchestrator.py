"""
Organization Orchestrator
Coordinates all agents and manages complex workflows
Uses LangGraph for workflow management
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.employee_types import Employee, JobTitle, Department
from divisions.hr_agent import HRAgent
from multi_agent.message_bus import MessageBus, Message, MessageType, MessagePriority, create_message
from multi_agent.employee_agent import EmployeeAgent
from multi_agent.executive_agent import (
    CEOAgent, CFOAgent, CROAgent, CTOAgent, COOAgent, ExecutiveAgent
)
from multi_agent.operational_workflows import OperationalWorkflows

# LangGraph imports (optional)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None

logger = logging.getLogger(__name__)


class OrganizationOrchestrator:
    """
    Orchestrates entire banking organization
    - Manages all employee agents
    - Coordinates workflows across departments
    - Handles escalations
    - Monitors organization health
    """

    def __init__(
        self,
        hr_agent: HRAgent,
        message_bus: Optional[MessageBus] = None,
        llm_provider: str = "anthropic"
    ):
        self.hr_agent = hr_agent
        self.message_bus = message_bus or MessageBus()
        self.llm_provider = llm_provider

        self.agents: Dict[str, EmployeeAgent] = {}
        self.executives: Dict[str, ExecutiveAgent] = {}
        self.department_coordinators: Dict[Department, List[str]] = {}

        self.active_workflows: List[Dict[str, Any]] = []
        self.workflow_history: List[Dict[str, Any]] = []

        # Operational Workflows (will be initialized after agents are created)
        self.operational_workflows: Optional[OperationalWorkflows] = None

        # Subscribe to message bus for monitoring
        self.message_bus.subscribe_broadcast(self._monitor_message)

        logger.info("[ORCHESTRATOR] Organization Orchestrator initialized")

    async def initialize_organization(self):
        """Initialize all employee agents"""
        logger.info("[ORCHESTRATOR] Initializing organization agents...")

        employees = self.hr_agent.get_all_employees()

        for employee in employees:
            await self.create_agent_for_employee(employee)

        logger.info(f"[ORCHESTRATOR] Initialized {len(self.agents)} employee agents")

        # Set up department coordinators
        self._setup_department_coordinators()

        # Connect reporting structure
        await self._connect_reporting_structure()

        # Initialize operational workflows with all agents
        agents_by_department = {}
        for dept in Department:
            agents_by_department[dept] = [
                self.agents[agent_id] for agent_id in self.department_coordinators.get(dept, [])
            ]

        self.operational_workflows = OperationalWorkflows(
            message_bus=self.message_bus,
            all_agents=self.agents,
            agents_by_department=agents_by_department
        )

        logger.info("[ORCHESTRATOR] Operational workflows initialized")

    async def create_agent_for_employee(self, employee: Employee) -> EmployeeAgent:
        """Create appropriate agent type for employee"""

        # Create executive agents for C-Level
        if employee.job_title == JobTitle.CEO:
            agent = CEOAgent(
                employee=employee,
                message_bus=self.message_bus,
                organization_agents=self.agents,
                llm_provider=self.llm_provider
            )
            self.executives[employee.employee_id] = agent

        elif employee.job_title == JobTitle.CFO:
            agent = CFOAgent(
                employee=employee,
                message_bus=self.message_bus,
                organization_agents=self.agents,
                llm_provider=self.llm_provider
            )
            self.executives[employee.employee_id] = agent

        elif employee.job_title == JobTitle.CRO:
            agent = CROAgent(
                employee=employee,
                message_bus=self.message_bus,
                organization_agents=self.agents,
                llm_provider=self.llm_provider
            )
            self.executives[employee.employee_id] = agent

        elif employee.job_title == JobTitle.CTO:
            agent = CTOAgent(
                employee=employee,
                message_bus=self.message_bus,
                organization_agents=self.agents,
                llm_provider=self.llm_provider
            )
            self.executives[employee.employee_id] = agent

        elif employee.job_title == JobTitle.COO:
            agent = COOAgent(
                employee=employee,
                message_bus=self.message_bus,
                organization_agents=self.agents,
                llm_provider=self.llm_provider
            )
            self.executives[employee.employee_id] = agent

        elif employee.job_title in [JobTitle.VP, JobTitle.SVP, JobTitle.DIRECTOR]:
            agent = ExecutiveAgent(
                employee=employee,
                message_bus=self.message_bus,
                organization_agents=self.agents,
                llm_provider=self.llm_provider
            )
            self.executives[employee.employee_id] = agent

        else:
            # Regular employee agent
            agent = EmployeeAgent(
                employee=employee,
                message_bus=self.message_bus,
                llm_provider=self.llm_provider
            )

        self.agents[employee.employee_id] = agent

        logger.info(
            f"[ORCHESTRATOR] Created agent for {employee.full_name} "
            f"({employee.display_title})"
        )

        return agent

    def _setup_department_coordinators(self):
        """Set up department coordination structure"""
        for dept in Department:
            dept_agents = [
                agent_id for agent_id, agent in self.agents.items()
                if agent.employee.department == dept
            ]
            self.department_coordinators[dept] = dept_agents

            logger.info(f"[ORCHESTRATOR] Department {dept.value}: {len(dept_agents)} agents")

    async def _connect_reporting_structure(self):
        """Connect managers and reports"""
        for agent in self.agents.values():
            if agent.employee.manager_id:
                logger.debug(
                    f"[ORCHESTRATOR] {agent.employee.full_name} reports to "
                    f"{agent.employee.manager_id}"
                )

    def _monitor_message(self, message: Message):
        """Monitor all messages (for analytics/alerts)"""
        # Log critical messages
        if message.priority in [MessagePriority.URGENT, MessagePriority.HIGH]:
            logger.warning(
                f"[ORCHESTRATOR] HIGH PRIORITY: {message.from_agent} -> {message.to_agent}: "
                f"{message.subject}"
            )

        # Detect escalation patterns
        if message.message_type == MessageType.ESCALATION:
            logger.warning(f"[ORCHESTRATOR] ESCALATION: {message.subject}")

    async def execute_banking_transaction(
        self,
        customer_id: str,
        transaction_type: str,
        amount: float,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute complete banking transaction workflow
        Coordinates multiple departments and agents
        """
        workflow_id = f"TXN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        logger.info(
            f"[ORCHESTRATOR] Starting transaction workflow {workflow_id}: "
            f"{transaction_type} ${amount:,.2f}"
        )

        workflow = {
            "workflow_id": workflow_id,
            "type": "banking_transaction",
            "transaction_type": transaction_type,
            "amount": amount,
            "customer_id": customer_id,
            "details": details,
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "steps": []
        }

        self.active_workflows.append(workflow)

        try:
            # Step 1: Front Office Intake
            front_office_agents = [
                agent for agent in self.agents.values()
                if agent.employee.department == Department.RETAIL_BANKING
                and not agent.employee.is_manager
            ]

            if not front_office_agents:
                raise Exception("No front office agents available")

            intake_agent = front_office_agents[0]

            intake_result = await intake_agent.process_task(
                f"Process {transaction_type} transaction for customer {customer_id}",
                {"amount": amount, **details}
            )

            workflow["steps"].append({
                "step": "front_office_intake",
                "agent": intake_agent.employee.full_name,
                "result": intake_result,
                "timestamp": datetime.now().isoformat()
            })

            # Step 2: Risk Assessment (if amount > $10k)
            if amount > 10000:
                risk_agents = [
                    agent for agent in self.agents.values()
                    if agent.employee.department == Department.RISK_MANAGEMENT
                ]

                if risk_agents:
                    risk_agent = risk_agents[0]

                    risk_result = await risk_agent.process_task(
                        f"Risk assessment for {transaction_type} transaction",
                        {
                            "amount": amount,
                            "customer_id": customer_id,
                            "transaction_type": transaction_type
                        }
                    )

                    workflow["steps"].append({
                        "step": "risk_assessment",
                        "agent": risk_agent.employee.full_name,
                        "result": risk_result,
                        "timestamp": datetime.now().isoformat()
                    })

                    if risk_result.get("requires_escalation"):
                        # Escalate to Risk Manager
                        risk_manager = await self._find_department_manager(Department.RISK_MANAGEMENT)
                        if risk_manager:
                            escalation_result = await risk_manager.process_task(
                                f"Review escalated transaction {workflow_id}",
                                {"original_assessment": risk_result}
                            )

                            workflow["steps"].append({
                                "step": "risk_escalation",
                                "agent": risk_manager.employee.full_name,
                                "result": escalation_result,
                                "timestamp": datetime.now().isoformat()
                            })

            # Step 3: Approval (if amount > $25k)
            if amount > 25000:
                approval_result = await self._get_transaction_approval(amount, transaction_type, workflow_id)

                workflow["steps"].append({
                    "step": "approval",
                    "result": approval_result,
                    "timestamp": datetime.now().isoformat()
                })

                if not approval_result.get("approved"):
                    workflow["status"] = "rejected"
                    workflow["rejection_reason"] = approval_result.get("reason", "Not approved")
                    return workflow

            # Step 4: Processing (Operations)
            ops_agents = [
                agent for agent in self.agents.values()
                if agent.employee.department == Department.OPERATIONS
            ]

            if ops_agents:
                ops_agent = ops_agents[0]

                processing_result = await ops_agent.process_task(
                    f"Process approved transaction {workflow_id}",
                    {"transaction_type": transaction_type, "amount": amount}
                )

                workflow["steps"].append({
                    "step": "processing",
                    "agent": ops_agent.employee.full_name,
                    "result": processing_result,
                    "timestamp": datetime.now().isoformat()
                })

            # Step 5: Settlement
            settlement_agents = [
                agent for agent in self.agents.values()
                if agent.employee.department == Department.CLEARING_SETTLEMENT
            ]

            if settlement_agents:
                settlement_agent = settlement_agents[0]

                settlement_result = await settlement_agent.process_task(
                    f"Settle transaction {workflow_id}",
                    {"transaction_type": transaction_type, "amount": amount}
                )

                workflow["steps"].append({
                    "step": "settlement",
                    "agent": settlement_agent.employee.full_name,
                    "result": settlement_result,
                    "timestamp": datetime.now().isoformat()
                })

            workflow["status"] = "completed"
            workflow["end_time"] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Workflow {workflow_id} failed: {e}")
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            workflow["end_time"] = datetime.now().isoformat()

        self.active_workflows.remove(workflow)
        self.workflow_history.append(workflow)

        logger.info(f"[ORCHESTRATOR] Workflow {workflow_id} completed: {workflow['status']}")

        return workflow

    async def _find_department_manager(self, department: Department) -> Optional[EmployeeAgent]:
        """Find manager for a department"""
        dept_agents = [
            agent for agent in self.agents.values()
            if agent.employee.department == department and agent.employee.is_manager
        ]

        return dept_agents[0] if dept_agents else None

    async def _get_transaction_approval(
        self,
        amount: float,
        transaction_type: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get appropriate approval for transaction amount"""

        # Determine required approval level
        if amount > 500000:
            # Requires C-Level
            approver = self._find_cfo()
        elif amount > 100000:
            # Requires Director+
            approver = await self._find_director()
        else:
            # Requires Manager+
            approver = await self._find_manager()

        if not approver:
            return {
                "approved": False,
                "reason": "No appropriate approver available"
            }

        # Request approval
        approval_message = create_message(
            from_agent="ORCHESTRATOR",
            to_agent=approver.employee.employee_id,
            message_type=MessageType.APPROVAL_REQUEST,
            subject=f"Approval Required: {transaction_type} ${amount:,.2f}",
            content={
                "workflow_id": workflow_id,
                "transaction_type": transaction_type,
                "amount": amount,
                "request": f"Approval for {transaction_type} transaction of ${amount:,.2f}"
            },
            priority=MessagePriority.HIGH if amount > 100000 else MessagePriority.NORMAL,
            requires_response=True
        )

        response = await self.message_bus.publish(approval_message)

        return response or {"approved": False, "reason": "Timeout"}

    def _find_cfo(self) -> Optional[ExecutiveAgent]:
        """Find CFO"""
        for agent in self.executives.values():
            if agent.employee.job_title == JobTitle.CFO:
                return agent
        return None

    async def _find_director(self) -> Optional[EmployeeAgent]:
        """Find a director"""
        directors = [
            agent for agent in self.agents.values()
            if agent.employee.job_title == JobTitle.DIRECTOR
        ]
        return directors[0] if directors else None

    async def _find_manager(self) -> Optional[EmployeeAgent]:
        """Find a manager"""
        managers = [
            agent for agent in self.agents.values()
            if agent.employee.is_manager
        ]
        return managers[0] if managers else None

    async def execute_strategic_initiative(
        self,
        initiative_name: str,
        objectives: List[str],
        departments: List[Department]
    ) -> Dict[str, Any]:
        """Execute strategic initiative coordinated by CEO"""

        # Find CEO
        ceo = None
        for agent in self.executives.values():
            if agent.employee.job_title == JobTitle.CEO:
                ceo = agent
                break

        if not ceo:
            return {"error": "CEO not found"}

        # CEO initiates project
        result = await ceo.initiate_project(
            project_name=initiative_name,
            departments=[dept.value for dept in departments],
            objectives=objectives
        )

        return result

    async def conduct_executive_meeting(self, agenda: List[str]) -> Dict[str, Any]:
        """Conduct executive meeting"""

        # Find CEO to chair meeting
        ceo = None
        for agent in self.executives.values():
            if agent.employee.job_title == JobTitle.CEO:
                ceo = agent
                break

        if not ceo:
            return {"error": "CEO not found"}

        meeting_result = await ceo.conduct_executive_meeting(agenda)

        return meeting_result

    def get_organization_status(self) -> Dict[str, Any]:
        """Get complete organization status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "total": len(self.agents),
                "executives": len(self.executives),
                "active": sum(1 for a in self.agents.values() if a.is_active)
            },
            "departments": {
                dept.value: len(agent_ids)
                for dept, agent_ids in self.department_coordinators.items()
            },
            "workflows": {
                "active": len(self.active_workflows),
                "completed": len(self.workflow_history)
            },
            "message_bus": self.message_bus.get_stats()
        }

    def get_agent(self, employee_id: str) -> Optional[EmployeeAgent]:
        """Get agent by employee ID"""
        return self.agents.get(employee_id)

    def get_agents_by_department(self, department: Department) -> List[EmployeeAgent]:
        """Get all agents in a department"""
        return [
            self.agents[agent_id]
            for agent_id in self.department_coordinators.get(department, [])
            if agent_id in self.agents
        ]

    async def shutdown(self):
        """Shutdown orchestrator"""
        logger.info("[ORCHESTRATOR] Shutting down...")

        # Deactivate all agents
        for agent in self.agents.values():
            agent.is_active = False

        logger.info("[ORCHESTRATOR] Shutdown complete")
