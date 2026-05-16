# Cycle 008 Review: Package Runtime Index

Date: 2026-05-16
Role: read-only review sidecar
Write scope: this file only

## Scope Reviewed

Reviewed only the Cycle 008 package runtime index scope:

- `docs/superpowers/specs/2026-05-16-package-runtime-index-design.md`
- `docs/superpowers/plans/2026-05-16-package-runtime-index.md`
- `docs/agent-handoffs/cycle-008-demand-analysis.md`
- `docs/agent-handoffs/cycle-008-implementation.md`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_material_packages.py`
- Relevant alias behavior tests in `tests/unit/test_questions.py`

The working tree contains unrelated dirty files from other cycles. I treated those as other agents' work and did not revert or overwrite anything.

## Findings

No high-severity or behavior-blocking issues found in the Cycle 008 package runtime index changes.

## Review Notes

Behavior drift:

- `MaterialPackage.entrypoint_by_id()` now uses the validated private dict at `src/ai_presenter/packages/models.py:178` while preserving the public `KeyError("Unknown operation entrypoint: ...")` behavior.
- Package-owned alias matching still happens before the legacy alias table in `src/ai_presenter/runtime/questions.py:278`, preserving the package-over-legacy rule.
- Longest package-owned alias still wins because `src/ai_presenter/runtime/questions.py:304` tracks the longest normalized alias with a strict `>` comparison, preserving first-match behavior on equal lengths.
- The alias path remains a linear substring scan over package alias records. Cycle 008 improves repeated work by pre-normalizing package-owned aliases once, but it is not a full alias lookup table. That matches the documented narrow scope.

Pydantic private attr safety:

- `_entrypoints_by_id` and `_entrypoint_question_aliases` are `PrivateAttr`s and are assigned after validation completes in `src/ai_presenter/packages/models.py:166`.
- `entrypoints_by_id` exposes a `MappingProxyType`, preventing accidental mutation through the public diagnostic surface.
- `entrypoint_question_aliases` exposes an immutable tuple of frozen dataclass records.

Serialization and schema leakage:

- The added `test_runtime_indexes_do_not_leak_into_model_dump` covers `package.model_dump(by_alias=True)` and confirms `entrypointsById`, `entrypointQuestionAliases`, `_entrypoints_by_id`, and `_entrypoint_question_aliases` are absent while `operationEntrypoints` remains present.
- I also ran a schema probe against `MaterialPackage.model_json_schema(by_alias=True)` and found no runtime index properties in the schema.

Stale-index risk:

- The private indexes are validation-time snapshots. Direct post-validation mutation of `operation_entrypoints`, `OperationEntrypoint.id`, or `question_aliases` can make the indexes stale.
- This is an accepted risk in the Cycle 008 design, which says callers should keep treating loaded packages as immutable runtime inputs.
- Existing `model_copy(update=...)` usage in `src/ai_presenter/runtime/controller.py:398` updates only `demo_flows`, so it does not stale the entrypoint or alias indexes today. Future `model_copy(update={"operation_entrypoints": ...})` use should rebuild through full model validation rather than relying on copied private attrs.

Test adequacy:

- New unit coverage checks the read-only entrypoint index, unchanged unknown-id behavior, normalized alias index content, and model dump non-leakage.
- Existing question tests cover package-owned aliases without the legacy table, package-owned alias precedence over legacy aliases, and longest package-owned alias selection.
- The remaining untested edge is intentional package mutation after validation. I do not recommend adding behavior guarantees for that unless the project decides `MaterialPackage` should become frozen or revalidation-safe.

## Verification Commands

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Result: `40 passed in 9.91s`

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Result: `All checks passed!`

```powershell
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Result: `Success: no issues found in 4 source files`

```powershell
git diff --check -- src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py
```

Result: exit code 0; Git printed expected LF-to-CRLF working-copy warnings for the three checked files.

```powershell
.\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; from ai_presenter.packages.models import MaterialPackage; package = load_material_package(Path('packages/ringcentral-video.yaml')); dump = package.model_dump(by_alias=True); schema = MaterialPackage.model_json_schema(by_alias=True); forbidden = {'entrypointsById', 'entrypointQuestionAliases', '_entrypoints_by_id', '_entrypoint_question_aliases'}; print('dump_forbidden=', sorted(forbidden & set(dump))); print('schema_forbidden=', sorted(forbidden & set(schema.get('properties', {})))); print('operationEntrypoints_in_dump=', 'operationEntrypoints' in dump); print('operationEntrypoints_in_schema=', 'operationEntrypoints' in schema.get('properties', {}))"
```

Result:

```text
dump_forbidden= []
schema_forbidden= []
operationEntrypoints_in_dump= True
operationEntrypoints_in_schema= True
```

## Recommendation

Cycle 008 is acceptable as implemented. The runtime index changes preserve observable question/action behavior, avoid Pydantic serialization/schema leakage, and add focused tests for the intended public surfaces. The main follow-up is to keep package objects immutable by convention or introduce an explicit rebuild/revalidation path before any future code starts copying or mutating `operation_entrypoints` after validation.
