import json
import logging
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TRENDING_URL = "https://github.com/trending?since=monthly"
OUTPUT_JSON = "trending_tech.json"
OUTPUT_MD = "TRENDING.md"


def fetch_trending_repos() -> list[dict[str, Any]]:
    logger.info(f"📡 Fetching GitHub trending repos from {TRENDING_URL}...")
    try:
        response = requests.get(TRENDING_URL, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"❌ Failed to fetch trending page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    repos = []

    # GitHub's trending page structure (subject to change, hence try-except blocks)
    for article in soup.select("article.Box-row"):
        try:
            # Repo Name (Owner/Name)
            title_tag = article.select_one("h2 a")
            if not title_tag:
                continue

            repo_path = title_tag.get("href", "").strip().lstrip("/")

            # Description
            desc_tag = article.select_one("p.col-9")
            description = desc_tag.get_text(strip=True) if desc_tag else "No description."

            # Language
            lang_tag = article.select_one("[itemprop='programmingLanguage']")
            language = lang_tag.get_text(strip=True) if lang_tag else "Unknown"

            # Stars (Total)
            stars_tag = article.select_one("a[href$='/stargazers']")
            stars_total = stars_tag.get_text(strip=True).replace(",", "") if stars_tag else "0"

            repos.append(
                {
                    "name": repo_path,
                    "url": f"https://github.com/{repo_path}",
                    "description": description,
                    "language": language,
                    "stars": stars_total,
                    "fetched_at": datetime.now().isoformat(),
                }
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse a repo row: {e}")

    logger.info(f"✅ Found {len(repos)} trending repositories.")
    return repos


def save_json(repos: list[dict[str, Any]]) -> None:
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)
    logger.info(f"💾 Saved JSON to {OUTPUT_JSON}")


def save_markdown(repos: list[dict[str, Any]]) -> None:
    content = "# 📈 GitHub Trending (Monthly)\n\n"
    content += f"**Fetched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    content += "| Repository | Language | Stars | Description |\n"
    content += "|---|---|---|---|\n"

    for repo in repos:
        name = repo["name"]
        url = repo["url"]
        lang = repo["language"]
        stars = repo["stars"]
        desc = repo["description"]
        # Escape pipes in description to prevent table breaking
        desc = desc.replace("|", "-")

        content += f"| [{name}]({url}) | {lang} | {stars} | {desc} |\n"

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"📝 Saved Markdown to {OUTPUT_MD}")


def main() -> None:
    repos = fetch_trending_repos()
    if repos:
        save_json(repos)
        save_markdown(repos)
    else:
        logger.warning("No repositories found to save.")


if __name__ == "__main__":
    main()
