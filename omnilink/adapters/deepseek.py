"""
OmniLink DeepSeek Adapter
=========================
Connects OmniLink with DeepSeek Harness desktop runtime and API models.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from .base import BaseAgentAdapter
from ..core.protocol import OmniLinkMessage, MessageType

class DeepSeekAdapter(BaseAgentAdapter):
    def __init__(self, agent_id: str = "deepseek", default_model: str = "free/deepseek-v4-pro-0813"):
        super().__init__(agent_id, "DeepSeek Intelligence Engine", ["reasoning", "code", "architecture", "review"])
        self.default_model = default_model
        self.config = self._discover_dsh_config()

    def _discover_dsh_config(self) -> Dict[str, Any]:
        """Auto-discover credentials and active endpoints from DeepSeek Harness (~/.dsh)."""
        creds_file = os.path.expanduser("~/.dsh/.credentials.yaml")
        creds = {}
        if os.path.exists(creds_file):
            try:
                with open(creds_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if ":" in line and not line.startswith("#"):
                            k, v = line.split(":", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k and v:
                                creds[k] = v
            except Exception:
                pass

        api_key = creds.get("APINEX_API_KEY") or creds.get("FREE2_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.apinex.bond/v1")

        return {
            "api_key": api_key,
            "base_url": base_url,
            "model": self.default_model
        }

    def is_available(self) -> bool:
        return bool(self.config.get("api_key"))

    def send(self, message: OmniLinkMessage) -> OmniLinkMessage:
        if not self.is_available():
            raise RuntimeError("DeepSeek Adapter unavailable: No API key found in ~/.dsh or environment.")

        prompt = str(message.content)
        system_prompt = (
            "أنت نموذج DeepSeek، شريك ذكي ومهندس معماري ضمن شبكة OmniLink Universal Agent Bus. "
            "قدم تحليلات هندسية دقيقة، حلول برمجية قوية، وأكواد نظيفة متوافقة مع متطلبات الوكلاء الآخرين."
        )

        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.config.get("model", self.default_model),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        endpoint = f"{self.config['base_url'].rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers
        )

        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                reply_text = res_data["choices"][0]["message"]["content"]
                return message.create_reply(content=reply_text, msg_type=MessageType.COLLAB_RESPONSE)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            if e.code == 429:
                err_text = "[LIMIT_EXCEEDED] نفد رصيد أو حد الاستخدام لنموذج DeepSeek (HTTP 429)"
            else:
                err_text = f"HTTP Error {e.code}: {e.reason} - {err_body}"
            raise RuntimeError(err_text)
        except Exception as e:
            raise RuntimeError(f"DeepSeek Connection Failure: {e}")
