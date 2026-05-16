# Cycle 033 Summary: Q&A Matcher Candidate Precompute

Date: 2026-05-16
Role: implementation summary

## Goal

Reduce repeated per-question matcher work by precomputing stable package Q&A and entrypoint fallback candidates while preserving current matching behavior exactly.

## Implemented

- Added `QuestionAnswerMatchCandidate` and `EntrypointMatchCandidate` runtime-only dataclasses in `src/ai_presenter/packages/models.py`.
- Added `MaterialPackage.qa_question_candidates` and `MaterialPackage.entrypoint_match_candidates` read-only tuple properties backed by `PrivateAttr`.
- Built Q&A candidates from base and localized questions during package validation.
- Built entrypoint fallback candidates with precomputed id/title/area/purpose token sets during package validation.
- Moved matcher token helpers into package models so candidate construction and query matching share the same tokenizer/stopword rules.
- Updated `runtime/questions.py` to use precomputed candidates for Q&A and entrypoint token fallback.
- Kept legacy `_ENTRYPOINT_ALIASES` dynamic so monkeypatch-based behavior tests remain valid.
- Extended material package tests for candidate construction, ordering, model dump non-leakage, and `with_demo_flow()` rebuild identity.

## TDD Evidence

RED:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_precomputed_qa_question_candidates tests\unit\test_material_packages.py::test_material_package_exposes_precomputed_entrypoint_match_candidates tests\unit\test_material_packages.py::test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow tests\unit\test_material_packages.py::test_runtime_indexes_do_not_leak_into_model_dump
```

Result: `3 failed, 1 passed`. Failures were missing `qa_question_candidates` and `entrypoint_match_candidates` attributes.

GREEN structure:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_precomputed_qa_question_candidates tests\unit\test_material_packages.py::test_material_package_exposes_precomputed_entrypoint_match_candidates tests\unit\test_material_packages.py::test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow tests\unit\test_material_packages.py::test_runtime_indexes_do_not_leak_into_model_dump
```

Result: `4 passed in 1.45s`.

## Verification

Focused behavior:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
```

Result: `82 passed in 13.84s`.

Focused static checks:

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py
```

Results:

- `All checks passed!`
- `Success: no issues found in 4 source files`

Full verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

Results:

- `539 passed, 1 warning in 42.71s`
- `All checks passed!`
- `Success: no issues found in 81 source files`
- `git diff --check` exit 0 with LF-to-CRLF warnings only

The pytest warning is the existing pywinauto STA COM threading warning.

## Review

Review subagent found no blockers. It confirmed matching priority, Q&A candidate order, `PrivateAttr` rebuild behavior, serialization non-leakage, and `can_operate` independence.

## Out Of Scope Kept

- No package YAML changes.
- No semantic search or embeddings.
- No global cache.
- No wall-clock performance assertions.
- No route safety policy changes.
- No answer text changes.

## Suggested Next Slice

Continue performance hygiene with a small package alias match-order index, or switch back to UI by doing a no-live visual smoke plan for long operator summary wrapping.
