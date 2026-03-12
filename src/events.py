from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Event:
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)