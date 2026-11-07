"""
OmniLink Base Adapter
====================
Interface that every agent adapter must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..core.protocol import OmniLinkMessage

class BaseAgentAdapter(ABC):
    def __init__(self, agent_id: str, name: str, capabilities: Optional[list] = None):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities or ["chat", "code", "review"]

    @abstractmethod
    def send(self, message: OmniLinkMessage) -> OmniLinkMessage:
        """Process incoming message and return response message."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if local runtime / provider for this agent is accessible."""
        pass

    def get_info(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "available": self.is_available()
        }
