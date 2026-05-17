# Cycle 185 Risk Scan

Date: 2026-05-17

## Findings

- P1 staging risk: `.coverage` is modified by default test runs and is tracked. Use explicit `git add` paths and verify cached diff excludes it.
- No privacy or safety issue found in the question-policy diagnostic slice. The new check reports package entrypoint IDs only.
- The diagnostic should stay informational/OK unless a future slice defines package-specific required IDs.
- The exact current RingCentralVideo answer-only policy set is `ringcentral.video.top.meeting-info` and `ringcentral.video.more.notes`.
- Localization checks for zh, ja, and es must remain green because this cycle touches package diagnostics and RingCentralVideo source docs.

## Guardrails

- Do not stage `.coverage`.
- Do not add or remove `questionPolicy` declarations.
- Do not change `_can_operate(...)` behavior.
- Do not confuse Q&A answer-only routing with entrypoint `questionPolicy: answerOnly`.
- Do not claim live RingCentral acceptance from a doctor output.

## Suggested Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov tests/unit/test_cli.py tests/unit/test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language zh --require-localization
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language ja --require-localization
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
```
