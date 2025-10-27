"""
Base agent class and common interfaces for the agent system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import asyncio
import logging
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    COMPLETED = "completed"


class MessageType(Enum):
    """Message type enumeration."""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    HANDOFF = "handoff"


@dataclass
class AgentMessage:
    """Standard message format for agent communication."""
    message_id: str
    sender: str
    recipient: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create from dictionary."""
        data['message_type'] = MessageType(data['message_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_params: List[str]


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        """Initialize base agent."""
        self.agent_id = agent_id
        self.name = name
        self.config = config
        self.status = AgentStatus.IDLE
        self.capabilities: List[AgentCapability] = []
        self.memory: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Initialize capabilities
        self._initialize_capabilities()
    
    @abstractmethod
    def _initialize_capabilities(self) -> None:
        """Initialize agent capabilities."""
        pass
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message."""
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task."""
        pass
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get agent capabilities."""
        return self.capabilities
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type."""
        return any(cap.name == task_type for cap in self.capabilities)
    
    def update_status(self, status: AgentStatus) -> None:
        """Update agent status."""
        self.status = status
        self.logger.info(f"Agent {self.name} status changed to {status.value}")
    
    def store_memory(self, key: str, value: Any) -> None:
        """Store data in agent memory."""
        self.memory[key] = value
        self.logger.debug(f"Stored memory: {key}")
    
    def retrieve_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve data from agent memory."""
        return self.memory.get(key, default)
    
    def clear_memory(self) -> None:
        """Clear agent memory."""
        self.memory.clear()
        self.logger.debug("Cleared agent memory")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status.value,
            'capabilities': [cap.name for cap in self.capabilities],
            'memory_size': len(self.memory),
            'timestamp': datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.name}({self.agent_id})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(id='{self.agent_id}', name='{self.name}', status={self.status.value})"


class AgentRegistry:
    """Registry for managing agents."""
    
    def __init__(self):
        """Initialize agent registry."""
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent_registry")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent."""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def find_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """Find agents that can handle a specific capability."""
        return [agent for agent in self.agents.values() 
                if agent.can_handle(capability)]
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self.agents.values())
    
    async def broadcast_message(self, message: AgentMessage) -> List[AgentMessage]:
        """Broadcast message to all agents."""
        responses = []
        
        for agent in self.agents.values():
            try:
                response = await agent.process_message(message)
                responses.append(response)
            except Exception as e:
                self.logger.error(f"Error broadcasting to {agent}: {e}")
        
        return responses
    
    async def route_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route message to appropriate agent."""
        target_agent = self.get_agent(message.recipient)
        
        if not target_agent:
            self.logger.error(f"Target agent not found: {message.recipient}")
            return None
        
        try:
            return await target_agent.process_message(message)
        except Exception as e:
            self.logger.error(f"Error routing message to {target_agent}: {e}")
            return None
