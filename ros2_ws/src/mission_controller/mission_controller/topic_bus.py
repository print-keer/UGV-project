from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, DefaultDict, List

from autonomy_interfaces.contracts import TopicEnvelope


Subscriber = Callable[[object], None]


@dataclass
class TopicBus:
    """Tiny in-process message bus for simulation-first topic orchestration."""

    subscribers: DefaultDict[str, List[Subscriber]] = field(
        default_factory=lambda: defaultdict(list)
    )
    published_messages: List[TopicEnvelope] = field(default_factory=list)

    def subscribe(self, topic: str, callback: Subscriber) -> None:
        self.subscribers[topic].append(callback)

    def publish(self, topic: str, payload: object) -> None:
        envelope = TopicEnvelope(topic=topic, payload=payload)
        self.published_messages.append(envelope)
        for callback in self.subscribers.get(topic, []):
            callback(payload)

