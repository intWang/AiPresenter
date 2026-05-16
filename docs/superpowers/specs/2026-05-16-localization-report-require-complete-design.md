# Localization Report Require Complete Design

Date: 2026-05-16
Cycle: 028

## Problem

`localization-report` shows whether a package has complete localized narration and Q&A for a language, but it always exits `0`. That is useful for humans, but weak for handoffs, CI, and future language expansion because agents cannot ask the command to fail when required localization is incomplete.

## Acceptance

- Default `localization-report` behavior stays unchanged and exits `0` for partial coverage.
- `localization-report --require-complete` still prints the normal report.
- With `--require-complete`, the command exits `1` when any required demo step narration, Q&A localized question, or Q&A localized answer is missing for the chosen language.
- Missing `questionAliases.<language>` does not fail the gate; aliases remain informational.
- The command remains package-only and does not load diagnostics, voice assets, provider modules, desktop automation, or controller/runtime factory modules.

## Design

Add a pure completion property to `LocalizationStatusReport`:

- `required_localization_complete`

The property compares:

- `demo_localized_steps == demo_total_steps`
- `qa_localized_questions == qa_total`
- `qa_localized_answers == qa_total`

`cli.localization_report` gains a boolean `--require-complete` option. It renders the report exactly as before, then checks the property. If incomplete, it appends a concise failure line and raises `typer.Exit(1)`.

## Out Of Scope

- JSON output or percentage thresholds.
- Package schema changes for declared required languages.
- Adding another language's content.
- Extending `doctor` to enforce localization gates.
