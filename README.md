# Access Risk Copilot

**[Open the live dashboard →](https://vanshika1302.github.io/Access-Risk-Copilot/)**

## TL;DR

**Problem.** Access requests get approved or denied by a person. Which ones deserve a second look, and can an LLM explain why without making things up? This project flags risky requests with SQL controls, scores denial risk with ML, has an LLM write an audit finding for each flagged case, and checks every finding against the SQL facts.

| 0.863 | 2.5x | 0 / 60 |
|---|---|---|
| **Test AUC**, random forest predicting denied requests (logistic regression 0.851) | **High-risk-resource lift**: 14.7% of flagged held-out requests were denied vs 5.8% overall | **Silent AI errors** on the held-out test set, scored once (dev: 0 / 77) |

![Dashboard](docs/screenshot.png)

The 0 / 60 is a small sample: with no events in 60 cases the true silent-error rate could still be about 5%. See [Limitations](#limitations).

## Data

[Amazon Employee Access Challenge](https://www.kaggle.com/c/amazon-employee-access-challenge), fetched from OpenML (`Amazon_employee_access`, did 4135, no login): 32,769 real access requests, 9 anonymised ID columns (resource, manager, role and department IDs) and the outcome (1,897 denied, 5.8%). Every column is an opaque ID, so nothing here has a human name. Raw file is in `data/raw/` (gitignored); `python etl/load.py` rebuilds the warehouse.

## What is in it

| Piece | Where | What it does |
|---|---|---|
| SQL controls | `sql/controls.sql`, `etl/` | DuckDB views: segregation of duties, unusual access for a department, high-risk resource |
| ML | `ml/train.py` | Logistic regression then random forest, 60/20/20 stratified split, AUC and top drivers |
| AI layer | `ai/` | `claude -p` writes a finding per flagged case, schema-checked, tools disabled |
| Evals | `ai/scoring.py`, `ai/evaluate.py` | Findings vs SQL facts; test set scored once |
| Dashboard | `dashboard/template.html` → `index.html` | Static page for GitHub Pages |
| Tableau | `tableau/*.csv` | Scored request extract (32,769 rows) and the 60 test findings |

### The three controls
- **Segregation of duties (SoD).** A manager's approved requests for the same resource come from both roles of a conflicting `ROLE_FAMILY` pair. Without an employee ID, "one person holds both" cannot be tested; manager plus resource is the closest real signal. The 6 conflict pairs are an **illustrative, seeded list** (`etl/sod_pairs.py`), not real policy. 66 flags.
- **Unusual access for a department.** The department/resource pair is under 1% of the department's requests and seen fewer than 3 times. 8,521 flags (too many to review in practice; see limitations).
- **High-risk resource.** Top decile of resources by denial rate, using only training rows. 949 flags.

### ML
Chosen on dev, test scored once. Random forest: dev AUC 0.865, **test 0.863**. Logistic regression: dev 0.858, **test 0.851**. Top 5% of test scores contain 55% denials and catch 47% of all denials. Top drivers (random forest permutation importance): manager, department, resource. These are ID columns, so they say where risk concentrates, not why.

### AI layer and evals
Claude (`claude-sonnet-5-5`) runs through Claude Code headless mode, no API key: `--tools ""`, no skills or MCP, no settings, empty working directory, API keys removed from the environment, JSON schema output, recordings replayed from `data/recordings/`. Each finding must set three claims (SoD, unusual, high-risk), quote three numbers, and say if it is uncertain.

The scorer buckets every finding: correct, correct but flagged uncertain, **caught** (wrong, flagged uncertain), **silent** (wrong, not flagged). Errors are: a claim that differs from the SQL flag, a quoted number that differs, any other number in the text, or an SoD case rated low or auto-approved. Prompt v1 was run on 77 dev cases and **not changed**; 60 test cases were then generated and scored once (a second scoring is refused in code).

| Set | Cases | Correct | Correct, flagged uncertain | Caught | Silent |
|---|---|---|---|---|---|
| Dev | 77 | 53 | 24 | 0 | 0 |
| **Test, scored once** | 60 | 41 | 19 | 0 | **0** |

## Limitations
- **Small sample.** 0 silent errors in 60 does not mean zero; the 95% upper bound is about 5% (about 2% over all 137).
- The scorer checks structured claims and numbers. It does **not** judge free-text reasoning or tone; I read a sample by eye.
- The template baseline (fills a sentence from the facts) is correct by construction, so the LLM adds readable explanation, not accuracy. Findings are only as good as the SQL facts they are given.
- Controls are rules I wrote on anonymised IDs. SoD pairs are illustrative; SoD flags only approved requests, so their denial rate is 0 by design.
- Findings were written for a sample (137 cases), not all flagged requests, and through a subscription, not the API.
- ML drivers are anonymised IDs and the data is from 2010-2011.

## Run it
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python etl/load.py              # warehouse + SQL controls (needs data/raw/amazon_access.arff from OpenML)
.venv/bin/python ml/train.py              # models, AUC, scores
.venv/bin/python -m ai.facts              # case samples
.venv/bin/python -m ai.findings --split dev --live    # live Claude Code calls; omit --live to replay recordings
.venv/bin/python -m ai.evaluate           # scores dev, and test once
.venv/bin/python scripts/export_dashboard.py          # index.html + tableau/ CSVs
.venv/bin/pytest
```
Working rules are in `CLAUDE.md`, choices in `DECISIONS.md`, vocabulary in `GLOSSARY.md`, the plan in `.scratch/access-risk-copilot/`.
