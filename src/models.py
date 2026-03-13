from dataclasses import asdict, dataclass, field
from typing import Any, Optional, Self

from rich.markdown import Markdown


@dataclass
class Task:
    id: int
    title: str
    status: Optional[str]
    error: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Plan:
    goal: str
    language: str = "en"
    tasks: list[Task] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> Markdown:
        return Markdown(f"{self.solution}\n\n{self.tool_outputs}")

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
        return {"input": self.input, "output": self.output, "total": self.total}

@dataclass
class TokenUsageStats:
    planner: TokenUsage = field(default_factory=TokenUsage)
    task_solver: TokenUsage = field(default_factory=TokenUsage)
    task_tools: TokenUsage = field(default_factory=TokenUsage)
    total: TokenUsage  = field(default_factory=TokenUsage)

    def to_string(self) -> str:
        return f"Planner     {self.planner.to_string()}\nTask Solver {self.task_solver.to_string()}\nTask Tool   {self.task_tools.to_string()}\n-----------------------------------------------\nTotal       {self.total.to_string()}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "planner": self.planner.to_dict(),
            "task_solver": self.task_solver.to_dict(),
            "task_tools": self.task_tools.to_dict(),
            "total": self.total.to_dict()
        }

@dataclass
class State:
    goal: str
    working_memory: list[dict[str, Any]]
    token_usage_stats: TokenUsageStats
    language: str | None = None
    tasks: list[Task] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "language": self.language,
            "working_memory": self.working_memory,
            "token_usage_stats": self.token_usage_stats.to_dict(),
            "tasks": [t.to_dict() for t in self.tasks] if self.tasks else None
        }
