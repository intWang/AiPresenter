# Cycle 155 Technical Scan

## Recommendation

Proceed with a narrow TDD slice for `Where is the microphone button?`.

Expected behavior:
- route to `ringcentral.video.toolbar.audio`
- keep `can_operate is False`
- create no question interrupt step

This is safe as a package-alias fix. Current behavior routes the question to
`ringcentral.video.toolbar.audio-menu`, while already keeping `can_operate=False`
and no interrupt. The implementation should not change runtime matching,
operation policy, or menu behavior.

## Scan Notes

`packages/ringcentral-video.yaml:204` defines
`ringcentral.video.toolbar.audio` as `Microphone control`; its purpose contains
`Toggle mute and unmute in the live meeting`, so the question runtime marks it
not operable.

`packages/ringcentral-video.yaml:230` defines
`ringcentral.video.toolbar.audio-menu` as the microphone and speaker menu. Its
purpose contains microphone, speaker, leave-computer-audio, phone-audio, and
more audio settings, which explains why token scoring currently wins for
`Where is the microphone button?`.

`tests/unit/test_questions.py` already has nearby safety patterns:
- Spanish location route for the mute button maps to
  `ringcentral.video.toolbar.audio` with `can_operate=False`.
- Japanese `microphone is where` coverage maps to
  `ringcentral.video.toolbar.audio` with `can_operate=False`.
- Several tests assert `create_question_interrupt_step(package, response) is None`
  for non-operable answers.

Runtime scan:
- `src/ai_presenter/runtime/questions.py:407` checks package aliases before token
  scoring.
- `src/ai_presenter/runtime/questions.py:445` matches package aliases by
  substring against the normalized question.
- `src/ai_presenter/runtime/questions.py:555` computes `can_operate`; audio stays
  false because risky words include `toggle`, `mute`, and `unmute`.
- `src/ai_presenter/runtime/session.py:88` returns no interrupt whenever
  `response.can_operate` is false.

Observed current probe:

```text
question: Where is the microphone button?
entrypoint: ringcentral.video.toolbar.audio-menu
can_operate: False
interrupt step is None: True
```

## Red Method

Add this test to `tests/unit/test_questions.py`, near the existing RingCentral
question-routing tests:

```python
def test_ringcentral_microphone_button_location_routes_to_audio_without_interrupt(
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

Run the red check without coverage so `.coverage` is not touched:

```powershell
.\.venv\Scripts\pytest tests\unit\test_questions.py::test_ringcentral_microphone_button_location_routes_to_audio_without_interrupt -q --no-cov
```

Expected red failure before the package alias:

```text
assert 'ringcentral.video.toolbar.audio-menu' == 'ringcentral.video.toolbar.audio'
```

## Green Implementation

Modify only the `questionAliases` block for
`ringcentral.video.toolbar.audio` in `packages/ringcentral-video.yaml`:

```yaml
  questionAliases:
    en:
    - microphone button
    es:
    - ubicacion del boton mute
    - control del microfono en la barra
    - estado del microfono en reunion
```

The exact Spanish lines above are shown without accents only to avoid terminal
encoding confusion in this handoff. Preserve the existing accented Spanish text
in the file when applying the change.

Do not add the alias to `ringcentral.video.toolbar.audio-menu`. The phrase
`microphone button` names the toolbar button, not the device menu.

## Verification Commands

Use `--no-cov` for pytest commands in this slice because repository pytest
defaults write coverage data.

```powershell
.\.venv\Scripts\pytest tests\unit\test_questions.py::test_ringcentral_microphone_button_location_routes_to_audio_without_interrupt -q --no-cov
.\.venv\Scripts\pytest tests\unit\test_questions.py -q --no-cov
git diff --check -- tests\unit\test_questions.py packages\ringcentral-video.yaml
```

Optional package-regression spot checks:

```powershell
.\.venv\Scripts\pytest tests\unit\test_material_packages.py::test_ringcentral_package_owns_spanish_aliases_for_location_routes tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes -q --no-cov
```

## No-Go Scope

- Do not edit runtime matcher scoring or alias ordering.
- Do not edit `src/ai_presenter/runtime/questions.py`.
- Do not make `ringcentral.video.toolbar.audio` operable from questions.
- Do not create an interrupt for this question.
- Do not change audio-menu, video, camera, settings, or QA routing.
- Do not edit profiles, README, existing docs, or `.coverage`.
