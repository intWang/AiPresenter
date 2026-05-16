# Controller Voice Readiness Design

Date: 2026-05-16

## Problem

Cycle 015 made local voice assets visible through `voices` and `doctor`, but the live controller
still shows only the selected language/tone label. An operator can select a locally routed voice,
press Start, and discover missing SAPI or Piper assets too late.

The controller should answer the operator's real question before Start: can this selected voice
actually speak locally on this machine?

## Design

Keep the feature centered on the existing pure controller view model.

Add a small voice-readiness value to `ControllerOperatorSnapshot`:

- `None` means no local assets are required or the route is not applicable.
- `OK` means required local assets are available.
- `FAIL` means required local assets are missing or unavailable.

The view model should expose a concise `voice_readiness_label` and include readiness in button
state calculation:

- Start requires target readiness, idle state, and voice readiness.
- Submit also requires voice readiness, because a safe matched question can start or queue a spoken
  demo.
- Non-local routes where readiness is `None` should behave like today's controller.

The Tk controller should use `check_voice_asset_availability(profile, current_voice())` at a narrow
adapter boundary. It should convert checker exceptions into a failed readiness value so UI refresh
does not crash the event loop. The operator summary should show the selected voice plus readiness,
for example:

`Voice: Chinese / Friendly | Voice assets: OK`

or:

`Voice: Chinese / Friendly | Voice assets: FAIL - speech=windows-sapi-zh requires installed SAPI voice matching Huihui`

`start()` and `submit_question()` should re-check readiness before triggering work so direct button
callbacks remain guarded even if UI state is stale.

## Error Handling

Voice compatibility remains separate from voice asset readiness:

- `validate_profile_voice()` continues to report unsupported profile/language combinations.
- Asset readiness is only meaningful after compatibility passes.
- Checker exceptions become `FAIL` readiness messages.

Running-app scan requirements remain independent. If the selected running app has not been scanned,
scan-required messaging stays visible; if the scan is ready but voice assets are missing, Start stays
disabled and the summary names the missing asset.

## Testing

Do not depend on real SAPI, COM, Piper modules, or local model files.

Test the pure view model with constructed readiness values:

- OK local readiness keeps Start enabled when target is ready.
- FAIL local readiness disables Start and Submit and exposes the detail.
- `None` readiness preserves current non-local behavior.
- Running-app scan requirements and voice readiness compose predictably.

Test controller helper functions with fake checkers:

- OK checker returns an OK readiness label.
- FAIL checker blocks Start before runner invocation.
- Checker exceptions become failed readiness messages.

## Out Of Scope

- Installing or downloading voice assets.
- Changing provider routing or profile schema.
- Validating speaker devices or audible output.
- Large Tk layout redesign.
- Adding a programmatic asset guard inside `PresenterController.start()` for non-Tk callers.
