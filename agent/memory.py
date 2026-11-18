"""
Module: memory.py
Purpose: JSON-backed conversation store with per-session TTL.
Evidence: Module 9 — Orchestration, Memory, Integration and Protocol Design.
"""
from __future__ import annotations

import json
import time
import pathlib
from typing import Any

DEFAULT_STORE_PATH = pathlib.Path(".conversation_store.json")
DEFAULT_TTL_SECONDS = 3600  # 1 hour


class ConversationMemory:
    """
    Lightweight, file-backed conversation memory.

    Each session is a list of turn dicts:
        {"role": "user"|"assistant"|"tool", "content": str, "ts": float}

    Stale sessions (older than TTL) are pruned on load.
    """

    def __init__(
        self,
        session_id: str,
        store_path: pathlib.Path = DEFAULT_STORE_PATH,
        ttl: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        self.session_id = session_id
        self.store_path = store_path
        self.ttl = ttl
        self._store: dict[str, list[dict[str, Any]]] = {}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, role: str, content: str) -> None:
        """Append a turn to this session."""
        if self.session_id not in self._store:
            self._store[self.session_id] = []
        self._store[self.session_id].append(
            {"role": role, "content": content, "ts": time.time()}
        )
        self._save()

    def get_turns(self) -> list[dict[str, Any]]:
        """Return all turns for the current session, oldest first."""
        return self._store.get(self.session_id, [])

    def clear(self) -> None:
        """Delete the current session."""
        self._store.pop(self.session_id, None)
        self._save()

    def as_messages(self) -> list[dict[str, str]]:
        """
        Convert turns to the OpenAI-compatible message list format,
        dropping the timestamp field.
        """
        return [
            {"role": t["role"], "content": t["content"]}
            for t in self.get_turns()
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self.store_path.exists():
            try:
                raw = json.loads(self.store_path.read_text(encoding="utf-8"))
                self._store = raw
            except (json.JSONDecodeError, OSError):
                self._store = {}
        self._prune_stale()

    def _save(self) -> None:
        self.store_path.write_text(
            json.dumps(self._store, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _prune_stale(self) -> None:
        cutoff = time.time() - self.ttl
        to_delete = []
        for sid, turns in self._store.items():
            if turns and turns[-1]["ts"] < cutoff:
                to_delete.append(sid)
        for sid in to_delete:
            del self._store[sid]
        if to_delete:
            self._save()
