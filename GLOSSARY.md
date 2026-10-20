# Glossary

**Request**: one row of the data: an employee-role asking for access to a resource, approved or denied.
**Denied**: `target = 0` in the source (Kaggle `ACTION` 1 = approved). The rare class, 5.8%.
**Segregation of duties (SoD)**: no one should hold two conflicting capabilities. Here: a manager's approved requests for one resource come from both roles of a conflicting role-family pair.
**Conflict pair**: an authored, illustrative pair of `ROLE_FAMILY` IDs treated as incompatible.
**Unusual access**: a department/resource pair that appears exactly once, in a department with at least 300 requests.
**High-risk resource**: a resource in the top decile of training-set denial rate (at least 20 requests).
**Flag**: a request matched by at least one control.
**Facts**: the numbers and flags computed by SQL and the model for a case; the AI sees them, the scorer checks against them.
**Finding**: a short audit note written by the LLM for one flagged case.
**Silent error**: a finding that contradicts the facts and does not say it is uncertain.
**Caught error**: a wrong finding that was flagged uncertain.
**Held out**: rows (dev, test) that no control or model was built from.
