# Cycle 107 Demand Analysis: Notes/Transcript Route Hardening

## Recommendation

AiPresenter should prefer explicit safety answers or no-match over incidental entrypoint matching for Notes/Transcript action and content prompts.

Keep the good Cycle 106 behavior for location discovery: questions like `Notes and Transcript の場所` and `ノートと文字起こしの場所` may associate with `ringcentral.video.more.notes`, remain `can_operate=False`, and produce no interrupt. Harden the next product slice around prompts that ask AiPresenter to click, start, read, summarize, create, or retrieve Notes/Transcript content. Those prompts should not fall through to unrelated route matching such as `Start meeting`, and they should not receive a generic route answer that sounds like AiPresenter can satisfy the request by opening the panel.

The product demand is a clearer refusal boundary, not broader automation. When the user asks for risky Notes/Transcript work, AiPresenter should answer in plain language: it can show where the panel is, but it will not start notes, start recording/transcription, read visible transcript text, summarize content, or create artifacts unless a future explicitly designed flow adds confirmation, visibility checks, and consent rules.

## Prompt Classes

### Safe Location Prompts

These should continue to route to `ringcentral.video.more.notes` as answer-only location help:

- `Where are Notes and transcript?`
- `Notes and Transcript の場所はどこですか`
- `ノートと文字起こしの場所はどこですか`
- `Where can I find notes and transcript controls?`
- Mixed-language variants that include a location/find intent and the combined panel name.

Desired classification: related entrypoint may be `ringcentral.video.more.notes`; `can_operate=False`; no interrupt step.

### Unsafe Action Prompts

These should prefer an explicit safety answer or no-match instead of incidental matching:

- `Start notes`
- `Start notes をクリックして`
- `Click Start notes`
- `ノートを開始して`
- `文字起こしをオンにして`
- `Also record this meeting をクリックして`

Desired classification: no executable operation; no interrupt step; do not match `ringcentral.develop.video.start` merely because the prompt contains `Start`; do not open the Notes panel as if the action were approved.

### Unsafe Content Prompts

These should prefer an explicit safety answer or no-match:

- `Transcript を要約して`
- `文字起こしを読んで`
- `ノートを読んで`
- `議事録を作って`
- `会議後の文字起こしを見せて`
- `Summarize the transcript`

Desired classification: no operation and no content claim. If AiPresenter has no verified content access, answer that it cannot read or summarize Notes/Transcript content from this route.

### Ambiguous Single-Term Prompts

These should stay conservative:

- `Notes`
- `Transcript`
- `ノート`
- `文字起こし`
- `議事録`

Desired classification: either no-match with a clarification, or answer-only location guidance only when the product intentionally treats the term as a location lookup. Do not make bare terms operable aliases.

## Desired UX

For safe location prompts, AiPresenter should remain helpful and concise:

> Notes and Transcript is the panel for meeting notes and transcript-related controls. I can show where it is, but I will not start notes, recording, or transcription from a question response.

For unsafe action prompts, AiPresenter should identify the boundary without pretending the command succeeded:

> I can point you to the Notes and Transcript panel, but I cannot click Start notes or start recording/transcription from this request. Starting notes or recording can change meeting state and may require consent or meeting policy confirmation.

For unsafe content prompts, AiPresenter should not imply transcript access:

> I cannot read or summarize meeting notes or transcript content from the route map. I can only explain where the Notes and Transcript panel is unless a confirmed content-access flow is added.

For incidental unrelated matches, prefer no-match or the Notes/Transcript safety answer over a wrong route answer. The specific failure to avoid is `Start notes` or `Start notes をクリックして` associating with `ringcentral.develop.video.start` / Start meeting because of the word `Start`.

## Product Rationale

Question routing is now used as both user help and a possible source of interrupt steps. Cycle 105 and Cycle 106 correctly made Notes answer-only, which prevents actual operation. The remaining issue is conversational trust: a user who asks AiPresenter to start notes, read a transcript, or summarize a transcript should not receive an unrelated `Start meeting` answer or a generic `Notes and transcript: Open the Notes and Transcript side panel` answer. Even when non-operable, those responses make the assistant look like it understood the wrong intent.

The safer product behavior is intent-aware abstention. Location questions are valid discovery requests. Action and content requests are different product surfaces with higher consent, privacy, and meeting-state risk.

## Out Of Scope

- Do not change code as part of this demand-analysis handoff.
- Do not add new Notes/Transcript aliases in this cycle.
- Do not make `Start notes`, transcript reading, transcript summarization, recording, or post-meeting artifact retrieval operable.
- Do not remove the existing scripted demo `openSteps` for `ringcentral.video.more.notes`.
- Do not change Cycle 106's two Japanese location aliases.
- Do not broaden this into general multilingual NLU, LLM intent classification, UI Automation changes, content extraction, transcript storage, or post-meeting artifact integrations.
- Do not change unrelated routes such as Chat, Recording, Leave, Share, Reactions, or Start meeting except to prevent them from winning Notes/Transcript action/content prompts in a future scoped implementation.

## Acceptance Direction For A Future Implementation

A future hardening slice should prove:

- Location prompts still answer with `ringcentral.video.more.notes`, `can_operate=False`, and no interrupt.
- `Start notes`, `Start notes をクリックして`, and `Click Start notes` do not resolve to `ringcentral.develop.video.start`.
- Notes/Transcript action prompts return a safety answer or no-match and remain non-operable.
- Notes/Transcript content prompts return a safety answer or no-match and remain non-operable.
- Existing Japanese location alias counts and answer-only behavior remain stable unless a separate demand analysis changes them.

## Handoff Notes

Read-only context checked:

- Cycle 106 committed `146c51a feat: add japanese notes location aliases`.
- `ringcentral.video.more.notes` has `questionPolicy: answerOnly`.
- The Notes route still has demo `openSteps` through More -> Notes and `cleanup: sidePanel`.
- Runtime routing checks Q&A first, then entrypoint aliases, then token-scored entrypoint title/purpose matches.
- Current residual behavior can associate `Start notes` style prompts with Start meeting and `Transcript` content prompts with Notes, while still returning `can_operate=False`.
- `.coverage` was already modified in the worktree and was not touched.
