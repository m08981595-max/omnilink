"""
OmniLink Shared Memory (Agent Blackboard)
=========================================
Thread-safe and cross-process shared state storage for agents.
"""

import os
import json
import time
from typing import Dict, Any, Optional, List

class SharedMemory:
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = storage_path
        else:
            home = os.path.expanduser("~/.omnilink")
            os.makedirs(home, exist_ok=True)
            self.storage_path = os.path.join(home, "shared_memory.json")
        self._cache: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def _save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def set(self, key: str, value: Any, author: str = "system") -> None:
        """Store a value with metadata."""
        self._load()
        self._cache[key] = {
            "value": value,
            "author": author,
            "updated_at": int(time.time() * 1000)
        }
        self._save()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a stored value."""
        self._load()
        entry = self._cache.get(key)
        if entry is None:
            return default
        return entry.get("value", default)

    def get_entry(self, key: str) -> Optional[Dict[str, Any]]:
        self._load()
        return self._cache.get(key)

    def list_keys(self) -> List[str]:
        self._load()
        return list(self._cache.keys())

    def clear(self) -> None:
        self._cache = {}
        self._save()
