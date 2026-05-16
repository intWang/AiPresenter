# Cycle 148 Risk Scan: Renderer Acceptance Draft Boundary

Date: 2026-05-17
Cycle: 148
Scope: documentation-only risk scan for renderer-level unit tests around
`acceptance-draft` draft-only semantics.
Do not modify source, tests, package YAML, generated artifacts, `.coverage`, or
acceptance evidence records for this task.

## Read Basis

- `docs/agent-handoffs/cycle-147-risk-scan.md`
- `tests/unit/test_acceptance_manual_record.py`
- `src/ai_presenter/acceptance/manual_record.py`

## Risk Summary

Renderer-level unit tests should keep the manual acceptance draft unmistakably
draft-only without turning the renderer into a brittle word filter. The draft
must be allowed to render required field labels such as `Pass/fail`, `Evidence
files`, `Steps executed`, `Privacy notes`, and `Locator updates needed`, because
those labels are placeholders the operator must fill after a real manual run.

The highest-risk test shape is a broad negative assertion that rejects evidence
or pass/fail vocabulary anywhere in the draft. That would either fail against
required manual fields or pressure future maintainers to remove useful labels.
The correct boundary is semantic: forbid claims that live acceptance happened,
while preserving fields and reminders that make the post-run record complete.

The existing renderer anchor remains:

```text
Draft only: this is not acceptance evidence until filled after the manual run
and appended to `acceptance-runs.md`.
No live RingCentral action has been performed by this helper.
```

## No-Go Claims

Renderer output and renderer tests must not claim or imply:

- A draft is acceptance evidence.
- A live RingCentral action occurred.
- The helper observed or validated a route, modal, cleanup action, provider
  state, speech action, privacy behavior, evidence file, failure, recovery, or
  locator update.
- A required field label means the field has been filled.
- `Pass/fail` means a pass or fail result is known.
- `Evidence files` means evidence exists.
- `Steps executed` means real steps were executed.
- `Privacy notes` means privacy handling was confirmed in a live run.
- `Post-Run Documentation Order` means documentation has already been updated.
- `acceptance-runs.md` has been appended or modified by the renderer.
- The word `acceptance` is unsafe in all contexts.
- The phrase `not acceptance evidence` is unsafe because it contains
  `acceptance evidence`.

## Safe Assertions

Safe renderer assertions should check the boundary in narrow, intentional ways:

- Output contains `Draft only`.
- Output contains `not acceptance evidence`.
- Output contains `No live RingCentral action has been performed by this
  helper.`
- Output contains the selected package, flow, entrypoint, and checklist context
  as intended targets, not completed evidence.
- Output contains required field labels returned by
  `required_manual_acceptance_fields()`.
- Output keeps `- Pass/fail:`, `- Evidence files:`, `- Failures:`,
  `- Recovery:`, and `- Locator updates needed:` as blank or operator-filled
  fields rather than claimed outcomes.
- Output says to `fill with actual steps after the run` for intended steps.
- Output says draft-only fields are placeholders until the manual run is
  complete.
- Output says to keep pass/fail, failures, recovery, evidence files, and locator
  updates blank until observed.
- Output rejects direct drafts for no-open-step entrypoints before rendering
  manual acceptance fields.

Targeted negative assertions are also safe when they avoid legitimate labels and
negated phrases:

- Reject `Accepted` as a proof-like status word.
- Reject exact phrases such as `acceptance evidence recorded`,
  `manual run completed`, `live action performed`, `evidence files captured`, or
  `pass confirmed` if they ever appear.
- Reject direct ledger-update wording such as `appended to acceptance-runs.md`
  unless the wording is explicitly future-facing, such as `after the run`.

## Negative Assertion Risks

Do not add broad substring bans that would catch required field labels or safety
language. Risky examples:

- `assert "acceptance evidence" not in draft`
- `assert "acceptance" not in draft`
- `assert "evidence" not in draft`
- `assert "pass" not in draft`
- `assert "fail" not in draft`
- `assert "executed" not in draft`
- `assert "observed" not in draft`
- `assert "acceptance-runs.md" not in draft`

Those patterns over-ban legitimate renderer text:

- `not acceptance evidence` is the explicit negation the draft needs.
- `Evidence files` is a required manual field.
- `Pass/fail`, `Failures`, and `Recovery` are required manual fields.
- `Steps executed` is a required field label, while its value should remain
  intended-step guidance until filled after the run.
- `until observed` appears in safe guidance telling the operator to leave proof
  fields blank.
- `acceptance-runs.md` is safe when referenced as the ledger to append a
  completed record to after a real run.

Prefer exact no-go phrase checks or line-level checks that distinguish labels
from values. For example, it is safer to assert that `- Pass/fail:` is present
and has no claimed result than to ban `pass` or `fail` globally.

## Go/No-Go Recommendation

Go for renderer-level acceptance draft tests if they preserve the draft-only
anchor, require the manual field labels, and use targeted proof-claim negatives.
The renderer should remain a template generator, not an evidence generator.

No-go if tests use broad vocabulary bans that would forbid field labels,
negated safety wording, or future-facing documentation instructions. No-go also
if tests allow proof-like status claims, live-action claims, or direct evidence
ledger update claims to appear in renderer output.

The safe state is precise: unit tests should block claims that acceptance
happened, while allowing the draft to name the fields a human must fill after
acceptance actually happens.
