# Cycle 182 Risk Scan: Spanish Accent Participant Privacy

Date: 2026-05-17

## Findings

No blocking regression was found for the current Cycle 182 working tree.

## Risk Notes

- `.coverage` is local generated output and currently appears as deleted or modified depending on the latest test run. It must remain unstaged.
- No package YAML changes were made, so alias counts and localization prompt counts should not drift.
- Spanish controller/session mixed-meta coverage is still absent. This is acceptable for this cycle because the default bind-speaker profile does not support Spanish speech output.
- The highest privacy risk remains panel/list wording combined with identity intent, such as `¿Quiénes están en el panel de participantes?`.

## Diagnostics Signals

Read-only risk scan observed:

- `169` package-owned aliases.
- `220` Q&A question prompts.
- Spanish localization complete: `51/51` demo steps, `16/16` Q&A questions, `16/16` Q&A answers, `69` Spanish aliases.
- Doctor expected shape: `11 ok`, `1 info`, `0 warnings`, `0 failed`.

## Mitigations In This Cycle

- Added Spanish plural `quienes` / `quiénes` identity terms.
- Added tests that distinguish `¿Dónde está...` navigation from `¿Quiénes están...` disclosure.
- Added durable privacy matrix guidance for Spanish participant prompts.

## Required Before Commit

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
```

Then stage explicit files only and confirm `git diff --cached -- .coverage` is empty.
