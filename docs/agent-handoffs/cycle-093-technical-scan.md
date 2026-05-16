# Cycle 093 Technical Scan - Japanese Raise Hand Narration

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-raise-hand`.

This scan intentionally created only this handoff file. Do not modify YAML, code, tests, source index, profiles, or other docs in this scan.

## Baseline Verified

Command run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current Japanese localization output:

```text
- meeting-control-map-demo: 14/22 narration localized
  missing: control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary

Localization report: 43/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

## YAML Findings

Entrypoint `ringcentral.video.toolbar.raise-hand` currently has:

- `title: Raise hand`
- `area: Meeting toolbar`
- `purpose: Raise or lower hand to request attention.`
- one `openSteps` item:
  - `action: clickWindowControl`
  - `target: Raise hand`
  - `match.alternateTargets: onconf.reactions.REMOVE_RAISE_HAND`
  - `match.controlType: button`
  - `match.cleanup: toggle`
- presenter notes say the button toggles state, shows a hand indicator and toolbar emphasis when active, and should be clicked again to lower the hand after demonstration.

Target demo step `meeting-control-map-demo` -> `control-map-raise-hand` currently has:

- `action.entrypointId: ringcentral.video.toolbar.raise-hand`
- `action.operation: toggle`
- `narration.placement: during`
- `narration.actionOffsetMs: 350`
- English text: "Raise hand is for moderated conversation. It signals that you want attention, and because it is a toggle, I lower the hand again after showing it."
- `localizedText.zh` only; no `localizedText.ja`.

The neighboring completed step `control-map-reactions` is separate and uses `ringcentral.video.toolbar.react` with `operation: open`; keep that separation intact.

## Expected Coverage Numbers After This Round

After adding only `localizedText.ja` to `control-map-raise-hand`:

- Overall Japanese demo narration: `43/51` -> `44/51`
- `meeting-control-map-demo`: `14/22` -> `15/22`
- First missing Japanese step in `meeting-control-map-demo`: `control-map-raise-hand` -> `control-map-more`
- Q&A remains `12/12` localized questions and `12/12` localized answers.
- Japanese aliases remain unchanged: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.
- `--require-complete` for Japanese still fails because later control-map steps remain untranslated.

## Focused Tests To Update/Add

In `tests/unit/test_material_packages.py`:

- Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
  - `report.demo_localized_steps`: `43` -> `44`
  - `meeting-control-map-demo.localized_steps`: `14` -> `15`
  - first missing step: `control-map-raise-hand` -> `control-map-more`
- Add `test_meeting_control_map_has_japanese_raise_hand_narration` near the existing `test_meeting_control_map_has_japanese_reactions_narration`.
- Update adjacent/previous focused tests that currently assert first missing is `control-map-raise-hand` so they now expect `control-map-more`.

In `tests/unit/test_cli.py`:

- In both Japanese localization report tests:
  - `Localization report: 43/51 demo steps` -> `Localization report: 44/51 demo steps`
  - `- meeting-control-map-demo: 14/22 narration localized` -> `- meeting-control-map-demo: 15/22 narration localized`
  - `missing: control-map-raise-hand` -> `missing: control-map-more`
- Keep `missing: explain-leave` absent and Q&A/alias assertions unchanged.

In `tests/unit/test_diagnostics.py`:

- Update `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
  - `43/51 demo steps` -> `44/51 demo steps`
  - keep status `FAIL`
  - keep detail `required ja localization incomplete`
  - keep `12/12 Q&A questions` and `12/12 Q&A answers`.

## Route/Action Assertions

The new focused test should assert:

- `step.action.entrypoint_id == "ringcentral.video.toolbar.raise-hand"`
- `step.action.operation == "toggle"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 350`
- `ja` exists in `step.narration.localized_text` and is non-empty CJK text.
- The raise-hand entrypoint has no Japanese aliases:
  - `assert "ja" not in raise_hand_entrypoint.question_aliases`
  - alias coverage remains `3` entrypoints and `9` aliases.
- The raise-hand entrypoint route stays toggle-safe:
  - `len(raise_hand_entrypoint.open_steps) == 1`
  - `open_step.action == "clickWindowControl"`
  - `open_step.target == "Raise hand"`
  - `open_step.match["alternateTargets"] == "onconf.reactions.REMOVE_RAISE_HAND"`
  - `open_step.match["controlType"] == "button"`
  - `open_step.match["cleanup"] == "toggle"`
- Adjacent step boundaries:
  - `control-map-reactions` still has Japanese narration and remains `operation: open` on `ringcentral.video.toolbar.react`.
  - `control-map-more` should remain without Japanese narration and become the first missing Japanese step.

## Safe Japanese Text Constraints

The Japanese narration should cover:

- `Raise hand` as a moderated-conversation signal, not a general reaction.
- It indicates the user wants attention or a chance to speak without interrupting the speaker.
- It is a visible meeting signal.
- It is a toggle: pressing once raises the hand, pressing again lowers it.
- The presenter should not raise, lower, or leave the hand raised without the user's explicit instruction.
- If the user explicitly confirms a demonstration, the hand must be lowered after the demonstration.

Recommended Japanese text:

```yaml
        ja: Raise hand は、司会進行のある会話で、発話を遮らずに注目してほしいことや発言機会を求めていることを示すトグル操作です。リアクションとは別の、会議中に見えるシグナルです。押すと手を上げた状態になり、もう一度押すと手を下げます。ユーザーが明示的に求めるまで、手を上げたり、手を下げたり、上げたままにしたりしません。実演を明確に確認した場合だけ操作し、実演後は手を下げます。
```

Focused text assertions should include:

- contains: `Raise hand`
- contains: `司会進行`
- contains: `発話を遮らず`
- contains: `発言機会`
- contains: `トグル`
- contains: `会議中に見えるシグナル`
- contains: `手を上げ`
- contains: `手を下げ`
- contains: `ユーザー`
- contains: `明示的`
- contains: `実演後は手を下げます`

Forbidden/guard assertions should include:

- no implication that Raise hand is a reaction: avoid text such as `リアクションを送信`
- no automatic action: avoid `自動`
- no guarantee language: avoid `必ず`
- no unqualified action promises: avoid `送信します`, `選択します`, `クリックします`
- no conflation with opening the Reactions strip: avoid `Reactions を開`
- no leaving the hand active: avoid `上げたままにします`

Be careful with Japanese verb forms: because this step is `operation: toggle`, the text may explain that pressing/clicking toggles the control, but should not say the presenter will perform the toggle unless the user explicitly requested the demonstration and cleanup.

## Source Index Update

When the implementation actually adds the Japanese narration, update `docs/knowledge/ringcentral-video/source-index.md` only if that remains the established pattern for localization slices.

The expected documentation note should advance the Japanese control-map coverage from through `reactions` to through `raise-hand`, and record the first remaining missing step as `control-map-more`.

Do not update the source index during this technical scan.

## Verification Commands

Use the focused pytest set after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_raise_hand_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Confirm the localization report:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected post-implementation lines:

```text
Localization report: 44/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 15/22 narration localized
  missing: control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Confirm Japanese required localization is still incomplete:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected behavior: exit code `1`, with `Localization coverage incomplete for ja.`

Check the final diff is narrow:

```powershell
git diff -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
```

For this scan itself, the only intended file addition is `docs/agent-handoffs/cycle-093-technical-scan.md`.
