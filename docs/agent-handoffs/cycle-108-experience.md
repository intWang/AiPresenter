# Cycle 108 Experience Handoff: Chinese Notes/Transcript Safety Matcher

## Decision Record

Cycle 108 used a runtime-only matcher extension for Chinese Notes/Transcript action and content prompts. The goal was not to teach the package more aliases; it was to stop action/content intent from being interpreted as a safe panel-location lookup.

Runtime matching was chosen over YAML aliases because package aliases describe discoverable controls. Prompts like `开始会议笔记`, `读取转录内容`, `总结会议笔记`, `复制转录内容`, and `导出转录` are not alternate names for the Notes panel. They ask AiPresenter to change meeting state or handle private meeting artifacts. Putting those phrases in `packages/ringcentral-video.yaml` would blur the privacy boundary, inflate package/localization counts, and make future diagnostics less meaningful.

The implementation reused the existing captions/live transcription/translation safety Q&A instead of adding copy or package data. That kept operation entrypoint counts, package-owned alias counts, Q&A counts, demo flow shape, and localization coverage stable.

## Implementation Pattern

The matcher pattern is a narrow three-part gate in `src/ai_presenter/runtime/questions.py`:

1. Require a Notes/Transcript subject term, including Chinese terms such as notes, transcript, captions, meeting notes, and mixed English UI labels like `Start notes`.
2. Exclude location intent before safety routing, using Chinese lookup terms such as `哪里`, `在哪`, `位置`, and `入口`.
3. Require an action/content term, such as start, enable, click, open, read, summarize, content, copy, save, export, create, or generate.

If all three conditions hold, the prompt routes to the existing answer-only safety Q&A with `entrypoint_id is None`, `can_operate is False`, and no question interrupt step.

The protected prompt classes were:

- Starting or opening Notes/Transcript controls: `开始会议笔记`, `启动会议笔记`, `点击 Start notes`.
- Reading or reciting transcript/notes content: `读取转录内容`.
- Summarizing meeting notes/transcripts: `总结会议笔记`, `总结转录`.
- Copying/exporting/saving artifacts: `复制转录内容`, `导出转录`.
- Mixed Chinese/English UI prompts where Chinese action words combine with English control labels.

The preserved prompt classes were:

- Chinese Notes/Transcript location lookups: `转录在哪里`, `会议笔记在哪里`, `转录入口在哪`.
- Captions/live transcription location and translation Q&A.
- Post-meeting artifact location Q&A.
- Recording safety Q&A.
- Start meeting routing, especially prompts containing `Start meeting`.
- Unrelated safe controls such as network quality.

## Verification Checklist

- Focused tests for Chinese Notes action and transcript content prompts assert `entrypoint_id is None`, `can_operate is False`, and `create_question_interrupt_step(...) is None`.
- Location sentinel tests assert Chinese Notes/Transcript lookup prompts still route to `ringcentral.video.more.notes` and remain answer-only.
- English and Japanese Cycle 107 sentinels still pass.
- Start meeting sentinels still route to `ringcentral.develop.video.start`; `Start notes` must not be confused with `Start meeting`.
- Captions/live transcription, post-meeting artifacts, recording safety, and unrelated safe-control routes remain unchanged.
- Localization and diagnostics counts remain stable: no new YAML aliases, no new Q&A prompts, no demo-flow changes, no new doctor warnings.
- CJK fixtures use UTF-8-safe source text or `\u` escapes where PowerShell rendering may be misleading.

Useful commands for the next reviewer:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_chinese_notes_action_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_chinese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_chinese_notes_location_routes_still_match_notes
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_japanese_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_start_meeting_questions_still_match_start_meeting
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video
```

## Future Skill/Rule Ideas

- Add a reusable "multilingual safety matcher expansion" rule: every new language needs subject terms, action/content terms, location exclusions, and unrelated-route sentinels.
- Add a review checklist item for "alias vs intent": if a phrase asks to operate, read, summarize, copy, save, or export, it should not become a package alias by default.
- Add a diagnostics note for stable-count hardening slices: runtime-only changes should justify any alias/Q&A/localization count drift.
- Add a CJK fixture hygiene rule: prefer escaped literals in tests when terminal encoding can hide the real prompt.
- Add a RingCentral Video privacy rule covering meeting artifacts: captions, transcripts, notes, chat, participants, meeting links, recordings, and post-meeting summaries all need explicit visible-context or consent boundaries.

## Next-Cycle Opportunities

- Build a small table-driven helper for multilingual subject/action/location gates if more languages are added. Keep it transparent; do not turn this into a broad NLU classifier.
- Expand coverage to additional Chinese variants only after collecting real prompt examples, especially Traditional Chinese and mixed UI-language prompts.
- Review whether the safety Q&A target should remain the captions/live transcription answer or become a dedicated Notes/Transcript artifact-safety Q&A. Do this only if product wants clearer copy; do not add it just to satisfy matcher mechanics.
- Add analytics-safe labels for answer-only safety routing so downstream reporting can distinguish "safe panel location" from "blocked artifact/action intent".
- For RingCentral Video, continue auditing adjacent privacy-sensitive routes: meeting info values, chat content, participant names, recording state, post-meeting artifacts, and visible shared-screen content.
