# Cycle 111 Technical Scan: RingCentral Video Knowledge Consolidation

Date: 2026-05-16
Scope: documentation-only scan. This handoff proposes a minimal slice and does not implement it.

## Current Docs Inventory

Knowledge package docs currently split responsibilities cleanly:

| File | Current role | Scan note |
| --- | --- | --- |
| `docs/knowledge/ringcentral-video/source-index.md` | Source taxonomy for official, repo-local, and evidence docs. | Currently modified in the worktree by another agent to link `runtime-safety-routing.md` and add a runtime safety-routing coverage bullet. Preserve that work if accepted. |
| `docs/knowledge/ringcentral-video/evidence-index.md` | Navigation layer for entrypoint evidence, flow coverage, risk queue, and validation targets. | Currently modified in the worktree by another agent to list `runtime-safety-routing.md` as a primary source. |
| `docs/knowledge/ringcentral-video/runtime-safety-routing.md` | New untracked consolidation note. | Already contains the right consolidation shape: runtime anchors, sensitive surface rules, tone-as-style-only invariant, count expectations, verification commands, and cycle anchors. |
| `docs/knowledge/ringcentral-video/privacy-matrix.md` | Surface-level privacy and safety policy. | Already covers meeting info, notes/transcript, recording, chat, participants, invite, share, leave/end, host/security, and post-meeting artifacts. Do not duplicate detailed runtime mechanics here. |
| `docs/knowledge/ringcentral-video/validation-checklist-index.md` | Procedure for safe manual validation and evidence upgrade rules. | Keep focused on live/manual validation. Runtime route/tone lessons belong in the new consolidation note. |
| `docs/knowledge/ringcentral-video/acceptance-runs.md` | Dated automated/manual acceptance records. | No change for this slice; the proposed consolidation is not live evidence. |
| `docs/knowledge/ringcentral-video/locator-matrix.md` | Locator confidence and route mechanics. | No change unless live/manual locator evidence changes. |
| `docs/knowledge/ringcentral-video/state-matrix.md` | State extraction and missing-state policy. | No change unless UI/state evidence changes. |
| `docs/knowledge/ringcentral-video/observation-log.md` | Read-only/live observations. | No change; this slice does not add observations. |

Recent handoffs that should be consolidated into durable docs:

| Cycle | Durable lesson |
| --- | --- |
| Cycle 104 | Japanese recording action/consent/status/artifact prompts must be Q&A-first and non-operable; location-only recording aliases are safe because recording has no `openSteps`. |
| Cycle 105 | `questionPolicy: answerOnly` separates question answers from scripted demo operation for sensitive but executable informational entrypoints. |
| Cycle 106 | Japanese Notes/Transcript location aliases are acceptable only after the Notes entrypoint is answer-only for questions. |
| Cycle 107 | English/Japanese Notes/Transcript action and content prompts should prefer safety Q&A over incidental entrypoint matching, while location lookups stay helpful. |
| Cycle 108 | Chinese Notes/Transcript hardening should use subject/action-content/location gates, not YAML aliases for private-content intent. |
| Cycle 109 | `careful` tone and aliases such as `privacy`, `safety`, and `compliance` are style choices, not policy engines. |
| Cycle 110 | Sensitive RingCentral question routing must be invariant across selected tones; compare route tuple and interrupt presence, not full answer prose. |

Useful commit anchors from the current branch:

- `394fba0` - Japanese recording safety routing.
- `adcc876` - `questionPolicy: answerOnly`.
- `146c51a` - Japanese Notes/Transcript location aliases.
- `64d7f31` - Notes/Transcript action/content route hardening.
- `1a0d358` - Chinese Notes/Transcript route hardening.
- `35a34dd` - careful presenter tone.
- `f45ea46` - cross-tone sensitive route-parity guard.

## Proposed File Changes

Recommended minimal slice:

1. Create or adopt `docs/knowledge/ringcentral-video/runtime-safety-routing.md`.
   - This file already exists in the working tree as untracked work from another agent.
   - Treat it as the single durable home for recent runtime safety, routing, and tone lessons.
   - Do not create a second consolidation doc.

2. Update `docs/knowledge/ringcentral-video/source-index.md`.
   - Add `runtime-safety-routing.md` to repository-local sources.
   - Add one coverage implication that points future alias, Q&A, route, and tone work to the consolidation note.
   - The current worktree already contains this exact shape.

3. Update `docs/knowledge/ringcentral-video/evidence-index.md`.
   - Add `runtime-safety-routing.md` to the primary source list.
   - Avoid broader evidence table churn because this slice adds guidance, not new acceptance evidence.

No production code, package YAML, tests, runbooks, locator docs, state docs, privacy policy rows, or acceptance records should change for this slice.

## Proposed Outline

For `runtime-safety-routing.md`, keep the outline compact and maintenance-oriented:

1. Purpose and invariant
   - Question routing can identify controls or safety Q&A.
   - Operation permission is separate.
   - Tone and language may change phrasing, not safety.

2. Current runtime anchors
   - Package aliases: discoverable controls only.
   - `runtime.questions`: Q&A-first, then entrypoint matching.
   - `_can_operate(...)`: `entrypoint_id` is not permission.
   - `create_question_interrupt_step(...)`: requires route plus `can_operate=True`.
   - `runtime.voice`: tone applies after route and eligibility.
   - Diagnostics: alias/Q&A overlap and substring reports are tripwires.

3. Sensitive surface rules
   - Notes/Transcript.
   - Recording.
   - Meeting information.
   - Chat, Participants, Invite, Share.
   - Leave, End, Host, Security.

4. Tone is style-only
   - `careful` plus aliases.
   - Allowed effects: prefixes, instructions, labels, pacing.
   - Forbidden effects: route, `can_operate`, `questionPolicy`, Q&A-first matching, interrupts, aliases, Q&A, demo flow, locators.

5. Localization and counts
   - Record current expected entrypoint, alias, Q&A, localization, and doctor signals.
   - Say count drift is a review trigger unless the cycle explicitly changes YAML.

6. Verification commands
   - Full checks for routing/package/tone changes.
   - Focused sentinels for tone parity, Chinese Notes/Transcript safety routing, and voice metadata.

7. Recent cycle anchors
   - Link cycles 108-110 directly in the table.
   - Consider adding cycles 104-107 too, since they are the foundation for recording, `answerOnly`, and Notes/Transcript hardening.

8. Maintenance checklist
   - Alias vs intent decision.
   - Check privacy/locator/validation docs before operation changes.
   - Protect localized authored answers.
   - Run route-parity tests before tone changes.
   - Record dated acceptance before promoting live evidence.

## Verification Plan

Docs-only required checks:

```powershell
git status --short --untracked-files=all -- docs\knowledge\ringcentral-video docs\agent-handoffs\cycle-111-technical-scan.md
git diff --check -- docs\knowledge\ringcentral-video\source-index.md docs\knowledge\ringcentral-video\evidence-index.md docs\agent-handoffs\cycle-111-technical-scan.md
Select-String -LiteralPath docs\knowledge\ringcentral-video\runtime-safety-routing.md -Pattern 'TODO|TBD'
Select-String -LiteralPath docs\knowledge\ringcentral-video\source-index.md,docs\knowledge\ringcentral-video\evidence-index.md -Pattern 'runtime-safety-routing.md'
```

Optional sanity checks only if the implementer wants to validate the commands cited by the doc:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant -q -o addopts=""
.\.venv\Scripts\python.exe -m pytest tests\unit\test_voice.py -q -o addopts=""
```

Do not require the optional tests for a pure docs-only slice. If tests are run, keep coverage disabled to avoid additional `.coverage` churn.

## Scope Risks

- There is active work by another agent: `.coverage` is dirty, `source-index.md` and `evidence-index.md` are modified, and `runtime-safety-routing.md` is untracked. Coordinate before staging or rewriting those files.
- The new consolidation note should not become a competing source of truth for privacy policy or live acceptance. Keep policy in `privacy-matrix.md` and dated evidence in `acceptance-runs.md`.
- Current counts can go stale quickly after package YAML changes. Phrase them as expected signals for the current package, not permanent product facts.
- Avoid broadening the slice into tests or runtime changes. The consolidation is meant to document lessons from cycles 104-110, not introduce new behavior.
- CJK text may render poorly in PowerShell output. Do not "fix" Japanese or Chinese package strings while doing this documentation slice unless a separate encoding task approves it.
- Tone guidance must stay narrow: `careful`, `privacy`, `safety`, `safe`, `guarded`, and `compliance` are wording aliases only and must not imply verified consent, legal compliance, role authorization, or visible-context validation.
