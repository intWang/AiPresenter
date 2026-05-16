# Stable Validation Target IDs Design

Date: 2026-05-16
Cycle: 029

## Problem

`validation-targets` currently generates target IDs from checklist priority and human-facing labels, such as `p0-add-coworkers-modal`. Those labels and priorities are expected to change as RingCentralVideo evidence improves, which makes CLI commands, runbooks, and subagent handoffs brittle.

## Acceptance

- RingCentral validation checklist tables include an explicit `Target ID` column.
- `validation-targets` uses explicit IDs when the column is present.
- `Target ID` remains optional for compatibility. Tables without the column still use the existing generated ID behavior.
- If a table has `Target ID`, blank target ID cells fail clearly instead of falling back.
- Duplicate resolved target IDs fail clearly.
- Priority checklist IDs use stable `rcv-*` names without priority or evidence status.
- `Do Not Execute Yet` rows also have status-neutral `rcv-*` IDs and remain visible only with `--include-blocked`.
- No live RingCentralVideo action is performed, and no evidence is promoted.

## Design

Add optional target ID parsing to `src/ai_presenter/acceptance/validation_targets.py`:

- `_parse_first_table(..., optional_headers=("Target ID",))` should include optional cells only when the header exists.
- Missing `Target ID` header means fallback to existing generated IDs.
- Present but blank `Target ID` cell raises `ValueError("blank validation target id for <route>")`.
- Explicit IDs are trimmed and optional backticks are removed, but they are not slugified, lowercased, or auto-prefixed.

Update `docs/knowledge/ringcentral-video/validation-checklist-index.md`:

- Priority rows use IDs such as `rcv-add-coworkers-modal`.
- Blocked rows use IDs such as `rcv-recording` and `rcv-leave-end-meeting`.

## Out Of Scope

- Target aliases from old generated IDs.
- JSON output.
- Package route ID changes.
- Acceptance evidence edits.
- Live RingCentral validation.
