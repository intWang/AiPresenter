# Cycle 088 Technical Scan: control-map-audio-menu JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-audio-menu
  title: Audio menu
  action:
    entrypointId: ringcentral.video.toolbar.audio-menu
    operation: open
  narration:
    text: The audio menu is the recovery tool when sound is wrong. It lets you switch microphone and speaker,
      leave computer audio, use phone audio, or open deeper audio settings.
    localizedText:
      zh: 麦克风旁边的菜单是排查声音问题的入口。可以换麦克风和扬声器，也可以离开电脑音频、改用电话音频，或进入更完整的音频设置。
    placement: during
    actionOffsetMs: 350
```

Current gap: `control-map-audio-menu` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.toolbar.audio-menu`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `350`

This slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-audio-menu`.

Baseline verified with `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja`: JA is `38/51` overall, `meeting-control-map-demo` is `9/22`, and the first missing step is `control-map-audio-menu`.

## Entrypoint Route

Entrypoint: `ringcentral.video.toolbar.audio-menu`

```yaml
- id: ringcentral.video.toolbar.audio-menu
  title: Microphone and speaker menu
  area: Meeting toolbar
  purpose: Open microphone and speaker device controls, audio level indicators, leave-computer-audio, phone-audio,
    and more audio settings.
  questionAliases:
    zh:
    - 音频设置
    - 换麦克风
    - 换扬声器
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '1'
      controlType: button
      cleanup: escape
  presenterNotes:
  - Observed menu sections include Microphone, Speaker, Leave computer audio, Use phone audio, and More audio settings.
  - Use this when explaining how to recover from the wrong microphone or speaker.
  - If a system-default-audio-devices toast appears, close it only when visible; its close coordinate overlaps Add
    coworkers on the clean main screen.
```

Route details:

- Area: `Meeting toolbar`
- Purpose: opens microphone/speaker device controls, audio level indicators, leave-computer-audio, phone-audio, and deeper audio settings.
- Route action: `clickWindowControl`
- Target: `More`
- Match: `occurrence: '1'`, `controlType: button`, `cleanup: escape`
- Existing Japanese aliases: none on this entrypoint. Do not add aliases in this slice.

Presenter-note semantics to preserve:

- Menu sections include `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, and `More audio settings`.
- This entrypoint is for explaining recovery from the wrong microphone or speaker.
- A system-default-audio-devices toast may appear; only close it when visible because its close coordinate overlaps `Add coworkers` on a clean main screen.

Important nuance: this demo step is `operation: open`, so the menu is opened and then cleaned up with Escape. The narration should explain device recovery options without implying that AiPresenter selects a device, leaves computer audio, switches to phone audio, opens settings, tests sound, reads device names aloud, or changes the live audio route.

## Test Updates

Expected coverage deltas after adding only this one JA narration:

- Overall JA demo narration: `38/51` -> `39/51`
- `meeting-control-map-demo`: `9/22` -> `10/22`
- First missing step: `control-map-audio-menu` -> `control-map-camera`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

Recommended focused test updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update localized steps from `38` to `39`, `meeting-control-map-demo` from `9` to `10`, and first missing from `control-map-audio-menu` to `control-map-camera`.
  - Add `test_meeting_control_map_has_japanese_audio_menu_narration` near `test_meeting_control_map_has_japanese_microphone_narration`.
  - Assert `step.action.entrypoint_id == "ringcentral.video.toolbar.audio-menu"`, `step.action.operation == "open"`, `step.narration.placement == "during"`, and `step.narration.action_offset_ms == 350`.
  - Assert the route has one open step using `clickWindowControl`, target `More`, `occurrence == "1"`, `controlType == "button"`, and `cleanup == "escape"`.
  - Assert `audio_menu_entrypoint.question_aliases` has no `ja` key and that global Japanese alias coverage remains unchanged.
  - Assert presenter notes mention `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, `More audio settings`, wrong microphone or speaker recovery, and toast-close caution.
  - Assert JA text exists, has CJK, and includes `マイク`, `スピーカー`, `音声`, `メニュー`, `コンピューター音声`, `電話音声`, `音声設定`, `復旧` or `直す`, `ユーザー`, and `明示的`.
  - Assert JA text does not include unsafe action claims such as `選択します`, `切り替えます`, `退出します`, `変更します`, `開きます` for deeper settings, `テストします`, `接続します`, `読み上げます`, `自動`, or `必ず`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests, update `Localization report: 38/51 demo steps` -> `Localization report: 39/51 demo steps`.
  - Update `- meeting-control-map-demo: 9/22 narration localized` -> `- meeting-control-map-demo: 10/22 narration localized`.
  - Update `missing: control-map-audio-menu` -> `missing: control-map-camera`.
  - Keep `missing: explain-leave` absent, Q&A at `12/12`, and alias coverage at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `38/51 demo steps` -> `39/51 demo steps`.
  - Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red state before YAML implementation:

- Updated count assertions fail because current state is `38/51` overall and `9/22` for `meeting-control-map-demo`.
- Updated first-missing assertion fails because current first missing step is `control-map-audio-menu`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-audio-menu`.

Expected green state after this slice:

- Overall JA demo narration: `39/51`
- `meeting-control-map-demo`: `10/22`
- First missing JA step in that flow: `control-map-camera`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: 音声に問題があるときは、マイク横のメニューが復旧の入口になります。ここではマイクとスピーカーの選択、コンピューター音声からの退出、電話音声の利用、さらに詳しい音声設定へ進む場所を確認できます。ユーザーが明示的に求めるまで、デバイスや音声接続は切り替えません。
```

Why this wording:

- Preserves the source meaning: the audio menu is the recovery tool when sound is wrong.
- Reflects presenter notes: the menu exposes microphone, speaker, computer audio, phone audio, and more audio settings.
- Fits `operation: open`, `placement: during`, and `actionOffsetMs: 350` by describing the opened menu after it appears.
- Keeps recovery explain-only: it identifies where options live without changing device routes or audio connection.

Acceptable shorter variant:

```yaml
        ja: マイク横の音声メニューは、音が正しくないときの復旧入口です。マイク、スピーカー、コンピューター音声、電話音声、詳しい音声設定の場所を確認できますが、ユーザーが明示的に求めるまでデバイスや接続は変更しません。
```

Avoid wording such as:

- `マイクを選択します`
- `スピーカーを切り替えます`
- `コンピューター音声から退出します`
- `電話音声に接続します`
- `音声設定を開きます`
- `デバイス名を読み上げます`
- `音声をテストします`
- `自動で切り替えます`
- `必ず変更します`

## Verification Commands

Focused test command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_audio_menu_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 39/51 demo steps
- meeting-control-map-demo: 10/22 narration localized
  missing: control-map-camera
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- This scan writes only `docs/agent-handoffs/cycle-088-technical-scan.md`; do not edit YAML, code, tests, source index, profiles, or other docs in this scan.
- Implementation should edit only the targeted JA narration and directly related test expectations.
- Do not change `control-map-audio-menu` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.toolbar.audio-menu` route semantics: keep `clickWindowControl`, target `More`, `occurrence: '1'`, `controlType: button`, and `cleanup: escape`.
- Do not add or change Japanese aliases; current JA alias coverage should remain `3/27` entrypoints and `9` aliases.
- Do not localize `control-map-camera` or any later `meeting-control-map-demo` step in this slice.
- Do not broaden into Q&A, Chinese/English narration, presenter notes, locator strategy, diagnostics behavior, CLI formatting, profiles, source-index updates, or acceptance evidence.
- Do not imply the presenter changes microphone or speaker device, leaves computer audio, uses phone audio, opens deeper settings, tests sound, reads device names, or changes any live audio route unless the user explicitly asks and visible state has been verified.
- Do not remove menu cleanup; this route opens a menu and should close it with Escape after explanation.
- Do not revert or overwrite concurrent edits from other agents.
