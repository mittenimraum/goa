import json
import os

from openai import OpenAI

from events import LogEvent, PlanCompleted, PlanStarted, TokensUpdated
from models import Plan, Task
from utils.event_bus import EventBus
from utils.observability import extract_token_usage
from utils.prompt_loader import load_prompt, load_schema


class Planner:
    def __init__(self, goal: str, client: OpenAI, logger: EventBus) -> None:
        self.goal = goal
        self.client = client
        self.logger = logger

    def execute(self) -> Plan:
        prompt_system = load_prompt("planner_system.txt")
        prompt_user = load_prompt("planner_user.txt")
        prompt_schema = load_schema("planner_schema.json")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        self.logger.emit(PlanStarted())
        self.logger.emit(LogEvent(context="PLANNER", message="Planning Started"))

        response = self.client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user.format(goal=self.goal)}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "planner_output",
                    "schema": prompt_schema,
                    "strict": True
                }
            }
        )

        tokens = extract_token_usage(response)
        data = json.loads(response.output_text)
        language = data.get("language", "en")
        tasks = [
            Task(id=id, title=item["title"], status="todo", error=None)
            for id, item in enumerate(data["tasks"], start=1)
        ]
        plan = Plan(goal=self.goal, language=language, tasks=tasks)

        self.logger.emit(PlanCompleted(plan))
        self.logger.emit(TokensUpdated(context="plan", usage=tokens))
        self.logger.emit(LogEvent(context="PLANNER", message="Planning Completed"))
        self.logger.emit(LogEvent("TOKENS", message=tokens.to_string()))

        return plan