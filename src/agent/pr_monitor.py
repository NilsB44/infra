import json
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MANAGED_REPOS = [
    "Buss",
    "CarbonFootPrint",
    "Eco-audit-web",
    "infra",
    "marketproj",
    "pyttan",
    "RAG",
    "WebScraper",
]

BASE_DIR = "/home/scila-nils/Documents/personal-repos"


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
    def __init__(self, repos_dir: str):
        self.repos_dir = repos_dir

    def run_gh_command(self, repo_path: str, args: list[str], check: bool = True) -> str:
        try:
            result = subprocess.run(
                ["gh"] + args,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=check,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if not check:
                # If we don't want to check, return stdout even if exit code is non-zero
                return e.stdout.strip() + "\n" + e.stderr.strip()
            logger.error(f"Error running gh command in {repo_path}: {e.stderr}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error running gh command: {e}")
            return ""

    def get_open_prs(self, repo_name: str) -> list[PRStatus]:
        repo_path = os.path.join(self.repos_dir, repo_name)
        if not os.path.exists(os.path.join(repo_path, ".git")):
            logger.warning(f"⚠️ {repo_name} is not a git repository or doesn't exist.")
            return []

        # Get PR list as JSON
        pr_list_json = self.run_gh_command(
            repo_path,
            ["pr", "list", "--state", "open", "--json", "number,title,author,url,mergeable"],
        )

        if not pr_list_json:
            return []

        try:
            prs_data = json.loads(pr_list_json)
            pr_statuses = []
            for pr in prs_data:
                # Use 'gh pr checks' with JSON for reliable parsing
                checks_json = self.run_gh_command(
                    repo_path, ["pr", "checks", str(pr["number"]), "--json", "state"], check=False
                )

                checks_state = "SUCCESS"
                try:
                    checks_data = json.loads(checks_json)
                    if not checks_data:
                        checks_state = "NONE"
                    else:
                        for check in checks_data:
                            state = check.get("state", "").upper()
                            if state in ["FAILURE", "FAILING", "ERROR", "CANCELLED"]:
                                checks_state = "FAILING"
                                break
                            if state in ["PENDING", "IN_PROGRESS", "QUEUED"]:
                                checks_state = "PENDING"
                                # Don't break, check if there's a failure too
                except Exception:
                    # Fallback to string matching if JSON fails
                    if "failing" in checks_json.lower() or "failure" in checks_json.lower():
                        checks_state = "FAILING"
                    elif "pending" in checks_json.lower():
                        checks_state = "PENDING"
                    elif "no checks" in checks_json.lower():
                        checks_state = "NONE"
                    else:
                        checks_state = "PENDING/UNKNOWN"

                pr_statuses.append(
                    PRStatus(
                        repo=repo_name,
                        number=pr["number"],
                        title=pr["title"],
                        author=pr["author"]["login"] if isinstance(pr["author"], dict) else pr["author"],
                        mergeable=pr["mergeable"],
                        checks_status=checks_state,
                        url=pr["url"],
                    )
                )
            return pr_statuses
        except Exception as e:
            logger.error(f"Failed to parse PR data for {repo_name}: {e}")
            return []

    def scan_all(self) -> list[PRStatus]:
        all_prs = []
        for repo in MANAGED_REPOS:
            logger.info(f"Scanning {repo}...")
            all_prs.extend(self.get_open_prs(repo))
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
            report += f"| {pr.repo} | #{pr.number} | {pr.title} | {pr.author} | {merge_icon} {pr.mergeable} | {status_icon} {pr.checks_status} | [Link]({pr.url}) |\n"

        return report


def main() -> None:
    monitor = PRMonitor(BASE_DIR)
    prs = monitor.scan_all()
    report = monitor.generate_report(prs)

    # Save to a file for the weekly report
    with open("PR_REPORT.md", "w") as f:
        f.write(report)

    logger.info(f"✅ Generated report for {len(prs)} PRs in PR_REPORT.md")


if __name__ == "__main__":
    main()
