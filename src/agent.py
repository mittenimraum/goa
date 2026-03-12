from openai import OpenAI
from rich.console import Console

from nodes.executor import Executor
from nodes.planner import Planner


class Agent:
    def __init__(self, goal: str, client: OpenAI):
        self.goal = goal
        self.client=client
        self.console = Console()

    def run(self) -> None:
        self.console.print(f"\nGoal: {self.goal}")
        plan = Planner(self.goal, self.client).execute()

        self.console.print("\nPlan:\n")

        for task in plan.tasks:
             self.console.print(f"{task.id}. {task.title}")

        solutions = Executor(plan, self.client).execute()

        for solution in solutions:
            markdown = solution.to_markdown()
            self.console.print(markdown)
