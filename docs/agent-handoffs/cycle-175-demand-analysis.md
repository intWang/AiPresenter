# Cycle 175 Demand Analysis: Chinese Presenter Meta-Request Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle175 demand-analysis handoff

## Scope And Boundary

This pass only writes this handoff:

- `docs/agent-handoffs/cycle-175-demand-analysis.md`

No source, test, YAML, coverage, staging, or commit changes were made. The working tree already had `.coverage` dirty before this handoff and should continue to treat that as unrelated existing work.

## Sources Read

- `docs/agent-handoffs/cycle-174-experience.md`
- `docs/agent-handoffs/cycle-174-demand-analysis.md`
- `docs/agent-handoffs/cycle-174-technical-development.md`
- `docs/agent-handoffs/cycle-174-test-review.md`
- `docs/agent-handoffs/cycle-174-followup-test-review.md`
- `docs/agent-handoffs/cycle-174-risk-scan.md`
- `docs/agent-handoffs/cycle-174-technical-scan.md`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`
- Focused portions of `tests/unit/test_questions.py`
- Focused aliases/Q&A in `packages/ringcentral-video.yaml`

## User Need

After Cycle174, English Presenter meta-requests such as `Answer in Chinese`, `Switch to careful tone`, `Be more concise`, and `I am new to RingCentral Video` are separated from RingCentralVideo control routing. The next user-facing gap is the same intent expressed directly in Chinese.

Users may type Chinese requests to change AiPresenter's expression, not the RingCentral meeting UI:

- language: ask the Presenter to answer in Chinese or English
- tone: ask for a careful, warmer, friendlier, or more professional tone
- detail: ask for a shorter, simpler, slower, or more detailed explanation
- familiarity: say they are new to RingCentral Video or already familiar with it

Those prompts should be answer-only, non-operable, and no-interrupt. They should not accidentally route to Chat, Participants, More, Video settings, Meeting information, or Views just because they contain product/control words.

## Recommended Slice

Extend the existing Presenter meta-request guard to a small set of high-confidence Chinese prompts for language, tone, detail, and familiarity, while preserving the Cycle174 safety ordering:

1. Existing Q&A safety routing still wins first.
2. Pure Chinese Presenter meta-requests return `QuestionResponse(entrypoint_id=None, can_operate=False)`.
3. Mixed prompts keep RingCentralVideo routing only when the product intent is explicit enough for Q&A, a package alias, a meeting-info location lookup, or an entrypoint title.
4. Broad token fallback remains skipped for meta prompts.
5. No RingCentralVideo YAML, voice state persistence, controller UI, or package diagnostic count changes.

This is the best next optimization because Cycle174 already established the route boundary in English and left localized Presenter meta-requests as the clear residual risk. The implementation should be small, testable, and valuable without changing live RingCentral behavior.

## Exact Candidate Prompts

Recommended positive pure-meta prompts:

- `请用中文回答`
- `用中文回答`
- `请用英文回答`
- `用英文回答`
- `请讲中文`
- `请说英文`
- `用更谨慎的语气回答`
- `请用谨慎一点的语气`
- `语气温和一点`
- `语气友好一点`
- `请更专业一点`
- `请讲简单一点`
- `简单说一下`
- `请简洁一点`
- `说短一点`
- `请详细一点`
- `讲慢一点`
- `我是 RingCentral Video 新手`
- `我是新手，请讲基础一点`
- `我不熟悉 RingCentral Video`
- `我很熟悉 RingCentral Video，请跳过基础`
- `我懂 RingCentral Video，简洁一点`

Recommended mixed-intent prompts that must preserve existing RingCentralVideo behavior:

- `请简洁一点，会议号在哪里`
- `用更谨慎的语气回答：能读出会议号吗`
- `请用中文回答，会议链接在哪里`
- `语气温和一点，可以复制会议链接吗`
- `请简单说，怎么管理参会人`
- `用更专业的语气回答，主持人怎么管理参会者`
- `请简洁一点，聊天在哪里`
- `请讲慢一点，谁在会议里`
- `用中文解释 full screen 在哪里`
- `请简洁一点，go full screen`

Recommended negative controls that must remain ordinary RingCentralVideo lookups:

- `聊天在哪里`
- `谁在会议里`
- `会议号在哪里`
- `会议笔记在哪里`
- `记录会议`
- `网络质量`
- `怎么离开会议`
- `full screen`
- `go full screen`

## Acceptance Criteria

Pure Chinese Presenter meta-request prompts satisfy all of the following:

- `response.entrypoint_id is None`
- `response.can_operate is False`
- `create_question_interrupt_step(package, response) is None`
- answer text starts with the existing Presenter meta framing or an equivalent localized Presenter-settings framing
- answer text does not use RingCentral control prefixes such as `Chat:`, `Participants:`, `Meeting information:`, `More actions:`, `More video settings:`, `View layout menu:`, `Network quality:`, or `Reactions:`
- answer text does not claim that language, tone, detail level, or familiarity was persistently changed unless this slice also implements and tests real state mutation

Mixed Chinese Presenter meta prompts satisfy the Cycle174 boundary:

- meeting ID/link read/copy/share prompts still use meeting-info privacy Q&A and remain answer-only with no interrupt
- meeting-info location prompts such as `会议号在哪里` and `会议链接在哪里` still route to `ringcentral.video.top.meeting-info` with `can_operate=False`
- host/participant management safety prompts still return host-controls guidance and do not operate Participants
- plain `聊天在哪里` and `谁在会议里` continue to route to Chat and Participants respectively
- full-screen prompts such as `go full screen` continue to route to `ringcentral.video.top.views` and remain operable when already covered by existing aliases
- language/tone/detail words do not change route choice, `entrypoint_id`, `can_operate`, or interrupt creation for existing safety Q&A

Suggested focused tests:

- extend `test_presenter_meta_requests_do_not_route_to_ringcentral_controls` or add a Chinese-specific parametrized test for the pure prompts above
- extend `test_presenter_meta_modifiers_do_not_steal_ringcentral_intents` with the mixed Chinese prompts above
- keep or add negative-control assertions for `聊天在哪里`, `谁在会议里`, `会议号在哪里`, `记录会议`, and `go full screen`

Suggested verification command for the implementation cycle:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_chinese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_ringcentral_full_screen_questions_route_to_view_layout
```

Before staging in any future implementation cycle:

```powershell
git diff --check
git status --short
git diff --cached --name-status
```

## Non-Goals

- Do not implement persistent natural-language voice or tone setting changes.
- Do not add controller UI, CLI flags, or selector behavior.
- Do not modify `packages/ringcentral-video.yaml`.
- Do not expand package aliases, localized titles, localized purposes, or Q&A counts for this need.
- Do not add a broad LLM/NLP intent classifier.
- Do not move voice alias constants into a shared API unless a later slice needs real state mutation.
- Do not add Japanese or Spanish Presenter meta prompts in this slice.
- Do not change meeting-info privacy, encryption/security, recording, notes/transcript, host-controls, chat-content, participant-name, or full-screen safety behavior.
- Do not run live RingCentral acceptance.
- Do not stage or commit `.coverage` or unrelated files.

## Why This Slice Is Valuable

This slice closes the most natural localization gap left by Cycle174. The app already supports Chinese prompts and Chinese answer rendering in many RingCentralVideo paths, so Chinese users are likely to ask expression-level questions in Chinese too. Without the guard, Chinese words like `聊天`, `参会人`, `会议号`, `记录会议`, `中文`, `语气`, `简洁`, or `新手` can sit near real control aliases and make route intent ambiguous.

The value is high because it improves trust during live demos: when a user asks AiPresenter to be clearer, shorter, slower, warmer, or to answer in Chinese, the Presenter should acknowledge that expression preference instead of moving the meeting UI. The cost is low because Cycle174 already created the insertion point, no-interrupt behavior, and mixed-intent pattern. The right implementation is a conservative prompt set plus focused regression tests, not a new routing architecture.

## Status

Cycle175 demand analysis complete. Recommended next optimization slice: extend the Cycle174 Presenter meta-request guard to high-confidence Chinese language, tone, detail, and familiarity prompts while preserving RingCentralVideo Q&A-first and explicit-route behavior.

Changed file path:

- `docs/agent-handoffs/cycle-175-demand-analysis.md`
