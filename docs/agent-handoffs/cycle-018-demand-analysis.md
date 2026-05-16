# Cycle 018 Demand Analysis: Manual Acceptance Record Helper

Date: 2026-05-16
Role: demand-analysis worker
Write scope: this file only

## Read Scope

Reviewed local repository context only:

- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/cli.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-017-summary.md`

No live RingCentral actions were run. No production code, tests, package YAML,
runbook, or knowledge docs were edited.

## 1. User/Operator Problem

RingCentral Video manual acceptance now has a good evidence map and validation
checklist, but the actual acceptance record is still hand-authored. That is a
small but meaningful friction point because the required record is detailed:
build, channel, Windows version, locale, DPI, monitor setup, devices, profile,
package flow, role, scenario, participant count, window bounds, evidence files,
steps, pass/fail, failures, recovery, privacy notes, and locator updates.

The operator also has to copy route-specific details from several places before
or after a validation pass:

- `packages/ringcentral-video.yaml` for entrypoint IDs, titles, areas,
  open-step cleanup modes, presenter notes, and explain-only routes.
- `validation-checklist-index.md` for priority, current state, validation
  action, cleanup, privacy boundary, and where results should be recorded.
- `evidence-index.md` for evidence level, current gaps, and route risk.
- `acceptance-runs.md` for the canonical manual acceptance template.
- `ringcentral-manual-acceptance.md` for smoke/controller context and the rule
  that checklist boxes are not proof.

The demand is not for a tool that clicks RingCentral. The demand is for a safe
record-preparation helper that reduces copy/paste mistakes and makes the next
manual proof entry structurally consistent after a human or supervised agent has
performed validation.

## 2. Proposed Scope And Out-of-Scope

Recommended scope: add an offline acceptance-run draft helper that generates a
markdown snippet for a target RingCentral package entrypoint or checklist row.

Suggested product shape:

- CLI-first, likely near existing Typer commands such as `entrypoints`,
  `flows`, and `doctor`.
- Input accepts one of:
  - `--entrypoint ringcentral.video.main.add-coworkers`
  - `--check "Add coworkers modal"` or a stable checklist key if later added
  - optional `--flow meeting-control-map-demo`
- Output is a markdown draft to stdout by default, suitable for appending to
  `docs/knowledge/ringcentral-video/acceptance-runs.md` after the run.
- The draft should prefill non-sensitive package/checklist context such as
  target entrypoint, title, area, intended action, cleanup expectation, current
  evidence level, privacy boundary, and docs to update.
- The draft should leave runtime proof fields blank or explicitly marked
  `TODO`, including build, participant count, pass/fail, evidence files,
  failures, recovery, and locator updates.
- It should include a prominent note that the draft is not acceptance evidence
  until the actual run result is completed and appended to `acceptance-runs.md`.

Minimum useful generated sections:

- Dated manual acceptance header placeholder.
- Tester and environment fields from the canonical template.
- Target fields: package, optional flow, entrypoint/checklist row, current
  evidence state, expected action, expected cleanup.
- Privacy boundaries copied or summarized from the checklist/package notes.
- Steps executed placeholder seeded with the intended route action, not a claim
  that it happened.
- Pass/fail, failures, recovery, evidence files, and locator updates as blank
  fields.
- Post-run docs reminder: update `acceptance-runs.md` first, then evidence and
  locator/state/privacy docs only when the completed run justifies it.

Out-of-scope:

- Clicking, focusing, scanning, or otherwise operating live RingCentral.
- Automatically appending completed proof to `acceptance-runs.md` without human
  review.
- Reading chat, participants, invite links, meeting IDs, shared content,
  account data, device names, notes, transcripts, or report contents.
- Promoting any route to `Accepted`.
- Generating screenshots or evidence files.
- Changing `packages/ringcentral-video.yaml` schema in the first slice.
- Replacing the validation checklist or evidence index as the source of
  acceptance policy.

## 3. Acceptance Criteria

A future implementation should be accepted when:

- The helper can generate a markdown draft for at least a package entrypoint ID,
  starting with `ringcentral.video.main.add-coworkers`.
- The helper can generate a draft from a validation checklist row or route group
  without losing the row's priority, validation action, cleanup, privacy
  boundary, and record-result guidance.
- The generated draft follows the field structure of the manual template in
  `acceptance-runs.md`.
- The generated draft clearly distinguishes intended steps from completed
  evidence. It must not prefill pass/fail as pass, mark a route accepted, or
  imply that RingCentral was clicked.
- Risky or explain-only routes such as `ringcentral.video.more.recording` and
  `ringcentral.video.toolbar.leave` are labeled as blocked/explain-only and
  produce drafts that do not instruct the operator to execute the live action.
- Privacy notes are present for sensitive targets such as Add coworkers,
  Invite, Chat, Participants, Share, Meeting info, Report issue, Notes,
  Settings, Background, Recording, and Leave.
- Unknown entrypoint/checklist targets fail with a clear message and suggest
  discovery commands or known targets.
- Unit tests cover successful draft generation, unknown target errors, and at
  least one blocked/explain-only target.
- Existing `run`, `demo`, `controller`, `flows`, `entrypoints`, `voices`, and
  `doctor` behavior remains unchanged.

## 4. Risks/Privacy Boundaries

- Overclaim risk: a generated draft can look like evidence. The output must say
  it is a draft until a completed manual run is appended to `acceptance-runs.md`.
- Live-action risk: operators may assume the helper validates RingCentral. Keep
  the helper offline and avoid names like `accept` or `validate` unless paired
  with `draft` or `record`.
- Drift risk: parsing markdown checklist rows can become brittle. A first slice
  can use conservative parsing and tests, but stable checklist IDs may be worth
  adding in a later docs/schema cycle.
- Privacy risk: prefilled context must summarize sensitive boundaries, not
  harvest sensitive runtime content. Never include invite links, names, chat
  text, meeting IDs, shared-screen content, device lists, notes, transcripts, or
  account details.
- Evidence-order risk: the helper should remind operators to update
  `acceptance-runs.md` first, then update index/matrix docs only after the run
  is complete.
- Scope creep risk: connecting this to controller/runtime automation would blur
  the safety boundary. Keep execution and record drafting separate.

## 5. Priority/Recommendation

Priority: high for operator quality, medium for runtime product breadth.

Recommendation: implement this as the next small CLI/documentation tooling slice
before more live RingCentral acceptance runs. It directly supports the Cycle 017
validation checklist by making the proof-record step less error-prone, while
preserving the core safety rule: the helper prepares markdown only; a human or
supervised agent performs validation and completes the evidence.

The first target should be `ringcentral.video.main.add-coworkers` because it is
P0, already observed as a UIA button, package-tested, and still missing live
modal open/close acceptance. The second target should be the queued Chat
controller check during `meeting-control-map-demo`, because it is also P0 and
validates a real operator workflow without requiring high-risk meeting actions.
