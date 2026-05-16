# Cycle 030 Technical Scan: Mixed Validation Draft Guidance

Date: 2026-05-16
Role: technical discovery
Scope: review-only. No production code or tests were edited during this scan; this handoff is the only file added.

## Recommendation

Implement a small acceptance-planning slice: improve `validation-targets` and `acceptance-draft`
guidance for validation targets that intentionally combine one demo flow with one operation
entrypoint.

The best current example is `rcv-controller-chat-question`. The catalog already knows this target is
both:

- `flow_ids=("meeting-control-map-demo",)`
- `entrypoint_ids=("ringcentral.video.toolbar.chat",)`

But the generated draft command currently drops both IDs and keeps only checklist context:

```text
draft: ai-presenter acceptance-draft --package ringcentral-video --checklist-target "P0 Controller queued Chat question"
```

That is safe, but not very helpful. `acceptance-draft` itself already supports
`--flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat` and validates that the
entrypoint belongs to the selected flow. The next slice should let `validation-targets` recommend
that richer draft command for unambiguous single-flow/single-entrypoint targets, then adjust the
draft template's intended-steps wording so the operator sees this as a combined "run the flow, ask or
verify this entrypoint during the flow" scenario.

## Current State

- `src/ai_presenter/acceptance/validation_targets.py:97` builds draft commands with three branches:
  single entrypoint only, single flow only, or checklist-only fallback. Mixed targets fall into the
  fallback branch.
- `src/ai_presenter/acceptance/validation_targets.py:126` renders the target block, including both
  `entrypoints:` and `flows:` lines before the draft command. The information is visible, but the
  recommended command does not use it.
- `src/ai_presenter/acceptance/manual_record.py:62` already validates combined flow plus entrypoint
  requests. If both are supplied, the entrypoint must be present in the flow.
- `src/ai_presenter/acceptance/manual_record.py:187` currently prefers entrypoint wording in
  `Steps executed`, so a combined request pre-fills only
  `Intended target: ringcentral.video.toolbar.chat...` even though the draft also has flow context.
- `tests/unit/test_validation_targets.py:126` already verifies that `rcv-controller-chat-question`
  separates flow IDs from entrypoint IDs.
- `tests/unit/test_acceptance_manual_record.py:43` covers flow-only drafts, and
  `tests/unit/test_acceptance_manual_record.py:62` covers rejection when an entrypoint is outside a
  selected flow. There is no positive mixed flow-plus-entrypoint draft test.
- `tests/unit/test_cli.py:684` covers a simple single-entrypoint validation target draft command.
  There is no CLI-level assertion for the mixed controller target.

## Probe Results

Command:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-controller-chat-question
```

Observed result:

```text
- rcv-controller-chat-question [P0] Controller queued Chat question
  entrypoints: ringcentral.video.toolbar.chat
  flows: meeting-control-map-demo
  ...
  draft: ai-presenter acceptance-draft --package ringcentral-video --checklist-target "P0 Controller queued Chat question"
```

Command:

```powershell
.\.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat --checklist-target "P0 Controller queued Chat question"
```

Observed result: the command already renders both Flow Context and Entrypoint Context, and it exits
successfully. The only guidance gap is the generated command and the `Steps executed` prefill, which
currently says only `Intended target: ringcentral.video.toolbar.chat`.

Focused tests run during scan:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command --no-cov
```

Result:

```text
21 passed in 5.77s
```

## Recommended Slice

Add an unambiguous mixed-target draft path.

Implementation shape:

1. Update `acceptance_draft_command()` in `src/ai_presenter/acceptance/validation_targets.py`.
   - Keep current single-entrypoint and single-flow behavior.
   - Add a branch for `len(target.flow_ids) == 1 and len(target.entrypoint_ids) == 1`.
   - Emit both `--flow <flow_id>` and `--entrypoint <entrypoint_id>` before
     `--checklist-target`.
   - Keep checklist-only fallback for group targets with multiple flows or multiple entrypoints.

2. Update mixed draft wording in `src/ai_presenter/acceptance/manual_record.py`.
   - Change `_intended_steps()` so a request with both flow and entrypoint pre-fills a combined
     sentence, for example:

```text
Intended flow: meeting-control-map-demo; intended target during flow: ringcentral.video.toolbar.chat; fill with actual steps after the run.
```

   - Keep flow-only, entrypoint-only, and checklist-only wording unchanged.

3. Optional but useful guard: add a pure validation-target test that exercises the real
   `rcv-controller-chat-question` row and proves the generated command can be passed directly to
   `acceptance-draft` semantics by containing both IDs. Avoid adding shell parsing in production
   code; a string assertion is enough for this slice.

## Files To Touch

- `src/ai_presenter/acceptance/validation_targets.py`
  - Modify `acceptance_draft_command()`.
- `src/ai_presenter/acceptance/manual_record.py`
  - Modify `_intended_steps()` only.
- `tests/unit/test_validation_targets.py`
  - Add `test_acceptance_draft_command_includes_flow_and_entrypoint_for_single_mixed_target`.
  - Existing `test_acceptance_draft_command_omits_entrypoint_for_group_target` should continue to
    prove multi-entrypoint group targets stay checklist-only.
- `tests/unit/test_acceptance_manual_record.py`
  - Add `test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps`.
- `tests/unit/test_cli.py`
  - Add a focused CLI regression for
    `validation-targets --package ringcentral-video --target rcv-controller-chat-question`, asserting
    the draft command includes both `--flow meeting-control-map-demo` and
    `--entrypoint ringcentral.video.toolbar.chat`.

No RingCentral knowledge docs need to change for the minimum slice. The checklist already carries the
right stable target ID and references both package IDs.

## Acceptance Criteria

- `validation-targets --package ringcentral-video --target rcv-controller-chat-question` prints a
  draft command containing both `--flow meeting-control-map-demo` and
  `--entrypoint ringcentral.video.toolbar.chat`.
- The same output still includes `--checklist-target "P0 Controller queued Chat question"`.
- `rcv-top-bar-routes` and other grouped targets with multiple entrypoints still omit
  `--entrypoint` and `--flow` in the generated draft command.
- `acceptance-draft --flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat`
  pre-fills a mixed intended-steps sentence that mentions both the flow and target.
- Existing validation remains offline and read-only. No evidence file is written and no live
  RingCentral route is executed.

## Risks

- If future checklist rows combine one flow and one entrypoint that are not actually related, the
  generated command will fail at `acceptance-draft` time because `manual_record.py` validates flow
  membership. This is acceptable for a small slice, but a later hardening pass could validate
  single-flow/single-entrypoint membership during target discovery.
- Do not apply the combined command to multi-entrypoint groups. Group targets intentionally avoid
  implying that one entrypoint was validated.
- Do not change `AcceptanceDraftRequest` fields or CLI option names. Existing runbooks and tests
  already depend on those stable flags.

## Comparison With Other Candidate Slices

### Controller UI summary rows

Still valuable, but broader. It touches Tk rendering and operator layout, and Cycle 020 already added
pure view-model summaries plus disabled-action reasons. Splitting the dense summary into rows would
improve scanability, but it is a UI polish pass rather than a direct unblocker for RingCentral
acceptance planning.

### Q&A matcher performance index

Also useful, but lower urgency. Cycle 008 already added immutable entrypoint and question-alias
indexes, so the current hot path is not as wasteful as the original scan. A deeper matcher cache
would need careful precedence tests for package Q&A, localized Q&A, package aliases, legacy aliases,
and token scoring. The mixed draft slice is smaller and directly follows the Cycle 029 residual risk.

## Verification Commands

Focused RED/GREEN:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py::test_acceptance_draft_command_includes_flow_and_entrypoint_for_single_mixed_target --no-cov
.\.venv\Scripts\python -m pytest tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps --no-cov
.\.venv\Scripts\python -m pytest tests\unit\test_cli.py::test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command --no-cov
```

Affected test set:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command --no-cov
```

Manual CLI smoke:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-controller-chat-question
.\.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat --checklist-target "P0 Controller queued Chat question"
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-top-bar-routes
```

Static checks:

```powershell
.\.venv\Scripts\python -m ruff check src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\acceptance\manual_record.py tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
.\.venv\Scripts\python -m mypy src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\acceptance\manual_record.py tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
git diff --check
```

Full verification before closing an implementation cycle:

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src tests
.\.venv\Scripts\python -m ruff check src tests
```

## Commands Run During This Scan

```powershell
Get-Content -Raw docs\agent-handoffs\cycle-029-demand-analysis.md
Get-Content -Raw docs\agent-handoffs\cycle-029-technical-scan.md
Get-Content -Raw docs\agent-handoffs\cycle-029-review.md
rg -n "validation-target|acceptance-draft|Acceptance|Target ID|include-blocked|mixed|entrypoint|checklist" src tests docs packages -g "!*.pyc"
Get-Content -Raw src\ai_presenter\acceptance\validation_targets.py
Get-Content -Raw src\ai_presenter\acceptance\manual_record.py
Get-Content -Raw tests\unit\test_validation_targets.py
Get-Content -Raw tests\unit\test_acceptance_manual_record.py
Get-Content -Raw docs\knowledge\ringcentral-video\validation-checklist-index.md
Get-Content -Raw docs\knowledge\ringcentral-video\evidence-index.md
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-controller-chat-question
.\.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat --checklist-target "P0 Controller queued Chat question"
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command --no-cov
```
