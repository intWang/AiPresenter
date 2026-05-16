# Cycle 087 Technical Scan: control-map-microphone JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-microphone
  title: Microphone
  action:
    entrypointId: ringcentral.video.toolbar.audio
    operation: point
  narration:
    text: Now we move into media readiness. The microphone button is the main privacy switch for speaking, so it
      is the first control to check before you contribute.
    localizedText:
      zh: 现在进入音视频准备区。麦克风是发言前最重要的隐私开关；开口前，先看这里是不是静音。
    placement: before
```

Current gap: `control-map-microphone` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.toolbar.audio`
- `operation`: `point`
- `placement`: `before`
- `actionOffsetMs`: default `0` / absent in YAML

This slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-microphone`.

Baseline verified with `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja`: JA is `37/51` overall, `meeting-control-map-demo` is `8/22`, and the first missing step is `control-map-microphone`.

## Entrypoint Route

Entrypoint: `ringcentral.video.toolbar.audio`

```yaml
- id: ringcentral.video.toolbar.audio
  title: Microphone control
  area: Meeting toolbar
  purpose: Toggle mute and unmute in the live meeting.
  questionAliases:
    ja:
    - マイク
    - ミュート
    - 音声
    zh:
    - 麦克风
    - 静音
    - 声音
  openSteps:
  - action: clickWindowControl
    target: Mute
    match:
      alternateTargets: Unmute
      controlType: button
  presenterNotes:
  - Button text alternates between Unmute and Mute depending on current state.
  - Use this entry point to explain audio privacy and meeting readiness.
```

Route details:

- Area: `Meeting toolbar`
- Purpose: `Toggle mute and unmute in the live meeting.`
- Route action: `clickWindowControl`
- Target: `Mute`
- Alternate target: `Unmute`
- Match: `controlType: button`
- Cleanup: none
- Existing Japanese aliases are exactly `["マイク", "ミュート", "音声"]`; this slice should not add aliases.

Presenter-note semantics to preserve:

- Button text alternates between `Unmute` and `Mute` depending on current state.
- Use this entry point to explain audio privacy and meeting readiness.

Important nuance: the demo step is `operation: point`, not `open` or `toggle`. The narration should explain the microphone control and readiness check without implying the demo clicked it or changed mute state.

## Test Updates

Expected coverage deltas after adding only this one JA narration:

- Overall JA demo narration: `37/51` -> `38/51`
- `meeting-control-map-demo`: `8/22` -> `9/22`
- First missing step: `control-map-microphone` -> `control-map-audio-menu`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

Recommended focused test updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update localized steps from `37` to `38`, `meeting-control-map-demo` from `8` to `9`, and first missing from `control-map-microphone` to `control-map-audio-menu`.
  - Add `test_meeting_control_map_has_japanese_microphone_narration` near `test_meeting_control_map_has_japanese_chat_narration`.
  - Assert `step.action.entrypoint_id == "ringcentral.video.toolbar.audio"`, `step.action.operation == "point"`, `step.narration.placement == "before"`, and `step.narration.action_offset_ms == 0`.
  - Assert the route has one open step using `clickWindowControl`, target `Mute`, `alternateTargets == "Unmute"`, and `controlType == "button"`.
  - Assert `cleanup` is not present on the microphone route match.
  - Assert JA aliases remain exactly `["マイク", "ミュート", "音声"]`.
  - Assert presenter notes mention text alternating between `Unmute` and `Mute`, current state, audio privacy, and meeting readiness.
  - Assert JA text exists, has CJK, and includes `Microphone`, `メディア`, `準備`, `発言`, `音声`, `ミュート`, `プライバシー`, `スイッチ`, `確認`, `ユーザー`, and `明示的`.
  - Assert JA text does not imply changing real media state, such as `クリックします`, `押します`, `切り替えます`, `ミュートします`, `ミュート解除します`, `オンにします`, `オフにします`, `変更します`, `操作します`, `自動`, or `必ず`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests, update `Localization report: 37/51 demo steps` -> `Localization report: 38/51 demo steps`.
  - Update `- meeting-control-map-demo: 8/22 narration localized` -> `- meeting-control-map-demo: 9/22 narration localized`.
  - Update `missing: control-map-microphone` -> `missing: control-map-audio-menu`.
  - Keep `missing: explain-leave` absent, Q&A at `12/12`, and alias coverage at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `37/51 demo steps` -> `38/51 demo steps`.
  - Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red state before YAML implementation:

- Updated count assertions fail because current state is `37/51` overall and `8/22` for `meeting-control-map-demo`.
- Updated first-missing assertion fails because current first missing step is `control-map-microphone`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-microphone`.

Expected green state after this slice:

- Overall JA demo narration: `38/51`
- `meeting-control-map-demo`: `9/22`
- First missing JA step in that flow: `control-map-audio-menu`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: ここからメディアの準備状況を確認します。Microphone ボタンは、発言する前に自分の音声がミュートかどうかを確認するための主要なプライバシースイッチです。ここでは場所と状態の見方を説明するだけで、ユーザーが明示的に求めるまでミュートやミュート解除は切り替えません。
```

Why this wording:

- Preserves the source meaning: this starts the media-readiness area and the microphone is the first control to check before speaking.
- Reflects presenter notes: microphone state can show `Mute` or `Unmute`; the entry point is for audio privacy and meeting readiness.
- Keeps the `point` operation explain-only by saying the presenter explains location and state, not a click or toggle.
- Avoids claiming the presenter mutes, unmutes, changes audio state, or performs the control without explicit user intent.

Acceptable shorter variant:

```yaml
        ja: ここから音声と映像の準備状況を見ます。Microphone は発言前に確認する主要なプライバシースイッチで、自分の音声がミュートかどうかを示します。ここでは場所と状態だけを説明し、ユーザーが明示的に求めるまで切り替えません。
```

Avoid wording such as:

- `Microphone をクリックします`
- `Mute を押します`
- `ミュートします`
- `ミュート解除します`
- `音声をオンにします`
- `音声をオフにします`
- `状態を切り替えます`
- `マイクを操作します`
- `自動でミュートを変更します`
- `必ず切り替えます`

## Verification Commands

Focused test command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_microphone_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 38/51 demo steps
- meeting-control-map-demo: 9/22 narration localized
  missing: control-map-audio-menu
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- This scan writes only `docs/agent-handoffs/cycle-087-technical-scan.md`; do not edit YAML, code, tests, source index, profiles, or other docs in this scan.
- Implementation should edit only the targeted JA narration and directly related test expectations.
- Do not change `control-map-microphone` action semantics: keep `entrypointId`, `operation`, `placement`, and default/no `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.toolbar.audio` route semantics: keep `clickWindowControl`, target `Mute`, `alternateTargets: Unmute`, `controlType: button`, and no cleanup.
- Do not add or change Japanese aliases; current JA alias coverage should remain `3/27` entrypoints and `9` aliases.
- Do not localize `control-map-audio-menu` or any later `meeting-control-map-demo` step in this slice.
- Do not broaden into Q&A, Chinese/English narration, presenter notes, locator strategy, diagnostics behavior, CLI formatting, profiles, source-index updates, or acceptance evidence.
- Do not imply the presenter clicks the microphone button, mutes, unmutes, toggles audio, changes media state, or performs recovery actions unless the user explicitly asks and visible state has been verified.
- Do not add cleanup to this route; the microphone step is a point/readiness explanation, not a panel or dialog.
- Do not revert or overwrite concurrent edits from other agents.
