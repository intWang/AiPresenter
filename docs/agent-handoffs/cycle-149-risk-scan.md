# Cycle 149 Risk Scan: Acceptance Draft Refusal Paths

Date: 2026-05-17
Cycle: 149
Scope: documentation-only risk scan for `acceptance-draft` refusal paths.
Do not modify source, tests, package YAML, generated artifacts, `.coverage`, or
acceptance evidence records for this task.

## Read Basis

- `docs/agent-handoffs/cycle-148-risk-scan.md`
- `tests/unit/test_cli.py` acceptance-draft refusal tests
- `src/ai_presenter/cli.py`
- `src/ai_presenter/acceptance/manual_record.py`

## Risk Summary

The refusal paths need to be clear enough for an operator to understand why the
draft was blocked, while staying outside the evidence boundary. A refusal is not
a manual acceptance draft, not a completed record, and not a ledger update.

The currently covered refusal surfaces are:

- Direct entrypoint drafts for entrypoints with no executable open steps.
- Refusals that must not create an `--output` file.
- Missing target selection.
- Unknown flow selection.
- Existing output file protection.
- Explicit refusal to write a draft to `acceptance-runs.md`.

The highest-risk path is the `acceptance-runs.md` output guard. The command
renders the draft before `_write_acceptance_draft_output()` rejects the reserved
ledger filename, so the safety property depends on the refusal message staying
fixed and the writer returning before any file write. Current tests assert the
refusal text and that the reserved file does not exist.

## No-Go Claims

Refusal output must not claim or imply:

- A manual acceptance draft was produced for the rejected request.
- A manual run happened.
- Any RingCentral action was performed, observed, validated, accepted, passed,
  failed, recovered, cleaned up, or privacy-checked.
- Evidence files exist, were captured, were validated, or were attached.
- The refusal generated a completed acceptance record.
- `acceptance-runs.md` was written, appended, updated, or prepared.
- The operator can treat the refusal as acceptance evidence.
- No-open-step entrypoints are safe for direct live execution.
- Existing output files were overwritten, merged, or inspected for evidence.

Refusals also must not print draft body content. In particular, blocked output
should not include the draft title, `### Manual Acceptance Fields`, required
manual field labels, intended steps, privacy notes, proof-order reminders, or
post-run documentation instructions.

## Safe Assertions

Safe refusal assertions should check narrow behavior and avoid treating all
acceptance vocabulary as unsafe.

- No-open-step entrypoint refusals can include the rejected entrypoint id.
- No-open-step entrypoint refusals can include `has no`, `executable`, `open
  steps`, `confirmation`, and `workflow`.
- No-open-step entrypoint refusals should exclude `Manual RingCentral Acceptance
  Draft` and `### Manual Acceptance Fields`.
- Refusals with `--output` should leave the requested output path absent or
  unchanged.
- Missing-target refusals can assert `Provide at least one target`.
- Unknown-flow refusals can assert `Unknown demo flow` and `Available flows`.
- Existing-output refusals can assert `Output file already exists` and verify the
  existing file contents are unchanged.
- Reserved-ledger refusals can assert `Refusing to write acceptance draft to
  acceptance-runs.md`.
- Successful file-write stdout can safely say `Wrote acceptance draft: <path>`
  only for non-ledger draft files, because the draft content is written to that
  separate file and the console message does not claim evidence.
- Successful file-write stdout should continue to avoid `acceptance evidence`.

The safe distinction is between naming the blocked draft operation and claiming
acceptance evidence. `acceptance draft` is safe in a refusal; `acceptance
evidence recorded` is not.

## Negative Assertion Risks

Avoid broad negative assertions on refusal output that would block legitimate
diagnostic text or reserved-path warnings:

- `assert "acceptance" not in output`
- `assert "draft" not in output`
- `assert "acceptance-runs.md" not in output`
- `assert "evidence" not in output`
- `assert "manual" not in output`
- `assert "workflow" not in output`
- `assert "open steps" not in output`

Those assertions would conflict with safe refusal language. For example,
`Refusing to write acceptance draft to acceptance-runs.md` is clear and safe
because it names the blocked operation and reserved ledger path without saying
the ledger was updated. Likewise, `confirmation workflow` is safe because it
explains why no-open-step entrypoints need a separate process before live
execution.

Prefer targeted no-go checks:

- Reject draft body markers in refusal output, such as `Manual RingCentral
  Acceptance Draft`, `### Manual Acceptance Fields`, `### Proof-Order Reminder`,
  and `### Post-Run Documentation Order`.
- Reject proof-like phrases such as `accepted`, `passed`, `manual run
  completed`, `live action performed`, `evidence files captured`, `acceptance
  evidence recorded`, `appended to acceptance-runs.md`, or `updated
  acceptance-runs.md`.
- For file refusals, assert filesystem state instead of inferring from wording:
  no new blocked file, no reserved ledger file, and no mutation of an existing
  output file.

One subtle risk is a future test that only asserts the refusal exit code and
reserved filename. That would miss accidental leakage if the CLI began printing
the rendered draft before raising the output-path error. Keep at least one
negative body-marker assertion on refusal paths that happen after render.

## Go/No-Go Recommendation

Go for the current refusal-path direction if tests keep the boundary semantic:
operators receive concise rejection reasons, blocked output files are not
created or changed, and refusal stdout/stderr never contains draft body content
or proof-like acceptance claims.

No-go if a refusal prints manual draft sections, echoes intended steps or
privacy notes, suggests evidence was generated, says the run passed or failed,
or claims `acceptance-runs.md` was appended. No-go also if tests use broad word
bans that would make clear reserved-path refusal messages impossible to keep.

The intended state is precise: refusal paths may name the requested draft action
and the reason it was blocked, but they must not become either a draft transport
or an evidence transport.
