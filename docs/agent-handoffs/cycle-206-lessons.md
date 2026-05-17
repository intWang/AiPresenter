# Cycle 206 Lessons: Guard Option Discoverability

## Reusable Lesson

When adding a sidecar guard option, make its scope discoverable in both CLI help and operator runbooks. The help should say what the option validates and what it does not do.

## Prompt Pattern

Ask: "Could an operator read this help text and think the option creates or proves live evidence?" If yes, add explicit boundary wording such as "not live evidence" and cross-link where real evidence must be recorded.

## Test Lesson

Protect help text for evidence-sensitive options. CLI help tests are cheap and catch regressions where a precise guard-source explanation drifts back into vague path wording.

## Follow-Up Candidates

- Add a short `validation-targets` examples section if CLI documentation grows beyond the runbook.
- Consider exposing a structured status object for loaded source paths if JSON output is added later.
