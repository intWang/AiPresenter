# Cycle 010 Demand Analysis: RingCentral Acceptance Evidence Index

Date: 2026-05-16
Role: demand-analysis sidecar
Write scope: this file only

## Read Scope

Reviewed local repo evidence only. No production code was modified.

- `docs/agent-handoffs/cycle-004-demand-analysis.md`
- `docs/agent-handoffs/cycle-004-review.md`
- `docs/agent-handoffs/cycle-004-summary.md`
- `docs/agent-handoffs/cycle-008-demand-analysis.md`
- `docs/agent-handoffs/cycle-008-summary.md`
- `docs/agent-handoffs/cycle-009-demand-analysis.md`
- `docs/agent-handoffs/cycle-009-review.md`
- `docs/agent-handoffs/cycle-009-summary.md`
- `docs/agent-handoffs/cycle-009-technical-scan.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`

The working tree was already dirty before this handoff. Existing modified and
untracked files were treated as other agents' work and were not reverted or
overwritten. This sidecar created only `docs/agent-handoffs/cycle-010-demand-analysis.md`.

## Current Context

The user wants deep familiarity with RingCentral Video and a material/knowledge
package that can be trusted during a live demo. The repo now has a real knowledge
set under `docs/knowledge/ringcentral-video`: source discipline, locator matrix,
state matrix, observation log, privacy/safety matrix, and acceptance run log.

Cycle 003 captured the first live read-only RingCentral Video observation for
build `26.2.20.355`, `en-US`, 100% DPI, empty-room state, and window bounds
`(500, 196, 1420, 836)`. Cycle 004 changed the `Add coworkers` route from a
coordinate click to a UIA `Add coworkers` button route and protected it with a
unit test. The docs correctly keep that route at low confidence because no live
click or modal cleanup validation has been recorded.

Cycles 005-009 improved controller trust, localized/package-owned Q&A, privacy-
safe telemetry, package runtime indexing, and language/tone selection. Those
were useful product increments, but they also widened the evidence surface. A
future agent now has to read several docs to answer a simple question: "What
RingCentral control is safe and worthwhile to validate next?"

## User-Facing Need

The user-facing need is operational confidence, not another broad knowledge dump.
When AiPresenter is used against RingCentral Video, the operator needs to know:

- which controls are safe enough for scripted demo operation;
- which controls are explanation-only because of privacy, role, or meeting impact;
- which locators have live dated evidence versus only package or unit-test evidence;
- which manual acceptance checks prove a route, cleanup, and privacy boundary;
- which validation target will most improve demo reliability next.

Without an evidence index, the knowledge package can still be accurate in pieces
but hard to act on. The next agent may validate a low-value target, miss a known
privacy risk, or overclaim that a package route is accepted when it is only
unit-tested.

## Recommended Next Increment

Create an acceptance evidence index for RingCentral Video. Recommended location:

- `docs/knowledge/ringcentral-video/evidence-index.md`

This should be a documentation-only or documentation-first increment. It should
connect existing knowledge rows rather than redesign package schema or runtime
behavior. The index should make evidence status scannable per entrypoint, state,
or validation target.

Recommended initial columns:

| Column | Purpose |
| --- | --- |
| `Target` | Entrypoint, state, or workflow being evaluated. |
| `Package route` | Link or ID for the executable or explain-only package route. |
| `Locator status` | Current locator type and confidence from `locator-matrix.md`. |
| `Observed evidence` | Dated observation-log or acceptance-run reference, including build/DPI/window state when available. |
| `Acceptance status` | Not run, observed-only, automated baseline, manual pass, manual fail, or accepted with risks. |
| `Privacy/risk note` | Summary from `privacy-matrix.md`; include whether confirmation is required. |
| `Manual check` | Related checklist item from `ringcentral-manual-acceptance.md` or a proposed focused check. |
| `Next validation target` | The smallest useful live/manual action to close the evidence gap. |
| `Owner notes` | Residual uncertainty, layout variants, or cleanup concerns. |

Keep the index compact enough that a future agent can scan it quickly. It should
link back to the source documents instead of copying every observation verbatim.

## What The Evidence Index Should Answer

The index should answer these questions directly:

1. Can this RingCentral control be clicked in a scripted demo today?
2. If yes, what proves the locator and cleanup path work on a real build?
3. If no, is the blocker locator confidence, privacy policy, role permission,
   missing state observation, or missing confirmation workflow?
4. Does the latest evidence come from a live observation, a unit test, official
   docs, a package route, or a manual acceptance run?
5. Which build, locale, DPI, window bounds, role, participant count, and meeting
   state does the evidence apply to?
6. Does the validation require a screenshot, and if so what privacy review or
   redaction rule applies?
7. What is the next smallest validation action that improves user confidence?

The most important distinction is between "observed", "implemented", and
"accepted". For example, `ringcentral.video.main.add-coworkers` is implemented
as a UIA route and backed by a unit test, but it is not live accepted until a
manual run confirms the click opens the invite modal and `cleanup=modal` closes
it without reading invite links or private suggestions.

## Suggested Acceptance Criteria

1. Index coverage:
   - Every row in `locator-matrix.md` appears in the evidence index or is
     explicitly grouped under an explain-only/non-executable section.
   - Every executable package route has an acceptance status.
   - Every explain-only route states why it is explain-only or what policy would
     be required before operation.

2. Evidence traceability:
   - Each index row references the relevant source docs: locator matrix,
     observation log, acceptance runs, privacy matrix, runbook checklist, or
     package entrypoint.
   - The index never treats official RingCentral documentation as locator
     evidence.
   - Dated live evidence includes build, locale, DPI/display scale, window
     bounds, meeting scenario, role when known, and participant count when known.

3. Acceptance semantics:
   - The index distinguishes repository/unit-test coverage from live manual
     acceptance.
   - "Accepted" requires route behavior plus cleanup behavior plus privacy-safe
     evidence capture.
   - Observed-only evidence can raise locator confidence, but should not imply a
     click path is safe unless a click and cleanup were actually run.

4. Privacy and risk:
   - Sensitive surfaces such as Invite/Add coworkers, Participants, Chat, Share,
     Notes, Recording, Settings, Security, and Leave carry privacy or
     confirmation notes.
   - The index records that real-meeting operation needs explicit user intent
     even when a control is safe inside a scripted demo.
   - Screenshot needs are called out only when UIA/window metadata is
     insufficient, with redaction expectations.

5. Next validation targeting:
   - The index identifies a ranked next validation queue, not just a passive
     status table.
   - The first recommended live target should be narrow and high value:
     validate `ringcentral.video.main.add-coworkers` click plus modal cleanup,
     because Cycle 003 observed the UIA button and Cycle 004 implemented the
     route but manual acceptance is still missing.
   - Additional targets should emphasize route brittleness: top-bar coordinate
     routes, `More` occurrence order, Notes direct-vs-nested variants, modal and
     side-panel cleanup, and participant/layout variants.

6. Maintenance:
   - Add a short "how to update this index" note that tells future agents to add
     an observation or acceptance run first, then update the index.
   - Do not require production code changes for the first index.
   - Do not change package locators or confidence levels unless the same cycle
     also records the supporting evidence.

## Priority Validation Targets

Recommended first targets for the index's initial ranked queue:

1. `ringcentral.video.main.add-coworkers`
   - Why: implemented as UIA route and unit-tested, but live click/modal cleanup
     is still unaccepted.
   - Evidence to collect: sanitized UIA snapshot, package executor click, invite
     modal opened, modal cleanup closed it, no invite links or suggestions read.

2. `More` occurrence order
   - Why: audio menu, video menu, overflow More, background/settings, and notes
     routes depend on occurrence ordering that was observed only in one empty
     room layout.
   - Evidence to collect: UIA bounds/order for empty room, one participant,
     two-plus participants, and narrow or fullscreen layout if available.

3. Top-bar coordinate routes
   - Why: meeting info, network quality, views, and report issue still depend on
     coordinates and window geometry.
   - Evidence to collect: window bounds, DPI, panel/dialog open behavior, and
     Escape/modal cleanup behavior.

4. Chat, Participants, Invite, Share cleanup
   - Why: these are core demo controls with privacy-sensitive surfaces.
   - Evidence to collect: open/close behavior only; avoid chat text, participant
     names, invite links, shared content, and private suggestions.

5. Notes and transcript variants
   - Why: docs already note uncertainty between direct toolbar Notes, nested
     More Notes, and `onconf.controls.NOTES`.
   - Evidence to collect: variant-specific UIA labels and whether the surface is
     side-panel, settings, or host/role dependent.

## Risks

- Evidence overclaim: a unit test can prove package shape, but not live RingCentral
  behavior. The index must avoid turning repository confidence into live
  acceptance.
- Stale evidence: RingCentral UI changes, locale, DPI, window bounds, participant
  count, and role can all invalidate locator assumptions.
- Privacy leakage: acceptance work can accidentally capture participant names,
  chat text, invite links, meeting IDs, emails, or shared content. UIA and window
  metadata should remain the default evidence source.
- Screenshot creep: screenshots are sometimes useful for layout variants, but
  they need explicit privacy review and redaction rules before being stored.
- False safety transfer: a control that is safe in a scripted demo is not
  automatically safe in a real meeting. The index should keep scripted-demo and
  real-meeting-confirmed action semantics separate.
- Maintenance drift: if package routes, locator matrix rows, observation logs,
  and acceptance runs can drift independently, the index may become misleading.
  The update rule should require source evidence first, index summary second.
- Scope creep: this cycle should not become a host-controls, confirmation-policy,
  or locator-refactor cycle unless coordination explicitly asks for that.

## Out Of Scope

- No production code changes.
- No package route changes.
- No new RingCentral entrypoints.
- No new confirmation workflow.
- No new screenshots unless separately approved by a validation cycle.
- No claim that `Add coworkers` or any other route is live accepted before a
  dated acceptance run records route and cleanup behavior.

## Commands Used

```powershell
Get-Content -LiteralPath C:\Users\rcadmin\.codex\superpowers\skills\using-superpowers\SKILL.md
Get-Content -LiteralPath C:\Users\rcadmin\.codex\superpowers\skills\writing-plans\SKILL.md
Get-Content -LiteralPath C:\Users\rcadmin\.codex\superpowers\skills\verification-before-completion\SKILL.md
Get-Content -LiteralPath C:\Users\rcadmin\.codex\superpowers\skills\brainstorming\SKILL.md
git status --short
rg --files docs
Get-ChildItem -LiteralPath docs\agent-handoffs -Force | Select-Object Name,Length,LastWriteTime
Get-ChildItem -LiteralPath docs\knowledge\ringcentral-video -Recurse -Force | Select-Object FullName,Length,LastWriteTime
Get-Content -LiteralPath docs\agent-handoffs\cycle-009-demand-analysis.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-009-technical-scan.md
Get-Content -LiteralPath docs\knowledge\ringcentral-video\locator-matrix.md
Get-Content -LiteralPath docs\knowledge\ringcentral-video\observation-log.md
Get-Content -LiteralPath docs\knowledge\ringcentral-video\acceptance-runs.md
Get-Content -LiteralPath docs\knowledge\ringcentral-video\privacy-matrix.md
Get-Content -LiteralPath docs\knowledge\ringcentral-video\source-index.md
Get-Content -LiteralPath docs\knowledge\ringcentral-video\state-matrix.md
Get-Content -LiteralPath docs\runbooks\ringcentral-manual-acceptance.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-008-demand-analysis.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-008-summary.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-004-demand-analysis.md
rg -n "evidence index|acceptance evidence|locator|observation|acceptance-runs|privacy|risk|next validation|manual acceptance|Add coworkers" docs packages\ringcentral-video.yaml tests\unit\test_material_packages.py
Get-Content -LiteralPath docs\agent-handoffs\cycle-009-summary.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-009-review.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-004-summary.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-004-review.md
Test-Path -LiteralPath docs\agent-handoffs\cycle-010-demand-analysis.md
rg -n "ringcentral.video.main.add-coworkers|clickWindowControl|cleanup: modal|action: clickWindowControl|target: Add coworkers|locator|confidence|privacy|presenterNotes|operationEntrypoints:|demoFlows:|qa:" packages\ringcentral-video.yaml tests\unit\test_material_packages.py docs\knowledge\ringcentral-video docs\runbooks\ringcentral-manual-acceptance.md
Get-Content -LiteralPath tests\unit\test_material_packages.py
Test-Path -LiteralPath docs\agent-handoffs\cycle-010-demand-analysis.md
git diff -- docs\agent-handoffs\cycle-010-demand-analysis.md
git status --short
rg -n "TODO|TBD|production code|Write scope|Commands Used" docs\agent-handoffs\cycle-010-demand-analysis.md
git ls-files --others --exclude-standard docs\agent-handoffs\cycle-010-demand-analysis.md
Get-Item -LiteralPath docs\agent-handoffs\cycle-010-demand-analysis.md | Select-Object FullName,Length,LastWriteTime
```
