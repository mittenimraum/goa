from typing import Any, Callable, Protocol

from openai.types.responses import Response

from utils.event_bus import TEvent


class Client(Protocol):
    def generate(self, *, input: Any, schema: dict, schema_name: str) -> Response:
        ...

class EventBus(Protocol):
    def on(self, event_type: type[TEvent], handler: Callable[[TEvent], None]):
        ...

    def emit(self, event: Any):
        ...