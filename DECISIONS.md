# Decisions

Grilling questions answered with the recommended option, one-line reason each.

| # | Question | Decision | Reason |
|---|---|---|---|
| 1 | Data source | OpenML `Amazon_employee_access` (did 4135, 32,769 rows, 9 ID features + `target`) | No login; row count, 5.8% minority class and column list match the Kaggle challenge |
| 2 | Which class is "denied" | `target = 0` is denied (1,897 rows, 5.8%) | Kaggle defines ACTION 1 = approved; OpenML description repeats it |
| 3 | Anonymised IDs | Treat every column as an opaque ID; never invent names | Real names are not in the data; fake labels would mislead |
| 4 | SoD definition | A manager (`MGR_ID`) whose approved requests for the SAME resource come from both roles of a conflicting `ROLE_FAMILY` pair | There is no employee ID, so "one person holds both" is not testable; manager plus resource is the closest real signal |
| 5 | Conflicting pairs | Authored list of ROLE_FAMILY pairs, chosen by a documented seeded rule among high-volume families, labelled illustrative | IDs are anonymised, so true conflicts are unknowable; the rule is reproducible and disclosed |
| 6 | Unusual access for a department | Request whose (ROLE_DEPTNAME, RESOURCE) pair appears exactly once, in a department with at least 300 requests | v2. v1 (pair under 1% of department and under 3 requests) flagged 8,521 requests (26%), too many to review; v2 flags 2,506 (7.6%). Threshold 300 was set by volume, not by denial lift (larger departments showed lower lift, so lift was not tuned for) |
| 7 | High-risk resource | Top decile of resources by denial rate with at least 20 requests | Uses the labels, but only on the training split to avoid leakage |
| 8 | Split | 60/20/20 train/dev/test, stratified, seed 42; test scored once | Same method as Menu-Profit-Simulator |
| 9 | Models | Logistic regression (one-hot) then random forest; report AUC and top drivers | As specified; AUC suits a 6% minority class |
| 10 | AI layer | `claude -p` with `--tools ""`, JSON schema, no API key in env, fresh empty cwd | Same guarded pattern as Menu-Profit-Simulator; no API key available |
| 11 | AI scope | Findings for a capped sample of flagged cases (about 150), not all | Subscription call budget and time; the cap is disclosed |
| 12 | Silent error | AI finding states a fact that contradicts the SQL facts AND does not flag uncertainty | Mirrors "wrong and unflagged" from Menu-Profit-Simulator |
| 13 | Dashboard | Static single-file `index.html` generated from a template plus JSON, no build tools | Matches the sibling projects, works on GitHub Pages and from disk |
| 14 | Wayfinder step 7 | Small static Kanban viewer in `.scratch/board/` served on a free localhost port | The skill asks for it; it reads map.md and issue files |
| 15 | Re-run after tightening control 6 | Discarded the v1 AI findings and test score (kept in `outputs/discarded_v1/`, `data/recordings_v1/`); regenerated dev and test findings with prompt v1 unchanged, test scored once again | The control changed, so the case samples and facts changed; the v1 test result no longer describes the shipped controls. Caveat: I had seen the v1 test result, so the v2 test set is not blind in the strict sense |
| 16 | Free-text check | Second `claude -p` judge, developed on dev (j1 -> j2), frozen, run once on test; calibrated with 24 injected false sentences per split; flags adjudicated by hand | The number scorer cannot see misused-but-real numbers; the injected set shows whether the judge can detect errors at all. Judge fix was a missing-context bug (field definitions), not tuning to results |
