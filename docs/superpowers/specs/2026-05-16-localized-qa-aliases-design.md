# Localized Q&A And Alias Content Design

Date: 2026-05-16

## Context

Cycle 001 added deterministic Chinese aliases in `runtime.questions`. That solved the immediate Chinese controller experience, but it left language knowledge in Python code. Cycle 006 moves the first slice of that knowledge into material packages so future languages and app-specific terminology can be authored with the package.

## Design

Extend package models in a backward-compatible way:

- `QuestionAnswer.localized_questions`: `dict[str, list[str]]`, YAML key `localizedQuestions`.
- `QuestionAnswer.localized_answers`: `dict[str, str]`, YAML key `localizedAnswers`.
- `OperationEntrypoint.question_aliases`: `dict[str, list[str]]`, YAML key `questionAliases`.

The matcher will:

- Match package Q&A against the English `question` plus all localized question phrases.
- Render a localized Q&A answer when `voice.language` has a localized answer.
- Match entrypoints using package-owned `questionAliases` before the legacy built-in alias fallback.
- Preserve longest-alias wins so generic aliases do not shadow specific phrases.

## Safety

This cycle changes matching and rendering only. It does not make any risky action operable. `can_operate` remains separate and continues to check open steps and risky entrypoint words.

## RingCentral Package Slice

Add Chinese `localizedQuestions` and `localizedAnswers` for the background privacy Q&A because it is low-risk and directly tied to the language/tone goal.

Add `questionAliases.zh` for a small set of RingCentral entrypoints already covered by Cycle 001 tests:

- Chat
- Invite
- Share
- Background
- Leave

Leave the legacy Python alias table in place as a fallback for aliases not yet migrated. Future cycles can migrate the rest and then remove the fallback.

## Tests

Add tests that prove:

- Pydantic models load localized Q&A and question aliases.
- A temp package with only package-owned aliases can match a Chinese phrase, proving the feature is not relying on the legacy RingCentral alias table.
- RingCentral background Q&A returns a Chinese localized answer for a Chinese localized question.
- Risky aliases such as Share and Leave still match but remain non-operable.
- Mojibake remains unsupported.

## Out Of Scope

- Adding new language codes beyond `en` and `zh`.
- Replacing all legacy aliases.
- Fuzzy semantic matching.
- Confirmation workflows for risky actions.
- Provider prompt skill injection.
