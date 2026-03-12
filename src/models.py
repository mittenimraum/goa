from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Task:
    id: int
    title: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Plan:
    goal: str
    language: str = "en"
    tasks: List[Task] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "language": self.language,
            "tasks": [task.to_dict() for task in self.tasks]
        }