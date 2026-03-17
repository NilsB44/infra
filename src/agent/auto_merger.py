import json
import logging
import os
import subprocess

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


class AutoMerger:
    def __init__(self, repos_dir: str):
        self.repos_dir = repos_dir
        self.merged_prs = []

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
                return e.stdout.strip() + "\n" + e.stderr.strip()
            logger.error(f"Error running gh command in {repo_path}: {e.stderr}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error running gh command: {e}")
            return ""

    def process_repo(self, repo_name: str):
        repo_path = os.path.join(self.repos_dir, repo_name)
        if not os.path.exists(os.path.join(repo_path, ".git")):
            return

        logger.info(f"Checking for mergeable Dependabot PRs in {repo_name}...")

        # Get Dependabot PRs
        # Note: Dependabot's author login is usually 'dependabot[bot]' or similar,
        # but 'app/dependabot' in 'gh' output usually translates to author 'dependabot'
        pr_list_json = self.run_gh_command(
            repo_path,
            ["pr", "list", "--author", "app/dependabot", "--state", "open", "--json", "number,title,mergeable,url"],
        )

        if not pr_list_json:
            # Try alternative author name just in case
            pr_list_json = self.run_gh_command(
                repo_path,
                ["pr", "list", "--author", "dependabot", "--state", "open", "--json", "number,title,mergeable,url"],
            )

        if not pr_list_json or pr_list_json.strip() == "[]":
            logger.info(f"No open Dependabot PRs in {repo_name}.")
            return

        try:
            prs = json.loads(pr_list_json)
            for pr in prs:
                pr_num = pr["number"]
                title = pr["title"]

                if pr["mergeable"] != "MERGEABLE":
                    logger.info(f"PR #{pr_num} ('{title}') is not mergeable. Skipping.")
                    continue

                # Check if all CI checks passed
                checks_json = self.run_gh_command(
                    repo_path, ["pr", "checks", str(pr_num), "--json", "state"], check=False
                )

                try:
                    checks_data = json.loads(checks_json)
                    if not checks_data:
                        logger.info(f"PR #{pr_num} has no checks. Skipping.")
                        continue

                    all_passed = True
                    for check in checks_data:
                        if check.get("state") != "SUCCESS":
                            all_passed = False
                            break

                    if all_passed:
                        logger.info(f"🚀 PR #{pr_num} ('{title}') is GREEN and MERGEABLE. Merging...")
                        merge_result = self.run_gh_command(
                            repo_path, ["pr", "merge", str(pr_num), "--merge", "--delete-branch"]
                        )
                        logger.info(f"✅ Merged PR #{pr_num}: {merge_result}")
                        self.merged_prs.append({"repo": repo_name, "number": pr_num, "title": title, "url": pr["url"]})
                    else:
                        logger.info(f"PR #{pr_num} ('{title}') has failing or pending checks. Skipping.")

                except Exception as e:
                    logger.error(f"Failed to check/merge PR #{pr_num} in {repo_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to parse PR list for {repo_name}: {e}")

    def run(self):
        for repo in MANAGED_REPOS:
            self.process_repo(repo)

        # Save merged PRs for the notifier
        with open("MERGED_REPORT.json", "w") as f:
            json.dump(self.merged_prs, f, indent=2)
        logger.info(f"✅ Saved info for {len(self.merged_prs)} merged PRs to MERGED_REPORT.json")


def main():
    merger = AutoMerger(BASE_DIR)
    merger.run()


if __name__ == "__main__":
    main()
