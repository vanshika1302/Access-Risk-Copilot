# 06 Evals
Type: task
Status: resolved
Blocked by: 05

## Question
Compare findings to SQL facts; dev/test split; silent error rate scored once on test.

## Answer
Test set (60 cases) scored once: 0 silent errors, 0 caught, 41 correct, 19 correct-but-flagged-uncertain. Dev (77): same, 0 errors. Rule of three: true silent rate could still be up to about 5% (test) / 2% (all 137).
