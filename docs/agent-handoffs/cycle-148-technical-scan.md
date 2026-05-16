# Cycle 148 Technical Scan: Renderer-Level Acceptance Draft Boundary

Date: 2026-05-17
Cycle: 148
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

This scan only reviews the renderer-level acceptance draft boundary in
`tests/unit/test_acceptance_manual_record.py` and
`src/ai_presenter/acceptance/manual_record.py`.

No source, test, package, or `.coverage` files were modified for this scan.
The recommended implementation is test-only and should not require changes to
`src/ai_presenter/acceptance/manual_record.py`.

Read inputs:

- `tests/unit/test_acceptance_manual_record.py`
- `src/ai_presenter/acceptance/manual_record.py`
- `docs/agent-handoffs/cycle-147-technical-scan.md`
- `docs/agent-handoffs/cycle-147-experience.md`

## Existing Coverage

`render_manual_acceptance_draft(...)` currently emits the successful draft
boundary from one renderer:

- `Draft only`
- `not acceptance evidence`
- `No live RingCentral action has been performed by this helper.`
- `Proof-Order Reminder`
- blank `Pass/fail`, `Failures`, `Recovery`, `Evidence files`, and
  `Locator updates needed` fields until a real manual run fills them in

`test_manual_acceptance_draft_includes_all_required_template_fields` confirms
that every required manual acceptance field is rendered for a direct entrypoint
draft.

`test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance`
is the only current renderer-level success test that directly guards the
draft-only boundary. It asserts the direct entrypoint draft includes `Draft only`,
`not acceptance evidence`, `No live RingCentral action has been performed by this
helper.`, the expected entrypoint context, and `- Pass/fail:`. It also asserts
`Accepted` is absent.

`test_manual_acceptance_draft_prefills_flow_steps` confirms the flow-only
renderer path includes the flow id, flow title, and referenced entrypoints, but
does not currently assert the draft-only / not-evidence / no-live-action
boundary.

`test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps` confirms
the mixed flow + entrypoint + checklist renderer path includes all three context
sections and the intended-steps wording, but does not currently assert the same
boundary.

The negative renderer tests already cover unknown entrypoints, unknown flows,
entrypoints outside a selected flow, and direct no-open-step entrypoints. Those
are useful refusal guards, but they do not prove that successful renderer drafts
remain draft-only.

## Gaps

The current renderer-level boundary is pinned only through the direct entrypoint
success test. Because flow-only and mixed flow + entrypoint drafts are separate
success paths, future renderer edits could accidentally drop or soften the
boundary for those paths while leaving the entrypoint test green.

The repeated boundary assertions should not be copied inline into every test.
A small local helper will make the contract explicit and keep future renderer
paths aligned.

The existing `Accepted` negative assertion is narrow and case-sensitive. A
renderer-level helper can more clearly block conclusion-like wording that would
make a draft read as completed acceptance evidence.

## Recommended Minimal Test-Only Change

Add a local helper in `tests/unit/test_acceptance_manual_record.py` near
`load_ringcentral_package()`:

```python
def assert_manual_acceptance_draft_boundary(draft: str) -> None:
    assert "Draft only" in draft
    assert "not acceptance evidence" in draft
    assert "No live RingCentral action has been performed by this helper." in draft
    lowered = draft.casefold()
    assert "accepted" not in lowered
    assert "passed" not in lowered
    assert "live validated" not in lowered
```

Recommended use:

- In `test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance`,
  replace the three positive boundary assertions and the final `Accepted`
  assertion with `assert_manual_acceptance_draft_boundary(draft)`.
- In `test_manual_acceptance_draft_prefills_flow_steps`, add
  `assert_manual_acceptance_draft_boundary(draft)`.
- In `test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps`, add
  `assert_manual_acceptance_draft_boundary(draft)`.

This is the smallest renderer-level acceptance draft guard. It covers the direct
entrypoint, flow-only, and mixed renderer success paths without adding new test
functions or changing production behavior.

## Recommended Test Names And Assertions

No new test names are required if the existing tests are strengthened in place.
The existing names already describe the renderer paths being exercised:

- `test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance`
- `test_manual_acceptance_draft_prefills_flow_steps`
- `test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps`

If the implementer prefers separate tests, use these names:

- `test_manual_acceptance_entrypoint_draft_keeps_draft_only_boundary`
- `test_manual_acceptance_flow_draft_keeps_draft_only_boundary`
- `test_manual_acceptance_mixed_draft_keeps_draft_only_boundary`

However, separate tests are slightly larger than necessary because the renderer
paths are already built by the existing tests.

Important assertion notes:

- `accepted` does not match `acceptance`, so it is safe for the current draft
  template.
- `passed` does not match the existing `Pass/fail` field.
- Keep the negative wording focused. Do not ban broad stems such as `accept`,
  `pass`, or `valid`, because those would conflict with legitimate template
  language like `acceptance`, `Pass/fail`, and package validation context.

## Need To Modify Src?

No.

`src/ai_presenter/acceptance/manual_record.py` already centralizes successful
draft rendering and already emits the required boundary text for all successful
drafts. The current gap is test coverage breadth, not production behavior.

Do not add production constants or renderer branches for this cycle unless a
future implementation discovers a real failing behavior. The expected final
implementation should leave `src/ai_presenter/acceptance/manual_record.py`
unchanged.

## TDD Red-Light Method

Use a temporary renderer wording break to prove the new helper catches the
contract:

1. Add `assert_manual_acceptance_draft_boundary(...)` and wire it into the three
   renderer success paths listed above.
2. Temporarily edit `src/ai_presenter/acceptance/manual_record.py` in one small
   way, such as changing `not acceptance evidence` to `not final evidence`, or
   removing `No live RingCentral action has been performed by this helper.`.
3. Run the focused renderer test command below and confirm the new helper fails.
4. Restore `src/ai_presenter/acceptance/manual_record.py` exactly.
5. Confirm no source diff remains:

```powershell
git diff -- src\ai_presenter\acceptance\manual_record.py
```

6. Re-run the focused renderer test command and confirm it passes.

Do not create the red light by changing package YAML, writing to
`acceptance-runs.md`, exercising no-open-step refusal paths, or changing CLI
output behavior. Those paths test different boundaries.

## Validation Commands

For this handoff document:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-148-technical-scan.md
git diff --check -- docs\agent-handoffs\cycle-148-technical-scan.md
```

For the later test-only implementation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_acceptance_manual_record.py
git diff --check -- tests\unit\test_acceptance_manual_record.py
git diff -- src\ai_presenter\acceptance\manual_record.py
```

Expected implementation footprint:

- Modify only `tests/unit/test_acceptance_manual_record.py`.
- Leave `src/ai_presenter/acceptance/manual_record.py` with no final diff.
- Do not modify packages, `.coverage`, or unrelated files.
