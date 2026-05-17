# Cycle 186 Risk Scan

Date: 2026-05-17

## Findings

- P1 UI privacy risk: question-submit exception text could be copied into `last_question_outcome`, which the operator summary renders directly. Exception text may contain private prompt or answer content.
- P2 staging risk: `.coverage` remains a tracked generated artifact and must not be staged.
- No package, profile, YAML, or live RingCentral acceptance wording drift is needed for this slice.

## Guardrails

- Operator status and summary rows may contain bounded outcome strings only.
- Do not include raw prompts, answer text, exception text, meeting links, participant names, chat content, or transcript content in status rows.
- Keep Q&A answer-only and entrypoint `questionPolicy: answerOnly` semantics distinct.
- Use `--no-cov` for focused verification to avoid refreshing `.coverage`; exclude `.coverage` before commit.

## Verification Suggested

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_questions.py::test_answer_question_logs_answer_source
```
