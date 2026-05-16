# Cycle 030 Demand Analysis: Next AiPresenter Slice

Date: 2026-05-16
Role: demand discovery
Scope: review-only demand analysis; no production code edits

## Inputs Reviewed

- Long-running user priorities: keep optimizing AiPresenter demand fit, UI, performance, language/tone coverage, presenter skills, and RingCentralVideo knowledge.
- Cycle 028 summary: `localization-report --require-complete` now provides an optional package-only localization quality gate.
- Cycle 029 summary and review: RingCentral validation targets now have stable explicit `rcv-*` IDs; the review left one small residual risk around mixed flow-plus-entrypoint acceptance draft guidance.
- Current RingCentral validation checklist: `rcv-controller-chat-question` references both `ringcentral.video.toolbar.chat` and `meeting-control-map-demo`.
- Current acceptance draft behavior: `acceptance-draft` already supports `--flow`, `--entrypoint`, and `--checklist-target` together, but `validation-targets` emits only `--checklist-target` for mixed flow-plus-entrypoint targets.
- Current controller summary behavior: the controller has a pure view-model and a single compact operator summary line.
- Current Q&A behavior: question answering is deterministic, localized Chinese aliases are package-owned, and timing is logged, but matching still scans package data at request time.
- Current presenter skills: `app-director` and `live-explainer` already encode general safety boundaries, but there is no RingCentral-specific safety skill.

## Ranking

| Rank | Candidate | Operator/User Value | Implementation Size | Verification Clarity | Recommendation |
| --- | --- | --- | --- | --- | --- |
| 1 | Mixed flow-plus-entrypoint acceptance draft guidance | High for the immediate RingCentral validation workflow. It makes the new stable target IDs more useful by giving operators and subagents a correct draft command for combined workflows like queued Chat interruption during `meeting-control-map-demo`. | Small. Mostly `acceptance_draft_command`, renderer expectations, and CLI tests. | High. Pure unit tests and CLI smoke can prove the exact command includes `--flow`, `--entrypoint`, and `--checklist-target`; no live RingCentral run needed. | Do next. |
| 2 | Controller operator summary rows/UI scanability | High live-operator value. The current single-line summary can get dense as voice readiness, scan state, question outcome, and disabled reasons grow. Rows would reduce scanning friction during demos. | Medium. Pure view-model output is easy, but Tk layout wiring and manual/visual confidence take care. | Medium. Unit tests can cover row data; full UI scanability still needs manual or screenshot review. | Good next UI cycle after the acceptance helper. |
| 3 | RingCentral safety presenter skill | Medium-high strategic value. It codifies privacy/destructive-action rules in a reusable skill, matching the long-running skill-improvement and RingCentral knowledge goals. | Small to medium. Add skill file, wire it into profiles, and update context tests/docs. | Medium-low. Tests can prove loading/formatting, but behavior change is mostly prompt/context quality unless paired with package/runtime safety checks. | Valuable as a docs/presenter-context slice, but not the best immediate implementation slice. |
| 4 | Q&A matcher performance index | Medium future value. It helps package growth and performance hygiene, but current package size is small and question timing is already logged. | Medium. Needs a careful index boundary so package aliases, localized Q&A, legacy aliases, longest-alias precedence, and safety remain unchanged. | Medium. Correctness is easy to test; performance assertions should avoid brittle wall-clock thresholds. | Defer until Q&A/package size grows or timing logs show matcher cost. |

## Recommended Slice

Implement mixed flow-plus-entrypoint acceptance draft guidance.

The immediate product story is: after Cycle 029, operators can choose `rcv-controller-chat-question`, but the generated draft command omits the target's known flow and entrypoint. That weakens the handoff right where the checklist is trying to be most helpful. The next slice should teach `validation-targets` to emit the most specific offline draft command it can safely infer:

```powershell
ai-presenter acceptance-draft --package ringcentral-video --flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat --checklist-target "P0 Controller queued Chat question"
```

This keeps the command read-only, preserves the existing checklist context, and gives the draft renderer enough package context to prefill both the flow and Chat entrypoint sections.

## Acceptance Criteria

- For a validation target with exactly one flow ID and exactly one entrypoint ID, `acceptance_draft_command()` includes both `--flow <flow-id>` and `--entrypoint <entrypoint-id>`.
- `validation-targets --package ringcentral-video --target rcv-controller-chat-question` prints a draft command containing:
  - `--flow meeting-control-map-demo`
  - `--entrypoint ringcentral.video.toolbar.chat`
  - `--checklist-target "P0 Controller queued Chat question"`
- Single-entrypoint targets without a flow keep the current entrypoint-only command shape.
- Single-flow targets without an entrypoint keep the current flow-only command shape.
- Multi-entrypoint or multi-flow group targets still omit ambiguous `--entrypoint` or `--flow` arguments and rely on `--checklist-target`.
- `acceptance-draft` continues to reject a provided entrypoint that is not used by the selected flow.
- The generated mixed command produces a draft with Flow Context, Entrypoint Context, Checklist Context, `Package flow: meeting-control-map-demo`, and an intended step that names `ringcentral.video.toolbar.chat`.
- No live RingCentral interaction is performed, no evidence status is promoted, and no acceptance record is appended.

## Suggested Technical Handoff

- Start with tests in `tests/unit/test_validation_targets.py`:
  - Add a regression for `rcv-controller-chat-question`.
  - Add synthetic cases for single-entrypoint, single-flow, mixed one-plus-one, and ambiguous group behavior if existing tests do not already cover them.
- Add a CLI regression in `tests/unit/test_cli.py` for `validation-targets --target rcv-controller-chat-question`.
- Consider a focused `tests/unit/test_acceptance_manual_record.py` assertion that the mixed command's target data renders both flow and entrypoint contexts.
- Keep implementation inside `src/ai_presenter/acceptance/validation_targets.py`; `manual_record.py` already supports the mixed request and should not need broad changes.
- Run focused verification first:
  - `.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command --no-cov`
  - `.\.venv\Scripts\python -m ruff check src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py tests\unit\test_cli.py tests\unit\test_acceptance_manual_record.py`
  - `.\.venv\Scripts\python -m mypy src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\acceptance\manual_record.py`
- If focused verification is clean, run the normal full pytest/mypy/ruff set before cycle summary.

## Out Of Scope

- Do not run live RingCentralVideo.
- Do not edit `acceptance-runs.md` or promote any evidence level.
- Do not redesign the manual acceptance draft template beyond clearer inferred target context.
- Do not add new validation targets or change `rcv-*` IDs.
- Do not change risky/blocked action policy.
- Do not change controller runtime behavior, Q&A matching, or presenter skill loading in this slice.

## Next Candidates After This Slice

1. Controller operator summary rows/UI scanability: split the current single-line summary into stable rows or fields so the controller remains readable as state grows.
2. RingCentral safety presenter skill: codify RingCentral-specific privacy, recording, leave/end, invite, chat, participant, transcript, and shared-screen boundaries as a reusable skill loaded by RingCentral profiles.
3. Q&A matcher performance index: introduce a deterministic precomputed matcher structure only after package scale or timing logs justify it.
