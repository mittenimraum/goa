import os
from typing import Any

from openai import OpenAI
from openai.types.responses import Response


class OpenAIClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self._client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate(self, *, input: Any, schema: dict, schema_name: str) -> Response:
        return self._client.responses.create(
            model=self.model,
            input=input,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": schema,
                    "strict": True
                }
            }
        )