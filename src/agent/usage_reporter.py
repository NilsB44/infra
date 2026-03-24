import base64
import json
import logging
import os
from typing import Any

from github import Auth, Github

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPOS_TO_SCAN = [
    "NilsB44/WebScraper",
    "NilsB44/infra",
    "NilsB44/Eco-audit-web",
    "NilsB44/CarbonCalculator",
    "NilsB44/ai-coding-agent",
    "NilsB44/Buss",
]


class UsageReporter:
    def __init__(self, token: str | None) -> None:
        if token:
            auth = Auth.Token(token)
            self.gh = Github(auth=auth)
        else:
            self.gh = Github()
        self.usage_data: dict[str, Any] = {}

    def fetch_usage(self, repo_full_name: str) -> None:
        try:
            repo = self.gh.get_repo(repo_full_name)
            logger.info(f"📊 Fetching LLM usage for {repo_full_name}...")

            try:
                content = repo.get_contents("data/usage_metrics.json", ref="main")
                if isinstance(content, list):
                    logger.warning(f"⚠️ Found directory instead of file at data/usage_metrics.json in {repo_full_name}")
                    return

                # content.content is base64 encoded
                decoded = base64.b64decode(content.content).decode("utf-8")
                metrics = json.loads(decoded)
                self.usage_data[repo.name] = metrics
                logger.info(f"✅ Successfully fetched usage metrics from {repo_full_name}.")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch usage metrics for {repo_full_name}: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to process {repo_full_name}: {e}")

    def run(self) -> None:
        for repo_name in REPOS_TO_SCAN:
            self.fetch_usage(repo_name)

        # Save report
        with open("USAGE_REPORT.json", "w") as f:
            json.dump(self.usage_data, f, indent=2)
        logger.info("✅ Saved usage report to USAGE_REPORT.json.")


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    reporter = UsageReporter(token)
    reporter.run()


if __name__ == "__main__":
    main()
