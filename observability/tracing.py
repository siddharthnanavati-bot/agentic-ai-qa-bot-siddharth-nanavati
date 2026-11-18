"""
Module: tracing.py
Purpose: OpenTelemetry tracer integration for agent lifecycle observability.
Evidence: Module 7 - Observability and Trace Debugging.
"""
from __future__ import annotations

import contextlib
import time
import uuid
from typing import Any, Generator


class SimpleSpan:
    """Lightweight in-memory span recorder compatible with OTel paradigms."""

    def __init__(self, name: str, parent_id: str | None = None) -> None:
        self.span_id = str(uuid.uuid4())[:8]
        self.name = name
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: float | None = None
        self.attributes: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []
        self.status = "OK"

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })

    def set_status(self, status: str) -> None:
        self.status = status

    def end(self) -> None:
        self.end_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        duration = (self.end_time - self.start_time) if self.end_time else 0.0
        return {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "duration_s": round(duration, 4),
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }


class AgentTracer:
    """Manages active trace spans and trace export."""

    def __init__(self) -> None:
        self.spans: list[SimpleSpan] = []
        self._current_span: SimpleSpan | None = None

    @contextlib.contextmanager
    def start_as_current_span(self, name: str) -> Generator[SimpleSpan, None, None]:
        parent_id = self._current_span.span_id if self._current_span else None
        span = SimpleSpan(name=name, parent_id=parent_id)
        prev_span = self._current_span
        self._current_span = span
        self.spans.append(span)
        try:
            yield span
        finally:
            span.end()
            self._current_span = prev_span

    def dump_traces(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.spans]
