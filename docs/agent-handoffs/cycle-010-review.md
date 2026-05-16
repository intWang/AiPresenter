# Cycle 010 Review: RingCentral Evidence Index

Date: 2026-05-16
Role: read-only review
Write scope: this file only

## Scope

Reviewed only the RingCentral Video evidence index documentation cycle:

- `docs/superpowers/specs/2026-05-16-ringcentral-evidence-index-design.md`
- `docs/superpowers/plans/2026-05-16-ringcentral-evidence-index.md`
- `docs/agent-handoffs/cycle-010-demand-analysis.md`
- `docs/agent-handoffs/cycle-010-technical-scan.md`
- `docs/agent-handoffs/cycle-010-implementation.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/source-index.md`

No production code or existing docs were edited. The worktree was already dirty and contained unrelated modified/untracked files; those were treated as other agents' work and left untouched.

## Review Result

Conditional pass. The evidence index covers the current package entrypoints and flows, keeps live acceptance claims appropriately conservative, and preserves the high-risk controls as blocked or explain-only. I found two documentation/verification follow-ups.

## Findings

### P2: Source index still lets the runbook read like current evidence

`docs/knowledge/ringcentral-video/source-index.md:25` labels the third repository-local column `Current Evidence`, and `docs/knowledge/ringcentral-video/source-index.md:33` lists `docs/runbooks/ringcentral-manual-acceptance.md` as `Manual acceptance` with smoke/audio/controller/check items as the evidence value. That conflicts with the stronger rule in `docs/knowledge/ringcentral-video/acceptance-runs.md:7` that a runbook checklist is not acceptance evidence until a run is recorded, and with `docs/knowledge/ringcentral-video/evidence-index.md:188`, which says to keep checklist items separate from dated acceptance evidence.

The evidence index itself mostly handles this correctly, but the changed `source-index.md` row can mislead a future agent into citing checklist coverage as evidence. Suggested doc-only fix: rename the role to `Manual acceptance checklist` and make the evidence cell say procedure only, with acceptance evidence recorded in `acceptance-runs.md`.

### P3: Section verification command is too loose

`docs/agent-handoffs/cycle-010-implementation.md:47` records an `rg` alternation for `Evidence Records|Entrypoint Coverage|Flow Coverage|Runbook Mapping|Risk Queue|...`, and `docs/agent-handoffs/cycle-010-implementation.md:48` says all expected sections and key targets were found. The actual index heading is `## Entry Point Evidence Table` at `docs/knowledge/ringcentral-video/evidence-index.md:57`, while `Entrypoint Coverage` is absent from the index. Because the `rg` pattern is a single alternation, it can pass when any one expected token matches.

The stronger table coverage check passed, so this is not a coverage blocker. Suggested verification improvement: assert required headings individually, or use a small Python check that reports missing headings separately from missing entrypoint/flow rows.

## Checked Criteria

- Current package shape: 27 operation entrypoints, 4 demo flows, 21 explainers, and 3 QA entries.
- Entrypoint coverage: passed. The entrypoint table contains 27 rows, with no missing or extra current package IDs.
- Flow coverage: passed. The flow table contains all 4 current flow IDs, with no missing or extra current package IDs.
- Live acceptance overclaim: passed. No entrypoint evidence row uses `Accepted`, and `docs/knowledge/ringcentral-video/evidence-index.md:30` states that no executable route is fully accepted for live operation.
- Add coworkers status: passed. `docs/knowledge/ringcentral-video/evidence-index.md:68` keeps `ringcentral.video.main.add-coworkers` at `Observed`, and lines 47 and 160 call out live click/modal cleanup as missing.
- Recording and leave: passed. `docs/knowledge/ringcentral-video/evidence-index.md:83`, `:87`, and `:166` keep recording and leave/end blocked or explain-only pending confirmation/role/privacy policy.
- Runbook/checklist semantics: mostly passed in the evidence index, with the source-index wording issue above.
- Privacy constraints: passed. The evidence index points sensitive surfaces to the privacy matrix, and `docs/knowledge/ringcentral-video/privacy-matrix.md:23-36` covers Add coworkers, participants, chat, share, notes/transcript, recording, and leave/end constraints.
- Maintenance rules: passed. `docs/knowledge/ringcentral-video/evidence-index.md:182-188` gives clear update rules for package entrypoints, locator confidence, acceptance runs, privacy policy changes, and checklist separation.
- Validation commands: partially passed. The package ID/table checks are adequate; the section/key-target `rg` check needs the tightening described above.

## Commands Run

```powershell
Get-Content -Raw C:\Users\rcadmin\.codex\superpowers\skills\using-superpowers\SKILL.md
git status --short
Test-Path docs\agent-handoffs\cycle-010-review.md
rg --files -g package.json -g pnpm-workspace.yaml -g package-lock.json -g yarn.lock -g pnpm-lock.yaml -g npm-shrinkwrap.json
rg -n "RingCentral|ringcentral|evidence|source-index|recording|leave|Add coworkers|runbook|checklist|privacy|acceptance|entrypoint|flow" docs\superpowers docs\agent-handoffs docs\knowledge\ringcentral-video
.\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; p=load_material_package(Path('packages/ringcentral-video.yaml')); print(f'entrypoints={len(p.operation_entrypoints)} flows={len(p.demo_flows)} explainers={len(p.explainers)} qa={len(p.qa)}'); print('ENTRYPOINTS'); [print(e.id) for e in p.operation_entrypoints]; print('FLOWS'); [print(f.id) for f in p.demo_flows]"
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\evidence-index.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\source-index.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\superpowers\specs\2026-05-16-ringcentral-evidence-index-design.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\superpowers\plans\2026-05-16-ringcentral-evidence-index.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-010-demand-analysis.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-010-technical-scan.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-010-implementation.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\acceptance-runs.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\knowledge\ringcentral-video\privacy-matrix.md' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
.\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; p=load_material_package(Path('packages/ringcentral-video.yaml')); text=Path('docs/knowledge/ringcentral-video/evidence-index.md').read_text(encoding='utf-8'); print('missing_entrypoint_ids=', sorted(e.id for e in p.operation_entrypoints if e.id not in text)); print('missing_flow_ids=', sorted(f.id for f in p.demo_flows if f.id not in text))"
rg -n "Accepted|Observed|Repo-tested|Backlog|Blocked|live accepted|live operation|Add coworkers|recording|Recording|Leave|leave|runbook|checklist|Privacy|privacy|maintenance|Maintenance" docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\source-index.md docs\agent-handoffs\cycle-010-implementation.md
rg -n "ringcentral\.video\.main\.add-coworkers|ringcentral\.video\.more\.recording|ringcentral\.video\.toolbar\.leave|openSteps: \[\]|action: clickWindowControl|target: Add coworkers|cleanup: modal|canOperate|can_operate|presenterNotes" packages\ringcentral-video.yaml docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\privacy-matrix.md docs\knowledge\ringcentral-video\locator-matrix.md docs\knowledge\ringcentral-video\acceptance-runs.md
Test-Path -LiteralPath 'docs\knowledge\ringcentral-video\evidence-index.md'; Test-Path -LiteralPath 'docs\knowledge\ringcentral-video\locator-matrix.md'; Test-Path -LiteralPath 'docs\knowledge\ringcentral-video\observation-log.md'; Test-Path -LiteralPath 'docs\knowledge\ringcentral-video\privacy-matrix.md'; Test-Path -LiteralPath 'docs\knowledge\ringcentral-video\acceptance-runs.md'; Test-Path -LiteralPath 'docs\runbooks\ringcentral-manual-acceptance.md'
rg -n "TODO|TBD|PLACEHOLDER" docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\source-index.md
.\.venv\Scripts\python -c "from pathlib import Path; import re; from ai_presenter.packages.loader import load_material_package; p=load_material_package(Path('packages/ringcentral-video.yaml')); text=Path('docs/knowledge/ringcentral-video/evidence-index.md').read_text(encoding='utf-8'); entry_section=text.split('## Entry Point Evidence Table',1)[1].split('## Flow Coverage',1)[0]; flow_section=text.split('## Flow Coverage',1)[1].split('## Runbook Mapping',1)[0]; entry_rows=set(re.findall(r'^\| `(ringcentral\.[^`]+)` \|', entry_section, re.M)); flow_rows=set(re.findall(r'^\| `([^`]+-demo)` \|', flow_section, re.M)); print('entry_table_rows=', len(entry_rows)); print('flow_table_rows=', len(flow_rows)); print('missing_entry_table_rows=', sorted(e.id for e in p.operation_entrypoints if e.id not in entry_rows)); print('extra_entry_table_rows=', sorted(entry_rows - {e.id for e in p.operation_entrypoints})); print('missing_flow_table_rows=', sorted(f.id for f in p.demo_flows if f.id not in flow_rows)); print('extra_flow_table_rows=', sorted(flow_rows - {f.id for f in p.demo_flows}))"
rg -n "^## Entrypoint Coverage$|^## Entry Point Evidence Table$|Entrypoint Coverage" docs\knowledge\ringcentral-video\evidence-index.md docs\agent-handoffs\cycle-010-implementation.md docs\agent-handoffs\cycle-010-technical-scan.md
rg -n "docs/runbooks/ringcentral-manual-acceptance.md|Current Evidence|checklist|acceptance evidence|not acceptance evidence" docs\knowledge\ringcentral-video\source-index.md docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\acceptance-runs.md docs\agent-handoffs\cycle-010-implementation.md
git diff --check -- docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\source-index.md docs\agent-handoffs\cycle-010-implementation.md
@'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
p = load_material_package(Path('packages/ringcentral-video.yaml'))
text = Path('docs/knowledge/ringcentral-video/evidence-index.md').read_text(encoding='utf-8')
entry_section = text.split('## Entry Point Evidence Table', 1)[1].split('## Flow Coverage', 1)[0]
flow_section = text.split('## Flow Coverage', 1)[1].split('## Runbook Mapping', 1)[0]
entry_rows = {line.split('`')[1] for line in entry_section.splitlines() if line.startswith('| `ringcentral.')}
flow_rows = {line.split('`')[1] for line in flow_section.splitlines() if line.startswith('| `')}
entry_ids = {entrypoint.id for entrypoint in p.operation_entrypoints}
flow_ids = {flow.id for flow in p.demo_flows}
print('entry_table_rows=', len(entry_rows))
print('flow_table_rows=', len(flow_rows))
print('missing_entry_table_rows=', sorted(entry_ids - entry_rows))
print('extra_entry_table_rows=', sorted(entry_rows - entry_ids))
print('missing_flow_table_rows=', sorted(flow_ids - flow_rows))
print('extra_flow_table_rows=', sorted(flow_rows - flow_ids))
'@ | .\.venv\Scripts\python -
rg -n '\| `[^`]+` \| .* \| `Accepted` \|' docs\knowledge\ringcentral-video\evidence-index.md
rg -n "^## |ringcentral\.video\.more\.recording|ringcentral\.video\.toolbar\.leave|ringcentral\.video\.main\.add-coworkers|Current overall state|Keep checklist items separate" docs\knowledge\ringcentral-video\evidence-index.md
rg -n "RingCentral app/build|Locale|DPI/display scale|Window bounds|Privacy notes|Locator updates needed|Manual validation|Follow-up|checklist is not acceptance evidence" docs\knowledge\ringcentral-video\acceptance-runs.md
rg -n "Invite/Add coworkers|Participants|Chat|Screen share|Notes and transcript|Recording|Leave/end|Observation Capture Policy|can_operate" docs\knowledge\ringcentral-video\privacy-matrix.md
```

Non-shell tool used: `apply_patch` to create only this review file.
