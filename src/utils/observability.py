from datetime import datetime, timezone

from events import LogEvent
from models import TokenUsage


def extract_token_usage(response) -> TokenUsage:
    usage = getattr(response, "usage", None)
    if usage is None:
        return TokenUsage()
    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    return TokenUsage(input_tokens, output_tokens, input_tokens + output_tokens)

def format_log_event(event: LogEvent) -> str:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    return f"[{ts}] [{event.context}] {event.message}"