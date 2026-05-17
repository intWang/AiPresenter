# Cycle 187 Risk Scan

Date: 2026-05-17

## Findings

- P1 privacy risk: generic controller exceptions could reach status rows and operator summaries.
- P2 staging risk: `.coverage` remains modified by test runs and must stay out of the commit.
- RingCentralVideo private-surface examples are valuable, but this cycle should avoid docs/package drift outside the controller status boundary.

## Guardrails

- Treat arbitrary exception text as private.
- Preserve only allowlisted public configuration messages.
- Keep raw prompt text, answer text, participant data, meeting links, local paths, provider exception details, and stack traces out of status rows.
- No package YAML, localization, alias, or live acceptance changes.

## Suggested Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
```
