# Cycle 091 Demand Analysis: RingCentral Video Control Map Share JA

## User need

Japanese users need the control map to explain where content sharing begins without making the presenter start sharing content for them.

The Share entry is valuable because it is the meeting toolbar route to presenting a screen, an application window, or selected content during a RingCentral Video meeting. Users need to know this location before they present slides, demo software, review a document, or hand visual context to other participants. It is also the point where accidental disclosure risk becomes high: the picker may reveal screen names, open windows, document titles, browser tabs, application names, previews, and a system-audio option.

This step should answer: "Where do I go to choose what to share?" It should not answer: "Please start sharing this content now," "Can everyone see my screen now," or "Read the window contents for me." The narration should frame Share as an entry and picker, not as consent to press the final Share button.

Important boundaries:

- The toolbar `Share` button opens the picker. The final `Share` button inside that picker starts the actual meeting-visible share and must remain confirmation-gated.
- Screen/window/source selection is separate from starting the share. The presenter can explain categories or visible choice types, but should not pick a source by default.
- `Share system audio` is an optional sharing scope, not a harmless description detail. It can expose alerts, media playback, notification sounds, or app audio, so it should be mentioned as an option that requires explicit user intent before enabling or starting.
- Window titles, thumbnails, browser tabs, documents, desktop content, and private app names are sensitive by default. The narration should avoid reading or interpreting them unless the user explicitly asks and the content is verified from an approved observation source.
- This step is about the sharing entry. It should not cover reading shared content after sharing starts; the package already treats shared content as private unless verified and allowed.

## Presenter behavior

The existing step is `meeting-control-map-demo` -> `control-map-share`, using `entrypointId: ringcentral.video.toolbar.share`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`. The underlying entrypoint opens the `Share` button and has `cleanup: escape`, so the presenter may open the picker for orientation and then close it before continuing to Reactions.

Expected behavior for this narration:

- Explain that `Share` opens the picker for screen or application/window sharing.
- Mention that the presenter can explain the choices at a category level.
- State that the final `Share` button is not pressed unless the user confirms what should be shown.
- Treat `Share system audio` as an option that can broaden what others hear, not as something automatically enabled.
- Keep the action limited to opening the picker during the tour and closing it after explanation.
- Avoid reading source names, window titles, document titles, browser tabs, thumbnails, or visible screen contents by default.
- Avoid selecting a source, toggling system audio, starting a share, claiming the share is active, or narrating shared content unless a later explicit user request and visible verification justify it.

## Localization tone

Use natural Japanese guidance that is calm, concise, and protective. This is a high-privacy collaboration control, so the narration should sound like a careful live presenter, not like a legal disclaimer.

Recommended tone:

- Keep visible UI labels in English where useful: `Share`, final `Share` button, and `Share system audio`.
- Prefer route-level Japanese terms such as "画面またはアプリケーションウィンドウの選択画面", "共有する対象", "選択肢の種類", and "システム音声".
- Use explicit confirmation language, such as "ユーザーが表示する内容を確認するまで" or "ユーザーが明確に求めるまで".
- Keep privacy wording concrete: "共有候補や画面内容は読み上げない" is better than broad claims about safety or privacy.
- Do not imply the presenter can decide whether a source is safe to show. The user chooses the source and confirms the final action.
- One compact paragraph should be enough. The control map should remain a fast orientation tour.

Good semantic target for the Japanese text:

`Share` opens the picker for sharing a screen or application window. It can include system audio, but the presenter only explains the choices and does not select a source, enable audio, read source contents, or press the final `Share` button until the user confirms what should be shown. After the explanation, the picker is closed.

## Out of scope

- Do not modify YAML, tests, runtime code, source index, profiles, Q&A, aliases, diagnostics, CLI output, or any other documentation in this demand-analysis turn.
- Do not localize later `meeting-control-map-demo` steps such as Reactions, Raise hand, More, Recording, Notes, Background, Settings, Leave, or Summary.
- Do not change the existing Share action semantics, locator, timing, placement, cleanup, flow order, or entrypoint presenter notes.
- Do not add Japanese question aliases for Share in this slice unless a separate implementation task explicitly assigns alias work.
- Do not change existing `meeting-controls-tour` -> `explain-share` Japanese narration unless a separate task assigns harmonization work.
- Do not introduce behavior that selects a screen/window, toggles `Share system audio`, starts screen sharing, reads picker entries, inspects thumbnails, interprets document/window contents, captures shared content, or claims participants can see the screen.
- Do not capture or preserve evidence containing participant names, meeting identifiers, window titles, document names, browser tabs, desktop thumbnails, app previews, notifications, or screen contents unless a later validation task explicitly requires sanitized evidence.

## Acceptance criteria

- This handoff exists as `docs/agent-handoffs/cycle-091-demand-analysis.md`.
- No YAML, code, tests, source-index files, profiles, or other docs are modified by this demand-analysis subagent.
- The future implementation target is only `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-share` -> `narration.localizedText.ja`.
- Current baseline is treated as `41/51` Japanese demo steps, `meeting-control-map-demo: 12/22`, first missing `control-map-share`.
- The future localized narration should advance Japanese demo coverage to `42/51` and `meeting-control-map-demo` to `13/22`.
- After implementation, the first remaining missing `meeting-control-map-demo` Japanese step should become `control-map-reactions`.
- Existing Share behavior remains:
  - `entrypointId: ringcentral.video.toolbar.share`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 400`
  - underlying entrypoint target `Share`, control type `button`, cleanup `escape`
- The Japanese narration explains Share as the picker for screen/application/window sharing.
- The Japanese narration distinguishes opening the picker from pressing the final `Share` button.
- The Japanese narration mentions system audio as an optional share scope that requires explicit user intent before use.
- The Japanese narration includes privacy boundaries for source names, window titles, thumbnails, screen contents, and shared content.
- The Japanese narration says the picker is closed after explanation.
- Japanese `--require-complete` should still fail after this future slice because later control-map steps remain untranslated.
- Q&A localization and `questionAliases.ja` coverage should remain unchanged unless separately assigned.

## Next handoff notes

Implementation should be a narrow narration-only package-content slice. Reuse the safety posture already established in `meeting-controls-tour` -> `explain-share`, but tighten it for the control-map context by making the picker/final-share boundary explicit and adding a clearer system-audio boundary.

Suggested implementation wording should preserve the visible UI label `Share` and may reuse the existing Japanese phrase for "screen or application window picker." The main additions for this slice are: do not select a source, do not enable system audio, do not read source or screen contents, do not press the final `Share` button until the user confirms what should be shown, and close the picker after explanation.

Recommended next artifacts after implementation:

- A technical scan confirming the exact YAML location, count changes, first missing step, and focused tests to update.
- A risk scan focused on source picker privacy, final Share confirmation, system-audio scope, and cleanup.
- A focused implementation handoff documenting changed files and verification commands.
