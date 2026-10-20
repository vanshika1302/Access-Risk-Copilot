# Talking points

**30 seconds.** I took 32,769 real access requests and built three SQL controls, a denial-risk model, and an LLM that writes an audit finding per flagged case. Then I tested the LLM: every finding is checked against the SQL facts, and I report the wrong-and-unflagged ("silent") error rate on a held-out set scored once.

**EY Digital/Tech Risk angle (controls design)**
- Segregation of duties needs an employee ID; the data has none. I said so, used manager plus resource as the closest signal, and labelled the conflict pairs illustrative. Knowing what a control can and cannot test is the judgment.
- I tightened the unusual-access control from 26% of requests flagged to 7.6% because 8,521 flags is not reviewable. I picked the cutoff by volume, not by lift, and disclosed that the second test run was not blind.
- SoD flags approved requests only, so its denial rate is 0 by design: it is a policy control, not a predictor.

**Adobe Data/AI angle (ML and AI risk)**
- Random forest test AUC 0.863 (logistic regression 0.851); the top 5% of scores holds 47% of denials. Drivers are anonymised IDs, so they show where risk concentrates, not why.
- Evals: 0 of 60 silent errors on the test set by the number scorer. Say the caveat first: zero in 60 still allows about 5%.
- The number scorer missed a sentence whose numbers were all real but misused ("137 requests, 132 from the department"). A second LLM judge found it. I calibrated the judge with 24 injected false sentences per split (24 of 24 caught) and still say its recall on subtle errors is unmeasured.
- My first judge flagged 50 of 77 genuine findings because it lacked the context the writer had. That was my bug, found on dev, fixed, then frozen before test.

**Questions to expect**
- *Why trust an LLM to audit an LLM?* I do not fully; the judge is a triage filter and a human adjudicates. I adjudicated alone, which is a stated limit.
- *No API key?* Everything ran through Claude Code headless mode with all tools disabled, recorded for replay; results say nothing about the API path.
- *What would you do next?* A second human reader on the judge flags, and a real employee-level entitlement table for true SoD.
