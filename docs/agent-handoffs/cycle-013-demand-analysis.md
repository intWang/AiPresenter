# Cycle 013 Demand Analysis: Voice Discovery

Date: 2026-05-16

## User-Facing Need

Operators can select and preflight voices, but they cannot discover valid languages, tones, aliases, or profile compatibility without trying a demo/controller command. Add a safe lookup surface before launch.

## Workflows

- `ai-presenter voices` lists canonical languages, tones, aliases, and defaults.
- `ai-presenter voices --profile ringcentral-video-bind-speaker` shows configured speech provider plus supported routes.
- `ai-presenter voices --profile ringcentral-video --language zh-CN --tone friendly` reports the normalized selected voice and compatibility failure without launching RingCentral.
- `ai-presenter doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly` includes an opt-in voice compatibility check.

## Acceptance Criteria

- Reuse `PresenterVoiceSettings`, `validate_profile_voice()`, and `resolve_speech_provider_name()`.
- Expose public metadata helpers for aliases and tone descriptions.
- `voices` catalog output exits 0.
- Targeted incompatible `voices --profile --language/--tone` exits 1 with profile/provider/voice detail.
- `doctor` output is unchanged unless a voice option is supplied.
- CLI tests cover catalog output, profile rows, targeted validation, and doctor opt-in validation.

## Risks

- `doctor` should not become noisy by default.
- Compatibility means routing compatibility, not installed voice/audio/OpenAI readiness.
- Tone support is mostly prompt/rendering behavior; hard compatibility is language/provider based.

## Documentation Suggestions

- Add README examples near the existing voice flag docs.
- Add a runbook preflight step for `voices --profile`.
- Clarify that regional aliases map to English/Chinese output families.
