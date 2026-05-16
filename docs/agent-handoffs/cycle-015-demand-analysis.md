# Cycle 015 Demand Analysis: Local Voice Asset Availability

Date: 2026-05-16

## User Problem

Recent voice work made language and tone choices discoverable, and `voices` / `doctor --language --tone` can now report whether a profile is configured to support a requested voice route. That is not the same as proving the local machine can actually speak through that route.

This matters for AiPresenter demos because live acceptance is machine-specific:

- Windows SAPI routes assume installed voices whose display names include `Zira` for English and `Huihui` for Chinese.
- Piper routes assume the `piper` Python module is importable and the selected model, currently `en_US-lessac-medium`, is available under the expected cache/data directory.
- Current output can say `supported via speech=windows-sapi-zh` even when the Windows voice is not installed, or can list the Piper profile as compatible even when the model download has not happened.

For demo operators, that gap appears late: the profile loads, the CLI preflight passes, and only speech synthesis fails or produces no audible narration during a run. Cycle 015 should move those failures into an explicit pre-demo check.

## Proposed Cycle 015 Scope

In scope:

- Add a local speech availability diagnostic layer that distinguishes configured voice compatibility from runtime asset availability.
- For Windows SAPI, detect whether required local SAPI voices are installed for the resolved route:
  - English route: voice name contains `Zira`.
  - Chinese route: voice name contains `Huihui`.
  - Generic `windows-sapi`: report the default SAPI engine as available when COM can enumerate voices, and route-specific checks when language/tone is supplied.
- For Piper, check that the Piper module can be invoked/imported and that the configured model asset for `en_US-lessac-medium` is locally available in the default or configured Piper data directory.
- Surface availability in `ai-presenter voices --profile ...` and `ai-presenter doctor --profile ... --language ... --tone ...`.
- Keep checks side-effect light: no model downloads, no audible synthesis, no RingCentral automation, and no cloud calls.
- Provide actionable failure details, including the missing voice/model and the README command or path to fix it.

Out of scope:

- Adding new languages, new voice aliases, or new tone behavior.
- Downloading Piper models automatically.
- Changing the provider registry, playback behavior, or synthesis implementation beyond shared read-only availability helpers.
- Validating speaker device routing, virtual microphone wiring, OpenAI TTS voice availability, or actual audible output.
- Reworking profile schema for explicit voice names unless implementation discovers that current hard-coded defaults cannot be represented cleanly.

## Acceptance Criteria

CLI:

- `ai-presenter voices` continues to list language and tone aliases without requiring local SAPI, Piper, or OpenAI assets.
- `ai-presenter voices --profile ringcentral-video-bind-speaker` distinguishes:
  - configured support, such as English/Chinese route compatibility;
  - local availability, such as installed `Zira` / `Huihui` SAPI voices.
- `ai-presenter voices --profile ringcentral-video-piper-speaker` reports Piper availability separately from route compatibility, including a clear missing-model message when `en_US-lessac-medium` is not installed.
- Targeted checks with `--language` / `--tone` exit nonzero when the selected route is configured but missing required local assets.
- Existing unsupported-profile behavior remains intact, for example fake speech still fails for Chinese because the provider route is not configured.

Diagnostics:

- `doctor --profile ... --language ... --tone ...` keeps the current `voice` compatibility check, but adds or expands output to make local availability explicit.
- SAPI failures name the missing local voice and the resolved route, for example `speech=windows-sapi-zh requires installed SAPI voice matching Huihui`.
- Piper failures name both the missing runtime/module case and the missing model case distinctly.
- Availability checks are deterministic and testable without requiring real SAPI or Piper installs by injecting/enumerating through small helper boundaries.
- The RingCentral manual acceptance checklist can add one pre-demo command that proves the configured voice route is locally runnable before launching the controller or demo.

## Risks And Follow-Ups

- SAPI voice display names vary across Windows editions, language packs, and Office/Edge voice installations. The first implementation should match current runtime behavior (`Zira`, `Huihui`) and document the limitation rather than trying to infer every possible locale voice.
- COM/SAPI enumeration may fail on non-Windows CI or machines without `pywin32`; tests should use fakes and production checks should return a clear unavailable result instead of crashing.
- Piper CLI/package behavior may change across versions. A robust check should avoid relying on one fragile internal path, but it should still verify the actual local model files that the current provider will need.
- `PiperSpeechProvider` accepts `data_dir` and `download_dir`, but profiles do not currently expose these. A follow-up may be needed to make voice/model selection configurable instead of hard-coded.
- Actual audio output still depends on device routing. Cycle 015 should not solve that, but the next diagnostics candidate is speaker/virtual microphone availability.

## Recommendation

Prioritize Cycle 015 before deeper demo polish. The feature is small, local, and directly reduces demo risk introduced by the successful Cycle 013/014 discovery work. It also gives operators a trustworthy preflight story: `voices` answers "what can this profile claim to support," while `doctor` answers "will this machine satisfy the selected route right now."

Implementation priority: high for RingCentral manual acceptance and any Windows demo using Chinese narration; medium for the broader product because it strengthens the diagnostics model without changing runtime behavior.
