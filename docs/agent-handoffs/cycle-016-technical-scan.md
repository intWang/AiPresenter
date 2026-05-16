# Cycle 016 Technical Scan: Controller Voice Asset Readiness

Date: 2026-05-16

## Current Architecture

- `PresenterController` in `src/ai_presenter/runtime/controller.py` owns runtime demo state,
  target switching, question interrupts, and voice forwarding into runner functions. It already
  validates voice compatibility with `validate_profile_voice()` before starting a demo, but it does
  not check local SAPI/Piper asset availability.
- `run_controller()` is the Tk wiring layer. It owns `StringVar` state, target/source selection,
  running-app scanning, session updates, and calls `build_controller_operator_view_model()` from
  `refresh_operator_view()` to derive labels and button states.
- `controller_view_model.py` is pure and test-friendly. `ControllerOperatorSnapshot` describes UI
  facts; `build_controller_operator_view_model()` computes summary labels and button enablement.
  Today readiness only means package/flow or scanned running-app target readiness.
- `voice_assets.py` exposes `check_voice_asset_availability(profile, voice, ...)`, returning
  `VoiceAssetAvailability(status="OK" | "FAIL", route, detail)` for local routes and `None` for
  routes without local assets such as `fake`/`openai`.
- `diagnostics.py` already gates voice asset checks behind successful voice compatibility, which is
  the model the controller should mirror.

## Likely Change Points

- `ControllerOperatorSnapshot`: add voice asset readiness fields, likely one optional
  `voice_asset_status: VoiceAssetAvailability | None` or a smaller pure DTO if avoiding an import
  from `voice_assets`.
- `ControllerOperatorViewModel`: add a label such as `voice_asset_label` or fold the status into
  `voice_label`; prefer a separate label internally so summary text can remain explicit.
- `build_controller_operator_view_model()`: include asset readiness in labels and `start_enabled`.
  `submit_enabled` should probably also require voice assets when submission may start/queue a
  spoken demo, but confirm desired text-only behavior before implementation.
- `_target_ready()` or a new `_voice_ready()` helper in `controller_view_model.py`: keep target
  readiness and voice asset readiness separate so scan-required messaging does not mask voice
  failures.
- `run_controller()` in `controller.py`: add a small local adapter used by `refresh_operator_view()`,
  `start()`, and `submit_question()` to evaluate the current voice without exposing Tk tests to real
  COM/Piper assets.
- `operator_summary.set(...)`: append or integrate the voice asset label, for example
  `Voice: English / Professional (assets ready)` or `Voice assets: missing ...`.

## Injection/Test Strategy

- Do not call real SAPI/Piper/COM in unit tests. Add an injectable checker function at the Tk
  boundary, e.g. `run_controller(..., voice_asset_checker=check_voice_asset_availability)` or a
  module-level wrapper that tests monkeypatch. The checker shape should accept `(profile, voice)`
  and return `VoiceAssetAvailability | None`.
- Keep `controller_view_model.py` tests fully pure by constructing fake readiness values directly:
  `None` for cloud/fake routes, `OK` for ready local assets, `FAIL` for missing local assets.
- If importing `VoiceAssetAvailability` into the view model feels too coupled, define a tiny frozen
  view-model DTO with `status` and `detail`; convert from `voice_assets` only in `controller.py`.
- Existing `test_voice_assets.py` already covers injected SAPI/Piper dependencies. New controller
  tests should not repeat asset discovery; they should assert wiring/labels/button states with a
  fake checker.
- Preserve current `PresenterController` runner tests. Asset preflight belongs in the operator/Tk
  start path, not in `PresenterController._start_target()`, unless the product decision is to block
  all programmatic starts too.

## Edge Cases

- Running app source before scan: Start should remain disabled/blocked because scan is missing; the
  summary should still show voice asset readiness so the operator can fix voice setup before scan.
- Running app scan success with missing voice assets: target labels should show scanned/ready, but
  Start should stay disabled and status/summary should explain the selected voice asset problem.
- Running app refresh or selection change after scan: stale scan clearing should continue to drive
  target readiness independently of any cached voice asset result.
- Language/tone changes: asset status must recompute immediately when either `StringVar` changes.
  Current option menus do not pass `command=` callbacks, so add traces or commands for `language`
  and `tone` that call `refresh_operator_view()`.
- Voice compatibility failure versus asset failure: `validate_profile_voice()` remains the
  compatibility gate; only call/check local assets for a compatible voice, mirroring diagnostics.
- Start button enablement: require `target_ready`, `can_start_new_action`, and `voice_ready`.
  On direct `start()` invocation, re-check assets and set a clear `Start error:` or status message
  rather than relying only on disabled buttons.
- Submit question: for unscanned running apps, keep scan-required behavior. For missing local voice
  assets, decide whether to block all submissions or allow text-only answers; if blocking, use the
  same `voice_ready` gate as Start and show the voice asset detail.
- Checker exceptions: treat as voice asset failure in the Tk adapter so UI refresh cannot crash the
  event loop.
- Non-local routes: `None` from `check_voice_asset_availability()` should mean "no local voice asset
  required" and should not disable Start.

## Proposed Implementation File List

- `src/ai_presenter/runtime/controller_view_model.py`
- `src/ai_presenter/runtime/controller.py`
- `tests/unit/test_controller_view_model.py`
- `tests/unit/test_controller.py`

No production runner, provider, or diagnostics changes appear necessary for this follow-up.
