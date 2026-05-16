# Cycle 017 Demand Analysis: RingCentral Evidence Structure

Date: 2026-05-16
Role: demand-analysis worker
Write scope: this file only

## Read Scope

Reviewed local repository context only:

- `README.md`
- `packages/ringcentral-video.yaml`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/agent-handoffs/cycle-003-*`
- `docs/agent-handoffs/cycle-004-*`
- `docs/agent-handoffs/cycle-010-*`
- `docs/agent-handoffs/cycle-011-summary.md` through `cycle-016-summary.md`

Existing modified and untracked files were treated as other agents' work. No
production code, tests, package YAML, runbook, or knowledge docs were edited.

## 1. Operator/Developer Problem

RingCentral Video knowledge is now broad enough to be useful, but still hard to
operate from during a live acceptance pass. Cycle 010 added an evidence index,
yet the operator still has to jump between the package YAML, locator matrix,
privacy matrix, runbook checklist, evidence index, and acceptance run log to
answer practical questions:

- Which RingCentral route should be validated next?
- What exact evidence must be collected before a route becomes accepted?
- Which routes are blocked, explain-only, or safe only in a disposable meeting?
- What package entrypoints are still missing live click and cleanup evidence?
- How should a future agent update docs without overclaiming acceptance?

The repeated follow-up from Cycles 014-016 is still manual RingCentral evidence
for the observed `Add coworkers` UIA route. The product demand is not another
large knowledge dump; it is a lightweight structure that helps a human or agent
run a small validation pass, record it, and update the package evidence trail
consistently.

## 2. Proposed Cycle 017 Scope And Out-of-Scope

Recommended scope: create a lightweight RingCentral validation checklist index
that connects evidence gaps to concrete manual acceptance work.

Suggested location:

- `docs/knowledge/ringcentral-video/validation-checklist-index.md`

Minimum useful contents:

- A short update rule: record a dated acceptance run first, then update
  evidence/locator/privacy/index docs.
- A prioritized checklist for P0/P1 routes, starting with
  `ringcentral.video.main.add-coworkers`.
- Per-check rows with package entrypoint ID, current evidence level, source
  links, required setup, exact validation action, cleanup expectation, privacy
  boundary, pass/fail recording target, and post-run docs to update.
- A small "do not execute yet" section for recording, leave/end, and other
  confirmation/role-sensitive controls.
- Cross-link from `docs/knowledge/ringcentral-video/evidence-index.md` or
  `source-index.md` only if the implementing cycle is allowed to edit those
  docs.

Out-of-scope for this cycle:

- Production code or test changes.
- Package route changes in `packages/ringcentral-video.yaml`.
- New live RingCentral clicks unless explicitly requested as an acceptance
  execution cycle.
- New official-source research unless a specific RingCentral feature gap is
  being added.
- Treating automated/unit evidence as live acceptance.
- Expanding risky routes such as Recording or Leave into executable behavior.

## 3. Acceptance Criteria For Docs/Package Evidence

A Cycle 017 implementation should be accepted when:

- The new checklist index has actionable rows for at least:
  `ringcentral.video.main.add-coworkers`, top-bar coordinate routes, toolbar
  `More` occurrence routes, Chat, Participants, Invite, Share, Notes, Background,
  Settings, Recording, and Leave.
- Each row names the package entrypoint or route group, current evidence state,
  privacy constraint, required cleanup mode, and exact place to record the
  result.
- The first priority remains Add coworkers live click plus modal cleanup because
  Cycle 003 observed the UIA button and Cycle 004 implemented the route, but no
  live modal acceptance is recorded.
- The checklist distinguishes `Observed`, `Repo-tested`, `Accepted`, `Blocked`,
  and explain-only status without weakening the Cycle 010 evidence semantics.
- The checklist tells future agents not to read or store chat text, participant
  names, invite links, meeting IDs, shared content, account details, or private
  suggestions.
- Any docs cross-linking is minimal and consistent with existing source/evidence
  index language.
- No package route confidence is raised unless a dated acceptance run or
  observation record is added with build, locale, DPI, window bounds, role,
  meeting scenario, participant count, action, cleanup, and privacy notes.

## 4. Risks/Follow-Ups

- Duplication risk: a new checklist can drift from `evidence-index.md`. Keep it
  procedural and link back to evidence rows instead of copying all evidence.
- Overclaim risk: a passed unit test or checklist item is not live acceptance
  until it is recorded in `acceptance-runs.md`.
- Privacy risk: Invite, Chat, Participants, Share, Notes, Meeting info, Report
  issue, Recording, and Settings can expose sensitive content. UIA/window
  metadata should remain the default evidence source.
- Staleness risk: RingCentral build, locale, DPI, participant count, role, and
  layout can invalidate locators, especially coordinates and `More` occurrence
  order.
- Follow-up: after the checklist exists, run the P0 Add coworkers acceptance in a
  disposable empty-room meeting and update `acceptance-runs.md`,
  `evidence-index.md`, and any locator confidence notes.

## 5. Recommended Implementation Priority

Priority: high for a docs-only Cycle 017.

This is the smallest next increment that improves RingCentral package
maintainability without touching runtime behavior. It converts the existing
evidence index from a status map into an operator-ready validation queue, keeps
manual acceptance privacy-safe, and gives the next implementation or acceptance
worker a precise path to close the highest-value evidence gap.
