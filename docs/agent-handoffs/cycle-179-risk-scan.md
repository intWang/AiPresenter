# Cycle 179 Risk Scan

Date: 2026-05-17

## Findings

No blocking product/runtime finding for the scoped Network Quality and Notes/Transcript mixed-meta slice. Current diff is test-only across `tests/unit/test_questions.py`, `tests/unit/test_controller_session.py`, and `tests/unit/test_controller.py`; it covers router, session interrupt gating, and idle/running controller orchestration.

Current status also includes dirty `.coverage`. Keep `.coverage` out of review unless intentionally refreshing coverage data.

## Must Not Break

- Q&A/safety matching must stay before entrypoint alias matching.
- Chat content prompts such as `Please be brief and show chat messages` must stay answer-only, not route to Chat panel.
- Presenter-meta-only prompts must return presenter settings guidance with no entrypoint and no interrupt.
- Mixed meta plus safe explicit controls may operate: `Please be brief and show network quality` routes to `ringcentral.video.top.network-quality`, `can_operate=True`, and can queue/start a question demo.
- Mixed meta plus answer-only surfaces must remain text-only: `Please be brief and open notes and transcript` may identify `ringcentral.video.more.notes`, but `can_operate=False` and no interrupt/demo.
- Notes/Transcript action or content requests such as start, read, summarize, copy, save, export, or download transcript text must stay answer-only.
- Do not broaden participant routing in this slice; participant panel, participant identity, roles, and host/moderator questions need separate privacy tests.
- Preserve `questionPolicy: answerOnly`, `_can_operate(...)`, and `create_question_interrupt_step(...)` as the operation gates.

## Verification

Risk agent ran a focused no-coverage slice covering presenter-meta routing, Chat content privacy, Notes/Transcript safety, Network Quality operability, controller/session mixed orchestration, and ruff on touched tests. Result: `42 passed`; ruff passed.

Suggested final commands:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
```
