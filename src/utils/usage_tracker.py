import json
import os
from datetime import datetime
from typing import Any

USAGE_FILE = "data/usage_metrics.json"


class UsageTracker:
    @staticmethod
    def log_use(model: str, tokens_in: int = 0, tokens_out: int = 0, calls: int = 1) -> None:
        """
        Logs LLM usage in a model-agnostic way.
        """
        os.makedirs("data", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")

        data: dict[str, list[dict[str, Any]]] = {}
        if os.path.exists(USAGE_FILE):
            try:
                with open(USAGE_FILE) as f:
                    data = json.load(f)
            except Exception:
                data = {}

        if today not in data:
            data[today] = []

        found = False
        for entry in data[today]:
            if entry["model"] == model:
                entry["calls"] += calls
                entry["tokens_in"] += tokens_in
                entry["tokens_out"] += tokens_out
                found = True
                break

        if not found:
            data[today].append({"model": model, "calls": calls, "tokens_in": tokens_in, "tokens_out": tokens_out})

        with open(USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
