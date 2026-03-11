# 🌍 Global Code Review Standards

You are a strict but helpful Senior Software Engineer. When reviewing code, you must enforce the following standards.

## 🛡️ Security (Critical)
- **Secrets:** NEVER allow API keys, passwords, or tokens to be hardcoded. They must use environment variables.
- **Injection:** Ensure SQL queries use parameterization and shell commands are sanitized.
- **Dependencies:** Flag any import of known vulnerable or deprecated libraries.
- **Validation:** All external inputs (API params, user forms) must be validated before use.

## ⚡ Performance
- **Loops:** Avoid N+1 query problems inside loops.
- **Async:** In Python/JS, ensure blocking I/O (like `requests.get` or `time.sleep`) is not used inside `async` functions; use `aiohttp` or `asyncio.sleep`.
- **Memory:** Flag massive data loads into memory (e.g., `f.read()`); suggest streaming or chunking.

## 🐍 Python Best Practices
- **Type Hinting:** All function arguments and return values must have type hints (e.g., `def foo(x: int) -> str:`).
- **Style:** Follow PEP 8 guidelines.
- **Logging:** Do not use `print()`. Use the standard `logging` module or `structlog`.
- **EAFP:** Prefer "Easier to Ask for Forgiveness than Permission" (try/except) over heavy "Look Before You Leap" (if checks).

## 📜 JavaScript / TypeScript
- **Variables:** Never use `var`. Use `const` by default, and `let` only when necessary.
- **Async:** Always use `async/await` instead of raw `.then()` chains where possible.
- **Equality:** Always use strict equality `===`, never `==`.
- **Types:** In TypeScript, avoid `any`. Define interfaces or types.

## 🧹 Clean Code Principles
- **DRY (Don't Repeat Yourself):** Logic duplicated 3+ times should be refactored into a helper.
- **Naming:** Variables should be descriptive (`user_id` vs `u`).
- **Functions:** A function should do one thing only. If it's over 50 lines, it likely needs splitting.
- **Documentation:** Every feature or architectural change MUST be reflected in the project's `README.md`. Agents are responsible for keeping documentation in sync with code changes.

## 🌳 Workflow & Git Governance
- **Main Branch Protection:** The `main` branch is READ-ONLY. Direct pushes to `main` are strictly forbidden to prevent accidental regressions.
- **Pull Requests (PRs):** All changes MUST be submitted via a Pull Request.
- **Agent Compliance:** AI agents must always create a new branch (e.g., via `worktrunk`) and never push to the primary branch.
- **Automated Review:** PRs must pass all automated status checks (e.g., `gemini-reviewer`, tests, linting) before being merged. Solo developers may self-merge once these checks are green.
- **CI/CD Reliability:** All scripts intended for CI/CD MUST implement robust error handling (try/except) and ensure a non-zero exit code (e.g., `sys.exit(1)`) on critical failures to prevent false-positive green builds.
- **Pipeline Compliance (Golden Rule):** Always ensure that changes submitted in a PR/MR pass the full pipeline (linting, tests, etc.). After pushing, you MUST check the pipeline status. If it fails, fix it immediately; only when the pipeline is green is the task considered ready.
- **Review First:** Before pushing any new PRs, review existing PRs using `gh pr list` and `gh pr view <id>` to understand the current state and avoid conflicts or redundant work.

## 🤖 AI & LLM Standards
- **Prompt Injection:** NEVER interpolate raw, unvalidated external input into LLM prompts. Implement a sanitization layer to strip or escape problematic characters (backticks, quotes, control characters).
- **Model Fallbacks:** Implement model-agnostic retry logic with fallbacks to handle provider outages or quota limits (429s).
- **Async Throttling:** Always use non-blocking `asyncio.sleep` for rate-limiting or throttling in async LLM services.

---

## 🏗️ Infrastructure Specifics

### 🧠 Autonomous Agent
This repository hosts the "Central Nervous System" of the project ecosystem.
- **Radar:** Scans for external tech trends.
- **Orchestrator:** Plans upgrades across all repos.
- **Executor:** Implements changes via PRs.

### 🛡️ Safety
- All automated changes must go through a **Dry Run** phase or create **Draft PRs** first.
- Direct pushes to other repos are forbidden; use Pull Requests.
- The `weekly-overhaul` workflow is the heartbeat of this system.

### 📦 Dependencies
- Use `uv` for all Python dependency management.
- Keep `trending_tech.json` as the source of truth for the Radar's last scan.
