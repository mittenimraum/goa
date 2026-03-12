from rich.console import RenderableType


class ProgressView:
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, agent):
        self.agent = agent
        self.spinner_index = 0

    def __rich__(self) -> RenderableType:
        self.spinner_index += 1
        lines = []
        if self.agent.plan is None:
            lines.append(f"{self.SPINNER_FRAMES[self.spinner_index % len(self.SPINNER_FRAMES)]}")
            return "".join(lines)
        lines.append(f"Goal: {self.agent.goal}\n")
        lines.append("Plan:")
        for task in self.agent.plan.tasks:
            status = self.agent.task_status.get(task.id)
            if status == "done":
                prefix = "✔"
            elif status == "running":
                prefix = "➜"
            elif status == "failed":
                prefix = "✖"
            else:
                prefix = " "
            lines.append(f"{prefix} {task.id}. {task.title}")
        lines.append("")
        lines.append(f"{self.SPINNER_FRAMES[self.spinner_index % len(self.SPINNER_FRAMES)]} {self.agent.progress_message}")
        return "\n".join(lines)
