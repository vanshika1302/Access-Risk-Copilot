# What to review

1. **SoD definition and the 6 conflict pairs** (`DECISIONS.md` rows 4-5, `etl/sod_pairs.py`). Authored and illustrative; decide whether you are comfortable presenting it that way in an interview.
2. **Unusual-access control v2.** Tightened from 26% to 7.6% of requests; v1 AI results are archived in `outputs/discarded_v1/`. The second test run was not blind (I had seen the first); disclosed in the README.
3. **Eval honesty.** 0/60 silent errors is a small sample and the scorer checks claims and numbers, not free text. Read a few findings in `outputs/findings_test.json`.
4. **Dashboard** at https://vanshika1302.github.io/Access-Risk-Copilot/ (Pages may take a minute). Check it in light mode too.
5. **Tableau**: `tableau/access_requests_scored.csv` (4.6 MB, one row per request) is the main extract; `ai_findings_test.csv` is the findings.
6. **Committed model outputs**: `data/recordings/` (137 Claude Code replays) and `outputs/`. Raw data and the DuckDB file are gitignored.
7. Note: the dev run needed two retries after timeouts (fixed in `ai/client.py`); the prompt was not changed.
