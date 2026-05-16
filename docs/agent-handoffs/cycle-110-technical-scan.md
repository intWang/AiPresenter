# Cycle 110 Tone Route-Parity Technical Scan

> **For agentic workers:** This is a handoff scan, not a production-code change request. Work test-first if implementing the slice, and keep edits scoped to the test file unless a failing test proves a runtime bug.

**Goal:** Lock down that presenter tone, including the `privacy` alias for `careful`, does not change sensitive question routing, authorization, or interrupt creation.

**Architecture:** `answer_question()` normalizes and matches the question before applying tone to generated presenter text. `create_question_interrupt_step()` only depends on `entrypoint_id` and `can_operate`, so tone should not affect whether a step is queued.

**Tech Stack:** Python, pytest, RingCentral package YAML, `PresenterVoiceSettings`.

---

## Current Behavior

- Current worktree note: `tests/unit/test_questions.py` is already modified by another worker. The uncommitted diff adds `test_ringcentral_sensitive_prompt_routing_is_tone_invariant` near the existing careful-tone privacy test.
- The current added test passes in the repo venv: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant -q -o addopts=""` returned `9 passed in 1.93s`.
- `src/ai_presenter/runtime/questions.py` matches QA first, then entrypoints. Tone is not read by `_match_qa()`, `_match_entrypoint()`, `_can_match_qa_fragment()`, or `_can_operate()`.
- Tone is only used when rendering text: QA localized answers are returned as authored text, non-localized QA and entrypoint answers go through `render_presenter_text()`.
- `src/ai_presenter/runtime/voice.py` canonicalizes `tone="privacy"` to `careful`. For English generated text, careful adds `Safety note.`; for Chinese generated text it adds `我会谨慎说明。`; Japanese and localized QA text generally keep authored text unless `concise` is used.
- `src/ai_presenter/runtime/session.py` queues an interrupt only when `response.entrypoint_id is not None` and `response.can_operate is True`.
- `_can_operate()` rejects `questionPolicy: answerOnly`, missing `openSteps`, and risky entrypoint words. `ringcentral.video.top.meeting-info` and `ringcentral.video.more.notes` are already `answerOnly` in `packages/ringcentral-video.yaml`.

## Proposed Test Slice

Recommended slice: test-only.

If the current uncommitted test is accepted, the minimal Cycle 110 slice is already present. I would make one small tightening before merge: carry expected `can_operate` and expected interrupt in the parameter table so the baseline cannot silently drift while still remaining tone-invariant.

Suggested table:

| Prompt | Language | Expected route | Expected can_operate | Expected interrupt |
| --- | --- | --- | --- | --- |
| `how do I handle meeting recording safely?` | `en` | `ringcentral.video.more.recording` | `False` | `False` |
| `Read the transcript` | `en` | `None` | `False` | `False` |
| `meeting information` | `en` | `ringcentral.video.top.meeting-info` | `False` | `False` |
| `Can AiPresenter read meeting messages or participant names?` | `en` | `None` | `False` | `False` |
| `invite people` | `en` | `ringcentral.video.toolbar.invite` | `False` | `False` |
| `share screen` | `en` | `ringcentral.video.toolbar.share` | `False` | `False` |
| `participants` | `en` | `ringcentral.video.toolbar.participants` | `True` | `True` |
| `leave meeting` | `en` | `ringcentral.video.toolbar.leave` | `False` | `False` |
| `network quality` | `en` | `ringcentral.video.top.network-quality` | `True` | `True` |

Tone matrix:

- Baseline: `professional`
- Compared tones: `friendly`, `coach`, `support`, `privacy`
- Optional explicit canonical check: include `careful` too if the team wants both alias and canonical coverage. The existing `privacy` row already exercises alias normalization into `careful`.

Invariants for every prompt and compared tone:

- `response.entrypoint_id == baseline.entrypoint_id`
- `response.can_operate is baseline.can_operate`
- `(create_question_interrupt_step(package, response) is not None) is baseline_interrupt`
- Baseline should equal the table's expected route, `can_operate`, and interrupt value.

No helper is required for the current nine-row matrix. If more languages or tones are added, use a tiny local helper in `tests/unit/test_questions.py`:

```python
def assert_question_route_tone_invariant(
    package: MaterialPackage,
    *,
    question: str,
    expected_entrypoint_id: str | None,
    expected_can_operate: bool,
    expected_interrupt: bool,
    language: str = "en",
    tones: tuple[str, ...] = ("friendly", "coach", "support", "privacy"),
) -> None:
    baseline = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language=language, tone="professional"),
    )
    baseline_interrupt = create_question_interrupt_step(package, baseline) is not None

    assert baseline.entrypoint_id == expected_entrypoint_id
    assert baseline.can_operate is expected_can_operate
    assert baseline_interrupt is expected_interrupt

    for tone in tones:
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(language=language, tone=tone),
        )

        assert response.entrypoint_id == baseline.entrypoint_id
        assert response.can_operate is baseline.can_operate
        assert (create_question_interrupt_step(package, response) is not None) is baseline_interrupt
```

## Expected Red/Green Behavior

Expected red failures:

- If any tone participates in QA or entrypoint matching, a compared tone can produce a different `entrypoint_id`.
- If careful/privacy tone is treated as a safety blanket at authorization time, the intentionally operable prompts `participants` and `network quality` may stop creating interrupts.
- If careful/privacy tone bypasses safety gates, blocked prompts such as `Read the transcript`, `meeting information`, `invite people`, `share screen`, or `leave meeting` may become operable or queue an interrupt.
- If `privacy` stops normalizing to `careful`, the test errors at `PresenterVoiceSettings(tone="privacy")`.

Expected green behavior:

- Text may differ by tone, but route, `can_operate`, and interrupt presence remain identical to `professional`.
- Sensitive answer-only prompts remain answer-only.
- Legitimate operable discovery prompts remain operable under careful/privacy tone.

## Compatibility Risks

- Do not assert full `answer_text` equality across tones; English careful/support/friendly/coach intentionally add different prefixes.
- Do not make the matrix "all sensitive prompts are non-operable"; `participants` and `network quality` are important positive controls.
- Avoid adding `concise` to the same test if the test later checks answer fragments, because `concise` intentionally truncates text.
- Localized QA answers often bypass tone prefixes. If adding Chinese or Japanese rows, keep the invariant focused on route/authorization/interrupt, not tone prose.
- The worktree already has dirty `.coverage` and `tests/unit/test_questions.py`. Do not revert or rewrite those changes when implementing the handoff.

## Change Scope

- Production code: no change expected.
- Package YAML: no change expected.
- Diagnostics behavior or counts: no change expected.
- Localization strings or localization counts: no change expected.
- Tests: one parameterized unit test is sufficient; optional helper only if the matrix expands.

## Verification Commands

Use the repo venv. The global Python on this machine does not currently have pytest installed.

Focused check, coverage disabled to avoid touching `.coverage`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant -q -o addopts=""
```

Related route/privacy cluster:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_questions.py::test_ringcentral_careful_tone_preserves_privacy_question_route `
  tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant `
  tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only `
  tests\unit\test_questions.py::test_notes_privacy_gate_does_not_depend_on_risky_words `
  -q -o addopts=""
```

Full suite with the repository's configured coverage gate:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Full suite without coverage side effects:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts=""
```
