# Voice Discovery Design

Date: 2026-05-16

## Context

Cycles 011 and 012 made voice selection usable and safer. Operators can pass `--language` and `--tone`, and unsupported profile/voice combinations fail before automation. The remaining gap is discoverability: users still have to guess accepted aliases or try a command to learn whether a profile supports a voice.

## Design

Add two complementary surfaces:

- `ai-presenter voices` is the discovery command.
  - With no profile, it lists canonical language and tone choices, accepted aliases, defaults, and a short compatibility note.
  - With `--profile`, it reports configured speech provider and language support rows using existing validation/routing logic.
  - With `--language` and/or `--tone`, it reports the normalized selected voice and compatibility for that profile if provided.
- `ai-presenter doctor --language --tone` is the validation command.
  - Voice diagnostics are included only when the user supplies either option, keeping existing doctor output stable by default.
  - The diagnostic uses `validate_profile_voice()` and `resolve_speech_provider_name()`.

Expose small public metadata helpers from `runtime.voice` so CLI formatting does not read private alias dictionaries.

## Behavior

- `voices` exits 0 for catalog and profile support listings.
- `voices --profile ringcentral-video --language zh-CN --tone friendly` prints an unsupported row and exits nonzero because it is a targeted validation.
- `voices --profile ringcentral-video-bind-speaker` shows English and Chinese as supported, with Chinese resolving to `windows-sapi-zh`.
- `doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly` includes `[OK] voice`.
- `doctor --profile ringcentral-video --language zh-CN` includes `[FAIL] voice` and exits 1.

## Non-Goals

- No installed SAPI voice detection.
- No Piper model download detection.
- No OpenAI credentials change beyond the existing provider environment check.
- No new languages beyond current English and Chinese output families.

## Acceptance Criteria

- `voices` lists language labels, tone labels, aliases, and tone descriptions.
- `voices --profile` uses `validate_profile_voice()` and `resolve_speech_provider_name()` rather than duplicating compatibility rules.
- Targeted incompatible `voices --profile --language ...` exits 1 with profile/provider/voice detail.
- `doctor` output is unchanged unless voice options are supplied.
- `doctor --language/--tone` adds `[OK] voice` or `[FAIL] voice`.
- Focused CLI/diagnostics/voice tests, ruff, mypy, and full tests pass.

## Risks

- Voice compatibility is routing compatibility, not proof that local audio output works.
- Doctor counts change only for opt-in voice checks; tests should assert both default and opt-in behavior.
- Tone support is presentation behavior; provider compatibility is mainly language/provider routing.
