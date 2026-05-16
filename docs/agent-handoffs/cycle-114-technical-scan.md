# Cycle 114 Technical Scan: Runtime Question Matching Response-Time Slice

Date: 2026-05-16
Scope: technical scan only. This handoff recommends one low-risk implementation slice and does not implement it.

## Goal

Improve runtime response time for controller questions without changing package content, public behavior, localization semantics, production workflows, profiles, coverage, git history, or knowledge indexes.

## Scan Summary

The best next slice is in runtime question matching, not diagnostics, localization reporting, or controller voice readiness.

| Area inspected | Current state | Recommendation |
| --- | --- | --- |
| Runtime Q&A matching | `src/ai_presenter/runtime/questions.py` already uses package indexes, but some fallback paths recompute query token sets for the same normalized question. | Optimize one question-match invocation to compute query tokens once and pass them through matcher helpers. |
| `MaterialPackage` indexes | `src/ai_presenter/packages/models.py` precomputes `qa_question_candidates`, `qa_questions_by_normalized`, `entrypoint_match_candidates`, and alias match order during validation. | Keep this structure; do not add another package index in this cycle. |
| Diagnostics and localization report | `src/ai_presenter/runtime/diagnostics.py` and `src/ai_presenter/packages/localization_status.py` are offline/CLI checks. Their loops are linear over package data and not in the live answer path. | No performance slice here unless future packages become much larger. |
| Controller start and voice cache | `_ControllerVoiceReadinessCache` in `src/ai_presenter/runtime/controller.py` already caches per canonical `(language, tone)` and has targeted tests. | Leave as-is; avoid changing controller startup behavior. |
| Tests | Existing tests cover routing, safety, localized Q&A, timing log privacy, diagnostics, localization report output, and voice readiness cache reuse. | Add one focused matcher call-count assertion before code changes. |

## Concrete Implementation Slice

Implement a small matcher-context optimization in `src/ai_presenter/runtime/questions.py`.

Target functions:

- `answer_question()` / `_answer_question()` at `src/ai_presenter/runtime/questions.py:233` and `src/ai_presenter/runtime/questions.py:268`
- `_match_qa()` at `src/ai_presenter/runtime/questions.py:296`
- `_match_entrypoint()` at `src/ai_presenter/runtime/questions.py:402`
- `_meaningful_tokens()` at `src/ai_presenter/runtime/questions.py:475`
- `_is_specific_question_fragment()` at `src/ai_presenter/runtime/questions.py:479`
- `_can_match_qa_fragment()` at `src/ai_presenter/runtime/questions.py:485`

Root cause/opportunity:

- `MaterialPackage` already precomputes candidate-side data in `src/ai_presenter/packages/models.py:171`, `src/ai_presenter/packages/models.py:321`, and `src/ai_presenter/packages/models.py:357`.
- Runtime still recomputes query-side meaningful tokens as helper functions recurse through Q&A fallback and entrypoint fallback.
- Current RingCentral prompts are small, so this is not a bug. The opportunity is response-time predictability as localized Q&A aliases and generated temporary packages grow.

Suggested implementation shape:

1. Compute `query_tokens = _meaningful_tokens(normalized)` once in `_answer_question()`.
2. Pass `query_tokens` into `_match_qa()` and `_match_entrypoint()`.
3. Change `_is_specific_question_fragment()` to accept the already-computed token set.
4. Change `_can_match_qa_fragment()` to accept the same token set and pass it onward when it needs `_match_entrypoint()`.
5. Keep exact-match and safety-special-case ordering unchanged.
6. Do not change `MaterialPackage`, package YAML, controller UI behavior, localization-report output, or diagnostics wording.

## Red-First Test

Add one deterministic benchmark-style assertion in `tests/unit/test_questions.py`, near the existing matcher and timing tests.

Use a synthetic package with many Q&A candidates containing the same short fragment. Monkeypatch `questions_module._meaningful_tokens` to count calls, then assert the matcher computes query tokens once per public answer operation.

Sketch:

```python
def test_answer_question_reuses_query_tokens_across_qa_fragment_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.chat",
                    "title": "Chat",
                    "area": "Toolbar",
                    "purpose": "Open chat.",
                    "questionAliases": {"en": ["chat"]},
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Chat",
                            "match": {"controlType": "button"},
                        }
                    ],
                }
            ],
            "demoFlows": [],
            "qa": [
                {
                    "question": f"Can you read chat message {index}?",
                    "answer": "No.",
                }
                for index in range(40)
            ],
            "manualControls": [],
        }
    )
    calls = 0
    original = questions_module._meaningful_tokens

    def counting_meaningful_tokens(text: str) -> set[str]:
        nonlocal calls
        calls += 1
        return original(text)

    monkeypatch.setattr(questions_module, "_meaningful_tokens", counting_meaningful_tokens)

    response = answer_question(
        package=package,
        question="chat",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "demo.chat"
    assert calls == 1
```

Why this goes red first:

- Today the Q&A fragment fallback can ask `_is_specific_question_fragment()` and `_match_entrypoint()` to re-tokenize the same normalized prompt while scanning candidates.
- The implementation should make the count independent of candidate volume.

If exact `calls == 1` proves too tight because a safety branch needs one separate tokenization, use `assert calls <= 2`, but start with `1` to force the design to share the query tokens deliberately.

## Risks

- Matching precedence is safety-sensitive. Preserve exact Q&A match, recording safety, notes/transcript safety, title lookup suppression, Q&A fragment matching, Q&A token scoring, package aliases, legacy aliases, and entrypoint scoring order.
- Do not cache across calls or on the package object. This should be per-question invocation state only.
- Avoid broad benchmark timing thresholds; they will be noisy on CI and local Windows.
- Changing `MaterialPackage` indexes would widen the blast radius into package validation and diagnostics counts.
- Controller voice readiness already has cache behavior covered by `tests/unit/test_controller.py:86`, `tests/unit/test_controller.py:116`, and `tests/unit/test_controller.py:176`; do not mix that into this slice.
- `.coverage` is already modified in the worktree and must not be staged.

## Verification Commands

Focused red/green command:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_questions.py::test_answer_question_reuses_query_tokens_across_qa_fragment_fallback `
  -q -o addopts=""
```

Question-routing guard cluster:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_questions.py::test_package_owned_alias_matches_without_legacy_alias_table `
  tests\unit\test_questions.py::test_package_owned_alias_takes_precedence_over_legacy_alias_table `
  tests\unit\test_questions.py::test_longest_package_owned_alias_wins `
  tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant `
  tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only `
  -q -o addopts=""
```

Related non-runtime guard checks:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage `
  tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage `
  tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package `
  tests\unit\test_controller.py::test_controller_voice_readiness_cache_reuses_selected_voice_until_it_changes `
  -q -o addopts=""
```

Scope checks:

```powershell
git diff --check -- docs\agent-handoffs\cycle-114-technical-scan.md
git status --short
```

Before any future staging, confirm only the intended implementation files are staged and `.coverage` remains unstaged.
