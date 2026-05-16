# Cycle 023 Demand Analysis

Date: 2026-05-16
Theme: RingCentralVideo Chinese demo-flow narration

## Recommendation

Use Cycle 023 for a small package-content-only localization slice: add `narration.localizedText.zh` to every step in `vbg-blur-demo` and `meeting-basics-demo`.

Why this slice:

- Cycle 022 localized Chinese Q&A and aliases, but short scripted flows still fall back to English narration.
- `meeting-control-map-demo` is already fully localized and is the README/runbook primary Chinese demo flow.
- `vbg-blur-demo` is a focused, user-visible RingCentral value story: privacy and presentation quality through Blur.
- `meeting-basics-demo` covers the everyday meeting controls Chinese users are most likely to ask about: microphone, participants, and chat.
- The older `meeting-controls-tour` has 22 unlocalized steps, but it overlaps heavily with the already-localized `meeting-control-map-demo`; localizing it now is larger and lower leverage.

## Current Flow State

- `meeting-control-map-demo`: 22/22 steps already have `localizedText.zh`.
- `vbg-blur-demo`: 0/4 steps localized.
- `meeting-basics-demo`: 0/3 steps localized.
- `meeting-controls-tour`: 0/22 steps localized.

## Target Steps

Localize these seven steps in `packages/ringcentral-video.yaml`:

- `vbg-blur-demo`
  - `open-video-settings`
  - `open-background-panel`
  - `select-blur`
  - `verify-meeting-video`
- `meeting-basics-demo`
  - `show-mic`
  - `show-participants`
  - `show-chat`

The Chinese copy should be authored, not machine-literal. Keep product labels such as `Settings`, `Background`, `Blur`, `Participants`, and `Chat` when they match the visible RingCentral UI, but explain their value in natural Chinese.

## Acceptance Criteria

- `packages/ringcentral-video.yaml` adds `narration.localizedText.zh` for all seven target steps only.
- Existing English `narration.text`, step ids, entrypoint ids, operations, placements, offsets, and open steps are unchanged.
- Add or update a focused unit test in `tests/unit/test_material_packages.py` proving both target flows have non-empty Chinese `localized_text["zh"]` for every step and that each string contains at least one CJK character.
- Add a focused voice rendering assertion, either in existing voice tests or material package tests, proving one newly localized step renders the Chinese text with `PresenterVoiceSettings(language="zh")`.
- Run focused verification:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py`
  - If a voice rendering test is added outside that file, include that exact test module too.

## Risks

- PowerShell may render Chinese as mojibake; preserve UTF-8 and judge file content/tests rather than terminal display.
- `vbg-blur-demo` includes a real Blur selection action. Do not broaden route behavior or safety policy in this cycle.
- Avoid expanding to `meeting-controls-tour` unless the implementer has extra time and explicit scope approval; it is larger and duplicates the localized map flow.
- Do not change runtime localization fallback, package schema, CLI/controller flow selection, or RingCentral open-step locators.

## Follow-Up Candidate

After this slice, decide whether to retire, alias, or fully localize `meeting-controls-tour`. If it remains a supported public flow, add `localizedText.zh` to all 22 steps in a separate package-content-only cycle with the same test pattern.
