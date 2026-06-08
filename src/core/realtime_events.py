from __future__ import annotations

import json
import queue
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Any


@dataclass
class InventoryEvent:
    id: int
    camp_id: int
    source: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_sse(self) -> str:
        data = {
            "id": self.id,
            "camp_id": self.camp_id,
            "source": self.source,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
        return (
            f"id: {self.id}\n"
            "event: inventory.changed\n"
            f"data: {json.dumps(data, separators=(',', ':'))}\n\n"
        )


class InventoryEventBroker:
    def __init__(self) -> None:
        self._subscribers: dict[int, tuple[queue.Queue[InventoryEvent], set[int] | None]] = {}
        self._subscriber_ids = count(1)
        self._event_ids = count(1)
        self._lock = threading.Lock()

    def publish(
        self,
        camp_id: int,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        event = InventoryEvent(
            id=next(self._event_ids),
            camp_id=camp_id,
            source=source,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        with self._lock:
            subscribers = list(self._subscribers.values())

        for subscriber_queue, camp_filter in subscribers:
            if camp_filter is not None and camp_id not in camp_filter:
                continue
            try:
                subscriber_queue.put_nowait(event)
            except queue.Full:
                continue

    def subscribe(self, camp_ids: set[int] | None = None) -> Iterator[InventoryEvent]:
        subscriber_id = next(self._subscriber_ids)
        subscriber_queue: queue.Queue[InventoryEvent] = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers[subscriber_id] = (subscriber_queue, camp_ids)

        try:
            while True:
                try:
                    yield subscriber_queue.get(timeout=15)
                except queue.Empty:
                    yield InventoryEvent(
                        id=0,
                        camp_id=0,
                        source="heartbeat",
                        created_at=datetime.now(timezone.utc).isoformat(),
                    )
        finally:
            with self._lock:
                self._subscribers.pop(subscriber_id, None)


inventory_events = InventoryEventBroker()


class SystemEventBroker:
    def __init__(self) -> None:
        self._subscribers: dict[int, queue.Queue[str]] = {}
        self._subscriber_ids = count(1)
        self._lock = threading.Lock()

    def publish(self, event_type: str, data: dict[str, Any]) -> None:
        message = json.dumps({"type": event_type, "data": data}, separators=(",", ":"))
        with self._lock:
            subscribers = list(self._subscribers.values())
        for subscriber_queue in subscribers:
            try:
                subscriber_queue.put_nowait(message)
            except queue.Full:
                continue

    def subscribe(self) -> Iterator[str]:
        subscriber_id = next(self._subscriber_ids)
        subscriber_queue: queue.Queue[str] = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers[subscriber_id] = subscriber_queue
        try:
            while True:
                try:
                    yield subscriber_queue.get(timeout=30)
                except queue.Empty:
                    yield ": heartbeat\n\n"
        finally:
            with self._lock:
                self._subscribers.pop(subscriber_id, None)


system_events = SystemEventBroker()
