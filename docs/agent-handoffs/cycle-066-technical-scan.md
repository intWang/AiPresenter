# Cycle 066 Technical Scan: meeting-controls-tour / explain-microphone JA narration

## Scope

Scan only for the next implementation pass. The proposed implementation should add Japanese `localizedText.ja` narration to one step:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-microphone`
- Entrypoint: `ringcentral.video.toolbar.audio`
- Operation: `point`

Do not change runtime behavior, open steps, action offsets, aliases, Q&A, flow order, diagnostics logic, CLI logic, tests, YAML outside this one narration entry, git state, or unrelated docs as part of this scan.

## Local Context Read

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- Recent handoffs:
  - `docs/agent-handoffs/cycle-065-technical-scan.md`
  - `docs/agent-handoffs/cycle-065-implementation.md`
  - `docs/agent-handoffs/cycle-065-review.md`
  - `docs/agent-handoffs/cycle-065-summary.md`
  - `docs/agent-handoffs/cycle-065-risk-scan.md`

Current verified baseline from:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

- `Localization report: 16/51 demo steps`
- `meeting-controls-tour: 9/22 narration localized`
- first missing `meeting-controls-tour` step: `explain-microphone`
- Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- Japanese aliases remain partial: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Important current-tree note: the focused Cycle 066 tests already appear advanced to the expected post-implementation state. The package YAML has not yet been advanced for `explain-microphone`, so the implementation owner should expect the focused tests to fail until the YAML gets the Japanese narration. I confirmed this with the focused pytest command in the verification section: `5 failed`.

## Source Step

Current English narration:

```yaml
text: Now the media controls. Mute is the main privacy switch for your microphone. Before speaking, this is
  the first control to check.
```

Current Chinese narration:

```yaml
zh: 现在看媒体控制。Mute 是麦克风的主要隐私开关；发言前，最先应该确认这里的状态。
```

Relevant entrypoint details for `ringcentral.video.toolbar.audio`:

- Title: `Microphone control`
- Area: `Meeting toolbar`
- Purpose: `Toggle mute and unmute in the live meeting.`
- Open step targets `Mute` with alternate target `Unmute`, but this tour step uses operation `point`, not `open` or `toggle`.
- Presenter notes say button text alternates between `Unmute` and `Mute` depending on current state.
- Presenter notes say to use this entry point to explain audio privacy and meeting readiness.

Relevant prior slices:

- Cycle 063 localized `explain-invite`, preserving invite/link privacy.
- Cycle 064 localized `explain-participants`, preserving roster privacy.
- Cycle 065 localized `explain-chat`, preserving message privacy and making `explain-microphone` the first missing Japanese step.
- Cycle 065 summary explicitly says `explain-microphone` should get its own live-state risk review because mute/unmute affects meeting-visible audio privacy.

## Recommended Japanese Wording

Recommended insertion under `narration.localizedText`:

```yaml
        ja: 次はメディアコントロールです。Mute はマイクの主なプライバシースイッチです。話す前に、まずここで現在の状態を確認します。ユーザーの明確な指示なしに、ミュート解除したりマイク状態を切り替えたりしません。
```

Rationale:

- Preserves visible UI label `Mute`.
- Names `マイク` and `プライバシー`, matching the microphone/audio privacy intent.
- Keeps the English meaning: media controls, Mute as the primary microphone privacy switch, and checking this control before speaking.
- Adds the live-state safety boundary missing from the terse English/Chinese source: do not unmute or toggle microphone state unless the user explicitly instructs it.
- Avoids promising the presenter knows whether the user is currently muted unless the visible UI state has been checked.
- Avoids adding device-routing details that belong to the following `explain-audio-menu` step.

## Expected Count Changes

After adding only this `localizedText.ja` entry:

- Overall Japanese demo narration: `16/51` -> `17/51`
- `meeting-controls-tour`: `9/22` -> `10/22`
- First missing `meeting-controls-tour` step should advance from `explain-microphone` to `explain-audio-menu`
- Q&A counts should remain `12/12` questions and `12/12` answers
- Japanese alias counts should remain `questionAliases.ja present on 3/27 entrypoints (9 aliases)`
- `--require-complete` for Japanese should still fail because the package remains partially localized.

## Tests To Update/Add

The current test files already contain the expected Cycle 066 assertions. If the implementation owner is working from this tree, no test edits should be needed; the YAML narration should turn the existing red tests green.

Existing expected test coverage to preserve:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - expects `report.demo_localized_steps == 17`
  - expects `report.flow_by_id["meeting-controls-tour"].localized_steps == 10`
  - keeps `report.demo_total_steps == 51`
  - keeps `meeting-controls-tour` total at `22`
  - keeps Q&A and alias expectations unchanged

- `tests/unit/test_material_packages.py::test_meeting_controls_tour_has_japanese_microphone_narration`
  - asserts `step.action.operation == "point"`
  - asserts Japanese text exists and contains CJK
  - asserts `Mute`
  - asserts `マイク`
  - asserts `プライバシー`
  - asserts `話す前`
  - asserts `確認`
  - asserts `ミュート解除`
  - asserts `切り替えません`

- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - expects `Localization report: 17/51 demo steps`
  - expects `- meeting-controls-tour: 10/22 narration localized`
  - expects `missing: explain-audio-menu`
  - keeps Q&A and alias lines unchanged

- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`
  - expects exit code `1`
  - expects `Localization report: 17/51 demo steps`
  - expects `- meeting-controls-tour: 10/22 narration localized`
  - expects `missing: explain-audio-menu`
  - keeps `Localization coverage incomplete for ja.`

- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
  - expects diagnostic detail to include `17/51 demo steps`
  - keeps `required ja localization incomplete`
  - keeps `12/12 Q&A questions` and `12/12 Q&A answers`

If applying this scan to a branch that does not already have the microphone-focused test, add it with the assertions listed above. Do not add Japanese `questionAliases` in this pass; `ringcentral.video.toolbar.audio` already has Japanese aliases, and expected alias counts above assume no alias change.

## Expected CLI Output Changes

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected relevant output after implementation:

```text
Language: ja
- meeting-controls-tour: 10/22 narration localized
  missing: explain-audio-menu, explain-camera, explain-camera-menu, explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
Localization report: 17/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected result after implementation:

- Exit code: `1`
- Includes `Localization report: 17/51 demo steps`
- Includes `- meeting-controls-tour: 10/22 narration localized`
- Includes `missing: explain-audio-menu`
- Includes `Localization coverage incomplete for ja.`

## Verification Commands

Run targeted tests with the project venv:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_microphone_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected pre-implementation result in this current tree:

- `5 failed`
- failures are the advanced `17/51`, `10/22`, and `localized_text["ja"]` expectations for `explain-microphone`

Optional broader package-localization sweep:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k "japanese or localization_status or microphone"
```

CLI smoke checks:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Optional doctor localization preflight:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization
```

Expected doctor result remains nonzero because Japanese localization is still incomplete, but the localization detail should move to `17/51 demo steps`.

## Notes For Implementer

- Keep the YAML insertion under `localizedText.ja`, not `localizedText.jp`.
- Preserve existing English text, Chinese `localizedText.zh`, and `placement: before`.
- Keep product/UI labels in English where they match visible UI: `Mute`.
- This step is `operation: point`; do not change it to `open` or `toggle`.
- Do not click or toggle the live microphone in this narration-only pass.
- Do not claim the microphone is muted or unmuted unless the visible UI state is verified.
- Keep audio-device routing, speaker selection, phone audio, and settings language for the following `explain-audio-menu` slice.
- Do not change aliases, Q&A, route matching, diagnostics logic, or CLI output formatting.
