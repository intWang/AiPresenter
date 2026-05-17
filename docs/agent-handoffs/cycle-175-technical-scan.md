# Cycle 175 Technical Scan: Chinese Presenter Meta Guard

Date: 2026-05-17

## Scope

- Inspected `src/ai_presenter/runtime/questions.py` at `8d16dc8`.
- Inspected `tests/unit/test_questions.py` at `8d16dc8`.
- Did not modify source, tests, package YAML, or git state.
- Existing dirty file before this scan: `.coverage`.

## Current Baseline

`questions.py` now has the right English guard shape:

1. `_answer_question(...)` normalizes the prompt.
2. `_match_qa(...)` runs before Presenter meta handling.
3. `_is_presenter_meta_request(...)` checks `_PRESENTER_META_REQUEST_FRAGMENTS`.
4. Meta prompts use `_match_explicit_entrypoint(...)`, not broad token fallback.
5. Pure meta prompts return `QuestionResponse` with no `entrypoint_id` and `can_operate=False`.

That placement is important. It lets RingCentralVideo safety Q&A win before the Presenter meta guard, while still preventing vague style prompts from becoming fuzzy RingCentralVideo control matches.

The gap is localization: `_PRESENTER_META_REQUEST_FRAGMENTS` is English-only at `questions.py:220`, so high-confidence Chinese requests such as `请用中文回答`, `请简洁一点`, `请讲慢一点`, and `我是新手，请讲简单一点` currently fall through to the normal no-match answer instead of the `Presenter settings:` guard.

## Recommended Implementation Point

Keep the implementation in `src/ai_presenter/runtime/questions.py`.

Primary change: extend `_PRESENTER_META_REQUEST_FRAGMENTS` with narrow Chinese full-phrase fragments. Do not add these to `packages/ringcentral-video.yaml`; they are Presenter expression requests, not RingCentralVideo app knowledge.

Do not add bare fragments such as `中文`, `语气`, `简洁`, `慢`, `新手`, `安全`, or `隐私`. They are too broad and can collide with RingCentralVideo routes, especially meeting information, security, host controls, notes/transcript, and recording.

Recommended constants to add:

```python
    "请用中文回答",
    "用中文回答",
    "可以用中文说吗",
    "能用中文说吗",
    "请说中文",
    "请讲中文",
    "请简洁一点",
    "回答简洁一点",
    "请讲慢一点",
    "请说慢一点",
    "解释慢一点",
    "请用更友好的语气回答",
    "用友好的语气回答",
    "请用谨慎的语气回答",
    "用谨慎的语气回答",
    "我是新手",
    "我是初学者",
    "请讲简单一点",
    "从基础讲起",
```

Secondary route-order fix to consider in the same file: add a small contained-QA check before `_is_package_entrypoint_alias_lookup(...)` inside `_match_qa(...)`. A Chinese prompt like `请用谨慎的语气回答，会议信息里能看到加密状态吗` currently contains the full localized encryption QA, but `会议信息` can trigger the meeting-info alias guard before the QA candidate loop. The safer implementation point is `_match_qa(...)`, not the meta guard:

```python
def _match_contained_qa_question(
    package: MaterialPackage,
    normalized_question: str,
) -> QuestionAnswer | None:
    for candidate in package.qa_question_candidates:
        if (
            candidate.normalized_question in normalized_question
            and _is_specific_question_fragment(candidate.normalized_question)
        ):
            return candidate.item
    return None
```

Call it after the existing explicit safety helpers (`_match_recording_safety_qa`, `_match_notes_transcript_safety_qa`, `_match_meeting_info_privacy_qa`) and before `_is_meeting_info_location_lookup(...)` / `_is_package_entrypoint_alias_lookup(...)`. This preserves full localized Q&A when a Presenter style phrase is prefixed, without making bare aliases into Q&A matches.

## Exact Tests To Add

Extend `test_presenter_meta_requests_do_not_route_to_ringcentral_controls` with pure Chinese Presenter meta prompts:

```python
        "请用中文回答",
        "可以用中文说吗",
        "请简洁一点",
        "请讲慢一点",
        "请用更友好的语气回答",
        "我是新手，请讲简单一点",
```

Add a Chinese mixed-intent test next to `test_presenter_meta_modifiers_do_not_steal_ringcentral_intents`:

```python
@pytest.mark.parametrize(
    (
        "question",
        "expected_entrypoint_id",
        "expected_can_operate",
        "expected_interrupt",
        "expected_answer",
        "unexpected_answer",
    ),
    [
        (
            "请简洁一点，复制会议链接",
            "ringcentral.video.top.meeting-info",
            False,
            False,
            "私人会议详情",
            "Meeting information:",
        ),
        (
            "请用谨慎的语气回答，会议信息里能看到加密状态吗",
            "ringcentral.video.top.meeting-info",
            False,
            False,
            "加密状态",
            "Meeting information:",
        ),
        (
            "我是新手，主持人怎么管理参会者",
            None,
            False,
            False,
            "明确要求",
            "Presenter settings:",
        ),
        (
            "请讲慢一点，开始会议笔记",
            None,
            False,
            False,
            "不要自动开启",
            "Presenter settings:",
        ),
        (
            "请用中文回答，聊天在哪里",
            "ringcentral.video.toolbar.chat",
            True,
            True,
            "聊天",
            "Presenter settings:",
        ),
        (
            "我是新手，网络质量",
            "ringcentral.video.top.network-quality",
            True,
            True,
            "Network quality",
            "Presenter settings:",
        ),
    ],
)
def test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents(
    question: str,
    expected_entrypoint_id: str | None,
    expected_can_operate: bool,
    expected_interrupt: bool,
    expected_answer: str,
    unexpected_answer: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == expected_entrypoint_id
    assert response.can_operate is expected_can_operate
    assert (create_question_interrupt_step(package, response) is not None) is (
        expected_interrupt
    )
    assert expected_answer in response.answer_text
    assert unexpected_answer not in response.answer_text
```

Keep the existing English tests unchanged; they are valuable regression coverage for the route shape added in Cycle174.

## Focused Commands

Use commands that avoid coverage/cache churn:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents
```

Broaden only to nearby routing sentinels:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_localized_encryption_status_questions_are_answer_only tests\unit\test_questions.py::test_chinese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_ringcentral_chinese_notes_action_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_localized_host_controls_question_returns_chinese_guidance tests\unit\test_questions.py::test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table
```

Lint the touched Python files if implementation follows:

```powershell
.\.venv\Scripts\python.exe -B -m ruff check src\ai_presenter\runtime\questions.py tests\unit\test_questions.py
```

Confirm the doc/source boundary before handoff:

```powershell
git diff -- src\ai_presenter\runtime\questions.py tests\unit\test_questions.py docs\agent-handoffs\cycle-175-technical-scan.md
git status --short
```

## Risks

- Broad Chinese fragments will steal RingCentralVideo controls. Keep full phrases and avoid standalone nouns/adjectives.
- The current `_match_qa(...)` alias guard can block a prefixed localized security QA when the prompt contains `会议信息`; add the contained-QA check if the security overlap test is included.
- Meta prompts intentionally skip broad token fallback. Mixed prompts should route only through Q&A, package aliases, meeting-info location lookup, or entrypoint titles.
- The guard only answers that Presenter settings are separate from RingCentralVideo controls; it does not persistently change `PresenterVoiceSettings`.
- `.coverage` was already dirty before this scan. Avoid default pytest coverage runs unless a later agent explicitly wants to refresh it.

## Status

Technical scan complete. Source and tests were inspected only. This handoff is the only intended file change.

Changed file: `docs/agent-handoffs/cycle-175-technical-scan.md`
