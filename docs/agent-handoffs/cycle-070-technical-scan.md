# Cycle 070 Technical Scan: meeting-controls-tour / explain-share JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-share`
- Entrypoint: `ringcentral.video.toolbar.share`
- Operation: `open`

No runtime, locator, alias, Q&A, diagnostics, or CLI implementation changes are needed.

## Current Source Step

```yaml
- id: explain-share
  title: Share
  action:
    entrypointId: ringcentral.video.toolbar.share
    operation: open
  narration:
    text: Share opens the picker for your screen or application windows. It can also share system audio, but I
      do not press the final Share button unless you confirm.
    localizedText:
      zh: Share 会打开屏幕或应用窗口选择器，也可以共享系统音频。但在你确认要展示哪个内容前，我不会点击最终的 Share 按钮。
    placement: during
    actionOffsetMs: 400
```

Relevant route facts:

- Locator matrix: `ringcentral.video.toolbar.share` uses UIA `Share`, cleanup `Escape`, medium repo confidence.
- Package presenter notes: observed picker includes entire screen, application windows, Share system audio, and Share.
- Privacy matrix: shared applications, documents, and desktop content are sensitive; describing content requires explicit approval and verified observation.

## Recommended Japanese Text

```yaml
        ja: Share は画面またはアプリケーションウィンドウの選択画面を開きます。システム音声も共有できますが、表示する内容をユーザーが確認するまで、最終的な Share ボタンは押しません。共有候補や画面内容は、明確な許可なしに読み上げません。説明したら選択画面を閉じます。
```

Rationale:

- Preserves Share, screen/application window picker, system audio, and final Share confirmation.
- Adds privacy boundary for picker candidates and shared content.
- Mentions cleanup because the route uses `Escape`.
- Does not claim that AiPresenter chooses content or starts sharing.

## Test Updates

Expected count updates:

- `tests/unit/test_material_packages.py`
  - Japanese report `demo_localized_steps`: `20` -> `21`
  - `meeting-controls-tour.localized_steps`: `13` -> `14`
  - Add focused test for `explain-share`
- `tests/unit/test_cli.py`
  - `Localization report: 20/51 demo steps` -> `21/51`
  - `- meeting-controls-tour: 13/22 narration localized` -> `14/22`
  - first missing `explain-share` -> `explain-reactions`
- `tests/unit/test_diagnostics.py`
  - diagnostic detail `20/51 demo steps` -> `21/51 demo steps`

Focused test should assert:

- `step.action.operation == "open"`
- Japanese text exists and has CJK
- Includes `Share`, `画面`, `アプリケーション`, `ウィンドウ`, `システム音声`, `ユーザー`, `確認`, `最終的な Share ボタン`, `押しません`, `読み上げません`, and `閉じます`
- Does not include a claim that sharing starts automatically.

## Expected CLI Result

After implementation:

```text
- meeting-controls-tour: 14/22 narration localized
  missing: explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 21/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

Japanese `--require-complete` should still exit `1`.
