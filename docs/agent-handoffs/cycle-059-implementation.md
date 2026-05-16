# Cycle 059 Implementation

## Scope

Added an INFO-level diagnostics guardrail for package-owned aliases that appear as substrings inside longer Q&A prompts.

## Changes

- Extended diagnostic status values with `INFO`.
- Added `DiagnosticReport.info_count` and included info counts in doctor summaries.
- Added `qa alias substring risk` after the exact `qa alias overlap` check.
- Kept exact Q&A prompt versus alias collisions in the existing `qa alias overlap` WARN path.
- Kept substring findings non-failing and non-warning by returning `INFO`, matching the cycle risk scan's guidance to avoid noisy warnings for the current RingCentral package.
- Filtered substring findings to same-language aliases and Q&A prompts, excluded exact matches, and ignored aliases whose entrypoint is already listed in the Q&A item's `relatedEntrypointIds`.
- Updated the RingCentral Video source index to document this doctor signal.

## TDD Evidence

Red run before implementation:

`.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info tests\unit\test_diagnostics.py::test_diagnostics_allows_qa_alias_substring_for_related_entrypoint tests\unit\test_diagnostics.py::test_diagnostics_excludes_exact_alias_overlap_from_substring_info tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_doctor_reports_qa_alias_substring_risk_as_info`

Result: `6 failed`, because the new check and INFO status did not exist yet.

Green run after implementation:

Same command: `6 passed`.

Focused follow-up:

- `tests/unit/test_diagnostics.py`: `33 passed`.
- `tests/unit/test_cli.py`: `63 passed`.

## Behavior Notes

- Current RingCentral emits an INFO line with `11 Q&A question prompts` that contain same-language package-owned alias substrings outside related entrypoints.
- The INFO line is intentionally not a WARN because Q&A-first matching still applies and the current package has explicit runtime regressions for the most sensitive Japanese aliases.
- Future alias expansion should treat this INFO as a prompt to add or review runtime tests before adding broad aliases.

## Next Candidates

- Add a documented allowlist or review notes for known benign substring findings if the INFO detail becomes too noisy.
- Add Japanese aliases for Network quality, Meeting information, or Notes only with matching Q&A priority tests.
- Consider a verbose diagnostics mode if maintainers need all substring findings instead of the first example plus a count.
