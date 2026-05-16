# Cycle 049 Risk Scan

## Pre-Review Notes

- Do not change runtime Q&A matching. This cycle is diagnostic-only.
- Keep `.coverage` unstaged.
- Do not convert duplicate Q&A prompts into package validation failures.
- Preserve the exact-match index first-winner behavior from Cycle 048.
- Avoid scanning raw package YAML; use `qa_question_candidates` so English and localized prompts share the same normalized representation used by runtime matching.

## Recommended Regression Tests

- Duplicate English primary questions warn.
- Duplicate localized questions warn and report the localized language.
- Same-item duplicate prompts do not warn.
- CLI doctor includes the new OK/WARN line.
- Existing alias duplicate diagnostics remain unchanged.

