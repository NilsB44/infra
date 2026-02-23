# AI Coding Standards

All development in this repository MUST adhere to the global standards defined in the infrastructure coordinator:

👉 **[Global Standards (infra/GEMINI.md)](https://github.com/NilsB44/infra/blob/main/GEMINI.md)**

## Infrastructure Specifics

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
