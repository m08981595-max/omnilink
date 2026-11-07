"""
OmniLink Universal Agent Bus
============================
The central message broker routing tasks and collaborations between local AI agents.
"""

from typing import Dict, List, Optional, Callable, Any
from .protocol import OmniLinkMessage, MessageType
from .shared_memory import SharedMemory
from ..adapters.base import BaseAgentAdapter
from ..adapters.deepseek import DeepSeekAdapter
from ..adapters.gemini import GeminiAdapter
from ..adapters.ollama import OllamaAdapter

class AgentBus:
    def __init__(self, memory: Optional[SharedMemory] = None):
        self.memory = memory or SharedMemory()
        self.adapters: Dict[str, BaseAgentAdapter] = {}
        self.listeners: List[Callable[[OmniLinkMessage], None]] = []
        self._init_default_adapters()

    def _init_default_adapters(self):
        """Auto-register default system adapters."""
        try:
            self.register_adapter(DeepSeekAdapter())
        except Exception:
            pass
        try:
            self.register_adapter(GeminiAdapter())
        except Exception:
            pass
        try:
            self.register_adapter(OllamaAdapter())
        except Exception:
            pass

    def register_adapter(self, adapter: BaseAgentAdapter) -> None:
        self.adapters[adapter.agent_id] = adapter

    def list_agents(self) -> List[Dict[str, any]]:
        return [adapter.get_info() for adapter in self.adapters.values()]

    def send(self, message: OmniLinkMessage) -> OmniLinkMessage:
        """Route message to destination agent and notify listeners."""
        for listener in self.listeners:
            try:
                listener(message)
            except Exception:
                pass

        dst = message.dst_agent
        adapter = self.adapters.get(dst)
        if not adapter:
            raise ValueError(f"Agent '{dst}' not registered in OmniLink bus. Available agents: {list(self.adapters.keys())}")

        response = adapter.send(message)

        # Notify listeners of the reply
        for listener in self.listeners:
            try:
                listener(response)
            except Exception:
                pass

        return response

    def collaborate(self, task: str, primary_agent: str = "deepseek", secondary_agent: str = "gemini") -> Dict[str, Any]:
        """Orchestrate dual-agent debate and collaboration workflow."""
        # Step 1: Query primary agent (Architect / Reasoning)
        msg1 = OmniLinkMessage(
            src_agent="coordinator",
            dst_agent=primary_agent,
            content=task,
            msg_type=MessageType.COLLAB_REQUEST
        )
        reply1 = self.send(msg1)

        # Step 2: Query secondary agent with primary's output for synthesis/review
        synthesis_prompt = (
            f"المهمة الأساسية: {task}\n\n"
            f"مقترح وتحليل {primary_agent}:\n{reply1.content}\n\n"
            "قم بمراجعة المقترح، تدقيق حالات الحافة (Edge Cases)، وتجهيز خطة التنفيذ الميدانية."
        )
        msg2 = OmniLinkMessage(
            src_agent=primary_agent,
            dst_agent=secondary_agent,
            content=synthesis_prompt,
            msg_type=MessageType.CODE_REVIEW,
            correlation_id=msg1.msg_id
        )
        reply2 = self.send(msg2)

        return {
            "task": task,
            "primary": {"agent": primary_agent, "response": reply1.content},
            "secondary": {"agent": secondary_agent, "response": reply2.content}
        }
