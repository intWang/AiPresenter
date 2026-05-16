# Cycle 149 Demand Analysis: Acceptance Draft Refusal Paths

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## User Value

When `acceptance-draft` rejects a request, the CLI must fail without side
effects and without output that can be mistaken for a completed manual
acceptance record. Refusal paths such as no executable open step, existing
output file, and `acceptance-runs.md` output must not write files, must not
render `### Manual Acceptance Fields`, and must not print evidence-like success
phrasing.

This preserves the core safety boundary: `acceptance-draft` is only a draft
template helper. It must never look like live RingCentral acceptance evidence
unless a human has run the workflow and completed the record afterward.

## Current Context

- Cycle 148 added renderer-focused coverage for successful draft rendering and
  recorded the required draft-only anchors:
  `Draft only`, `not acceptance evidence`, and
  `No live RingCentral action has been performed by this helper.`
- `tests/unit/test_cli.py` has CLI success coverage through
  `assert_acceptance_draft_boundary(...)`, plus refusal tests for no-open-step,
  failed output write after no-open-step, existing output file, and
  `acceptance-runs.md` output.
- `src/ai_presenter/cli.py` renders the draft before writing output. The output
  writer then refuses `acceptance-runs.md`, refuses existing files, creates the
  parent directory, and writes the draft.
- `src/ai_presenter/acceptance/manual_record.py` rejects direct no-open-step
  entrypoints before rendering the manual fields.

## Minimal Scope

Prefer a test-only cycle. Strengthen the existing CLI refusal tests so every
rejected `acceptance-draft` path proves the same negative contract:

- no draft output file is created or overwritten;
- `Manual RingCentral Acceptance Draft` is absent from command output;
- `### Manual Acceptance Fields` is absent from command output;
- success/write wording such as `Wrote acceptance draft` is absent;
- conclusion-style evidence wording such as `Accepted`, `passed`, or
  `live validated` is absent.

Use precise assertions. Do not ban broad stems such as `accept`, `acceptance`,
`pass`, `fail`, `evidence`, `valid`, or `observed`, because valid safety
messages and field labels can contain those words.

## Out Of Scope

- Do not modify production code unless the strengthened tests reveal an actual
  bug.
- Do not modify `src/ai_presenter/acceptance/manual_record.py` for final output.
- Do not modify `acceptance-runs.md`.
- Do not declare or simulate live RingCentral acceptance.
- Do not update package YAML, generated artifacts, package metadata, or runtime
  behavior unrelated to the refusal boundary.
- Do not touch `.coverage`; if it is already dirty, leave it dirty.
- Do not revert unrelated changes from other agents.

## Acceptance Criteria

- Existing no-open-step refusal coverage still confirms the refusal message
  names the entrypoint and explains the missing executable open steps plus
  confirmation workflow requirement.
- The no-open-step refusal with `--output` still confirms the target output file
  does not exist after the command.
- Existing-output refusal still confirms the existing file contents remain
  unchanged.
- `acceptance-runs.md` output refusal still confirms no output file is created.
- All refusal tests assert no manual acceptance draft body or manual fields are
  rendered in CLI output.
- All refusal tests assert no success/write message and no conclusion-style
  evidence wording appears in CLI output.
- A focused test run for the affected CLI tests passes.
- Handoff/doc hygiene passes:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-149-demand-analysis.md
git diff --check -- docs\agent-handoffs\cycle-149-demand-analysis.md
```

## Implementation Handoff Prompt

You are working in `C:\Users\rcadmin\Documents\Repos\AiPresenter` on Cycle 149:
`acceptance-draft` refusal paths.

User value: when a draft request is refused, the CLI must not write files, must
not render Manual Acceptance Fields, and must not output evidence-like success
wording. This is a safety boundary around draft-only RingCentral acceptance
records.

Read these files first:

- `docs/agent-handoffs/cycle-148-experience.md`
- `docs/agent-handoffs/cycle-149-demand-analysis.md`
- `tests/unit/test_cli.py`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/acceptance/manual_record.py`

Implement test-first and keep the cycle as test-only unless a strengthened test
exposes a real production bug. In `tests/unit/test_cli.py`, add a small helper
for refusal-output boundaries if it keeps assertions DRY. Apply it to these
refusal paths:

- no-open-step direct entrypoint refusal;
- no-open-step direct entrypoint refusal with `--output`;
- existing output file refusal;
- `acceptance-runs.md` output refusal.

The helper should check command output precisely:

- it does not contain `Manual RingCentral Acceptance Draft`;
- it does not contain `### Manual Acceptance Fields`;
- it does not contain `Wrote acceptance draft`;
- casefolded output does not contain `accepted`, `passed`, or
  `live validated`.

Keep the existing positive refusal-message assertions and file side-effect
assertions. Do not add broad negative checks for `acceptance`, `evidence`,
`pass`, `fail`, `valid`, or `observed`.

Do not modify `acceptance-runs.md`, package YAML, package metadata, generated
artifacts, or `.coverage`. Do not declare live acceptance. Do not revert
unrelated work from other agents.

Suggested focused verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_cli.py -k "acceptance_draft"
rg -n "[ \t]+$" docs\agent-handoffs\cycle-149-demand-analysis.md
git diff --check -- docs\agent-handoffs\cycle-149-demand-analysis.md
git diff --check -- tests\unit\test_cli.py
git status --short
```

Expected final diff for this implementation cycle should be limited to
`tests/unit/test_cli.py` and any Cycle 149 handoff notes the user explicitly
asks for. If production code changes become necessary, explain which failing
test forced the change and keep the edit narrowly scoped.
