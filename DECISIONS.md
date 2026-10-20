# Decisions

Grilling questions answered with the recommended option, one-line reason each.

| # | Question | Decision | Reason |
|---|---|---|---|
| 1 | Data source | OpenML `Amazon_employee_access` (did 4135, 32,769 rows, 9 ID features + `target`) | No login; row count, 5.8% minority class and column list match the Kaggle challenge |
| 2 | Which class is "denied" | `target = 0` is denied (1,897 rows, 5.8%) | Kaggle defines ACTION 1 = approved; OpenML description repeats it |
| 3 | Anonymised IDs | Treat every column as an opaque ID; never invent names | Real names are not in the data; fake labels would mislead |
| 4 | SoD definition | A manager (`MGR_ID`) whose approved requests for the SAME resource come from both roles of a conflicting `ROLE_FAMILY` pair | There is no employee ID, so "one person holds both" is not testable; manager plus resource is the closest real signal |
| 5 | Conflicting pairs | Authored list of ROLE_FAMILY pairs, chosen by a documented seeded rule among high-volume families, labelled illustrative | IDs are anonymised, so true conflicts are unknowable; the rule is reproducible and disclosed |
| 6 | Unusual access for a department | Request where (ROLE_DEPTNAME, RESOURCE) has under 1% of that department's requests and under 3 requests overall | Simple, explainable, tunable |
| 7 | High-risk resource | Top decile of resources by denial rate with at least 20 requests | Uses the labels, but only on the training split to avoid leakage |
| 8 | Split | 60/20/20 train/dev/test, stratified, seed 42; test scored once | Same method as Menu-Profit-Simulator |
| 9 | Models | Logistic regression (one-hot) then random forest; report AUC and top drivers | As specified; AUC suits a 6% minority class |
| 10 | AI layer | `claude -p` with `--tools ""`, JSON schema, no API key in env, fresh empty cwd | Same guarded pattern as Menu-Profit-Simulator; no API key available |
| 11 | AI scope | Findings for a capped sample of flagged cases (about 150), not all | Subscription call budget and time; the cap is disclosed |
| 12 | Silent error | AI finding states a fact that contradicts the SQL facts AND does not flag uncertainty | Mirrors "wrong and unflagged" from Menu-Profit-Simulator |
| 13 | Dashboard | Static single-file `index.html` generated from a template plus JSON, no build tools | Matches the sibling projects, works on GitHub Pages and from disk |
| 14 | Wayfinder step 7 | Small static Kanban viewer in `.scratch/board/` served on a free localhost port | The skill asks for it; it reads map.md and issue files |
