# Cycle 148 Experience: Renderer Draft Boundary Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Theme And User Value

Cycle 148 extends the `acceptance-draft` safety boundary from the CLI success
paths down to renderer-level unit tests. The user value is preventing direct
calls to `render_manual_acceptance_draft(...)` from drifting into output that
looks like live acceptance evidence.

The draft remains useful because it can prefill package, flow, entrypoint,
checklist, privacy reminders, proof-order reminders, and blank post-run fields.
It must still be unmistakably draft-only until a human performs the live
RingCentral workflow and fills the record after the run.

## Sub-Agent Handoff Notes

Demand analysis framed the task as test-only renderer protection, with flow-only
and mixed flow plus entrypoint drafts sharing the same boundary as the existing
entrypoint draft.

Technical scan confirmed production rendering already centralizes the required
boundary text, so the expected final change was test-only. It also suggested a
small local helper to avoid duplicated assertions.

Risk scan sharpened the main testing hazard: do not turn the renderer test into
a brittle vocabulary filter. The output is allowed to mention `acceptance`,
`not acceptance evidence`, `Pass/fail`, `Evidence files`, `Steps executed`, and
future-facing `acceptance-runs.md` instructions.

Implementation added `assert_manual_draft_boundary(...)` and wired it into the
entrypoint, flow-only, and mixed renderer success paths. The red check
temporarily broke `src/ai_presenter/acceptance/manual_record.py`, then restored
it.

Review found no issues. It confirmed the helper requires all three draft-only
anchors and avoids broad negative substring bans.

## Experience Rules

- Renderer and CLI must both preserve the same draft-only contract:
  `Draft only`, `not acceptance evidence`, and
  `No live RingCentral action has been performed by this helper.`
- Treat `acceptance-draft` as a template generator, not evidence generation.
  It may name fields a human must fill later, but it must not claim the run
  happened.
- Negative assertions must be precise. Block conclusion-style claims such as
  `Accepted` or `live validated`, but do not ban broad stems like `accept`,
  `pass`, `fail`, `evidence`, `valid`, or `observed`.
- Do not mistake required labels for outcomes. `Pass/fail` is a blank field,
  and `not acceptance evidence` is the required safety wording.
- If TDD red-light work temporarily edits `src`, immediately restore it and
  confirm there is no final `src` diff before handing off.
- Do not touch `acceptance-runs.md`, package YAML, runtime behavior, generated
  artifacts, or `.coverage` for this boundary task.
- If `.coverage` is dirty from local test runs, leave it alone and do not stage
  it.

## Next-Cycle Suggestions

The next narrow cycle can guard `acceptance-draft` refusal paths. Useful checks
would confirm rejected requests do not write output files, do not render manual
acceptance fields, and keep the wording clearly outside live evidence.

An alternative next cycle is a validation-targets evidence-none fallback guard:
when no runnable evidence target exists, the workflow should fail safely with
clear operator guidance instead of implying validation happened.

## Verification And Commit Notes

Before staging or committing the Cycle 148 implementation, run a full hygiene
pass:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider
.\.venv\Scripts\ruff.exe check --no-cache .
.\.venv\Scripts\mypy.exe .
git diff --check
git diff -- src\ai_presenter\acceptance\manual_record.py
git status --short
```

Only stage the intended test and handoff docs. Do not stage `.coverage`, and do
not revert unrelated work from other agents.

For this experience handoff itself, the required checks are:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-148-experience.md
git diff --check -- docs\agent-handoffs\cycle-148-experience.md
```
