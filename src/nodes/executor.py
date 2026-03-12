
from openai import OpenAI

from models import Plan, TaskSolution
from nodes.worker import Worker


class Executor:
    def __init__(self, plan: Plan, client: OpenAI) -> None:
        self.plan = plan
        self.client = client

    def execute(self) -> list[TaskSolution]:

        solutions: list[TaskSolution] = []

        for task in self.plan.tasks:
            worker = Worker(self.client)

            solution = worker.run(goal=self.plan.goal, language=self.plan.language, task=task)
            solutions.append(solution)

        return solutions

