from dataclasses import dataclass
from typing import Any, Literal

from models import Plan, Task, TokenUsage


@dataclass
class PlanStarted:
    pass

@dataclass
class PlanCompleted:
    plan: Plan

@dataclass
class TaskStarted:
    task: Task

@dataclass
class TaskCompleted:
    task: Task

@dataclass
class TaskFailed:
    task: Task
    error: str

@dataclass
class ProgressUpdated:
    message: str

@dataclass
class TokensUpdated:
    context: Literal["plan", "task_tool", "task_solver"]
    usage: TokenUsage

@dataclass
class ExecutorCompleted:
    success_count: int
    failed_count: int
    solutions: list[Any]

@dataclass
class LogEvent:
    context: str
    message: str

