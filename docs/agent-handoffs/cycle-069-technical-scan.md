# Cycle 069 Technical Scan: meeting-controls-tour / explain-camera-menu JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-camera-menu`
- Entrypoint: `ringcentral.video.toolbar.video-menu`
- Operation: `open`

No runtime, locator, alias, Q&A, diagnostics, or CLI implementation changes are needed.

## Current Source Step

```yaml
- id: explain-camera-menu
  title: Camera menu
  action:
    entrypointId: ringcentral.video.toolbar.video-menu
    operation: open
  narration:
    text: The camera arrow opens camera selection and a shortcut to more video settings, including background
      configuration.
    localizedText:
      zh: 摄像头箭头会打开摄像头选择，并提供进入更多视频设置的入口，包括背景配置。
    placement: during
    actionOffsetMs: 350
```

Relevant route facts:

- Locator matrix: `ringcentral.video.toolbar.video-menu` uses UIA `More`, occurrence `2`, cleanup `Escape`, low repo confidence.
- Evidence index: the route was observed in one empty-room state only; current occurrence and menu labels still need validation.
- Privacy matrix: camera/background/settings may expose room, custom images, device names, and persistent preferences.

## Recommended Japanese Text

```yaml
        ja: カメラ横の矢印は、カメラ選択と、背景設定を含む詳しいビデオ設定へのショートカットを開きます。ここでは場所を説明するだけで、ユーザーの明確な指示なしにカメラを切り替えません。背景やビデオ設定も変更しません。説明したらメニューを閉じます。
```

Rationale:

- Preserves camera arrow, camera selection, more video settings, and background configuration.
- Adds explicit boundaries for camera switching and settings/background changes.
- Mentions menu cleanup because the entrypoint uses `Escape`.
- Avoids device names and current camera state claims.

## Test Updates

Expected count updates:

- `tests/unit/test_material_packages.py`
  - Japanese report `demo_localized_steps`: `19` -> `20`
  - `meeting-controls-tour.localized_steps`: `12` -> `13`
  - Add focused test for `explain-camera-menu`
- `tests/unit/test_cli.py`
  - `Localization report: 19/51 demo steps` -> `20/51`
  - `- meeting-controls-tour: 12/22 narration localized` -> `13/22`
  - first missing `explain-camera-menu` -> `explain-share`
- `tests/unit/test_diagnostics.py`
  - diagnostic detail `19/51 demo steps` -> `20/51 demo steps`

Focused test should assert:

- `step.action.operation == "open"`
- Japanese text exists and has CJK
- Includes `カメラ`, `選択`, `背景`, `ビデオ設定`, `ユーザー`, `明確な指示`, `切り替えません`, `変更しません`, and `閉じます`
- Does not include `Start video` or `Stop video`

## Expected CLI Result

After implementation:

```text
- meeting-controls-tour: 13/22 narration localized
  missing: explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 20/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

Japanese `--require-complete` should still exit `1`.
