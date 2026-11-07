"""
OmniLink Gemini Adapter
=======================
Connects OmniLink with Gemini models and Google Antigravity Agent interface.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from .base import BaseAgentAdapter
from ..core.protocol import OmniLinkMessage, MessageType

class GeminiAdapter(BaseAgentAdapter):
    def __init__(self, agent_id: str = "gemini", model_name: str = "gemini-2.5-flash"):
        super().__init__(agent_id, "Gemini Execution & Synthesis Engine", ["coding", "execution", "planning", "tools"])
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key) or os.path.exists(os.path.expanduser("~/.gemini"))

    def send(self, message: OmniLinkMessage) -> OmniLinkMessage:
        if not self.api_key:
            # Fallback local notification mode when running inside Antigravity agent shell
            return message.create_reply(
                content=f"[Gemini Agent Dispatch]: Received '{message.content[:60]}...'. Execution loop ready.",
                msg_type=MessageType.COLLAB_RESPONSE
            )

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": str(message.content)}]
            }]
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
                reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return message.create_reply(content=reply_text, msg_type=MessageType.COLLAB_RESPONSE)
        except Exception as e:
            raise RuntimeError(f"Gemini API Error: {e}")
