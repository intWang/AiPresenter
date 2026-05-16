# Cycle 008 Implementation: Package Runtime Index

Date: 2026-05-16

## Objective

Reduce repeated runtime lookup work in hot question/action paths by building validated package indexes once per `MaterialPackage`.

## Scope

Implemented the narrow version of the demand-analysis recommendation:

- Indexed operation entrypoint lookup by id.
- Indexed package-owned question aliases with pre-normalized alias text.
- Updated question alias matching to consume the prebuilt package alias index.

Deferred to later cycles:

- Flow lookup index.
- Q&A phrase/token index.
- Entrypoint token/scoring index.
- Legacy alias migration into package YAML.

The narrower scope keeps existing fuzzy scoring and Q&A behavior unchanged while improving the highest-confidence repeated lookup paths.

## Files Changed

- `src/ai_presenter/packages/models.py`
  - Added frozen `EntrypointQuestionAlias`.
  - Added private Pydantic attrs for `_entrypoints_by_id` and `_entrypoint_question_aliases`.
  - Built both indexes inside the existing `validate_entrypoint_references()` validation pass.
  - Added read-only `entrypoints_by_id` property via `MappingProxyType`.
  - Added immutable `entrypoint_question_aliases` property.
  - Updated `entrypoint_by_id()` to use the validated dict and preserve the unknown-id `KeyError` message.
- `src/ai_presenter/runtime/questions.py`
  - Updated package-owned alias matching to iterate `package.entrypoint_question_aliases`.
  - Preserved package-owned alias precedence over the legacy alias table.
  - Preserved longest-alias-wins behavior.
- `tests/unit/test_material_packages.py`
  - Added coverage for the read-only entrypoint index.
  - Added coverage for preserved unknown-id behavior.
  - Added coverage for normalized package alias index content.
  - Added coverage that private runtime indexes do not leak into `model_dump(by_alias=True)`.

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_read_only_entrypoint_index tests\unit\test_material_packages.py::test_entrypoint_by_id_preserves_unknown_id_error tests\unit\test_material_packages.py::test_material_package_exposes_normalized_question_alias_index
```

Red result:

- `test_material_package_exposes_read_only_entrypoint_index` failed because `MaterialPackage.entrypoints_by_id` did not exist.
- `test_material_package_exposes_normalized_question_alias_index` failed because `MaterialPackage.entrypoint_question_aliases` did not exist.
- `test_entrypoint_by_id_preserves_unknown_id_error` already passed, confirming existing behavior before the implementation.

Green result after implementation:

- Same command: `3 passed in 2.23s`.

## Verification

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py`
  - Result: `40 passed in 8.88s`
- `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py src\ai_presenter\runtime\package_demo.py tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_package_demo.py`
  - Result: `All checks passed!`
- `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py`
  - Result: `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py src\ai_presenter\runtime\package_demo.py tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_package_demo.py`
  - Result: `Success: no issues found in 6 source files`
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py`
  - Result: `Success: no issues found in 4 source files`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_package_demo.py tests\unit\test_material_runtime.py tests\unit\test_controller_session.py`
  - Result: `30 passed in 2.08s`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - Result: `384 passed, 1 warning in 21.41s`
- `git diff --check`
  - Result: no whitespace errors; Git reported expected CRLF conversion warnings for touched files.

## Known Follow-Ups

- Add flow id indexing and route `demo_flow_by_id()` through it.
- Precompute Q&A question candidates and token sets once package behavior is better characterized by telemetry.
- Precompute entrypoint scoring tokens only with careful tie-break regression coverage.
- Consider adding a synthetic timing probe in docs after more index-backed surfaces exist; avoid brittle wall-clock CI thresholds.
