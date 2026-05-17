# Cycle 176 Technical Development: Presenter Meta Routing Knowledge

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle176 technical-development handoff

## Scope And Boundary

This handoff documents the current Cycle176 documentation-contract diff. Per
assignment, this pass writes only:

- `docs/agent-handoffs/cycle-176-technical-development.md`

No source, test, RingCentralVideo knowledge doc, package YAML, staging, or commit
changes were made by this handoff. The workspace already contained the Cycle176
knowledge-doc and docs-contract test edits, the Cycle176 scan handoffs, and a
dirty `.coverage` file before this doc was written.

## Problem

Cycles 174 and 175 established a runtime safety boundary for Presenter expression
requests. Prompts about answer language, tone, pacing, detail level, or beginner
guidance are AiPresenter meta requests, not RingCentral Video control requests.
Pure meta prompts should answer safely without selecting a RingCentralVideo
entrypoint, allowing operation, or creating an interrupt step.

The missing Cycle176 piece was durable knowledge. Future agents needed the
runtime safety guide to make the boundary explicit so they do not move Presenter
meta phrases into `packages/ringcentral-video.yaml`, describe the guard as
persistent voice-state mutation, or treat local routing tests as live
RingCentral acceptance evidence.

## Implementation Summary

The current Cycle176 diff updates
`docs/knowledge/ringcentral-video/runtime-safety-routing.md` with a new section:

- `Presenter Meta Requests Are Runtime Answer-Only`

That section documents the stable routing contract:

- Presenter expression requests are runtime answer-only guards.
- Q&A safety matching still runs before Presenter meta matching.
- Contained authored Q&A must still win before package aliases when a style
  prefix is added to a sensitive RingCentral prompt.
- Pure meta requests must not produce a RingCentralVideo entrypoint, operation
  permission, or `create_question_interrupt_step(...)`.
- Mixed prompts can still preserve explicit RingCentralVideo intent through
  authored Q&A, package aliases, meeting-info location lookup, or entrypoint
  titles.
- Broad entrypoint token fallback is skipped while Presenter meta matching is
  active.
- The guard does not persist language, tone, pacing, detail, or guidance-depth
  settings.
- Presenter meta phrases do not belong in RingCentralVideo package YAML,
  aliases, Q&A, localized titles, or package facts.
- Phrase-level fragments are required, especially for Chinese and other CJK
  prompts; broad words and mojibake should not become supported routes.
- Repo tests prove local routing boundaries only, not live RingCentral
  acceptance.

The same doc's focused sentinel checklist now includes a Presenter meta
maintenance reminder covering answer-only/no-interrupt wording, no persistent
voice-state mutation claim, package YAML ownership separation, and no promotion
of repo tests to live evidence.

`tests/unit/test_material_packages.py` extends
`test_ringcentral_knowledge_docs_preserve_evidence_boundaries` with literal
docs-contract assertions for the new boundary.

## Files Touched

Current Cycle176 implementation diff before this handoff:

- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` - adds the
  Presenter meta runtime answer-only documentation section and checklist item.
- `tests/unit/test_material_packages.py` - adds docs-contract assertions that
  lock the runtime answer-only, no-entrypoint, and no-persistent-state wording.
- `.coverage` - already dirty in the working tree; unrelated to this handoff.

Cycle176 scan handoffs already present and read by this pass:

- `docs/agent-handoffs/cycle-176-demand-analysis.md`
- `docs/agent-handoffs/cycle-176-risk-scan.md`
- `docs/agent-handoffs/cycle-176-technical-scan.md`

This pass changed only:

- `docs/agent-handoffs/cycle-176-technical-development.md`

## Exact Doc Contract

`tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries`
now requires `runtime-safety-routing.md` to contain these exact fragments:

```text
Presenter expression requests are runtime answer-only guards, not RingCentralVideo package aliases or Q&A.
Pure meta requests are answer-only
should not produce a RingCentralVideo entrypoint
Do not claim persistent language or tone state changes
```

The knowledge doc also now includes this exact focused-sentinel checklist item:

```text
Before documenting Presenter meta routing, verify the wording says answer-only/no-interrupt, does not claim persistent voice-state mutation, keeps package YAML ownership separate, and does not promote repo tests to live RingCentral evidence.
```

Keep these phrases stable unless a later cycle intentionally updates the
docs-contract test and the knowledge doc together.

## Verification

Focused verification run by this handoff:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes
```

Result:

```text
..                                                                       [100%]
2 passed in 0.29s
```

Whitespace check run by this handoff:

```powershell
git diff --check -- docs\knowledge\ringcentral-video\runtime-safety-routing.md tests\unit\test_material_packages.py
```

Result:

```text
Exit code 0. No whitespace errors reported.
Warnings only: Git reported LF will be replaced by CRLF the next time it touches the two edited files.
```

No runtime question-routing suite, diagnostics suite, package count suite, or
live RingCentral acceptance run was executed by this handoff.

## Known Limits And Future Work

- This is a documentation-contract slice. It does not change runtime question
  routing, package YAML, aliases, Q&A, localization, diagnostics, or counts.
- The Presenter meta guard still returns an answer-only response. It does not
  persist language, tone, pacing, detail, or guidance-depth settings unless a
  future controller/session state slice implements and tests that behavior.
- The documentation intentionally avoids copying full fragment lists or recent
  handoff prompt matrices, because those can drift.
- Future multilingual expansion should keep fragments phrase-level and add
  negative route-stealing tests for meeting-info privacy, encryption/security,
  host controls, notes/transcript, recording, chat, participants, share, invite,
  leave, and full-screen behavior.
- Mojibake remains unsupported; do not add mojibake variants as Presenter meta
  phrases or RingCentralVideo aliases.
- Repo-local tests are not live RingCentral acceptance evidence. A dated live
  acceptance run is still required before promoting any live route claim.
- `.coverage` remains dirty in the working tree and should not be staged unless
  a later owner intentionally refreshes coverage.

## Status

Status: Cycle176 technical-development handoff complete. The current
documentation-contract diff is documented, focused docs sentinels passed, and no
source, tests, or knowledge docs were modified by this handoff.

Changed file path:

- `docs/agent-handoffs/cycle-176-technical-development.md`
