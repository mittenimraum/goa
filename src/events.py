from dataclasses import dataclass
from typing import Any, Literal

from models import Plan, Task, TaskSolution, TokenUsage


@dataclass(frozen=True)
class PlanStarted:
    pass

@dataclass(frozen=True)
class PlanCompleted:
    plan: Plan

@dataclass(frozen=True)
class TaskStarted:
    task: Task

@dataclass(frozen=True)
class TaskCompleted:
    solution: TaskSolution

@dataclass(frozen=True)
class TaskFailed:
    task: Task
    error: str

@dataclass(frozen=True)
class ProgressUpdated:
    message: str

@dataclass(frozen=True)
class TokensUpdated:
    context: Literal["plan", "task_tool", "task_solver"]
    usage: TokenUsage

@dataclass(frozen=True)
class ExecutorStarted:
    pass

@dataclass(frozen=True)
class ExecutorCompleted:
    success_count: int
    failed_count: int
    solutions: list[Any]

@dataclass(frozen=True)
class LogEvent:
    context: str
    message: str