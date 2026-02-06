import glob
import os

from google import genai  # Or anthropic / openai

# CONFIGURATION
TARGET_REPO = "../WebScraper" # Change this to your target
API_KEY = os.environ.get("GEMINI_API_KEY")

def get_repo_context(repo_path: str) -> str:
    """
    Scans the target repo to create a compact map of what currently exists.
    It grabs the file tree and contents of key configuration files.
    """
    context = f"## REPOSITORY SCAN: {repo_path}\n\n"

    # 1. Get File Tree (ignoring git/node_modules/venv)
    context += "### FILE STRUCTURE:\n"
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', '.mypy_cache']]
        for file in files:
            file_path = os.path.join(root, file)
            context += f"- {os.path.relpath(file_path, repo_path)}\n"

    # 2. Get Key Config Files (Context for the Agent)
    # Add more key files as needed (Dockerfile, tox.ini, etc.)
    key_files = ['pyproject.toml', 'requirements.txt', '.github/workflows/*.yml', 'README.md', 'Dockerfile']
    context += "\n### KEY CONFIGURATION FILES:\n"

    for pattern in key_files:
        full_pattern = os.path.join(repo_path, pattern)
        for filepath in glob.glob(full_pattern):
            try:
                with open(filepath) as f:
                    context += f"\n#### FILE: {os.path.basename(filepath)}\n```\n{f.read()}\n```\n"
            except Exception:
                pass # Skip if can't read

    return context

def generate_plan(repo_context: str) -> str:
    client = genai.Client(api_key=API_KEY)

    # THE GOLDEN STANDARD PROMPT
    # This is where the "Senior Architect" intelligence lives.
    system_instruction = """
    You are a Staff Software Engineer and DevOps Architect.
    Your goal is to audit a repository and create a strictly ordered "Modernization Roadmap".

    DEFINITIONS OF STATE-OF-THE-ART (2025):
    1.  **Parallel Agent Workflow:** The repo must be compatible with 'Worktrunk' (git worktree manager).
        - Must have a `.gitignore` that ignores sibling worktree directories (e.g., `../{repo_name}.*`).
        - Must have a `CLAUDE.md` or `AGENT.md` that instructs agents to run tests in isolation.
    2.  **Dependency Management:** strict use of `uv` (faster than poetry/pip).
    3.  **CI/CD:** GitHub Actions for formatting, testing, and security.
    4.  **Strict Typing:** `mypy` configured in `pyproject.toml`.

    OUTPUT FORMAT:
    Return a Markdown document titled "ROADMAP.md".
    Divide into PHASES.

    IMPORTANT: Phase 1 MUST be "Enable Parallel Agents".
    - Task: Install `worktrunk` and configure git ignores.
    - Why: Allows multiple AI agents to work on different features simultaneously without git lock conflicts.
    - Prompt: Provide a prompt to install worktrunk (brew/curl) and update .gitignore
      to exclude `*.worktree` or sibling folders.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash", # or gemini-1.5-pro
        contents=[system_instruction, f"Here is the current repository context:\n{repo_context}"]
    )

    return response.text or ""

if __name__ == "__main__":
    print(f"🔍 Scanning {TARGET_REPO}...")
    context = get_repo_context(TARGET_REPO)

    print("🧠 Planning modernization strategy...")
    plan = generate_plan(context)

    output_path = os.path.join(TARGET_REPO, "ROADMAP.md")
    with open(output_path, "w") as f:
        f.write(plan)

    print(f"✅ Plan generated! Check {output_path}")
