# Cycle 150 Technical Scan: Validation Targets Evidence None Fallback

Date: 2026-05-17
Cycle: 150
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

This scan reviews the `validation-targets` catalog and renderer behavior when
no evidence file content/path is supplied.

No source, test, package, or `.coverage` files were modified for this scan. The
recommended follow-up is test-only and should not require changes to
`src/ai_presenter/acceptance/validation_targets.py`.

Read inputs:

- `tests/unit/test_validation_targets.py`
- `src/ai_presenter/acceptance/validation_targets.py`
- `docs/agent-handoffs/cycle-149-technical-scan.md`
- `docs/agent-handoffs/cycle-149-experience.md`

## Existing Coverage

`tests/unit/test_validation_targets.py` already covers normal catalog discovery
with a real checklist and real evidence index:

- `test_discover_validation_targets_reads_priority_checklist_rows` proves
  checklist rows become targets and evidence levels are attached from the
  evidence index.
- `test_discover_validation_targets_has_no_unknown_evidence_for_real_catalog`
  proves the real catalog has no `unknown` evidence levels when the evidence
  index is supplied.
- `test_render_validation_target_lines_keeps_normal_draft_command` proves the
  renderer includes the checklist path, concrete evidence path, non-evidence
  note, draft label, and single-entrypoint draft command.
- `test_render_validation_target_lines_suppresses_blocked_draft_command` proves
  blocked rows render refusal details without draft commands.
- `test_discover_validation_targets_can_include_blocked_rows` proves blocked
  checklist rows can still be included when requested.

The implementation already has a fallback path:

- `discover_validation_targets(...)` skips evidence-index validation and uses
  empty evidence maps when `evidence_text` is `None`, empty, or whitespace.
- `ValidationTargetCatalog.evidence_path` is `Path | None`.
- `render_validation_target_lines(...)` renders
  `Evidence: none` when `catalog.evidence_path` is `None`.
- `_NON_EVIDENCE_NOTE` renders immediately after the evidence line:
  `repo-derived planning list only; not live acceptance evidence.`
- `_evidence_for(...)` assigns `unknown` per entrypoint when no evidence level
  exists.

## Gap

There is no test that constructs a catalog without `evidence_text` and
`evidence_path`.

The nearest renderer test,
`test_render_validation_target_lines_keeps_normal_draft_command`, only covers
the concrete evidence file path case:

- `Evidence: docs/knowledge/ringcentral-video/evidence-index.md`
- non-evidence note
- target block and draft command

Because the no-evidence path is untested, a regression could remove
`Evidence: none`, drop the non-evidence note, or accidentally stop rendering
checklist-derived target rows when evidence is unavailable.

## Recommended Minimal Test-Only Change

Add one focused test to `tests/unit/test_validation_targets.py`.

Recommended test name:

```python
def test_render_validation_target_lines_marks_missing_evidence_without_dropping_targets() -> None:
```

Recommended test body shape:

```python
catalog = discover_validation_targets(
    load_ringcentral_package(),
    checklist_text=load_checklist_text(),
    checklist_path=Path("docs/knowledge/ringcentral-video/validation-checklist-index.md"),
    evidence_text=None,
    evidence_path=None,
)

text = "\n".join(
    render_validation_target_lines(catalog, target_id="rcv-add-coworkers-modal")
)

assert "Evidence: none" in text
assert "repo-derived planning list only; not live acceptance evidence" in text
assert "- rcv-add-coworkers-modal [P0] Add coworkers modal" in text
assert "entrypoints: ringcentral.video.main.add-coworkers" in text
assert "evidence: ringcentral.video.main.add-coworkers=unknown" in text
assert "draft:" in text
```

This is intentionally one new test rather than a helper or broad parameterized
matrix. It covers the user-visible fallback contract directly:

- renderer says there is no evidence file;
- renderer still prints the non-evidence note;
- checklist target rows still render;
- missing evidence levels remain explicit as `unknown`.

## Assertion Notes

Keep assertions narrow and user-facing.

Required assertions:

- `Evidence: none`
- `repo-derived planning list only; not live acceptance evidence`
- `- rcv-add-coworkers-modal [P0] Add coworkers modal`
- `entrypoints: ringcentral.video.main.add-coworkers`
- `evidence: ringcentral.video.main.add-coworkers=unknown`

Useful optional assertion:

- `draft:` remains present for a normal, unblocked target, proving the renderer
  still emits the full target block from the checklist.

Avoid asserting on every field in the block. Existing tests already cover
`current`, `validate`, cleanup, privacy, and draft command content for the
normal evidence-path case.

## TDD Red-Light Method

Use a temporary source-local break only to prove the new test fails, then
restore it exactly.

Suggested red-light options:

1. Add the new test.
2. Temporarily change the renderer evidence line in
   `src/ai_presenter/acceptance/validation_targets.py` from fallback `none` to
   another word, such as `missing`.
3. Run the focused test and confirm it fails on `Evidence: none`.
4. Restore `src/ai_presenter/acceptance/validation_targets.py` exactly.
5. Re-run the focused test and confirm it passes.
6. Confirm there is no source diff:

```powershell
git diff -- src\ai_presenter\acceptance\validation_targets.py
```

An alternate red light is to temporarily remove the non-evidence note from
`render_validation_target_lines(...)`, then restore it. Do not red-light by
editing package YAML, checklist docs, evidence docs, or production parsing
behavior permanently.

## Need To Modify Src?

No.

The current implementation already supports the desired behavior:

- absent evidence text/path is accepted;
- evidence-path display falls back to `none`;
- non-evidence note always renders;
- checklist-derived targets still render;
- per-entrypoint evidence displays as `unknown`.

The gap is coverage, not production behavior.

## Validation Commands

For this handoff document:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-150-technical-scan.md
git diff --check -- docs\agent-handoffs\cycle-150-technical-scan.md
```

For the later test-only implementation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_validation_targets.py -k "missing_evidence or render_validation_target_lines"
git diff --check -- tests\unit\test_validation_targets.py
git diff -- src\ai_presenter\acceptance\validation_targets.py
```

Expected implementation footprint:

- Modify only `tests/unit/test_validation_targets.py`.
- Leave `src/ai_presenter/acceptance/validation_targets.py` with no final diff.
- Do not modify package files, checklist/evidence docs, `.coverage`, or
  unrelated work from other agents.
