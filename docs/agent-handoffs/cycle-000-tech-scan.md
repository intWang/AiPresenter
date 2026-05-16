# Cycle 000 Technical Scan

Date: 2026-05-16

Scope: read-only scan of the AiPresenter codebase. Business code was not modified.

## 1. Architecture Summary

Current flow, in words:

```text
Typer CLI
  -> resolve/load profile YAML
  -> resolve/load material package YAML, when demo/controller mode is used
  -> runtime.factory
      -> WindowsDesktopDriver
      -> ProfileRunner launches/binds a desktop window
      -> ProviderRegistry supplies vision, narration, and speech providers
      -> AppAdapter extracts app-specific state from raw desktop observations
      -> runtime loop or material demo runtime executes the selected workflow
```

The CLI in `src/ai_presenter/cli.py` is the entry point. It exposes `run`, `demo`, `controller`, `flows`, `entrypoints`, and `doctor`. It resolves profile/package names against the current working directory, repo-level `profiles/` and `packages/`, and packaged default profiles.

Profiles are loaded by `src/ai_presenter/config/loader.py` into Pydantic models in `src/ai_presenter/config/models.py`. The schema already has `DesktopAppProfile` and `BrowserAppProfile`, but the executable MVP path only accepts desktop profiles. Profiles define launch/bind behavior, observation sources, event types, narration policy, audio output, and provider names.

Material packages are loaded by `src/ai_presenter/packages/loader.py` into models in `src/ai_presenter/packages/models.py`. Packages provide operation entrypoints, demo flows, explainers, Q&A, manual controls, and localized narration text. Package validation catches duplicate entrypoints and broken demo/Q&A/explainer references.

`src/ai_presenter/runtime/factory.py` is the main composition root. It creates the Windows desktop driver, profile runner, provider registry, RingCentral adapter, presenter loop, media output, package action executor, synchronized timeline runner, and material demo runtime. This keeps object construction centralized, but the provider registry has growing conditional logic for speech-provider and language fallback combinations.

The desktop layer is split between protocol-like models in `src/ai_presenter/desktop/base.py` and the Windows implementation in `src/ai_presenter/desktop/windows.py`. The driver focuses windows, enumerates visible windows/controls, captures metadata/screenshot/UIA text, clicks controls, clicks relative points, and presses keys. App-specific state is extracted by `src/ai_presenter/adapters/ringcentral.py`, which turns raw UI text/metadata into `MeetingState`.

The live presenter path is:

```text
WindowsDesktopDriver.capture()
  -> RingCentralAdapter.extract_state()
  -> optional VisionProvider.recognize()
  -> EventDetector.detect()
  -> NarrationEngine.prepare_narration()
  -> NarrationProvider.narrate()
  -> SpeechProvider.synthesize()
  -> MediaOutput.play()
```

The package-demo path is:

```text
MaterialDemoRuntime
  -> SynchronizedTimelineRunner
      -> SpeechProvider.synthesize()
      -> MediaOutput.play()
      -> PackageActionExecutor.execute()
          -> WindowsDesktopDriver clicks/keys
```

The controller path layers a small Tk UI on top of the same runtime. `PresenterController` owns a background demo thread, `DemoControl` owns pause/stop/interrupt signals, `ControllerSession` tracks the active package/voice/target, and `ControllerAppCatalog` lists material packages and running windows. Running-app scan builds an in-memory temporary package from visible controls.

## 2. UI And Controller Shape

Current shape:

- `run_controller()` in `src/ai_presenter/runtime/controller.py` builds the whole Tk window inline.
- UI state is stored in `StringVar`s plus closure-local variables such as `scanned_package`, `scanned_handle`, and chat history.
- Tested pure/controller pieces include `PresenterController`, status resolution, chat transcript formatting, running-app scan state, and session behavior.
- The actual Tk layout, button enablement, scan latency, and menu update behavior are mostly covered indirectly rather than by UI-level tests.

Improvement opportunities:

- Split controller into a small view-model/service layer and a Tk adapter. The existing pure helpers show this would fit the current testing style.
- Move hardcoded language/tone labels out of `run_controller()` into shared voice metadata. This would reduce duplicated mapping work when adding languages or tones.
- Make Refresh/Scan visibly non-blocking. `list_visible_windows()` and `list_visible_controls()` can walk UI Automation trees and currently run in UI callbacks.
- Use `ControllerAppCatalog.list_material_packages()` in the UI. The method exists, but the UI currently stays centered on the initially supplied package unless the user chooses a running app.
- Add button state rules: disable Start while running, disable Pause/End when idle, disable Scan until a real running app is selected, and show scan freshness more explicitly.
- Consider `ttk` widgets for native sizing and less fragile layout before any larger visual redesign.

## 3. Performance Hotspot Hypotheses

Startup:

- `run_material_demo()` creates a fresh `WindowsDesktopDriver`, provider registry, media output, profile runner, adapter, action executor, and timeline runner each run.
- `ProfileRunner.launch_and_bind()` may focus via pywinauto path first, then scan processes through psutil, then poll for a target window every 0.1 seconds until timeout.
- Provider construction is lightweight for fake paths, but OpenAI/Codex/Piper/SAPI paths add environment checks, external process setup, COM setup, or network/runtime cost at synth/narrate time.

Scanning:

- `WindowsDesktopDriver.list_visible_windows()` enumerates desktop windows and resolves process names per window.
- `list_visible_controls()` binds to the selected window and walks the UI Automation tree. It suppresses stale-control errors, which is good for resilience, but it can still be slow for dense desktop apps.
- Controller scan state caches only whether the selected window has already been scanned. It does not cache package options, control lists, or scan durations.

Package query:

- `runtime.questions.answer_question()` tokenizes the question and re-tokenizes package Q&A and entrypoint fields on every query.
- `MaterialPackage.entrypoint_by_id()` is linear. This is fine for the current RingCentral package but easy to improve if packages grow or running-app scan produces many controls.

Narration:

- `NarrationEngine` dedupes by event fingerprint and cooldown, which is good. Fingerprinting recursively normalizes payloads every attempt.
- Codex CLI narration starts an external `codex exec` process per narration and uses a temp file with a 120-second timeout.
- OpenAI narration is synchronous network I/O through Responses API.
- The live presenter path blocks from narration generation through TTS and audio output before updating previous state.

TTS/audio output:

- Piper and Windows SAPI synthesize into temp WAV files per utterance.
- OpenAI TTS is synchronous network I/O per utterance.
- `SoundDeviceSink.play()` decodes WAV bytes on every sink playback. In `AudioOutputMode.BOTH`, both sinks can decode the same audio independently.
- Playback is blocking except for the timeline runner's internal background playback wrapper, used to coordinate `during` narration.

Logging:

- Logs are useful but do not include durations for launch, scan, capture, provider calls, TTS, decode, playback, or action execution.
- `runtime.logging.redact_value()` exists but is not wired into a formatter/filter.
- `configure_logging()` uses `basicConfig`; repeated CLI invocations in the same process may not fully reset handlers, though logger level is updated.

## 4. Language And Tone Extension Landing Points

Primary code landing points:

- `src/ai_presenter/runtime/voice.py`
  - `PresenterLanguage = Literal["en", "zh"]`
  - `PresenterTone = Literal["professional", "conversational", "concise"]`
  - `_TONE_DESCRIPTIONS`
  - `_CHINESE_REPLACEMENTS`
  - `render_voice_instruction()`
  - `render_presenter_text()`
  - `render_narration_text()`
  - `validate_profile_voice()`
  - `resolve_speech_provider_name()`
  - `sapi_rate_for_voice()`
- `src/ai_presenter/runtime/controller.py`
  - Tk language menu hardcodes `English`/`Chinese`.
  - Tk tone menu hardcodes `Professional`/`Conversational`/`Concise`.
  - `tone_values` maps display labels to `PresenterTone`.
- `src/ai_presenter/runtime/factory.py`
  - Provider registry wires language fallback names such as `windows-sapi-en` and `windows-sapi-zh`.
  - SAPI voice names and tone-specific rates are selected here.
- `src/ai_presenter/packages/models.py`
  - `DemoStepNarration.localized_text: dict[str, str]` can already hold more language keys.
- `packages/*.yaml`
  - Demo-step `localizedText` entries are the content-level expansion point.
- `src/ai_presenter/runtime/questions.py`
  - Matching stopwords/tokenization are English-centric.
  - Chinese output currently depends on `render_presenter_text()` replacements rather than native package Q&A localization.
- `src/ai_presenter/providers/codex_cli.py` and `src/ai_presenter/providers/openai_provider.py`
  - Narration prompts are currently English-only for live event narration.
  - `NarrationProvider.narrate()` does not accept voice settings, so live event language/tone support would require interface or provider-context changes.

Tests already protecting part of this:

- `tests/unit/test_voice.py`
- `tests/unit/test_runtime_factory.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_controller_session.py`

## 5. Low-Risk First-Round Recommendations

### Recommendation 1: Extract Controller Voice/Status View Helpers

Why first: It improves UI maintainability and prepares language/tone expansion without touching desktop automation or provider behavior.

Files:

- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_voice.py`

Implementation shape:

- Add shared display metadata for languages and tones, for example label/value pairs.
- Replace the local `tone_values` and language ternary in `run_controller()` with pure conversion helpers.
- Keep Tk wiring behavior unchanged.
- Optionally add pure helpers for button enabled/disabled state based on `ControllerStatusSnapshot`.

Test strategy:

- Unit-test display-label to `PresenterVoiceSettings` conversion.
- Extend `test_controller.py` around status/button-state helpers without constructing Tk.
- Run focused tests: `tests/unit/test_controller.py`, `tests/unit/test_voice.py`, `tests/unit/test_runtime_factory.py`.

Potential risk:

- Small risk of label/value mismatch causing the controller to pass the wrong voice. Keep existing labels stable and add tests for every label.

### Recommendation 2: Add A Reusable Package Question Index

Why first: It targets package-query cost and keeps future running-app scans responsive when temporary packages contain many controls.

Files:

- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_controller_session.py`

Implementation shape:

- Introduce a small immutable index object that precomputes tokens for Q&A and operation entrypoints.
- Let `answer_question()` keep its current public API by constructing the index internally.
- Let `ControllerSession` optionally keep an index for the active package after `select_target()` or `scan_running_app()`.
- Preserve current scoring and risk rules in the first pass.

Test strategy:

- Existing question tests should remain behavior-identical.
- Add a test that repeated session questions use the same indexed package path, using a tiny fake package or a spy if needed.
- Add one regression test for temporary-package control matches.

Potential risk:

- Matching behavior can drift if token precomputation subtly changes casefolding or stopword filtering. Keep the scoring functions shared rather than duplicating them.

### Recommendation 3: Add Timing Logs Before Deeper Performance Work

Why first: It is the safest way to validate startup, scan, narration, TTS, audio, and action hotspots before optimizing paths that touch real desktop apps.

Files:

- `src/ai_presenter/runtime/logging.py`
- `src/ai_presenter/runtime/profile_runner.py`
- `src/ai_presenter/runtime/factory.py`
- `src/ai_presenter/runtime/presenter.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/sync.py`
- `src/ai_presenter/media/output.py`
- `tests/unit/test_runtime_logging.py`
- targeted `caplog` tests near changed call sites

Implementation shape:

- Add a tiny `timed_operation` context manager/helper that logs `operation_started` and `operation_completed duration_ms=...`.
- Instrument launch/bind, running-window refresh, scan-visible-controls, package demo setup, state capture, narration provider call, speech synth, audio decode/play, and package action execution.
- Keep log names and levels stable; prefer `DEBUG` for noisy per-step timings and `INFO` for top-level launch/scan/demo timings.

Test strategy:

- Unit-test the timing helper with an injected clock.
- Add focused `caplog` tests for one startup path and one audio path.
- Avoid live desktop tests in this round.

Potential risk:

- Log volume can become noisy. Start with a small set of high-value spans and use debug level for inner loops.

## Notes For Next Agents

- The codebase has a useful pattern of pure helpers plus dependency injection in tests. Follow that pattern before touching Tk or Windows automation directly.
- Browser profile models exist, but runtime/controller paths are desktop-only.
- Provider configuration is string-based and permissive. This helps iteration but means provider support checks are split between diagnostics, factory, and runtime lookup.
- Chinese text appears in source/package tests, but PowerShell output may render mojibake depending on console encoding. Treat file encoding as UTF-8 and avoid judging content from terminal rendering alone.
- No tests were run during this scan because this subagent was restricted to writing only this handoff document.
