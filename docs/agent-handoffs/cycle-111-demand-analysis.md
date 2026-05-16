# Cycle 111 Demand Analysis: RingCentral Video Safety-Routing Knowledge Consolidation

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product Demand

Cycles 104 through 110 spread important RingCentral Video safety-routing knowledge across demand analyses, implementation handoffs, reviews, tests, and the knowledge package. Future agents now need one compact place to understand the product rule before they touch package YAML or routing code:

- Location discovery is useful and should stay helpful.
- Meeting-state changes and private content access must stay gated.
- Route identity and operation permission are separate decisions.
- Tone can change response style, but not routing, authorization, or interrupt creation.
- Localization work must preserve known counts unless a cycle explicitly changes package data.

The user demand is deep RingCentral Video familiarity, not broader automation. The most useful next slice is a small documentation consolidation that lets maintainers answer "what should happen for Recording, Notes/Transcript, Q&A-first safety routes, careful tone, localization counts, and verification?" without rereading seven recent cycle folders.

## Target Audience

- Future agents planning RingCentral Video package, routing, or localization work.
- Maintainers reviewing changes to `packages/ringcentral-video.yaml`, `src/ai_presenter/runtime/questions.py`, or tone rendering.
- QA reviewers deciding which automated checks and manual acceptance records are needed.
- Documentation maintainers keeping `docs/knowledge/ringcentral-video` coherent.

The document should assume the reader can follow entrypoint IDs and test names, but should not require them to know the full Cycle 104 to 110 history.

## Recommended Knowledge Doc Scope

Recommended one-cycle update: add a compact "Safety Routing Consolidation" section to `docs/knowledge/ringcentral-video/source-index.md`.

Why `source-index.md`:

- It already separates official RingCentral sources from repo-local behavior.
- It already has a "Coverage Implications" section that mentions question policy, Notes/Transcript, localization, and diagnostics.
- It is the first navigation document a future agent is likely to read before opening runtime code or package YAML.

Keep the update small. Add one table plus short bullets, then link to existing docs instead of duplicating them:

| Topic | Consolidate In Source Index | Link Out For Detail |
| --- | --- | --- |
| Notes/Transcript | Location questions may identify `ringcentral.video.more.notes`; action/content prompts should use safety Q&A or no-match. | `privacy-matrix.md`, `state-matrix.md`, Cycle 105 to 108 handoffs. |
| Recording | Location/help is answer-only; start/stop/status/artifact/consent prompts must stay Q&A-first and non-operable. | `privacy-matrix.md`, Cycle 104 handoffs. |
| Q&A-first routing | Safety matchers should win before entrypoint fallback when the user intent is action, consent, status, artifact, or content access. | `src/ai_presenter/runtime/questions.py`, relevant unit tests. |
| Tone | `careful` and aliases such as `privacy` are style-only. Tone may affect wording, not route or permission. | Cycle 109 and 110 handoffs. |
| Localization counts | Record current count baselines and say count changes need explicit package-scope justification. | Localization report, doctor output, package tests. |
| Verification | Route changes require focused routing tests; package-data changes require localization and doctor checks; live route claims require `acceptance-runs.md`. | `acceptance-runs.md`, `validation-checklist-index.md`, `evidence-index.md`. |

If the source-index section grows beyond one screen, create an adjacent `docs/knowledge/ringcentral-video/safety-routing.md` and add only a pointer from `source-index.md`. For one cycle, prefer the source-index-only version.

## Must-Capture Facts

### Notes/Transcript

- `ringcentral.video.more.notes` has `questionPolicy: answerOnly` for question responses.
- Scripted demo `openSteps` may still open the Notes and Transcript panel, but question responses must return `can_operate=False` and create no interrupt step.
- Safe location prompts can identify the Notes/Transcript surface. This includes English, Chinese, and Japanese location phrasing covered by recent cycles.
- Action prompts such as starting notes, clicking `Start notes`, starting transcription, or clicking recording-related controls from the panel should not be treated as ordinary location lookup.
- Content prompts such as reading, summarizing, copying, exporting, saving, creating minutes, or showing transcript/notes content should not associate with `ringcentral.video.more.notes`.
- Cycle 107 hardened English and Japanese Notes/Transcript action/content prompts. Cycle 108 extended the same boundary to Chinese.
- Location intent should be excluded before safety action/content matching so prompts like "where are Notes and Transcript?" keep working.

### Recording

- `ringcentral.video.more.recording` remains explain-only/non-operable and has no executable `openSteps`.
- Japanese Recording location aliases were added in Cycle 104, but Recording action, consent, status, and artifact prompts route through Q&A-first safety handling.
- Recording should not be started, stopped, status-asserted, or summarized from question routing.
- Recording can affect everyone in a meeting and may require host role, organization policy, participant consent, and visible context.
- Recording prompt handling should not be allowed to fall through to unrelated executable routes such as Participants.

### Q&A-First Routing And Operation Gates

- Runtime question handling should prefer authored safety Q&A or no-match for high-risk intent before entrypoint title/alias fallback.
- `entrypoint_id` is not the same as permission to operate. Some responses can identify an entrypoint while remaining answer-only.
- `create_question_interrupt_step(...)` should only produce a step when the response has an entrypoint and `can_operate=True`.
- Sensitive but useful informational routes include Meeting information and Notes/Transcript. Their answer-only behavior must remain separate from scripted demo execution.
- Avoid broad aliases for sensitive surfaces. Bare words like Notes, Transcript, Recording, More, participant names, or artifacts can blur discovery, state change, and private content access.

### Tone As Style Only

- Cycle 109 added the canonical `careful` tone with aliases including `privacy`, `safety`, `safe`, `guarded`, and `compliance`.
- `careful` should frame safety-sensitive answers with calm boundary wording. It is not a legal or compliance engine.
- Tone may change deterministic prefixes, labels, voice instructions, and pacing.
- Tone must not change Q&A matching, `entrypoint_id`, `can_operate`, risky-word gates, or interrupt-step creation.
- Cycle 110 added parity coverage so sensitive RingCentral prompts route the same across `professional`, `friendly`, `coach`, `support`, and `privacy`.
- Localized authored answers should keep their authored language; a tone prefix must not inject English into Chinese or Japanese package-owned Q&A.

### Localization Counts And Package Baselines

Current baseline to preserve unless a future package-data cycle explicitly changes it:

- Japanese `questionAliases.ja`: `13/27` entrypoints and `34` aliases.
- Package-owned aliases: `87`.
- Q&A prompts: `71`.
- Demo localization baseline remains complete for the RingCentral Video demo set: `51/51` demo steps.
- Q&A localization baseline remains complete for the safety set: `12/12` localized Q&A questions and `12/12` localized Q&A answers.
- Source-index coverage already notes Chinese and Japanese Q&A localization and Japanese coverage for the virtual background, meeting basics, meeting controls tour, and meeting control map demo flows.

The consolidation should say that docs-only work must not change these counts. Any future YAML alias or Q&A expansion should update expected counts, localization-report expectations, doctor expectations, and the handoff notes in the same cycle.

### Verification And Evidence

- Documentation consolidation can be verified with file review, `git diff --check`, and requirement checklist review.
- Runtime routing changes need focused `tests/unit/test_questions.py` coverage around response entrypoint, `can_operate`, and interrupt-step creation.
- Tone changes need voice metadata/rendering tests plus RingCentral route-parity sentinels.
- Package YAML/localization changes need material package tests, localization report, and doctor checks.
- Live RingCentral route claims require dated evidence in `docs/knowledge/ringcentral-video/acceptance-runs.md`; automated tests or dry runs do not promote a route to accepted live operation.
- Manual evidence must avoid reading or storing meeting IDs, links, participant names, chat text, transcript/notes content, invite suggestions, recordings, or account details.

## Non-Goals

- Do not edit production code, tests, package YAML, profiles, runbooks, live evidence, locator docs, state docs, or privacy policy docs in Cycle 111.
- Do not add aliases, Q&A prompts, tone choices, runtime matchers, locators, or demo flows as part of this analysis.
- Do not broaden Recording, Notes/Transcript, Leave, host controls, or post-meeting artifacts into executable behavior.
- Do not create a full policy engine or consent workflow.
- Do not duplicate the full `privacy-matrix.md`, `state-matrix.md`, or `evidence-index.md`.
- Do not claim live RingCentral acceptance from repository tests, dry-run output, or old read-only UIA observations.
- Do not update count baselines unless a future implementation actually changes package data.

## Acceptance Criteria

A future one-cycle documentation implementation satisfies this demand when:

- `docs/knowledge/ringcentral-video/source-index.md` gains a compact safety-routing consolidation section, or a new adjacent safety-routing doc is added with a source-index pointer if the table would become too large.
- The update covers Notes/Transcript, Recording, Q&A-first routing, tone-as-style-only, localization counts, and verification.
- The update names the key entrypoints: `ringcentral.video.more.notes`, `ringcentral.video.more.recording`, and `ringcentral.video.top.meeting-info`; it should also mention high-impact adjacent surfaces such as Leave, Participants, Chat, Invite, and Share where useful.
- The update preserves the distinction between location discovery, action/state-change requests, and private content/artifact requests.
- The update records the current package count baselines: Japanese aliases `13/27` entrypoints and `34` aliases, package-owned aliases `87`, Q&A prompts `71`, demo localization `51/51`, and localized Q&A `12/12` questions and `12/12` answers.
- The update says `careful`/`privacy` tone is style-only and must not change route identity, authorization, or interrupt-step creation.
- The update links to `privacy-matrix.md`, `state-matrix.md`, `evidence-index.md`, `validation-checklist-index.md`, and `acceptance-runs.md` instead of duplicating their full content.
- The implementation diff is documentation-only and does not change runtime behavior, package YAML, tests, or count expectations.
- Verification includes a requirement checklist against this handoff and a whitespace/link sanity check such as `git diff --check -- docs/knowledge/ringcentral-video/source-index.md`.

## Handoff Notes

- Recommended edit location: after `Source Discipline` or near `Coverage Implications` in `docs/knowledge/ringcentral-video/source-index.md`.
- Keep the voice concise. Future agents need a map, not another long cycle narrative.
- Use stable phrasing: "location discovery", "action/content prompts", "answer-only", "Q&A-first", "style-only tone", and "dated acceptance evidence".
- Avoid adding new policy claims that are not already supported by recent handoffs or knowledge docs.
- If the implementation owner decides to create `safety-routing.md`, make it short and link it from the source index, evidence index, and privacy matrix only if those files need navigation help.
- Do not stage or touch `.coverage`; it was already dirty at the start of this handoff.
