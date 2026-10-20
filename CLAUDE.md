# Access Risk Copilot: working rules

1. Work autonomously through the map (`.scratch/access-risk-copilot/map.md`) in dependency order.
2. For grilling questions, choose the recommended option and log each decision with a one-line reason in `DECISIONS.md`.
3. After each ticket: run tests (`.venv/bin/pytest`), commit, and push to main.
4. Only stop if something fails 3 times, a decision would change scope, or a login, key, or anything that costs money is needed.
5. Write large files in small pieces and commit often (the connection drops).
6. When done, write a short summary of what to review (`REVIEW.md`).

## Conventions
- Python in `.venv` (`python3 -m venv .venv`; `pip install -r requirements.txt`). No uv here.
- Issue tracker: local markdown under `.scratch/` (see `~/.claude/agent-docs/issue-tracker.md`). Vocabulary: `GLOSSARY.md`; ADRs in `docs/adr/`.
- Never create accounts, accept terms, or use an API key. LLM calls go through `claude -p` with all tools disabled.
- Raw data lives in `data/raw/` (gitignored).
