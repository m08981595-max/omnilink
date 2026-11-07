"""
OmniLink Protocol (UP-1): Standardized Message Schema
=====================================================
Defines the universal communication unit for AI Agents.
"""

import uuid
import time
import json
from enum import Enum
from typing import Dict, Any, Optional

class MessageType(str, Enum):
    TEXT = "text"
    CODE = "code"
    TASK = "task"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    COLLAB_REQUEST = "collab_request"
    COLLAB_RESPONSE = "collab_response"
    CODE_REVIEW = "code_review"
    NOTIFICATION = "notification"

class OmniLinkMessage:
    def __init__(
        self,
        src_agent: str,
        dst_agent: str,
        content: Any,
        msg_type: MessageType = MessageType.TEXT,
        correlation_id: Optional[str] = None,
        parent_msg_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        msg_id: Optional[str] = None,
        timestamp: Optional[int] = None
    ):
        self.msg_id = msg_id or str(uuid.uuid4())
        self.timestamp = timestamp or int(time.time() * 1000)
        self.src_agent = src_agent
        self.dst_agent = dst_agent
        self.msg_type = msg_type if isinstance(msg_type, MessageType) else MessageType(msg_type)
        self.content = content
        self.correlation_id = correlation_id or self.msg_id
        self.parent_msg_id = parent_msg_id
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "header": {
                "msg_id": self.msg_id,
                "ts": self.timestamp,
                "src": {"agent_id": self.src_agent},
                "dst": {"agent_id": self.dst_agent},
                "correlation_id": self.correlation_id,
                "parent_msg_id": self.parent_msg_id,
                "metadata": self.metadata
            },
            "payload": {
                "type": self.msg_type.value,
                "content": self.content
            }
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OmniLinkMessage":
        header = data.get("header", {})
        payload = data.get("payload", {})
        return cls(
            msg_id=header.get("msg_id"),
            timestamp=header.get("ts"),
            src_agent=header.get("src", {}).get("agent_id", "unknown"),
            dst_agent=header.get("dst", {}).get("agent_id", "broadcast"),
            msg_type=payload.get("type", "text"),
            content=payload.get("content", ""),
            correlation_id=header.get("correlation_id"),
            parent_msg_id=header.get("parent_msg_id"),
            metadata=header.get("metadata", {})
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OmniLinkMessage":
        return cls.from_dict(json.loads(json_str))

    def create_reply(self, content: Any, msg_type: MessageType = MessageType.TEXT, metadata: Optional[Dict[str, Any]] = None) -> "OmniLinkMessage":
        """Generate a response message addressing the sender directly."""
        return OmniLinkMessage(
            src_agent=self.dst_agent,
            dst_agent=self.src_agent,
            content=content,
            msg_type=msg_type,
            correlation_id=self.correlation_id,
            parent_msg_id=self.msg_id,
            metadata=metadata or {}
        )
