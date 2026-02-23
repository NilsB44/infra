# Infrastructure Roadmap

## 🎯 Mission
To serve as the central nervous system for the entire repository ecosystem, ensuring all projects adhere to global standards, utilize the latest proven technologies, and maintain high code quality through autonomous orchestration.

## 🏗️ Core Architecture: Autonomous Tech Radar

The infrastructure will evolve from a static standard definition to an active, weekly agentic loop.

### 1. The Radar (Discovery)
- **Script:** `src/radar/fetch_trending.py`
- **Source:** GitHub Trending (Monthly), Python Weekly, Hacker News (simulated via LLM knowledge retrieval or scraping).
- **Output:** A structured `trending_tech.json` and `TRENDING.md` report.
- **Goal:** Identify new libraries, security patches, CI/CD patterns (e.g., `uv` over `poetry`, new `ruff` rules).

### 2. The Analyst (Evaluation)
- **Script:** `src/agent/analyst.py`
- **Input:** `trending_tech.json` + `global_standards.md` + Target Repo `pyproject.toml` / `package.json`.
- **Logic:** Uses Gemini to ask: "Is this trending tool 'X' relevant to project 'Y'? Does it solve a known pain point or improve performance?"
- **Output:** A list of `CandidateUpgrade` objects.

### 3. The Planner (Strategy)
- **Script:** `src/agent/planner.py` (Enhancement of existing logic)
- **Logic:**
    - Groups upgrades by risk level (Low: Linting, Mid: Dep updates, High: Architecture).
    - Checks for dependency conflicts.
    - **Crucial:** Breaks down changes into **atomic** tasks.
- **Output:** A prioritized `tasks_queue.json`.

### 4. The Executor (Implementation)
- **Script:** `src/agent/executor.py`
- **Action:**
    - Clones/Checkouts target repo.
    - Creates a feature branch (e.g., `infra/upgrade-ruff-v0.9`).
    - Applies changes (using Gemini for code mod or shell commands for install).
    - **Verification:** Runs local tests (`uv run pytest`, `npm test`).
    - **Submission:** Creates a Pull Request with a detailed summary.

## 🤖 Workflows

### `weekly-overhaul.yml`
- **Schedule:** Weekly (e.g., Monday 02:00 UTC).
- **Steps:**
    1. Checkout `infra`.
    2. Run **Radar**.
    3. Run **Analyst** (comparing against `WebScraper`, `CarbonFootPrint`, etc.).
    4. Run **Planner**.
    5. Run **Executor** (max 1-2 PRs per week to avoid chaos).

## 📅 Phases

### Phase 1: Foundation (Current)
- [x] Global `GEMINI.md` standards.
- [x] Basic project structure.

### Phase 2: The Radar
- [ ] Implement `fetch_trending.py`.
- [ ] Generate `TRENDING.md` view.

### Phase 3: The Orchestrator
- [ ] Implement `orchestrator.py` (Analyst + Planner).
- [ ] Connect to Gemini API for relevance scoring.

### Phase 4: The Executor (CI/CD)
- [ ] Implement PR creation logic (`PyGithub` or `gh` CLI).
- [ ] Create `weekly-overhaul.yml`.

## 🛡️ Safety Protocols
- **No Direct Pushes:** All changes via PRs.
- **Test Mandate:** PRs must include passing test results in the body.
- **Rate Limit:** Max 3 autonomous PRs per week across the ecosystem.
