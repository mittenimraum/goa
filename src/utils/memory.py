import os
from dataclasses import dataclass

from models import TaskSolution


@dataclass
class MemoryEntry:
    task_title: str
    task_summary: str

    def to_string(self, index: int | None = None) -> str:
        prefix = f"{index}. " if index is not None else ""
        return (
            f"{prefix}Task: {self.task_title}\n"
            f"  Summary: {self.task_summary}"
        )

    def size(self, index:int | None = None) -> int:
        return len(self.to_string(index=index).encode("utf-8"))

class WorkingMemory:
    def __init__(self, max_bytes: int | None = None) -> None:
        env_value = os.getenv("GOA_MEMORY_MAX_BYTES", "4096")
        self.max_bytes = max_bytes if max_bytes is not None else int(env_value)
        self.entries = []

    def add (self, solution: TaskSolution) -> None:
        self.entries.append(MemoryEntry(task_title=solution.task.title, task_summary=solution.summary.strip()))
        self._trim_to_budget()

    def _serialize(self, entries: list[MemoryEntry]) -> str:
        return "\n".join(
            entry.to_string(index=i)
            for i, entry in enumerate(entries, start=1)
        )

    def _size(self, entries: list[MemoryEntry]) -> int:
        return len(self._serialize(entries).encode("utf-8"))

    def _trim_to_budget(self) -> None:
        trimmed = list(self.entries)
        while trimmed and self._size(trimmed) > self.max_bytes:
            trimmed.pop()
        self.entries = trimmed

    def as_text(self) -> str:
        if not self.entries:
            return "No previous task summaries"
        return self._serialize(self.entries)

    def to_list(self) -> list[dict[str, str]]:
        return [
            {
                "task_title": entry.task_title,
                "task_summary": entry.task_summary
            }
            for entry in self.entries
        ]
