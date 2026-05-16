# Cycle 094 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-more` -> `narration.localizedText.ja`.

The user value is orientation and safety. In RingCentral Video, `More` is the overflow hub for secondary meeting actions: tools that users do need, but usually not every minute, and often not without intent. A control-map tour should help the user recognize that `More` is where deeper meeting tools live, without treating every item inside it as something to click during the tour.

This matters because the visible toolbar can make high-frequency actions feel obvious while hiding important secondary actions behind one label. Users need to know that `More` is not a random extras menu; it is the navigation point for features such as recording, notes/transcript variants, background, settings, and sometimes leave-related or meeting-management actions depending on layout. The narration should make the hub useful without over-teaching each downstream feature, because later steps cover those boundaries separately.

Boundary with adjacent and downstream controls:

- `More` is the entry point and grouping concept. It can be opened to show that secondary actions exist.
- `Recording` changes meeting state and may involve participant consent, policy, and host permissions. It is high risk and explain-only unless explicitly confirmed.
- `Notes and Transcript` can expose meeting note-taking or transcript surfaces, and may also be connected to recording-like state changes. Opening a panel for explanation is different from starting notes, transcript, or recording.
- `Background` changes how the user appears and can affect privacy and presentation quality. It is less destructive than recording, but still changes visible meeting output.
- `Settings` is a broad configuration center. It can change audio, video, background, translation, join preferences, and general meeting behavior, so it should be treated as deliberate configuration rather than casual discovery.
- `Leave` is an exit path that can end the user's presence in the meeting. It is outside the `More` hub in the current control-map step sequence, but the broader overflow mental model should still make clear that exit/destructive actions require confirmation.

## Presenter behavior

The presenter should treat `control-map-more` as an `open` operation on `ringcentral.video.toolbar.more`. It may open the menu as a navigation step, name the kinds of secondary actions grouped there, and then leave the menu without selecting any item.

Required behavior in real meeting context:

- Explain `More` as the overflow hub or advanced shelf for secondary meeting actions.
- Preserve the current observed layout nuance: in this build, `Notes` is already on the toolbar, while `More` gathers lower-frequency or more careful actions such as recording, background, and settings.
- State that this step explains the entry point only.
- Do not click `Start recording`, start/stop notes, change background, open or change settings, or click leave/end actions as part of this step.
- Do not imply that opening `More` approves any downstream action.
- Close or leave the opened menu in a neutral state before moving on, following existing cleanup expectations.
- Keep the narration short enough for a control-map pass; detailed risk handling belongs to the later `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, and `control-map-leave` steps.

Good semantics: "More is where the deeper or less frequent meeting tools are collected; here I only show the entrance and do not start recording or change settings unless the user clearly asks." Avoid language that suggests More itself is dangerous, that every item is hidden or unavailable, or that AiPresenter will inspect private meeting content inside these surfaces.

## Localization tone

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` style: calm, concise, and safety-aware. Keep UI labels like `More`, `Notes`, `Start recording`, `Background`, and `Settings` in English when naming the interface.

Recommended tone points:

- Use `More` plus a Japanese explanation such as `二次的な会議操作の入口`, `拡張メニュー`, or `より深い会議ツールへの入口`.
- Preserve the hub metaphor without sounding playful: `高度な操作棚` is acceptable if it stays practical, but `拡張メニュー` or `入口` may be clearer for spoken narration.
- Describe frequency and risk together: `使用頻度が低い操作や、慎重に扱う操作`.
- Mention `Start recording`, `Background`, and `Settings`; mention `Notes` only as the current-layout boundary that is already on the toolbar.
- Include the safety boundary directly: `ここでは入口だけを説明し、録画の開始、背景や設定の変更、退出操作はユーザーが明確に求めるまで実行しません`.
- Keep it spoken and compact. The line should feel like a meeting coach orienting the user, not a compliance notice.

Suggested semantic shape, not a required final string:

```text
最後に More は、二次的な会議操作をまとめた拡張メニューです。このビルドでは Notes はすでにツールバー上にあり、More には Start recording、Background、Settings など、使用頻度が低い操作や慎重に扱う操作がまとまっています。ここでは入口だけを説明し、録画の開始、背景や設定の変更、退出につながる操作は、ユーザーが明確に求めるまで実行しません。
```

## Out of scope

- Do not edit `packages/ringcentral-video.yaml` in this demand-analysis handoff.
- Do not add Japanese narration for `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change Chinese, English, Q&A, aliases, presenter notes, locator metadata, operation definitions, cleanup behavior, source-index text, or tests in this handoff.
- Do not rework the existing `meeting-controls-tour` step `explain-more`, though the implementation agent may use it as a style and boundary reference.
- Do not describe the detailed consent model for recording here beyond identifying it as a downstream action that requires explicit confirmation.
- Do not imply AiPresenter will start recording, start notes/transcript, change background, alter settings, leave the meeting, or inspect private meeting content from this step.
- Do not broaden this slice into manual acceptance of `More` occurrence order or locator variants.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-more` -> `narration.localizedText.ja`.
- Japanese localization advances from `44/51` to `45/51` overall and `meeting-control-map-demo` advances from `15/22` to `16/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-recording`.
- The More step remains `entrypointId: ringcentral.video.toolbar.more`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- The Japanese text mentions `More` and explains it as an overflow, expansion, or secondary-action hub.
- The Japanese text names or clearly references secondary actions such as `Start recording`, `Background`, and `Settings`.
- The Japanese text preserves the current layout boundary that `Notes` is already on the toolbar in this build.
- The Japanese text clearly says or implies that this step explains only the entry point and does not trigger downstream actions.
- The text does not say or imply that AiPresenter starts recording, starts notes/transcript, changes background, changes settings, leaves the meeting, or treats opening `More` as approval for any secondary action.

Useful negative assertions for implementation tests:

```python
assert "ja" in more_step.narration.localized_text
assert "ja" not in recording_step.narration.localized_text
assert "More" in ja_text
assert "Start recording" in ja_text or "録画" in ja_text
assert "Background" in ja_text
assert "Settings" in ja_text
assert "Notes" in ja_text
assert "入口" in ja_text or "拡張メニュー" in ja_text
assert "実行しません" in ja_text or "変更しません" in ja_text or "開始しません" in ja_text
assert "自動" not in ja_text or "自動で" in ja_text
assert "開始します" not in ja_text
assert "変更します" not in ja_text
assert "退出します" not in ja_text
```

## Next handoff notes

Implementation should be a narrow localization update only. Start from the current baseline after cycle 093: Japanese demo coverage `44/51`, `meeting-control-map-demo: 15/22`, first missing `control-map-more`.

The closest existing reference is the already-localized `meeting-controls-tour` step `explain-more`, which explains `More` as the expansion menu for deeper meeting tools and says it does not start recording or change background/settings without a clear user request. The control-map version can be slightly shorter and should match the current `control-map-more` English/Chinese semantics: "advanced shelf", `Notes` already on the toolbar, and `More` holding riskier or less frequent tools.

Keep this step separate from the following detailed safety slices. `control-map-more` teaches "where the hub is"; `control-map-recording` teaches recording consent/state boundaries; `control-map-notes` teaches notes/transcript panel boundaries; `control-map-background` teaches appearance and privacy boundaries; `control-map-settings` teaches configuration boundaries; `control-map-leave` teaches exit confirmation. That separation is the main user-safety value of this round.

After implementation, update only the files required by the implementation task and tests. This demand-analysis handoff intentionally does not commit and does not touch package YAML, tests, or other docs.
