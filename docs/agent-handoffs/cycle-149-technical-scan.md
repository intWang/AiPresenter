# Cycle 149 Technical Scan: CLI Acceptance Draft Refusal Paths

Date: 2026-05-17
Cycle: 149
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

This scan reviews only the CLI-level `acceptance-draft` refusal paths in
`tests/unit/test_cli.py` and the output writer boundary in
`src/ai_presenter/cli.py`.

No source, test, package, or `.coverage` files were modified for this scan.
The recommended implementation is test-only and should not require changes to
`src/ai_presenter/cli.py`.

Read inputs:

- `tests/unit/test_cli.py` acceptance-draft tests
- `src/ai_presenter/cli.py` `acceptance_draft(...)` and
  `_write_acceptance_draft_output(...)`
- `docs/agent-handoffs/cycle-148-technical-scan.md`
- `docs/agent-handoffs/cycle-148-experience.md`

## Existing Coverage

`tests/unit/test_cli.py` already has a CLI helper,
`assert_acceptance_draft_boundary(text)`, for successful draft output. It
requires the draft-only anchors:

- `Draft only`
- `not acceptance evidence`
- `No live RingCentral action has been performed by this helper.`

It also blocks conclusion-like success wording in successful draft bodies:

- `accepted`
- `passed`
- `live validated`

The successful CLI paths currently covered are:

- `test_acceptance_draft_outputs_entrypoint_template`
- `test_acceptance_draft_outputs_flow_template`
- `test_acceptance_draft_can_write_to_output_file`

The existing refusal paths cover these behaviors:

- `test_acceptance_draft_rejects_no_open_step_entrypoint` checks a no-open-step
  entrypoint returns nonzero and does not print `Manual RingCentral Acceptance
  Draft` or `### Manual Acceptance Fields`.
- `test_acceptance_draft_refusal_does_not_write_output_file` checks a no-open-step
  entrypoint with `--output` returns nonzero and does not create the requested
  file.
- `test_acceptance_draft_requires_target` checks the no-target request fails.
- `test_acceptance_draft_rejects_missing_flow_with_available_flows` checks an
  unknown flow fails and lists available flows.
- `test_acceptance_draft_rejects_existing_output_file` checks an existing output
  file is not overwritten.
- `test_acceptance_draft_rejects_acceptance_runs_output_file` checks
  `acceptance-runs.md` is refused and not created.

`src/ai_presenter/cli.py` renders the draft before entering the writer branch.
The writer itself refuses `acceptance-runs.md`, refuses existing files, creates
parent directories only after those refusals, and writes only after both writer
guards pass. On a successful write, the CLI prints `Wrote acceptance draft:
{output}`.

## Gaps

The refusal tests do not consistently assert that rejected CLI output avoids
success and evidence wording. Only the direct no-open-step refusal currently
checks two rendered-template headings. The other refusal paths could regress by
printing partial draft content or writer success text while still returning a
nonzero exit.

The current `--output` no-open-step refusal proves the file is not created, but
does not prove stdout/stderr avoids draft headings, writer success text, or
evidence-sounding language.

The existing-output refusal proves file contents are preserved, but does not
assert that the refusal output avoids `Wrote acceptance draft`, manual template
headings, or success/evidence wording.

The `acceptance-runs.md` refusal proves the file is not created, but its error
message intentionally contains `acceptance-runs.md` and `completed evidence
manually`. A broad ban on all `evidence` wording would be too brittle. The
guard should target the exact success/evidence phrases requested for this cycle
instead of banning every evidence-related word.

## Recommended Minimal Test-Only Change

Add a second local helper in `tests/unit/test_cli.py` next to
`assert_acceptance_draft_boundary(...)`:

```python
def assert_acceptance_draft_refusal_boundary(output: str) -> None:
    assert "Manual RingCentral Acceptance Draft" not in output
    assert "Manual Acceptance Fields" not in output
    assert "Wrote acceptance draft" not in output
    lowered = output.casefold()
    assert "acceptance evidence" not in lowered
    assert "accepted" not in lowered
    assert "passed" not in lowered
    assert "live validated" not in lowered
```

Recommended use:

- In `test_acceptance_draft_rejects_no_open_step_entrypoint`, replace the two
  inline negative heading assertions with
  `assert_acceptance_draft_refusal_boundary(result.output)`.
- In `test_acceptance_draft_refusal_does_not_write_output_file`, add
  `assert_acceptance_draft_refusal_boundary(result.output)`.
- In `test_acceptance_draft_requires_target`, add
  `assert_acceptance_draft_refusal_boundary(result.output)`.
- In `test_acceptance_draft_rejects_missing_flow_with_available_flows`, add
  `assert_acceptance_draft_refusal_boundary(result.output)`.
- In `test_acceptance_draft_rejects_existing_output_file`, add
  `assert_acceptance_draft_refusal_boundary(result.output)` and keep the current
  file-content preservation assertion.
- In `test_acceptance_draft_rejects_acceptance_runs_output_file`, add
  `assert_acceptance_draft_refusal_boundary(result.output)` and keep the current
  non-creation assertion.

This keeps the implementation footprint to one helper plus calls from existing
tests. No new test functions are necessary.

## File Creation And Overwrite Assertions

Keep the existing file safety checks:

- `test_acceptance_draft_refusal_does_not_write_output_file` should continue to
  assert `not output_path.exists()`.
- `test_acceptance_draft_rejects_existing_output_file` should continue to assert
  the original file text remains exactly `existing draft`.
- `test_acceptance_draft_rejects_acceptance_runs_output_file` should continue to
  assert `not output_path.exists()`.

Do not add filesystem checks to no-target or missing-flow tests unless an
`--output` option is added to those invocations. The current smallest useful
change is to guard their refusal wording only.

## Assertion Notes

Use exact heading strings for manual-template leakage:

- `Manual RingCentral Acceptance Draft`
- `Manual Acceptance Fields`

Use exact writer success text:

- `Wrote acceptance draft`

Use the specific evidence phrase requested by this cycle:

- `acceptance evidence`

Avoid banning broad stems such as `accept`, `draft`, `evidence`, `manual`,
`pass`, `fail`, or `valid`. Those would conflict with legitimate refusal
guidance such as `Refusing to write acceptance draft to acceptance-runs.md` and
`append completed evidence manually`.

The recommended `accepted`, `passed`, and `live validated` checks mirror the
existing success-output helper and are narrow enough for current refusal
messages.

## Need To Modify Src?

No.

`src/ai_presenter/cli.py` already raises `BadParameter` before writer calls for
renderer refusals, and `_write_acceptance_draft_output(...)` already refuses
dangerous or existing outputs before `mkdir` and `write_text`. The current gap
is assertion breadth in `tests/unit/test_cli.py`, not production behavior.

Do not change `acceptance_draft(...)`, `_write_acceptance_draft_output(...)`,
package YAML, or renderer behavior for this cycle unless the later TDD run
discovers a real failing behavior.

## TDD Red-Light Method

Use temporary test-local or source-local breaks to prove the helper catches the
intended regressions, then restore them exactly:

1. Add `assert_acceptance_draft_refusal_boundary(...)` and wire it into the
   refusal tests listed above.
2. Temporarily inject a forbidden phrase into one refusal path. The least noisy
   options are:
   - add `typer.echo("Wrote acceptance draft: bogus.md")` before the
     `acceptance-runs.md` `BadParameter`, or
   - temporarily include `Manual Acceptance Fields` in one CLI refusal message.
3. Run the focused CLI tests and confirm the new helper fails.
4. Restore `src/ai_presenter/cli.py` exactly, or remove the temporary test-local
   break.
5. Confirm no source diff remains:

```powershell
git diff -- src\ai_presenter\cli.py
```

6. Re-run the focused CLI tests and confirm they pass.

Do not create the red light by writing to `acceptance-runs.md`, changing package
YAML, modifying renderer tests, or weakening the output writer guards.

## Validation Commands

For this handoff document:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-149-technical-scan.md
git diff --check -- docs\agent-handoffs\cycle-149-technical-scan.md
```

For the later test-only implementation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_cli.py -k "acceptance_draft"
git diff --check -- tests\unit\test_cli.py
git diff -- src\ai_presenter\cli.py
```

Expected implementation footprint:

- Modify only `tests/unit/test_cli.py`.
- Leave `src/ai_presenter/cli.py` with no final diff.
- Do not modify package files, `.coverage`, or unrelated work from other
  agents.
