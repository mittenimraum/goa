
from openai import OpenAI

from events import Event
from models import Plan, TaskSolution
from nodes.worker import Worker


class Executor:
    def __init__(self, client: OpenAI, on_event=None) -> None:
        self.client = client
        self.on_event = on_event

    def emit(self, event_type: str, **payload) -> None:
        if self.on_event:
            self.on_event(Event(type=event_type, payload=payload))

    def execute(self, plan: Plan) -> list[TaskSolution]:

        solutions: list[TaskSolution] = []

        self.emit("plan_started", task_count=len(plan.tasks), tasks=plan.tasks)
        self.emit("progress_updated", message=f"Starting execution of {len(plan.tasks)} tasks")

        for index, task in enumerate(plan.tasks, start=1):
            task.status = "running"

            self.emit("task_started", task_id=task.id, title=task.title, index=index, total=len(plan.tasks))
            self.emit("progress_updated", message=f"Starting work on task {index}")

            try:
                worker = Worker(self.client, on_event=self._handle_event)
                solution = worker.run(goal=plan.goal, language=plan.language, task=task)
                solutions.append(solution)

                task.status = "done"

                self.emit("task_completed", task_id=task.id, title=task.title)
                self.emit("progress_updated", message=f"Completed task {index}/{len(plan.tasks)}: {task.title}")
            except Exception as exc:
                task.status = "failed"
                task.error = str(exc)

                self.emit("task_failed", task_id=task.id, title=task.title, error=task.error)
                self.emit("progress_updated", message=f"Failed task {index}/{len(plan.tasks)}: {task.title}")

        self.emit("execution_finished", solutions=solutions, task_count=len(plan.tasks), success_count=sum(1 for t in plan.tasks if t.status == "done"), failed_count=sum(1 for t in plan.tasks if t.status == "failed"))

        return solutions

    def _handle_event(self, event) -> None:
        self.emit("progress_updated", message=event.payload["message"])