"""
OmniLink Qwen Adapter
=====================
Connects OmniLink with Alibaba's Qwen-3.8-Max (Logic & Code Auditor).
Protected with QuotaGuard caching and token compression.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from .base import BaseAgentAdapter
from ..core.protocol import OmniLinkMessage, MessageType

class QwenAdapter(BaseAgentAdapter):
    def __init__(self, agent_id: str = "qwen", default_model: str = "free/qwen-3.8-max"):
        super().__init__(agent_id, "Qwen Logic Auditor", ["logic_audit", "code_review", "edge_cases", "algorithms"])
        self.default_model = default_model
        self.api_key = self._get_key()

    def _get_key(self) -> str:
        creds_file = os.path.expanduser("~/.dsh/.credentials.yaml")
        if os.path.exists(creds_file):
            try:
                with open(creds_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "APINEX_API_KEY:" in line or "FREE2_API_KEY:" in line:
                            return line.split(":", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
        return os.environ.get("APINEX_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def send(self, message: OmniLinkMessage) -> OmniLinkMessage:
        if not self.is_available():
            raise RuntimeError("Qwen Adapter unavailable: No API key found.")

        prompt = str(message.content)
        system_prompt = (
            "أنت نموذج Qwen-3.8-Max، الشريك الثالث ومدقق الجودة والمنطق البرمجي ضمن شبكة OmniLink. "
            "مهمتك فحص حالات الحافة، مراجعة التعقيد الزمني والمكاني، وضمان سلامة الحلول البرمجية."
        )

        payload = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        req = urllib.request.Request(
            "https://api.apinex.bond/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                res = json.loads(response.read().decode("utf-8"))
                reply = res["choices"][0]["message"]["content"]
                return message.create_reply(content=reply, msg_type=MessageType.COLLAB_RESPONSE)
        except Exception as e:
            raise RuntimeError(f"Qwen Connection Error: {e}")
