# Cycle 212 Demand Analysis

Date: 2026-05-17
Cycle: 212
Role: Demand analysis subagent

## Recommendation

Extend French package-local narration for the four-step `vbg-blur-demo` flow.

## User Value

- Turns the existing French background Q&A seed into a coherent background
  privacy pocket.
- Improves measurable French demo narration coverage from `3/51` to `7/51`.
- Keeps RingCentral UI labels such as Settings, Background, Blur, and Stop
  video literal so users can still find English UI controls.

## Selected Slice

- Add `localizedText.fr` to `open-video-settings`,
  `open-background-panel`, `select-blur`, and `verify-meeting-video`.
- Update package localization tests, CLI report tests, diagnostics detail, and
  durable RingCentral/language docs.

## Non-Goals

- No `--language fr` runtime support.
- No OpenAI-only French voice promotion.
- No Q&A prompt, alias, route, locator, controller UI, presenter skill, or live
  RingCentral evidence changes.

## Acceptance Criteria

- French localization report shows `7/51` demo steps.
- `vbg-blur-demo` shows `4/4` French narration localized.
- French Q&A remains `1/16` questions and `1/16` answers.
- `--require-complete` still fails for French.
- `demo --language fr` still rejects before runtime starts.
