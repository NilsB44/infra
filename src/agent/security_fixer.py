import json
import logging
import os
from typing import Any

from github import Auth, Github

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MANAGED_REPOS = [
    "NilsB44/Buss",
    "NilsB44/CarbonCalculator",
    "NilsB44/Eco-audit-web",
    "NilsB44/infra",
    "NilsB44/ai-coding-agent",
    "NilsB44/WebScraper",
]


class SecurityFixer:
    def __init__(self, token: str | None) -> None:
        if token:
            auth = Auth.Token(token)
            self.gh = Github(auth=auth)
        else:
            self.gh = Github()
        self.security_alerts: list[dict[str, Any]] = []

    def scan_repo(self, repo_full_name: str) -> None:
        try:
            repo = self.gh.get_repo(repo_full_name)
            logger.info(f"🛡️ Scanning {repo_full_name} for security alerts...")

            # Use get_dependabot_alerts (requires advanced security or public repo)
            try:
                alerts = repo.get_dependabot_alerts(state="open")
                alert_count = 0
                for alert in alerts:
                    alert_count += 1
                    self.security_alerts.append(
                        {
                            "repo": repo.name,
                            "severity": alert.security_advisory.severity,
                            "package": alert.security_vulnerability.package.name,
                            "advisory": alert.security_advisory.summary,
                            "url": alert.html_url,
                        }
                    )
                logger.info(f"✅ Found {alert_count} open security alerts in {repo_full_name}.")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch Dependabot alerts for {repo_full_name}: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to process {repo_full_name}: {e}")

    def run(self) -> None:
        for repo_name in MANAGED_REPOS:
            self.scan_repo(repo_name)

        # Save report
        with open("SECURITY_REPORT.json", "w") as f:
            json.dump(self.security_alerts, f, indent=2)
        logger.info(f"✅ Saved security report with {len(self.security_alerts)} alerts.")


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    fixer = SecurityFixer(token)
    fixer.run()


if __name__ == "__main__":
    main()
