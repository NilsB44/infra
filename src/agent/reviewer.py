import logging
import os
import subprocess

from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


class PRReviewer:
    def __init__(self):
        if not API_KEY:
            logger.error("⚠️ GEMINI_API_KEY not found.")
            self.client = None
        else:
            self.client = genai.Client(api_key=API_KEY)

    def get_pr_diff(self) -> str | None:
        try:
            # We assume we are in a PR checkout context
            # Get the diff between the PR branch and the base branch (usually main)
            # gh pr view --json diff --jq '.diff'
            result = subprocess.run(
                ["gh", "pr", "view", "--json", "diff", "--jq", ".diff"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to get PR diff: {e}")
            return None

    def post_review_comment(self, comment: str):
        if not GITHUB_TOKEN:
            logger.warning("⚠️ GITHUB_TOKEN not found. Cannot post comment.")
            print(comment)
            return

        try:
            # Post the AI review as a comment on the PR
            subprocess.run(
                ["gh", "pr", "comment", "--body", comment],
                check=True,
            )
            logger.info("✅ Successfully posted review comment.")
        except Exception as e:
            logger.error(f"Failed to post PR comment: {e}")

    def analyze_diff(self, diff: str) -> str:
        if not self.client:
            return "AI Review skipped: No API Key."

        prompt = f"""
        You are a Senior Software Engineer. Review the following Git diff for a Pull Request.

        Provide:
        1. A summary of the changes.
        2. Potential bugs or performance issues.
        3. Suggestions for improvement (clean code, style, logic).
        4. Security concerns (secrets, injections).

        DIFF:
        {diff[:15000]}  # Truncate if too long
        """

        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            return response.text
        except Exception as e:
            return f"AI Analysis failed: {e}"

    def run(self):
        logger.info("🔍 Fetching PR diff...")
        diff = self.get_pr_diff()

        if not diff:
            logger.info("✨ No diff found or not in a PR context.")
            return

        logger.info("🧠 Analyzing with Gemini AI...")
        review = self.analyze_diff(diff)

        logger.info("💬 Posting review comment...")
        self.post_review_comment(f"## 🤖 AI Code Review\n\n{review}")


def main():
    reviewer = PRReviewer()
    reviewer.run()


if __name__ == "__main__":
    main()
