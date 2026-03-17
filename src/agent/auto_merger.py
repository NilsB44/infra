import json
import logging
import os
from typing import Any

from github import Github

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MANAGED_REPOS = [
    "NilsB44/Buss",
    "NilsB44/CarbonCalculator",
    "NilsB44/Eco-audit-web",
    "NilsB44/infra",
    "NilsB44/marknadsinfo",
    "NilsB44/pyttan",
    "NilsB44/ai-coding-agent",
    "NilsB44/WebScraper",
]


class AutoMerger:
    def __init__(self, token: str | None) -> None:
        self.gh = Github(token) if token else Github()
        self.merged_prs: list[dict[str, Any]] = []

    def process_repo(self, repo_full_name: str) -> None:
        try:
            repo = self.gh.get_repo(repo_full_name)
            logger.info(f"Checking for mergeable Dependabot PRs in {repo_full_name}...")

            prs = repo.get_pulls(state="open")
            for pr in prs:
                if "dependabot" not in pr.user.login.lower():
                    continue

                logger.info(f"Checking Dependabot PR #{pr.number}: {pr.title}")

                if not pr.mergeable:
                    logger.info(f"PR #{pr.number} is not mergeable. Skipping.")
                    continue

                combined_status = repo.get_commit(pr.head.sha).get_combined_status().state.upper()

                if combined_status == "SUCCESS":
                    logger.info(f"🚀 PR #{pr.number} is GREEN and MERGEABLE. Merging...")
                    pr.merge(merge_method="merge")
                    logger.info(f"✅ Merged PR #{pr.number}")
                    self.merged_prs.append(
                        {"repo": repo.name, "number": pr.number, "title": pr.title, "url": pr.html_url}
                    )
                else:
                    logger.info(f"PR #{pr.number} status is {combined_status}. Skipping.")

        except Exception as e:
            logger.error(f"Failed to process {repo_full_name}: {e}")

    def run(self) -> None:
        for repo_name in MANAGED_REPOS:
            self.process_repo(repo_name)

        with open("MERGED_REPORT.json", "w") as f:
            json.dump(self.merged_prs, f, indent=2)
        logger.info(f"✅ Saved info for {len(self.merged_prs)} merged PRs to MERGED_REPORT.json")


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    merger = AutoMerger(token)
    merger.run()


if __name__ == "__main__":
    main()
