# Cycle 149 Experience: Acceptance Draft Refusal Boundaries

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Topic And User Value

Cycle 149 tightened the `acceptance-draft` refusal contract at the CLI test
layer. The user value is preserving a clear safety boundary: a rejected draft
request must remain only a refusal, not a partial manual acceptance draft, not a
file write, and not output that can be mistaken for live RingCentral evidence.

The protected cases are:

- direct entrypoint requests with no executable open steps;
- the same no-open-step refusal when `--output` is provided;
- existing output file protection;
- reserved `acceptance-runs.md` output protection.

For operators, this keeps blocked requests understandable without creating
false confidence. They can see why the command refused the request, but they do
not receive rendered manual acceptance fields, write-success wording, or
conclusion-like evidence language.

## Sub-Agent Handoff

The cycle worked well because each handoff narrowed the next agent's task:

- Demand analysis defined the user-facing safety boundary and explicitly kept
  the scope test-only unless a real production bug appeared.
- Technical scan identified the exact CLI helper shape and call sites, while
  noting that production writer guards already refused dangerous paths before
  writes.
- Risk scan separated safe refusal vocabulary from unsafe evidence claims, which
  prevented over-broad negative assertions.
- Implementation added one refusal-boundary helper and applied it only to the
  requested paths.
- Review verified the helper stayed narrow, the diff was test-only, and
  `src/ai_presenter/cli.py` had no final diff.

The most important handoff detail was the distinction between naming the blocked
draft operation and implying acceptance evidence. Messages like `Refusing to
write acceptance draft to acceptance-runs.md` remain safe because they name the
blocked operation and reserved ledger path without claiming the ledger changed.

## Experience Rules

- Refusal paths must not render draft fields. Keep `Manual RingCentral
  Acceptance Draft` and `### Manual Acceptance Fields` out of rejected command
  output.
- Refusal paths must not print write-success text. `Wrote acceptance draft` is
  only valid after a non-reserved draft file has actually been written.
- Refusal paths must not write files. Assert absent output files for blocked
  writes and unchanged contents for existing-file refusals.
- Refusal paths must not sound like completed evidence. Keep narrow checks for
  `accepted`, `passed`, and `live validated` in casefolded output.
- Negative assertions must stay narrow. Do not ban broad words such as
  `acceptance`, `draft`, `manual`, `evidence`, `pass`, `fail`, `valid`, or
  `observed`; those can appear in legitimate refusal guidance.
- The `acceptance-runs.md` refusal boundary is especially sensitive. Tests
  should allow the reserved filename and safe refusal wording, while still
  proving no draft body, write success, or conclusion-like evidence language is
  printed.
- Prefer filesystem assertions for write safety. Output wording can explain a
  refusal, but side-effect guarantees should be checked by file existence or
  exact content preservation.
- Do not expand a refusal test into broad semantic policing. The purpose is to
  block draft-body leakage and evidence-like success claims without making safe
  diagnostics impossible.

## Next-Round Suggestions

One narrow follow-up is `validation-targets` behavior when no evidence file is
available. Guard that `Evidence: none` remains traceability state and cannot be
read as proof. A useful fallback test would cover the omitted-evidence-file path
and verify the output stays explicit about missing evidence rather than implying
validation happened.

Another follow-up is an `acceptance-draft` refusal boundary for unknown or
missing targets. Current Cycle 149 implementation focused on the four requested
paths. A next cycle could add the same refusal-boundary helper to missing target
and unknown flow refusals if that remains compatible with their expected help
text.

## Verification And Commit Notes

Before submitting a broader branch that includes this work, run the full local
verification set:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check --no-cache .
.\.venv\Scripts\mypy.exe .
git diff --check
```

For documentation-only experience updates, also run targeted hygiene:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-149-experience.md
git diff --check -- docs\agent-handoffs\cycle-149-experience.md
```

Do not stage `.coverage`. It was already dirty during the implementation and
review handoffs, and it is outside the Cycle 149 deliverable. Also avoid staging
unrelated source, package, test, or generated-file changes from other agents.
