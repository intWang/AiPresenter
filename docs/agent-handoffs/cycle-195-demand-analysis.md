# Cycle 195 Demand Analysis: Executive Tone As Canonical Presenter Tone

Date: 2026-05-17

## User Need

Operators keep asking to expand AiPresenter tone types while preserving RingCentralVideo safety.
`executive` was accepted only as an alias for `formal`, so the UI/CLI could mention it but runtime
behavior collapsed to `Formal`. Promoting it to a canonical tone gives operators a clearer
boardroom/demo-briefing mode without changing RingCentralVideo routes.

## Operator Value

- Makes an already-public tone request visible as its own selectable voice: `English / Executive`.
- Gives presenters a distinct style for leadership demos: concise, decision-oriented, polished,
  and outcome-focused.
- Improves perceived tone coverage with a small, testable runtime slice.
- Keeps the feature inside presenter voice rendering instead of RingCentralVideo package YAML.

## Chosen Slice

Promote `executive` from a `formal` alias to a canonical presenter tone with distinct label,
description, English rendering, Chinese dynamic prefix, CLI listing, and route-parity coverage.

## Acceptance Criteria

- `PresenterVoiceSettings(tone="executive").tone == "executive"`.
- `PRESENTER_TONE_CHOICES` includes `("Executive", "executive")`.
- `briefing` and `boardroom` normalize to `executive`; `structured` remains `formal`.
- CLI `voices` lists `Executive aliases:`.
- Controller/operator voice label renders `English / Executive`.
- RingCentralVideo sensitive prompt routing remains tone-invariant.
- `executive tone` presenter meta requests stay answer-only and no-interrupt.

## Non-Goals

- No RingCentralVideo package aliases, Q&A, entrypoints, locators, or YAML count changes.
- No changes to `can_operate`, `questionPolicy`, Q&A-first matching, or interrupt creation.
- No persistent natural-language tone state changes from chat prompts.
- No new speech providers, voice assets, or live RingCentral acceptance claims.
