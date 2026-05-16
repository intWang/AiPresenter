# Cycle 145 Implementation: Validation Targets Non-Evidence Note Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Implemented a narrow test-only guard for the `validation-targets` CLI and
renderer boundary. The command can list targets, show target detail, and print
`acceptance-draft` commands, but the output must remain a repo-derived planning
surface rather than live RingCentral acceptance evidence.

Touched files:

- `tests/unit/test_cli.py`
- `tests/unit/test_validation_targets.py`
- `docs/agent-handoffs/cycle-145-implementation.md`

No production behavior, package YAML, profiles, runtime/provider code, live
RingCentral evidence, or generated artifacts were intentionally changed.
`.coverage` was already dirty and was not touched intentionally.

## Changes

- Added `VALIDATION_TARGETS_NON_EVIDENCE_NOTE` in `tests/unit/test_cli.py` so
  validation-target tests share the exact CLI boundary phrase.
- Guarded the note across four CLI output shapes:
  - priority listing;
  - entrypoint detail with draft command;
  - mixed flow plus entrypoint detail with draft command;
  - blocked target detail without draft command.
- Added renderer-level coverage in `tests/unit/test_validation_targets.py` so
  `render_validation_target_lines` keeps the planning-only note even outside
  the Typer CLI wrapper.

## Red/Green Verification

Red check:

1. Added the CLI assertions.
2. Temporarily changed
   `src/ai_presenter/acceptance/validation_targets.py` from
   `repo-derived planning list only; not live acceptance evidence.` to
   `repo-derived planning list.`
3. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command tests\unit\test_cli.py::test_validation_targets_blocked_target_omits_draft_command
```

Result: `4 failed`, each failing on the missing non-evidence note.

Green check:

1. Restored the production note.
2. Added the renderer-level assertion.
3. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command tests\unit\test_cli.py::test_validation_targets_blocked_target_omits_draft_command tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
```

Result: `5 passed`.

## Boundaries

- `validation-targets` output remains a planning aid.
- `acceptance-draft` commands remain draft helpers, not acceptance records.
- A live RingCentral route or flow still requires a dated entry in
  `docs/knowledge/ringcentral-video/acceptance-runs.md`.
- No new runtime, provider, language, profile, package, or live acceptance claim
  was introduced.

## Follow-Up

The next small guard could check that validation-target output continues to
name the source checklist and evidence files, so future operators can trace the
planning list back to durable docs without treating it as proof.
