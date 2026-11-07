"""
OmniLink Ollama Adapter
=======================
Connects OmniLink with local LLMs (DeepSeek-R1, Llama 3, Qwen, Mistral) via Ollama.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from .base import BaseAgentAdapter
from ..core.protocol import OmniLinkMessage, MessageType

class OllamaAdapter(BaseAgentAdapter):
    def __init__(self, agent_id: str = "ollama", host: str = "http://localhost:11434", default_model: str = "deepseek-r1:latest"):
        super().__init__(agent_id, "Ollama Local Agent", ["local_execution", "offline", "privacy"])
        self.host = host.rstrip("/")
        self.default_model = default_model

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as res:
                return res.status == 200
        except Exception:
            return False

    def send(self, message: OmniLinkMessage) -> OmniLinkMessage:
        endpoint = f"{self.host}/api/generate"
        payload = {
            "model": message.metadata.get("model", self.default_model),
            "prompt": str(message.content),
            "stream": False
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
                reply_text = data.get("response", "")
                return message.create_reply(content=reply_text, msg_type=MessageType.COLLAB_RESPONSE)
        except Exception as e:
            raise RuntimeError(f"Ollama Connection Failed: {e}")
