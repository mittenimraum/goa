import json

from events import LogEvent, ProgressUpdated, TokensUpdated
from models import Task, TaskSolution
from protocols import Client, EventBus
from tools.search import SearchToolError, web_search
from utils.observability import extract_token_usage
from utils.prompt_loader import load_prompt, load_schema

ALLOWED_SEARCH_REASONS = {
    "needs_current_information",
    "needs_specific_comparison",
    "needs_external_reference"
}

class Worker:
    def __init__(self, client: Client, logger: EventBus) -> None:
        self.client = client
        self.logger = logger

    def run(self, goal: str, language: str, task: Task):
        self.logger.emit(ProgressUpdated("Checking tools use"))

        # Tool Check
        tool_selection = self.select_tool(goal=goal, language=language, task=task)
        tool_results = []

        if tool_selection["tool"] == "web_search":
            query = tool_selection["query"].strip() or task.title

            try:
                self.logger.emit(ProgressUpdated("Doing web search"))
                # Tool Use
                tool_results = web_search(query)

                self.logger.emit(LogEvent(context="TOOL", message="web_search ok"))
            except SearchToolError as exc:
                self.logger.emit(LogEvent(context="TOOL", message=f"web_search failed {exc}"))

        formatted_tool_results = []
        for index, item in enumerate(tool_results, start=1):
            formatted_tool_results.append(f"Result: {index}")
            formatted_tool_results.append(item.to_string())
            formatted_tool_results.append("")

        self.logger.emit(ProgressUpdated("Researching task"))

        # Solver
        result = self.solve(goal=goal, language=language, task=task, tool_results="\n".join(formatted_tool_results).strip())

        formatted_outputs = []
        for index, item in enumerate(tool_results, start=1):
            formatted_outputs.append(f"[{item.url}]({item.url})\n")

        return TaskSolution(
            task=task,
            tool_name=tool_selection["tool"],
            tool_reason=tool_selection["reason"],
            tool_input=tool_selection["query"],
            tool_outputs="".join(formatted_outputs).strip(),
            solution=result["solution"],
            summary=result["summary"])

    def select_tool(self, goal: str, language: str, task: Task):
        prompt_system = load_prompt("task_tools_system.txt")
        prompt_user = load_prompt("task_tools_user.txt")
        prompt_schema = load_schema("task_tools_schema.json")

        self.logger.emit(LogEvent(context="WORKER", message="Tool selection started"))

        response = self.client.generate(
            input=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user.format(goal=goal, task=task.title, language=language)}
            ],
            schema=prompt_schema,
            schema_name="task_tools_output"
        )

        tokens = extract_token_usage(response)
        data = json.loads(response.output_text)

        self.logger.emit(TokensUpdated(context="task_tool", usage= tokens))
        self.logger.emit(LogEvent(context="WORKER", message="Tool selection completed"))
        self.logger.emit(LogEvent("TOKENS", message=tokens.to_string()))

        if data["tool"] == "web_search" and data["reason"] not in ALLOWED_SEARCH_REASONS:
            self.logger.emit(LogEvent(context="GUARDRAIL", message="overrode web_search to none because decision_reason did not justify external search"))

        if data["tool"] not in ("web_search, none"):
            raise ValueError("Invalid tool selector output: unsupported tool")

        return data

    def solve(self, goal: str, language: str, task: Task, tool_results: str):
        prompt_system = load_prompt("task_solver_system.txt")
        prompt_user = load_prompt("task_solver_user.txt")
        prompt_schema = load_schema("task_solver_schema.json")

        self.logger.emit(LogEvent(context="WORKER", message="Solver started"))

        response = self.client.generate(
            input=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user.format(
                    goal=goal,
                    task=task.title,
                    language=language,
                    tool_results=tool_results)}
            ],
            schema=prompt_schema,
            schema_name="task_solver_output"
        )

        tokens = extract_token_usage(response)
        data = json.loads(response.output_text)

        self.logger.emit(TokensUpdated(context="task_solver", usage= tokens))
        self.logger.emit(LogEvent(context="WORKER", message="Solver completed"))
        self.logger.emit(LogEvent("TOKENS", message=tokens.to_string()))

        if "solution" not in data or "summary" not in data:
            raise ValueError("Invalid worker output: missing solution or summary")

        return data



