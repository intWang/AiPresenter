# Cycle 147 Risk Scan: Acceptance Draft Draft-Only Boundary

Date: 2026-05-17
Cycle: 147
Scope: documentation-only risk scan for `acceptance-draft` draft-only
boundary and related `validation-targets` draft command wording.
Do not modify source, tests, package YAML, generated artifacts, `.coverage`, or
acceptance evidence records for this task.

## Read Basis

- `docs/agent-handoffs/cycle-146-risk-scan.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `src/ai_presenter/acceptance/manual_record.py`
- `tests/unit/test_acceptance_manual_record.py`
- `tests/unit/test_cli.py` acceptance-draft and validation-targets draft tests

Current working-tree note: `.coverage` was already modified before this scan.
Leave it untouched.

## Risk Summary

`acceptance-draft` is useful because it creates a structured manual acceptance
record template with package, flow, entrypoint, checklist, required fields, and
privacy reminders. That output can reduce operator error after a real manual
RingCentral run.

The boundary risk is that a helpful draft can look like evidence. A generated
draft is only a pre-run or post-run note-taking aid. It must not be written into
`docs/knowledge/ringcentral-video/acceptance-runs.md` by the helper, and it must
not imply that a live RingCentral click, modal open, cleanup action, speech
action, provider check, or privacy-safe observation occurred.

The existing draft language is the anchor:

```text
Draft only: this is not acceptance evidence until filled after the manual run
and appended to `acceptance-runs.md`.
No live RingCentral action has been performed by this helper.
```

## Draft Vs Proof Boundary

Draft output can safely answer:

- Which package, flow, entrypoint, or checklist target the operator intends to
  validate.
- Which manual acceptance fields must be filled after a real run.
- Which route context, open steps, cleanup labels, and presenter notes should be
  considered before the run.
- Which privacy categories must not be recorded.
- Which documentation files may need updates after a completed run justifies
  them.

Draft output cannot answer:

- Whether the selected RingCentral route was executed.
- Whether a modal, panel, menu, settings page, cleanup path, or side effect was
  observed live.
- Whether pass/fail, failures, recovery, locator updates, or evidence files are
  known.
- Whether private chat text, participant names, invite links, meeting IDs,
  notes, transcripts, recordings, account details, shared content, device lists,
  or report contents were avoided in a real run.
- Whether provider readiness, OpenAI speech, virtual microphone routing, device
  state, locale, DPI, window bounds, or Spanish behavior was validated.
- Whether a checklist target, validation-targets draft command, or generated
  Markdown block is acceptance evidence.

`acceptance-runs.md` is the evidence ledger. A generated draft becomes relevant
there only after a human completes a dated manual run and fills the fields with
observed results. The helper should not append directly to that ledger.

## No-Go Claims

Do not claim or imply:

- `acceptance-draft` performed a live RingCentral action.
- A draft is acceptance evidence.
- A draft can be written directly to `acceptance-runs.md`.
- A draft command emitted by `validation-targets` proves the target was run.
- A filled-looking placeholder means pass/fail was observed.
- Package context, flow context, entrypoint context, open steps, or checklist
  context prove acceptance.
- `Steps executed: Intended ...` means actual steps were executed.
- `Privacy notes` in a draft prove privacy-safe handling occurred.
- `Post-Run Documentation Order` means the post-run documentation was already
  updated.
- A route with no executable open steps may receive a direct draft or be
  executed without a separate confirmation workflow.
- Blocked targets are draftable, executable, click-safe, cleanup-safe, or
  ready for unattended action.
- Acceptance status can be inferred from filenames, source paths, test names,
  template fields, generated commands, or successful draft rendering.
- The helper observed RingCentral app/build, Windows version, locale, DPI,
  monitor setup, audio devices, virtual mic, meeting role, participant count,
  window bounds, evidence files, failures, recovery, or locator updates.

## Safe Wording

Preferred wording:

- "draft only"
- "not acceptance evidence"
- "No live RingCentral action has been performed by this helper."
- "template for manual recording after a run"
- "intended flow"
- "intended target"
- "fill with actual steps after the run"
- "append the completed record to `acceptance-runs.md` after the run"
- "draft command prepares a record template; it does not execute the target"
- "blocked route; do not execute without a separate confirmation workflow"
- "manual/live acceptance requires a dated run record with environment, action,
  cleanup, pass/fail, recovery, and privacy notes"

Avoid wording that sounds like proof:

- "accepted"
- "validated"
- "verified"
- "executed"
- "observed"
- "passed"
- "completed run"
- "live evidence"
- "proof"
- "recorded in acceptance-runs"
- "safe to run"
- "cleanup confirmed"
- "privacy confirmed"

If a `validation-targets` detail view prints an `acceptance-draft` command,
keep non-evidence wording nearby:

```text
draft: ai-presenter acceptance-draft ...
Note: repo-derived planning list only; not live acceptance evidence.
```

If `acceptance-draft --output` succeeds, the success message should identify a
draft file only. It should not say the evidence ledger was updated or that a
manual run was recorded.

## Testing Risk

Risk: high if tests assert only that a draft renders or a draft command appears.
Those assertions can accidentally bless proof-like wording around the draft.

Safe test assertions:

- `acceptance-draft` output contains "Draft only" and "not acceptance evidence".
- Draft output contains "No live RingCentral action has been performed by this
  helper."
- Draft output keeps `Pass/fail`, `Failures`, `Recovery`, `Evidence files`, and
  `Locator updates needed` as fields to fill, not claimed results.
- Draft output uses intended-step wording and says to fill actual steps after
  the run.
- Draft output does not contain proof words such as `Accepted`.
- Direct drafts for no-open-step entrypoints are rejected before rendering
  manual acceptance fields.
- Rejected draft requests do not create output files.
- Existing output files are not overwritten.
- `acceptance-draft --output acceptance-runs.md` is refused and does not create
  or modify that path.
- `validation-targets` detail output may include a draft command only while the
  non-evidence note remains visible.
- `validation-targets --include-blocked --target ...` omits draft commands for
  blocked targets and keeps "Do not execute" wording.

No-go test assertions:

- Do not assert that a draft command means a manual run happened.
- Do not assert that writing an output file updates acceptance evidence.
- Do not test by writing to the real
  `docs/knowledge/ringcentral-video/acceptance-runs.md`.
- Do not add live RingCentral automation, UI clicks, screenshots, speech checks,
  provider checks, virtual microphone checks, or device checks for draft-only
  behavior.
- Do not relax refusal of `acceptance-runs.md` writes to simplify CLI tests.
- Do not rewrite package YAML, checklist rows, evidence levels, acceptance run
  records, or templates to make a draft test pass.
- Do not touch `.coverage`.

Suggested future verification for an implementation owner:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py -k acceptance_draft
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py -k validation_targets
git diff --check -- src\ai_presenter\acceptance\manual_record.py src\ai_presenter\cli.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
```

For this Cycle 147 task, the requested verification is markdown-only.

## Go/No-Go Recommendation

Go for draft helpers only if the output remains unmistakably draft-only, refuses
direct writes to `acceptance-runs.md`, rejects no-open-step direct drafts, and
keeps `validation-targets` draft commands framed as planning aids rather than
evidence.

No-go if any wording or behavior lets a generated draft become acceptance
evidence, suggests a live action occurred, writes the evidence ledger, turns
intended steps into executed steps, or offers draft commands for blocked routes.

The safe success state is narrow: `acceptance-draft` may prepare a human to
record a run, but proof begins only after a real dated manual/live run is
completed and recorded in `acceptance-runs.md`.
