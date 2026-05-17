# Cycle 175 Experience Handoff: Chinese Presenter Meta Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: write only `docs/agent-handoffs/cycle-175-experience.md`

## Sources Read

- `docs/agent-handoffs/cycle-175-demand-analysis.md`
- `docs/agent-handoffs/cycle-175-risk-scan.md`
- `docs/agent-handoffs/cycle-175-technical-scan.md`
- `docs/agent-handoffs/cycle-174-experience.md`
- Current working diff for `src/ai_presenter/runtime/questions.py`
- Current working diff for `tests/unit/test_questions.py`
- `git status --short` and `git diff --stat`

Current workspace context: `.coverage`, `src/ai_presenter/runtime/questions.py`, and `tests/unit/test_questions.py` were already dirty, and the three Cycle175 scan docs were already untracked. Treat all of that as work from other agents. This pass only writes the experience handoff named above.

## Chinese Presenter Meta Need

Cycle174 separated English Presenter expression requests from RingCentralVideo control routing. Cycle175 extends the same user need to Chinese.

Users may ask AiPresenter, in Chinese, to change how the answer is delivered:

- language: `请用中文回答`, `用中文回答`, `请讲中文`
- tone: `请用谨慎的语气回答`, `用友好的语气回答`
- detail and pacing: `请简洁一点`, `请讲慢一点`, `请讲简单一点`
- familiarity: `我是新手`, `我是初学者`, `从基础讲起`

These are Presenter-level requests, not RingCentralVideo UI actions. Pure meta prompts should be answer-only, non-operable, and no-interrupt:

- `entrypoint_id is None`
- `can_operate is False`
- `create_question_interrupt_step(...) is None`
- answer text should acknowledge an answer-style request, but must not claim a persistent language, tone, or familiarity setting changed unless controller or voice state is actually updated and tested

The experience goal is trust during live demos: asking AiPresenter to speak differently must not move the meeting UI.

## Durable Routing Pattern

Keep Presenter meta handling in `src/ai_presenter/runtime/questions.py`, not `packages/ringcentral-video.yaml`. These prompts describe AiPresenter expression, not RingCentralVideo product knowledge, package aliases, or Q&A.

The stable routing shape is:

1. Normalize the prompt with `normalize_question_prompt(...)`.
2. Let explicit safety Q&A win first.
3. Preserve contained localized Q&A before alias and location guards.
4. Detect only high-confidence Presenter meta phrase fragments.
5. For pure meta prompts, return `QuestionResponse(entrypoint_id=None, can_operate=False)`.
6. For mixed prompts, route RingCentralVideo only through Q&A, package aliases, meeting-info location lookup, or entrypoint titles.
7. Skip broad token fallback for Presenter meta prompts.
8. Let `create_question_interrupt_step(...)` be the final gate: no entrypoint or `can_operate=False` means no interrupt.
9. Render with `PresenterVoiceSettings`, but do not let voice language or tone change route choice.

The current diff follows that shape by extending `_PRESENTER_META_REQUEST_FRAGMENTS` with Chinese phrase-level prompts and adding focused pure-meta, mixed-intent, bare safety word, and mojibake tests.

## Contained-QA Lesson

The subtle Cycle175 lesson is that mixed Chinese prompts can contain a complete localized Q&A after a style prefix. Example:

`请用谨慎的语气回答，会议信息里能看到加密状态吗`

If `_match_qa(...)` checks package entrypoint aliases too early, `会议信息` can trigger meeting-info alias/location behavior before the more specific encryption-status Q&A has a chance to answer. That would lose the authored privacy/security answer and return a generic location answer.

The contained-QA pattern fixes this narrowly:

- inspect `package.qa_question_candidates`
- accept a candidate only when `candidate.normalized_question in normalized_question`
- require `candidate.normalized_question != normalized_question`
- require `_is_specific_question_fragment(candidate.normalized_question)`
- run this after explicit safety helpers and before meeting-info location or package alias lookup

That placement preserves localized Q&A when a Presenter style phrase is prefixed, without turning bare aliases into Q&A matches.

## Bare CJK Fragment Risk

Chinese matching must stay phrase-level. Bare CJK fragments are too broad and can steal real RingCentralVideo intents.

Avoid using standalone fragments such as:

- `中文`
- `语气`
- `简洁`
- `慢`
- `新手`
- `说`
- `讲`
- `解释`
- `安全`
- `隐私`
- `状态`
- `确认`

These words can appear in valid meeting-info, encryption/security, chat, participants, recording, notes/transcript, screen-share, invite, leave, and host-control prompts. They should not classify a request as Presenter meta, and they should not activate contained-QA by themselves.

The current source diff adds Chinese safety words to `_BROAD_QA_FRAGMENT_TOKENS`; the experience lesson is to use that as a blocker against over-broad contained-QA matches, not as permission to match those words alone.

Mojibake is also a product risk. Do not add corrupted Chinese variants or encoding repair into routing. Broken text should remain unsupported rather than accidentally becoming a valid Presenter meta request or RingCentralVideo alias.

## RingCentralVideo Knowledge Gained

- `entrypoint_id` identifies a surface; it is not permission to operate.
- `questionPolicy`, `openSteps`, risky wording, and `can_operate` decide whether a route can become a UI action.
- `create_question_interrupt_step(...)` is the final interrupt gate.
- Meeting information is sensitive because it can include meeting ID, meeting link, dial-in, host/account information, encryption, and E2EE details.
- Meeting-info private action prompts should remain answer-only and must not claim to read, copy, share, verify, or expose private values.
- Encryption/security questions belong to meeting-info answer-only behavior, even when the prompt includes style words like `谨慎`, `隐私`, or `中文`.
- Chat and Participants are real controls for location/opening prompts such as `聊天在哪里` or `谁在会议里`, but chat content, participant names, host identity, and private meeting data need answer-only safety boundaries.
- Full screen belongs to Views/layout routing, not Leave, Share, or operating-system full-screen behavior.
- Recording, notes/transcript, screen share, invite, and leave prompts have their own safety boundaries; Presenter style modifiers must not bypass them.
- Package YAML should not absorb Presenter expression requests because that would blur app knowledge with AiPresenter behavior and disturb localization/package diagnostics.

## Reusable Prompts For Next Agents

Implementation continuation prompt:

```text
Continue Cycle175 Chinese Presenter meta routing. Read the Cycle175 handoffs and current diff first. Keep changes limited to runtime question routing and focused tests unless explicitly assigned more. Preserve Q&A-first safety, the contained-QA-before-alias pattern, and pure Presenter meta answer-only behavior. Do not modify RingCentralVideo YAML or persistent voice state.
```

Review prompt:

```text
Review the Cycle175 Chinese Presenter meta guard for false positives. Focus on whether Chinese language, tone, detail, or beginner fragments can steal meeting-info privacy, encryption/security, host controls, recording, notes/transcript, screen-share, invite, leave, chat, participants, network quality, or full-screen routing. Prioritize route regressions and missing tests over style comments.
```

Regression-test prompt:

```text
Add focused regression tests for Chinese Presenter meta overlaps. Separate pure meta prompts from mixed RingCentralVideo prompts. Pure meta prompts should have no entrypoint, no operation, and no interrupt. Mixed prompts with real Q&A, package aliases, meeting-info location, or entrypoint titles should preserve the existing RingCentralVideo route and safety policy.
```

Knowledge-update prompt:

```text
After the Cycle175 implementation is tested and reviewed, update repo-local RingCentral runtime safety guidance. Document that Presenter expression requests are runtime answer-only guards, while RingCentralVideo aliases and Q&A remain package-owned. Do not claim live RingCentral acceptance without dated evidence.
```

## Next-Cycle Candidate Backlog

- Run focused `tests/unit/test_questions.py` verification with `--no-cov`, `-p no:cacheprovider`, `-B`, and `PYTHONDONTWRITEBYTECODE=1` so `.coverage` and cache churn do not expand.
- Review whether the current contained-QA helper can match any overly broad localized Q&A despite `_BROAD_QA_FRAGMENT_TOKENS`.
- Add more Chinese overlap tests for screen share, invite, leave, recording, notes/transcript, chat-content privacy, participant-name privacy, host identity, and encryption/security.
- Add controller/session sentinel tests proving Chinese Presenter meta requests never enqueue `question-answer-demo`.
- Decide separately whether natural-language language or tone requests should ever persist to `PresenterVoiceSettings`; if yes, design controller state mutation and copy that accurately reflects persistence.
- Update `docs/knowledge/ringcentral-video/runtime-safety-routing.md` only after implementation tests and review pass.
- Keep Spanish, Japanese, and broader multilingual Presenter meta prompts as later slices unless there is a concrete prompt set and route-risk test plan.
- Keep package YAML, package counts, localization diagnostics, staging, and commits out of this slice unless a future assignment explicitly owns them.

## Status

Cycle175 experience handoff complete. The key lesson is that Chinese Presenter expression requests need a narrow runtime answer-only guard, while mixed prompts must continue through RingCentralVideo Q&A and explicit routing. No source, tests, package YAML, staging, or commits were performed in this pass.

Changed file path:

- `docs/agent-handoffs/cycle-175-experience.md`
