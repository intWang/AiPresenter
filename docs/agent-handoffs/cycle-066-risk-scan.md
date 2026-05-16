# Cycle 066 Risk Scan: `explain-microphone` JA Narration

Date: 2026-05-16

## Scope

Assess risks for adding Japanese `localizedText.ja` narration to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-microphone`.

Only this handoff document was edited. The scan read targeted local context:

- `packages/ringcentral-video.yaml`
- `presenter/skills/ringcentral-safety.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- Cycle 065 handoffs for the Chat-to-Microphone boundary
- focused localization tests already present for this slice

## Risk List

1. **Live microphone state change**
   - `ringcentral.video.toolbar.audio` is the live meeting microphone control.
   - Its package purpose is "Toggle mute and unmute in the live meeting."
   - Clicking it can expose the presenter's audio or unexpectedly silence the presenter.
   - The Japanese narration must not imply AiPresenter will toggle the microphone automatically.

2. **Point operation vs toggle operation**
   - The `explain-microphone` demo step uses `operation: point`, not `open`.
   - The entrypoint itself has executable `openSteps` that click the `Mute` or `Unmute` button if invoked as an operation.
   - Any implementation or future test should preserve the step as a point-only explanation, because operating the entrypoint is not the same as pointing at it.

3. **Mute/Unmute label variation**
   - The modeled control targets `Mute` with `alternateTargets: Unmute`.
   - Presenter notes say button text alternates between `Unmute` and `Mute` depending on current state.
   - The adapter has historically recognized exact `Mute microphone` / `Unmute microphone` labels and avoids bare `Mute` / `Unmute` false positives.
   - Japanese narration should keep the visible product label `Mute` while describing the concept, and should avoid claiming a specific current state unless it was observed.

4. **Privacy wording drift**
   - English says `Mute` is the main privacy switch for the microphone and the first control to check before speaking.
   - A loose Japanese translation could sound like an instruction to unmute, switch, or start speaking.
   - The line should say to check the state before speaking, not to change it.

5. **False assurance about audio privacy**
   - Muted UI state does not prove every local input path is safe in all device/OS situations.
   - The narration should frame `Mute` as the meeting microphone privacy control, not as a universal guarantee that no sound can ever be captured or routed.

6. **Boundary with audio menu**
   - The next step, `explain-audio-menu`, owns the microphone arrow and device recovery path.
   - That menu covers microphone choice, speaker choice, leave computer audio, phone audio, and more audio settings.
   - The microphone step should not drift into device switching, speaker selection, audio settings, phone audio, or leave-computer-audio behavior.

7. **Audio menu locator fragility**
   - `ringcentral.video.toolbar.audio-menu` uses `More` occurrence `1` and `cleanup: escape`.
   - Toolbar layout, localized labels, or visible state could make the arrow/menu less stable than the main microphone button.
   - Do not use the microphone narration slice to modify menu locators or prove device-menu behavior.

8. **Previous Chat panel cleanup**
   - Cycle 065 noted that Chat should close before microphone narration.
   - If the Chat side panel remains open while audio privacy is explained, the demo mixes message privacy with microphone privacy and may expose chat content.
   - The microphone slice should assume stable meeting controls are visible before pointing at the mic.

9. **Question routing and aliases**
   - Japanese aliases already exist for the microphone entrypoint: microphone, mute, and audio concepts.
   - Privacy or readiness questions can mention audio while still requiring answer-only handling or multiple controls.
   - Adding narration must not broaden aliases, Q&A routing, or `can_operate` behavior so Japanese "mute/unmute" intent toggles the microphone without explicit confirmation.

10. **Scripted demo vs real meeting distinction**
    - Safety policy allows explaining controls by default, but microphone, camera, reactions, and raise hand create meeting-visible state.
    - Real meetings require user intent before changing microphone state.
    - The handoff owner should keep this as a narration-only localization pass, not an acceptance claim that live toggling is safe.

## Mitigations

- Keep implementation narration-only: add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-microphone`.
- Preserve `action.operation: point`; do not change it to `open`, do not add action offsets, and do not trigger the entrypoint's click steps.
- Keep the visible product label `Mute` in the Japanese line so it maps to the modeled control.
- Mention microphone privacy and readiness at a high level.
- Say the control's state should be checked before speaking.
- Explicitly state that AiPresenter does not switch to unmuted or toggle the mic without clear user instruction.
- Avoid claiming the current state is muted or unmuted unless the observed state is verified elsewhere.
- Keep audio menu content for `explain-audio-menu`; do not mention microphone/speaker device selection, leave computer audio, phone audio, or more audio settings here.
- Do not change entrypoints, locators, `openSteps`, cleanup behavior, aliases, Q&A, runtime behavior, tests, or unrelated docs unless a separate owner explicitly owns that scope.
- Manual validation, if any, should use a disposable meeting and a known-safe microphone setup.

## Must Verify

- YAML shape:
  - `localizedText.ja` is added under `meeting-controls-tour` -> `explain-microphone` -> `narration`.
  - Existing English text, Chinese `localizedText.zh`, `placement: before`, `entrypointId: ringcentral.video.toolbar.audio`, and `operation: point` remain unchanged.
  - No `openSteps`, locator, cleanup, alias, Q&A, runtime, or unrelated flow changes are bundled into this narration slice.

- Text safety:
  - Includes the visible label `Mute`.
  - Mentions microphone/mic privacy.
  - Mentions checking the state before speaking.
  - Does not say AiPresenter will unmute, mute, switch, toggle, click, recover devices, choose a microphone, choose a speaker, leave computer audio, or use phone audio by default.
  - Does not claim the current mic is muted or unmuted unless that state is explicitly verified by the live observation path.
  - Does not blur self microphone mute with participant mute or host controls.

- Live-state behavior:
  - The scripted step points at the microphone control only.
  - Running the tour does not change local microphone mute state during `explain-microphone`.
  - If manual validation observes a state change, treat it as a failure unless the tester intentionally clicked outside this step.
  - The Chat panel is closed or the meeting toolbar is otherwise stable before microphone narration begins.

- Boundary with audio menu:
  - `explain-microphone` stays about the main mute/privacy control.
  - Device choice, speaker choice, audio level indicators, leave computer audio, phone audio, and more audio settings remain owned by `explain-audio-menu`.
  - The next missing Japanese step after implementation should be `explain-audio-menu`, not skipped or bundled.

- Expected localization movement after implementation:
  - Overall Japanese demo narration should move from `16/51` to `17/51`.
  - `meeting-controls-tour` Japanese narration should move from `9/22` to `10/22`.
  - First missing `meeting-controls-tour` step should advance from `explain-microphone` to `explain-audio-menu`.
  - Q&A localization should remain `12/12` questions and `12/12` answers.
  - Japanese aliases should remain `3/27 entrypoints (9 aliases)`.
  - `--require-complete` for Japanese should still fail because later demo narration remains incomplete.

- Current-tree test expectation note:
  - Focused tests already appear advanced for this slice.
  - `test_meeting_controls_tour_has_japanese_microphone_narration` expects `operation == "point"` and Japanese text containing `Mute`, microphone, privacy, before-speaking/check concepts, unmute concept, and "does not switch" language.
  - CLI and diagnostics coverage tests expect `17/51`, `meeting-controls-tour: 10/22`, and `missing: explain-audio-menu`.

- Suggested focused checks after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_microphone_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Manual validation should be limited to a disposable RingCentral meeting. Before and after the microphone step, record only generic state such as "muted state unchanged" or "unmuted state unchanged"; do not record participant audio, participant names, chat content, invite links, or meeting IDs.

## Recommendation

Proceed as a narrow narration-only slice if the Japanese line keeps `Mute` mapped to the visible microphone control, frames it as the main privacy/readiness check before speaking, and explicitly says AiPresenter will not switch to unmuted or toggle the microphone without clear user instruction. Do not batch this with `explain-audio-menu`, locator changes, alias/Q&A changes, runtime behavior, or any live microphone operation acceptance.

## Changed Files

- `docs/agent-handoffs/cycle-066-risk-scan.md`
