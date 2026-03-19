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

    def load_dict(self, file_path: str) -> dict[str, Any]:
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path) as f:
                return cast(dict[str, Any], json.load(f))
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return {}

    def generate_summary(self) -> str | None:
        merged_prs = self.load_data(MERGED_FILE)
        new_tasks = self.load_data(TASKS_FILE)
        security_alerts = self.load_data("SECURITY_REPORT.json")
        usage_data = self.load_dict("USAGE_REPORT.json")

        if not merged_prs and not new_tasks and not security_alerts and not usage_data:
            return None

        summary = "🗓 Weekly Maintenance Summary\n\n"

        if usage_data:
            summary += "📊 LLM Usage (Past 7 Days):\n"
            for repo_name, metrics in usage_data.items():
                total_calls = 0
                for _date, day_metrics in metrics.items():
                    # metrics is a dict where keys are dates and values are lists of model metrics
                    for model_metric in day_metrics:
                        total_calls += model_metric.get("calls", 0)
                summary += f"- {repo_name}: {total_calls} calls\n"
            summary += "\n"

        if merged_prs:
            summary += f"🚀 Merged {len(merged_prs)} Dependabot PRs:\n"
            # Group by repo
            repos: dict[str, list[dict[str, Any]]] = {}
            for pr in merged_prs:
                repo_name = pr["repo"]
                if repo_name not in repos:
                    repos[repo_name] = []
                repos[repo_name].append(pr)

            for repo_name, prs in repos.items():
                summary += f"\n📦 {repo_name}:\n"
                for pr in prs:
                    summary += f"- #{pr['number']}: {pr['title']}\n"
        else:
            summary += "✅ No Dependabot PRs needed merging.\n"

        summary += "\n"

        if security_alerts:
            summary += f"🛡️ Security Alerts Found ({len(security_alerts)}):\n"
            # Group by repo
            sec_repos: dict[str, list[dict[str, Any]]] = {}
            for alert in security_alerts:
                repo_name = alert["repo"]
                if repo_name not in sec_repos:
                    sec_repos[repo_name] = []
                sec_repos[repo_name].append(alert)

            for repo_name, alerts in sec_repos.items():
                summary += f"- {repo_name}: {len(alerts)} alerts\n"
        else:
            summary += "🛡️ No security alerts found.\n"

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
        if summary:
            logger.info("Sending weekly notification...")
            notifier = Notifier()
            notifier.send_notification("Weekly Infra Overhaul", summary)
        else:
            logger.info("No changes to report. Skipping notification.")


def main() -> None:
    summarizer = WeeklySummarizer()
    summarizer.run()


if __name__ == "__main__":
    main()
