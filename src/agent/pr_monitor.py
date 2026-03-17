import logging
import os
from dataclasses import dataclass

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


@dataclass
class PRStatus:
    repo: str
    number: int
    title: str
    author: str
    mergeable: str
    checks_status: str
    url: str


class PRMonitor:
    def __init__(self, token: str | None):
        self.gh = Github(token) if token else Github()

    def get_open_prs(self, repo_full_name: str) -> list[PRStatus]:
        try:
            repo = self.gh.get_repo(repo_full_name)
            prs = repo.get_pulls(state="open")
            pr_statuses = []

            for pr in prs:
                head_sha = pr.head.sha
                combined_status = repo.get_commit(head_sha).get_combined_status().state.upper()

                checks_state = "PENDING/UNKNOWN"
                if combined_status == "SUCCESS":
                    checks_state = "SUCCESS"
                elif combined_status in ["FAILURE", "ERROR"]:
                    checks_state = "FAILING"
                elif combined_status == "PENDING":
                    checks_state = "PENDING"

                pr_statuses.append(
                    PRStatus(
                        repo=repo.name,
                        number=pr.number,
                        title=pr.title,
                        author=pr.user.login,
                        mergeable="MERGEABLE" if pr.mergeable else "CONFLICTING",
                        checks_status=checks_state,
                        url=pr.html_url,
                    )
                )
            return pr_statuses
        except Exception as e:
            logger.error(f"Failed to scan {repo_full_name}: {e}")
            return []

    def scan_all(self) -> list[PRStatus]:
        all_prs = []
        for repo_name in MANAGED_REPOS:
            logger.info(f"Scanning {repo_name}...")
            all_prs.extend(self.get_open_prs(repo_name))
        return all_prs

    def generate_report(self, prs: list[PRStatus]) -> str:
        if not prs:
            return "## Pull Request Status\n\n✅ No open Pull Requests found."

        report = "## Pull Request Status\n\n"
        report += "| Repo | PR | Title | Author | Mergeable | Checks | Link |\n"
        report += "|------|----|-------|--------|-----------|--------|------|\n"

        for pr in prs:
            status_icon = "✅" if pr.checks_status == "SUCCESS" else "❌" if pr.checks_status == "FAILING" else "⏳"
            merge_icon = "✅" if pr.mergeable == "MERGEABLE" else "⚠️"
            row = (
                f"| {pr.repo} | #{pr.number} | {pr.title} | {pr.author} | "
                f"{merge_icon} {pr.mergeable} | {status_icon} {pr.checks_status} | [Link]({pr.url}) |\n"
            )
            report += row

        return report


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    monitor = PRMonitor(token)
    prs = monitor.scan_all()
    report = monitor.generate_report(prs)

    with open("PR_REPORT.md", "w") as f:
        f.write(report)

    logger.info(f"✅ Generated report for {len(prs)} PRs in PR_REPORT.md")


if __name__ == "__main__":
    main()
