# Cycle 209 Technical Scan

Date: 2026-05-17
Cycle: 209
Role: Technical scan subagent

## Implementation Map

- Add `presenter/skills/ringcentral-onboarding.md`.
- Mirror the file to `src/ai_presenter/presenter/skills/ringcentral-onboarding.md`.
- Add the skill to all root RingCentral profiles before
  `ringcentral-safety`.
- Add the skill to the packaged `src/ai_presenter/profiles/ringcentral-video.yaml`.

## Tests

- `tests/unit/test_config_loader.py`
  - Assert all RingCentral profiles load the four active runtime skills in order.
  - Assert the packaged profile resolves the packaged onboarding skill path.
- `tests/unit/test_presenter_context.py`
  - Assert the loaded context includes the onboarding skill and stable training
    phrases.
- `tests/unit/test_presenter_skill_packaging.py`
  - Lock the new skill name and package-copy parity.
- `tests/unit/test_openai_provider.py` and `tests/unit/test_codex_cli_provider.py`
  - Assert loaded presenter context reaches provider prompts.

## Risk Notes

- This is an active prompt behavior change, so wording must stay narrow and
  RingCentral-specific.
- The onboarding skill must not dilute `ringcentral-safety`; safety remains
  last in profile order.
- Package-local French text remains distinct from runtime `--language fr`
  support.
