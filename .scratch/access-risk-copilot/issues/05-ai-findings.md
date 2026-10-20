# 05 AI audit findings
Type: task
Status: resolved
Blocked by: 03, 04

## Question
claude -p with tools disabled writes a short finding per flagged case.

## Answer
ai/ generates schema-checked findings via claude -p (tools disabled, no key). 77 dev findings recorded in data/recordings (prompt v1). Test findings NOT generated yet: they are produced after the dev score, once.
