"""
OmniLink Kimi Adapter
=====================
Connects OmniLink with Moonshot AI's Kimi K3 (Long-Context & Repository Specialist).
Protected with QuotaGuard multi-tier caching and token compression.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from .base import BaseAgentAdapter
from ..core.protocol import OmniLinkMessage, MessageType

class KimiAdapter(BaseAgentAdapter):
    def __init__(self, agent_id: str = "kimi", default_model: str = "free/kimi-k3"):
        super().__init__(agent_id, "Kimi Long-Context Specialist", ["long_context", "repo_analysis", "huge_documents", "deep_research"])
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
            raise RuntimeError("Kimi Adapter unavailable: No API key found.")

        prompt = str(message.content)
        system_prompt = (
            "أنت نموذج Kimi K3، الشريك الرابع والمتخصص في معالجة السياق الطويل والمستودعات البرمجية "
            "الضخمة ضمن شبكة OmniLink العالمية. مهمتك قراءة وتحليل المشاريع الكبيرة دفعة واحدة."
        )

        payload = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
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
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data["choices"][0]["message"]["content"]
                return OmniLinkMessage(
                    sender=self.agent_id,
                    recipient=message.sender,
                    content=reply_text,
                    msg_type=MessageType.RESPONSE,
                    correlation_id=message.message_id,
                    metadata={"model": self.default_model, "tokens": data.get("usage", {}).get("total_tokens", 0)}
                )
        except Exception as e:
            raise RuntimeError(f"Kimi API execution error: {e}")
