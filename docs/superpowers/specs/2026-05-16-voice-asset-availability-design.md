# Voice Asset Availability Design

Date: 2026-05-16

## Problem

AiPresenter can now normalize presenter language and tone choices and can report whether a
profile is configured to route a selected voice. That does not prove the local machine can
actually synthesize that voice. Windows SAPI routes can be missing the expected installed voice,
and Piper routes can be missing the Python module or local model files.

This should be caught before a live RingCentral demo starts.

## Approaches Considered

Recommended: add a read-only local asset check shared by `voices` and `doctor`.

- Pros: gives operators one clear preflight story, keeps runtime behavior unchanged, and avoids
  downloads, synthesis, cloud calls, or RingCentral automation.
- Cons: SAPI display names are machine-specific, so the first version should match the current
  runtime defaults rather than trying to infer every possible voice.

Alternative: keep checks only in `doctor`.

- Pros: least disruptive.
- Cons: leaves `voices --profile` saying "supported via ..." without warning that the selected
  local asset is missing.

Alternative: block every demo/controller launch on local asset checks.

- Pros: strongest runtime safety.
- Cons: makes dry-run and fake/test profiles brittle, and can be frustrating on machines where
  users only want configuration discovery.

## Design

Add provider-level helper APIs for local asset discovery:

- Windows SAPI helpers enumerate installed SAPI voices and test whether a configured substring
  match is available. The match must use the same case-insensitive substring behavior as
  `WindowsSapiSpeechProvider`.
- Piper helpers resolve the default model and config file paths for the current provider default
  voice, then check whether both files are present locally.

Add a runtime-level availability helper that:

- Resolves the actual speech route with `resolve_speech_provider_name()`.
- For `windows-sapi-en`, requires an installed SAPI voice matching `Zira`.
- For `windows-sapi-zh`, requires an installed SAPI voice matching `Huihui`.
- For plain `windows-sapi`, requires at least one installed SAPI voice.
- For `piper`, requires the `piper` Python module and local `en_US-lessac-medium` model/config
  assets in the current default data directory.
- Returns no check for `fake` and `openai`.

`doctor --language/--tone` should remain the strict preflight. It first reports the existing
configured voice compatibility check. If compatibility passes and the route is local, it adds a
`voice assets` diagnostic that can pass or fail.

`voices --profile` should display local asset status next to supported local routes without
failing the command. When the user asks for a targeted selection with `--language` or `--tone`,
missing local assets should exit nonzero, just like an unsupported configured route.

## Error Handling

SAPI enumeration errors should not crash CLI output. They should become unavailable asset details
for explicit local voice checks.

Piper checks must not run `python -m piper`, synthesize audio, download models, or touch the
network. They should only check module discoverability and local files.

Failure messages should name the route and missing asset, for example:

- `speech=windows-sapi-zh requires installed SAPI voice matching Huihui`
- `speech=piper requires Python module piper`
- `speech=piper requires local Piper voice assets for en_US-lessac-medium`

## Testing

Tests must not require real Windows voices, COM, Piper binaries, or Piper model downloads.

Use fake SAPI dispatchers/listers, temporary Piper asset files, and monkeypatched diagnostic
helpers. Cover:

- SAPI helper substring matching.
- Piper asset path resolution and presence checks.
- `doctor` OK and FAIL output for local SAPI assets.
- `doctor` OK and FAIL output for Piper assets.
- `voices --profile` printing local asset status without failing in matrix mode.
- Targeted `voices --profile --language --tone` exiting nonzero when assets are missing.

## Out Of Scope

- Installing Windows language packs or SAPI voices.
- Downloading Piper models.
- Adding profile schema for custom voice names or Piper model paths.
- Validating speaker devices or actual audible output.
- Changing provider registry, synthesis, or playback behavior.
