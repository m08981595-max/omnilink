"""
OmniLink: Universal Inter-Agent Communication Bus & Protocol
============================================================
Seamless local-first collaboration between autonomous AI agents
(DeepSeek, Gemini, Claude, Ollama, Cursor, etc.).
"""

__version__ = "0.1.0"
__author__ = "OmniLink Core Team"
__license__ = "MIT"

from .core.protocol import OmniLinkMessage, MessageType
from .core.bus import AgentBus
from .core.shared_memory import SharedMemory

__all__ = ["OmniLinkMessage", "MessageType", "AgentBus", "SharedMemory", "__version__"]
