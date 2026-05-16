# Cycle 049 Demand Analysis

## Recommended Slice

Add a `doctor` readiness check for duplicate normalized Q&A question text.

## User Value

Cycle 048 made exact Q&A lookup deterministic and fast by indexing normalized question text. That preserves first-declared behavior, but it also means duplicate authored questions can silently shadow later Q&A items. A doctor warning lets package authors catch that before live Q&A routes to an unexpected answer.

## Acceptance Criteria

- The current RingCentral package reports an OK `qa questions` diagnostic.
- A synthetic package with duplicate English Q&A questions warns.
- A synthetic package with duplicate localized Q&A questions warns.
- Duplicate question prompts inside the same Q&A item do not warn.
- Warning details include normalized question text, languages, affected Q&A item labels, and current first-match winner.
- The warning is non-fatal.
- Runtime matching, answer text, tone rendering, localization, `can_operate`, and exact-match index behavior remain unchanged.

## Out Of Scope

- No package YAML edits.
- No schema validation failure for duplicates.
- No runtime match-order changes.
- No semantic or fuzzy matching.
- No entrypoint alias exact-lookup optimization in this cycle.

