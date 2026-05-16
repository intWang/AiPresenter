# Cycle 108 Technical Scan: Chinese Notes/Transcript Action And Content Routing

## Recommendation

Proceed with a minimal runtime-only extension to the existing Notes/Transcript safety matcher in `src/ai_presenter/runtime/questions.py`.

Cycle 107 already added `_match_notes_transcript_safety_qa(...)` for English and Japanese subject plus action/content terms, returning the existing answer-only captions/transcription Q&A. The remaining gap is Chinese action/content wording around Notes, transcript, captions, reading, summaries, copying, saving, opening, and starting.

Do not change package YAML, demo content, production routes, or existing Q&A copy. Add only Chinese subject and action/content terms to the existing matcher, with focused red tests in `tests/unit/test_questions.py`.

## Current Baseline

Verified in the current worktree after Cycle 107 commit `64d7f31 fix: harden notes transcript safety routing`.

- Existing dirty worktree item: `.coverage`; leave it untouched.
- `packages/ringcentral-video.yaml` still has `27` operation entrypoints.
- Chinese localization report: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- Chinese aliases: `15/27` entrypoints, `49` aliases.
- Japanese localization report: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- Japanese aliases: `13/27` entrypoints, `34` aliases.
- Total package-owned aliases: `87`.
- Q&A prompts: `71`.
- Diagnostics remain:
  - `87 package-owned aliases have no cross-entrypoint duplicates`
  - `71 Q&A question prompts have no cross-item duplicates`
  - `71 Q&A question prompts have no unsafe package-owned alias overlaps`
  - `11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`

## Observed Residual Behavior

Probed with `answer_question(...)` against `packages/ringcentral-video.yaml`.

```text
Start notes 请帮我点击
  entrypoint=None
  can_operate=False
  interrupt=False
  answer=existing captions/transcription safety Q&A

请开始笔记
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
  answer=generic Notes and transcript entrypoint answer

请打开 Notes and Transcript
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
  answer=existing Notes location Q&A

帮我朗读转录内容
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
  answer=generic Notes and transcript entrypoint answer

请总结转录内容
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
  answer=generic Notes and transcript entrypoint answer

请复制字幕
  entrypoint=None
  can_operate=False
  interrupt=False
  answer=Chinese no-match answer

请保存转录
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
  answer=generic Notes and transcript entrypoint answer

笔记和转录在哪里
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
  answer=existing Notes location Q&A

字幕在哪里
  entrypoint=None
  can_operate=False
  interrupt=False
  answer=existing captions/transcription safety Q&A
```

The execution safety boundary is intact: all cases are `can_operate=False` and no question interrupt step is created. The remaining concern is answer quality and route association. Chinese action/content prompts should return the existing captions/transcription safety answer, not a generic Notes entrypoint answer or no-match answer.

## Relevant Code Paths

- `src/ai_presenter/runtime/questions.py`
  - `_match_qa(...)` now calls `_match_recording_safety_qa(...)` and `_match_notes_transcript_safety_qa(...)` before broad Q&A fragment and token matching.
  - `_match_notes_transcript_safety_qa(...)` checks `_NOTES_TRANSCRIPT_TERMS`, excludes `_LOCATION_LOOKUP_TERMS`, then requires `_NOTES_TRANSCRIPT_ACTION_OR_CONTENT_TERMS`.
  - `_NOTES_TRANSCRIPT_TERMS` currently covers English UI strings and Japanese terms, but not Chinese `笔记`, `转录`, `字幕`.
  - `_NOTES_TRANSCRIPT_ACTION_OR_CONTENT_TERMS` currently covers English and Japanese action/content terms, but not Chinese `开始`, `打开`, `开启`, `朗读`, `总结`, `内容`, `复制`, `保存`, `导出`.
  - `_LOCATION_LOOKUP_TERMS` currently covers English/Japanese lookup wording, but not Chinese `哪里`, `在哪`, `入口`, `位置`.
- `packages/ringcentral-video.yaml`
  - Existing Notes Q&A: `Where are notes and transcript controls?`, related to `ringcentral.video.more.notes`.
  - Existing captions/transcription Q&A: `Where are captions, live transcription, and translation controls?`, no related entrypoint, with localized Chinese answer warning not to automatically start notes/transcription/captions/translation, read caption/transcript text, or promise summaries.
- `tests/unit/test_questions.py`
  - Cycle 107 already covers English and Japanese Notes/Transcript action/content prompts.
  - Existing Chinese package-alias test covers location-style `会议笔记在哪里`, which should continue routing to `ringcentral.video.more.notes`.

## Minimal Implementation Slice

Change only `src/ai_presenter/runtime/questions.py`.

Extend existing constants:

```python
_NOTES_TRANSCRIPT_TERMS = (
    ...
    "笔记",
    "转录",
    "字幕",
)

_NOTES_TRANSCRIPT_ACTION_OR_CONTENT_TERMS = (
    ...
    "点击",
    "打开",
    "开启",
    "开始",
    "朗读",
    "读",
    "总结",
    "摘要",
    "内容",
    "复制",
    "保存",
    "导出",
)

_LOCATION_LOOKUP_TERMS = (
    ...
    "哪里",
    "在哪",
    "入口",
    "位置",
)
```

Keep the matcher structure unchanged:

1. Subject term must match.
2. Location-only wording must be excluded.
3. Action/content term must match.
4. Return the existing captions/transcription Q&A via `_NOTES_TRANSCRIPT_SAFETY_QUESTION`.

Do not add package `questionAliases.zh`, localized Q&A prompts, or new Q&A items. Counts should remain unchanged.

## Red Tests To Write First

Add focused tests to `tests/unit/test_questions.py`.

Test 1: Chinese Notes action requests route to the captions/transcription safety answer.

```python
@pytest.mark.parametrize(
    "question",
    [
        "请开始笔记",
        "请打开 Notes and Transcript",
        "请开启笔记",
    ],
)
def test_ringcentral_chinese_notes_action_requests_stay_answer_only(question: str) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "不要自动开启笔记" in response.answer_text
```

Expected RED now:

- `请开始笔记` returns `ringcentral.video.more.notes`.
- `请打开 Notes and Transcript` returns `ringcentral.video.more.notes`.

Test 2: Chinese transcript/caption content requests route to the captions/transcription safety answer.

```python
@pytest.mark.parametrize(
    "question",
    [
        "帮我朗读转录内容",
        "请总结转录内容",
        "请复制字幕",
        "请保存转录",
    ],
)
def test_ringcentral_chinese_transcript_content_requests_stay_answer_only(question: str) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "不要朗读字幕或转录内容" in response.answer_text
```

Expected RED now:

- `帮我朗读转录内容`, `请总结转录内容`, and `请保存转录` return `ringcentral.video.more.notes`.
- `请复制字幕` returns no-match instead of the safety Q&A.

Test 3: Chinese location lookups still route through existing location behavior.

```python
@pytest.mark.parametrize(
    "question",
    [
        "笔记和转录在哪里",
        "会议笔记在哪里",
        "字幕在哪里",
    ],
)
def test_ringcentral_chinese_notes_transcript_location_lookups_still_work(question: str) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "不要自动开启" not in response.answer_text
```

Expected RED now: should already pass for the purpose of guarding against over-broad matching. If the implementation chooses to keep `字幕在哪里` on the captions/transcription Q&A, drop the final negative assertion for that parameter or split it into a separate assertion that `entrypoint_id is None`.

## Expected Counts

Counts should remain unchanged because this is runtime matcher logic only:

- Operation entrypoints: `27`
- Total package-owned aliases: `87`
- Chinese aliases: `15/27` entrypoints, `49` aliases
- Japanese aliases: `13/27` entrypoints, `34` aliases
- Q&A prompts: `71`
- Chinese localized Q&A coverage: `12/12` questions and `12/12` answers
- Japanese localized Q&A coverage: `12/12` questions and `12/12` answers
- Demo localized coverage: `51/51` for Chinese and Japanese
- `qa alias substring risk`: INFO at `11`

## Verification Commands

Focused red/green command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_chinese_notes_action_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_chinese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_chinese_notes_transcript_location_lookups_still_work
```

Regression around Cycle 107 and nearby behavior:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_japanese_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_english_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_show_me_where_notes_remains_location_lookup tests\unit\test_questions.py::test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table
```

Count verification:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected lines:

```text
questionAliases.zh present on 15/27 entrypoints (49 aliases)
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for zh.

questionAliases.ja present on 13/27 entrypoints (34 aliases)
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

Diagnostics verification:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video
```

Expected lines:

```text
[OK] question aliases: 87 package-owned aliases have no cross-entrypoint duplicates
[OK] qa questions: 71 Q&A question prompts have no cross-item duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 10 ok, 1 info, 0 warnings, 0 failed.
```

Optional broader confidence pass:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_chinese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_reports_profile_and_package_ok tests\unit\test_diagnostics.py
```

## Guardrails

- Do not edit `packages/ringcentral-video.yaml`.
- Do not add Chinese package aliases for bare `笔记`, `转录`, or `字幕`.
- Do not add localized Q&A prompt variants for these action/content phrases in this slice.
- Do not change `ringcentral.video.more.notes` `questionPolicy: answerOnly`.
- Do not change `openSteps`, demo flows, presenter notes, CLI formatting, diagnostics logic, or localization reports.
- Preserve legitimate Chinese location behavior for `会议笔记在哪里` and `笔记和转录在哪里`.
- Keep all Chinese Notes/Transcript action/content responses non-operable and ensure no question interrupt step is created.
