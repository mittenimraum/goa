from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Self

from rich.markdown import Markdown


@dataclass
class Task:
    id: int
    title: str
    status: Optional[str]
    error: Optional[str]

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

@dataclass
class TaskSolution:
    task: Task
    tool_name: str
    tool_input: str
    tool_reason: str
    tool_outputs: str
    solution: str
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> Markdown:
        return Markdown(f"{self.solution}\n\n{self.tool_outputs}")

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_string(self) -> str:
        return f"Title: {self.title}\nURL: {self.url}\nSnippet: {self.snippet}"

@dataclass
class TokenUsage:
    input: int = 0
    output: int = 0
    total: int = 0

    def add(self, usage: Self) -> None:
        self.input += usage.input
        self.output += usage.output
        self.total += usage.total

    def to_string(self) -> str:
        return f"in={self.input} out={self.output} total={self.input + self.output}"

@dataclass
class TokenUsageStats:
    planner: TokenUsage = field(default_factory=TokenUsage)
    task_solver: TokenUsage = field(default_factory=TokenUsage)
    task_tools: TokenUsage = field(default_factory=TokenUsage)
    total: TokenUsage  = field(default_factory=TokenUsage)

    def to_string(self) -> str:
        return f"Planner     {self.planner.to_string()}\nTask Solver {self.task_solver.to_string()}\nTask Tool   {self.task_tools.to_string()}\n-----------------------------------------------\nTotal       {self.total.to_string()}"