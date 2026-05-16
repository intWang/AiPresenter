# Cycle 114 Test Review: Legacy Alias Match Precomputation

Date: 2026-05-16

## Verdict

No blocking issues found.

The narrower implementation is acceptable as an internal runtime performance hygiene slice even though it does not implement the demand handoff's diagnostics-index recommendation or the technical handoff's query-token reuse recommendation. It still fits the cycle's broader performance theme, stays small, and preserves the risk scan's main route-order guardrails.

This is not live RingCentral acceptance evidence. It does not change package YAML, schema, profiles, diagnostics output, localization counts, knowledge indexes, or live-app behavior evidence.

## Findings

Critical: None.

Important: None.

Minor: Identity-based cache invalidation only detects replacement of `_ENTRYPOINT_ALIASES`, not in-place mutation of the same dict object.

- File/lines: `src/ai_presenter/runtime/questions.py:453-468`
- Impact: This is acceptable for the current private constant and the tested hook shape because `monkeypatch.setattr(..., "_ENTRYPOINT_ALIASES", new_dict)` replaces the source object and rebuilds the tuple. A future hook that mutates the existing dict in place would see stale precomputed aliases until the source object is replaced.
- Guidance: Keep future hooks replacing `_ENTRYPOINT_ALIASES` wholesale, or add an explicit cache reset/version marker if in-place mutation ever becomes supported.

Reviewed behavior notes:

- Source-identity cache: `_LEGACY_ENTRYPOINT_ALIAS_SOURCE is _ENTRYPOINT_ALIASES` correctly avoids stale aliases when tests or future hooks replace `_ENTRYPOINT_ALIASES` with a new dict.
- Longest-first behavior: preserved by sorting normalized aliases by descending length before matching.
- Tie/order behavior: preserved because Python sorting is stable. Equal-length aliases keep the original dict insertion order and tuple order, matching the old strict `>` best-length behavior.
- Route precedence: preserved as Q&A/safety matching in `_answer_question()` runs before `_match_entrypoint()`, and `_match_entrypoint_alias()` still checks package-owned aliases before legacy aliases, with token scoring after aliases.
- Ruff/mypy risk: no issue found for the global typing or private helper test under the focused checks below.

## Verification

Focused tests:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_legacy_alias_matches_are_precomputed_longest_first tests\unit\test_questions.py::test_legacy_alias_table_remains_dynamic_for_runtime_matching tests\unit\test_questions.py::test_package_owned_alias_takes_precedence_over_legacy_alias_table tests\unit\test_questions.py::test_longest_package_owned_alias_wins tests\unit\test_questions.py::test_ringcentral_japanese_recording_safety_question_stays_qa_first
```

Result: `5 passed in 0.84s`.

Ruff:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache src\ai_presenter\runtime\questions.py tests\unit\test_questions.py
```

Result: `All checks passed!`

Mypy:

```powershell
.\.venv\Scripts\mypy.exe --no-incremental src\ai_presenter\runtime\questions.py tests\unit\test_questions.py
```

Result: `Success: no issues found in 2 source files`.

Whitespace:

```powershell
git diff --check -- src\ai_presenter\runtime\questions.py tests\unit\test_questions.py docs\agent-handoffs\cycle-114-implementation.md
```

Result: exit code `0`; Git reported only LF-to-CRLF working-copy warnings for `src/ai_presenter/runtime/questions.py` and `tests/unit/test_questions.py`.

No long full suite, live RingCentral validation, package doctor run, localization report, coverage review, or knowledge-index verification was run for this lightweight review.

## Staging Guidance

Stage only the intended Cycle 114 files:

- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_questions.py`
- `docs/agent-handoffs/cycle-114-demand-analysis.md`
- `docs/agent-handoffs/cycle-114-technical-scan.md`
- `docs/agent-handoffs/cycle-114-risk-scan.md`
- `docs/agent-handoffs/cycle-114-implementation.md`
- `docs/agent-handoffs/cycle-114-test-review.md`

Do not stage `.coverage`.

Before committing, run `git status --short` and verify `.coverage` remains unstaged.
