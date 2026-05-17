# Cycle 198 Lessons: Language Readiness Is Multi-Axis

Date: 2026-05-17

## What Changed

Cycle 198 added a source-checked language/provider matrix to
`docs/knowledge/language-lifecycle.md`. The matrix separates package text,
runtime language recognition, provider compatibility, local voice assets, and
live RingCentral acceptance evidence.

## Reusable Lesson

Language readiness is not a single flag. Future language work should name which
axis it changes:

- Package localization and package query readiness.
- Runtime language selection through `--language`.
- Package-only inspection through `--localization-language`.
- Speech provider compatibility.
- Local voice asset availability.
- Live RingCentral acceptance evidence.

## Important Correction

`doctor --require-localization --localization-language es` can report runtime
language support as `[OK]` because the runtime recognizes `es`. That does not
mean the selected profile can speak Spanish. Provider compatibility is checked
when `--language es` selects Spanish voice output.

## Next-Cycle Candidates

- Generate CLI `voices` documentation from runtime constants.
- Add a compact provider compatibility table to the `voices` command output.
- Mine RingCentral acceptance docs for a cleaner status taxonomy that separates
  repo-tested, observed, manually accepted, and blocked states.
