# Cycle 154 Technical Scan: RingCentral Video Question Phrasing

## Scope Inspected

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `src/ai_presenter/packages/models.py`

No source, test, README, package, profile, existing docs, or `.coverage` files were edited during this scan.

## Smallest TDD Slice

Add package-owned English phrasing coverage for the microphone toolbar button:

- User phrasing: `Where is the microphone button?`
- Expected route: `ringcentral.video.toolbar.audio`
- Expected `can_operate`: `False`

Why this is the smallest low-risk slice:

- Current behavior routes `Where is the microphone button?` to `ringcentral.video.toolbar.audio-menu`, because token scoring favors the menu entrypoint whose purpose also mentions microphone controls.
- The word `button` points to the toolbar mute/unmute control, not the microphone/speaker device menu.
- A single package YAML `questionAliases.en` entry can override scoring without changing matcher code.
- `ringcentral.video.toolbar.audio` is already non-operable because its title/purpose include risky media-state words such as `mute`, `unmute`, and `toggle`.

Current behavior probe:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; from ai_presenter.runtime.questions import answer_question; from ai_presenter.runtime.voice import PresenterVoiceSettings; p=load_material_package(Path('packages/ringcentral-video.yaml')); r=answer_question(package=p, question='Where is the microphone button?', voice=PresenterVoiceSettings()); print(r.entrypoint_id, r.can_operate)"
```

Observed before implementation:

```text
ringcentral.video.toolbar.audio-menu False
```

## Alias Structure Notes

- `OperationEntrypoint.question_aliases` is modeled at `src/ai_presenter/packages/models.py:61` with YAML alias `questionAliases`.
- Package aliases are converted into `EntrypointQuestionAlias` records during package validation at `src/ai_presenter/packages/models.py:186`.
- Package-owned aliases are sorted longest-first by `_sort_entrypoint_question_aliases_by_match_order` at `src/ai_presenter/packages/models.py:342`.
- Q&A phrasing uses `QuestionAnswer.localized_questions` at `src/ai_presenter/packages/models.py:120`; `_qa_questions` at `src/ai_presenter/packages/models.py:383` combines the canonical question plus localized question variants.
- This slice should use an entrypoint `questionAliases` update, not a Q&A alias, because the expected answer is a direct location/control route.

## Exact Test To Add

Add this focused test near the existing package-owned alias tests in `tests/unit/test_questions.py`, close to `test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table` at line 1711 or the Spanish/Japanese alias coverage that follows it:

```python
def test_ringcentral_english_microphone_button_question_matches_audio_control_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question="Where is the microphone button?",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.audio"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
```

RED command:

```powershell
.\.venv\Scripts\pytest.exe tests/unit/test_questions.py::test_ringcentral_english_microphone_button_question_matches_audio_control_alias -q
```

Expected RED result before the YAML alias:

```text
assert 'ringcentral.video.toolbar.audio-menu' == 'ringcentral.video.toolbar.audio'
```

## Exact Green Implementation

Modify only the `questionAliases` field for `ringcentral.video.toolbar.audio` in `packages/ringcentral-video.yaml:208`.

Add an English alias before the existing `es` aliases:

```yaml
  questionAliases:
    en:
    - microphone button
    es:
    - ubicacion del boton mute
    - control del microfono en la barra
    - estado del microfono en reunion
```

The actual file already contains accented Spanish text; preserve the existing text exactly when editing. The unaccented Spanish above only indicates placement.

## Verification Commands

Run the targeted test first:

```powershell
.\.venv\Scripts\pytest.exe tests/unit/test_questions.py::test_ringcentral_english_microphone_button_question_matches_audio_control_alias -q
```

Then run the surrounding question suite:

```powershell
.\.venv\Scripts\pytest.exe tests/unit/test_questions.py -q
```

Before handing off, also run:

```powershell
rg -n "[ \t]+$" packages\ringcentral-video.yaml tests\unit\test_questions.py
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py
```

## No-Go Scope

- Do not change matcher scoring in `src/ai_presenter/runtime/questions.py`.
- Do not change the package models in `src/ai_presenter/packages/models.py`.
- Do not add or edit Q&A items for this slice.
- Do not add broad aliases such as `microphone` or `mic`; those can steal valid device-menu phrasing.
- Do not change `can_operate`, `questionPolicy`, `openSteps`, or risky-word policy.
- Do not touch `.coverage`.
