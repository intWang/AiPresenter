# Cycle 178 Test Review

Date: 2026-05-17

## Findings

1. **[P1] Broad Chat aliases could bypass chat-content privacy routing.**
   `open chat` and `show chat` are package aliases, and alias matching is substring-based. Before the fix, `Can you show chat messages?`, `Open chat messages`, and `Please be brief and show chat messages` routed to `ringcentral.video.toolbar.chat` with `can_operate=True` and created an interrupt.

2. **[P2] Durable docs still reported stale authored Q&A item count.**
   The package loads as 16 Q&A items, 220 Q&A candidates, and 169 aliases. The current docs had been updated for aliases and prompts but still said 12 Q&A items.

3. **[P3] Running-controller safe mixed test did not assert no stop request.**
   The queued-interrupt test should also prove the controller does not request a demo stop while queuing a safe mixed prompt.

## Fixes Applied

- Added `_match_chat_content_privacy_qa(...)` in `src/ai_presenter/runtime/questions.py` before package-alias guards.
- Expanded chat privacy tests with `Can you show chat messages?`, `Open chat messages`, and presenter-meta-prefixed chat-message variants.
- Updated current RingCentralVideo docs from 12 to 16 Q&A items and from 12/12 to 16/16 Q&A localization coverage.
- Added `control.is_stop_requested is False` to the running-controller safe mixed test.

## Residual Risk

Controller/session coverage now hits Chat safe and Meeting Info answer-only paths. Broader mixed-meta surfaces remain candidates for later cycles: network quality, participants, Notes/Transcript, and localized Spanish/Japanese privacy prompts.

`.coverage` is dirty in the working tree and should stay out of the commit.

## Recommended Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py tests\unit\test_material_packages.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
```
