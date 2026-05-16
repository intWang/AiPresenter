# Cycle 107 Technical Scan: Notes/Transcript Action And Content Routing

## Recommendation

Harden the question matcher with a narrow Japanese Notes/Transcript action/content safety guard before broad entrypoint token scoring.

Recommended minimal slice:

1. Add a runtime-only safety matcher in `src/ai_presenter/runtime/questions.py` for Japanese Notes/Transcript action/content requests.
2. Return existing answer-only package Q&A instead of broad entrypoint scoring for those unsafe prompts.
3. Add focused red tests in `tests/unit/test_questions.py`.
4. Do not change production package YAML, demo routes, package Q&A content, localization counts, aliases, or diagnostics counts.

The target behavior is not to make Notes/Transcript action requests operable. It is to prevent action/content language from being misclassified as a different route, especially `ringcentral.develop.video.start`.

## Current Baseline

Verified in the current worktree after Cycle 106 commit `146c51a feat: add japanese notes location aliases`.

- Existing dirty worktree item: `.coverage`; leave it untouched.
- `packages/ringcentral-video.yaml` still has `27` operation entrypoints.
- Japanese localization is complete: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- Japanese package-owned aliases remain `13/27` entrypoints and `34` aliases.
- Total package-owned aliases remain `87`.
- Q&A prompts remain `71`.
- Expected diagnostics remain:
  - `87 package-owned aliases have no cross-entrypoint duplicates`
  - `71 Q&A question prompts have no cross-item duplicates`
  - `71 Q&A question prompts have no unsafe package-owned alias overlaps`
  - `11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`

## Observed Residual Behavior

Runtime probes show the residual issue is not operability, but route association:

```text
Start notes をクリックして
  entrypoint=ringcentral.develop.video.start
  can_operate=False
  interrupt=False

Start notes の場所はどこですか
  entrypoint=ringcentral.develop.video.start
  can_operate=False
  interrupt=False

Notes and Transcript の場所はどこですか
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False

ノートと文字起こしの場所はどこですか
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False

Transcript を要約して
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False

文字起こしを要約して
  entrypoint=None
  can_operate=False
  interrupt=False

start meeting
  entrypoint=ringcentral.develop.video.start
  can_operate=False
  interrupt=False

Start meeting をクリックして
  entrypoint=ringcentral.develop.video.start
  can_operate=False
  interrupt=False
```

`can_operate=False` and `create_question_interrupt_step(...) is None` are already protecting execution. The remaining concern is answer quality and route correctness: unsafe Notes/Transcript action/content prompts should not look like Start meeting, and Transcript summarization should not look like opening the Notes panel.

## Relevant Code Paths

- `src/ai_presenter/runtime/questions.py:227`
  - `_match_qa(...)` checks exact Q&A, recording safety, title lookup, fragments, then token overlap.
- `src/ai_presenter/runtime/questions.py:233`
  - `_match_recording_safety_qa(...)` already provides a useful precedent for a narrow Japanese safety matcher.
- `src/ai_presenter/runtime/questions.py:309`
  - `_match_entrypoint(...)` runs package aliases first, then broad token scoring.
- `src/ai_presenter/runtime/questions.py:364`
  - `_score_entrypoint_match(...)` weights ID/title tokens heavily. This is why `Start notes ...` can select `ringcentral.develop.video.start`.
- `src/ai_presenter/runtime/questions.py:421`
  - `_can_operate(...)` prevents `answerOnly`, no-open-step, and risky-word routes from becoming interruptable.
- `src/ai_presenter/runtime/session.py:88`
  - `create_question_interrupt_step(...)` returns `None` when `can_operate` is false.
- `packages/ringcentral-video.yaml:24`
  - `ringcentral.develop.video.start` has title `Start meeting`.
- `packages/ringcentral-video.yaml:473`
  - `ringcentral.video.more.notes` has `questionPolicy: answerOnly` and the two Cycle 106 Japanese location aliases.
- `packages/ringcentral-video.yaml:1517`
  - Existing Notes Q&A is related to `ringcentral.video.more.notes`.
- `packages/ringcentral-video.yaml:1532`
  - Existing captions/transcription Q&A is answer-only with no related entrypoint and says not to start notes/transcription/captions/translation, read transcript text, or promise summaries unless explicitly requested and verified.

## Minimal Implementation Slice

Change only `src/ai_presenter/runtime/questions.py`.

Add a helper next to `_match_recording_safety_qa(...)`, called before `_is_entrypoint_title_lookup(...)`:

```python
notes_transcript_safety_match = _match_notes_transcript_safety_qa(package, normalized_question)
if notes_transcript_safety_match is not None:
    return notes_transcript_safety_match
```

Suggested matching shape:

- Notes/Transcript subject terms:
  - English UI terms used in Japanese prompts: `start notes`, `transcript`, `notes and transcript`
  - Japanese terms: `ノート`, `文字起こし`, `議事録`
- Action/content terms:
  - start/click/open action wording: `クリック`, `押して`, `開始`, `始め`, `開いて`
  - content verbs: `要約`, `読ん`, `読み上げ`, `内容`, `コピー`, `保存`, `エクスポート`
- Exclude location-only prompts:
  - `場所`, `どこ`, `入口`

Return policy:

- For action/content terms, prefer the existing captions/transcription Q&A at `packages/ringcentral-video.yaml:1532`, because it has no related entrypoint and produces `entrypoint_id is None`.
- For future variants that only ask where the Notes panel is, keep the existing alias/Q&A path so `ringcentral.video.more.notes` location routes keep working.

This avoids changing package Q&A prompt counts. It also avoids adding broad package aliases such as bare `Transcript`, `ノート`, or `文字起こし`, which would increase alias/count churn and create more substring risk.

## Red Tests To Write First

Add focused tests to `tests/unit/test_questions.py`.

Test 1: Notes action prompts do not route to Start meeting.

```python
@pytest.mark.parametrize(
    "question",
    [
        "Start notes をクリックして",
        "Start notes を押して",
        "ノートを開始して",
    ],
)
def test_ringcentral_japanese_notes_action_requests_do_not_match_start_meeting(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.develop.video.start"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "開始" in response.answer_text or "start" in response.answer_text.casefold()
```

Expected RED now:

- `Start notes をクリックして` returns `ringcentral.develop.video.start`.
- `Start notes を押して` is likely to return `ringcentral.develop.video.start`.

Test 2: Transcript content requests stay answer-only without panel association.

```python
@pytest.mark.parametrize(
    "question",
    [
        "Transcript を要約して",
        "Transcript の内容を読んで",
        "文字起こしを要約して",
    ],
)
def test_ringcentral_japanese_transcript_content_requests_stay_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "要約" in response.answer_text
```

Expected RED now:

- `Transcript を要約して` returns `ringcentral.video.more.notes`.

Test 3: Legitimate Start meeting still routes to the develop start entrypoint.

```python
@pytest.mark.parametrize(
    "question",
    [
        "start meeting",
        "Start meeting をクリックして",
    ],
)
def test_ringcentral_start_meeting_questions_still_match_start_meeting(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id == "ringcentral.develop.video.start"
    assert response.can_operate is False
```

Expected RED now: should already pass. Keep it in the slice to prevent over-broad blocking of `start`.

Test 4: Cycle 106 Notes location routes still work.

```python
@pytest.mark.parametrize(
    "question",
    [
        "Notes and Transcript の場所はどこですか",
        "ノートと文字起こしの場所はどこですか",
    ],
)
def test_ringcentral_japanese_notes_location_routes_still_match_notes(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id == "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
```

Expected RED now: should already pass. Keep it in the slice to protect the Cycle 106 location alias behavior.

## Expected Counts

The implementation should not change any package, localization, alias, or diagnostics counts:

- `27` operation entrypoints
- `87` package-owned aliases
- Japanese aliases: `13/27` entrypoints, `34` aliases
- Chinese aliases: `15/27` entrypoints, `49` aliases
- English aliases: `1/27` entrypoint, `4` aliases
- Q&A prompts: `71`
- Q&A localized coverage: `12/12` questions and `12/12` answers for Japanese
- Demo localized coverage: `51/51` Japanese demo steps
- `qa alias substring risk`: INFO at `11`

Do not add package aliases or localized Q&A prompts in this slice, because that would change counts.

## Verification Commands

Focused red/green command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_japanese_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_start_meeting_questions_still_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_notes_location_routes_still_match_notes
```

Focused regression around existing related behavior:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_japanese_recording_location_aliases_are_answer_only tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_localized_caption_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint tests\unit\test_questions.py::test_notes_matches_notes_entrypoint tests\unit\test_questions.py::test_start_meeting_answer_is_not_operable
```

Count verification:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected lines:

```text
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
```

Optional broader confidence pass:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_reports_profile_and_package_ok tests\unit\test_diagnostics.py
```

## Guardrails

- Do not edit `packages/ringcentral-video.yaml` for this slice.
- Do not change `ringcentral.video.more.notes` `openSteps`.
- Do not remove or weaken `questionPolicy: answerOnly`.
- Do not add broad package aliases for `Notes`, `Transcript`, `ノート`, or `文字起こし`.
- Do not add localized Q&A prompts for these action/content phrases in this slice.
- Do not block legitimate `start meeting` / `Start meeting をクリックして` matching.
- Do not block Cycle 106 location routes for `Notes and Transcript の場所` or `ノートと文字起こしの場所`.
- Keep all question responses non-operable and ensure no question interrupt step is created for Notes/Transcript action/content prompts.
