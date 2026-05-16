# Cycle 145 Demand Analysis: validation-targets CLI Output Boundary

Date: 2026-05-17
Cycle: 145
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## User Value

The user value is to make RingCentral Video planning output harder to misread.
`validation-targets` and the adjacent `acceptance-draft` workflow help an
operator choose the next manual validation target, but they must not sound like
live RingCentral acceptance evidence.

The important distinction is:

- `validation-targets` output is a repo-derived planning list built from
  `validation-checklist-index.md` and `evidence-index.md`.
- `acceptance-draft` output is a draft/template for a future manual record.
- Neither command performs a live RingCentral action, records an acceptance
  run, or proves that RingCentral accepted a route in the current build.

This matters because the RingCentral Video docs already separate
`Repo-tested`, `Observed`, and `Accepted`. If CLI output drops that boundary,
future agents or operators may incorrectly promote automated tests, dry runs,
read-only UIA observations, checklists, or draft text into live acceptance
claims.

## Recommended Minimum Scope

Keep the implementation slice narrow: strengthen output/contract coverage
around existing wording, without changing runtime behavior.

Recommended implementation:

- In `tests/unit/test_cli.py`, add assertions near the existing
  `validation-targets` tests that successful list and detail output contains
  `repo-derived planning list only; not live acceptance evidence`.
- If acceptance-draft coverage needs a nearby sentinel, use existing
  acceptance-draft tests and assert the already-established draft boundary
  phrases rather than inventing new acceptance wording.
- Prefer test-only changes unless a test shows the boundary note is missing
  from an output path that should already render it.
- Treat `src/ai_presenter/acceptance/validation_targets.py` as already having
  the desired CLI note; only change it if an existing command path truly omits
  the note.

The highest-value check is that both priority listing and single-target detail
views visibly carry the non-evidence note while still showing the useful
planning details and draft command.

## Out Of Scope

Do not broaden this cycle into live acceptance or package behavior changes.

Do not touch:

- `packages/ringcentral-video.yaml`
- `profiles/*.yaml`
- runtime, controller, question matching, voice, localization, or route behavior
- RingCentral acceptance run records
- live/manual acceptance evidence levels
- `.coverage`

Do not add or imply:

- any new live RingCentral acceptance claim
- any new dated acceptance run
- any statement that `validation-targets` proves a route is accepted
- any statement that `acceptance-draft` is acceptance evidence
- any promotion from `Repo-tested` or `Observed` to `Accepted`
- any claim that automated tests, dry runs, `doctor`, CLI inspection, or
  read-only UIA observation prove live acceptance

If implementation appears to require package YAML, profile, runtime, or source
behavior changes, pause and rescope. This demand is about preserving user-facing
CLI evidence boundaries, not changing RingCentral operation.

## Acceptance Criteria

Implementation should be accepted when:

- `validation-targets --package ringcentral-video --priority P0` output is
  still useful as a planning list and includes the non-evidence note.
- `validation-targets --package ringcentral-video --target
  rcv-add-coworkers-modal` output still includes the target details and
  `acceptance-draft` command, while also including the non-evidence note.
- Existing `acceptance-draft` output remains clearly draft-only and does not
  claim live acceptance.
- No live acceptance record is added or modified.
- No package YAML, profile, runtime behavior, or generated coverage artifact is
  changed.
- Focused tests pass for the touched CLI boundary checks.
- `git diff --check` reports no whitespace errors for touched files.

Suggested focused verification for the implementation subtask:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template
git diff --check -- tests\unit\test_cli.py
git status --short
```

Manual smoke is optional if only tests change, but useful if wording behavior is
edited:

```powershell
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --target rcv-add-coworkers-modal
```

Expected smoke trait: each `validation-targets` output includes
`Note: repo-derived planning list only; not live acceptance evidence.`

## Handoff Prompt For Implementation Subtask

Cycle145 implementation subtask. You are not the only agent in this repo. Keep
the change narrow and do not modify package YAML, profiles, runtime behavior, or
`.coverage`.

Repository:
`C:\Users\rcadmin\Documents\Repos\AiPresenter`

Goal:
Guard the RingCentral Video `validation-targets` CLI output boundary so future
changes cannot make the command look like live RingCentral acceptance evidence.
The command should remain a repo-derived planning list, and any
`acceptance-draft` command it prints should remain a draft helper, not proof.

Read first:

- `docs/agent-handoffs/cycle-145-demand-analysis.md`
- `docs/agent-handoffs/cycle-144-experience.md`
- `docs/agent-handoffs/cycle-144-technical-scan.md`
- `tests/unit/test_cli.py` around `validation-targets` and
  `acceptance-draft`
- `src/ai_presenter/acceptance/validation_targets.py`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`

Recommended implementation:

- Add assertions to the existing successful `validation-targets` CLI tests so
  list and detail outputs must contain
  `repo-derived planning list only; not live acceptance evidence`.
- Preserve the existing target details and `acceptance-draft` command
  assertions.
- Do not create or update any acceptance run.
- Do not add live acceptance wording.
- Do not change package YAML, profiles, runtime behavior, or source unless a
  focused test proves the existing note is missing from a required output path.
- Leave pre-existing `.coverage` dirty state alone.

Verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template
git diff --check -- tests\unit\test_cli.py
git status --short
```

Success means the CLI boundary is guarded by tests and the diff contains no
live acceptance claim, no acceptance run, and no unrelated file edits.
