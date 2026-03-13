from collections import defaultdict
from typing import Any, Callable, TypeVar

TEvent = TypeVar("TEvent")

class NotificationCenter:

    def __init__(self):
        self._subscribers: dict[type[Any], list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_type: type[TEvent], handler: Callable[[TEvent], None]):
        self._subscribers[event_type].append(handler)

    def emit(self, event: Any):
        for handler in self._subscribers[type(event)]:
            handler(event)