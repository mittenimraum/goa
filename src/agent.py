
from openai import OpenAI
from rich.console import Console
from rich.live import Live

from nodes.executor import Executor
from nodes.planner import Planner
from ui import ProgressView


class Agent:

    def __init__(self, goal: str, client: OpenAI):
        self.goal = goal
        self.client = client
        self.console = Console()
        self.view = ProgressView(self)
        self.executor = Executor(self.client, on_event=self._handle_event)
        self.spinner_index = 0
        self.progress_message = "Waiting to start"
        self.task_status = {}
        self.plan = None
        self.live = None
        self.solutions = []
        self.stop_spinner = False

    def run(self) -> None:
        self.console.print()

        with Live(self.view, console=self.console, refresh_per_second=8):
            self.plan = Planner(self.goal, self.client).execute()
            self.solutions = self.executor.execute(self.plan)

        self.console.print()

        for solution in self.solutions:
            markdown = solution.to_markdown()
            self.console.rule(f" Task {solution.task.id}. {solution.task.title} ")
            self.console.print()
            self.console.print(markdown)
            self.console.print()


    def _handle_event(self, event) -> None:
        if event.type == "task_started":
            self.task_status[event.payload["task_id"]] = "running"
        elif event.type == "task_completed":
            self.task_status[event.payload["task_id"]] = "done"
        elif event.type == "task_failed":
            self.task_status[event.payload["task_id"]] = "failed"
        elif event.type == "progress_updated":
            self.progress_message = event.payload["message"]
        elif event.type == "execution_finished":
            self.progress_message = f"Finished. Succeeded: {event.payload['success_count']} Failed: {event.payload['failed_count']}"
            self.solutions = event.payload["solutions"]
