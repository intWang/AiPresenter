# Cycle 150 Risk Scan: Validation Targets Evidence None Fallback

Date: 2026-05-17
Cycle: 150
Scope: documentation-only risk scan for `validation-targets` evidence fallback
wording.
Do not modify source, tests, package YAML, generated artifacts, `.coverage`, or
acceptance evidence records for this task.

## Read Basis

- `docs/agent-handoffs/cycle-149-risk-scan.md`
- `tests/unit/test_validation_targets.py`
- `src/ai_presenter/acceptance/validation_targets.py`

## Risk Summary

`Evidence: none` is a catalog-level source traceability statement. It means the
rendered validation target list was built without an evidence index path. It is
not live acceptance proof, not evidence gap resolution, and not a signal that
targets are ready to execute.

The current implementation has two nearby fallback surfaces:

- Header fallback: `Evidence: none` when `catalog.evidence_path` is absent.
- Per-target fallback: `evidence: unknown` when a target has no entrypoints or
  an entrypoint lacks a parsed evidence level.

Those fallbacks are safe only if they remain descriptive of source availability.
They become unsafe if downstream copy, tests, or operator docs treat them as
proof that no acceptance evidence is needed, no gaps remain, or no live check is
required.

## No-Go Claims

Validation target output and tests must not claim or imply:

- `Evidence: none` means the target has passed manual acceptance.
- `Evidence: none` means no live RingCentral validation is required.
- `Evidence: none` means evidence gaps are resolved, waived, or absent.
- `Evidence: none` means no privacy, cleanup, or post-run record work remains.
- `Evidence: none` is equivalent to `Accepted`, `Observed`, `Repo-tested`,
  `Backlog`, or `Blocked`.
- `evidence: unknown` is a successful evidence status.
- Missing evidence index input is itself acceptance evidence.
- Missing source traceability authorizes live execution.
- A rendered planning list is an acceptance record.
- The `acceptance-draft` command shown for a target has already run.
- The target catalog updates `acceptance-runs.md` or any evidence ledger.
- Absence of an evidence path proves absence of user-impacting risk.

Also avoid wording such as `no evidence needed`, `evidence cleared`, `gap
closed`, `proof absent but acceptable`, `safe to execute`, or `ready because
Evidence: none`.

## Safe Assertions

Safe assertions should stay narrow and source-oriented:

- The header may render `Evidence: none` only when `catalog.evidence_path` is
  absent.
- The header may render `Evidence: <path>` when an evidence index path was
  provided.
- The note `repo-derived planning list only; not live acceptance evidence`
  remains a useful boundary marker and should not be weakened.
- Per-target evidence can render `unknown` for source traceability absence.
- Per-target evidence can render known evidence levels only when parsed from the
  evidence index.
- Evidence index integrity tests can require every package entrypoint to appear
  exactly once in the real evidence index.
- Validation target discovery can reject unknown checklist ids and unknown
  evidence-index entrypoints.
- Output can include draft commands as operator next steps, provided they remain
  planning instructions and not run results.

The safe frame is: validation targets are a planning surface derived from repo
sources. They can describe which evidence source was available and which level
was parsed, but they cannot prove live behavior by themselves.

## Negative Assertion Risks

Avoid broad negative assertions that would block safe traceability language:

- `assert "Evidence: none" not in text`
- `assert "none" not in text`
- `assert "unknown" not in text`
- `assert "evidence" not in text`
- `assert "acceptance" not in text`
- `assert "draft:" not in text`

Those assertions blur the difference between source traceability and acceptance
proof. They could force removal of useful boundary text, especially the current
non-evidence note.

Prefer targeted assertions:

- When no evidence path is supplied, assert the exact header fallback:
  `Evidence: none`.
- Pair any `Evidence: none` assertion with the non-evidence note.
- Reject proof-like phrases near the fallback, such as `accepted`, `passed`,
  `validated live`, `gap resolved`, `evidence captured`, `ledger updated`, or
  `ready to execute`.
- For real catalog discovery, continue asserting that no entrypoint evidence
  level remains `unknown`.
- For synthetic no-evidence inputs, assert that `unknown` remains an absence of
  source traceability, not a valid evidence level.

One subtle risk is a future test that celebrates `Evidence: none` as a
successful evidence state. That would invert the boundary: the fallback should
make source absence visible, not convert absence into proof.

## Go/No-Go Recommendation

Go if `Evidence: none` remains a literal source-path fallback and the rendered
output keeps the non-evidence note. Go if tests treat `unknown` as traceability
absence and reserve acceptance levels for values parsed from the evidence index.

No-go if wording or tests treat `Evidence: none` as live acceptance proof, as a
closed evidence gap, or as permission to execute. No-go if the planning list is
described as an acceptance record or if draft commands are described as already
run.

The intended state is precise: `Evidence: none` may say no evidence index source
was attached to this rendered catalog. It must not say the product behavior was
accepted, observed, cleared, or proven.
