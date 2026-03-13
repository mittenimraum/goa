
from rich.console import Console
from rich.live import Live

from events import (
    ExecutorCompleted,
    LogEvent,
    ProgressUpdated,
    TokensUpdated,
)
from models import TokenUsageStats
from nodes.executor import Executor
from nodes.planner import Planner
from protocols import Client
from ui import ProgressView
from utils.event_bus import EventBus
from utils.observability import format_log_event


class Agent:

    def __init__(self, goal: str, client: Client, verbose: bool = False):
        self.goal = goal
        self.client = client
        self.verbose = verbose
        self.console = Console()
        self.logger = EventBus()
        self.planner = Planner(goal, client, self.logger)
        self.executor = Executor(client, self.logger)
        self.view = ProgressView(self)
        self.token_usage = TokenUsageStats()
        self.plan = None
        self.log = []
        self._register_event_handlers()

    def run(self) -> None:
        self.console.print()

        with Live(self.view, console=self.console, refresh_per_second=8):
            # Planner
            self.plan = self.planner.execute()
            # Executor
            self.solutions = self.executor.execute(self.plan)

        self.console.print()

        for solution in self.solutions:
            markdown = solution.to_markdown()
            self.console.rule(f" Task {solution.task.id}. {solution.task.title} ")
            self.console.print()
            self.console.print(markdown)
            self.console.print()

        if self.verbose:
            self.console.print()
            self.console.rule("Run Summary")
            self.console.print("")
            self.console.print(f"Tasks executed: {len(self.plan.tasks)}")
            self.console.print(f"Tasks succeeded: {sum(1 for t in self.plan.tasks if t.status == 'done')}")
            self.console.print(f"Tasks failed: {sum(1 for t in self.plan.tasks if t.status == 'failed')}")
            self.console.print()
            self.console.print("Token Usage\n-----------------------------------------------")
            self.console.print(self.token_usage.to_string())

    def _register_event_handlers(self) -> None:
        self.logger.on(ProgressUpdated, self._on_progress_updated)
        self.logger.on(ExecutorCompleted, self._on_executor_completed)
        self.logger.on(LogEvent, self._on_log_event)
        self.logger.on(TokensUpdated, self._on_tokens_updated)

    def _on_progress_updated(self, event: ProgressUpdated) -> None:
        self.progress_message = event.message

    def _on_executor_completed(self, event: ExecutorCompleted) -> None:
        self.progress_message = f"Finished. Succeeded: {event.success_count} Failed: {event.failed_count}"

    def _on_log_event(self, event: LogEvent) -> None:
        if self.verbose:
            self.log.append(format_log_event(event))

    def _on_tokens_updated(self, event: TokensUpdated) -> None:
        match event.context:
            case "plan":
                self.token_usage.planner.add(event.usage)
            case "task_solver":
                self.token_usage.task_solver.add(event.usage)
            case "task_tool":
                self.token_usage.task_tools.add(event.usage)
            case _:
                raise ValueError(f"Unknown token context: {event.context}")

        self.token_usage.total.add(event.usage)