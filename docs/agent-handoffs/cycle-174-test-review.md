# Cycle 174 Test Review

## Findings

### P2 - Meta short-circuit steals mixed RingCentral intents before safety/control routing

The new Presenter meta-request check in `src/ai_presenter/runtime/questions.py` runs immediately after normalization, before `_match_qa(...)` and `_match_entrypoint(...)`. Because `_is_presenter_meta_request(...)` uses unanchored substring matching, a prompt that combines a style modifier with a RingCentralVideo request returns the generic `Presenter settings:` answer instead of the existing RingCentral safety or control route.

Manual probes against the current diff showed:

| Prompt | Current result | Expected boundary behavior |
| --- | --- | --- |
| `Please be brief and read meeting information aloud` | `entrypoint_id=None`, no interrupt, `Presenter settings:` | Meeting-info privacy Q&A, answer-only, no interrupt |
| `Use privacy tone and read meeting information aloud` | `entrypoint_id=None`, no interrupt, `Presenter settings:` | Meeting-info privacy Q&A, answer-only, no interrupt |
| `Be concise: is this meeting encrypted?` | `entrypoint_id=None`, no interrupt, `Presenter settings:` | Encryption/security Q&A via meeting-info, answer-only, no interrupt |
| `Use coach tone and mute all participants` | `entrypoint_id=None`, no interrupt, `Presenter settings:` | Host-controls/participants safety Q&A, answer-only, no interrupt |
| `Please be brief and go full screen` | `entrypoint_id=None`, no interrupt, `Presenter settings:` | Full-screen route to `ringcentral.video.top.views`, operable safe interrupt |

This does not trigger a dangerous operation; `can_operate` remains false and no interrupt is created. The risk is that mixed-intent prompts bypass the specific privacy/security/host-control guidance, and safe full-screen routing is suppressed. I would not accept the current diff as final without either a mixed-intent guard or explicit product acceptance that any Presenter-style modifier should intentionally no-op the app request.

## Verification Performed

- Reviewed the uncommitted diff for:
  - `src/ai_presenter/runtime/questions.py`
  - `tests/unit/test_questions.py`
- Inspected existing RingCentralVideo routing boundaries in:
  - `packages/ringcentral-video.yaml`
  - `tests/unit/test_questions.py`
  - `src/ai_presenter/runtime/session.py`
- Tried global pytest first:
  - `python -m pytest tests/unit/test_questions.py tests/unit/test_controller_session.py -q`
  - Result: blocked, global Python has no `pytest` module.
- Ran focused no-write pytest via repo venv:
  - `$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller_session.py`
  - Result: `394 passed in 77.48s`
- Ran controller no-interrupt sentinels:
  - `$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_queues_safe_question_without_stopping_running_demo tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo`
  - Result: `2 passed in 2.07s`
- Ran manual routing probes for mixed Presenter-style plus RingCentralVideo prompts; results are summarized in the finding.

## Residual Risks

- The added unit test covers positive meta-request phrases, but not overlap/negative prompts where a style phrase is attached to meeting-info privacy, encryption/security, host controls, or full-screen requests.
- The meta fragment list is English-only. That is not a new RingCentralVideo safety regression, but localized Presenter meta requests may still fall through to normal matching.
- I did not run full coverage-enabled pytest because `.coverage` is already dirty and this handoff was constrained to write only this doc file.

## Recommendation

Revise before merge. Keep the answer-only/no-interrupt short-circuit for pure Presenter settings requests, but add overlap tests and route mixed RingCentralVideo intents through the existing safety/control boundaries. A conservative fix would apply the meta short-circuit only when no RingCentral Q&A or entrypoint intent is present, or at least let privacy/security/host-control Q&A and full-screen aliases win over meta fragments.

## Status

Status: review complete; source and test files were not modified, staged, or committed.

Changed file: `docs/agent-handoffs/cycle-174-test-review.md`
