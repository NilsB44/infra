# 🧠 Infra: The Agentic Workflow Coordinator

This repository is the central orchestration unit for an automated, agent-ready GitHub ecosystem. It serves as the "Senior Architect" and "DevOps Lead" for all other projects in this workspace.

## 🏗️ Core Components

### 1. The Infra Planner (`planner.py`)
A state-of-the-art repository auditor. It scans target repositories and generates a **Modernization Roadmap** (`ROADMAP.md`) based on 2026 SOTA standards.
- **Priority One:** Enabling "Parallel Agent Workflows" via Git Worktrees.
- **Standards:** Enforces `uv` for dependency management, strict `mypy` typing, and automated CI/CD.

### 2. Global Code Review Standards (`GEMINI.md`)
The "source of truth" for all AI agents.
- **Centralized:** Other repositories (like `WebScraper`) fetch these rules dynamically during CI runs.
- **Governance:** Mandates PR-only workflows and write-protected `main` branches.
- **Auto-Sync:** Agents are mandated to update `README.md` whenever architectural changes are implemented.

### 3. Automated Reviewer (`.github/workflows/reviewer.yml`)
A reusable GitHub Action that triggers Gemini-powered code reviews on every Pull Request.
- **Critical Blocking:** Automatically blocks merges if "Bug Risk" or "Security" issues are detected.
- **Solo-Friendly:** Allows self-merging once automated checks are green, removing bottlenecks for solo developers.

## 🔄 SOTA 2026: Parallel Agent Workflow

This ecosystem is optimized for **Gemini CLI** using **Git Worktrees** to allow multiple agents to work in parallel without git lock conflicts.

### 1. Multi-Repo Orchestration
To manage multiple repositories simultaneously, boot Gemini CLI with access to the entire workspace:
```bash
# Boot in the root of your repos directory
gemini-cli --include-directories CarbonFootPrint,WebScraper,Eco-audit-web,RAG,infra
```

### 2. Parallelizing with Worktrees (`worktrunk`)
Use `worktrunk` (`wt`) to spawn isolated environments for parallel Gemini CLI sessions:
1.  **Create Worktrees:**
    ```bash
    wt add feature/api-upgrade
    wt add feature/ui-refactor
    ```
2.  **Launch Parallel Agents:** Open separate terminal tabs and launch Gemini CLI in each worktree folder:
    ```bash
    # Tab 1
    cd ../repo.feature-api-upgrade && gemini-cli
    
    # Tab 2
    cd ../repo.feature-ui-refactor && gemini-cli
    ```

### 3. Using Sub-Agents
For complex tasks, use Gemini CLI's built-in sub-agent delegation:
- **Architecture Tasks:** Delegate to `codebase_investigator`.
- **Testing Tasks:** Delegate to a specialized test-agent.
- **CLI Help:** Use `cli_help` for runtime configuration queries.

## 🤖 Workflow Steps

1.  **Plan:** Run `uv run planner.py` to generate the `ROADMAP.md`.
2.  **Branch:** Create an isolated worktree via `wt add <branch-name>`.
3.  **Execute:** Use **Gemini CLI** inside the worktree to implement features.
4.  **Sync:** Ensure the Agent updates the `README.md` to reflect new logic.
5.  **Verify:** Run `uv run ruff check .` and local tests.
6.  **Submit:** Push and open a PR. Gemini Guardian and AI Reviewer will validate.

## 🛠️ Setup

1.  **Dependencies:**
    ```bash
    uv sync --extra dev
    ```
2.  **Configuration:**
    Ensure `GEMINI_API_KEY` is set in your environment.
3.  **Standards:**
    All code in this repo must pass:
    ```bash
    uv run ruff check .
    uv run mypy .
    ```

---
*Optimized for Gemini CLI — Scaling agentic development in 2026.*
