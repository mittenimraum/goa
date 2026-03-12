from openai import OpenAI

from planner import create_plan


class Agent:
    def __init__(self, goal: str, client: OpenAI):
        self.goal = goal
        self.plan = create_plan(goal, client)
        self.language = self.plan.language

    def run(self) -> None:
        print(f"\nDetected Language: {self.language}")
        print(f"\nGoal: {self.goal}")
        print("\nPlan:\n")
        for task in self.plan.tasks:
            print(f"{task.id}. {task.title}")
