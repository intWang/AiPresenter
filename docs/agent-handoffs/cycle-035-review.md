# Cycle 035 Review: Package Alias Match-Order Index

Date: 2026-05-16
Role: review
Scope: review of uncommitted Cycle 035 alias match-order changes.

## Review Inputs

- Base commit: `4b69a2591d9ca3da2961c1edd075045be4f4bda7`
- Plan: `docs/superpowers/plans/2026-05-16-package-alias-match-order-index.md`
- Spec: `docs/superpowers/specs/2026-05-16-package-alias-match-order-index-design.md`

## Findings

No critical or important issues were found.

The reviewer confirmed:

- `entrypoint_question_aliases` remains source ordered.
- `entrypoint_question_aliases_by_match_order` is runtime-only and sorted longest-first.
- Equal-length aliases keep source order.
- Q&A still precedes entrypoint matching.
- Package-owned aliases still precede legacy aliases.
- The legacy `_ENTRYPOINT_ALIASES` table remains read at runtime.
- Serialization does not expose runtime indexes.
- `with_demo_flow()` rebuilds runtime indexes.

## Minor Follow-Up

The reviewer suggested adding a positive regression test for dynamic legacy alias monkeypatching. Existing tests already covered package aliases with the legacy table removed, but did not prove a replacement legacy alias table is still honored.

Action taken:

- Added `test_legacy_alias_table_remains_dynamic_for_runtime_matching`.
- The test monkeypatches `_ENTRYPOINT_ALIASES` to a custom alias pointing at an existing package entrypoint and verifies `answer_question()` still matches it when package-owned aliases do not apply.

## Review Verdict

Approved with no blocking issues.
