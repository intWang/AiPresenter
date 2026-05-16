# Cycle 023 Technical Scan: RingCentral Video Demo-Flow Chinese Narration

Date: 2026-05-16

## Scope

Review-only scan for package demo model/runtime/tests and `packages/ringcentral-video.yaml`.
No production or package implementation files were changed.

## Findings

- Localized demo-step text is already modeled. `DemoStepNarration.localized_text` maps YAML
  `localizedText` to `dict[str, str]` in `src/ai_presenter/packages/models.py`.
- Localized demo-step text is already rendered at runtime. `src/ai_presenter/runtime/factory.py`
  applies `render_narration_text(step.narration, voice)` before a step reaches the synchronized
  timeline, and `src/ai_presenter/runtime/sync.py` speaks `step.narration.text`.
- Language fallback is already defined in `src/ai_presenter/runtime/voice.py`: if
  `narration.localized_text[settings.language]` exists and is nonblank, it is used; otherwise the
  English `narration.text` goes through `render_presenter_text()`.
- Tone interaction is intentionally narrow for localized narration. Localized text is returned as
  authored content except `tone="concise"`, which truncates to the first sentence. Friendly/coach/formal
  prefixes are not added to localized package narration.
- Current RingCentral package coverage:
  - `meeting-control-map-demo`: 22/22 steps have `localizedText.zh`.
  - `vbg-blur-demo`: 0/4 steps have `localizedText.zh`.
  - `meeting-basics-demo`: 0/3 steps have `localizedText.zh`.
  - `meeting-controls-tour`: 0/22 steps have `localizedText.zh`.
  - Q&A localization is already complete: 8/8 Q&A items have Chinese questions and answers.
  - Package-owned Chinese aliases exist on 15/27 entrypoints.
- Existing tests already prove the core behavior:
  - `tests/unit/test_voice.py` asserts localized Chinese narration wins and concise uses the first sentence.
  - `tests/unit/test_runtime_factory.py` asserts material demo runtime applies localized Chinese narration before
    running a step.
  - `tests/unit/test_material_packages.py` asserts every `meeting-control-map-demo` step has Chinese localized text.

## Pitfalls

- `package_demo.py` only executes actions; it does not select narration language. Avoid adding localization logic there.
- `CamelModel.extra="forbid"` means any new YAML shape beyond existing `localizedText` will require schema changes.
  Cycle 023 should use only existing `narration.localizedText.zh`.
- Flow IDs matter. CLI/tests already reference `meeting-control-map-demo`, `meeting-controls-tour`, and
  `vbg-blur-demo`; do not rename flows or step IDs for a content-only slice.
- Adaptive invite narration can be stale in Chinese. `adjust_ringcentral_demo_step()` changes `narration.text`
  for active multi-person meetings but preserves the original `localized_text`; later `render_narration_text()`
  will prefer the stale localized text for `zh`. This matters for steps like Add coworkers if localized package
  text describes the empty-room state.
- The package still stores English UI labels such as `Chat`, `Settings`, `Background`, and `Leave` inside Chinese
  narration. That matches current tests, but reviewers should decide whether this is intentional product-label style.
- Some console output in PowerShell can display UTF-8 as mojibake; use UTF-8-aware reads or semantic assertions rather
  than copying garbled terminal text.

## Safe Files To Modify

- `packages/ringcentral-video.yaml`
  - Add `narration.localizedText.zh` to existing demo steps only.
  - Keep existing `text`, `placement`, and `actionOffsetMs` unchanged unless there is a separate behavior reason.
- `tests/unit/test_material_packages.py`
  - Add or expand content-shape assertions for the newly localized flows.
  - Assert presence of `localized_text["zh"]`, CJK characters, and English `text` remaining ASCII.
- `tests/unit/test_runtime_factory.py`
  - Only needed if asserting an end-to-end package flow with `PresenterVoiceSettings(language="zh")`.
- `tests/unit/test_adaptive_demo.py` or `src/ai_presenter/runtime/adaptive_demo.py`
  - Only needed if Cycle 023 chooses to fix the active-meeting stale-localized-text pitfall.

## Recommended TDD Slice

1. RED: Add a focused test in `tests/unit/test_material_packages.py` for one target flow, preferably
   `meeting-controls-tour`, asserting every step has nonblank `narration.localized_text["zh"]` containing at least
   one CJK character while `narration.text` stays ASCII.
2. GREEN: Add `localizedText.zh` to each `meeting-controls-tour` step in `packages/ringcentral-video.yaml`.
3. RED: Add the same coverage for `vbg-blur-demo` and `meeting-basics-demo`.
4. GREEN: Add their `localizedText.zh` entries.
5. Optional RED for the adaptive pitfall: create a test where an Add coworkers step has stale `localizedText.zh`,
   active participant count rewrites it to Invite, and Chinese runtime text must not use the stale empty-room Chinese.
6. Optional GREEN: clear or replace `localized_text` when adaptive narration rewrites `text`, or provide a Chinese
   localized override for the adaptive narration. Keep this separate from the content-only package slice.

## Verification Run

Executed:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q `
  tests\unit\test_voice.py::test_render_narration_text_prefers_localized_chinese_script `
  tests\unit\test_voice.py::test_render_narration_text_concise_chinese_uses_first_sentence `
  tests\unit\test_runtime_factory.py::test_existing_window_material_demo_applies_localized_chinese_narration `
  tests\unit\test_material_packages.py::test_meeting_control_map_demo_is_directed_and_complete
```

Result: `4 passed`.
