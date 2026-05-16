# Cycle 010 Technical Scan

Date: 2026-05-16

Scope: read-only scan for the next RingCentral Video candidate: a maintainable manual/live acceptance evidence index. Production code was not edited by this sidecar; only this handoff document was created.

Workspace note: the worktree was already dirty when this scan began. Existing modified and untracked files were left untouched. In particular, `docs/runbooks/ringcentral-manual-acceptance.md` and `packages/ringcentral-video.yaml` were inspected as current workspace contents, not as a clean baseline.

## Summary

Cycle 010 should add an evidence index that points to the existing RingCentral Video knowledge docs instead of replacing them. The repository already has the right source-of-truth split:

- `docs/knowledge/ringcentral-video/source-index.md` explains source discipline and says live manual observations are required before a locator or flow is treated as current-build evidence.
- `docs/knowledge/ringcentral-video/observation-log.md` records observed facts, including the Cycle 003 empty-room UIA snapshot.
- `docs/knowledge/ringcentral-video/locator-matrix.md` maps package entrypoint ids to locator type, cleanup, confidence, and verification need.
- `docs/knowledge/ringcentral-video/state-matrix.md` separates state recognition from locator confidence.
- `docs/knowledge/ringcentral-video/privacy-matrix.md` defines what can be explained, clicked, read, or treated as confirmed.
- `docs/knowledge/ringcentral-video/acceptance-runs.md` records actual automated/manual runs and explicitly says a checklist is not evidence until a run is recorded.
- `docs/runbooks/ringcentral-manual-acceptance.md` is the checklist to execute, not the evidence record itself.

The new index should be a navigation and coverage layer: one place where a future agent can answer "what has evidence, what is stale, and what should I validate next?" without rereading every doc.

## Existing Structure To Preserve

Keep these docs authoritative for their current purpose:

- Source taxonomy: `docs/knowledge/ringcentral-video/source-index.md:13` `## Official RingCentral Sources`, `:23` `## Repository-Local Sources`, `:39` `## Source Discipline`, `:46` `## Coverage Implications`.
- Observation details: `docs/knowledge/ringcentral-video/observation-log.md:9` `## Observation Template`, `:35` `## Seed Observations From Repository Evidence`, `:66` `## Live Observations`, `:68` `## 2026-05-16 01:15 +08:00 - Empty-Room UIA Snapshot`, `:95` `## Needed Live Observations`.
- Acceptance evidence: `docs/knowledge/ringcentral-video/acceptance-runs.md:9` `## Automated Baseline Template`, `:27` `## Manual Acceptance Template`, `:56` `## Current Automated Evidence From Cycle 001`, `:72` `## 2026-05-16 - Cycle 002 Automated Baseline`, `:90` `## 2026-05-16 01:15 +08:00 - Cycle 003 Read-Only RingCentral Observation`, `:122` `## 2026-05-16 - Cycle 004 Automated Baseline`, `:137` `## Manual Acceptance Backlog`.
- Locator coverage: `docs/knowledge/ringcentral-video/locator-matrix.md:5` `## Locator Confidence Legend`, `:13` `## Current Entrypoint Matrix`, `:45` `## Locator Risks`, `:55` `## Next Locator Work`.
- State coverage: `docs/knowledge/ringcentral-video/state-matrix.md:9` `## State Coverage`, `:34` `## Missing Or Weak States`, `:56` `## State Policy`.
- Privacy and safety: `docs/knowledge/ringcentral-video/privacy-matrix.md:5` `## Default Policy`, `:9` `## Operation Modes`, `:17` `## Surface Matrix`, `:39` `## Safety In Runtime`, `:46` `## Observation Capture Policy`, `:53` `## Open Policy Questions`.
- Manual procedure: `docs/runbooks/ringcentral-manual-acceptance.md:3` `## Preconditions`, `:11` `## Smoke Checklist`, `:33` `## Real Audio And OpenAI Checklist`, `:46` `## Controller Acceptance Checklist`.

Do not duplicate raw UIA labels, private values, or screenshot details into the evidence index. Link to observation and acceptance records, then summarize status and next action.

## Package IDs To Index

The current package shape is `27` operation entrypoints, `4` demo flows, `51` demo flow steps, `21` explainers, and `3` QA entries in `packages/ringcentral-video.yaml`.

Index every `operationEntrypoints` id from `packages/ringcentral-video.yaml:10` through `:443`, because these are the units that locator confidence and executable acceptance attach to:

- Launch/app shell: `ringcentral.develop.video.tab`, `ringcentral.develop.video.start`.
- Meeting overview/top bar: `ringcentral.video.overview`, `ringcentral.video.top.meeting-info`, `ringcentral.video.top.network-quality`, `ringcentral.video.top.views`, `ringcentral.video.top.report-issue`.
- Empty-room and toolbar controls: `ringcentral.video.main.add-coworkers`, `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video`, `ringcentral.video.toolbar.video-menu`, `ringcentral.video.toolbar.share`, `ringcentral.video.toolbar.invite`, `ringcentral.video.toolbar.participants`, `ringcentral.video.toolbar.chat`, `ringcentral.video.toolbar.react`, `ringcentral.video.toolbar.raise-hand`, `ringcentral.video.toolbar.more`, `ringcentral.video.toolbar.leave`.
- Settings/background routes: `ringcentral.video.settings.video`, `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.background`, `ringcentral.video.more.settings`.
- More-menu routes: `ringcentral.video.more.recording`, `ringcentral.video.more.notes`.

Index the demo flow ids from `packages/ringcentral-video.yaml:448` through `:1006` separately from entrypoint ids:

- `vbg-blur-demo`
- `meeting-basics-demo`
- `meeting-controls-tour`
- `meeting-control-map-demo`

The runbook uses `meeting-control-map-demo` as the primary smoke/controller flow, so it deserves a flow-level row that summarizes whether the constituent entrypoint rows are currently accepted, stale, explain-only, or blocked.

## Evidence Index Format

Recommended future file: `docs/knowledge/ringcentral-video/evidence-index.md`.

Use stable evidence ids and keep the raw evidence in existing docs. A simple id scheme is enough:

- `RCV-EVID-001` for repository/test baselines.
- `RCV-OBS-YYYYMMDD-NN` for live observations.
- `RCV-MAN-YYYYMMDD-NN` for manual click/audio/controller acceptance runs.

Suggested sections:

1. `## Evidence Records`
   - Columns: `Evidence ID`, `Type`, `Source`, `Environment`, `Scope`, `Result`, `Privacy Class`, `Freshness`.
   - `Source` should link to sections such as `acceptance-runs.md` Cycle 003/Cycle 004 or `observation-log.md` Empty-Room UIA Snapshot.
   - `Environment` should be short but enough to judge staleness: app build, locale, DPI, window bounds, meeting scenario.

2. `## Entrypoint Coverage`
   - Columns: `Entrypoint ID`, `Package Source`, `Locator Row`, `State Prereq`, `Privacy Surface`, `Evidence IDs`, `Acceptance Status`, `Open Risk`, `Next Validation`.
   - `Entrypoint ID` must match `packages/ringcentral-video.yaml` exactly.
   - `Acceptance Status` should use a small vocabulary: `repo-tested`, `live-observed`, `manual-click-passed`, `manual-click-failed`, `explain-only`, `blocked`, `stale`.
   - `Package Source` can use line references as breadcrumbs, but the durable key is the entrypoint id.

3. `## Flow Coverage`
   - Columns: `Flow ID`, `Entrypoints Used`, `Current Evidence`, `Weakest Link`, `Safe To Run Dry`, `Safe To Run Live`, `Next Validation`.
   - The live-safety answer should depend on the weakest entrypoint in the flow, not on whether the flow loads.

4. `## Runbook Mapping`
   - Columns: `Runbook Check ID`, `Runbook Section`, `Check Summary`, `Evidence IDs`, `Last Result`, `Next Run Notes`.
   - Because the runbook checklist items do not have stable item anchors today, define index-local ids such as `RUN-SMOKE-001`, `RUN-AUDIO-001`, and `RUN-CTRL-001`. Keep the section heading as the source link.

5. `## Risk Queue`
   - Columns: `Risk ID`, `Affected IDs`, `Evidence Gap`, `Privacy Constraint`, `Priority`, `Suggested Validation`.
   - This prevents the index from becoming just a pass/fail table; it should also drive the next manual target.

Avoid using line numbers as the permanent join key. They are useful breadcrumbs in a handoff, but the evidence index should join on package ids, evidence ids, runbook check ids, and exact section names.

## Current Evidence To Seed

Seed rows should point to these existing records:

- `acceptance-runs.md:56` Cycle 001 automated baseline: full tests, ruff, mypy, controller dry run.
- `acceptance-runs.md:72` Cycle 002 automated baseline: six knowledge docs present and full test suite, but no live RingCentral acceptance.
- `acceptance-runs.md:90` Cycle 003 read-only observation: RingCentral Video `26.2.20.355`, `en-US`, 100% DPI, bounds `(500, 196, 1420, 836)`, empty-room state, UIA/metadata only, no screenshots or clicks.
- `acceptance-runs.md:122` Cycle 004 automated baseline: package route changed for `ringcentral.video.main.add-coworkers`, tests passed, but no live click or modal validation.
- `observation-log.md:68` Empty-Room UIA Snapshot: observed `Add coworkers`, toolbar labels, and `More` occurrence order for one exact build/window/DPI/scenario.
- `locator-matrix.md:24` `ringcentral.video.main.add-coworkers`: now a UIA button route but still low repo confidence until modal open/close is manually accepted.
- `cycle-004-review.md` recommended next validation: click `ringcentral.video.main.add-coworkers` through the package executor path and validate `cleanup=modal` without reading invite links or private suggestions.
- `cycle-009-summary.md:64` Cycle 010 candidate: build an evidence index that connects locator rows, manual checklist items, observed UIA labels, and unresolved risks.

## Unresolved Locator And Acceptance Risks

Highest-priority risks for the evidence index to expose:

- Top-bar coordinate routes: `ringcentral.video.top.meeting-info`, `ringcentral.video.top.network-quality`, `ringcentral.video.top.views`, and `ringcentral.video.top.report-issue` still depend on window geometry and DPI.
- `ringcentral.video.top.report-issue` has modal cleanup risk because Escape was previously unreliable.
- `ringcentral.video.main.add-coworkers` has observed UIA evidence and a package route, but no live click, Invite modal open, or modal close acceptance.
- `More` occurrence order is overloaded across `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video-menu`, `ringcentral.video.toolbar.more`, `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.notes`, `ringcentral.video.more.background`, and `ringcentral.video.more.settings`.
- The Cycle 003 `More` order is valid only for empty-room, `en-US`, 100% DPI, bounds `(500, 196, 1420, 836)`.
- `ringcentral.video.more.notes` needs a layout-variant decision: direct toolbar Notes vs nested More item vs UIA `onconf.controls.NOTES`.
- Settings routes need evidence for last-selected panel behavior and close path.
- Side-panel cleanup still depends on runtime cleanup behavior and hard-coded fallback points; Chat, Participants, and Notes need live close-path acceptance.
- Share picker should be opened but final Share must not be clicked unless explicitly confirmed; the index should distinguish picker-open acceptance from content-sharing acceptance.
- Reactions and Raise hand are meeting-visible signals; acceptance must include no-send or cleanup proof, especially lowering hand after demonstration.
- `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave` are explain-only by design. Do not add executable acceptance status unless a confirmation workflow exists first.
- Adapter and locators assume English UIA labels. Chinese narration and aliases exist, but localized RingCentral UI labels are not accepted evidence.
- Current live evidence covers an empty-room state only. One-person, two-plus participants, host/moderator, prejoin, sharing active, recording active, localized UI, fullscreen, narrow window, and non-100% DPI remain unaccepted.
- Real audio/OpenAI and controller visual behavior are checklist items, not fresh acceptance records, until a dated manual run is appended to `acceptance-runs.md`.

## Suggested First Slice

For the first evidence-index implementation, keep the scope small:

1. Create `docs/knowledge/ringcentral-video/evidence-index.md`.
2. Add `Evidence Records` rows for Cycle 001, Cycle 002, Cycle 003, and Cycle 004.
3. Add `Entrypoint Coverage` rows for all 27 entrypoint ids, using `locator-matrix.md` status and existing evidence ids.
4. Add `Flow Coverage` rows for the 4 flow ids, with `meeting-control-map-demo` marked as dry-run covered but not fully live-click accepted.
5. Add `Risk Queue` rows for Add coworkers modal validation, top-bar coordinates, More occurrence order, Notes variant, side-panel cleanup, settings close path, localized UIA labels, and real audio/OpenAI acceptance.

Do not update `packages/ringcentral-video.yaml` in the index cycle unless the user explicitly expands the task. The index should make evidence gaps visible before changing routes or confidence.

## Lightweight Validation Commands

For a docs-only evidence index:

```powershell
Test-Path -LiteralPath 'docs\knowledge\ringcentral-video\evidence-index.md'
rg -n "Evidence Records|Entrypoint Coverage|Flow Coverage|Runbook Mapping|Risk Queue|ringcentral.video.main.add-coworkers|meeting-control-map-demo" docs\knowledge\ringcentral-video\evidence-index.md
.\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; p=load_material_package(Path('packages/ringcentral-video.yaml')); print(f'entrypoints={len(p.operation_entrypoints)} flows={len(p.demo_flows)} qa={len(p.qa)}')"
.\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; p=load_material_package(Path('packages/ringcentral-video.yaml')); text=Path('docs/knowledge/ringcentral-video/evidence-index.md').read_text(encoding='utf-8'); print('missing_entrypoint_ids=', sorted(e.id for e in p.operation_entrypoints if e.id not in text)); print('missing_flow_ids=', sorted(f.id for f in p.demo_flows if f.id not in text))"
git diff --check -- docs\knowledge\ringcentral-video\evidence-index.md docs\agent-handoffs\cycle-010-technical-scan.md
```

For an optional no-live-app smoke check, reuse the existing runbook commands:

```powershell
.\.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run
.\.venv\Scripts\ai-presenter controller --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run
```

For live acceptance, do not treat `doctor`, dry runs, or UIA observation as manual click acceptance. A live run should append a dated record to `acceptance-runs.md` and link that record from the index.

## Commands Used

```powershell
Get-Content -LiteralPath 'C:\Users\rcadmin\.codex\superpowers\skills\using-superpowers\SKILL.md'
Get-Content -LiteralPath 'C:\Users\rcadmin\.codex\superpowers\skills\verification-before-completion\SKILL.md'
rg --files docs/knowledge/ringcentral-video docs/agent-handoffs | Sort-Object
Get-ChildItem -LiteralPath 'docs' -Force | Select-Object Name,Mode
git status --short
rg -n "^#{1,6} |RCV-|RCVID-|Acceptance|Evidence|locator|Locator|risk|Risk|TODO|unresolved|manual|Manual|privacy|Privacy|state|State" docs/knowledge/ringcentral-video docs/runbooks/ringcentral-manual-acceptance.md docs/agent-handoffs/cycle-000-ringcentral-knowledge.md docs/agent-handoffs/cycle-008-technical-scan.md docs/agent-handoffs/cycle-009-technical-scan.md docs/agent-handoffs/cycle-009-demand-analysis.md docs/agent-handoffs/cycle-009-implementation.md docs/agent-handoffs/cycle-009-review.md docs/agent-handoffs/cycle-009-summary.md
Get-Content -LiteralPath 'packages\ringcentral-video.yaml'
Get-Content -LiteralPath 'docs\runbooks\ringcentral-manual-acceptance.md'
Get-Content -LiteralPath 'docs\agent-handoffs\cycle-009-technical-scan.md'
Get-Content -LiteralPath 'docs\agent-handoffs\cycle-009-summary.md'
Get-Content -LiteralPath 'docs\agent-handoffs\cycle-000-ringcentral-knowledge.md'
Get-Content -LiteralPath 'docs\agent-handoffs\cycle-008-technical-scan.md'
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\acceptance-runs.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\locator-matrix.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\state-matrix.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\observation-log.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\privacy-matrix.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\source-index.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\runbooks\ringcentral-manual-acceptance.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
rg -n "RingCentral|ringcentral|acceptance|Acceptance|locator|evidence|Cycle 010|manual|Manual" docs/agent-handoffs
rg -n "^(operationEntrypoints:|demoFlows:|explainers:|qa:|manualControls:)|^- id:|^  [A-Za-z].*:|^appId:|^appName:|^version:|^profileIds:" packages\ringcentral-video.yaml
$raw = Get-Content -Encoding UTF8 -LiteralPath 'packages\ringcentral-video.yaml'; $sections = @{}; for ($i=0; $i -lt $raw.Count; $i++) { if ($raw[$i] -match '^operationEntrypoints:') { $sections.operation = $i }; if ($raw[$i] -match '^demoFlows:') { $sections.flows = $i }; if ($raw[$i] -match '^explainers:') { $sections.explainers = $i }; if ($raw[$i] -match '^qa:') { $sections.qa = $i }; if ($raw[$i] -match '^manualControls:') { $sections.manual = $i } }; $entrypoints = ($raw[$sections.operation..($sections.flows-1)] | Select-String -Pattern '^- id:' | Measure-Object).Count; $flows = ($raw[$sections.flows..($sections.explainers-1)] | Select-String -Pattern '^- id:' | Measure-Object).Count; $flowSteps = ($raw[$sections.flows..($sections.explainers-1)] | Select-String -Pattern '^  - id:' | Measure-Object).Count; $explainers = ($raw[$sections.explainers..($sections.qa-1)] | Select-String -Pattern '^  [A-Za-z].*:' | Measure-Object).Count; $qa = ($raw[$sections.qa..($sections.manual-1)] | Select-String -Pattern '^- question:' | Measure-Object).Count; "entrypoints=$entrypoints flows=$flows flow_steps=$flowSteps explainers=$explainers qa=$qa lines=$($raw.Count)"
rg -n "action: clickWindowRelative|action: clickWindowControl|cleanup:|openSteps: \[\]|alternateTargets:|occurrence:|xFromRight:|x: '|y: '" packages\ringcentral-video.yaml
Test-Path -LiteralPath 'docs\agent-handoffs\cycle-010-technical-scan.md'
Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-004-implementation.md'
Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-004-review.md'
Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-004-summary.md'
Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-006-summary.md'
Test-Path -LiteralPath 'docs\agent-handoffs\cycle-010-technical-scan.md'
rg -n "Evidence Index Format|Unresolved Locator And Acceptance Risks|Lightweight Validation Commands|Commands Used" docs\agent-handoffs\cycle-010-technical-scan.md
$matches = Select-String -Path 'docs\agent-handoffs\cycle-010-technical-scan.md' -Pattern '[ \t]+$'; if ($matches) { $matches; exit 1 } else { 'no trailing whitespace' }
$bytes = [System.IO.File]::ReadAllBytes('docs\agent-handoffs\cycle-010-technical-scan.md'); if ($bytes | Where-Object { $_ -gt 127 }) { 'non-ascii bytes found'; exit 1 } else { 'ascii only' }
git diff --check -- docs\agent-handoffs\cycle-010-technical-scan.md
git status --short -- docs\agent-handoffs\cycle-010-technical-scan.md
```

Non-shell tool used: `apply_patch` to create only `docs/agent-handoffs/cycle-010-technical-scan.md`.
