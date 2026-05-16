# Cycle 145 Risk Scan: Validation Targets CLI Evidence Boundary

Date: 2026-05-17
Cycle: 145
Scope: risk scan for adding guards around the `validation-targets` CLI boundary.
This handoff is documentation-only. Do not modify source, tests, package YAML,
generated artifacts, or `.coverage` for this risk-scan task.

## Read Basis

- `docs/agent-handoffs/cycle-144-risk-scan.md`
- `docs/agent-handoffs/cycle-144-experience.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `src/ai_presenter/acceptance/validation_targets.py`
- `tests/unit/test_cli.py` around the `validation-targets` tests

Current working-tree note: `.coverage` was already modified before this scan.
This task must not stage, revert, normalize, or otherwise touch it.

## Current Boundary Observed

The `validation-targets` command is an offline planner. It loads the material
package plus checklist/evidence markdown, renders target rows, and can include
an `acceptance-draft` command string. It does not run RingCentral, click UI,
open settings, check providers, inspect runtime speech, or record acceptance.

The rendered output already includes the boundary note:

```text
repo-derived planning list only; not live acceptance evidence.
```

That wording is the central guard to preserve. Listing a target, showing target
details, showing an evidence level from the index, or printing a draft command
must remain a planning affordance only.

## No-Go Claims

Do not claim or imply:

- `validation-targets` output is live RingCentral acceptance evidence.
- A target listing means the route is accepted, current, live-safe, or ready to
  run unattended.
- A target detail page, evidence level, `current` field, `validate` field,
  cleanup text, or privacy boundary proves that the route was clicked,
  cleaned up, or accepted.
- A generated `acceptance-draft` command is evidence. It is only a command to
  prepare a manual record template.
- `Observed` means click-safe or cleanup-safe. It can describe dated sanitized
  observation only.
- `Repo-tested` means RingCentral accepted the route in the current app build.
- Manual checklist rows or runbook checkboxes are acceptance evidence before a
  dated result is recorded in `acceptance-runs.md`.
- CLI guards prove runtime/provider readiness, OpenAI speech readiness, local
  provider readiness, virtual microphone readiness, or live Spanish behavior.
- CLI guards introduce new RingCentral live claims for audio menu, video menu,
  More menu, Settings, Background, Notes, Invite, Participants, Chat, Share,
  reactions, raise hand, recording, or leave/end.

## Safe Wording

Preferred language:

- "`validation-targets` renders a repo-derived planning list."
- "The CLI output is not live acceptance evidence."
- "The draft command prepares an acceptance-run template; it does not execute
  the target or record a pass."
- "Accepted live behavior requires a dated manual/live record in
  `docs/knowledge/ringcentral-video/acceptance-runs.md`."
- "Repo tests cover parsing, output shape, and boundary wording."
- "Evidence levels are imported from the evidence index and must keep their
  documented meanings: `Accepted`, `Observed`, `Repo-tested`, `Backlog`, and
  `Blocked`."
- "Runtime/provider readiness and RingCentral live acceptance are separate
  gates."
- "Spanish package or CLI inspection boundaries do not create local provider
  support or live RingCentral acceptance."

If a test guard is added, name the boundary directly. For example:

```text
validation-targets output must describe itself as a repo-derived planning list
only and not live acceptance evidence.
```

Avoid vague words such as "validated", "verified", "ready", or "safe" unless
the sentence states exactly which evidence level and source support the claim.

## Privacy And Acceptance Boundaries

`validation-targets` may summarize checklist privacy boundaries, but that does
not grant permission to inspect private content. Keep the CLI and any guard
wording on the documentation/planning side of the line.

Privacy no-go areas:

- Device names, selected microphones, speakers, cameras, levels, camera
  previews, or hardware readiness.
- Chat text, participant names, roles, invite suggestions, invite links,
  meeting IDs, dial-in details, captions, transcripts, notes, recordings, or
  report contents.
- Background thumbnails, custom images, room imagery, mirror state, blur state,
  account labels, or settings preferences.
- Screenshots as default evidence.

Acceptance boundary:

- `validation-checklist-index.md` is procedure, not proof.
- `evidence-index.md` is navigation and evidence-level summary, not a fresh
  run.
- `acceptance-runs.md` is where dated manual/live evidence belongs.
- `validation_targets.py` can parse and render planning data, but it must not be
  treated as a runtime acceptance engine.
- Any future promotion to `Accepted` requires environment, route, action,
  cleanup, pass/fail, recovery, and privacy notes in `acceptance-runs.md`.

## Test Scope Risk

Risk: medium-high if the guard is implemented too broadly.

Safe test scope:

- Assert `validation-targets` list/detail output includes the non-evidence note.
- Assert detail output that includes a draft command still includes the same
  non-evidence note.
- Assert blocked targets continue to omit draft commands.
- Assert unknown-target errors remain about catalog lookup only.
- Keep tests focused in the existing CLI test area if the implementation owner
  chooses a guard.

No-go test scope:

- Do not edit source behavior just to manufacture a broader evidence claim.
- Do not add live RingCentral automation, UI clicks, provider checks, speech
  playback, virtual microphone checks, or runtime profile execution.
- Do not require optional metadata completeness.
- Do not change package YAML, aliases, Q&A, route definitions, evidence levels,
  provider compatibility, or Spanish runtime boundaries.
- Do not write to `acceptance-runs.md` as part of a CLI guard unless an actual
  dated manual/live run was performed and recorded with privacy notes.
- Do not touch `.coverage`.

Suggested focused verification for a future guard owner:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py -k validation_targets
git diff --check -- src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_cli.py
```

If the change is docs-only, run only the relevant markdown whitespace checks.

## Go/No-Go Recommendation

Go for a narrow CLI output guard that preserves the existing non-evidence
boundary across list, detail, and draft-command output. It is useful because
the command intentionally places checklist targets, evidence levels, and draft
commands next to each other, which can invite overclaiming.

No-go if the change expands into runtime/provider claims, live RingCentral
claims, package changes, source behavior changes beyond wording/output
plumbing, or acceptance-record updates without an actual dated manual/live run.

The safest success state is modest: users can discover validation targets and
draft the next manual acceptance record, while the CLI remains explicit that
the output is only a repo-derived planning list and not live acceptance
evidence.
