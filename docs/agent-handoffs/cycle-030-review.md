# Cycle 030 Review: Mixed Validation Draft Guidance

Date: 2026-05-16
Role: review
Scope: Review-only for code and docs; this handoff is the only file written during review.

## Findings

No blocker findings.

The implementation satisfies the requested behavior:

- `acceptance_draft_command()` keeps single-entrypoint and single-flow behavior unchanged, adds `--flow` then `--entrypoint` for exactly one flow plus exactly one entrypoint, and falls back to checklist-only for grouped targets.
- The mixed `acceptance-draft` template pre-fills `Steps executed` with both `meeting-control-map-demo` and `ringcentral.video.toolbar.chat`.
- The reviewed paths are offline/read-only. I did not run live RingCentral automation or write acceptance evidence.

## Residual Risks

- There is no explicit synthetic unit test for a multi-flow group target. The code path falls through to checklist-only unless there is exactly one flow and exactly one entrypoint, and the real `rcv-top-bar-routes` multi-entrypoint target is covered, but a dedicated multi-flow fixture would make that acceptance criterion more direct.
- `acceptance_draft_command()` still uses simple double-quote wrapping for `--checklist-target`. Current checklist labels are safe and tested, but a future label containing embedded quotes or shell metacharacters would need stronger escaping.
- The broader worktree has untracked `docs/knowledge/ringcentral-video/*` evidence/checklist files, so Git cannot attribute those files to this cycle from diff alone. I found no Cycle 030 evidence promotion or acceptance-run append in the reviewed Cycle 030 docs or command outputs.

## Review Notes

- Command ordering is correct for the mixed target:
  `ai-presenter acceptance-draft --package ringcentral-video --flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat --checklist-target "P0 Controller queued Chat question"`.
- Group fallback is preserved for `rcv-top-bar-routes`; its rendered draft command includes only `--package` and `--checklist-target`.
- Manual draft wording remains draft-only and does not claim acceptance evidence. Pass/fail, evidence files, failures, recovery, and locator updates remain blank.

## Commands And Results

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command --no-cov
```

Result: `24 passed in 13.00s`.

```powershell
.\.venv\Scripts\python -m ruff check src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\acceptance\manual_record.py tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
```

Result: `All checks passed!`

```powershell
.\.venv\Scripts\python -m mypy src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\acceptance\manual_record.py tests\unit\test_validation_targets.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
```

Result: `Success: no issues found in 5 source files`.

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-controller-chat-question
```

Result: rendered the mixed P0 target with `flows: meeting-control-map-demo`, `entrypoints: ringcentral.video.toolbar.chat`, and the mixed draft command containing `--flow`, `--entrypoint`, and `--checklist-target`.

```powershell
.\.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --flow meeting-control-map-demo --entrypoint ringcentral.video.toolbar.chat --checklist-target "P0 Controller queued Chat question"
```

Result: rendered Flow Context, Entrypoint Context, Checklist Context, `Package flow: meeting-control-map-demo`, and `Steps executed: Intended flow: meeting-control-map-demo; intended target during flow: ringcentral.video.toolbar.chat; fill with actual steps after the run.`

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-top-bar-routes
```

Result: rendered a checklist-only draft command for the multi-entrypoint top-bar group.

```powershell
rg -n "Cycle 030|rcv-controller-chat-question|Controller queued Chat question|Pass/fail:|Evidence Level|Accepted|P0 Controller" docs\knowledge\ringcentral-video\acceptance-runs.md docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\validation-checklist-index.md
```

Result: showed the target remains `Unit-tested, not manually accepted`; no Cycle 030 acceptance evidence append or promotion was found.
