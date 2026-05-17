# Cycle 211 Lessons

Date: 2026-05-17
Cycle: 211
Role: Lessons and carry-forward notes

## What Changed

- Added flow step counts to the CLI loaded-flow summary for both `demo` and
  `controller`.
- Tightened dry-run tests for `meeting-controls-tour` and
  `meeting-control-map-demo`.
- Kept missing-flow and flow-list behavior unchanged.

## What To Preserve

- Keep operator-feedback output additive and prefix-compatible where possible.
- When an output line is printed before a dry-run branch, document that the same
  detail also appears for real runs.
- Continue using focused CLI tests before broader full-gate verification.

## Follow-Up Ideas

- Consider adding package-local onboarding Q&A only after repeated operator
  questions show up in live or manual practice.
- Revisit runbook wording only if testers start using exact CLI output checks
  instead of command success and summary content.
