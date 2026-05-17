# Cycle 175 Risk Scan: Chinese Presenter Meta Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle175 risk-scan handoff

## Scope And Boundary

This pass reviewed the Cycle174 Presenter meta-request guard and the RingCentralVideo Chinese/localized routing tests. Per assignment, it writes only this file:

- `docs/agent-handoffs/cycle-175-risk-scan.md`

No source, test, YAML, coverage, staging, or commit changes were made. The workspace already had `.coverage` dirty before this scan and it was not touched.

Reviewed anchors:

- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/voice.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_voice.py`
- `docs/agent-handoffs/cycle-174-risk-scan.md`
- `docs/agent-handoffs/cycle-174-technical-development.md`
- `docs/agent-handoffs/cycle-174-test-review.md`
- `docs/agent-handoffs/cycle-174-followup-test-review.md`

## Current Guard Shape

Cycle174 left the guard in a conservative position:

1. `_answer_question(...)` normalizes the prompt with `normalize_question_prompt(...)`.
2. `_match_qa(...)` runs before Presenter meta handling.
3. `_is_presenter_meta_request(...)` checks a narrow English fragment list.
4. If the prompt is meta and has an explicit RingCentralVideo package alias, meeting-info location lookup, or entrypoint title, `_match_explicit_entrypoint(...)` can still preserve the app intent.
5. Pure meta prompts return `QuestionResponse(entrypoint_id=None, can_operate=False)`, so `create_question_interrupt_step(...)` stays `None`.

The Cycle174 follow-up review confirms the earlier P2 was resolved: mixed style modifiers no longer steal meeting-info privacy, encryption, host-control, or full-screen routing.

Cycle175 candidate goal: add high-confidence Chinese Presenter meta prompts, for example language, tone, pacing, detail, and beginner-guidance requests such as `请用中文回答`, `讲慢一点`, `更简洁一点`, `用友好语气`, `用谨慎语气`, and `按新手讲`.

## False-Positive Risk Areas

### 1. Chinese Meeting-Info Privacy

Highest risk. Chinese meeting-info privacy is already covered by tests such as `test_chinese_meeting_link_short_question_uses_privacy_qa` and `test_chinese_meeting_info_action_requests_use_privacy_qa`. The private surface includes meeting ID, meeting link, host information, dial-in, encryption, and E2EE details.

Adding Chinese meta fragments can regress this if broad fragments like `用中文`, `回答`, `说`, `讲`, `简洁`, `隐私`, or `安全` short-circuit before Q&A, or if pure-meta logic treats `请用中文读出会议号` as a language request instead of a private meeting-info action request.

Must preserve:

- `请用中文读出会议号`, `用隐私语气复制会议链接`, and `更简洁地分享会议链接` route to meeting-info privacy Q&A.
- `entrypoint_id == "ringcentral.video.top.meeting-info"`, `can_operate is False`, and no interrupt.
- The answer contains the Chinese private-detail boundary, not the generic `Presenter settings:` answer and not the `Meeting information:` location answer.
- The answer must not contain real or sample URLs, domains, meeting IDs, copied/read/shared completion language, host names, or dial-in values.

### 2. Screen Share, Leave, And Invite Safety

High risk. The Chinese package aliases for `共享屏幕`, `邀请`, `拉人`, `加人`, `离开会议`, `退出会议`, and `结束会议` are real RingCentral controls. Current behavior keeps these non-operable for risky routes by `questionPolicy`, absent `openSteps`, or `_RISKY_ENTRYPOINT_WORDS`.

Chinese meta prompts can create false positives in both directions:

- They can swallow a real control request, returning `Presenter settings:` for `请用中文说明怎么共享屏幕`.
- They can over-route a private action phrase such as `用友好语气发送邀请` into an executable or overly confident invite answer.
- They can confuse `离开会议` with a harmless language/tone request if fragments like `请用中文` or `说明` are too broad.

Must preserve:

- Screen-share safety Q&A remains Q&A-first for content/action requests, with `can_operate is False`.
- Invite and Leave remain non-operable and no-interrupt unless a future explicit confirmation workflow is separately designed.
- Chinese mixed prompts with explicit aliases should not become pure Presenter meta answers unless product explicitly changes the Cycle174 mixed-intent policy.

### 3. Chat, Participants, And Location Controls

Medium-high risk. `聊天在哪里`, `谁在会议里`, `参会者`, and `参会人列表` are package-owned Chinese aliases. Existing tests verify Chinese package aliases work without the legacy alias table.

The false-positive line is thin:

- `请用中文说明聊天在哪里` is a location/control lookup with a style modifier; it should keep the Chat route.
- `用新手语气讲谁在会议里` may be a Participants location/overview request and should not be swallowed by meta matching.
- `请用中文读出聊天消息` and `用简洁语气列出参会者姓名` are private-content requests, not location lookups and not pure meta prompts.

Must preserve:

- Plain and mixed Chinese location prompts for Chat and Participants continue to route to the correct entrypoint.
- Private chat content, participant names, participant roles, host/moderator identity, and private tabs stay answer-only, no-interrupt, and do not route to `ringcentral.video.toolbar.chat` or `ringcentral.video.toolbar.participants` as operable controls.
- Broad Chinese words such as `说`, `讲`, `解释`, `简单`, and `新手` must not by themselves classify a prompt as meta.

### 4. Encryption And Security

High risk. Encryption/security is anchored to meeting-info answer-only behavior, including localized Chinese coverage in `test_ringcentral_localized_encryption_status_questions_are_answer_only`.

The dangerous overlap is `隐私语气`, `谨慎语气`, `安全`, `确认`, and `状态`. These can mean Presenter tone or they can mean meeting security status. Adding Chinese meta support must not cause `用隐私语气确认加密状态` or `用中文告诉我会议安全吗` to bypass encryption/security Q&A.

Must preserve:

- Concrete Chinese encryption/security status prompts route to `ringcentral.video.top.meeting-info`, `can_operate is False`, and no interrupt.
- Bare or vague `安全`, `隐私`, `确认`, `状态` should not newly match encryption/security or Presenter meta by themselves.
- Answers must avoid claims that AiPresenter has verified, changed, copied, shared, enabled, or disabled encryption/security status.

### 5. Mojibake And Normalization

Medium risk but easy to miss. `normalize_question_prompt(...)` currently strips Latin diacritics, case-folds, trims, and preserves CJK. It does not repair mojibake, does not fold halfwidth Japanese, and does not normalize Chinese variants into aliases. Tests already verify mojibake Chinese input like `èŠå¤©` is not treated as a supported alias.

Adding Chinese meta fragments should not add a mojibake repair layer or paste corrupted variants into the matcher. Otherwise broken text could accidentally become an accepted meta request while ordinary corrupted control aliases remain rejected.

Must preserve:

- Mojibake text for Chinese meta prompts does not match `_is_presenter_meta_request(...)`.
- Existing mojibake alias rejection remains unchanged.
- Tests should either save Chinese source as UTF-8 or use `\u` escapes intentionally; do not mix encodings.

## Must-Have Negative Tests

Add these before expanding the Chinese meta fragment list. Suggested home: `tests/unit/test_questions.py`.

### Pure Chinese Meta Smoke

`test_chinese_presenter_meta_prompts_stay_answer_only`

Prompts:

- `请用中文回答`
- `用中文讲`
- `讲慢一点`
- `更简洁一点`
- `用友好语气`
- `用谨慎语气`
- `按新手讲`

Expected:

- `entrypoint_id is None`
- `can_operate is False`
- `create_question_interrupt_step(package, response) is None`
- no RingCentral control prefix such as `Chat panel:`, `Participants panel:`, `Meeting information:`, `Screen sharing:`, `Invite participants:`, or `Leave meeting:`
- do not claim a persistent language/tone state changed unless the implementation actually changes controller voice state

### Meeting-Info Privacy

`test_chinese_meta_modifiers_do_not_steal_meeting_info_privacy`

Prompts:

- `请用中文读出会议号`
- `用隐私语气复制会议链接`
- `更简洁地分享会议链接`
- `请用中文朗读会议信息`

Expected:

- `entrypoint_id == "ringcentral.video.top.meeting-info"`
- `can_operate is False`
- no interrupt
- Chinese privacy answer is returned, not `Presenter settings:` and not `Meeting information:`
- no URL/domain/sample ID/copied/read/shared completion wording

### Share, Invite, Leave

`test_chinese_meta_modifiers_preserve_share_invite_leave_safety`

Prompts and expected routes:

- `请用中文说明共享屏幕内容` -> screen-share safety Q&A, `ringcentral.video.toolbar.share`, `can_operate is False`, no interrupt
- `用更简洁的方式说明怎么共享屏幕` -> Share route remains non-operable/no-interrupt
- `请用中文说明怎么邀请别人` -> Invite route remains non-operable/no-interrupt
- `用友好语气发送邀请` -> Invite privacy/safety answer, non-operable/no-interrupt
- `简洁说明怎么离开会议` -> Leave route/leave safety answer, non-operable/no-interrupt
- `请用中文结束会议` -> Leave safety answer, non-operable/no-interrupt

Each assertion should also check the answer does not start with `Presenter settings:`.

### Chat And Participants

`test_chinese_meta_modifiers_preserve_chat_participants_location_controls`

Prompts:

- `请用中文说明聊天在哪里`
- `用新手语气讲聊天在哪里`
- `简单说参会者在哪里`
- `用中文说明谁在会议里`

Expected:

- Chat prompts route to `ringcentral.video.toolbar.chat`.
- Participants prompts route to `ringcentral.video.toolbar.participants`.
- Current `can_operate` expectations for those entrypoints remain unchanged.
- The answer does not start with `Presenter settings:`.

`test_chinese_meta_modifiers_preserve_chat_participant_content_privacy`

Prompts:

- `请用中文读出聊天消息`
- `简洁总结聊天内容`
- `用中文列出参会者姓名`
- `用友好语气告诉我主持人是谁`

Expected:

- `entrypoint_id is None` for private content/identity answers, or the existing safety Q&A route if the current matcher owns one.
- `can_operate is False`
- no interrupt
- the answer contains the authored privacy/verified-source boundary
- no `Chat panel:` or `Participants panel:` prefix

### Encryption And Security

`test_chinese_meta_modifiers_preserve_encryption_security_answer_only`

Prompts:

- `用中文确认加密状态`
- `用隐私语气检查会议是否加密`
- `简洁说明安全状态`
- `请用中文说会议安全吗`

Expected:

- `entrypoint_id == "ringcentral.video.top.meeting-info"`
- `can_operate is False`
- no interrupt
- localized encryption/security answer is returned
- no `Presenter settings:` prefix
- no copied/read/shared/verified-as-fact completion claims

`test_chinese_meta_bare_safety_words_do_not_match`

Prompts:

- `安全`
- `隐私`
- `状态`
- `确认`

Expected:

- no new Presenter meta match
- no new encryption/security route
- `entrypoint_id is None`
- `can_operate is False`

### Mojibake And Encoding

`test_chinese_presenter_meta_mojibake_does_not_match`

Prompts:

- mojibake for `请用中文回答`
- mojibake for `更简洁一点`
- existing `èŠå¤©` sentinel

Expected:

- `entrypoint_id is None`
- `can_operate is False`
- no interrupt
- no `Presenter settings:` answer for mojibake meta text
- no Chat route for mojibake alias text

## Recommended Implementation Boundary

Proceed only with a narrow runtime matcher update in `src/ai_presenter/runtime/questions.py`. Do not add Presenter meta prompts to `packages/ringcentral-video.yaml`; that would pollute RingCentral package Q&A/localization counts and would not protect temporary running-app packages.

Recommended guard rules:

- Keep `_match_qa(...)` before `_is_presenter_meta_request(...)`.
- Keep mixed explicit RingCentralVideo intents eligible for `_match_explicit_entrypoint(...)`.
- Add only high-confidence Chinese phrase fragments, not bare concept words.
- Require phrase-level intent such as `请用中文回答`, `用中文讲`, `更简洁一点`, `讲慢一点`, `用友好语气`, `用谨慎语气`, or `按新手讲`.
- Avoid single-token triggers: `中文`, `回答`, `说`, `讲`, `解释`, `简单`, `详细`, `新手`, `友好`, `谨慎`, `隐私`, `安全`, `状态`.
- Avoid adding mojibake variants or encoding-repair behavior.
- If the response is localized for Chinese, it must say this is a Presenter answer-style request and must not say settings were permanently changed unless controller/session voice state is actually updated and tested.

## No-Go Conditions

Do not accept a Cycle175 implementation if any of these occur:

- Chinese meeting-info private action prompts return `Presenter settings:` or become operable.
- Screen share, invite, leave, chat, participants, or location prompts lose their existing routes merely because the prompt includes `请用中文`, `简洁`, `友好`, `新手`, or `语气`.
- Chat message, participant identity, host/moderator identity, transcript, caption, invite link, or meeting-info values are read, copied, summarized, shared, or claimed verified without the existing explicit-user-request and verified-source boundary.
- Concrete Chinese encryption/security questions stop routing to meeting-info answer-only.
- Bare `安全`, `隐私`, `状态`, or `确认` starts matching either Presenter meta or encryption/security.
- Mojibake Chinese starts matching either Presenter meta prompts or RingCentral aliases.
- The implementation moves meta matching ahead of Q&A-first safety routing.
- The implementation modifies YAML localization counts for a Presenter-level feature.

## Recommendation

Recommend Cycle175 proceed only after the negative tests above are added. The source change should be a small phrase-list expansion plus any narrowly required Chinese meta answer rendering. Keep the current Cycle174 routing order and mixed-intent behavior intact. The safest acceptable implementation is one where pure Chinese Presenter style/language/detail prompts are answer-only, while Chinese prompts that mention RingCentral meeting info, sharing, invite, leave, chat, participants, location, or security continue through the existing RingCentralVideo safety and routing boundaries.

## Status

Status: risk scan complete; no source/tests/YAML were modified, staged, or committed.

Changed file path:

- `docs/agent-handoffs/cycle-175-risk-scan.md`
