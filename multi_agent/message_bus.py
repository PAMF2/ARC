"""
Message Bus for Inter-Agent Communication
Sistema de mensagens assíncronas entre agentes
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Prioridade de mensagens"""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class MessageType(Enum):
    """Tipos de mensagens"""
    # Requests
    REQUEST = "request"
    QUERY = "query"
    COMMAND = "command"

    # Responses
    RESPONSE = "response"
    ACK = "acknowledgment"

    # Notifications
    NOTIFICATION = "notification"
    ALERT = "alert"

    # Workflow
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"

    # Escalation
    ESCALATION = "escalation"


@dataclass
class Message:
    """Mensagem entre agentes"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    subject: str
    content: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    parent_message_id: Optional[str] = None
    requires_response: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "subject": self.subject,
            "content": self.content,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "parent_message_id": self.parent_message_id,
            "requires_response": self.requires_response,
            "metadata": self.metadata
        }


class MessageBus:
    """
    Central message bus for agent communication
    Implements pub-sub pattern with routing
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}  # agent_id -> [callbacks]
        self.department_subscribers: Dict[str, List[Callable]] = {}  # dept -> [callbacks]
        self.broadcast_subscribers: List[Callable] = []
        self.message_history: List[Message] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.lock = asyncio.Lock()

        logger.info("[MESSAGE BUS] Initialized")

    def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe agent to receive messages"""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)
        logger.info(f"[MESSAGE BUS] Agent {agent_id} subscribed")

    def subscribe_department(self, department: str, callback: Callable):
        """Subscribe to all messages for a department"""
        if department not in self.department_subscribers:
            self.department_subscribers[department] = []
        self.department_subscribers[department].append(callback)
        logger.info(f"[MESSAGE BUS] Department {department} subscribed")

    def subscribe_broadcast(self, callback: Callable):
        """Subscribe to all messages (admin/monitoring)"""
        self.broadcast_subscribers.append(callback)
        logger.info(f"[MESSAGE BUS] Broadcast subscriber added")

    def unsubscribe(self, agent_id: str, callback: Callable):
        """Unsubscribe agent"""
        if agent_id in self.subscribers and callback in self.subscribers[agent_id]:
            self.subscribers[agent_id].remove(callback)

    async def publish(self, message: Message) -> Optional[Any]:
        """
        Publish message to recipients

        Returns:
            Response if requires_response=True
        """
        async with self.lock:
            self.message_history.append(message)

        logger.info(
            f"[MESSAGE BUS] {message.from_agent} -> {message.to_agent}: "
            f"{message.message_type.value} | {message.subject}"
        )

        # Handle special routing
        if message.to_agent == "ALL":
            await self._broadcast(message)
        elif message.to_agent.startswith("DEPT:"):
            department = message.to_agent.replace("DEPT:", "")
            await self._publish_to_department(department, message)
        else:
            await self._publish_to_agent(message.to_agent, message)

        # Handle response requirement
        if message.requires_response:
            future = asyncio.Future()
            self.pending_responses[message.message_id] = future
            try:
                response = await asyncio.wait_for(future, timeout=30.0)
                return response
            except asyncio.TimeoutError:
                logger.warning(f"[MESSAGE BUS] Response timeout for {message.message_id}")
                return None

        return None

    async def _publish_to_agent(self, agent_id: str, message: Message):
        """Publish to specific agent"""
        callbacks = self.subscribers.get(agent_id, [])

        tasks = []
        for callback in callbacks:
            tasks.append(self._safe_callback(callback, message))

        if tasks:
            await asyncio.gather(*tasks)

        # Also notify broadcast subscribers
        await self._notify_broadcast(message)

    async def _publish_to_department(self, department: str, message: Message):
        """Publish to all agents in department"""
        callbacks = self.department_subscribers.get(department, [])

        tasks = []
        for callback in callbacks:
            tasks.append(self._safe_callback(callback, message))

        if tasks:
            await asyncio.gather(*tasks)

        await self._notify_broadcast(message)

    async def _broadcast(self, message: Message):
        """Broadcast to all subscribers"""
        all_callbacks = []
        for callbacks in self.subscribers.values():
            all_callbacks.extend(callbacks)

        tasks = [self._safe_callback(cb, message) for cb in all_callbacks]
        if tasks:
            await asyncio.gather(*tasks)

        await self._notify_broadcast(message)

    async def _notify_broadcast(self, message: Message):
        """Notify broadcast subscribers (monitoring)"""
        tasks = [self._safe_callback(cb, message) for cb in self.broadcast_subscribers]
        if tasks:
            await asyncio.gather(*tasks)

    async def _safe_callback(self, callback: Callable, message: Message):
        """Execute callback with error handling"""
        try:
            result = callback(message)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.error(f"[MESSAGE BUS] Callback error: {e}")

    async def respond(self, original_message_id: str, response_data: Any):
        """Send response to waiting message"""
        if original_message_id in self.pending_responses:
            future = self.pending_responses.pop(original_message_id)
            if not future.done():
                future.set_result(response_data)

    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Message]:
        """Get message history with filters"""
        messages = self.message_history

        if agent_id:
            messages = [
                m for m in messages
                if m.from_agent == agent_id or m.to_agent == agent_id
            ]

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        return messages[-limit:]

    def get_conversation_thread(self, message_id: str) -> List[Message]:
        """Get conversation thread for a message"""
        thread = []

        # Find original message
        original = next((m for m in self.message_history if m.message_id == message_id), None)
        if not original:
            return thread

        thread.append(original)

        # Find all responses
        current_id = message_id
        while True:
            response = next(
                (m for m in self.message_history if m.parent_message_id == current_id),
                None
            )
            if not response:
                break
            thread.append(response)
            current_id = response.message_id

        return thread

    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            "total_messages": len(self.message_history),
            "active_subscribers": len(self.subscribers),
            "department_subscribers": len(self.department_subscribers),
            "broadcast_subscribers": len(self.broadcast_subscribers),
            "pending_responses": len(self.pending_responses),
            "messages_by_type": self._count_by_type(),
            "messages_by_priority": self._count_by_priority()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count messages by type"""
        counts = {}
        for msg in self.message_history:
            msg_type = msg.message_type.value
            counts[msg_type] = counts.get(msg_type, 0) + 1
        return counts

    def _count_by_priority(self) -> Dict[str, int]:
        """Count messages by priority"""
        counts = {}
        for msg in self.message_history:
            priority = msg.priority.name
            counts[priority] = counts.get(priority, 0) + 1
        return counts


def create_message(
    from_agent: str,
    to_agent: str,
    message_type: MessageType,
    subject: str,
    content: Dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL,
    requires_response: bool = False,
    parent_message_id: Optional[str] = None
) -> Message:
    """Helper to create a message"""
    return Message(
        message_id=str(uuid.uuid4()),
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=message_type,
        subject=subject,
        content=content,
        priority=priority,
        requires_response=requires_response,
        parent_message_id=parent_message_id
    )
