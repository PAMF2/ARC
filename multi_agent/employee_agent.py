"""
Employee Agent
Cada funcionário como um agente autônomo com LLM
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.employee_types import Employee, EmployeeLevel, Department, JobTitle
from multi_agent.message_bus import MessageBus, Message, MessageType, MessagePriority, create_message

# LangChain imports (optional, graceful degradation)
try:
    from langchain.chat_models import ChatOpenAI, ChatAnthropic
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmployeeAgent:
    """
    Autonomous employee agent
    Each employee can make decisions, communicate with peers, and execute tasks
    """

    def __init__(
        self,
        employee: Employee,
        message_bus: MessageBus,
        llm_provider: str = "anthropic",  # "openai", "anthropic", or "mock"
        model: str = "claude-3-5-sonnet-20241022"
    ):
        self.employee = employee
        self.message_bus = message_bus
        self.llm_provider = llm_provider
        self.model = model

        self.inbox: List[Message] = []
        self.tasks: List[Dict[str, Any]] = []
        self.is_active = True

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Subscribe to messages
        self.message_bus.subscribe(self.employee.employee_id, self._handle_message)
        self.message_bus.subscribe_department(
            self.employee.department.value,
            self._handle_department_message
        )

        logger.info(f"[AGENT] {self.employee.full_name} ({self.employee.display_title}) initialized")

    def _initialize_llm(self):
        """Initialize LLM based on provider"""
        if self.llm_provider == "mock":
            return None

        if self.llm_provider == "anthropic" and ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                return Anthropic(api_key=api_key)
            else:
                logger.warning(f"[AGENT] {self.employee.full_name}: No Anthropic API key, using mock")
                return None

        if self.llm_provider == "openai" and LANGCHAIN_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                return ChatOpenAI(model=self.model, temperature=0.7)
            else:
                logger.warning(f"[AGENT] {self.employee.full_name}: No OpenAI API key, using mock")
                return None

        return None

    def _handle_message(self, message: Message):
        """Handle incoming message"""
        self.inbox.append(message)
        logger.info(
            f"[AGENT] {self.employee.full_name} received: "
            f"{message.message_type.value} from {message.from_agent}"
        )

        # Auto-process certain message types
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            asyncio.create_task(self._process_task_assignment(message))
        elif message.message_type == MessageType.APPROVAL_REQUEST:
            asyncio.create_task(self._process_approval_request(message))
        elif message.message_type == MessageType.QUERY:
            asyncio.create_task(self._process_query(message))

    def _handle_department_message(self, message: Message):
        """Handle department-wide messages"""
        if message.from_agent != self.employee.employee_id:
            logger.info(
                f"[AGENT] {self.employee.full_name} received department message: {message.subject}"
            )

    async def process_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task using LLM decision-making

        Args:
            task_description: What needs to be done
            context: Additional context

        Returns:
            Result of task processing
        """
        context = context or {}

        # Build prompt based on employee role
        system_prompt = self._build_system_prompt()
        task_prompt = self._build_task_prompt(task_description, context)

        # Get LLM response
        if self.llm and self.llm_provider == "anthropic":
            response = await self._get_anthropic_response(system_prompt, task_prompt)
        elif self.llm and self.llm_provider == "openai":
            response = await self._get_openai_response(system_prompt, task_prompt)
        else:
            response = self._get_mock_response(task_description)

        result = {
            "employee_id": self.employee.employee_id,
            "employee_name": self.employee.full_name,
            "task": task_description,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "requires_escalation": self._should_escalate(task_description, response)
        }

        logger.info(f"[AGENT] {self.employee.full_name} completed task: {task_description[:50]}...")

        return result

    def _build_system_prompt(self) -> str:
        """Build system prompt based on employee profile"""
        prompt = f"""You are {self.employee.full_name}, {self.employee.display_title} at GlobalBank.

Your Profile:
- Department: {self.employee.department.value.replace('_', ' ').title()}
- Level: {self.employee.level.value.title()}
- Years of Service: {self.employee.years_of_service}
- Location: {self.employee.location}

Your Responsibilities:
"""

        # Add role-specific responsibilities
        responsibilities = self._get_role_responsibilities()
        for resp in responsibilities:
            prompt += f"- {resp}\n"

        prompt += """
Decision-Making Guidelines:
- Stay within your authority level
- Escalate complex issues to your manager
- Be thorough but efficient
- Consider risk and compliance
- Communicate clearly

Respond professionally and concisely.
"""
        return prompt

    def _get_role_responsibilities(self) -> List[str]:
        """Get responsibilities based on job title"""
        responsibilities_map = {
            JobTitle.TELLER: [
                "Process customer deposits and withdrawals",
                "Handle cash transactions accurately",
                "Provide basic account information",
                "Escalate complex issues to supervisors"
            ],
            JobTitle.LOAN_OFFICER: [
                "Review loan applications",
                "Assess creditworthiness",
                "Structure loan terms",
                "Recommend approval or denial"
            ],
            JobTitle.RISK_ANALYST: [
                "Assess transaction risks",
                "Monitor for fraud patterns",
                "Evaluate compliance issues",
                "Generate risk reports"
            ],
            JobTitle.SOFTWARE_ENGINEER: [
                "Develop and maintain systems",
                "Fix bugs and issues",
                "Implement new features",
                "Code review and testing"
            ],
            JobTitle.DEPARTMENT_MANAGER: [
                "Oversee team operations",
                "Make approval decisions",
                "Resource allocation",
                "Performance management"
            ],
            JobTitle.DIRECTOR: [
                "Strategic planning",
                "Cross-department coordination",
                "Budget oversight",
                "Major decision approval"
            ],
            JobTitle.CFO: [
                "Financial strategy",
                "Risk management oversight",
                "Capital allocation",
                "Regulatory compliance"
            ],
            JobTitle.CEO: [
                "Overall strategy",
                "Major decisions",
                "Stakeholder management",
                "Vision and direction"
            ]
        }

        return responsibilities_map.get(
            self.employee.job_title,
            ["Execute assigned tasks", "Collaborate with team", "Follow procedures"]
        )

    def _build_task_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build task-specific prompt"""
        prompt = f"Task: {task}\n\n"

        if context:
            prompt += "Context:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"

        prompt += "Please provide your analysis and recommended action."
        return prompt

    async def _get_anthropic_response(self, system_prompt: str, task_prompt: str) -> str:
        """Get response from Anthropic Claude"""
        try:
            message = self.llm.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": task_prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"[AGENT] Anthropic API error: {e}")
            return self._get_mock_response(task_prompt)

    async def _get_openai_response(self, system_prompt: str, task_prompt: str) -> str:
        """Get response from OpenAI"""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=task_prompt)
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"[AGENT] OpenAI API error: {e}")
            return self._get_mock_response(task_prompt)

    def _get_mock_response(self, task: str) -> str:
        """Generate mock response based on role"""
        responses = {
            "approve": f"As {self.employee.display_title}, I have reviewed this request and recommend approval based on standard procedures.",
            "review": f"I have analyzed this from the {self.employee.department.value} perspective. The metrics look acceptable.",
            "execute": f"Task acknowledged. I will process this according to {self.employee.department.value} protocols.",
            "escalate": f"This requires additional approval from {self.employee.level.value.upper()} level. Escalating to management."
        }

        # Simple keyword matching for mock
        task_lower = task.lower()
        if "approve" in task_lower or "authorization" in task_lower:
            return responses["approve"]
        elif "review" in task_lower or "analyze" in task_lower:
            return responses["review"]
        elif "escalate" in task_lower or "complex" in task_lower:
            return responses["escalate"]
        else:
            return responses["execute"]

    def _should_escalate(self, task: str, response: str) -> bool:
        """Determine if task should be escalated"""
        escalation_keywords = ["escalate", "manager", "approval", "complex", "uncertain"]

        task_lower = task.lower()
        response_lower = response.lower()

        return any(keyword in task_lower or keyword in response_lower for keyword in escalation_keywords)

    async def _process_task_assignment(self, message: Message):
        """Process task assignment message"""
        task_desc = message.content.get("task_description", "")
        context = message.content.get("context", {})

        result = await self.process_task(task_desc, context)

        # Send completion notification
        response_msg = create_message(
            from_agent=self.employee.employee_id,
            to_agent=message.from_agent,
            message_type=MessageType.TASK_COMPLETION,
            subject=f"Task completed: {task_desc[:50]}",
            content=result,
            parent_message_id=message.message_id
        )

        await self.message_bus.publish(response_msg)

        # Escalate if needed
        if result["requires_escalation"] and self.employee.manager_id:
            escalation_msg = create_message(
                from_agent=self.employee.employee_id,
                to_agent=self.employee.manager_id,
                message_type=MessageType.ESCALATION,
                subject=f"Escalation: {task_desc[:50]}",
                content={
                    "original_task": task_desc,
                    "reason": "Requires higher authority",
                    "analysis": result["response"]
                },
                priority=MessagePriority.HIGH
            )
            await self.message_bus.publish(escalation_msg)

    async def _process_approval_request(self, message: Message):
        """Process approval request"""
        request_details = message.content.get("request", "")
        amount = message.content.get("amount", 0)

        # Check authority level
        can_approve = self._check_approval_authority(amount)

        if can_approve:
            decision = await self.process_task(
                f"Approval request: {request_details}",
                {"amount": amount}
            )

            response_msg = create_message(
                from_agent=self.employee.employee_id,
                to_agent=message.from_agent,
                message_type=MessageType.APPROVAL_RESPONSE,
                subject="Approval decision",
                content={
                    "approved": True,
                    "decision": decision["response"],
                    "approver": self.employee.full_name,
                    "approver_level": self.employee.level.value
                },
                parent_message_id=message.message_id
            )
        else:
            # Escalate to manager
            if self.employee.manager_id:
                escalation_msg = create_message(
                    from_agent=self.employee.employee_id,
                    to_agent=self.employee.manager_id,
                    message_type=MessageType.APPROVAL_REQUEST,
                    subject=f"Escalated approval: {request_details[:50]}",
                    content=message.content,
                    priority=MessagePriority.HIGH,
                    requires_response=True
                )
                await self.message_bus.publish(escalation_msg)

            response_msg = create_message(
                from_agent=self.employee.employee_id,
                to_agent=message.from_agent,
                message_type=MessageType.APPROVAL_RESPONSE,
                subject="Approval escalated",
                content={
                    "approved": False,
                    "escalated": True,
                    "reason": "Exceeds approval authority",
                    "escalated_to": self.employee.manager_id
                },
                parent_message_id=message.message_id
            )

        await self.message_bus.publish(response_msg)

    async def _process_query(self, message: Message):
        """Process information query"""
        query = message.content.get("query", "")

        result = await self.process_task(f"Query: {query}", message.content)

        response_msg = create_message(
            from_agent=self.employee.employee_id,
            to_agent=message.from_agent,
            message_type=MessageType.RESPONSE,
            subject=f"Re: {message.subject}",
            content={
                "query": query,
                "response": result["response"]
            },
            parent_message_id=message.message_id
        )

        await self.message_bus.publish(response_msg)

    def _check_approval_authority(self, amount: float) -> bool:
        """Check if employee can approve given amount"""
        authority_limits = {
            EmployeeLevel.JUNIOR: 1000,
            EmployeeLevel.PLENO: 5000,
            EmployeeLevel.SENIOR: 25000,
            EmployeeLevel.MANAGER: 100000,
            EmployeeLevel.DIRECTOR: 500000,
            EmployeeLevel.VP: 2000000,
            EmployeeLevel.C_LEVEL: float('inf')
        }

        limit = authority_limits.get(self.employee.level, 0)
        return amount <= limit

    async def send_message(
        self,
        to_agent: str,
        message_type: MessageType,
        subject: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_response: bool = False
    ) -> Optional[Any]:
        """Send message to another agent"""
        message = create_message(
            from_agent=self.employee.employee_id,
            to_agent=to_agent,
            message_type=message_type,
            subject=subject,
            content=content,
            priority=priority,
            requires_response=requires_response
        )

        return await self.message_bus.publish(message)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "employee_id": self.employee.employee_id,
            "name": self.employee.full_name,
            "title": self.employee.display_title,
            "department": self.employee.department.value,
            "level": self.employee.level.value,
            "is_active": self.is_active,
            "inbox_count": len(self.inbox),
            "tasks_count": len(self.tasks),
            "llm_provider": self.llm_provider if self.llm else "mock"
        }
