# Cycle 146 Demand Analysis: validation-targets Source Traceability Guard

Date: 2026-05-17
Cycle: 146
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## User Value

The user value is source traceability without evidence overclaiming.
`validation-targets` should keep helping an operator choose the next manual
RingCentral Video validation target, while making it obvious which repo docs
the planning list came from.

The output should continue to show both source paths:

- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`

Those paths matter because an operator can trace the checklist target, evidence
level, and main gap back to the material package docs instead of treating CLI
text as an unexplained result. The boundary from Cycle 145 still applies:
source traceability is not live acceptance evidence. The CLI lists a
repo-derived planning view; it does not run RingCentral, record a dated
acceptance run, or prove that any route is currently accepted.

## Recommended Minimum Scope

Keep this cycle as a narrow output-contract guard. The production renderer
already emits a shared header with `Package:`, `Checklist:`, `Evidence:`, and
the non-evidence note. The likely implementation is test-only.

Recommended implementation:

- In `tests/unit/test_cli.py`, strengthen the successful
  `validation-targets` list test so it asserts both
  `validation-checklist-index.md` and `evidence-index.md` are present.
- In `tests/unit/test_cli.py`, strengthen at least one successful detail path,
  preferably `test_validation_targets_detail_outputs_draft_command`, so detail
  output also must include both source paths and the Cycle 145 non-evidence
  note.
- In `tests/unit/test_validation_targets.py`, strengthen renderer coverage so
  `render_validation_target_lines(...)` directly guards the shared header paths
  for normal output.
- Preserve the existing target detail, evidence level, validate, cleanup,
  privacy, blocked, and draft command assertions.
- Treat `src/ai_presenter/acceptance/validation_targets.py` as already
  satisfying the feature unless a focused test shows a missing header path.

The minimum useful behavior is: every successful list/detail rendering remains
traceable to the checklist and evidence index, while still saying it is only a
repo-derived planning list.

## Out Of Scope

Do not turn this into live acceptance, package behavior, or runtime work.

Do not touch:

- `packages/ringcentral-video.yaml`
- `profiles/*.yaml`
- runtime, controller, route, question matching, localization, voice, or UIA
  behavior
- RingCentral acceptance run records
- live/manual acceptance evidence levels
- package docs content unless a separate task explicitly asks for it
- `package` metadata, dependency files, or lockfiles
- `.coverage`

Do not add or imply:

- a new live RingCentral acceptance claim
- a new dated acceptance run
- a promotion from `Repo-tested` or `Observed` to `Accepted`
- wording that checklist or evidence source paths are themselves acceptance
  proof
- wording that `acceptance-draft` is acceptance evidence
- broad renderer refactors unrelated to source path traceability

If implementation seems to require source behavior changes, first confirm the
failure is a real missing output path rather than a missing assertion. If the
current renderer already prints the path, prefer tests only.

## Acceptance Criteria

Implementation should be accepted when:

- `validation-targets --package ringcentral-video --priority P0` output still
  includes the target planning list and visibly includes both
  `validation-checklist-index.md` and `evidence-index.md`.
- `validation-targets --package ringcentral-video --target
  rcv-add-coworkers-modal` output still includes target detail and the
  `acceptance-draft` command, while also visibly including both source paths.
- Renderer-level coverage directly guards the shared `Checklist:` and
  `Evidence:` header lines, so CLI list/detail paths inherit the same contract.
- The output continues to include
  `repo-derived planning list only; not live acceptance evidence`.
- No live acceptance record is added or modified.
- No package YAML, profile, runtime behavior, dependency metadata, tests outside
  the narrow guard, or generated coverage artifact is changed unless a focused
  failure proves it is necessary.
- Focused tests pass for the touched CLI and renderer checks.
- Whitespace verification passes for this handoff and any implementation diff.

Suggested focused verification for the implementation subtask:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
git diff --check -- tests\unit\test_cli.py tests\unit\test_validation_targets.py
git status --short
```

Manual smoke is optional for a test-only change, but the expected visible
header shape is:

```text
Package: ringcentral-video
Checklist: docs/knowledge/ringcentral-video/validation-checklist-index.md
Evidence: docs/knowledge/ringcentral-video/evidence-index.md
Note: repo-derived planning list only; not live acceptance evidence.
```

## Handoff Prompt For Implementation Subtask

Cycle146 implementation subtask. You are not the only agent in this repo. Keep
the change narrow, do not revert other work, and do not stage or revert
`.coverage`.

Repository:
`C:\Users\rcadmin\Documents\Repos\AiPresenter`

Goal:
Guard `validation-targets` source traceability so successful CLI list/detail
output continues to show the checklist and evidence source paths:
`validation-checklist-index.md` and `evidence-index.md`. This is for operator
traceability back to the planning docs, not for live acceptance evidence.

Read first:

- `docs/agent-handoffs/cycle-146-demand-analysis.md`
- `docs/agent-handoffs/cycle-145-experience.md`
- `docs/agent-handoffs/cycle-145-review.md`
- `src/ai_presenter/acceptance/validation_targets.py`
- `tests/unit/test_cli.py` around `validation-targets`
- `tests/unit/test_validation_targets.py` around
  `render_validation_target_lines`

Recommended implementation:

- Add or strengthen assertions in
  `test_validation_targets_lists_ringcentral_targets` so list output contains
  both `validation-checklist-index.md` and `evidence-index.md`.
- Add or strengthen assertions in
  `test_validation_targets_detail_outputs_draft_command` so detail output
  contains both source paths plus the existing non-evidence note.
- Add renderer-level assertions in
  `test_render_validation_target_lines_keeps_normal_draft_command` for the
  shared `Checklist:` and `Evidence:` header lines.
- Keep existing assertions for target ids, entrypoints, draft command wording,
  and the non-evidence note.
- Do not change source unless a focused failing test proves a required source
  path is genuinely absent from output.
- Do not create or update acceptance runs.
- Do not add live acceptance wording.
- Do not touch package YAML, profiles, runtime behavior, dependency metadata,
  or `.coverage`.

Verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
git diff --check -- tests\unit\test_cli.py tests\unit\test_validation_targets.py
git status --short
```

Success means list/detail and renderer output are guarded for checklist and
evidence source traceability, while the diff still makes no live acceptance
claim and contains no unrelated file edits.
