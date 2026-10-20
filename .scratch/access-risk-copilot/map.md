# Map: Access Risk Copilot

## Destination
A public repo and GitHub Pages dashboard that shows controls design (SQL), ML, and AI-risk judgment on the Amazon Employee Access data, with a README TL;DR (problem, 3 headline numbers, screenshot).

## Notes
- Override of "plan, don't do": execution is carried into the map. Work every ticket in dependency order without stopping (see CLAUDE.md). Grilling answers are recorded in DECISIONS.md.
- Tickets are the build units; each ends with tests, commit, push.
- Data IDs are anonymised; no invented names.

## Decisions so far
- [01 Scope and decisions](issues/01-scope-decisions.md): see DECISIONS.md rows 1-14.
- [02 Data source](issues/02-data-source.md): OpenML did 4135, verified 32,769 rows, saved to data/raw/.
- [03 Warehouse and SQL controls](issues/03-warehouse-sql-controls.md): SQL controls built: SoD 66 flags, unusual access 8,521 (8.8% denied vs 5.8% base), high-risk resource 949 (18.2% denied). SoD pairs illustrative.
- [04 ML models](issues/04-ml-models.md): Logistic regression test AUC 0.851 (dev 0.858); random forest test AUC 0.863 (dev 0.865). Top RF drivers by permutation: manager, department, resource.
- [05 AI audit findings](issues/05-ai-findings.md): ai/ generates schema-checked findings via claude -p (tools disabled, no key). 77 dev findings recorded in data/recordings (prompt v1). Test findings NOT generated yet: they are produced after the dev score, once.

## Not yet specified
- Dashboard layout details (after the numbers exist).
- Whether the AI findings need a second prompt version (after the dev set).

## Out of scope
- Tableau workbook itself (only the CSV extract), real-time scoring, any paid API.
