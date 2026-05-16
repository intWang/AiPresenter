# Cycle 014 Demand Analysis: Demo Flow Lookup

Date: 2026-05-16

## User-Facing Need

Operators need missing or mistyped demo-flow IDs to fail fast and consistently as material packages grow. Entry points already have indexed lookup; demo flows should match that reliability.

## Workflows

- `demo --flow missing-flow --dry-run` reports a clear unknown-flow message with available flows.
- `controller --flow missing-flow --dry-run` reports the same style of message.
- `doctor --package ... --flow missing-flow` uses the same lookup/error source.
- Runtime paths validate flow IDs before desktop automation or background threads.
- Controller question-answer synthetic flows remain resolvable after being appended.

## Acceptance Criteria

- Add package-owned demo-flow lookup with read-only index.
- Reject duplicate demo flow IDs.
- Preserve the unknown-flow message shape with available flow IDs.
- Avoid stale indexes when appending `question-answer-demo`.
- Flow preflight happens before desktop/Tk/thread side effects.
- Focused and full tests pass.

## Risks

- Private indexes can go stale after Pydantic `model_copy(update=...)`.
- Duplicate flow validation is a tightening change.
- Diagnostics wording changes should preserve useful substrings.

## Documentation Suggestions

- Add a README/runbook note to use `flows --package ...` before scripted demos.
- Add a missing-flow dry-run acceptance check.
