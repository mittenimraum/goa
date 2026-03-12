import json
import os

from openai import OpenAI

from models import Plan, Task
from utils.prompt_loader import load_prompt, load_schema


def create_plan(goal: str, client: OpenAI):
    prompt_system = load_prompt("planner_system.txt")
    prompt_user = load_prompt("planner_user.txt")
    prompt_schema = load_schema("planner_schema.json")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user.format(goal=goal)}
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

    data = json.loads(response.output_text)
    language = data.get("language", "en")
    tasks = [
        Task(id=id, title=item["title"])
        for id, item in enumerate(data["tasks"], start=1)
    ]
    return Plan(goal=goal, language=language, tasks=tasks)