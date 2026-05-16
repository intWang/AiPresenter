# Cycle 016 Demand Analysis: Controller Voice Readiness

Date: 2026-05-16

## User And Operator Problem

Cycle 015 made local SAPI and Piper asset availability visible in `voices` and `doctor`, but the
controller is still the main live-operator surface. An operator can pick Chinese or Piper-backed
speech in the controller, see a normal voice label such as `Chinese / Friendly`, and press Start
without the summary saying whether the selected local route is actually ready on this machine.

That gap matters because local voice failures are machine-specific and confusing during demos:

- `validate_profile_voice()` proves the selected language/tone can route through the profile, not
  that the required local voice files or installed SAPI voices exist.
- SAPI Chinese depends on an installed voice matching `Huihui`; SAPI English depends on `Zira` or
  an available generic SAPI voice depending on route.
- Piper depends on the `piper` Python module and local model/config files for the selected default
  voice assets.
- The controller operator summary already shows source, target, flow, voice, scan state, and
  question outcome, so voice readiness belongs in the same pre-Start status loop.

The product demand is to make the live controller answer, before Start: "Can this selected voice
actually speak locally here?"

## Proposed Cycle 016 Scope

In scope:

- Extend the controller/view-model status model to include selected voice asset readiness for local
  SAPI and Piper routes.
- Reuse `check_voice_asset_availability()` as the readiness source instead of duplicating SAPI/Piper
  checks in controller code.
- Show a concise readiness label in the operator summary beside or within the existing voice field:
  for example `Voice: Chinese / Friendly (assets missing)` or a separate `Voice assets: OK/FAIL`.
- Disable Start when the selected voice route is local and required assets are missing.
- Keep non-local or non-asset routes such as fake/OpenAI as not-applicable so existing smoke flows
  remain startable.
- Preserve current route compatibility errors: unsupported language/provider combinations should
  still surface through `validate_profile_voice()` with the existing profile/provider/voice context.
- Add/update unit tests around `controller_view_model` and controller Start behavior using injected
  or monkeypatched readiness results, without requiring real SAPI or Piper installs.
- Update the manual acceptance checklist to include verifying the controller summary shows local
  voice readiness before Start if this cycle includes docs beyond the handoff.

Out of scope:

- Downloading Piper models, installing SAPI voices, or attempting speech synthesis as a readiness
  test.
- Changing provider routing, voice aliases, tone behavior, or profile compatibility rules.
- Adding profile schema for configurable SAPI voice names or Piper model names.
- Validating speaker output devices, virtual microphone routing, RingCentral audio receipt, or
  actual audible playback.
- Reworking the controller UI layout beyond the minimal summary/status and button-state changes.

## Acceptance Criteria

Controller/view-model behavior:

- The operator summary includes the selected voice readiness state for local routes:
  `OK`, `missing/unavailable`, or `not checked/not applicable` with wording short enough for the
  existing summary row.
- For supported local routes, missing assets make Start disabled while the controller is idle.
- When Start is blocked by missing local voice assets, the visible status or summary names the
  concrete requirement from `VoiceAssetAvailability.detail`, such as `Huihui`, `Zira`, `piper`, or
  `en_US-lessac-medium`.
- Changing language or tone refreshes the readiness state before the operator presses Start.
- Running desktop app mode keeps the existing scan requirements and combines them with voice
  readiness: Start requires both a scanned target and a ready selected voice.
- Material package mode keeps the existing package/flow readiness and combines it with voice
  readiness: Start requires package/flow plus a ready selected voice.
- Question submission should not regress. If a question can start or queue a spoken demo, it should
  use the same selected voice readiness guard; text-only answers may remain available if the
  implementation can keep that path clear and understandable.
- Routes where `check_voice_asset_availability()` returns `None` do not block Start and should not
  display a failure.
- Controller unit tests cover:
  - local route ready enables Start when target requirements are also satisfied;
  - local route missing disables Start and reports the missing asset detail;
  - non-local/not-applicable route preserves current Start behavior;
  - language/tone changes update the displayed readiness;
  - running-app scan requirements and missing-voice requirements compose predictably.

## Risks And Follow-Ups

- The Tk controller currently builds the summary from a pure view model but computes runtime details
  in the UI closure. Keep asset probing at a small boundary so tests can fake it and the UI does not
  grow harder to reason about.
- Asset checks may touch COM/SAPI or filesystem/module state. They should be side-effect light and
  cached or refreshed deliberately if repeated polling makes the controller feel sluggish.
- A disabled Start button needs an obvious reason. If only the button disables, operators may be
  more confused than before; the status/summary must carry the actionable detail.
- Existing `PresenterController.start()` validates compatibility but not assets. A follow-up may be
  to add an optional asset guard closer to the controller domain so programmatic controller use gets
  the same protection as Tk.
- Profile-level voice configuration remains a follow-up: hard-coded SAPI/Piper expectations are
  acceptable for Cycle 016 because they match Cycle 015, but they are not a long-term voice catalog.
- Device routing diagnostics remain separate and should be considered after controller voice
  readiness, especially for virtual microphone acceptance.

## Recommendation

Priority: high for Cycle 016.

This is the natural next step after Cycle 015. The CLI now gives operators a reliable preflight, but
the live controller can still present a startable-looking setup that fails late when local speech
assets are absent. Exposing selected voice readiness in the operator summary and blocking Start for
known-missing local assets should reduce demo anxiety with a small, testable change centered on the
existing controller view model and `voice_assets` helper.
