
from openai import OpenAI

from events import (
    ExecutorCompleted,
    LogEvent,
    ProgressUpdated,
    TaskCompleted,
    TaskFailed,
    TaskStarted,
)
from models import Plan, TaskSolution
from nodes.worker import Worker
from utils.notification_center import NotificationCenter


class Executor:
    def __init__(self, client: OpenAI, logger: NotificationCenter) -> None:
        self.client = client
        self.logger = logger

    def execute(self, plan: Plan) -> list[TaskSolution]:

        solutions: list[TaskSolution] = []

        self.logger.emit(ProgressUpdated(f"Starting execution of {len(plan.tasks)} tasks"))
        self.logger.emit(LogEvent(context="EXECUTOR", message=f"Starting work on {len(plan.tasks)} tasks"))

        for index, task in enumerate(plan.tasks, start=1):
            task.status = "running"

            self.logger.emit(TaskStarted(task))
            self.logger.emit(ProgressUpdated(f"Starting work on task {index}"))
            self.logger.emit(LogEvent(context="EXECUTOR", message=f"Starting execution of task {index}"))

            try:
                worker = Worker(self.client, logger=self.logger)
                solution = worker.run(goal=plan.goal, language=plan.language, task=task)
                solutions.append(solution)

                task.status = "done"

                self.logger.emit(TaskCompleted(task))
                self.logger.emit(ProgressUpdated(f"Completed task {index}/{len(plan.tasks)}: {task.title}"))
            except Exception as exc:
                task.status = "failed"
                task.error = str(exc)

                self.logger.emit(TaskFailed(task, error=task.error))
                self.logger.emit(ProgressUpdated(f"Failed task {index}/{len(plan.tasks)}: {task.title}"))
                self.logger.emit(LogEvent(context="EXECUTOR", message=f"Task execution failed for task id {task.id} error: {exc}"))

        success_count = sum(1 for t in plan.tasks if t.status == "done")
        failed_count = sum(1 for t in plan.tasks if t.status == "failed")

        self.logger.emit(ExecutorCompleted(solutions=solutions, success_count=success_count, failed_count=failed_count))
        self.logger.emit(LogEvent(context="EXECUTOR", message=f"Completed execution (successful: {success_count} failed: {failed_count})"))

        return solutions