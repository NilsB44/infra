import json
import logging
import os
import sys
from typing import Any

from google import genai
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TRENDING_FILE = "trending_tech.json"
API_KEY = os.environ.get("GEMINI_API_KEY")


class CandidateUpgrade(BaseModel):
    project_name: str
    tool_name: str
    justification: str
    action_plan: str
    risk_level: str = Field(description="Low, Medium, or High")


class Orchestrator:
    def __init__(self) -> None:
        if not API_KEY:
            logger.warning("⚠️ GEMINI_API_KEY not found. Agentic features will be mocked.")
            self.client = None
        else:
            self.client = genai.Client(api_key=API_KEY)

    def load_trending(self) -> list[dict[str, Any]]:
        if not os.path.exists(TRENDING_FILE):
            logger.error(f"❌ {TRENDING_FILE} not found. Run fetch_trending.py first.")
            return []
        with open(TRENDING_FILE) as f:
            from typing import cast

            return cast(list[dict[str, Any]], json.load(f))

    def analyze_relevance(
        self, trending_repos: list[dict[str, Any]], target_projects: list[str]
    ) -> list[CandidateUpgrade]:
        """
        Uses Gemini to cross-reference trending tech with our projects.
        """
        if not self.client:
            return []

        logger.info(
            f"🧠 Agentic Analyst scanning {len(trending_repos)} trending repos "
            f"against {len(target_projects)} projects..."
        )

        # Simplified context for the LLM
        trending_summary = "\n".join(
            [
                f"- {r['name']} ({r['language']}): {r['description']}"
                for r in trending_repos[:15]  # Limit to top 15 to save tokens
            ]
        )

        upgrades: list[CandidateUpgrade] = []

        # In a real loop, we would read the actual project files (pyproject.toml, etc.)
        # For now, we simulate knowledge of the stack based on the repo names.

        prompt = f"""
        You are a Senior DevOps Architect.

        OUR PROJECTS:
        1. WebScraper (Python, Crawl4AI, Gemini, Pydantic)
        2. CarbonFootPrint (Python, Terraform)
        3. Eco-audit-web (Next.js, TypeScript)
        4. infra (Python, Orchestration)

        TRENDING TECH THIS MONTH:
        {trending_summary}

        INSTRUCTIONS:
        1. Identify if any of the "Trending Tech" libraries or tools are HIGHLY relevant upgrades to "Our Projects".
        2. Focus on: Performance, Security, Developer Experience (e.g., new linters, faster bundlers).
        3. Ignore irrelevant stuff (e.g., don't suggest a Swift game engine for a Python web scraper).
        4. If a trending item is already used (like 'uv'), suggest an upgrade check.

        Return a JSON object with a list of 'candidates' matching the CandidateUpgrade schema.
        """

        try:
            # Using 'gemini-1.5-flash' for speed/cost.
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"response_mime_type": "application/json", "response_schema": list[CandidateUpgrade]},
            )

            from typing import cast

            if response.parsed:
                upgrades = cast(list[CandidateUpgrade], response.parsed)
                logger.info(f"💡 Gemini identified {len(upgrades)} potential upgrades.")

        except Exception as e:
            logger.error(f"❌ Gemini analysis failed: {e}")

        return upgrades

    def plan_tasks(self, upgrades: list[CandidateUpgrade]) -> None:
        """
        Saves the identified upgrades as a prioritized task list.
        """
        if not upgrades:
            logger.info("✨ No upgrades necessary at this time.")
            return

        logger.info("📋 Planning execution for identified upgrades...")
        tasks = [u.model_dump() for u in upgrades]

        with open("tasks_queue.json", "w") as f:
            json.dump(tasks, f, indent=2)

        logger.info(f"✅ Saved {len(tasks)} tasks to tasks_queue.json")


def main() -> None:
    orchestrator = Orchestrator()
    trending = orchestrator.load_trending()
    if not trending:
        sys.exit(1)

    # Define our managed repos
    projects = ["WebScraper", "CarbonFootPrint", "Eco-audit-web", "infra"]

    candidates = orchestrator.analyze_relevance(trending, projects)
    orchestrator.plan_tasks(candidates)


if __name__ == "__main__":
    main()
