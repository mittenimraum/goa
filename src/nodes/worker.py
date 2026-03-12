import json
import os

from openai import OpenAI

from models import Task, TaskSolution
from tools.search import SearchToolError, web_search
from utils.prompt_loader import load_prompt, load_schema

ALLOWED_SEARCH_REASONS = {
    "needs_current_information",
    "needs_specific_comparison",
    "needs_external_reference"
}

class Worker:
    def __init__(self, client: OpenAI) -> None:
        self.client = client
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def select_tool(self, goal: str, language: str, task: Task):
        prompt_system = load_prompt("task_tools_system.txt")
        prompt_user = load_prompt("task_tools_user.txt")
        prompt_schema = load_schema("task_tools_schema.json")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user.format(goal=goal, task=task.title, language=language)}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "task_tools_output",
                    "schema": prompt_schema,
                    "strict": True
                }
            }
        )

        data = json.loads(response.output_text)

        if data["tool"] not in ("web_search, none"):
            raise ValueError("Invalid tool selector output: unsupported tool")

        return data

    def solve(self, goal: str, language: str, task: Task, tool_results: str):
        prompt_system = load_prompt("task_solver_system.txt")
        prompt_user = load_prompt("task_solver_user.txt")
        prompt_schema = load_schema("task_solver_schema.json")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user.format(
                    goal=goal,
                    task=task.title,
                    language=language,
                    tool_results=tool_results)}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "task_tools_output",
                    "schema": prompt_schema,
                    "strict": True
                }
            }
        )

        data = json.loads(response.output_text)

        if "solution" not in data or "summary" not in data:
            raise ValueError("Invalid worker output: missing solution or summary")

        return data

    def run(self, goal: str, language: str, task: Task):
        tool_selection = self.select_tool(goal=goal, language=language, task=task)
        tool_results = []

        if tool_selection["tool"] == "web_search":
            query = tool_selection["query"].strip() or task.title

            try:
                tool_results = web_search(query)
            except SearchToolError as exc:
                print(f"{exc}")

        formatted_tool_results = []
        for index, item in enumerate(tool_results, start=1):
            formatted_tool_results.append(f"Result: {index}")
            formatted_tool_results.append(item.to_string())
            formatted_tool_results.append("")

        result = self.solve(goal=goal, language=language, task=task, tool_results="\n".join(formatted_tool_results).strip())

        return TaskSolution(
            tool_name=tool_selection["tool"],
            tool_reason=tool_selection["reason"],
            tool_input=tool_selection["query"],
            solution=result["solution"],
            summary=result["summary"])

