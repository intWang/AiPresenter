# Cycle 033 Technical Scan: Q&A Matcher Candidate Precompute

Date: 2026-05-16
Role: technical discovery
Scope: read-only technical scan. No implementation changes were made in this pass.

## Recommendation

Add immutable runtime-only matcher candidates to `MaterialPackage` and update `runtime/questions.py` to consume them.

Current matcher hot spots:

- `_match_qa()` rebuilds base plus localized Q&A candidate lists for each question.
- `_match_qa()` recomputes normalized question strings and meaningful token sets for every candidate.
- `_score_entrypoint_match()` recomputes id/title/area/purpose token sets for every entrypoint on every fallback match.

The lowest-risk improvement is to precompute stable package candidates during package validation and keep query-specific work inside `answer_question()`.

## Recommended Data Structures

In `src/ai_presenter/packages/models.py`:

- `QuestionAnswerMatchCandidate`
  - `item: QuestionAnswer`
  - `question: str`
  - `normalized_question: str`
  - `meaningful_tokens: frozenset[str]`
- `EntrypointMatchCandidate`
  - `entrypoint: OperationEntrypoint`
  - `id_tokens: frozenset[str]`
  - `title_tokens: frozenset[str]`
  - `area_tokens: frozenset[str]`
  - `purpose_tokens: frozenset[str]`
  - `title_or_id_tokens: frozenset[str]`

Add private attrs:

- `_qa_question_candidates`
- `_entrypoint_match_candidates`

Expose them through read-only tuple properties:

- `qa_question_candidates`
- `entrypoint_match_candidates`

Use `PrivateAttr`, not `@computed_field`, so runtime indexes do not serialize into `model_dump()`.

## Implementation Notes

- Build indexes in the existing `validate_entrypoint_references()` path after entrypoints, aliases, flows, explainers, and Q&A references validate.
- Prefer a `_rebuild_runtime_indexes()` helper to centralize private attr assignment.
- Preserve candidate order exactly:
  - Q&A base question first, followed by localized question values in current dictionary/list order.
  - Entrypoint candidates in `operation_entrypoints` order.
- Keep legacy `_ENTRYPOINT_ALIASES` dynamic so tests that monkeypatch it still work.
- Keep `with_demo_flow()` using `model_dump(by_alias=True)` plus `MaterialPackage.model_validate(data)`. Avoid `model_copy(update=...)` for package shape changes because Pydantic v2 does not re-run validation and can leave private attrs stale.

## Tests To Add

- `test_material_package_exposes_precomputed_qa_question_candidates`
  - Tuple is read-only.
  - Base question and localized question candidates exist.
  - Candidate `item` points to the package Q&A item.
  - `normalized_question == question.casefold()`.
  - `meaningful_tokens` is a `frozenset`.
- `test_material_package_exposes_precomputed_entrypoint_match_candidates`
  - Candidate order matches `operation_entrypoints`.
  - Chat candidate id/title tokens include `chat`.
  - Candidate `entrypoint` points to the package entrypoint object.
- Extend `test_runtime_indexes_do_not_leak_into_model_dump`.
- Extend `test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow` so copied candidates point to copied model objects.

Optional:

- `test_package_alias_match_order_is_longest_first_and_stable_for_ties` if package aliases are reordered.

## Risks

- P0: Matching precedence must remain Q&A, package alias, legacy alias, token fallback.
- P0: Q&A substring pass must remain before token overlap fallback.
- P0: Localized Q&A candidates must include all current localized values and must not introduce filtering that changes behavior.
- P0: Package-owned aliases must continue to beat legacy aliases.
- P1: Legacy alias monkeypatch tests will break if legacy aliases are precomputed too early.
- P1: `can_operate` is a safety gate; keep it separate from matcher candidates.

## Suggested Focused Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py
```
