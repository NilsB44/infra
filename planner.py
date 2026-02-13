import glob
import logging
import os

from google import genai

# CONFIGURATION
TARGET_REPO = os.environ.get("TARGET_REPO", "../WebScraper")
API_KEY = os.environ.get("GEMINI_API_KEY")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_repo_context(repo_path: str) -> str:
    context = f"## REPOSITORY SCAN: {repo_path}\n\n"
    context += "### FILE STRUCTURE:\n"
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "node_modules", "venv", ".mypy_cache"]]
        for file in files:
            file_path = os.path.join(root, file)
            context += f"- {os.path.relpath(file_path, repo_path)}\n"
    key_files = [
        "pyproject.toml", "package.json", "requirements.txt",
        ".github/workflows/*.yml", "README.md", "Dockerfile"
    ]
    context += "\n### KEY CONFIGURATION FILES:\n"
    for pattern in key_files:
        full_pattern = os.path.join(repo_path, pattern)
        for filepath in glob.glob(full_pattern):
            try:
                with open(filepath) as f:
                    context += f"\n#### FILE: {os.path.basename(filepath)}\n```\n{f.read()}\n```\n"
            except (OSError, UnicodeDecodeError):
                pass
    return context

def generate_plan(repo_context: str) -> str:
    client = genai.Client(api_key=API_KEY)
    system_instruction = """
You are a Staff Software Engineer and DevOps Architect. Divide into PHASES.
Phase 1 MUST be "Enable Parallel Agents" using git worktrees.
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[system_instruction, f"Here is the current repository context:\n{repo_context}"],
    )
    return response.text or ""

if __name__ == "__main__":
    logging.info(f"🔍 Scanning {TARGET_REPO}...")
    context = get_repo_context(TARGET_REPO)
    logging.info("🧠 Planning modernization strategy...")
    plan = generate_plan(context)
    output_path = os.path.join(TARGET_REPO, "ROADMAP.md")
    with open(output_path, "w") as f:
        f.write(plan)
    logging.info(f"✅ Plan generated! Check {output_path}")
