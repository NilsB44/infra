import json
import logging
import os
from typing import Any, cast

from src.agent.notifier import Notifier

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MERGED_FILE = "MERGED_REPORT.json"
TASKS_FILE = "tasks_queue.json"


class WeeklySummarizer:
    def load_data(self, file_path: str) -> list[dict[str, Any]]:
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path) as f:
                return cast(list[dict[str, Any]], json.load(f))
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return []

    def generate_summary(self) -> str:
        merged_prs = self.load_data(MERGED_FILE)
        new_tasks = self.load_data(TASKS_FILE)

        summary = "🗓 Weekly Maintenance Summary\n\n"

        if merged_prs:
            summary += f"✅ Merged {len(merged_prs)} Dependabot PRs:\n"
            for pr in merged_prs:
                summary += f"- {pr['repo']} #{pr['number']}: {pr['title']}\n"
        else:
            summary += "✅ No Dependabot PRs needed merging.\n"

        summary += "\n"

        if new_tasks:
            summary += f"📋 Identified {len(new_tasks)} new maintenance tasks:\n"
            for task in new_tasks:
                summary += f"- [{task['project_name']}] {task['tool_name']}: {task['risk_level']} risk\n"
        else:
            summary += "📋 No new maintenance tasks identified.\n"

        return summary

    def run(self) -> None:
        summary = self.generate_summary()
        logger.info("Sending weekly notification...")
        notifier = Notifier()
        notifier.send_notification("Weekly Infra Overhaul", summary)


def main() -> None:
    summarizer = WeeklySummarizer()
    summarizer.run()


if __name__ == "__main__":
    main()
