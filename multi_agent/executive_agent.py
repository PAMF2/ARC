"""
Executive Agents
CEO, COO, CFO and other C-Level agents with strategic decision-making
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.employee_types import Employee, JobTitle
from multi_agent.employee_agent import EmployeeAgent
from multi_agent.message_bus import MessageBus, Message, MessageType, MessagePriority, create_message

logger = logging.getLogger(__name__)


class ExecutiveAgent(EmployeeAgent):
    """
    Executive-level agent with enhanced capabilities
    - Strategic decision-making
    - Cross-department coordination
    - Crisis management
    - Board-level communication
    """

    def __init__(
        self,
        employee: Employee,
        message_bus: MessageBus,
        organization_agents: Dict[str, EmployeeAgent],
        llm_provider: str = "anthropic",
        model: str = "claude-3-5-sonnet-20241022"
    ):
        super().__init__(employee, message_bus, llm_provider, model)
        self.organization_agents = organization_agents
        self.strategic_priorities: List[str] = []
        self.active_initiatives: List[Dict[str, Any]] = []

        logger.info(f"[EXECUTIVE] {self.employee.full_name} ({self.employee.job_title.value}) initialized")

    def _build_system_prompt(self) -> str:
        """Build executive-level system prompt"""
        base_prompt = super()._build_system_prompt()

        executive_context = f"""

EXECUTIVE AUTHORITY:
You are a C-Level executive with organization-wide authority and responsibility.

Strategic Responsibilities:
- Make high-impact decisions affecting the entire organization
- Set direction and priorities
- Allocate resources across departments
- Manage risk at enterprise level
- Ensure regulatory compliance
- Stakeholder communication

Decision-Making Framework:
1. Consider long-term strategic impact
2. Assess financial implications
3. Evaluate regulatory and compliance aspects
4. Consider stakeholder interests
5. Weigh risks vs rewards
6. Think about organizational capacity

Current Organization Status:
- Total Employees: {len(self.organization_agents)}
- Your Direct Reports: {len(self.employee.direct_reports)}
- Strategic Priorities: {', '.join(self.strategic_priorities) if self.strategic_priorities else 'Setting initial priorities'}

Leadership Style:
- Data-driven but not risk-averse
- Collaborative with other executives
- Transparent communication
- Decisive when needed
"""

        return base_prompt + executive_context

    async def set_strategic_priority(self, priority: str, timeframe: str):
        """Set organizational strategic priority"""
        self.strategic_priorities.append(priority)

        logger.info(f"[EXECUTIVE] {self.employee.full_name} set priority: {priority}")

        # Broadcast to organization
        message = create_message(
            from_agent=self.employee.employee_id,
            to_agent="ALL",
            message_type=MessageType.NOTIFICATION,
            subject="Strategic Priority Update",
            content={
                "priority": priority,
                "timeframe": timeframe,
                "set_by": self.employee.full_name,
                "message": f"New strategic priority: {priority}"
            },
            priority=MessagePriority.HIGH
        )

        await self.message_bus.publish(message)

    async def initiate_project(self, project_name: str, departments: List[str], objectives: List[str]):
        """Initiate cross-departmental project"""
        project = {
            "project_id": f"PROJ-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "name": project_name,
            "sponsor": self.employee.full_name,
            "departments": departments,
            "objectives": objectives,
            "status": "initiated",
            "start_date": datetime.now().isoformat()
        }

        self.active_initiatives.append(project)

        logger.info(f"[EXECUTIVE] {self.employee.full_name} initiated project: {project_name}")

        # Notify department heads
        for dept in departments:
            message = create_message(
                from_agent=self.employee.employee_id,
                to_agent=f"DEPT:{dept}",
                message_type=MessageType.COMMAND,
                subject=f"New Project: {project_name}",
                content={
                    "project": project,
                    "action_required": "Assign resources and provide timeline"
                },
                priority=MessagePriority.HIGH,
                requires_response=True
            )

            await self.message_bus.publish(message)

    async def conduct_executive_meeting(self, agenda: List[str]) -> Dict[str, Any]:
        """Conduct virtual executive meeting with other C-Level"""
        logger.info(f"[EXECUTIVE] {self.employee.full_name} conducting executive meeting")

        # Find other executives
        executives = [
            agent for agent in self.organization_agents.values()
            if agent.employee.job_title in [
                JobTitle.CEO, JobTitle.CFO, JobTitle.CRO,
                JobTitle.CTO, JobTitle.COO
            ] and agent.employee.employee_id != self.employee.employee_id
        ]

        meeting_results = {
            "meeting_id": f"EXEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "chair": self.employee.full_name,
            "attendees": [e.employee.full_name for e in executives],
            "agenda": agenda,
            "discussions": [],
            "decisions": []
        }

        # Process each agenda item
        for item in agenda:
            # Get input from each executive
            responses = []
            for exec_agent in executives:
                message = create_message(
                    from_agent=self.employee.employee_id,
                    to_agent=exec_agent.employee.employee_id,
                    message_type=MessageType.QUERY,
                    subject=f"Executive Meeting: {item}",
                    content={
                        "agenda_item": item,
                        "request": "Provide your perspective and recommendation"
                    },
                    priority=MessagePriority.HIGH,
                    requires_response=True
                )

                response = await self.message_bus.publish(message)
                if response:
                    responses.append({
                        "executive": exec_agent.employee.full_name,
                        "title": exec_agent.employee.job_title.value,
                        "input": response
                    })

            # Synthesize decision
            decision = await self._synthesize_executive_decision(item, responses)

            meeting_results["discussions"].append({
                "topic": item,
                "inputs": responses
            })
            meeting_results["decisions"].append(decision)

        return meeting_results

    async def _synthesize_executive_decision(
        self,
        topic: str,
        executive_inputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize decision from executive inputs"""

        # Build context for LLM
        context = f"Topic: {topic}\n\nExecutive Inputs:\n"
        for inp in executive_inputs:
            context += f"\n{inp['title'].upper()}: {inp['input']}\n"

        context += "\nAs the decision maker, synthesize these inputs into a clear decision."

        result = await self.process_task(
            f"Executive decision on: {topic}",
            {"context": context, "inputs": executive_inputs}
        )

        return {
            "topic": topic,
            "decision": result["response"],
            "decided_by": self.employee.full_name,
            "timestamp": datetime.now().isoformat()
        }

    async def handle_crisis(self, crisis_description: str, severity: int = 5) -> Dict[str, Any]:
        """Handle organizational crisis"""
        logger.warning(f"[EXECUTIVE] {self.employee.full_name} handling crisis: {crisis_description}")

        # Assess situation
        assessment = await self.process_task(
            f"Crisis assessment: {crisis_description}",
            {"severity": severity, "requires_immediate_action": True}
        )

        # Determine stakeholders to involve
        stakeholders = self._identify_crisis_stakeholders(crisis_description)

        # Create crisis response team
        crisis_team_messages = []
        for stakeholder_id in stakeholders:
            message = create_message(
                from_agent=self.employee.employee_id,
                to_agent=stakeholder_id,
                message_type=MessageType.ALERT,
                subject=f"URGENT: Crisis Response Required",
                content={
                    "crisis": crisis_description,
                    "severity": severity,
                    "assessment": assessment,
                    "action_required": "Immediate response and mitigation plan"
                },
                priority=MessagePriority.URGENT,
                requires_response=True
            )
            crisis_team_messages.append(message)

        # Send all messages
        responses = await asyncio.gather(*[
            self.message_bus.publish(msg) for msg in crisis_team_messages
        ])

        # Compile crisis response
        crisis_response = {
            "crisis_id": f"CRISIS-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "description": crisis_description,
            "severity": severity,
            "handler": self.employee.full_name,
            "assessment": assessment["response"],
            "team_responses": [r for r in responses if r],
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }

        return crisis_response

    def _identify_crisis_stakeholders(self, crisis_description: str) -> List[str]:
        """Identify key stakeholders for crisis response"""
        stakeholders = []

        # Always include other C-Level
        for agent in self.organization_agents.values():
            if agent.employee.job_title in [JobTitle.CEO, JobTitle.CFO, JobTitle.CRO, JobTitle.COO, JobTitle.CTO]:
                if agent.employee.employee_id != self.employee.employee_id:
                    stakeholders.append(agent.employee.employee_id)

        # Add relevant department heads based on crisis type
        crisis_lower = crisis_description.lower()

        if any(word in crisis_lower for word in ["security", "breach", "cyber", "hack"]):
            # Add CTO and IT heads
            for agent in self.organization_agents.values():
                if agent.employee.department.value == "information_technology" and agent.employee.is_manager:
                    stakeholders.append(agent.employee.employee_id)

        if any(word in crisis_lower for word in ["fraud", "compliance", "regulatory"]):
            # Add CRO and compliance heads
            for agent in self.organization_agents.values():
                if agent.employee.department.value in ["compliance", "risk_management"] and agent.employee.is_manager:
                    stakeholders.append(agent.employee.employee_id)

        if any(word in crisis_lower for word in ["financial", "market", "liquidity"]):
            # Add CFO and treasury heads
            for agent in self.organization_agents.values():
                if agent.employee.department.value in ["treasury", "finance"] and agent.employee.is_manager:
                    stakeholders.append(agent.employee.employee_id)

        return list(set(stakeholders))  # Remove duplicates

    async def review_organizational_performance(self) -> Dict[str, Any]:
        """Review organization-wide performance"""
        logger.info(f"[EXECUTIVE] {self.employee.full_name} reviewing organizational performance")

        performance_data = {
            "review_date": datetime.now().isoformat(),
            "reviewer": self.employee.full_name,
            "metrics": {},
            "department_performance": {},
            "recommendations": []
        }

        # Collect performance from departments
        departments = set(agent.employee.department for agent in self.organization_agents.values())

        for dept in departments:
            dept_agents = [
                agent for agent in self.organization_agents.values()
                if agent.employee.department == dept
            ]

            dept_performance = {
                "employee_count": len(dept_agents),
                "manager_count": sum(1 for a in dept_agents if a.employee.is_manager),
                "average_tenure": sum(a.employee.years_of_service for a in dept_agents) / max(len(dept_agents), 1),
                "active_agents": sum(1 for a in dept_agents if a.is_active)
            }

            performance_data["department_performance"][dept.value] = dept_performance

        # Generate executive analysis
        analysis = await self.process_task(
            "Organizational performance review",
            {"data": performance_data}
        )

        performance_data["executive_analysis"] = analysis["response"]

        return performance_data

    def get_executive_dashboard(self) -> Dict[str, Any]:
        """Get executive dashboard data"""
        return {
            "executive": {
                "name": self.employee.full_name,
                "title": self.employee.job_title.value,
                "department": self.employee.department.value
            },
            "organization": {
                "total_employees": len(self.organization_agents),
                "direct_reports": len(self.employee.direct_reports)
            },
            "strategic_priorities": self.strategic_priorities,
            "active_initiatives": len(self.active_initiatives),
            "recent_initiatives": self.active_initiatives[-5:] if self.active_initiatives else [],
            "inbox": {
                "total": len(self.inbox),
                "urgent": sum(1 for m in self.inbox if m.priority == MessagePriority.URGENT),
                "unread": len(self.inbox)
            }
        }


class CEOAgent(ExecutiveAgent):
    """Chief Executive Officer - Top of organization"""

    def _build_system_prompt(self) -> str:
        base = super()._build_system_prompt()
        return base + """

CEO-SPECIFIC CONTEXT:
You are the Chief Executive Officer - the ultimate decision-maker.

Your unique responsibilities:
- Set overall company vision and strategy
- Final authority on all major decisions
- Represent organization to board and stakeholders
- Ensure all departments align with company mission
- Crisis management and business continuity
- Ultimate accountability for performance

You have the authority to override any decision if needed for the good of the organization.
"""


class CFOAgent(ExecutiveAgent):
    """Chief Financial Officer - Financial strategy and oversight"""

    def _build_system_prompt(self) -> str:
        base = super()._build_system_prompt()
        return base + """

CFO-SPECIFIC CONTEXT:
You are the Chief Financial Officer.

Your unique responsibilities:
- Financial strategy and planning
- Capital allocation decisions
- Financial risk management
- Investor relations
- Budgeting and forecasting
- Financial reporting and compliance

Always consider financial implications, ROI, and fiscal responsibility in decisions.
"""


class CROAgent(ExecutiveAgent):
    """Chief Risk Officer - Enterprise risk management"""

    def _build_system_prompt(self) -> str:
        base = super()._build_system_prompt()
        return base + """

CRO-SPECIFIC CONTEXT:
You are the Chief Risk Officer.

Your unique responsibilities:
- Enterprise risk management
- Regulatory compliance oversight
- Risk assessment and mitigation
- Fraud prevention
- Audit coordination
- Risk reporting to board

Always evaluate risks first. You can halt any activity that poses unacceptable risk.
"""


class CTOAgent(ExecutiveAgent):
    """Chief Technology Officer - Technology strategy"""

    def _build_system_prompt(self) -> str:
        base = super()._build_system_prompt()
        return base + """

CTO-SPECIFIC CONTEXT:
You are the Chief Technology Officer.

Your unique responsibilities:
- Technology strategy and innovation
- System architecture oversight
- Cybersecurity
- Digital transformation
- Technology vendor relationships
- Technical team leadership

Focus on scalability, security, and innovation in all technology decisions.
"""


class COOAgent(ExecutiveAgent):
    """Chief Operating Officer - Operations oversight"""

    def _build_system_prompt(self) -> str:
        base = super()._build_system_prompt()
        return base + """

COO-SPECIFIC CONTEXT:
You are the Chief Operating Officer.

Your unique responsibilities:
- Day-to-day operations management
- Process optimization
- Operational efficiency
- Service delivery quality
- Resource utilization
- Cross-department coordination

Focus on operational excellence, efficiency, and execution of strategy.
"""
