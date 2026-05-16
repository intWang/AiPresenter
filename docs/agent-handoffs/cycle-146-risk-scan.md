# Cycle 146 Risk Scan: Validation Targets Traceability Boundary

Date: 2026-05-17
Cycle: 146
Scope: documentation-only risk scan for `validation-targets` traceability wording.
Do not modify source, tests, package YAML, generated artifacts, `.coverage`, or
acceptance evidence records for this task.

## Read Basis

- `docs/agent-handoffs/cycle-145-risk-scan.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `tests/unit/test_cli.py` around the `validation-targets` tests
- `tests/unit/test_validation_targets.py`

Current working-tree note: `.coverage` was already modified before this scan.
Leave it untouched.

## Risk Summary

`validation-targets` is useful because it joins checklist rows, evidence levels,
entrypoint IDs, flow IDs, blocked reasons, and draft acceptance commands into
one planner view. Adding source paths to that output can improve auditability:
operators can see which markdown index or package source produced a row.

The guard risk is that source paths may look authoritative. A rendered path such
as `validation-checklist-index.md`, `evidence-index.md`, `acceptance-runs.md`,
or `packages/ringcentral-video.yaml` must not imply that the listed target has
fresh live acceptance proof. Those paths are traceability pointers only. The
existing CLI boundary note remains the anchor:

```text
Note: repo-derived planning list only; not live acceptance evidence.
```

## Traceability Vs Proof Boundary

Source paths can safely answer:

- Where did this target row come from?
- Which checklist procedure or evidence index row should be inspected next?
- Which package entrypoint or flow ID is connected to the target?
- Which file should a human update after a real dated run?

Source paths cannot answer:

- Whether the route was accepted in the current RingCentral build.
- Whether a modal, panel, menu, settings page, or cleanup path was clicked live.
- Whether privacy-sensitive content was avoided in a recent manual run.
- Whether provider, speech, virtual microphone, device, or runtime readiness was
  verified.
- Whether a checklist row, evidence-index row, or draft command is itself proof.

`validation-checklist-index.md` is procedure, not proof.
`evidence-index.md` is a navigation and evidence-level summary, not a fresh run.
`acceptance-runs.md` is the evidence ledger, but only dated run records inside
it can support acceptance claims. Merely printing the path to
`acceptance-runs.md` is not acceptance evidence.

## No-Go Claims

Do not claim or imply:

- Source paths prove live RingCentral acceptance.
- A checklist source path means the route is validated, click-safe,
  cleanup-safe, privacy-safe, current, or ready for unattended execution.
- An evidence-index source path upgrades `Observed`, `Repo-tested`, `Backlog`,
  or `Blocked` into `Accepted`.
- A path to `acceptance-runs.md` means a matching dated manual run exists.
- A target sourced from `validation-checklist-index.md` has already passed the
  checklist.
- A target sourced from `evidence-index.md` has current build evidence beyond
  the documented evidence level.
- A source path plus `acceptance-draft` command is a proof chain.
- A `current`, `validate`, `cleanup`, `privacy boundary`, `record result`, or
  `evidence level` field is live acceptance proof by itself.
- Source paths validate runtime/provider readiness, OpenAI speech output, local
  provider support, virtual microphone routing, device state, or Spanish
  behavior.
- Source paths make blocked targets executable.
- Printing private-sensitive source references grants permission to inspect
  chat, participant names, invite links, device names, meeting IDs, notes,
  transcripts, recordings, report contents, or background imagery.

## Safe Wording

Preferred wording:

- "source: traceability pointer only"
- "sources: checklist/evidence/package paths for audit, not proof"
- "Repo-derived source paths help locate the planning inputs."
- "A source path does not replace a dated manual/live record in
  `docs/knowledge/ringcentral-video/acceptance-runs.md`."
- "Checklist rows describe what to validate; they do not prove validation."
- "Evidence-index rows summarize documented evidence levels; they do not create
  fresh live acceptance."
- "A draft command prepares a record template; it does not execute or pass the
  target."
- "Accepted live behavior requires a dated run record with environment, action,
  cleanup, pass/fail, recovery, and privacy notes."

Avoid vague labels that sound like proof:

- "validated by"
- "verified by"
- "proof source"
- "accepted source"
- "evidence source" unless the sentence distinguishes evidence-level summary
  from dated proof
- "source of truth" for checklist or evidence-index paths
- "ready", "safe", "passed", or "confirmed" unless tied to a specific dated
  acceptance run

If source paths are rendered, pair them with boundary language nearby:

```text
sources: docs/knowledge/ringcentral-video/validation-checklist-index.md
         docs/knowledge/ringcentral-video/evidence-index.md
source paths are for traceability only; not live acceptance evidence.
```

## Testing Risk

Risk: medium if source-path guards assert only that filenames appear. Filename
assertions can accidentally bless proof-like wording.

Safe test assertions:

- Existing list/detail output keeps
  `Note: repo-derived planning list only; not live acceptance evidence.`
- Any source-path output uses traceability wording, not proof wording.
- Detail output with an `acceptance-draft` command still states that output is
  not live acceptance evidence.
- Blocked targets with source paths still omit draft commands and keep blocked
  wording.
- Unknown target and unknown checklist reference errors remain catalog lookup
  failures, not acceptance failures.
- `tests/unit/test_validation_targets.py` continues to check parser integrity,
  target IDs, evidence-level imports, blocked rows, and draft-command shape
  without turning docs into proof.

No-go test assertions:

- Do not assert that `validation-checklist-index.md` or `evidence-index.md`
  proves acceptance.
- Do not assert that the presence of `acceptance-runs.md` means a dated run was
  found.
- Do not add live RingCentral automation, UI clicks, speech/provider checks,
  virtual microphone checks, or screenshots for a traceability guard.
- Do not rewrite package YAML, checklist rows, evidence levels, run records, or
  acceptance templates to make the CLI test easier.
- Do not touch `.coverage`.

Suggested future verification for a source-path implementation owner:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py -k validation_targets
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py
git diff --check -- src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_validation_targets.py
```

For this Cycle 146 task, the requested verification is markdown-only.

## Go/No-Go Recommendation

Go for source paths only if the output explicitly frames them as traceability
metadata and keeps the non-evidence note visible in list, detail, draft-command,
and blocked-target contexts.

No-go if the wording turns checklist/evidence/package paths into acceptance
proof, promotes evidence levels, suggests current RingCentral runtime readiness,
or encourages users to treat draft commands as executed runs.

The safe success state is narrow: `validation-targets` can show where planning
inputs came from, while remaining unmistakable that live acceptance requires a
dated manual/live record in `acceptance-runs.md`.
