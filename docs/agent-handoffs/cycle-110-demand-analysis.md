# Cycle 110 Demand Analysis: Cross-Tone Sensitive Prompt Parity

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product Need

Cycle 109 added `careful` as a privacy/safety-aware presenter tone. The next user-facing risk is not that `careful` sounds wrong; it is that a sensitive RingCentral Video prompt might route differently when the operator changes tone. Tone must remain a style layer. It may change phrasing, prefixes, labels, and speech pacing, but it must never change authorization, route matching, or whether AiPresenter creates an interrupt step.

The practical demand is a small regression guard for live demo operators. When they ask about recording, transcripts, meeting links, invite flows, participant names, chat, sharing, or leaving a meeting, switching between normal, support, and careful phrasing should not make a blocked operation look executable or make an answer-only safety prompt become a UI action.

## Scope

Build a focused RingCentral Video question-routing parity matrix for sensitive prompts across selected tones.

In scope:

- English RingCentral Video prompts only for the first cycle, except where an existing localized safety regression is already cheap to include.
- Route and authorization invariants for `answer_question(...)` plus `create_question_interrupt_step(...)`.
- The highest-risk tones: `professional`, `support`, and `careful` through the public `privacy` alias.
- A small warm-tone sentinel set if implementation cost is low: `friendly` and `coach`.
- One operable non-sensitive control sentinel so the test proves parity in both blocked and allowed directions.

Out of scope for this cycle:

- Expanding package YAML, Q&A text, aliases, or localization coverage.
- Full all-tones x all-languages golden answer matrices.
- Manual RingCentralVideo validation or live UI interaction.

## Prioritized Prompt Matrix

| Priority | Prompt class | Representative prompt | Expected route | Expected authorization | Why it matters |
| --- | --- | --- | --- | --- | --- |
| P0 | Recording | `how do I handle meeting recording safely?` | `ringcentral.video.more.recording` | `can_operate=False`, no interrupt | Recording changes meeting state and may require participant consent. Tone must not convert explain-only guidance into a click. |
| P0 | Notes/transcript action or content | `Read the transcript` | `None` safety Q&A route | `can_operate=False`, no interrupt | Artifact content and transcript operations are private. They should stay answer-only instead of falling through to the Notes panel. |
| P0 | Meeting info and links | `meeting information` | `ringcentral.video.top.meeting-info` | `can_operate=False`, no interrupt | Meeting IDs, links, dial-in details, and account data are sensitive even when the visible route is known. |
| P0 | Chat and participant content | `Can AiPresenter read meeting messages or participant names?` | `None` privacy Q&A route | `can_operate=False`, no interrupt | Chat text, names, and roles must not become routable just because a tone is friendlier or more helpful. |
| P0 | Leave/end meeting | `leave meeting` | `ringcentral.video.toolbar.leave` | `can_operate=False`, no interrupt | Leaving or ending is destructive. Tone must not weaken confirmation or destructive-action boundaries. |
| P1 | Invite/share people or links | `invite people` | `ringcentral.video.toolbar.invite` | `can_operate=False`, no interrupt | Invite flows expose links, emails, suggestions, and meeting access details. Route identity should remain stable. |
| P1 | Screen share | `share screen` | `ringcentral.video.toolbar.share` | `can_operate=False`, no interrupt | Sharing can expose private screen content and system audio. Tone must not change it into an executable interrupt. |
| P1 | Participants panel lookup | `participants` | `ringcentral.video.toolbar.participants` | `can_operate=False`, no interrupt | The panel is useful to locate, but names/roles and host controls are sensitive. |
| P1 | Host participant controls | `where are host controls for participants` | `None` privacy Q&A route | `can_operate=False`, no interrupt | This catches the Q&A-first path where the right answer is guidance, not a panel open. |
| P2 | Safe operable sentinel | `network quality` | `ringcentral.video.top.network-quality` | `can_operate=True`, interrupt allowed | Prevents the parity guard from only proving blocked behavior; safe controls should also remain safe across tones. |

If one cycle must be even smaller, keep the five P0 rows plus the safe operable sentinel. Add the P1 rows only if they fit without broad helper rewrites.

## Tones To Compare

Minimum required comparison:

- `professional`: current default and baseline.
- `support`: existing recovery-oriented tone that can add helpful wording.
- `privacy`: public alias for canonical `careful`; proves the new careful tone stays style-only through alias normalization.

Recommended small extension:

- `friendly`: catches casual prefix risks such as reassuring language before boundaries.
- `coach`: catches step-by-step guidance pressure around controls that should remain answer-only.

Do not make this an all-tone exhaustive suite in Cycle 110 unless the implementation is table-driven and stays readable. Existing voice metadata tests already cover normalization and rendering for the broader tone catalog.

## Expected Invariant Fields

For each prompt, all compared tones must produce identical values for:

- `QuestionResponse.entrypoint_id`.
- `QuestionResponse.can_operate`.
- Whether `create_question_interrupt_step(package, response)` returns a step.
- If an interrupt step exists, the step target entrypoint id and operation.
- The answer route class: package Q&A vs entrypoint fallback should not drift when that distinction is observable through `entrypoint_id` and interrupt behavior.

Fields that may vary by tone:

- `QuestionResponse.answer_text` wording, prefix, and localized presentation style.
- Voice instruction text, CLI/controller labels, and speech pacing.

Answer text still has safety constraints even though it is not an equality invariant:

- It must not invent meeting IDs, links, names, roles, chat text, transcript content, or shared-screen content.
- It must not imply AiPresenter can start recording, read private content, share the screen, invite people, or leave/end the meeting without the existing explicit request and policy gates.
- Localized authored answers should not receive English prefixes.

## Non-Goals

- Do not change `packages/ringcentral-video.yaml`.
- Do not add new RingCentral aliases, Q&A entries, demo flows, routes, or locator metadata.
- Do not change `questionPolicy`, `_can_operate(...)`, Q&A-first matching, risky-word lists, or interrupt-step creation behavior.
- Do not add a new policy engine, consent workflow, role detector, or manual acceptance process.
- Do not assert exact answer text equality across tones.
- Do not broaden this into full multilingual coverage; use existing localized sentinels only if they are already available and cheap.

## Acceptance Criteria

A Cycle 110 implementation satisfies this demand when:

- A table-driven regression covers the P0 prompt rows across at least `professional`, `support`, and `privacy`.
- The safe operable sentinel proves an allowed route remains allowed across the same tones.
- For every matrix case, `entrypoint_id`, `can_operate`, and interrupt-step presence match the `professional` baseline.
- `privacy` is used in the matrix, not only `careful`, so alias normalization is covered at the product-facing entry point.
- The test suite does not require exact answer text equality across tones.
- No production authorization behavior changes are made to pass the test.
- No package YAML, localization count, Q&A count, or route count changes are introduced.
- Existing Cycle 109 careful-tone behavior remains intact: careful wording may add a boundary-first prefix, but routing and operability do not change.

Nice-to-have if still one-cycle small:

- Include `friendly` and `coach` in the same table.
- Add one localized careful/privacy sentinel that proves authored Chinese or Japanese safety Q&A stays answer-only and avoids English prefixes, without expanding the full matrix.

## Implementation Handoff Notes

- Likely home: `tests/unit/test_questions.py`, using the existing `load_material_package(...)`, `answer_question(...)`, `PresenterVoiceSettings(...)`, and `create_question_interrupt_step(...)` patterns.
- Prefer one readable parametrized matrix over many bespoke tests. Keep expected values in the table so route drift is obvious in review.
- Use the `professional` result as the baseline, then assert each comparison tone matches it. Also assert the baseline expected route for each row so a bad baseline cannot hide drift.
- Include `privacy` as the careful-tone input because Cycle 109 positioned privacy as the most important user-facing alias.
- Keep assertions focused on route identity and authorization. If answer text is checked, use only safety-negative assertions such as no fabricated links or no English prefix in localized text.
- Do not touch production code unless the new regression exposes an existing bug. If it does, document the failing prompt and keep any fix narrowly inside question routing or tone rendering, with no package content changes.
- Useful verification target after implementation: focused `tests/unit/test_questions.py` route-parity tests plus existing Cycle 109 voice tests if any tone metadata changes are made.
