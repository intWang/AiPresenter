# Cycle 150 Experience: Validation Targets Evidence None Fallback

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Theme And User Value

Cycle 150 tightened the `validation-targets` no-evidence rendering boundary.
The operator value is clarity under missing traceability: a catalog can still
render checklist-derived planning rows when no evidence file is attached, but
the header must say `Evidence: none` and the note must keep saying
`repo-derived planning list only; not live acceptance evidence.`

This protects against a subtle confidence leak. Missing evidence input should
not look like a loaded evidence index, and it should not look like live
RingCentral acceptance. It is only a source-availability state for a planning
surface.

## Subagent Handoff Flow

Demand analysis framed the expected user-visible behavior and kept the cycle
narrow: prefer a test-only change, and only touch production code if a failing
test proved the renderer/catalog normalized absent evidence incorrectly.

Technical scan found the implementation already supported the desired fallback:
no evidence text leads to empty evidence maps, no evidence path renders as
`Evidence: none`, the non-evidence note remains present, and per-entrypoint
evidence falls back to `unknown`. The gap was coverage, not source behavior.

Risk scan supplied the wording guardrails. It separated catalog-level source
traceability from acceptance proof and warned against treating `none` or
`unknown` as a successful evidence state.

Implementation added one focused unit test for the missing-evidence renderer
case. It used a temporary TDD red-light change in production to prove the test
failed, then restored production code and confirmed the final diff had no
`src` change.

Review found no issues. The final implementation diff was test-only plus
handoff documentation, with `.coverage` already dirty but untouched.

## Experience Rules

- `Evidence: none` is traceability absence, not proof. It says no evidence
  source path is attached to the rendered catalog; it does not mean accepted,
  observed, safe, complete, or ready to execute.
- Checklist rows can still render without an evidence path. The output remains
  useful as a repo-derived planning list, but per-entrypoint evidence should be
  `unknown` unless a real evidence index was parsed.
- Pair no-evidence assertions with the boundary note. Tests that assert
  `Evidence: none` should also keep
  `repo-derived planning list only; not live acceptance evidence` visible.
- Do not weaken evidence-index integrity checks. Real evidence text should
  still reject missing, unknown, duplicate, unbackticked, or invalid rows.
- If TDD temporarily breaks production, restore it exactly and verify there is
  no final `src` diff before claiming completion.
- Avoid broad negative assertions around words like `evidence`, `unknown`, or
  `draft`; they can accidentally remove useful safety language.
- Keep `.coverage` out of the work. It may be dirty from local test runs, but
  this cycle must not stage or normalize it.

## Next Cycle Suggestions

The next narrow follow-up could add a CLI-level smoke for a custom checklist
rendered without an evidence path. That would prove the no-evidence contract
from the command surface, not only the unit-level renderer surface.

Alternatively, return to the language and tone expansion track now that the
evidence-boundary chain has a demand analysis, technical scan, risk scan,
implementation note, review, and experience record.

## Verification And Submission Notes

Before a submission or PR, run the broader verification set rather than relying
only on the focused Cycle 150 checks:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q
.\.venv\Scripts\ruff.exe check --no-cache .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --check
git diff -- src\ai_presenter\acceptance\validation_targets.py
git status --short
```

Submission hygiene:

- Do not stage `.coverage`.
- Confirm `src\ai_presenter\acceptance\validation_targets.py` has no diff if
  the cycle remains test-only.
- Keep live RingCentral evidence files and `acceptance-runs.md` out of scope
  unless a future task explicitly asks for live acceptance work.
- If only Cycle 150 handoff docs are being submitted, verify each doc with
  `rg -n "[ \t]+$"` and `git diff --check -- <path>` before staging.
